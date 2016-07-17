# stdlib imports
import array
import io
import pickle
import random
import sys

# third party imports

# local module imports
import rotors
import reflectors


class Machine:
    def __init__(
            self,
            plugboardStack=[],
            rotorStack=[],
            reflector=None,
            state=None,
            stateSeed=''
            ):
        """Initialize a new Enigma Machine.

        Keyword arguments;
        -   plugboardStack
        """
        # Initialize the empty variables
        self.plugboard = []
        self.rotors = []
        self.reflector = None

        # Unpack the state
        if state:
            self.stateSet(state)

        # If seed is present, generate randomized state
        elif stateSeed:
            self.stateRandom(stateSeed)

        # or unpack the args into the class
        else:
            self._initPlugboard(plugboardStack)
            self._initRotors(rotorStack)
            self._initReflector(reflector)

        # Link all of the rotors and reflectors together
        self._link()

        # go ahead and set a break point
        self.breakSet()

    def _initPlugboard(self, stack):
        '''Initialize the plugboard translation matrix'''
        # Start with an untampered matrix
        self.plugboard = array.array('B', [i for i in range(256)])

        # Swap up the mappings for each desired pair
        for pair in stack:
            x = pair[0]
            y = pair[1]
            self.plugboard[x] = y
            self.plugboard[y] = x

    def _initRotors(self, stack):
        '''Check the passed rotors to see if they're strings or real rotors'''
        for i, entry in enumerate(stack):

            rotor = None

            # if it's an actual rotor instance, keep on swimming
            if isinstance(entry, rotors._Base):
                rotor = entry

            # if it's a string, turn it into a rotor
            if isinstance(entry, str):
                rotor = rotors.fromString(entry)

            # Must be invalid then
            if rotor is None:
                raise TypeError(
                    'Unknown type of rotor passed into the machine'
                )

            # Make sure the rotor matches the mode
            if len(rotor._wiring) < 256:
                raise ValueError(
                    'Rotor is not byte-compatible'
                )

            # Append it, yo
            self.rotors.append(rotor)

    def _initReflector(self, reflector):
        '''Check to make sure a real reflector was passed in'''
        # if it's an actual reflector instance, keep on swimming
        if isinstance(reflector, reflectors._Base):
            self.reflector = reflector

        # if it's a string, turn it into a reflector
        if isinstance(reflector, str):
            self.reflector = reflectors.fromString(reflector)

        # Must be invalid then
        if self.reflector is None:
            raise TypeError(
                'Unknown type of reflector passed into the machine'
            )

        # Make sure the reflector matches the mode
        if len(self.reflector._wiring) < 256:
            raise ValueError(
                'Reflector is not byte-compatible'
            )

    def _link(self):
        """Link the rotors and reflectors together in a node-like fashion"""
        # Link the rotors forward
        for i in range(len(self.rotors))[:-1]:
            self.rotors[i].next = self.rotors[i + 1]

        # Link the rotors backwards
        for i in range(len(self.rotors))[1:]:
            self.rotors[i].previous = self.rotors[i - 1]

        # Link the reflector into the loop
        self.rotors[-1].next = self.reflector
        self.reflector.previous = self.rotors[-1]

    def hexdump(self, data, spaced=False):
        if not hasattr(data, 'read'):
            data = io.BytesIO(data)
        w = sys.stdout.write

        def spacer():
            w('\n')
            w('  offset  ')
            w(' '.join('%02x' % i for i in range(16)))
            w('\n')
            w('          _______________________________________________\n')

        spacer()
        chunk = data.read(16)
        count = 0
        i = 0

        while chunk:
            count += len(chunk)
            if i % 16 == 0 and i > 0 and spaced:
                spacer()

            w('%08x |' % (i*16))
            w(' '.join('%02x' % j for j in chunk))
            w('\n')
            chunk = data.read(16)
            i += 1

        w('\nTotal bytes: ' + str(count) + '\n')
        w('\n')

    def stateGet(self):
        '''Get a serialized state of the machine. (the 'settings')'''
        s = pickle.dumps((
            self.plugboard,
            self.rotors,
            self.reflector
        ), -1)
        return s

        # state = io.BytesIO()
        # state.write(self.plugboard)
        # state.write(bytes([len(self.rotors)]))
        # for r in self.rotors:
        #     state.write(r._wiring)
        #     state.write(r.notches)
        #     state.write(bytes([r.setting]))
        #
        # state.write(self.reflector._wiring)

    def stateSet(self, state):
        '''Set the state of the machine from a serialized input'''
        (
            self.plugboard,
            self.rotors,
            self.reflector
        ) = pickle.loads(state)

    def stateRandom(self, seed):
        """Randomly generate a state from a string seed"""
        # Seed the random generator
        random.seed(seed)

        # Generate a random plugboard
        plugboardStack = []
        abet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        for i in range(random.randint(0, 13)):
            pair = ''
            for j in range(2):
                k = random.randrange(0, len(abet))
                pair += abet[k]
                del abet[k]
            plugboardStack.append(pair)
        self._initPlugboard(plugboardStack)

        # Generate random rotors (there will always be three)
        rotorStack = []
        abet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        rotorNames = sorted(
            [r._short for r in rotors._RotorBase.__subclasses__()]
        )
        rotorNames.remove('base-ref')
        for i in range(3):
            rotor = '{0}:{1}:{2}'.format(
                random.choice(rotorNames),
                random.choice(abet),
                random.choice(abet)
            )
            rotorStack.append(rotor)
        self._initRotors(rotorStack)

        # Pick a random reflector
        reflNames = sorted(
            [r._short for r in rotors._ReflectorBase.__subclasses__()]
        )
        reflector = random.choice(reflNames)
        self._initReflector(reflector)

    def breakSet(self):
        '''Save the current state to be easily returned to later'''
        self._breakstate = self.stateGet()

    def breakGo(self):
        '''Return to the saved break state'''
        assert hasattr(self, '_breakstate')
        self.stateSet(self._breakstate)

    def translatePin(self, pin):
        """
        Translate a singular pin (as an integer) through the plugboard,
        rotors, reflector, and back again.
        """
        # Isolate the first (maybe only) rotor
        rotor = self.rotors[0]

        # Forward through the plugboard
        pin = self.plugboard[pin]

        # Send the pin through the rotors
        pin = rotor.translate(pin)

        # Backwards through the plugboard
        pin = self.plugboard[pin]

        # Step the rotors
        rotor.step()

        # Return the fruits of our labor
        return pin

    def translateChunk(self, chunk_in):
        """
        Translate a non-empty bytes or bytearray object through the machine.
        """
        # Initialize the outgoing chunk
        chunk_out = array.array('B')

        # For bytes, this is super easy
        for byte_in in chunk_in:
            chunk_out.append(self.translatePin(byte_in))

        # Return the processed chunk
        return chunk_out

    def translateString(self, s, **kwargs):
        """Lazy method to translate a string"""
        return str(self.translateChunk(bytes(s), **kwargs))

    def _readChunks(self, stream, chunkSize):
        """Yield discrete chunks from a stream."""
        while True:
            data = stream.read(chunkSize)
            if not data:
                break
            yield data

    def _streamSize(self, stream):
        """Return the size of a stream in bytes"""
        stream.seek(0, 2)
        size = stream.tell()
        stream.seek(0)
        return size

    def translateStream(
            self,
            stream_in,
            stream_out=None,
            progressCallback=None,
            chunkSize=128,
            **kwargs
            ):
        """Translate a stream (file-like object) chunk by chunk."""
        # Figure out the size of the input stream
        stream_in_size = self._streamSize(stream_in)

        # If no outgoing stream is specified, make one
        if not stream_out:
            stream_out = io.BytesIO()
        stream_out_size = 0

        # Make the initial call to the progress function
        if progressCallback:
            progressCallback(stream_out_size, stream_in_size)

        # Iterate through chunks
        for chunk_in in self._readChunks(stream_in, chunkSize):
            chunk_out = self.translateChunk(chunk_in, **kwargs)
            stream_out.write(chunk_out)
            stream_out_size += chunkSize
            if progressCallback:
                progressCallback(stream_out_size, stream_in_size)

        # Return the outgoing stream (in case one wasn't passed in)
        return stream_out
