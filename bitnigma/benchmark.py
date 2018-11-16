# stdlib imports
import datetime
import io
import secrets
import time

# vendor imports

# local imports
import bitnigma.machine


print('Creating a randomized standard three rotor machine...')
seed = datetime.datetime.utcnow().isoformat()
print('  seed string:', seed)
machine = bitnigma.machine.RandomMachine(
    seed_string=seed,
)
initialState = machine.stateGet()
print('  state recorded')


iterations = 10
stages = [
    ('1 KiB', 1024 * 1),
    ('32 KiB', 1024 * 32),
    # ('256 KiB', 1024 * 256),
    # ('1 MiB', (1024 ** 2) * 1),
    # ('2 MiB', (1024 ** 2) * 2),
    # ('4 MiB', (1024 ** 2) * 2),
]

results = []

for i, (stageLabel, stageBytes) in enumerate(stages):
    print(f'Stage {i + 1}: {iterations} iterations of {stageLabel}')
    results.append([])
    for j in range(iterations):
        print(f'  Iteration {j + 1}')
        print(f'    generating {stageLabel} of random data...')
        source = io.BytesIO(
            secrets.token_bytes(stageBytes)
        )
        noop = io.BytesIO()
        print('    resetting machine state...')
        machine.stateSet(initialState)
        print('    running translation...')
        start = time.perf_counter_ns()
        machine.translateStream(source, noop)
        end = time.perf_counter_ns()
        results[i].append(end - start)
        print(f'    translation took ~{end - start}ns')

        del source, noop
        # exit()

    print()


print('Results;')
for i, (stageLabel, stageBytes) in enumerate(stages):
    mean = sum(results[i]) / len(results[i])
    seconds = mean / 1e9
    print(f'  {stageLabel} took on average {round(seconds, 2)}s')


nspbSum = 0
nspbCount = 0
for i, (stageLabel, stageBytes) in enumerate(stages):
    for ns in results[i]:
        nspbSum += ns / stageBytes
        nspbCount += 1

nspb = nspbSum / nspbCount
spb = nspb / 1e9
bps = 1 / spb

print()
print('Speed ratings;')
for i, measure in enumerate(['B', 'KiB', 'MiB']):
    rate = bps / (1024 ** i)
    print(f'  {round(rate, 2)} {measure}/s')
