"""
This program is generating the domain with some charge on it
Can be used for 2D, 3D and for testing surface, bacteria surface
"""
from numpy import ndarray
import numpy as np
from SurfaceGenerator.Surface import Surface
from typing import Tuple, List
from ExternalIO import showMessage, writeLog
import math
import time


class DomainGenerator:
    """
    This class is used to generate the domain on the surface passed in
    """
    # Declare the type of all variable
    seed: int

    def __init__(self, seed: int):
        """
        Init this domain generate
        :param seed: seed for random, if using same seed can repeat the simulation
        """
        self.seed = seed

    def generateDomain(self, surface: Surface, shape: str, size: Tuple[int, int], concentration: float,
                       charge_concentration: float) -> ndarray:
        """
        This function takes in a surface, shape and size of domain want to generate on the surface

        Introduced a new parameter called charge_concentration which determines the
        concentration of +ve and -ve charge on domain -> can change name later
        The charge_concentration is assumed to be the charge concentration of positives

        :param surface: the surface want to generate the domain
        :param shape: shape of the domain
        :param size: size of the surface, in unit micrometer, 1micrometer = 100 points, NOTICE: size of domain must smaller than surface
        :param concentration: concentration of the charge
        :return: return the surface with wanted domain on it
        """
        writeLog("This is function generateDomain in Domain.py")
        showMessage("Start to generate domain ......")
        writeLog([self.__dict__, surface.__dict__, shape, size, concentration])

        # get size
        domainLength = size[0] * 100
        domainWidth = size[1] * 100

        # calculate how many domain should generate
        # calculation for the number of domains which needs to be generated depends on the shape of the domain
        # set corresponding check and generate function
        # generate the corresponding domain shape

        # more shape coming soon, leave for more extension

        if shape.upper() == "DIAMOND":
            generateShape = self._generateDiamond
            # Number of domains
            domainNum = int((surface.length * surface.width * concentration) / (domainWidth * domainLength))
        elif shape.upper() == "CROSS":
            generateShape = self._generateCross
            # Number of domains
            domainNum = int((surface.length * surface.width * concentration) / (2 * domainWidth + 2 * domainLength))
        elif shape.upper() == "OCTAGON":
            generateShape = self._generateOctagon
            # Number of domains
            domainNum = int((surface.length * surface.width * concentration) / (
                        2 * (1 + math.sqrt(2)) * domainWidth * domainLength))
        elif shape.upper() == "SINGLE":
            generateShape = self._generateSingle
            # Number of domains
            domainNum = int(surface.length * surface.width * concentration)
        else:
            raise RuntimeError("Unknown shape")

        showMessage("Domain number is: {}".format(domainNum))

        # first, make entire passed in surface positive
        # This surface is neutral
        # newSurface = self._makeSurfaceNeutral(surface)
        newSurface = surface.originalSurface[:]

        # record info into log
        showMessage("generate new surface done")
        writeLog(newSurface)

        # init generated domain number
        generated = 0

        # set seed for random
        np.random.seed(self.seed)

        showMessage("Start to generate domain on the surface")
        writeLog(surface)

        # check generate domain number is not too small
        if generated >= domainNum:
            raise RuntimeError("Domain concentration is too low")

        # Initialize the charge count (NOTE: charge count is a list with the first element being positive charge
        # while second element being negative charge)
        count_charge = [0, 0]

        # Initialize total number of positive and negative charge needed on the surface
        total_charge = self._totalNumberCharge(surface, concentration, charge_concentration)

        # start to generate the domain on surface
        while generated < domainNum:
            start_time = time.time()
            # pick a point in the matrix as the start point of generate domain
            # randint pick x and y, leave the enough space for not touching the edge
            start = self._randomPoint(surface.length, surface.width, domainLength, domainWidth, shape)

            # generate this shape's domain
            [newSurface, count_charge] = generateShape(newSurface, domainWidth, domainLength, start,
                                                       charge_concentration, count_charge)

            # update generated number
            if shape.upper() == "SINGLE":
                generated += 5
            else:
                generated += 1

            total_time = time.time() - start_time

            # showMessage("Generated number is: {}".format(generated))
            # showMessage("Time it took to generate is: {} seconds".format(total_time))

        showMessage("Domain generated done")

        newSurface = self._balanceCharge(count_charge, newSurface, domainLength, domainWidth, total_charge)

        writeLog(newSurface)
        # return the surface generated based on k value
        return newSurface

    def _balanceCharge(self, count_charge: List[int,int], surface: Surface, domainLength: int, domainWidth: int, total_charge: List[int,int]) -> ndarray:
        """
        This function is used to balance any excess or lack charge for the surface
        To do this, this function will take in the domain shape and continue to generate/remove it until it reaches the proper charge count
        """
        showMessage("Generating/removing remaining charges....")
        writeLog("number of +ve and -ve charge before generation/removal {}".format(count_charge))
        # generate additional charge spots on the surface if needed
        if count_charge[0] < total_charge[0] or count_charge[1] < total_charge[1]:
            # positive charge
            while count_charge[0] < total_charge[0]:
                # pick a random point within the range
                # if the surface is 2D, then we can pass in surfaceHeight as zero
                # otherwise, if the surface is 3D, then we pass in the surfaceHeight of the surface
                if surface.dimension == 2:
                    (x,y,z) = self._randomPoint(surface, surface.length, surface.width, 0, )
                x = int(np.random.choice(range(surface.length - 50), 1))
                y = int(np.random.choice(range(surface.width - 50), 1))


                # If the point is either positive or negative, choose a new point
                if newSurface[y][x] != 0:
                    continue

                # if shape.upper() != "SINGLE":
                # To make things go quicker, add a bunch from specified area and slowly reduce the number of
                    # additional generations
                if total_charge[0] - count_charge[0] > 2500:
                    for i in range(50):
                        for j in range(50):
                            if newSurface[y + j][x + i] == 0:
                                newSurface[y + j][x + i] = 1
                                count_charge[0] += 1
                # Else
                newSurface[y][x] = 1

                # Update the count
                count_charge[0] += 1

            # negative charge
            while count_charge[1] < total_charge[1]:
                # pick a random point
                x = int(np.random.choice(range(surface.length - 50), 1))
                y = int(np.random.choice(range(surface.width - 50), 1))
                # If the point is either positive or negative, choose a new point
                if newSurface[y][x] != 0:
                    continue

                # if shape.upper() != "SINGLE":
                # To make things go quicker, add a bunch from specified area and slowly reduce the number of additional generations, except for single
                if total_charge[1] - count_charge[1] > 2500:
                    for i in range(50):
                        for j in range(50):
                            if newSurface[y + j][x + i] == 0:
                                newSurface[y + j][x + i] = -1
                                count_charge[1] += 1

                # Else
                newSurface[y][x] = -1

                # Update the count
                count_charge[1] += 1

        # remove additional charges if needed
        elif count_charge[0] > total_charge[0] or count_charge[1] > total_charge[1]:
            # positive charge
            while count_charge[0] > total_charge[0]:
                # pick a random point
                x = int(np.random.choice(range(surface.length - 50), 1))
                y = int(np.random.choice(range(surface.width - 50), 1))
                # If the point is neutral or negative, choose a new point
                if newSurface[y][x] != 1:
                    continue

                # if shape.upper() != "SINGLE":
                # To make things go quicker, remove a bunch from specified area and slowly reduce the number of additional generations
                if count_charge[0] - total_charge[0] > 2500:
                    for i in range(50):
                        for j in range(50):
                            if newSurface[y + j][x + i] == 1:
                                newSurface[y + j][x + i] = 0
                                count_charge[0] -= 1

                # If the difference is less than 2500, just remove 1 at a time
                newSurface[y][x] = 0

                # Update the count
                count_charge[0] -= 1

            # negative charge
            while count_charge[1] > total_charge[1]:
                # pick a random point
                x = int(np.random.choice(range(surface.length - 50), 1))
                y = int(np.random.choice(range(surface.width - 50), 1))
                # If the point is either neutral or positive, choose a new point
                if newSurface[y][x] != -1:
                    continue

                # if shape.upper() != "SINGLE":
                # To make things go quicker, remove a bunch from specified area and slowly reduce the number of additional generations
                if count_charge[1] - total_charge[1] > 2500:
                    for i in range(50):
                        for j in range(50):
                            if newSurface[y + j][x + i] == -1:
                                newSurface[y + j][x + i] = 0
                                count_charge[1] -= 1
                # Else
                newSurface[y][x] = 0

                # Update the count
                count_charge[1] -= 1

        showMessage("Finished generating/removing charges")
        writeLog("number of +ve and -ve charge after generation/removal {}".format(count_charge))
        writeLog("number of +ve and -ve charge need in total {}".format(total_charge))

        return newSurface

    def _makeSurfaceNeutral(self, passInSurface: Surface) -> ndarray:
        """
        Make the entire surface passed in neutral, which means set all values in the passed in nested list to 0
        """
        writeLog("This is _makeSurfaceNeutral in Domain.py")
        showMessage("start to make surface neutral")
        writeLog(passInSurface.__dict__)
        # get the original surface in the passed in surface
        neutralSurface = passInSurface.originalSurface

        # if passed in is a 2D surface
        if passInSurface.dimension == 2:
            # access each row
            for i in range(len(neutralSurface)):
                # access each point
                for j in range(len(neutralSurface[i])):
                    # set the value in position to 1, which means positive
                    neutralSurface[i][j] = 0

        # if passed in is a 3D surface
        elif passInSurface.dimension == 3:
            # access each row
            for i in range(len(neutralSurface)):
                # access each column
                for j in range(len(neutralSurface[i])):
                    # access each height
                    for k in range(len(neutralSurface[i][j])):
                        # set the value in position to 1, which means positive
                        neutralSurface[i][j][k] = 0

        else:
            raise RuntimeError("Surface passed in is not 2D or 3D")

        # return the generated result
        return neutralSurface

    def _generatePositiveNegative(self, charge_concentration: float) -> int:
        """
        Generates either a positive charge or negative charge depending on the charge_concentration
        """
        charge = int(np.random.choice([-1, 1], 1, p=[1 - charge_concentration, charge_concentration]))
        return charge

    def _totalNumberCharge(self, surface: Surface, charge_concentration: float, concentration: float) -> list:
        """
        Returns the total number of positive and negative charge needed to implement on the surface
        """
        if surface.shape.upper() == "RECTANGLE":
            positive = int(surface.length * surface.width * charge_concentration * concentration)
            negative = int(surface.length * surface.width * (1 - charge_concentration) * concentration)
        else:
            raise RuntimeError("Surface shape is unknown")

        total = [positive, negative]
        return total

    def _randomPoint(self, surfaceLength: int, surfaceWidth: int, domainLength: int, domainWidth: int, shape: str) \
            -> Tuple[int, int]:
        """
        Randomly pick a point on the surface given
        :return a tuple represent a point in the surface in the matrix
        """
        # writeLog("This is _randomPoint in Domain.py")
        # writeLog([self.__dict__, surfaceLength, surfaceWidth, domainLength, domainWidth, shape])

        # Find random coordinate
        if shape.upper() == "DIAMOND":
            # Set restrictions on where the starting position can be
            x_possibility = range(domainLength + 1, surfaceLength - domainLength - 1)
            y_possibility = range(0, surfaceWidth - domainWidth * 2 - 1)
            x = int(np.random.choice(x_possibility, 1, replace=False))
            y = int(np.random.choice(y_possibility, 1, replace=False))

        elif shape.upper() == "CROSS":
            # Set restrictions on where the starting positions can be
            x_possibility = range(domainLength + 1, surfaceLength - domainLength - 1)
            y_possibility = range(domainWidth, surfaceWidth - domainWidth - 1)
            x = int(np.random.choice(x_possibility, 1, replace=False))
            y = int(np.random.choice(y_possibility, 1, replace=False))

        elif shape.upper() == "OCTAGON":
            # Set restriction on where the starting positions can be
            # Separate cases for when domainLength/domainWidth are either even or odd
            if domainLength % 2 == 0:
                x_possibility = range(int(domainLength + (domainLength / 2) + 1),
                                      int(surfaceLength - domainLength - (domainLength / 2) - 1))
                y_possibility = range(int(domainWidth + (domainWidth / 2) + 1),
                                      int(surfaceWidth - domainWidth - (domainWidth / 2) - 1))
            elif domainLength % 2 == 1:
                x_possibility = range(int(domainLength + ((domainLength + 1) / 2) + 1),
                                      int(surfaceLength - domainLength - ((domainLength + 1) / 2) - 1))
                y_possibility = range(int(domainWidth + ((domainWidth + 1) / 2) + 1),
                                      int(surfaceWidth - domainWidth - ((domainWidth + 1) / 2) - 1))
            x = int(np.random.choice(x_possibility, 1, replace=False))
            y = int(np.random.choice(y_possibility, 1, replace=False))

        elif shape.upper() == "SINGLE":
            # Set restriction on where the starting positions can be
            x_possibility = range(2, surfaceLength - 2)
            y_possibility = range(2, surfaceWidth - 2)
            x = int(np.random.choice(x_possibility, 1, replace=False))
            y = int(np.random.choice(y_possibility, 1, replace=False))

        else:
            raise RuntimeError("Wrong shape in the function _randomPoint")

        coordinate = (y, x)
        writeLog("Point picked is: {}".format(coordinate))

        # return the result as tuple
        return coordinate

    def _generateDiamond(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int],
                         charge_concentration: float, countCharge: List[int]) -> [ndarray, List[int]]:
        """
        This function generate diamond shape domain
        This function is adjusted based on:
        https://www.studymite.com/python/examples/program-to-print-diamond-pattern-in-python/
        :return return the surface with diamond domain on it
        """
        ln = domainWidth
        # Fill out diamond triangles
        eg = domainWidth + 1
        for i in range(0, ln + 1):
            for j in range(0, eg):
                # Initialize either positive or negative charge
                charge = self._generatePositiveNegative(charge_concentration)
                # top right
                if surface[int(startPoint[0] - i), int(startPoint[1] + j)] == 0:
                    surface[int(startPoint[0] - i), int(startPoint[1] + j)] = charge
                    # Add charge count
                    if charge == 1:
                        countCharge[0] += 1
                    elif charge == -1:
                        countCharge[1] += 1
                # top left
                if surface[int(startPoint[0] - i), int(startPoint[1] - j)] == 0:
                    surface[int(startPoint[0] - i), int(startPoint[1] - j)] = charge
                    # Add charge count
                    if charge == 1:
                        countCharge[0] += 1
                    elif charge == -1:
                        countCharge[1] += 1
                # bottom right
                if surface[int(startPoint[0] + i), int(startPoint[1] + j)] == 0:
                    surface[int(startPoint[0] + i), int(startPoint[1] + j)] = 1
                    # Add charge count
                    if charge == 1:
                        countCharge[0] += 1
                    elif charge == -1:
                        countCharge[1] += 1
                # bottom left
                if surface[int(startPoint[0] + i), int(startPoint[1] - j)] == 0:
                    surface[int(startPoint[0] + i), int(startPoint[1] - j)] = charge
                    # Add charge count
                    if charge == 1:
                        countCharge[0] += 1
                    elif charge == -1:
                        countCharge[1] += 1
            eg -= 1

        # return the generated surface
        return surface, countCharge

    def _generateCross(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int],
                       charge_concentration: float, countCharge: List[int]) -> [ndarray, List[int]]:
        """
        This function generate cross shape for surface
        """
        # Change the names for each variable
        cen = startPoint

        # create the vertical line of the cross
        for i in range(domainWidth + 1):
            # Initialize either positive or negative charge
            charge = self._generatePositiveNegative(charge_concentration)
            # Add the charge if the position is neutral
            if surface[cen[0] + i - 1, cen[1] - 1] == 0:
                surface[cen[0] + i - 1, cen[1] - 1] = charge
                # Add charge count
                if charge == 1:
                    countCharge[0] += 1
                elif charge == -1:
                    countCharge[1] += 1
            # Add the charge if the position is neutral
            if surface[cen[0] - i - 1, cen[1] - 1] == 0:
                surface[cen[0] - i - 1, cen[1] - 1] = charge
                # Add charge count
                if charge == 1:
                    countCharge[0] += 1
                elif charge == -1:
                    countCharge[1] += 1

        # create the horizontal line of the cross
        for j in range(domainLength + 1):
            # Initialize either positive or negative charge
            charge = self._generatePositiveNegative(charge_concentration)

            if surface[cen[0] - 1, cen[1] + j - 1] == 0:
                surface[cen[0] - 1, cen[1] + j - 1] = charge
                # Add charge count
                if charge == 1:
                    countCharge[0] += 1
                elif charge == -1:
                    countCharge[1] += 1
            if surface[cen[0] - 1, cen[1] - j - 1] == 0:
                surface[cen[0] - 1, cen[1] - j - 1] = charge
                # Add charge count
                if charge == 1:
                    countCharge[0] += 1
                elif charge == -1:
                    countCharge[1] += 1

        return surface, countCharge

    def _generateOctagon(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int],
                         charge_concentration: float, countCharge: List[int]) -> [ndarray, List[int]]:
        """
        This function generate octagon shape for surface
        """

        # Rename variables
        ln = domainWidth
        cen = startPoint
        # Find the center of the hexagon
        # If the length is an odd number, the center of the octagon should be located between 4 points (ie center point should end as .5)
        if cen[0] % 2 == cen[1] % 2 and ln % 2 == 1:
            if cen[0] % 2 == 1:
                cen = [cen[0], cen[1]]
            elif cen[0] % 2 == 0:
                cen = [cen[0] - 0.5, cen[1] - 0.5]
        elif cen[0] % 2 != cen[1] % 2 and ln % 2 == 1:
            if cen[0] % 2 == 1:
                cen = [cen[0], cen[1] - 0.5]
            elif cen[1] % 2 == 1:
                cen = [cen[0] - 0.5, cen[1]]

        # Separate conditions between if the length is odd or even
        # If the length is odd
        if ln % 2 == 1:
            # Initial square surrounding the center
            n = int(ln / 2 + 0.5)
            for i in range(n):
                for j in range(n):
                    if surface[int(cen[0] + (0.5 + i)), int(cen[1] + (0.5 + j))] == 0:
                        # Initialize charge
                        charge = self._generatePositiveNegative(charge_concentration)
                        surface[int(cen[0] + (0.5 + i)), int(cen[1] + (0.5 + j))] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                        elif charge == -1:
                            countCharge[1] += 1
                    if surface[int(cen[0] + (0.5 + i)), int(cen[1] - (0.5 + j))] == 0:
                        # Initialize charge
                        charge = self._generatePositiveNegative(charge_concentration)
                        surface[int(cen[0] + (0.5 + i)), int(cen[1] - (0.5 + j))] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                        elif charge == -1:
                            countCharge[1] += 1
                    if surface[int(cen[0] - (0.5 + i)), int(cen[1] + (0.5 + j))] == 0:
                        # Initialize charge
                        charge = self._generatePositiveNegative(charge_concentration)
                        surface[int(cen[0] - (0.5 + i)), int(cen[1] + (0.5 + j))] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                        elif charge == -1:
                            countCharge[1] += 1
                    if surface[int(cen[0] - (0.5 + i)), int(cen[1] - (0.5 + j))] == 0:
                        # Initialize charge
                        charge = self._generatePositiveNegative(charge_concentration)
                        surface[int(cen[0] - (0.5 + i)), int(cen[1] - (0.5 + j))] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                        elif charge == -1:
                            countCharge[1] += 1

            # Index edges of the square
            # top right edge
            ed_tr = [int(cen[0] - ln / 2), int(cen[1] + ln / 2)]
            # top left edge
            ed_tl = [int(cen[0] - ln / 2), int(cen[1] - ln / 2)]
            # bottom right edge
            ed_br = [int(cen[0] + ln / 2), int(cen[1] + ln / 2)]
            # bottom left edge
            ed_bl = [int(cen[0] + ln / 2), int(cen[1] - ln / 2)]

        # If the length is even
        elif ln % 2 == 0:
            # Initial square surrounding the center
            n = int(ln / 2)
            for i in range(n + 1):
                for j in range(n + 1):
                    if surface[int(cen[0] + i), int(cen[1] + j)] == 0:
                        # Initialize charge
                        charge = self._generatePositiveNegative(charge_concentration)
                        surface[int(cen[0] + i), int(cen[1] + j)] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                        elif charge == -1:
                            countCharge[1] += 1
                    if surface[int(cen[0] + i), int(cen[1] - j)] == 0:
                        # Initialize charge
                        charge = self._generatePositiveNegative(charge_concentration)
                        surface[int(cen[0] + i), int(cen[1] - j)] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                        elif charge == -1:
                            countCharge[1] += 1
                    if surface[int(cen[0] - i), int(cen[1] + j)] == 0:
                        # Initialize charge
                        charge = self._generatePositiveNegative(charge_concentration)
                        surface[int(cen[0] - i), int(cen[1] + j)] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                        elif charge == -1:
                            countCharge[1] += 1
                    if surface[int(cen[0] - i), int(cen[1] - j)] == 0:
                        # Initialize charge
                        charge = self._generatePositiveNegative(charge_concentration)
                        surface[int(cen[0] - i), int(cen[1] - j)] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                        elif charge == -1:
                            countCharge[1] += 1

            # Index edges of the square
            # top right edge
            ed_tr = [int(cen[0] - ln / 2), int(cen[1] + ln / 2)]
            # top left edge
            ed_tl = [int(cen[0] - ln / 2), int(cen[1] - ln / 2)]
            # bottom right edge
            ed_br = [int(cen[0] + ln / 2), int(cen[1] + ln / 2)]
            # bottom left edge
            ed_bl = [int(cen[0] + ln / 2), int(cen[1] - ln / 2)]

        # Fill out the 4 triangles
        eg = ln + 1
        for i in range(0, ln + 1):
            for j in range(0, eg):
                # Initialize charge
                charge = self._generatePositiveNegative(charge_concentration)
                # top right  
                if surface[int(ed_tr[0] - i), int(ed_tr[1] + j)] == 0:
                    surface[int(ed_tr[0] - i), int(ed_tr[1] + j)] = charge
                    # Add charge count
                    if charge == 1:
                        countCharge[0] += 1
                    elif charge == -1:
                        countCharge[1] += 1
                # top left
                if surface[int(ed_tl[0] - i), int(ed_tl[1] - j)] == 0:
                    surface[int(ed_tl[0] - i), int(ed_tl[1] - j)] = charge
                    # Add charge count
                    if charge == 1:
                        countCharge[0] += 1
                    elif charge == -1:
                        countCharge[1] += 1
                # bottom right
                if surface[int(ed_br[0] + i), int(ed_br[1] + j)] == 0:
                    surface[int(ed_br[0] + i), int(ed_br[1] + j)] = charge
                    # Add charge count
                    if charge == 1:
                        countCharge[0] += 1
                    elif charge == -1:
                        countCharge[1] += 1
                # bottom left
                if surface[int(ed_bl[0] + i), int(ed_bl[1] - j)] == 0:
                    surface[int(ed_bl[0] + i), int(ed_bl[1] - j)] = charge
                    # Add charge count
                    if charge == 1:
                        countCharge[0] += 1
                    elif charge == -1:
                        countCharge[1] += 1
            eg -= 1

        # Finally, fill out the remaining 4 squares
        for i in range(1, ln + 1):
            for j in range(1, ln + 1):
                # Initialize charge
                charge = self._generatePositiveNegative(charge_concentration)
                # top square
                if surface[int(ed_tl[0] - i), int(ed_tl[1] + j)] == 0:
                    surface[int(ed_tl[0] - i), int(ed_tl[1] + j)] = charge
                    # Add charge count
                    if charge == 1:
                        countCharge[0] += 1
                    elif charge == -1:
                        countCharge[1] += 1
                # left square
                if surface[int(ed_tl[0] + i), int(ed_tl[1] - j)] == 0:
                    surface[int(ed_tl[0] + i), int(ed_tl[1] - j)] = charge
                    # Add charge count
                    if charge == 1:
                        countCharge[0] += 1
                    elif charge == -1:
                        countCharge[1] += 1
                # right square
                if surface[int(ed_br[0] - i), int(ed_br[1] + j)] == 0:
                    surface[int(ed_br[0] - i), int(ed_br[1] + j)] = charge
                    # Add charge count
                    if charge == 1:
                        countCharge[0] += 1
                    elif charge == -1:
                        countCharge[1] += 1
                # bottom square
                if surface[int(ed_br[0] + i), int(ed_br[1] - j)] == 0:
                    surface[int(ed_br[0] + i), int(ed_br[1] - j)] = charge
                    # Add charge count
                    if charge == 1:
                        countCharge[0] += 1
                    elif charge == -1:
                        countCharge[1] += 1
        return surface, countCharge

    def _generateSingle(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int],
                        charge_concentration: float, countCharge: List[int]) -> [ndarray, List[int]]:
        """
        This function generate single shape for surface
        """
        # Initialize charge
        charge = self._generatePositiveNegative(charge_concentration)
        if surface[int(startPoint[0]), int(startPoint[1])] == 0:
            surface[int(startPoint[0]), int(startPoint[1])] = charge
            # Add charge count
            if charge == 1:
                countCharge[0] += 1
            elif charge == -1:
                countCharge[1] += 1

        # Used to increase speed for generating domains since it takes a long time to generate all the domains
        if surface[int(startPoint[0]+1), int(startPoint[1]+1)] == 0:
            surface[int(startPoint[0]+1), int(startPoint[1]+1)] = charge
            # Add charge count
            if charge == 1:
                countCharge[0] += 1
            elif charge == -1:
                countCharge[1] += 1
        if surface[int(startPoint[0]-1), int(startPoint[1]-1)] == 0:
            surface[int(startPoint[0]-1), int(startPoint[1]-1)] = charge
            # Add charge count
            if charge == 1:
                countCharge[0] += 1
            elif charge == -1:
                countCharge[1] += 1
        if surface[int(startPoint[0]+1), int(startPoint[1]-1)] == 0:
            surface[int(startPoint[0]+1), int(startPoint[1]-1)] = charge
            # Add charge count
            if charge == 1:
                countCharge[0] += 1
            elif charge == -1:
                countCharge[1] += 1
        if surface[int(startPoint[0]-1), int(startPoint[1]+1)] == 0:
            surface[int(startPoint[0]-1), int(startPoint[1]+1)] = charge
            # Add charge count
            if charge == 1:
                countCharge[0] += 1
            elif charge == -1:
                countCharge[1] += 1


        return surface, countCharge
