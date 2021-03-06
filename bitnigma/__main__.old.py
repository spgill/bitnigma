# stdlib imports
import argparse
import datetime
import io
import sys

# third party import

# local module imports
import bitnigma.machine as bitmachine
import bitnigma.rotors as rotors


def _serialize_plugboard(stack):
    """Serialize a plugboard stack back into character pairings"""
    pairs = [None for i in range(256)]

    # Yield the pairs that are not 1:1 and are not already present in reverse
    for i in range(256):
        if stack[i] != i:
            if not pairs[stack[i]]:
                pairs[i] = stack[i]
                yield '{0}:{1}'.format(i, stack[i])


def _serialize_notches(notches):
    """Serialize a rotor's notch matrix."""
    for i in range(256):
        if notches[i]:
            yield str(i)


def main():
    """Main method"""
    # Define the master parser
    parser = argparse.ArgumentParser(
        description='Process some data through a simulated Enigma machine'
    )

    # Rotor args
    parser.add_argument(
        '--plugboard', '-pl',
        nargs='+',
        default=[],
        type=str,
        required=False,
        help="""
        Specify a list of byte pairings for the plugboard.
        ex; 10:25 50:77 102:33
        """
    )
    parser.add_argument(
        '--rotors', '-ro',
        nargs='+',
        type=str,
        required=False,
        help="""
        Specify a list of rotors in the following format:
        SHORTNAME[:SETTING]
        ex; byte1:52
        """
    )
    parser.add_argument(
        '--reflector', '-rf',
        type=str,
        required=False,
        help="""
        Specify a reflector by its shortname.
        """
    )

    # State args
    parser.add_argument(
        '--state', '-s',
        type=str,
        default='',
        required=False,
        help="""
        Path for the state file (reading or writing). States can be used in
        lieu of manually specifying rotors and reflectors every time.
        """
    )
    parser.add_argument(
        '--state-create', '-sc',
        action='store_true',
        required=False,
        help="""
        Take the plugboard, rotor, and reflector args and save them to the
        state file (and then exit).
        """
    )
    parser.add_argument(
        '--state-update', '-su',
        action='store_true',
        required=False,
        help="""
        After processing, save the changed rotor state back to the state file.
        This allows for a continuous rotor progression over multiple
        program invocations. THERE IS NO ROLLBACK, SO BACK UP THE STATE.
        """
    )
    parser.add_argument(
        '--state-print', '-sp',
        action='store_true',
        required=False,
        help="""
        Print the state information to stdout and then exit.
        """
    )
    parser.add_argument(
        '--state-seed', '-ss',
        type=str,
        default='',
        required=False,
        help="""
        String seed for to create a randomly generated state.
        """
    )
    parser.add_argument(
        '--state-seed-file', '-ssf',
        type=str,
        default='',
        required=False,
        help="""
        File to use as seed for a randomly generated state.
        """
    )

    # Input args
    parser.add_argument(
        '--input', '-i',
        type=str,
        default='',
        required=False,
        help="""
        Input a string via this command line argument.
        """
    )
    parser.add_argument(
        '--input-std', '-is',
        action='store_true',
        required=False,
        help="""
        Read data from stdin pipe.
        """
    )
    parser.add_argument(
        '--input-path', '-ip',
        type=str,
        default='',
        required=False,
        help="""
        Open and read data from file path.
        """
    )

    # Output args
    parser.add_argument(
        '--output-std', '-os',
        action='store_true',
        required=False,
        help="""
        Write output to the stdout pipe.
        """
    )
    parser.add_argument(
        '--output-path', '-op',
        type=str,
        required=False,
        help="""
        Write output to the specified file path.
        """
    )

    # Other arguments
    parser.add_argument(
        '--chunk-size', '-c',
        type=int,
        default=128,
        required=False,
        help="""
        Chunk size for reading and writing data.
        """
    )
    parser.add_argument(
        '--benchmark', '-b',
        action='store_true',
        required=False,
        help="""
        Benchmark the processing time (prints results to stderr).
        """
    )
    parser.add_argument(
        '--progress', '-p',
        action='store_true',
        required=False,
        help="""
        Show the progress meter; written to stderr.
        """
    )

    if len(sys.argv) == 1:
        print('("--help" flag inferred from no args)\n')
        sys.argv.append('--help')
    args = parser.parse_args()

    # Initialize the enigma machine using specified rotors or a state file
    machine = None
    if args.state and not args.state_create:
        state = open(args.state, 'rb').read()
        machine = bitmachine.Machine(state=state)
    elif args.state_seed:
        machine = bitmachine.RandomMachine(seed_string=args.state_seed)
    elif args.state_seed_file:
        machine = bitmachine.RandomMachine(seed_file=args.state_seed_file)
    else:
        if not args.rotors or not args.reflector:
            raise ValueError('Rotors and reflectors were not provided')
        machine = bitmachine.Machine(
            plugboardStack=args.plugboard,
            rotorStack=args.rotors,
            reflector=args.reflector
        )

    # If a state file needs to be created, save it and exit
    if args.state_create:
        return open(args.state, 'wb').write(machine.stateGet())

    # If the state shall be printed, make it so, and exit
    if args.state_print:
        print('PLUGBOARD:', ' '.join(_serialize_plugboard(machine.plugboard)))
        for i, rotor in enumerate(machine.rotors):
            print(
                'ROTOR', i + 1, ':', rotor._name,
                'SETTING:', rotor.setting,
                'NOTCHES:', ', '.join(_serialize_notches(rotor.notches))
            )
        print('REFLECTOR:', machine.reflector._name)
        # print('RAW:', machine.stateGet())
        return

    # Work out the input
    input_file = None

    # input from the command-line
    if args.input:
        input_file = io.BytesIO(args.input.encode())

    # input from stdin
    elif args.input_std:
        input_file = sys.stdin.buffer

    # input from a file
    elif args.input_path:
        input_file = open(args.input_path, 'rb')

    # Make sure at least ONE input type was given
    if not (args.input or args.input_std or args.input_path):
        print('No input specified.')
        return

    # Now let's work out the output
    output_file = None

    # output to stdout
    if args.output_std:
        output_file = sys.stdout.buffer

    # output to a file
    elif args.output_path:
        output_file = open(args.output_path, 'wb')

    # Make sure at least ONE output type was given
    if not (args.output_std or args.output_path):
        print('No output specified.')
        return

    # get the size of the input
    input_file.seek(0, 2)
    input_size = input_file.tell()
    input_file.seek(0)

    time_start = datetime.datetime.utcnow()

    # Progress callback
    def callback(current, total):
        rs = ' '.join([f'0x{r.setting:02x}' for r in machine.rotors])
        p = min(int(current / total * 100.0), 100)
        sys.stderr.write(
            f'ROTORS: {rs} PROGRESS: {p}%     \r'
        )

    # Flip it off if needed
    if not args.progress:
        callback = None

    machine.translateStream(
        stream_in=input_file,
        stream_out=output_file,
        chunkSize=args.chunk_size,
        progressCallback=callback
    )

    # Add an extra return for the progress meter
    if callback:
        print()

    # Collect time for benchmarking
    if args.benchmark:
        time_stop = datetime.datetime.utcnow()
        time_delta = (time_stop - time_start).total_seconds()
        bps = input_size / time_delta
        kbps = input_size / time_delta / 1024.0
        mbps = input_size / time_delta / 1024.0 / 1024.0
        sys.stderr.write("""
{0} BYTES in {1:.2f} SECONDS
{2:>10.2f} BYTES/s
{3:>10.2f} KILOBYTES/s
{4:>10.2f} MEGABYTES/s
        """.format(input_size, time_delta, bps, kbps, mbps).strip())

    # Write back to the state file if asked to
    if args.state_update:
        if args.state:
            open(args.state, 'wb').write(machine.stateGet())

# Run if main
if __name__ == '__main__':
    main()
