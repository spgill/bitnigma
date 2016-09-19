# stdlib imports
import array
import io
import pickle
import random
import sys

# third party imports

# local module imports
import bitnigma.rotors as rotors
import bitnigma.reflectors as reflectors


class Machine:
    def __init__(
            self,
            plugboardStack=[],
            rotorStack=[],
            reflector=None,
            state=None
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
            x = 0
            y = 0

            # If a string pairing
            if isinstance(pair, str):
                [x, y] = [int(n) for n in pair.split(':')]

            # Else, must be some sort of list
            else:
                [x, y] = pair

            # Store them in the plugboard
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

    def stateGet(self):
        """Get a serialized state of the machine.

        Results in a byte string that is (513 + i * (258 + j)) bytes long,
        where i is the number of rotors in the machine, and j is the number
        of notches in each rotor.
        """
        # Start with a blank buffer
        state = io.BytesIO()

        # Write the plugboard config
        state.write(self.plugboard)

        # Write the number of rotors
        state.write(bytes([len(self.rotors)]))

        # Iterate through the rotors
        for r in self.rotors:

            # Write the wiring
            state.write(r.initial_wiring)

            # Write the number of notches
            state.write(bytes([len(r.initial_notches)]))

            # Write the actual notches
            state.write(bytes(r.initial_notches))

            # Write the rotor setting
            state.write(bytes([r.setting]))

        # Write the reflector wiring
        state.write(self.reflector.initial_wiring)

        # Return it all
        state.seek(0)
        return state.read()

    def stateSet(self, state):
        """Set the state of the machine from a serialized input"""
        # First, let's read it into a buffer
        state = io.BytesIO(state)

        # Unpack the plugboard
        self.plugboard = array.array('B', state.read(256))

        # Get the number of rotors
        rotor_count = state.read(1)[0]

        # Iterate through and unpack the rotors
        for i in range(rotor_count):

            # Unpack the wiring
            wiring = state.read(256)

            # Get the notches
            notch_count = state.read(1)[0]
            notches = state.read(notch_count)

            # Lastly, get the setting
            setting = state.read(1)[0]

            # Wrap it all up into a Custom rotor instance
            self.rotors.append(rotors.Custom(wiring, notches, setting))

        # Unpack and initialize the reflector
        self.reflector = reflectors.Custom(state.read(256))

        # Last but not least, we must link the components
        self._link()

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


class RandomMachine(Machine):
    """Bitnigma machine randomly generated from a string seed."""

    # Arbitrarily chosen default parameters of random generation
    _defaultconfig = {
        'plugs_min': 0,
        'plugs_max': 128,
        'rotor_count': 3,
        'rotor_notch_min': 1,
        'rotor_notch_max': 3
    }

    def __init__(self, seed_string=None, seed_file=None, override={}):
        """Initialize the random machine."""
        # Seed the random generator
        if seed_string:
            random.seed(seed_string)
        elif seed_file:
            seed_obj = seed_file
            if isinstance(seed_file, str):
                seed_obj = open(seed_file, 'rb')
            random.seed(seed_obj.read())
        else:
            raise RuntimeError('No seed given to RandomMachine')

        # Figure out the config params
        config = self._defaultconfig.copy()
        config.update(override)

        # Generate a random plugboard
        random_plugboard = []
        population_plugboard = {i for i in range(256)}
        for i in range(random.randint(config['plugs_min'], config['plugs_max'])):
            pair = [x, y] = random.sample(population_plugboard, 2)
            [population_plugboard.remove(z) for z in pair]
            random_plugboard.append(pair)

        # Generate random rotors
        random_rotors = []
        population_rotors = bytes([i for i in range(256)])
        for i in range(config['rotor_count']):
            random_rotors.append(rotors.Custom(
                wiring=bytearray(random.sample(population_rotors, 256)),
                notches=random.sample(population_rotors, random.randint(config['rotor_notch_min'], config['rotor_notch_max'])),
                setting=random.randint(0, 255)
            ))

        # Pick a random reflector
        population_reflector = {i for i in range(256)}
        reflector_wiring = [None for i in range(256)]
        for i in range(128):
            pair = [x, y] = random.sample(population_reflector, 2)
            [population_reflector.remove(z) for z in pair]
            reflector_wiring[x] = y
            reflector_wiring[y] = x
        random_reflector = reflectors.Custom(wiring=bytearray(reflector_wiring))

        # Initialize actual machine
        super().__init__(random_plugboard, random_rotors, random_reflector)
