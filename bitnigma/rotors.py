# stdlib module imports
import array

# third-party module imports

# local module imports


def fromString(s):
    '''Turn a string into an instantiated rotor'''
    # Get all immediate subclasses of the rotor base class
    classes = _Base.__subclasses__()

    # split the argument into name and settings
    split = s.split(':')

    # lookup the rotor
    name = split[0]
    rotor = None
    for c in classes:
        if name == c._short:
            rotor = c
            break
    if not rotor:
        raise ValueError(name + ' is not a valid rotor short-name')

    # extract the other settings
    setting = int(split[1]) if len(split) > 1 else 0

    # Instantiate the rotor
    return rotor(setting=setting)


class _Base:
    '''Base rotor class. Inherited by all proper rotors. NOT FOR CRYPTO USE!'''

    # class variables
    _name = 'BASE ROTOR'
    _short = 'base'
    _wiring = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff'
    _notches = b'\x00'

    def __init__(self, setting=0):
        '''Instantiate a new Rotor with custom or default settings'''
        self.setup(self._wiring, self._notches, setting)

    def _loop(self, n):
        '''Constrain a number N such that 0 <= i <= 255 in a circle'''
        return n % 256

    def setup(self, wiring, notches, setting):
        """Initialize the wiring, notches, and initial rotor setting."""
        # Save the initial setup parameters (useful for serialization)
        self.initial_wiring = wiring
        self.initial_notches = notches
        self.initial_setting = setting

        # Node relative references
        self.next = None
        self.previous = None

        # Initialize wiring matrices
        self.wiring_forward = array.array('h', [0 for i in range(256)])
        self.wiring_reverse = array.array('h', [0 for i in range(256)])

        for i in range(256):
            x = i
            y = wiring[i]
            self.wiring_forward[x] = y - x
            self.wiring_reverse[y] = x - y

        # Initialize the notch matrix
        self.notches = array.array('B', [0 for i in range(256)])
        for notch in notches:
            self.notches[notch] = 1

        # Initial rotor setting
        self.setting = setting

    def step(self):
        '''
        Step the rotor by one letter.
        Returns True if the rotor hit its notch and the
        next rotor in the series should be advanced by one letter as well
        '''
        # increment rotor index, in a loop
        self.setting = self._loop(self.setting + 1)

        # If a notch is hit, increment the next in the series
        if self.notches[self.setting] and self.next:
            self.next.step()

    def translate(self, pin):
        """Start the recursive(ish) translation process."""
        return self.translateForward(pin)

    def translateForward(self, pin_in):
        '''Translate one pin through this rotor in first pass mode.'''
        modifier = self.wiring_forward[self._loop(pin_in + self.setting)]
        pin = self._loop(pin_in + modifier)
        if self.next:
            return self.next.translateForward(pin)
        return self.previous.translateReverse(pin)

    def translateReverse(self, pin_in):
        '''Translate one pin through this rotor in reverse pass mode.'''
        modifier = self.wiring_reverse[self._loop(pin_in + self.setting)]
        pin = self._loop(pin_in + modifier)
        if self.previous:
            return self.previous.translateReverse(pin)
        return pin



class Custom(_Base):
    """Convenience class for instantiating a custom-wired rotor"""
    _name = 'CUSTOM ROTOR'
    _short = 'custom'
    _wiring = None
    _notches = None

    def __init__(self, wiring, notches, setting=0):
        self.setup(wiring, notches, setting)


class ByteI(_Base):
    _name = 'Byte Rotor I'
    _short = 'byte1'
    _wiring = b'\x9e\xe0\xee\x0e#\x89\xf1\x8f\x8d\xd1g\xfb l\xc0\xa61\x03\xb45I\x97s\xa3]\xbd\n_\xef\xc9\xb5\xc6:G\xecBm\xf3\x01\xca\xd0\xcdO\x17\x00\x10\xafc\xa9biFf\xd3W`\xb0w\xeb\xd5\x1d^\x050\x82\xe7C\xfeo\xfc;"r\t\'\x9d\xbb\x16\x99\xab\\4Ej$\rH\xbed\x88\xb7\x8bU\xc4\xa2t\xf2\xdc2V\xea\x18\xc2\xb6\xcc\xdb\xce!\xf5\x8e)\xb8\xfd\xf6AR\x1b\xbcq&\x1a-\x87\x06+\xc1\xdf\x02e\xaez\xba\xcb\x19\xe8\x13<\x9f\xe17\xe3\xb1\xd8\x94\xa19\xcfn\xdd\xd7%p}\x80\xff(\x15\x8a86\xde\xc7\xfa\x93\x83\x91\x0f\xb3L\x92\x81x{\x98\xb2\x04M\xd4\xbf\xd9\x0cv\x7fy\x90ka\xf8\xc5\xf9X\x08u\xe4\xa4\x96J@K\xa8\xc8\x85>\x1e\x9a\x1cD\x9b[\x1f\x86\xed\xd2\xa5,Q?\xd63\xa0\x0b/\xf4\xc3~\xb9\x14=Y.*\x11P\x9c\xad\xe2h\x84\xa7ZN\xda\x12\xf7\xe5\x07\xe6\x8c|\x95ST\xe9\xf0\xaa\xac'
    _notches = [112, 230, 254, 69, 179, 252, 2, 210, 53, 224, 38, 195, 61, 111, 75, 83]


