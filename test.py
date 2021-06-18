import random
from datetime import datetime

import numpy as np  # numpy is required to make matrices
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
import time

from ExternalIO import getHelp, getRestriction, openLog
from MainSimulation import Simulation


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

    def check(self):
        print("self.aa" in locals())
        print("cc" in locals())

    def b(self):
        self.cc = 3

def t():
    print(a)

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
        ws1.cell(1, 2, "Bacteria Characteristics:")
        ws1.cell(1, 3, "Film Seed # ")
        ws1.cell(1, 4, "Bacteria Seed # ")
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
        min_energy, min_x, min_y, min_energy_charge, min_charge, min_charge_x, min_charge_y = (91,92,93,94,95,96,97)

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
    filmSurfaceSize = (20, 20)
    filmSurfaceShape = "rectangle"
    filmNum = 1
    bacteriaNum = 1
    interval_x = 50
    interval_y = 50
    filmSurfaceCharge = 0
    filmDomainSize = (5,5)
    filmDomainShape = "diamond"
    filmDomainCon = 0.5
    bacteriaSeed = 10
    bacteriaSize = (5, 5)
    bacteriaSurfaceShape = "rectangle"
    bacteriaSurfaceCharge = 0
    bacteriaDomainSize = (1,1)
    bacteriaDomainShape = "diamond"
    bacteriaDomainCon = 0.5

    sim = Simulation(simulationType, trail, dimension,
                     filmSeed, filmSurfaceSize, filmSurfaceShape, filmSurfaceCharge,
                     filmDomainSize, filmDomainShape, filmDomainCon,
                     bacteriaSeed, bacteriaSize, bacteriaSurfaceShape, bacteriaSurfaceCharge,
                     bacteriaDomainSize, bacteriaDomainShape, bacteriaDomainCon, filmNum, bacteriaNum,
                     interval_x, interval_y)

    sim.runSimulate()

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


