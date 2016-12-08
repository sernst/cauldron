import sys


def make_gen():
    yield 1
    yield 2
    yield 3
    yield 4


for value in make_gen():
    if value < 3:
        continue

    print('Found:', value)
    break

for value in make_gen():
    if value < 2:
        continue

    print('Found:', value)
    break

