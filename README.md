<img src="https://raw.githubusercontent.com/spgill/bitnigma/master/icon.png" height="256">
Enigma Byte Machine
===
Using the same principles that [my 'classic' Enigma simulation](http://github.com/spgill/enigma)
is built on; I reverse-engineered a newer, stronger, more robust Enigma encryption scheme that
is capable of encoding any standard 8-bit character (also known as a byte).
By removing the 26 character limitation, we are now able to encrypt entire binary files
using the same basic mechanics as the original Enigma machine.

Technical Details
---
* Developed and tested on Python 3.5.2 for Windows
    * support for other versions and operating systems is likely, but not guaranteed
* Designed to be run as a module, but can be initiated from the ```__main__.py``` script

Downloading
---
This package is not currently available on PyPI, but may be installed using ```pip``` with the following command;

```pip install git+git://github.com/spgill/bitnigma```

Usage
---
```
usage: bitnigma [-h] [--plugboard PLUGBOARD [PLUGBOARD ...]]
                [--rotors ROTORS [ROTORS ...]] [--reflector REFLECTOR]
                [--state STATE] [--state-create] [--state-update]
                [--state-print] [--state-seed STATE_SEED] [--input INPUT]
                [--input-std] [--input-path INPUT_PATH] [--input-bz2]
                [--output-std] [--output-path OUTPUT_PATH] [--output-bz2]
                [--chunk-size CHUNK_SIZE] [--benchmark] [--no-progress]
                [--verbose] [--typewriter]

Process some data through a simulated Enigma machine

optional arguments:
  -h, --help            show this help message and exit
  --plugboard PLUGBOARD [PLUGBOARD ...], -p PLUGBOARD [PLUGBOARD ...]
                        Specify a list of character pairings for the
                        plugboard. ex; AB CF HJ
  --rotors ROTORS [ROTORS ...], -ro ROTORS [ROTORS ...]
                        Specify a list of rotors in the following format:
                        SHORTNAME[:SETTING[:NOTCHES]] ex; com1:C:QV
  --reflector REFLECTOR, -rf REFLECTOR
  --state STATE, -s STATE
                        Path for the state file (loading or creating). Can be
                        used in lieu of manually specifying rotors and
                        reflectors.
  --state-create, -sc   Take the rotor and reflector args and save it to the
                        state file.
  --state-update, -su   After processing, save the changed rotor state back to
                        the state file. This allows for a continuous rotor
                        progression over multiple script invocations. THERE IS
                        NO ROLLBACK, SO BACK IT UP.
  --state-print, -sp    Print the state information to stdout and exit.
  --state-seed STATE_SEED, -ss STATE_SEED
                        String seed for a randomly generated state.
  --input INPUT, -i INPUT
                        Input a string via this command line argument.
  --input-std, -is      Read data from stdin pipe.
  --input-path INPUT_PATH, -ip INPUT_PATH
                        Open and read data from file path.
  --input-bz2, -iz      Run input through BZ2 decompression before processing.
  --output-std, -os     Write output to the stdout pipe.
  --output-path OUTPUT_PATH, -op OUTPUT_PATH
                        Write output to the specified file path.
  --output-bz2, -oz     Run output through BZ2 compression before writing.
  --chunk-size CHUNK_SIZE, -c CHUNK_SIZE
                        Chunk size for reading and writing data.
  --benchmark, -b       Benchmark the processing time (prints results to
                        stderr).
  --no-progress, -np    Suppress the progress meter that is normal written to
                        stderr.
  --verbose, -v         Enable verbosity; printing LOTS of messages to stderr.
```
