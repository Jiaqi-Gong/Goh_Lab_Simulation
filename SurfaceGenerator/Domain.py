"""
This program is generating the domain with some charge on it
Can be used for 2D, 3D and for testing surface, bacteria surface
"""
import random

from numpy import ndarray
import numpy as np
from typing import Tuple
from SurfaceGenerator.Surface import Surface
from typing import Tuple, List
from ExternalIO import showMessage, writeLog
import math


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

        # domainLength = size[0]
        # domainWidth = size[1]

        # calculate how many domain should generate
        # calculation for the number of domains which needs to be generated depends on the shape of the domain
        # set corresponding check and generate function
        # more shape coming soon, leave for more extension using elif

        # calculate total charge need
        totalCharge = int(surface.length * surface.width * concentration)

        if shape.upper() == "DIAMOND":
            # Number of domains
            domainNum = int(totalCharge / (domainWidth * (domainLength)))
            generateShape = self._generateDiamond
        elif shape.upper() == "CROSS":
            # Number of domains
            domainNum = int(totalCharge / (2 * domainWidth + 2 * domainLength))
            generateShape = self._generateCross
        elif shape.upper() == "OCTAGON":
            # Number of domains
            domainNum = int(totalCharge / (2 * (1 + math.sqrt(2)) * domainWidth * domainLength))
            generateShape = self._generateOctagon
        elif shape.upper() == "SINGLE":
            # Number of domains
            domainNum = totalCharge
            generateShape = self._generateSingle
        else:
            raise RuntimeError("Unknown shape")

        showMessage("Domain number is: {}".format(domainNum))

        # no need for this, the surface pass in to generator is neutral
        # This surface is neutral
        # newSurface = self._makeSurfaceNeutral(surface)

        # copy the original surface to generate new surface
        newSurface = surface.originalSurface

        # init generated domain number
        generated = 0

        # set seed for random
        np.random.seed(self.seed)

        # generate the corresponding domain shape
        showMessage("Start to generate domain on the surface")
        writeLog(surface)

        # check generate domain number is not too small
        if generated >= domainNum:
            raise RuntimeError("Domain concentration is too low")

        # Initialize the charge count (NOTE: charge count is a list with the first element being positive charge
        # while second element being negative charge)
        chargeCount = [0, 0]

        # Initialize total number of positive and negative charge needed on the surface
        totalCharge = self._totalNumberCharge(surface, concentration, charge_concentration)

        # start to generate the domain on surface
        while generated < domainNum:
            # pick a point in the matrix as the start point of generate domain
            # randint pick x and y, leave the enough space for not touching the edge
            start = self._randomPoint(surface.length, surface.width, domainLength, domainWidth, shape)

            # generate this shape's domain
            newSurface, chargeCount = generateShape(newSurface, domainWidth, domainLength, start,
                                                    charge_concentration, chargeCount)

            # update generated number
            generated += 1

            # showMessage("Generated number is: {}".format(generated))

        showMessage("Domain generated done, {} domain is generated".format(generated))

        # call helper to balance charge
        self._balanceCharge(chargeCount, newSurface, totalCharge)

        writeLog(newSurface)

        # return the surface generated based on k value
        return newSurface

    def _balanceCharge(self, chargeCount: List[int], newSurface: ndarray, totalCharge: List[int]) -> None:
        """
        This method uses to balance any excess charge when generate domain
        """
        showMessage("Start to balance charges....")
        writeLog("number of +ve and -ve charge before generation/removal {}".format(chargeCount))

        # calculate the number of each charge need to adjust
        positiveChargeNum = chargeCount[0] - totalCharge[0]
        negativeChargeNum = chargeCount[1] - totalCharge[1]

        showMessage("The number of positive charge need to adjust is: {}, the number of negative charge need to adjust "
                 "is: {}".format(positiveChargeNum, negativeChargeNum))

        # init the target charge
        charge = 0

        # reshape the new surface to 1D and record the original dimension of surface
        surface1D = newSurface.reshape((-1,))

        # pick the point on the surface and do the change
        while True:
            # check if balance, stop
            if positiveChargeNum == 0 and negativeChargeNum == 0:
                break

            # decide need to generate which charge
            if positiveChargeNum > 0 or negativeChargeNum < 0:
                charge = -1
            elif positiveChargeNum < 0 or negativeChargeNum > 0:
                charge = 1
            else:
                charge = 0

            # randomly pick the point
            position = random.randint(0, surface1D.shape[0] - 1)

            # check the charge on this position
            curCharge = surface1D[position]

            # based on the current charge, change the charge
            # if it's positive
            if curCharge > 0:
                # check the charge need to generate
                # if charge is not 1, which means positive charge is excess
                if charge != 1:

                    # check need to generate negative or neutral
                    if charge == -1:
                        # generate negative charge
                        surface1D[position] = -1
                        negativeChargeNum += 1
                    else:
                        surface1D[position] = 0

                positiveChargeNum -= 1

            # if current charge is negative
            elif curCharge < 0:
                # check the charge need to generate
                # if charge is not -1, which means negative charge is excess
                if charge != -1:

                    # check need to generate positive or neutral
                    if charge == 1:
                        # generate positive charge
                        surface1D[position] = 1
                        positiveChargeNum += 1
                    else:
                        surface1D[position] = 0

                negativeChargeNum -= 1

            # if current charge is neutral
            else:
                surface1D[position] = charge

                # check which charge need generate
                if charge == 1:
                    positiveChargeNum += 1
                else:
                    negativeChargeNum += 1

        showMessage("Charge balance done")
        writeLog(newSurface)


    # def _balanceCharge(self, chargeCount: List[int], newSurface: ndarray, shape: str, surface: Surface,
    #                    totalCharge: List[int]) -> None:
    #     """
    #     This method uses to balance any excess charge when generate domain
    #     """
    #     showMessage("Start to balance charges....")
    #     writeLog("number of +ve and -ve charge before generation/removal {}".format(chargeCount))
    #
    #     # generate additional charge spots on the surface if needed
    #     if chargeCount[0] < totalCharge[0] or chargeCount[1] < totalCharge[1]:
    #         # positive charge
    #         while chargeCount[0] < totalCharge[0]:
    #             # pick a random point
    #             x = int(np.random.choice(range(surface.length - 50), 1))
    #             y = int(np.random.choice(range(surface.width - 50), 1))
    #             # If the point is either positive or negative, choose a new point
    #             if newSurface[y][x] != 0:
    #                 continue
    #
    #             if shape.upper() != "SINGLE":
    #                 # To make things go quicker, add a bunch from specified area and slowly reduce the number of
    #                 # additional generations
    #                 if totalCharge[0] - chargeCount[0] > 2500:
    #                     for i in range(50):
    #                         for j in range(50):
    #                             if newSurface[y + j][x + i] == 0:
    #                                 newSurface[y + j][x + i] = 1
    #                                 chargeCount[0] += 1
    #             # Else
    #             newSurface[y][x] = 1
    #
    #             # Update the count
    #             chargeCount[0] += 1
    #
    #         # negative charge
    #         while chargeCount[1] < totalCharge[1]:
    #             # pick a random point
    #             x = int(np.random.choice(range(surface.length - 50), 1))
    #             y = int(np.random.choice(range(surface.width - 50), 1))
    #             # If the point is either positive or negative, choose a new point
    #             if newSurface[y][x] != 0:
    #                 continue
    #
    #             if shape.upper() != "SINGLE":
    #                 # To make things go quicker, add a bunch from specified area and slowly reduce the number of additional generations, except for single
    #                 if totalCharge[1] - chargeCount[1] > 2500:
    #                     for i in range(50):
    #                         for j in range(50):
    #                             if newSurface[y + j][x + i] == 0:
    #                                 newSurface[y + j][x + i] = -1
    #                                 chargeCount[1] += 1
    #
    #             # Else
    #             newSurface[y][x] = -1
    #
    #             # Update the count
    #             chargeCount[1] += 1
    #
    #     # remove additional charges if needed
    #     elif chargeCount[0] > totalCharge[0] or chargeCount[1] > totalCharge[1]:
    #         # positive charge
    #         while chargeCount[0] > totalCharge[0]:
    #             # pick a random point
    #             x = int(np.random.choice(range(surface.length - 50), 1))
    #             y = int(np.random.choice(range(surface.width - 50), 1))
    #             # If the point is neutral or negative, choose a new point
    #             if newSurface[y][x] != 1:
    #                 continue
    #
    #             if shape.upper() != "SINGLE":
    #                 # To make things go quicker, remove a bunch from specified area and slowly reduce the number of additional generations
    #                 if chargeCount[0] - totalCharge[0] > 2500:
    #                     for i in range(50):
    #                         for j in range(50):
    #                             if newSurface[y + j][x + i] == 1:
    #                                 newSurface[y + j][x + i] = 0
    #                                 chargeCount[0] -= 1
    #
    #             # If the difference is less than 2500, just remove 1 at a time
    #             newSurface[y][x] = 0
    #
    #             # Update the count
    #             chargeCount[0] -= 1
    #
    #         # negative charge
    #         while chargeCount[1] > totalCharge[1]:
    #             # pick a random point
    #             x = int(np.random.choice(range(surface.length - 50), 1))
    #             y = int(np.random.choice(range(surface.width - 50), 1))
    #             # If the point is either neutral or positive, choose a new point
    #             if newSurface[y][x] != -1:
    #                 continue
    #
    #             if shape.upper() != "SINGLE":
    #                 # To make things go quicker, remove a bunch from specified area and slowly reduce the number of additional generations
    #                 if chargeCount[1] - totalCharge[1] > 2500:
    #                     for i in range(50):
    #                         for j in range(50):
    #                             if newSurface[y + j][x + i] == -1:
    #                                 newSurface[y + j][x + i] = 0
    #                                 chargeCount[1] -= 1
    #             # Else
    #             newSurface[y][x] = 0
    #
    #             # Update the count
    #             chargeCount[1] -= 1
    #     showMessage("Finished generating/removing charges")
    #     writeLog("number of +ve and -ve charge after generation/removal {}".format(chargeCount))
    #     writeLog("number of +ve and -ve charge need in total {}".format(totalCharge))

    # def _makeSurfaceNeutral(self, passInSurface: Surface) -> Surface:
    #     """
    #     Make the entire surface passed in neutral, which means set all values in the passed in nested list to 0
    #     """
    #     writeLog("This is _makeSurfaceNeutral in Domain.py")
    #     showMessage("start to make surface neutral")
    #     writeLog(passInSurface.__dict__)
    #     # get the original surface in the passed in surface
    #     neutralSurface = passInSurface.originalSurface
    #
    #     # if passed in is a 2D surface
    #     if passInSurface.dimension == 2:
    #         # access each row
    #         for i in range(len(neutralSurface)):
    #             # access each point
    #             for j in range(len(neutralSurface[i])):
    #                 # set the value in position to 1, which means positive
    #                 neutralSurface[i][j] = 0
    #
    #     # if passed in is a 3D surface
    #     elif passInSurface.dimension == 3:
    #         # access each row
    #         for i in range(len(neutralSurface)):
    #             # access each column
    #             for j in range(len(neutralSurface[i])):
    #                 # access each height
    #                 for k in range(len(neutralSurface[i][j])):
    #                     # set the value in position to 1, which means positive
    #                     neutralSurface[i][j][k] = 0
    #
    #     else:
    #         raise RuntimeError("Surface passed in is not 2D or 3D")
    #
    #     # return the generated result
    #     return neutralSurface

    def _generateCharge(self, charge_concentration: float) -> int:
        """
        Generates either a positive charge or negative charge depending on the charge_concentration
        """
        charge = int(np.random.choice([-1, 1], 1, p=[1 - charge_concentration, charge_concentration]))
        return charge

    def _totalNumberCharge(self, surface: Surface, charge_concentration: float, concentration: float) -> List[int]:
        """
        Returns the total number of positive and negative charge needed to implement on the surface
        """
        if surface.shape.upper() == "RECTANGLE":
            positive = int(surface.length * surface.width * charge_concentration * concentration)
            negative = int(surface.length * surface.width * (1 - charge_concentration) * concentration)
        else:
            raise RuntimeError("Unknown surface shape")

        total = [positive, negative]
        return total

    def _randomPoint(self, surfaceLength: int, surfaceWidth: int, domainLength: int, domainWidth: int, shape: str) \
            -> Tuple[int, int]:
        """
        Randomly pick a point on the surface given
        :return a tuple represent a point in the surface in the matrix
        """
        writeLog("This is _randomPoint in Domain.py")
        # writeLog([self.__dict__, surfaceLength, surfaceWidth, domainLength, domainWidth, shape])

        # Find random coordinate
        if shape.upper() == "DIAMOND":
            # Set restrictions on where the starting position can be
            x_possibility = range(domainLength + 1, surfaceLength - domainLength - 1)
            y_possibility = range(0, surfaceWidth - domainWidth * 2 - 1)

        elif shape.upper() == "CROSS":
            # Set restrictions on where the starting positions can be
            x_possibility = range(domainLength + 1, surfaceLength - domainLength - 1)
            y_possibility = range(domainWidth, surfaceWidth - domainWidth - 1)

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

        elif shape.upper() == "SINGLE":
            # Set restriction on where the starting positions can be
            x_possibility = range(1, surfaceLength - 1)
            y_possibility = range(1, surfaceWidth - 1)

        else:
            raise RuntimeError("Wrong shape in the function _randomPoint")

        # pick x y
        x = int(np.random.choice(x_possibility, 1, replace=False))
        y = int(np.random.choice(y_possibility, 1, replace=False))

        # way of define x y was wrong, so at here swap them
        coordinate = (y, x)
        writeLog("Point picked is: {}".format(coordinate))

        # return the result as tuple
        return coordinate

    def _generateDiamond(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int],
                         charge_concentration: float, chargeCount: List[int]) -> [ndarray, List[int]]:
        """
        This function generate diamond shape domain
        This function is adjusted based on:
        https://www.studymite.com/python/examples/program-to-print-diamond-pattern-in-python/
        :return return the surface with diamond domain on it
        """
        # set the new name
        n = domainWidth
        start = startPoint

        # set a variable for checking the width
        count = 0

        # make upper diamond
        for i in range(0, n + 1):
            for j in range(-count + 1, count):
                # Initialize either positive or negative charge
                charge = self._generateCharge(charge_concentration)

                # Add the charge if the position is neutral
                if surface[start[0] + i][start[1] + j] == 0:
                    surface[start[0] + i][start[1] + j] = charge

                    # update charge count
                    if charge == 1:
                        chargeCount[0] += 1
                    elif charge == -1:
                        chargeCount[1] += 1

            # upper part, width becomes wider
            count += 1

        # make lower diamond
        for i in range(n + 1, 2 * (n + 1) + 1):
            for j in range(-count + 1, count):
                # Initialize either positive or negative charge
                charge = self._generateCharge(charge_concentration)

                # Add the charge if the position is neutral
                if surface[start[0] + i][start[1] - j] == 0:
                    surface[start[0] + i][start[1] - j] = charge

                    # update charge count
                    if charge == 1:
                        chargeCount[0] += 1
                    elif charge == -1:
                        chargeCount[1] += 1

            # lower part, width becomes thinner
            count -= 1

        # return the generated surface
        return surface, chargeCount

    def _generateCross(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int],
                       charge_concentration: float, List: list) -> [ndarray, list]:
        """
        This function generate cross shape for surface
        """
        # Change the names for each variable
        cen = startPoint

        # create the vertical line of the cross
        for i in range(domainWidth + 1):
            # Initialize either positive or negative charge
            charge = self._generateCharge(charge_concentration)
            # Add the charge if the position is neutral
            if surface[cen[0] + i - 1, cen[1] - 1] == 0:
                surface[cen[0] + i - 1, cen[1] - 1] = charge
                # Add charge count
                if charge == 1:
                    List[0] += 1
                elif charge == -1:
                    List[1] += 1
            # Add the charge if the position is neutral
            if surface[cen[0] - i - 1, cen[1] - 1] == 0:
                surface[cen[0] - i - 1, cen[1] - 1] = charge
                # Add charge count
                if charge == 1:
                    List[0] += 1
                elif charge == -1:
                    List[1] += 1

        # create the horizontal line of the cross
        for j in range(domainLength + 1):
            # Initialize either positive or negative charge
            charge = self._generateCharge(charge_concentration)

            if surface[cen[0] - 1, cen[1] + j - 1] == 0:
                surface[cen[0] - 1, cen[1] + j - 1] = charge
                # Add charge count
                if charge == 1:
                    List[0] += 1
                elif charge == -1:
                    List[1] += 1
            if surface[cen[0] - 1, cen[1] - j - 1] == 0:
                surface[cen[0] - 1, cen[1] - j - 1] = charge
                # Add charge count
                if charge == 1:
                    List[0] += 1
                elif charge == -1:
                    List[1] += 1

        return surface, List

    def _generateOctagon(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int],
                         charge_concentration: float, List: list) -> [ndarray, list]:
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
        # If the length is an even number, the center of the octagon should be located on a point (ie center point should end as .0)
        elif cen[0] % 2 == cen[1] % 2 and ln % 2 == 0:
            if cen[0] % 2 == 1:
                cen = [cen[0] - 0.5, cen[1] - 0.5]
            elif cen[0] % 2 == 0:
                cen = [cen[0], cen[1]]
        elif cen[0] % 2 != cen[1] % 2 and ln % 2 == 0:
            if cen[0] % 2 == 1:
                cen = [cen[0] - 0.5, cen[1]]
            elif cen[1] % 2 == 1:
                cen = [cen[0], cen[1] - 0.5]

        # Separate conditions between if the length is odd or even
        # If the length is odd
        if ln % 2 == 1:
            # Initial square surrounding the center
            n = int(ln / 2 + 0.5)
            for i in range(n):
                for j in range(n):
                    if surface[int(cen[0] + (0.5 + i)), int(cen[1] + (0.5 + j))] == 0:
                        # Initialize charge
                        charge = self._generateCharge(charge_concentration)
                        surface[int(cen[0] + (0.5 + i)), int(cen[1] + (0.5 + j))] = charge
                        # Add charge count
                        if charge == 1:
                            List[0] += 1
                        elif charge == -1:
                            List[1] += 1
                    if surface[int(cen[0] + (0.5 + i)), int(cen[1] - (0.5 + j))] == 0:
                        # Initialize charge
                        charge = self._generateCharge(charge_concentration)
                        surface[int(cen[0] + (0.5 + i)), int(cen[1] - (0.5 + j))] = charge
                        # Add charge count
                        if charge == 1:
                            List[0] += 1
                        elif charge == -1:
                            List[1] += 1
                    if surface[int(cen[0] - (0.5 + i)), int(cen[1] + (0.5 + j))] == 0:
                        # Initialize charge
                        charge = self._generateCharge(charge_concentration)
                        surface[int(cen[0] - (0.5 + i)), int(cen[1] + (0.5 + j))] = charge
                        # Add charge count
                        if charge == 1:
                            List[0] += 1
                        elif charge == -1:
                            List[1] += 1
                    if surface[int(cen[0] - (0.5 + i)), int(cen[1] - (0.5 + j))] == 0:
                        # Initialize charge
                        charge = self._generateCharge(charge_concentration)
                        surface[int(cen[0] - (0.5 + i)), int(cen[1] - (0.5 + j))] = charge
                        # Add charge count
                        if charge == 1:
                            List[0] += 1
                        elif charge == -1:
                            List[1] += 1

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
                        charge = self._generateCharge(charge_concentration)
                        surface[int(cen[0] + i), int(cen[1] + j)] = charge
                        # Add charge count
                        if charge == 1:
                            List[0] += 1
                        elif charge == -1:
                            List[1] += 1
                    if surface[int(cen[0] + i), int(cen[1] - j)] == 0:
                        # Initialize charge
                        charge = self._generateCharge(charge_concentration)
                        surface[int(cen[0] + i), int(cen[1] - j)] = charge
                        # Add charge count
                        if charge == 1:
                            List[0] += 1
                        elif charge == -1:
                            List[1] += 1
                    if surface[int(cen[0] - i), int(cen[1] + j)] == 0:
                        # Initialize charge
                        charge = self._generateCharge(charge_concentration)
                        surface[int(cen[0] - i), int(cen[1] + j)] = charge
                        # Add charge count
                        if charge == 1:
                            List[0] += 1
                        elif charge == -1:
                            List[1] += 1
                    if surface[int(cen[0] - i), int(cen[1] - j)] == 0:
                        # Initialize charge
                        charge = self._generateCharge(charge_concentration)
                        surface[int(cen[0] - i), int(cen[1] - j)] = charge
                        # Add charge count
                        if charge == 1:
                            List[0] += 1
                        elif charge == -1:
                            List[1] += 1

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
        # top right
        nu_tr = ln + 1
        for i in range(0, ln + 1):
            for j in range(0, nu_tr):
                # Initialize charge
                charge = self._generateCharge(charge_concentration)
                if surface[int(ed_tr[0] - i), int(ed_tr[1] + j)] == 0:
                    surface[int(ed_tr[0] - i), int(ed_tr[1] + j)] = charge
                    # Add charge count
                    if charge == 1:
                        List[0] += 1
                    elif charge == -1:
                        List[1] += 1
            nu_tr -= 1

        # top left
        nu_tl = ln + 1
        for i in range(0, ln + 1):
            for j in range(0, nu_tl):
                # Initialize charge
                charge = self._generateCharge(charge_concentration)
                if surface[int(ed_tl[0] - i), int(ed_tl[1] - j)] == 0:
                    surface[int(ed_tl[0] - i), int(ed_tl[1] - j)] = charge
                    # Add charge count
                    if charge == 1:
                        List[0] += 1
                    elif charge == -1:
                        List[1] += 1
            nu_tl -= 1

        # bottom right
        nu_br = ln + 1
        for i in range(0, ln + 1):
            for j in range(0, nu_br):
                # Initialize charge
                charge = self._generateCharge(charge_concentration)
                if surface[int(ed_br[0] + i), int(ed_br[1] + j)] == 0:
                    surface[int(ed_br[0] + i), int(ed_br[1] + j)] = charge
                    # Add charge count
                    if charge == 1:
                        List[0] += 1
                    elif charge == -1:
                        List[1] += 1
            nu_br -= 1

        # bottom left triangle
        nu_bl = ln + 1
        for i in range(0, ln + 1):
            for j in range(0, nu_bl):
                # Initialize charge
                charge = self._generateCharge(charge_concentration)
                if surface[int(ed_bl[0] + i), int(ed_bl[1] - j)] == 0:
                    surface[int(ed_bl[0] + i), int(ed_bl[1] - j)] = charge
                    # Add charge count
                    if charge == 1:
                        List[0] += 1
                    elif charge == -1:
                        List[1] += 1
            nu_bl -= 1

        # Finally, fill out the remaining 4 squares
        # top square
        for i in range(1, ln + 1):
            for j in range(1, ln + 1):
                # Initialize charge
                charge = self._generateCharge(charge_concentration)
                if surface[int(ed_tl[0] - i), int(ed_tl[1] + j)] == 0:
                    surface[int(ed_tl[0] - i), int(ed_tl[1] + j)] = charge
                    # Add charge count
                    if charge == 1:
                        List[0] += 1
                    elif charge == -1:
                        List[1] += 1
        # left square
        for i in range(1, ln + 1):
            for j in range(1, ln + 1):
                # Initialize charge
                charge = self._generateCharge(charge_concentration)
                if surface[int(ed_tl[0] + i), int(ed_tl[1] - j)] == 0:
                    surface[int(ed_tl[0] + i), int(ed_tl[1] - j)] = charge
                    # Add charge count
                    if charge == 1:
                        List[0] += 1
                    elif charge == -1:
                        List[1] += 1
        # right square
        for i in range(1, ln + 1):
            for j in range(1, ln + 1):
                # Initialize charge
                charge = self._generateCharge(charge_concentration)
                if surface[int(ed_br[0] - i), int(ed_br[1] + j)] == 0:
                    surface[int(ed_br[0] - i), int(ed_br[1] + j)] = charge
                    # Add charge count
                    if charge == 1:
                        List[0] += 1
                    elif charge == -1:
                        List[1] += 1
        # bottom square
        for i in range(1, ln + 1):
            for j in range(1, ln + 1):
                # Initialize charge
                charge = self._generateCharge(charge_concentration)
                if surface[int(ed_br[0] + i), int(ed_br[1] - j)] == 0:
                    surface[int(ed_br[0] + i), int(ed_br[1] - j)] = charge
                    # Add charge count
                    if charge == 1:
                        List[0] += 1
                    elif charge == -1:
                        List[1] += 1
        return surface, List

    def _generateSingle(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int],
                        charge_concentration: float, chargeCount: List[int]) -> [ndarray, List[int]]:
        """
        This function generate single shape for surface
        """
        # Initialize charge
        charge = self._generateCharge(charge_concentration)
        if surface[int(startPoint[0]), int(startPoint[1])] == 0:
            surface[int(startPoint[0]), int(startPoint[1])] = charge
            # Add charge count
            if charge == 1:
                chargeCount[0] += 1
            elif charge == -1:
                chargeCount[1] += 1

        return surface, chargeCount
