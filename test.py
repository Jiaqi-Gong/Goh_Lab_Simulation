import random

import numpy as np  # numpy is required to make matrices


def test_diamond():
    a = np.zeros((20, 20))
    length = 8
    n = length
    c = 0  # for count
    start = (1, 8)

    # make upper diamond
    for i in range(0, n + 1):
        for j in range(-c + 1, c):
            a[start[0] + i][start[1] + j] = 1

        c += 1
    # make lower diamond
    for i in range(n + 1, 2 * (n + 1) + 1):
        for j in range(-c + 1, c):
            a[start[0] + i][start[1] - j] = 1

        c -= 1

    print(a)

def test_random_choice():
    a = np.zeros((20, 20))

    surfaceWidth = 10
    surfaceLength = 10

    domainWidth = 3
    domainLength = 3

    x = random.randint(domainWidth, surfaceWidth - domainWidth)
    y = random.randint(domainLength, surfaceLength - domainLength)







#test_diamond()
test_random_choice()

