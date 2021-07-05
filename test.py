import random
from datetime import datetime

import numpy as np  # numpy is required to make matrices
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
import time

from SimulatorFile.Dynamic import DynamicSimulator
from SimulatorFile.EnergyScan import EnergySimulator
from ExternalIO import getHelp, getRestriction, openLog


def test_diamond():
    a = np.zeros((15, 15))
    length = 3
    n = length
    c = 0  # for count
    start = (1, 6)
    a[start[0]][start[1]] = -1

    pos = 1

    # make upper diamond
    for i in range(0, n + 1):
        print(i)
        for j in range(-c + 1, c):
            print(i, j, (start[0] + i, start[1] + j - 1))
            a[start[0] + i][start[1] + j - 1] = pos
            pos += 1

        c += 1
    # make lower diamond
    for i in range(n + 1, 2 * (n + 1) + 1):
        for j in range(-c + 1, c):
            a[start[0] + i][start[1] - j - 1] = pos
            pos += 1

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


class A():
    def __init__(self):
        self.aa = 1
        self.bb = 2
        self.cc = None
        for parameter in self.__dict__:
            if self.__dict__[parameter] == None:
                raise RuntimeError("parameter {} is not set".format(parameter))

    def check(self):
        print("self.aa" in locals())
        print("cc" in locals())

    def b(self):
        self.cc = 3


def p():
    p = 1


def t():
    print(p)


def test_excel():
    from openpyxl import Workbook
    import time

    book = Workbook()
    sheet = book.active

    sheet['A1'] = 56
    sheet['A2'] = 43

    now = time.strftime("%x")
    sheet['A3'] = now

    # book.save("sample.xlsx")
    name = "Simulation type {} trail {}_{}.xlsx".format(str(3), 1,
                                                        datetime.now().strftime("%H-%M-%S"))
    file_path = "Result/" + name
    book.save(file_path)


def _output():
    """
        Output the simulation result into a file
        Copy from old code with minor change
        """
    startTime = datetime.now()
    time.sleep(3)

    # calculate the time use
    time_consume = (datetime.now() - startTime)
    time_consume = time_consume.seconds

    # creates excel file
    wb = Workbook()
    ws1 = wb.create_sheet("Results", 0)

    # naming the columns in the worksheet
    ws1.cell(1, 1, "Surface Characteristics:")
    ws1.cell(1, 2, "BacteriaFile Characteristics:")
    ws1.cell(1, 3, "FilmFile Seed # ")
    ws1.cell(1, 4, "BacteriaFile Seed # ")
    ws1.cell(1, 5, "Min Energy:")
    ws1.cell(1, 6, "Min X:")
    ws1.cell(1, 7, "Min Y:")
    ws1.cell(1, 8, "Surface Charge at Min Energy:")
    ws1.cell(1, 9, "Min Energy Gradient Strip: ")
    ws1.cell(1, 10, "Histogram: ")

    # create numbering for histogram plot
    count = 0
    for i in range(10, 31):
        ws1.cell(1, i, count)
        ws1.cell(2, i, 0)
        count += 1

    # adjust column width to text length
    for i in range(ws1.max_column):
        text = ws1.cell(1, i + 1).value
        if type(text) == int:
            text = str(text)
            column_width = len(text) + 1
        else:
            column_width = len(text)
        ws1.column_dimensions[get_column_letter(i + 1)].width = column_width

    # split the result
    min_energy, min_x, min_y, min_energy_charge, min_charge, min_charge_x, min_charge_y = (91, 92, 93, 94, 95, 96, 97)

    # shows the gradient lines position
    grad_strip = min_x // 500

    # write the result
    ws1.cell(3, 1, str(1) + " : " + str(2))
    ws1.cell(3, 2, str(1) + " : " + str(2))
    ws1.cell(3, 3, 3)
    ws1.cell(3, 4, 4)
    ws1.cell(3, 5, min_energy)
    ws1.cell(3, 6, min_x)
    ws1.cell(3, 7, min_x)
    ws1.cell(3, 8, min_energy_charge)
    ws1.cell(3, 9, grad_strip)
    ws1.cell(4, 9, time_consume)

    # special count for simulation type 2
    # save the excel file into folder result
    name = "Simulation type {} trail {}_{}.xlsx".format(str(2), 1, datetime.now().strftime("%H-%M-%S"))
    file_path = "Result/" + name
    wb.save(file_path)