class ByteII(_Base):
    _name = 'Byte Rotor II'
    _short = 'byte2'
    _wiring = b'5\x82\xb9i\x95\x8c\xb2\xc8\xb7\x97\xb8`!\x04\xa3\xccb[Z\x1d7\x94\xaa\xb0\xde\xa0p\xbcD\xbf,M\xc4Y2\x07J\x9d\xee_\xfa@\x1e\'\xdd^ej\x88\x1f\x18\xf5\xff\x1c$\xbb}\x14;\\\x90&\xba\x9f\xc5+\xab\x80\xa4\x0c\xef\x02\x7f\x9ao\x0f6gs]\x8d\xf9>\xd6\xa5\x83C\tq\xc7\x12\xc6/\xeb\xd9\x9e\xd3A\xd04OSr\xe7k\xd1\xc2\x98 =\x17\xbe\xec\xc3<\xcb\xed(\xe1\xb5\x81Q\n\x03\x96\x93\x84\x85\xdb0\x06\xe9\xceE:P\xf8\xa9\xe2L\xbdl"\xc1\xac\x1bK)\xfb\r\x15t\xd7\xae\x8a\xf2RTh\xea\x0b~\xf6\xady\xd4\xa2\xc9\xcd\xe0*\x00c\x13\x8b\xb3\x92\xe4\xb13\x19\x9b\xe8\xb41If\xa8n\xf7\x86\x8f%BvV\xda\xfdH\x91\x01\x08\xe3\xd5W\xf4\x1a9\xfc\xd2\xcaz\x99\xaf\x89\xa6\xc0\x87.\xd8-\xe5x\x11\x9cd\xf3\xa1|?\xf1N\xcfG\xdf{8\xdcwF\xe6Ua\xa7\x16\x0e\x05#\xfe\x10u\xf0\x8e\xb6Xm'
    _notches = [101, 62, 238, 225, 152, 135, 134, 65, 180, 59, 47, 77, 10, 231, 84, 227]


class ByteIII(_Base):
    _name = 'Byte Rotor III'
    _short = 'byte3'
    _wiring = b'\xfb\xbf\xb0\x04\xad\x82\x93\xee\xd7}\xe5~\x8b\xa2\xfew\xef\xcd\xe8\xb8*\x9a\x88h\xf0\']\xa4DA\x16F\xbc\x86\x89`\xcf\x81\xc1[\x91\xa8{2\xf3q\x87 \xbd\xf1\xa6\xb9\xa1\xb6\x15\xaa\xd6\xde\x13\xec&o\x8d\x92|\x02\x0c\xd0n;C\xf4\x98\t\xd16\xb4g\xb7\x14M:>ci\xcc\xd2.\xc5\x9b\x01N\x84\xd5R\x0eu\x96\nksfJ\xda\x94\xc6\x1d\xe6V\xaeK\xbb\xe2#"\xf7\xc2\x83\xf9\xdbL\x06pU\x05\x00\xca\x1c\xddb\xbe\xdf\x97l\xd8\xb1\xf8O\x90\x8c\x1b\xb3S\xa9-\xe9+z0\xce\xc7@\x80\xb54\x03,G\x9ddY\xba\xffm\xed8\xfc3\xea\x8f\r\xc9%\xf6\xc3\x1evP\x1a\x0bH\xa7_\xdc\x95\xf5W\xeb<\xe7$B\x08\x8e\x1fXje()a\xf2\xfa?=\x9fI\x07\x7f\\\xaf\xa5\x857Qy\x12T\xac\xa3\xc0\x10\xab\x9e\x9c\xe3\xe4x\xe1\x191\x17\x0ft9\xd4\xb2Z\xc4\xc8\x8a\xcb\x18!\xe0\x995\xfdr/E\xd9^\xa0\x11\xd3'
    _notches = [42, 246, 189, 77, 194, 75, 76, 158, 116, 100, 123, 104, 161, 101, 253, 111]


