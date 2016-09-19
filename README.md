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
* Developed and tested on Python 3.5.2 for Windows.
    * support for other versions and operating systems is likely, but not guaranteed.
* Designed to be run as a module, but can be initiated from the ```__main__.py``` script.
* Can be imported and used in your own applications, but no documentation is provided yet (though it shouldn't be too hard to figure out).
* Requires ```requests``` module and internet connection to build (because of the markdown conversion).

Downloading
---
This package is now available on PyPI, and may be installed using ```pip install bitnigma``` or
directly from the repo using ```pip install git+git://github.com/spgill/bitnigma```.


Usage
---
```
usage: __main__.py [-h] [--plugboard PLUGBOARD [PLUGBOARD ...]]
                   [--rotors ROTORS [ROTORS ...]] [--reflector REFLECTOR]
                   [--state STATE] [--state-create] [--state-update]
                   [--state-print] [--state-seed STATE_SEED]
                   [--state-seed-file STATE_SEED_FILE] [--input INPUT]
                   [--input-std] [--input-path INPUT_PATH] [--output-std]
                   [--output-path OUTPUT_PATH] [--chunk-size CHUNK_SIZE]
                   [--benchmark] [--no-progress]

Process some data through a simulated Enigma machine

optional arguments:
  -h, --help            show this help message and exit
  --plugboard PLUGBOARD [PLUGBOARD ...], -p PLUGBOARD [PLUGBOARD ...]
                        Specify a list of byte pairings for the plugboard. ex;
                        10:25 50:77 102:33
  --rotors ROTORS [ROTORS ...], -ro ROTORS [ROTORS ...]
                        Specify a list of rotors in the following format:
                        SHORTNAME[:SETTING] ex; byte1:52
  --reflector REFLECTOR, -rf REFLECTOR
                        Specify a reflector by its shortname.
  --state STATE, -s STATE
                        Path for the state file (reading or writing). States
                        can be used in lieu of manually specifying rotors and
                        reflectors every time.
  --state-create, -sc   Take the plugboard, rotor, and reflector args and save
                        them to the state file (and then exit).
  --state-update, -su   After processing, save the changed rotor state back to
                        the state file. This allows for a continuous rotor
                        progression over multiple program invocations. THERE
                        IS NO ROLLBACK, SO BACK UP THE STATE.
  --state-print, -sp    Print the state information to stdout and then exit.
  --state-seed STATE_SEED, -ss STATE_SEED
                        String seed for to create a randomly generated state.
  --state-seed-file STATE_SEED_FILE, -ssf STATE_SEED_FILE
                        File to use as seed for a randomly generated state.
  --input INPUT, -i INPUT
                        Input a string via this command line argument.
  --input-std, -is      Read data from stdin pipe.
  --input-path INPUT_PATH, -ip INPUT_PATH
                        Open and read data from file path.
  --output-std, -os     Write output to the stdout pipe.
  --output-path OUTPUT_PATH, -op OUTPUT_PATH
                        Write output to the specified file path.
  --chunk-size CHUNK_SIZE, -c CHUNK_SIZE
                        Chunk size for reading and writing data.
  --benchmark, -b       Benchmark the processing time (prints results to
                        stderr).
  --no-progress, -np    Suppress the progress meter that is normally written
                        to stderr.

```
