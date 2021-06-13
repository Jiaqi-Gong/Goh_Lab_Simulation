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

    def __init__(self, seed: int):
        """
        Init this domain generate
        :param seed: seed for random, if using same seed can repeat the simulation
        """
        self.seed = seed

    def generateDomain(self, surface: Surface, shape: str, size: Tuple[int, int], concentration: float):
        """
        This function takes in a surface, shape and size of domain want to generate on the surface
        :param surface: the surface want to generate the domain
        :param shape: shape of the domain
        :param size: size of the surface, in unit micrometer, 1micrometer = 100 points, NOTICE: size of domain must smaller than surface
        :param concentration: concentration of the charge
        :return: return the surface with wanted domain on it
        """

        # get size
        domainLength = size[0] * 100
        domainWidth = size[1] * 100

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

    def _crossEmpty(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: int):
        """
        This function check the position want to generate cross is empty
        """
        # TODO:
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
        # TODO:
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
        This function check the position want to generate octagon is empty
        """
        # TODO:

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
