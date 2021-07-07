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
        charge_balance = False
        while not charge_balance:
            start_time = time.time()
            # pick a point in the matrix as the start point of generate domain
            # randint pick x and y, leave the enough space for not touching the edge
            start = self._randomPoint(surface, surface.length, surface.width, surface.height, domainLength, domainWidth, shape)

            # generate this shape's domain
            [newSurface, count_charge] = generateShape(newSurface, domainWidth, domainLength, start, charge_concentration, count_charge, total_charge)

            if count_charge[0] == total_charge[0] and count_charge[1] == total_charge[1]:
                charge_balance = True

            # # update generated number
            # if shape.upper() == "SINGLE":
            #     generated += 5
            # else:
            #     generated += 1

            total_time = time.time() - start_time

            # showMessage("Generated number is: {}".format(generated))
            # showMessage("Time it took to generate is: {} seconds".format(total_time))

        showMessage("Domain generated done")
        showMessage("count charge is {}".format(count_charge))
        showMessage("total charge is {}".format(total_charge))

        # newSurface = self._balanceCharge(count_charge, newSurface, domainLength, domainWidth, total_charge)

        writeLog(newSurface)
        # return the surface generated based on k value
        return newSurface

    def _generatePositiveNegative(self, charge_concentration: float, countCharge: List[int], totalCharge: List[int]) -> int:
        """
        Generates either a positive charge or negative charge depending on the charge_concentration
        """
        charge = int(np.random.choice([-1, 1], 1, p=[1 - charge_concentration, charge_concentration]))

        # if the total charge equals count charge for the positive, it will only output negative
        if countCharge[0] == totalCharge[0]:
            charge = -1

        # if the total charge equals count charge for the negative, it will only output positive
        if countCharge[1] == totalCharge[1]:
            charge = 1

        # if the total charge on the surface is larger than expected, raise
        if countCharge[0] > totalCharge[0] or countCharge[1] > totalCharge[1]:
            raise RuntimeError("Charge too many")

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

    def _randomPoint(self, surface: Surface, surfaceLength: int, surfaceWidth: int, surfaceHeight: int, domainLength: int, domainWidth: int, shape: str) -> Tuple[int, int, int]:
        """
        Randomly pick a point on the surface given
        :return a tuple represent a point in the surface in the matrix
        """
        # writeLog("This is _randomPoint in Domain.py")
        # writeLog([self.__dict__, surfaceLength, surfaceWidth, domainLength, domainWidth, shape])
        # Find random coordinate
        if shape.upper() == "DIAMOND":
            # Set restrictions on where the starting position can be
            # for 2D surface
            if surface.dimension == 2:
                # if the dimension is 2, we don't have to worry about z since it will just be zero
                x_possibility = range(domainLength + 1, surfaceLength - domainLength - 1)
                y_possibility = range(domainWidth + 1, surfaceWidth - domainWidth - 1)
                x = int(np.random.choice(x_possibility, 1, replace=False))
                y = int(np.random.choice(y_possibility, 1, replace=False))
                z = 0

            # for 3D surface
            elif surface.dimension == 3:
                if surface.shape.upper() == "SPHERE":
                    # define all the possible coordinates where domain can be generated
                    x_possibility = range(domainLength + 2, surfaceLength - domainLength - 2)
                    y_possibility = range(domainWidth + 2, surfaceWidth - domainWidth - 2)
                    z_possibility = range(domainWidth + 2, surfaceHeight - domainWidth - 2)

                    # first chose a random coordinate on the point
                    x = int(np.random.choice(x_possibility, 1, replace=False))
                    y = int(np.random.choice(y_possibility, 1, replace=False))
                    z = int(np.random.choice(z_possibility, 1, replace=False))
                    # then, pick a plane to generate the domain
                    plane = np.random.choice(["x", "y", "z"], 1, replace=False)
                    # if the chosen plane is x, that means x will be zero
                    if plane == "x":
                        # x will be either zero or surface.size[2] - 1
                        x = int(np.random.choice([0, surface.size[2]], 1, replace=False))
                    elif plane == "y":
                        # y will be either zero or surface.size[1] - 1
                        y = int(np.random.choice([0, surface.size[1]], 1, replace=False))
                    elif plane == "z":
                        # z will be either zero or surface.size[0] - 1
                        z = int(np.random.choice([0, surface.size[0]], 1, replace=False))


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

        coordinate = (x, y, z)
        writeLog("Point picked is: {}".format(coordinate))

        # return the result as tuple
        return coordinate

    def nearestPoint(self, surface: Surface, point: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        This function takes in a point and returns a point closest to that point on the surface
        NOTE: the function takes in point differently than other functions
        point = Tuple[z,y,x]
        nearestPoint = Tuple[z,y,x]
        """

        # for a 2D surface, return the point since we don't need to traverse through the z-axis
        if surface.shape[0] == 1:
            return point

        # showMessage("surface shape is {}".format(surface.shape))

        # if the point is already on the surface, return the point
        if surface[point[0], point[1], point[2]] != 2:
            return point

        # define condition where closest point is found
        found = False

        # Split the condition into different scenarios
        # if the point is generated on the far right side of the array
        if point[2] == surface.shape[2] - 1:
            while not found:
                # search by moving left
                point[2] -= 1
                # check if the point is on the surface
                if surface[point[0], point[1], point[2]] != 2:
                    found = True

        # if the point is generated on the far left side of the array
        elif point[2] == 0:
            while not found:
                # search by moving right
                point[2] += 1
                # check if the point is on the surface
                if surface[point[0], point[1], point[2]] != 2:
                    found = True

        # if the point is generated on the far behind the array
        if point[1] == 0:
            while not found:
                # search by moving down
                point[1] += 1
                # check if the point is on the surface
                if surface[point[0], point[1], point[2]] != 2:
                    found = True

        # if the point is generated on the far infront the array
        elif point[1] == surface.shape[1] - 1:
            while not found:
                # search by moving up
                point[1] -= 1
                # check if the point is on the surface
                if surface[point[0], point[1], point[2]] != 2:
                    found = True

        # if the point is generated on the far above the array
        elif point[0] == 0:
            while not found:
                # search by moving below
                point[0] += 1
                # check if the point is on the surface
                if surface[point[0], point[1], point[2]] != 2:
                    found = True

        # if the point is generated on the far below the array
        elif point[0] == surface.shape[0] - 1:
            while not found:
                # search by moving below
                point[0] -= 1
                # check if the point is on the surface
                if surface[point[0], point[1], point[2]] != 2:
                    found = True
        return point

    def _generateDiamond(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int, int],
                         charge_concentration: float, countCharge: List[int], totalCharge: List[int]) -> [ndarray, List[int]]:
        """
        This function generate diamond shape domain
        This function is adjusted based on:
        https://www.studymite.com/python/examples/program-to-print-diamond-pattern-in-python/
        :return return the surface with diamond domain on it
        startPoint = Tuple[x,y,z]
        """
        ln = domainWidth
        # Fill out diamond triangles
        eg = domainWidth + 1

        # in x-z plane:
        if startPoint[1] == 0 or startPoint[1] == surface.shape[1] - 1:
            for i in range(0, ln + 1):
                for j in range(0, eg):

                    # top right
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), startPoint[1], int(startPoint[0] + j)])
                    if surface[point[0], point[1], point[2]] == 0:
                        # Initialize either positive or negative charge
                        charge = self._generatePositiveNegative(charge_concentration, countCharge, totalCharge)
                        surface[point[0], point[1], point[2]] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge
                        elif charge == -1:
                            countCharge[1] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge

                    # top left
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), startPoint[1], int(startPoint[0] - j)])
                    if surface[point[0], point[1], point[2]] == 0:
                        # Initialize either positive or negative charge
                        charge = self._generatePositiveNegative(charge_concentration, countCharge, totalCharge)
                        surface[point[0], point[1], point[2]] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge
                        elif charge == -1:
                            countCharge[1] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge

                    # bottom right
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), startPoint[1], int(startPoint[0] + j)])
                    if surface[point[0], point[1], point[2]] == 0:
                        # Initialize either positive or negative charge
                        charge = self._generatePositiveNegative(charge_concentration, countCharge, totalCharge)
                        surface[point[0], point[1], point[2]] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge
                        elif charge == -1:
                            countCharge[1] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge

                    # bottom left
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), startPoint[1], int(startPoint[0] - j)])
                    if surface[point[0], point[1], point[2]] == 0:
                        # Initialize either positive or negative charge
                        charge = self._generatePositiveNegative(charge_concentration, countCharge, totalCharge)
                        surface[point[0], point[1], point[2]] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge
                        elif charge == -1:
                            countCharge[1] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge
                eg -= 1

        # in x-y plane
        if startPoint[2] == 0 or startPoint[2] == surface.shape[0] - 1:
            for i in range(0, ln + 1):
                for j in range(0, eg):

                    # top right
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] - i), int(startPoint[0] + j)])
                    if surface[point[0], point[1], point[2]] == 0:
                        # Initialize either positive or negative charge
                        charge = self._generatePositiveNegative(charge_concentration, countCharge, totalCharge)
                        surface[point[0], point[1], point[2]] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge
                        elif charge == -1:
                            countCharge[1] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge

                    # top left
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] - i), int(startPoint[0] - j)])
                    if surface[point[0], point[1], point[2]] == 0:
                        # Initialize either positive or negative charge
                        charge = self._generatePositiveNegative(charge_concentration, countCharge, totalCharge)
                        surface[point[0], point[1], point[2]] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge
                        elif charge == -1:
                            countCharge[1] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge

                    # bottom right
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] + i), int(startPoint[0] + j)])
                    if surface[point[0], point[1], point[2]] == 0:
                        # Initialize either positive or negative charge
                        charge = self._generatePositiveNegative(charge_concentration, countCharge, totalCharge)
                        surface[point[0], point[1], point[2]] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge
                        elif charge == -1:
                            countCharge[1] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge

                    # bottom left
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] + i), int(startPoint[0] - j)])
                    if surface[point[0], point[1], point[2]] == 0:
                        # Initialize either positive or negative charge
                        charge = self._generatePositiveNegative(charge_concentration, countCharge, totalCharge)
                        surface[point[0], point[1], point[2]] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge
                        elif charge == -1:
                            countCharge[1] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge
                eg -= 1

        # in y-z plane
        if startPoint[0] == 0 or startPoint[0] == surface.shape[2] - 1:
            for i in range(0, ln + 1):
                for j in range(0, eg):

                    # top right
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), int(startPoint[1] + j), startPoint[0]])
                    if surface[point[0], point[1], point[2]] == 0:
                        # Initialize either positive or negative charge
                        charge = self._generatePositiveNegative(charge_concentration, countCharge, totalCharge)
                        surface[point[0], point[1], point[2]] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge
                        elif charge == -1:
                            countCharge[1] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge

                    # top left
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), int(startPoint[1] - j), startPoint[0]])
                    if surface[point[0], point[1], point[2]] == 0:
                        # Initialize either positive or negative charge
                        charge = self._generatePositiveNegative(charge_concentration, countCharge, totalCharge)
                        surface[point[0], point[1], point[2]] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge
                        elif charge == -1:
                            countCharge[1] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge

                    # bottom right
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), int(startPoint[1] + j), startPoint[0]])
                    if surface[point[0], point[1], point[2]] == 0:
                        # Initialize either positive or negative charge
                        charge = self._generatePositiveNegative(charge_concentration, countCharge, totalCharge)
                        surface[point[0], point[1], point[2]] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge
                        elif charge == -1:
                            countCharge[1] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge

                    # bottom left
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), int(startPoint[1] - j), startPoint[0]])
                    if surface[point[0], point[1], point[2]] == 0:
                        # Initialize either positive or negative charge
                        charge = self._generatePositiveNegative(charge_concentration, countCharge, totalCharge)
                        surface[point[0], point[1], point[2]] = charge
                        # Add charge count
                        if charge == 1:
                            countCharge[0] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge
                        elif charge == -1:
                            countCharge[1] += 1
                            # check if the countCharge is the same as the total charge
                            if countCharge[0] == totalCharge[0] and countCharge[1] == totalCharge[1]:
                                return surface, countCharge
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
