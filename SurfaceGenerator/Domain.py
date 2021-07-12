"""
This program is generating the domain with some charge on it
Can be used for 2D, 3D and for testing surface, bacteria surface
"""
from numpy import ndarray
import numpy as np
from SurfaceGenerator.Surface import Surface
from typing import Tuple, List, Union
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
        :param surface: the surface want to generate the domain
        :param shape: shape of the domain
        :param size: size of the surface, in the format ###x###, in unit micrometer, 1micrometer = 100 points, NOTICE: size of domain must smaller than surface
        :param concentration: concentration of the charge?
        :param k:
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
            checkEmpty = self._diamondEmpty
            # Number of domains
            domainNum = int((surface.length * surface.width * concentration) / (domainWidth * domainLength))
        elif shape.upper() == "CROSS":
            generateShape = self._generateCross
            checkEmpty = self._crossEmpty
            # Number of domains
            domainNum = int((surface.length * surface.width * concentration) / (2 * domainWidth + 2 * domainLength))
        elif shape.upper() == "OCTAGON":
            generateShape = self._generateOctagon
            checkEmpty = self._octagonEmpty
            # Number of domains
            domainNum = int((surface.length * surface.width * concentration) / (
                    2 * (1 + math.sqrt(2)) * domainWidth * domainLength))
        elif shape.upper() == "SINGLE":
            generateShape = self._generateSingle
            checkEmpty = self._singleEmpty
            # Number of domains
            domainNum = int(surface.length * surface.width * concentration)
        else:
            raise RuntimeError("Unknown shape")

        showMessage("Domain number is: {}".format(domainNum))
        newSurface = surface.originalSurface[:]

        # make it either positive or negative
        # This can be later changed to allow user to input if they want a positive or negative surface charge
        surfaceCharge = np.random.choice([-1,1], 1, replace=False)[0]

        # the surfaceCharge and charge of domain should be the opposite
        # This can be later changed to allow users to input if they want a positive or negative domain charge
        if surfaceCharge == 1:
            charge = -1
        else:
            charge = 1

        # make the new surface either all positive or all negative
        newSurface[newSurface == 0] = surfaceCharge

        # record info into log
        showMessage("generate new surface done")
        writeLog(newSurface)
        writeLog("Charge of the surface is {}".format(surfaceCharge))

        # set the seed for random
        np.random.seed(self.seed)

        # initialize number of domain generated on the surface
        generated = 0

        # check generate domain number is not too small
        if generated >= domainNum:
            raise RuntimeError("Domain concentration is too low")

        # Determine all the possible points allowed to be chosen as the start point to begin generating the domain
        possiblePoint = self._allPossiblePoint(surface, surface.length, surface.width, surface.height, domainLength,
                                               domainWidth, shape)

        writeLog(possiblePoint)

        # initialize how long we want the code to run
        # if its running for too long, that means we most likely reached the maximum amount of domains on the surface and
        # end the while loop
        timeout = time.time() + 15      # 1 minute from now
        # start to generate the domain on surface
        while generated < domainNum:
            writeLog(timeout - time.time())
            # if the while loop has been running for too long, break the while loop
            if time.time() > timeout or len(possiblePoint) == 0:
                break
            # initialize a random point on the surface with restrictions and the updated possiblePoint
            [start, possiblePoint] = self._randomPoint(possiblePoint)

            # check the position of this shape is empty, if not empty, then continue
            if not checkEmpty(newSurface, domainWidth, domainLength, start, charge):
                continue

            # generate this shape's domain
            newSurface = generateShape(newSurface, domainWidth, domainLength, start, charge)

            # update generated number
            generated += 1

            showMessage("Generated domain number {}".format(generated))

        # return the surface generated based on k value
        return newSurface

    def _allPossiblePoint(self, surface: Surface, surfaceLength: int, surfaceWidth: int, surfaceHeight: int,
                          domainLength: int, domainWidth: int, shape: str) -> List[Tuple[int, int, int]]:
        """
        This function determines all the possible points the random point can start
        This function was created for 2 reasons:
            1. Function _randomPoint was getting too long
            2. It increases speed of the code since it now only chooses positions that has not already been chosen and
            avoids going through for loops each time _randomPoint function is called
        """
        # For diamond shape domain
        if shape.upper() == "DIAMOND":
            # Set restrictions on where the starting position can be
            # for 2D surface
            if surface.dimension == 2:
                # if the dimension is 2, we don't have to worry about z since it will just be zero
                x_possibility = range(domainLength + 1, surfaceLength - domainLength - 1)
                y_possibility = range(domainWidth + 1, surfaceWidth - domainWidth - 1)
                z_possibility = [0]
                # create list with all possible coordinates using list comprehension
                possibleCoordinate = [(i, j, k) for i in x_possibility for j in y_possibility for k in z_possibility]

            # for 3D surface
            elif surface.dimension == 3:
                if surface.shape.upper() == "SPHERE":
                    # define all the possible coordinates where domain can be generated
                    x_possibility = range(domainLength + 2, surfaceLength - domainLength - 2)
                    y_possibility = range(domainWidth + 2, surfaceWidth - domainWidth - 2)
                    z_possibility = range(domainWidth + 2, surfaceHeight - domainWidth - 2)
                    # create list with all possible coordinates using list comprehension
                    # when x is constant
                    possibleCoordinate1 = [(i, j, k) for i in [0, int(surface.shape[2]) - 1] for j in y_possibility for k in
                                           z_possibility]
                    # when y is constant
                    possibleCoordinate2 = [(i, j, k) for i in x_possibility for j in [0, int(surface.shape[1]) - 1] for k in
                                           z_possibility]
                    # when z is constant
                    possibleCoordinate3 = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                           [0, int(surface.shape[0]) - 1]]
                    # add all possible coordinates for each axis to get all possible coordinates
                    possibleCoordinate = possibleCoordinate1 + possibleCoordinate2 + possibleCoordinate3


        # for cross shape domain
        elif shape.upper() == "CROSS":
            # Set restrictions on where the starting positions can be
            # for 2D surface
            if surface.dimension == 2:
                x_possibility = range(domainLength + 1, surfaceLength - domainLength - 1)
                y_possibility = range(domainWidth + 1, surfaceWidth - domainWidth - 1)
                z_possibility = [0]
                # create list with all possible coordinates using list comprehension
                possibleCoordinate = [(i, j, k) for i in x_possibility for j in y_possibility for k in z_possibility]

            # for 3D surface
            elif surface.dimension == 3:
                if surface.shape.upper() == "SPHERE":
                    x_possibility = range(domainLength + 1, surfaceLength - domainLength - 1)
                    y_possibility = range(domainWidth + 1, surfaceWidth - domainWidth - 1)
                    z_possibility = range(domainWidth + 1, surfaceHeight - domainWidth - 1)
                    # create list with all possible coordinates using list comprehension
                    # when x is constant
                    possibleCoordinate1 = [(i, j, k) for i in [0, int(surface.shape[2]) - 1] for j in y_possibility for k in
                                           z_possibility]
                    # when y is constant
                    possibleCoordinate2 = [(i, j, k) for i in x_possibility for j in [0, int(surface.shape[1]) - 1] for k in
                                           z_possibility]
                    # when z is constant
                    possibleCoordinate3 = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                           [0, int(surface.shape[0]) - 1]]
                    # add all possible coordinates for each axis to get all possible coordinates
                    possibleCoordinate = possibleCoordinate1 + possibleCoordinate2 + possibleCoordinate3


        # for octagon shape domain
        elif shape.upper() == "OCTAGON":
            # Set restriction on where the starting positions can be
            # for 2D surface
            if surface.dimension == 2:
                # Separate cases for when domainLength/domainWidth are either even or odd
                if domainLength % 2 == 0:
                    x_possibility = range(int(domainLength + (domainLength / 2) + 1),
                                          int(surfaceLength - domainLength - (domainLength / 2) - 1))
                    y_possibility = range(int(domainWidth + (domainWidth / 2) + 1),
                                          int(surfaceWidth - domainWidth - (domainWidth / 2) - 1))
                    z_possibility = [0]
                elif domainLength % 2 == 1:
                    x_possibility = range(int(domainLength + ((domainLength + 1) / 2) + 1),
                                          int(surfaceLength - domainLength - ((domainLength + 1) / 2) - 1))
                    y_possibility = range(int(domainWidth + ((domainWidth + 1) / 2) + 1),
                                          int(surfaceWidth - domainWidth - ((domainWidth + 1) / 2) - 1))
                    z_possibility = [0]
                # create list with all possible coordinates using list comprehension
                possibleCoordinate = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                      z_possibility]

            # for 3D surface
            elif surface.dimension == 3:
                # Set restriction on where the starting positions can be
                # Separate cases for when domainLength/domainWidth are either even or odd
                # for 3D surface
                if surface.shape.upper() == "SPHERE":
                    # if the domainLength is an even number
                    if domainLength % 2 == 0:
                        # define all the possible coordinates where domain can be generated
                        x_possibility = range(int(domainLength + (domainLength / 2) + 1),
                                              int(surfaceLength - domainLength - (domainLength / 2) - 1))
                        y_possibility = range(int(domainWidth + (domainWidth / 2) + 1),
                                              int(surfaceWidth - domainWidth - (domainWidth / 2) - 1))
                        z_possibility = range(int(domainWidth + (domainWidth / 2) + 1),
                                              int(surfaceHeight - domainWidth - (domainWidth / 2) - 1))
                    # if the domainLength is an odd number
                    elif domainLength % 2 == 1:
                        x_possibility = range(int(domainLength + ((domainLength + 1) / 2) + 1),
                                              int(surfaceLength - domainLength - ((domainLength + 1) / 2) - 1))
                        y_possibility = range(int(domainWidth + ((domainWidth + 1) / 2) + 1),
                                              int(surfaceWidth - domainWidth - ((domainWidth + 1) / 2) - 1))
                        z_possibility = range(int(domainWidth + ((domainWidth + 1) / 2) + 1),
                                              int(surfaceHeight - domainWidth - ((domainWidth + 1) / 2) - 1))
                    # create list with all possible coordinates using list comprehension
                    # when x is constant
                    possibleCoordinate1 = [(i, j, k) for i in [0, surface.shape[2] - 1] for j in y_possibility for k in
                                           z_possibility]
                    # when y is constant
                    possibleCoordinate2 = [(i, j, k) for i in x_possibility for j in [0, int(surface.shape[1]) - 1] for k in
                                           z_possibility]
                    # when z is constant
                    possibleCoordinate3 = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                           [0, int(surface.shape[0]) - 1]]
                    # add all possible coordinates for each axis to get all possible coordinates
                    possibleCoordinate = possibleCoordinate1 + possibleCoordinate2 + possibleCoordinate3


        # for single shape domain
        elif shape.upper() == "SINGLE":
            # Set restriction on where the starting positions can be
            # for 2D surface
            if surface.dimension == 2:
                # If the surface is 2D, x and y just has to be on the rectangle surface
                # define all the possible coordinates where domain can be generated
                x_possibility = range(2, surfaceLength - 2)
                y_possibility = range(2, surfaceWidth - 2)
                z_possibility = [0]
                # create list with all possible coordinates using list comprehension
                possibleCoordinate = [(i, j, k) for i in x_possibility for j in y_possibility for k in z_possibility]

            # for 3D surface
            elif surface.dimension == 3:
                if surface.shape.upper() == "SPHERE":
                    # If the surface was a sphere, the points must fall in a circle with the radius of either
                    # surface.length, surface.width or surface.height
                    radius = min(surface.length, surface.width, surface.height)
                    # create an empty list to append the coordinates to
                    possibleCoordinate = []
                    # calculate the center of the sphere along x, y, and z axis
                    # center of the 3D surface
                    cen = (int(surface.length / 2), int(surface.width / 2), int(surface.height / 2))

                    # locate all the points that fall inside the circle
                    # when keeping x constant
                    for k in range(int(surface.shape[0])):
                        for j in range(int(surface.shape[1])):
                            # calculate the distance from the startPoint to the chosen point
                            dist1 = ((j - cen[1]) ** 2 + (k - cen[2]) ** 2) ** 0.5
                            if radius >= dist1:
                                possibleCoordinate.append((0, j, k))
                                possibleCoordinate.append((int(surface.shape[2] - 1), j, k))
                    # when keeping y constant
                    for k in range(int(surface.shape[0])):
                        for i in range(int(surface.shape[2])):
                            # calculate the distance from the startPoint to the chosen point
                            dist1 = ((i - cen[0]) ** 2 + (k - cen[2]) ** 2) ** 0.5
                            if radius >= dist1:
                                possibleCoordinate.append((i, 0, k))
                                possibleCoordinate.append((i, int(surface.shape[1] - 1), k))
                    # when keeping z constant
                    for j in range(int(surface.shape[1])):
                        for i in range(int(surface.shape[2])):
                            # calculate the distance from the startPoint to the chosen point
                            dist1 = ((i - cen[0]) ** 2 + (j - cen[1]) ** 2) ** 0.5
                            if radius >= dist1:
                                possibleCoordinate.append((i, j, 0))
                                possibleCoordinate.append((i, j, int(surface.shape[0] - 1)))

        else:
            raise RuntimeError("Wrong shape in the function _allPossiblePoint")

        return possibleCoordinate

    def _randomPoint(self, possiblePoint: List[Tuple[int, int, int]]) \
            -> [Tuple[int, int, int], List[Tuple[int, int, int]]]:
        """
        Randomly pick a point on the surface given
        :return a tuple represent a point in the surface in the matrix
        NOTE: For the 2D surface, it is currently under the assumption that it is a RECTANGLE. Therefore need to change
        for different shape for 2D
        """
        # writeLog("This is _randomPoint in Domain.py")
        # writeLog([self.__dict__, surfaceLength, surfaceWidth, domainLength, domainWidth, shape])
        # choose a random index
        index = np.random.randint(len(possiblePoint))
        writeLog(index)
        # return the coordinate
        coordinate = possiblePoint[index]
        # remove the chosen coordinate from all possiblepoints
        possiblePoint.pop(index)


        writeLog("Point picked is: {}".format(coordinate))

        # return the result as tuple
        return coordinate, possiblePoint

    def nearestPoint(self, surface: Surface, point: List[Union[int, int, int]]) -> List[Union[int, int, int]]:
        """
        This function takes in a point and returns a point closest to that point on the surface
        NOTE: the function takes in point differently than other functions
        point = Tuple[z,y,x]
        nearestPoint = Tuple[z,y,x]
        charge = charge of domain
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
        if point[2] == int(surface.shape[2]) - 1:
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
        elif point[1] == int(surface.shape[1]) - 1:
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
        elif point[0] == int(surface.shape[0]) - 1:
            while not found:
                # search by moving below
                point[0] -= 1
                # check if the point is on the surface
                if surface[point[0], point[1], point[2]] != 2:
                    found = True
        return point

    def _diamondEmpty(self, surface: Surface, domainWidth: int, domainLength: int, startPoint: int, charge: int) \
            -> bool:
        """
        This function check the position want to generate diamond whether is empty
        :return True if all empty, False for no
        """

        ln = domainWidth
        # Fill out diamond triangles
        eg = domainWidth + 1

        # in x-z plane:
        if startPoint[1] == 0 or startPoint[1] == int(surface.shape[1]) - 1:
            for i in range(0, ln + 1):
                for j in range(0, eg):

                    # top right
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), startPoint[1], int(startPoint[0] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        return False

                    # top left
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), startPoint[1], int(startPoint[0] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        return False

                    # bottom right
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), startPoint[1], int(startPoint[0] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        return False

                    # bottom left
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), startPoint[1], int(startPoint[0] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        return False

                eg -= 1

        # in x-y plane
        if startPoint[2] == 0 or startPoint[2] == int(surface.shape[0]) - 1:
            for i in range(0, ln + 1):
                for j in range(0, eg):

                    # top right
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] - i), int(startPoint[0] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        return False

                    # top left
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] - i), int(startPoint[0] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        return False

                    # bottom right
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] + i), int(startPoint[0] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        return False

                    # bottom left
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] + i), int(startPoint[0] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        return False
                eg -= 1

        # in y-z plane
        if startPoint[0] == 0 or startPoint[0] == int(surface.shape[2]) - 1:
            for i in range(0, ln + 1):
                for j in range(0, eg):

                    # top right
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), int(startPoint[1] + j), startPoint[0]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        return False

                    # top left
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), int(startPoint[1] - j), startPoint[0]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        return False

                    # bottom right
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), int(startPoint[1] + j), startPoint[0]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        return False

                    # bottom left
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), int(startPoint[1] - j), startPoint[0]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        return False
                eg -= 1

        return True

    def _generateDiamond(self, surface: Surface, domainWidth: int, domainLength: int, startPoint: int, charge: int) \
            -> ndarray:
        """
        This function generate diamond shape domain
        :return return the surface with diamond domain on it
        """
        ln = domainWidth
        # Fill out diamond triangles
        eg = domainWidth + 1

        # in x-z plane:
        if startPoint[1] == 0 or startPoint[1] == int(surface.shape[1]) - 1:
            for i in range(0, ln + 1):
                for j in range(0, eg):

                    # top right
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), startPoint[1], int(startPoint[0] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        raise RuntimeError("Domain is being generated on an existing domain")
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # top left
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), startPoint[1], int(startPoint[0] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        raise RuntimeError("Domain is being generated on an existing domain")
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom right
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), startPoint[1], int(startPoint[0] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        raise RuntimeError("Domain is being generated on an existing domain")
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom left
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), startPoint[1], int(startPoint[0] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        raise RuntimeError("Domain is being generated on an existing domain")
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge


                eg -= 1

        # in x-y plane
        if startPoint[2] == 0 or startPoint[2] == int(surface.shape[0]) - 1:
            for i in range(0, ln + 1):
                for j in range(0, eg):

                    # top right
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] - i), int(startPoint[0] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # top left
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] - i), int(startPoint[0] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom right
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] + i), int(startPoint[0] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom left
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] + i), int(startPoint[0] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                eg -= 1

        # in y-z plane
        if startPoint[0] == 0 or startPoint[0] == int(surface.shape[2]) - 1:
            for i in range(0, ln + 1):
                for j in range(0, eg):

                    # top right
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), int(startPoint[1] + j), startPoint[0]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        raise RuntimeError("Domain is being generated on an existing domain")
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # top left
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), int(startPoint[1] - j), startPoint[0]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        raise RuntimeError("Domain is being generated on an existing domain")
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom right
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), int(startPoint[1] + j), startPoint[0]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        raise RuntimeError("Domain is being generated on an existing domain")
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom left
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), int(startPoint[1] - j), startPoint[0]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] == charge:
                        raise RuntimeError("Domain is being generated on an existing domain")
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                eg -= 1

        return surface

    def _crossEmpty(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: int):
        """
        This function check the position want to generate octagon is empty
        """
        # Change the names for each variable
        cen = startPoint
        # create the vertical line of the cross
        for i in range(domainWidth + 1):
            if surface[cen[0] + i - 1, cen[1] - 1] == 1:
                return False
            if surface[cen[0] - i - 1, cen[1] - 1] == 1:
                return False

        # create the horizontal line of the cross
        for j in range(domainLength + 1):
            if surface[cen[0] - 1, cen[1] + j - 1] == 1:
                return False
            if surface[cen[0] - 1, cen[1] - j - 1] == 1:
                return False

        return True

    def _generateCross(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int]):
        """
        This function generate cross shape for surface
        """
        # Change the names for each variable
        cen = startPoint
        # create the vertical line of the cross
        for i in range(domainWidth + 1):
            surface[cen[0] + i - 1, cen[1] - 1] = 1
            surface[cen[0] - i - 1, cen[1] - 1] = 1

        # create the horizontal line of the cross
        for j in range(domainLength + 1):
            surface[cen[0] - 1, cen[1] + j - 1] = 1
            surface[cen[0] - 1, cen[1] - j - 1] = 1

        return surface

    def _octagonEmpty(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int]):
        """
        This function check the position want to generate cross is empty
        """
        # domainWidth and domainLength should be the same
        if domainWidth != domainLength:
            return 'domainWidth and domainLength should be the same'

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
                    if surface[int(cen[0] + (0.5 + i)), int(cen[1] + (0.5 + j))] == 1:
                        return False
                    if surface[int(cen[0] + (0.5 + i)), int(cen[1] - (0.5 + j))] == 1:
                        return False
                    if surface[int(cen[0] - (0.5 + i)), int(cen[1] + (0.5 + j))] == 1:
                        return False
                    if surface[int(cen[0] - (0.5 + i)), int(cen[1] - (0.5 + j))] == 1:
                        return False

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
                    if surface[int(cen[0] + i), int(cen[1] + j)] == 1:
                        return False
                    if surface[int(cen[0] + i), int(cen[1] - j)] == 1:
                        return False
                    if surface[int(cen[0] - i), int(cen[1] + j)] == 1:
                        return False
                    if surface[int(cen[0] - i), int(cen[1] - j)] == 1:
                        return False

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
                if surface[int(ed_tr[0] - i), int(ed_tr[1] + j)] == 1:
                    return False
            nu_tr -= 1

        # top left
        nu_tl = ln + 1
        for i in range(0, ln + 1):
            for j in range(0, nu_tl):
                if surface[int(ed_tl[0] - i), int(ed_tl[1] - j)] == 1:
                    return False
            nu_tl -= 1

        # bottom right
        nu_br = ln + 1
        for i in range(0, ln + 1):
            for j in range(0, nu_br):
                if surface[int(ed_br[0] + i), int(ed_br[1] + j)] == 1:
                    return False
            nu_br -= 1

        # bottom left triangle
        nu_bl = ln + 1
        for i in range(0, ln + 1):
            for j in range(0, nu_bl):
                if surface[int(ed_bl[0] + i), int(ed_bl[1] - j)] == 1:
                    return False
            nu_bl -= 1

        # Finally, fill out the remaining 4 squares
        # top square
        for i in range(1, ln + 1):
            for j in range(1, ln + 1):
                if surface[int(ed_tl[0] - i), int(ed_tl[1] + j)] == 1:
                    return False

        # left square
        for i in range(1, ln + 1):
            for j in range(1, ln + 1):
                if surface[int(ed_tl[0] + i), int(ed_tl[1] - j)] == 1:
                    return False

        # right square
        for i in range(1, ln + 1):
            for j in range(1, ln + 1):
                if surface[int(ed_br[0] - i), int(ed_br[1] + j)] == 1:
                    return False

        # bottom square
        for i in range(1, ln + 1):
            for j in range(1, ln + 1):
                if surface[int(ed_br[0] + i), int(ed_br[1] - j)] == 1:
                    return False
        return True
    def _generateOctagon(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int]):
        """
        This function generate octagon shape for surface
        """
        # TODO:
        # domainWidth and domainLength should be the same
        if domainWidth != domainLength:
            return 'domainWidth and domainLength should be the same'

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
                    surface[int(cen[0] + (0.5 + i)), int(cen[1] + (0.5 + j))] = 1
                    surface[int(cen[0] + (0.5 + i)), int(cen[1] - (0.5 + j))] = 1
                    surface[int(cen[0] - (0.5 + i)), int(cen[1] + (0.5 + j))] = 1
                    surface[int(cen[0] - (0.5 + i)), int(cen[1] - (0.5 + j))] = 1

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
                    surface[int(cen[0] + i), int(cen[1] + j)] = 1
                    surface[int(cen[0] + i), int(cen[1] - j)] = 1
                    surface[int(cen[0] - i), int(cen[1] + j)] = 1
                    surface[int(cen[0] - i), int(cen[1] - j)] = 1

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
                surface[int(ed_tr[0] - i), int(ed_tr[1] + j)] = 1
            nu_tr -= 1

        # top left
        nu_tl = ln + 1
        for i in range(0, ln + 1):
            for j in range(0, nu_tl):
                surface[int(ed_tl[0] - i), int(ed_tl[1] - j)] = 1
            nu_tl -= 1

        # bottom right
        nu_br = ln + 1
        for i in range(0, ln + 1):
            for j in range(0, nu_br):
                surface[int(ed_br[0] + i), int(ed_br[1] + j)] = 1
            nu_br -= 1

        # bottom left triangle
        nu_bl = ln + 1
        for i in range(0, ln + 1):
            for j in range(0, nu_bl):
                surface[int(ed_bl[0] + i), int(ed_bl[1] - j)] = 1
            nu_bl -= 1

        # Finally, fill out the remaining 4 squares
        # top square
        for i in range(1, ln + 1):
            for j in range(1, ln + 1):
                surface[int(ed_tl[0] - i), int(ed_tl[1] + j)] = 1

        # left square
        for i in range(1, ln + 1):
            for j in range(1, ln + 1):
                surface[int(ed_tl[0] + i), int(ed_tl[1] - j)] = 1

        # right square
        for i in range(1, ln + 1):
            for j in range(1, ln + 1):
                surface[int(ed_br[0] - i), int(ed_br[1] + j)] = 1

        # bottom square
        for i in range(1, ln + 1):
            for j in range(1, ln + 1):
                surface[int(ed_br[0] + i), int(ed_br[1] - j)] = 1
        return surface

    def _singleEmpty(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: int):
        """
        This function check the position want to generate single is empty
        """
        # TODO:
        if surface[int(startPoint[0]),int(startPoint[1])] == 1:
            return False

        return True

    def _generateSingle(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: int):
        """
        This function generate single shape for surface
        """
        # TODO:
        surface[int(startPoint[0]),int(startPoint[1])] = 1
        return surface