def test3D():
    length = 5
    width = 5
    height = 5
    # finds center of array
    center = int(np.floor(length / 2)), int(np.floor(width / 2)), int(np.floor(height / 2))
    radius = min(np.floor(length / 2), np.floor(width / 2), np.floor(height / 2))
    # indexes the array
    index_x, index_y, index_z = np.indices((length, width, height))
    dist = ((index_x - center[0]) ** 2 + (index_y - center[1]) ** 2 + (index_z - center[2]) ** 2) ** 0.5
    return 1 * (dist <= radius) - 1 * (dist <= radius-1)

def testchange():
    dimension = 2
    arrayList = np.zeros((4,4))
    # init the list
    tupleList = []

    # depends on the dimension rephrase ndarray
    for x in range(len(arrayList)):
        for y in range(len(arrayList[x])):
            if dimension == 2:
                z = 3
                # Note, for 2D, the height of bacteria is fixed to 3, which means z-coordinate is 3
                position = (x, y, z, arrayList[x][y])
                tupleList.append(position)

            elif dimension == 3:
                raise NotImplementedError
            else:
                raise RuntimeError("Unknown dimension")

    return tupleList


def test_simulation():
    # get the help info
    helpDict = getHelp()

    # get special info dict, exec dict
    infoDict, execDict = getRestriction()

    # get log file
    openLog()

    simulationType = 1
    trail = 1
    dimension = 2
    filmSeed = 1
    filmSurfaceSize = (10, 10)
    filmSurfaceShape = "rectangle"
    filmNum = 1
    bacteriaNum = 10
    interval_x = 50
    interval_y = 50
    filmSurfaceCharge = 0
    filmDomainSize = (1, 1)
    filmDomainShape = "cross"
    filmDomainCon = 0.5
    filmDomainChargeConcentration = 0.5
    bacteriaSeed = 10
    bacteriaSize = (5, 5)
    bacteriaSurfaceShape = "rectangle"
    bacteriaSurfaceCharge = 0
    bacteriaDomainSize = (1, 1)
    bacteriaDomainShape = "single"
    bacteriaDomainCon = 0.5
    bacteriaDomainChargeConcentration = 0.5

    ### below is new variable
    simulatorType = 1
    interactType = "DOT"

    # below are for dynamic simulation, we are not using for now
    probabilityType = ""
    timestep = ""

    # take info for simulator
    if simulatorType == 1:
        simulator = EnergySimulator
        # taking info for energy scan simulation
        parameter = {"interactType": interactType}

    elif simulatorType == 2:
        simulator = DynamicSimulator
        # taking info for dynamic simulation
        parameter = {"probabilityType": probabilityType, "timestep": timestep}
    else:
        raise RuntimeError("Unknown simulator type")

    # generate simulator
    sim = simulator(simulationType, trail, dimension,
                    filmSeed, filmSurfaceSize, filmSurfaceShape, filmSurfaceCharge,
                    filmDomainSize, filmDomainShape, filmDomainCon, filmDomainChargeConcentration,
                    bacteriaSeed, bacteriaSize, bacteriaSurfaceShape, bacteriaSurfaceCharge,
                    bacteriaDomainSize, bacteriaDomainShape, bacteriaDomainCon, bacteriaDomainChargeConcentration,
                    filmNum, bacteriaNum, interval_x, interval_y)

    sim.setExtraParameter(parameter)
    sim.runSimulate()

def testVisible():
    from matplotlib import pyplot as plt
    data = np.zeros((100, 100))
    data[2][2] = 1
    data[1][1] = -1
    pos = np.where(data == 1)
    neu = np.where(data == 0)
    neg = np.where(data == -1)

    pos_x = pos[0]
    pos_y = pos[1]
    neu_x = neu[0]
    neu_y = neu[1]
    neg_x = neg[0]
    neg_y = neg[1]

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111)

    ax.scatter(pos_x, pos_y, c='blue', label='pos')
    ax.scatter(neu_x, neu_y, c='green', label='neu')
    ax.scatter(neg_x, neg_y, c='red', label='neg')
    ax.legend(loc="upper right")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')

    plt.imshow(data, interpolation='nearest')
    plt.show()
    plt.savefig("test.png")

def testPic():
    from ExternalIO import visPlot
    data = np.zeros((100, 100))
    np.reshape(data, (-1,))
    data[2][2] = 1
    data[1][1] = -1

    picName = "test"

    visPlot(data, picName)

if __name__ == '__main__':
    # test_diamond()
    # test_random_choice()

    # a = A()
    # print(a.__dict__)
    # a.check()

    # a = 12
    # t()

    # test_excel()

    # _output()

    test_simulation()

    # p = p()
    # t()

    # print(test3D())

    # print(testchange())

    # testVisible()

    # testPic()