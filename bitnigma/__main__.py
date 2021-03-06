# stdlib imports
import argparse
import binascii
import datetime
import hashlib
import io
import sys
import uuid

# third party import
import click

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


# The root CLI method
@click.group()
def cliRoot():
    pass


# Command to generate a certificate file
@cliRoot.command(name='gencert')
@click.option('--seed', '-s', type=str)
@click.option('--seed-file', '-sf', type=click.File('rb'))
@click.option('--out', '-o', type=click.File('w'))
def commandGenerate(seed, seed_file, out):
    # You must have either a seed or a seed file
    if seed is None and seed_file is None:
        raise click.ClickException('You must specify one of the seed options.')

    # Create the random machine and hexlify its state
    machine = bitmachine.RandomMachine(
        seed_string=seed,
        seed_file=seed_file
    )
    machineState = machine.stateGet()
    stateHash = hashlib.blake2s(machineState).hexdigest()
    stateHex = binascii.hexlify(machineState).decode()

    # Generate the certificate document
    document = ''
    document += str(uuid.uuid4()) + '\n'
    document += datetime.datetime.utcnow().isoformat() + '\n'
    document += stateHash + '\n'
    document += stateHex

    # Write it to the output file, if supplied
    if out:
        out.write(document)
    else:
        click.echo(document)


# If this is the main script, invoke the CLI
if __name__ == '__main__':
    cliRoot()
