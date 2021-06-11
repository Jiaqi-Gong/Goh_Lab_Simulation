"""
This program is generating the domain with some charge on it
Can be used for 2D, 3D and for testing surface, bacteria surface
"""
import random

from numpy import ndarray
import numpy as np
from typing import Tuple
import Surface


class DomainGenerator:
    """
    This class is used to generate the domain on the surface passed in
    """

    def __init__(self, trail: int, seed: int):
        """
        Init this domain generate
        :param trail: trail number
        :param seed: seed for random, if using same seed can repeat the simulation
        """
        self.trail = trail
        self.seed = seed

    def generateDomain(self, surface: Surface, shape: str, size: str, concentration: float):
        """
        This function takes in a surface, shape and size of domain want to generate on the surface
        :param surface: the surface want to generate the domain
        :param shape: shape of the domain
        :param size: size of the surface, in the format ###x###, in unit micrometer, 1micrometer = 100 points, NOTICE: size of domain must smaller than surface
        :param concentration: concentration of the charge
        :return: return the surface with wanted domain on it
        """

        # get size
        size = size.split("x")
        domainWidth = int(size[0]) * 100
        domainLength = int(size[1]) * 100

        # calculate how many domain should generate
        domainNum = int((surface.width * surface.length * concentration) / (domainWidth * domainLength))

        # first, make entire passed in surface positive
        newSurface = self._makeSurfacePositive(surface)

        # init generated domain number
        generated = 0

        # set seed for random
        np.random.seed(self.seed)

        # init two variable
        # just random pick one
        checkEmpty = self._diamondEmpty
        generateShape = self._generateDiamond

        # set corresponding check and generate function
        # generate the corresponding domain shape
        if shape.upper() == "DIAMOND":
            # diamond should have same width and length
            checkEmpty = self._diamondEmpty
            generateShape = self._generateDiamond
        elif shape.upper() == "CROSS":
            checkEmpty = self._crossEmpty
            generateShape = self._generateCross
        elif shape.upper() == "OCTAGON":
            checkEmpty = self._octagonEmpty
            generateShape = self._generateOctagon
        elif shape.upper() == "SINGLE":
            checkEmpty = self._singleEmpty
            generateShape = self._generateSingle

        # more shape coming soon, leave for more extension

        # start to generate the domain on surface
        while generated < domainNum:
            # pick a point as the start of the diamond shape, which point is the toppest point of the diamond shape

            # pick a point in the matrix as the start point of generate domain
            # randint pick x and y, leave the enough space for not touching the edge
            start = self._randomPoint(surface.length, surface.width, domainLength, domainWidth)

            # check the position of this shape is empty, if not empty, then continue
            if not checkEmpty(newSurface, domainWidth, domainLength, start):
                continue

            # generate this shape's domain
            surface = generateShape(newSurface, domainWidth, domainLength, start)

            # update generated number
            generated += 1

        # return the surface generated based on k value
        return surface

    def _makeSurfacePositive(self, passInSurface):
        """
        Make the entire surface passed in positive, which means set all values in the passed in nested list to 1
        """
        # get the original surface in the passed in surface
        positiveSurface = passInSurface.origionalSurface

        # if passed in is a 2D surface
        if passInSurface.dimension == 2:
            # access each row
            for i in range(len(positiveSurface)):
                # access each point
                for j in range(len(positiveSurface[i])):
                    # set the value in position to 1, which means positive
                    positiveSurface[i][j] = 1

        # if passed in is a 3D surface
        elif passInSurface.dimension == 3:
            # access each row
            for i in range(len(positiveSurface)):
                # access each column
                for j in range(len(positiveSurface[i])):
                    # access each height
                    for k in range(len(positiveSurface[i][j])):
                        # set the value in position to 1, which means positive
                        positiveSurface[i][j][k] = 1

        else:
            raise RuntimeError("Surface passed in is not 2D or 3D")

        return positiveSurface


    def _randomPoint(self, surfaceLength: int, surfaceWidth: int, domainLength: int, domainWidth: int) -> Tuple[int, int]:
        """
        Randomly pick a point on the surface given
        :return a tuple represent a point in the surface in the matrix
        """
        # pick a point on x-axis, this point should have enough space for domain to generate
        # without touch the boundary of surface
        x = random.randint(domainWidth, surfaceWidth - domainWidth)

        # pick a point on y-axis, this point should have enough space for domain to generate
        # without touch the boundary of surface
        y = random.randint(domainLength, surfaceLength - domainLength)

        # return the result as tuple
        return (x, y)


    def _diamondEmpty(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int]):
        """
        This function check the position want to generate diamond whether is empty
        This function is adjusted based on:
        https://www.studymite.com/python/examples/program-to-print-diamond-pattern-in-python/
        :return True if all empty, False for no
        """
        # set the new name
        n = domainWidth
        start = startPoint

        # set a variable for checking the width
        count = 0

        # make upper diamond
        for i in range(0, n + 1):
            for j in range(-count + 1, count):
                if surface[start[0] + i][start[1] + j] == 1:
                    return False

            # upper part, width becomes wider
            count += 1

        # make lower diamond
        for i in range(n + 1, 2 * (n + 1) + 1):
            for j in range(-count + 1, count):
                if surface[start[0] + i][start[1] - j] == 1:
                    return False

            # lower part, width becomes thinner
            count -= 1

        # return the checking result
        return True

    def _generateDiamond(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int]):
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
                surface[start[0] + i][start[1] + j] = 1

            # upper part, width becomes wider
            count += 1

        # make lower diamond
        for i in range(n + 1, 2 * (n + 1) + 1):
            for j in range(-count + 1, count):
                surface[start[0] + i][start[1] - j] = 1

            # lower part, width becomes thinner
            count -= 1

        # return the generated surface
        return surface

    """######################
    Rei and Nico do the function below, implement the function with # TODO: 
    You can read the code I write for diamond as example
    Basically, XXXEmpty and generateXXX are using mostly same code, the only different is the code in nested loop are 
    different, XXXEmpty is checking whether the number store in the position is 1, and it it's 1 then return False,
    generateXXX is doing the same loop just change the adjust part into assign the value store in the position to 1 
    for the shape want to generate, refer to Stanley's old code
    """#####################



    def _crossEmpty(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int]):
        """
        This function check the position want to generate cross is empty
        """
        # TODO:
        return surface

    def _generateCross(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int]):
        """
        This function generate cross shape for surface
        """
        # TODO:
        return surface

    def _octagonEmpty(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int]):
        """
        This function check the position want to generate octagon is empty
        """
        # TODO:
        return surface

    def _generateOctagon(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int]):
        """
        This function generate octagon shape for surface
        """
        # TODO:
        return surface

    def _singleEmpty(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int]):
        """
        This function check the position want to generate single is empty
        """
        # TODO:
        return surface

    def _generateSingle(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int]):
        """
        This function generate single shape for surface
        """
        # TODO:
        return surface
