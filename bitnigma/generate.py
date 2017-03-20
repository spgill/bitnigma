import random
import sys

population = bytes([i for i in range(256)])

if sys.argv[1] == 'reflector':
    print('WIRING')
    popset = set(population)
    buffer = [None for i in range(256)]
    for i in range(128):
        x, y = random.sample(popset, 2)
        popset.remove(x)
        popset.remove(y)
        buffer[x] = y
        buffer[y] = x
    print(bytes(buffer))

elif sys.argv[1] == 'rotor':
    print('WIRING')
    print(bytes(random.sample(population, 256)))
    print('NOTCHES')
    print(random.sample(population, random.randint(10, 20)))

elif sys.argv[1] == 'pattern':
    with open(sys.argv[2], 'wb') as file:
        total = eval(sys.argv[3])
        pattern = bytes([int(i) for i in sys.argv[4:]])
        count = 0
        while count < total:
            remaining = total - count
            if len(pattern) > remaining:
                file.write(pattern[:remaining])
            else:
                file.write(pattern)
            count += len(pattern)