class ByteIV(_Base):
    _name = 'Byte Rotor IV'
    _short = 'byte4'
    _wiring = b'\'b\xa2\x8ah\x97~2\x17e \x08&\x7f\xbf\xf3\xac\x8d\xa3{\xbc\x07iy\x16\xf8\x01$\xc0\xcd\xc7\xec\xfa\xef\xa4G/\xed\x98\x93\xf2\xb9\x02\xd8\x0f\xfdR\x90E\xbb\xe7\x0b\xb7\x00(\xe5\x1a\xc3\x87r\xa0m\xeef\x188\xc2\x15M\x8c\xe6!\xba\xd2g\xc5\xe8\x99\xf7aV;\xd1\xca\x95\xc4c\xa5\xc13\x10\xa7\x96+N`\xd0\xfe<U\xdd\x9d\x04I%\x811Z|\xb8\xd9\xb5\x82\xb3B\xeb\x05"\x0c.\xcb\xc8l\xd5?\x8eFv]\xad-\xe1P\xf5\xb4w\xe0\x89\xfc\xaa\x1bu\xccdo\x88\xf6\xd3\xc6\xb1\x9b=9\x11\xf1_\xf4)\x86k\ts\x94\xae\xa6\xde\xafn\xe3\xe9O^\x06\n\x19\xd4\\p[5\xd7\xdb\xa9\r\x1cz\x1e*\xdc\x80\xfb40\x9f\xbdW\x9a\xe2\xb2\xa8\x1d#@\xbe\xf0K\x8f}\xceQ\x0e,6:A\x91\xc9\xa17\x03>\xb6\x83T\xfft\x85\x92S\x8b\x13\xcfxHL\x9e\xda\x1fX\x14Y\x9cD\xab\xf9\xd6J\x12Cj\xdf\xb0q\x84\xe4\xea'
    _notches = [48, 16, 125, 113, 192, 212, 68, 251, 90, 51, 67, 174, 112, 128, 82, 182]


class ByteV(_Base):
    _name = 'Byte Rotor V'
    _short = 'byte5'
    _wiring = b'\xd6\x1d\xe9\xe2\xf5t<\x98\xc8\x9bw \xda\x86\xf8%\x8b\xc9\xe5"\x180d\xd9\xa4\x9e\xa2.&\xb6\xdd\x979{\x10l\x13\xaf\xc2Gq\xa1\xb1\x7f:\x88\x8a5\nM\x92\x83\xab?s\x95@\x8ei\xcd\x03\xc4\x8c\xfeo\xcb\x96\xf4\x8f\x02fb\x05#\xa5\x1f+\\\xd8\xb5u\x94I\xc0\x84e\x1a8\xd5\x802\xf2[\xf9\x8d\xc6\xeay\xf6\xd7\xbe_\x1b\xad\xfaW\xb3\x89H/\x9fO\xa3\xde\x90r\xe0\x1c\x15\xd1\xe4\xb4=Q\x19P\xbc-\xdc\x00\x85}]\xa8\x16^\x04K\x91\xe7\xf7\xa7\x93\xb2C\x0e\x82\xffa\xfd\x9aS\xd2E\xb8v\xb7\x0b\x12\xac\xe1\x07Y\x14RN\xf3\xeex\x01\xbb\x08\xcc\x0f\t\'\xdb\x87\r\xf0,\xb07V\x1e>\xbdFJ$!\x17;~\xc5\xaa\xa9z\xec\xbf\xed\xe8g\xcaL\xce\xa6\x9c\xc7\xb96`m\xd3(\x99\xef\x9d\xeb3kAXn\xdfh1\xe6cTB\xc1|\xcf\xfb\xa0\xc3\xba*\xd4\xd0\x81\x06\xe3\x0cDZjp)\xfc\xf1\x11U4\xae'
    _notches = [5, 238, 11, 185, 129, 66, 99, 25, 193, 52, 140, 211, 34, 205, 22, 42]
