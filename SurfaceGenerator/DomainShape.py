"""
This file is used to clean up the domain.py file since it was getting very long
It contains all the functions to generate and check all shapes of the domains
"""
from numpy import ndarray
import numpy as np
from SurfaceGenerator.Surface import Surface
from typing import Tuple, List, Union
from ExternalIO import showMessage, writeLog, visPlot
import math
import time
from multiprocessing import Pool, cpu_count
from functools import partial
import os

class DomainShapeGeneration:
    """
    This class is used to generate the domain shapes
    """

    def __init__(self):
        pass

    def nearestPoint(self, surface: Surface, point: List[Union[int, int, int]]) -> List[Union[int, int, int]]:
        """
        This function takes in a point and returns a point closest to that point on the surface
        NOTE: the function takes in point differently than other functions
        point = Tuple[z,y,x]
        nearestPoint = Tuple[z,y,x]
        """

        # for a 2D surface, return the point since we don't need to traverse through the z-axis
        if surface.shape[0] == 1:
            return point

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

    def _diamondEmpty(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int, int],
                      possible_charge: List[int]) -> bool:
        """
        This function check the position we want to generate diamond is empty
        :return True if all empty, False for no
        charge -> the charge of the domain
        possible_charge -> all possible charges the domain can have (a tuple with 2 integers either 0,1,-1)
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
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                    # top left
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), startPoint[1], int(startPoint[0] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                    # bottom right
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), startPoint[1], int(startPoint[0] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                    # bottom left
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), startPoint[1], int(startPoint[0] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                eg -= 1

        # in x-y plane
        if startPoint[2] == 0 or startPoint[2] == int(surface.shape[0]) - 1:
            for i in range(0, ln + 1):
                for j in range(0, eg):

                    # top right
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] - i), int(startPoint[0] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                    # top left
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] - i), int(startPoint[0] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                    # bottom right
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] + i), int(startPoint[0] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                    # bottom left
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] + i), int(startPoint[0] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                eg -= 1

        # in y-z plane
        if startPoint[0] == 0 or startPoint[0] == int(surface.shape[2]) - 1:
            for i in range(0, ln + 1):
                for j in range(0, eg):

                    # top right
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), int(startPoint[1] + j), startPoint[0]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                    # top left
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), int(startPoint[1] - j), startPoint[0]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                    # bottom right
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), int(startPoint[1] + j), startPoint[0]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                    # bottom left
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), int(startPoint[1] - j), startPoint[0]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                eg -= 1

        return True


    def _generateDiamond(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int, int],
                         charge: int) -> ndarray:
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
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                    # top left
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), startPoint[1], int(startPoint[0] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                    # bottom right
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), startPoint[1], int(startPoint[0] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                    # bottom left
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), startPoint[1], int(startPoint[0] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                eg -= 1

        # in x-y plane
        if startPoint[2] == 0 or startPoint[2] == int(surface.shape[0]) - 1:
            for i in range(0, ln + 1):
                for j in range(0, eg):
                    # top right
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] - i), int(startPoint[0] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                    # top left
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] - i), int(startPoint[0] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                    # bottom right
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] + i), int(startPoint[0] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                    # bottom left
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] + i), int(startPoint[0] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                eg -= 1

        # in y-z plane
        if startPoint[0] == 0 or startPoint[0] == int(surface.shape[2]) - 1:
            for i in range(0, ln + 1):
                for j in range(0, eg):
                    # top right
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), int(startPoint[1] + j), startPoint[0]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                    # top left
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), int(startPoint[1] - j), startPoint[0]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                    # bottom right
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), int(startPoint[1] + j), startPoint[0]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                    # bottom left
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), int(startPoint[1] - j), startPoint[0]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                eg -= 1
        return surface


    def _crossEmpty(self, surface: Surface, domainWidth: int, domainLength: int, startPoint: Tuple[int, int, int],
                    possible_charge: List[int]) -> bool:
        """
        This function check the position we want to generate cross is empty
        :return True if all empty, False for no
        """

        # in the y-z plane (keep x constant)
        if startPoint[0] == 0 or startPoint[0] == int(surface.shape[2]) - 1:
            # create the vertical line of the cross
            for i in range(domainWidth + 1):
                # bottom line
                point = self.nearestPoint(surface, [int(startPoint[2] + i), int(startPoint[1]), startPoint[0]])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

                # top line
                point = self.nearestPoint(surface, [int(startPoint[2] - i), int(startPoint[1]), startPoint[0]])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

            # create the horizontal line of the cross
            for j in range(domainLength + 1):
                # right line
                point = self.nearestPoint(surface, [int(startPoint[2]), int(startPoint[1] + j), startPoint[0]])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

                # left line
                point = self.nearestPoint(surface, [int(startPoint[2]), int(startPoint[1] - j), startPoint[0]])
                if surface[point[0], point[1], point[2]] == 0:
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        return False

        # in the x-z plane (keep y constant)
        if startPoint[1] == 0 or startPoint[1] == int(surface.shape[1]) - 1:
            # create the vertical line of the cross
            for i in range(domainWidth + 1):
                # bottom line
                point = self.nearestPoint(surface, [int(startPoint[2] + i), startPoint[1], int(startPoint[0])])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

                # top line
                point = self.nearestPoint(surface, [int(startPoint[2] - i), startPoint[1], int(startPoint[0])])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

            # create the horizontal line of the cross
            for j in range(domainLength + 1):
                # right line
                point = self.nearestPoint(surface, [int(startPoint[2]), startPoint[1], int(startPoint[0] + j)])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

                # left line
                point = self.nearestPoint(surface, [int(startPoint[2]), startPoint[1], int(startPoint[0] - j)])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

        # in the x-y plane (keep z constant)
        if startPoint[2] == 0 or startPoint[2] == int(surface.shape[0]) - 1:
            # create the vertical line of the cross
            for i in range(domainWidth + 1):
                # bottom line
                point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] + i), int(startPoint[0])])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

                # top line
                point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] - i), int(startPoint[0])])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

            # create the horizontal line of the cross
            for j in range(domainLength + 1):
                # right line
                point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1]), int(startPoint[0] + j)])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

                # left line
                point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1]), int(startPoint[0] - j)])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False
        return True


    def _generateCross(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int, int],
                       charge: int) -> ndarray:
        """
        This function generate cross shape for surface
        """
        # in the y-z plane (keep x constant)
        if startPoint[0] == 0 or startPoint[0] == int(surface.shape[2]) - 1:
            # create the vertical line of the cross
            for i in range(domainWidth + 1):
                # bottom line
                point = self.nearestPoint(surface, [int(startPoint[2] + i), int(startPoint[1]), startPoint[0]])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

                # top line
                point = self.nearestPoint(surface, [int(startPoint[2] - i), int(startPoint[1]), startPoint[0]])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

            # create the horizontal line of the cross
            for j in range(domainLength + 1):
                # right line
                point = self.nearestPoint(surface, [int(startPoint[2]), int(startPoint[1] + j), startPoint[0]])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

                # left line
                point = self.nearestPoint(surface, [int(startPoint[2]), int(startPoint[1] - j), startPoint[0]])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

        # in the x-z plane (keep y constant)
        if startPoint[1] == 0 or startPoint[1] == int(surface.shape[1]) - 1:
            # create the vertical line of the cross
            for i in range(domainWidth + 1):
                # bottom line
                point = self.nearestPoint(surface, [int(startPoint[2] + i), startPoint[1], int(startPoint[0])])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

                # top line
                point = self.nearestPoint(surface, [int(startPoint[2] - i), startPoint[1], int(startPoint[0])])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

            # create the horizontal line of the cross
            for j in range(domainLength + 1):
                # right line
                point = self.nearestPoint(surface, [int(startPoint[2]), startPoint[1], int(startPoint[0] + j)])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

                # left line
                point = self.nearestPoint(surface, [int(startPoint[2]), startPoint[1], int(startPoint[0] - j)])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

        # in the x-y plane (keep z constant)
        if startPoint[2] == 0 or startPoint[2] == int(surface.shape[0]) - 1:
            # create the vertical line of the cross
            for i in range(domainWidth + 1):
                # bottom line
                point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] + i), int(startPoint[0])])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

                # top line
                point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] - i), int(startPoint[0])])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

            # create the horizontal line of the cross
            for j in range(domainLength + 1):
                # right line
                point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1]), int(startPoint[0] + j)])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

                # left line
                point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1]), int(startPoint[0] - j)])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge
        return surface


    def _octagonEmpty(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int, int],
                      possible_charge: List[int]) -> bool:
        """
        This function check the position want to generate cross is empty
        """
        # Rename variables and change startPoint from tuple to list
        ln = domainWidth
        cen = list(startPoint)
        # Find the center of the octagon
        # If the length is an odd number, the center of the octagon should be located between 4 points (ie center point should end as .5)
        # for x
        if cen[0] % 2 == 0 and ln % 2 == 1 and cen[0] != 0 and cen[0] != surface.shape[2] - 1:
            cen[0] = cen[0] - 0.5

        # for y
        if cen[1] % 2 == 0 and ln % 2 == 1 and cen[1] != 0 and cen[1] != surface.shape[1] - 1:
            cen[1] = cen[1] - 0.5

        # for z
        if cen[2] % 2 == 0 and ln % 2 == 1 and cen[2] != 0 and cen[2] != surface.shape[0] - 1:
            cen[2] = cen[2] - 0.5

        # in y-z plane (keep x constant)
        if startPoint[0] == 0 or startPoint[0] == int(surface.shape[2]) - 1:
            # Separate conditions between if the length is odd or even
            # If the length is odd
            if ln % 2 == 1:
                # Initial square surrounding the center
                n = int(ln / 2 + 0.5)
                for i in range(n):
                    for j in range(n):
                        # 1st point
                        point = self.nearestPoint(surface, [int(cen[2] + (0.5 + i)), int(cen[1] - (0.5 + j)), cen[0]])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 2nd point
                        point = self.nearestPoint(surface, [int(cen[2] + (0.5 + i)), int(cen[1] + (0.5 + j)), cen[0]])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 3rd point
                        point = self.nearestPoint(surface, [int(cen[2] - (0.5 + i)), int(cen[1] + (0.5 + j)), cen[0]])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 4th point
                        point = self.nearestPoint(surface, [int(cen[2] - (0.5 + i)), int(cen[1] - (0.5 + j)), cen[0]])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False

            # If the length is even
            elif ln % 2 == 0:
                # Initial square surrounding the center
                n = int(ln / 2)
                for i in range(n + 1):
                    for j in range(n + 1):
                        # 1st points
                        point = self.nearestPoint(surface, [int(cen[2] + i), int(cen[1] + j), cen[0]])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 2nd points
                        point = self.nearestPoint(surface, [int(cen[2] + i), int(cen[1] - j), cen[0]])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 3rd points
                        point = self.nearestPoint(surface, [int(cen[2] - i), int(cen[1] + j), cen[0]])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 4th points
                        point = self.nearestPoint(surface, [int(cen[2] - i), int(cen[1] - j), cen[0]])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False

            # Index edges of the square
            # top right edge
            ed_tr = [int(cen[2] - ln / 2), int(cen[1] + ln / 2), cen[0]]
            # top left edge
            ed_tl = [int(cen[2] - ln / 2), int(cen[1] - ln / 2), cen[0]]
            # bottom right edge
            ed_br = [int(cen[2] + ln / 2), int(cen[1] + ln / 2), cen[0]]
            # bottom left edge
            ed_bl = [int(cen[2] + ln / 2), int(cen[1] - ln / 2), cen[0]]

            # Fill out the 4 triangles
            # top right
            eg = ln + 1
            for i in range(0, ln + 1):
                for j in range(0, eg):
                    # top right
                    point = self.nearestPoint(surface, [int(ed_tr[0] - i), int(ed_tr[1] + j), ed_tr[2]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # top left
                    point = self.nearestPoint(surface, [int(ed_tl[0] - i), int(ed_tl[1] - j), ed_tl[2]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # bottom right
                    point = self.nearestPoint(surface, [int(ed_br[0] + i), int(ed_br[1] + j), ed_br[2]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # bottom left
                    point = self.nearestPoint(surface, [int(ed_bl[0] + i), int(ed_bl[1] - j), ed_bl[2]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                eg -= 1

            # Finally, fill out the remaining 4 squares
            for i in range(1, ln + 1):
                for j in range(1, ln + 1):
                    # top square
                    point = self.nearestPoint(surface, [int(ed_tl[0] - i), int(ed_tl[1] + j), ed_tl[2]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # left square
                    point = self.nearestPoint(surface, [int(ed_tl[0] + i), int(ed_tl[1] - j), ed_tl[2]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # right square
                    point = self.nearestPoint(surface, [int(ed_br[0] - i), int(ed_br[1] + j), ed_br[2]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # bottom square
                    point = self.nearestPoint(surface, [int(ed_br[0] + i), int(ed_br[1] - j), ed_br[2]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

        # in x-z plane (keep y constant)
        if startPoint[1] == 0 or startPoint[1] == surface.shape[1] - 1:
            # Separate conditions between if the length is odd or even
            # If the length is odd
            if ln % 2 == 1:
                # Initial square surrounding the center
                n = int(ln / 2 + 0.5)
                for i in range(n):
                    for j in range(n):
                        # 1st point
                        point = self.nearestPoint(surface, [int(cen[2] + (0.5 + i)), cen[1], int(cen[0] - (0.5 + j))])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 2nd point
                        point = self.nearestPoint(surface, [int(cen[2] + (0.5 + i)), cen[1], int(cen[0] + (0.5 + j))])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 3rd point
                        point = self.nearestPoint(surface, [int(cen[2] - (0.5 + i)), cen[1], int(cen[0] + (0.5 + j))])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 4th point
                        point = self.nearestPoint(surface, [int(cen[2] - (0.5 + i)), cen[1], int(cen[0] - (0.5 + j))])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False

            # If the length is even
            elif ln % 2 == 0:
                # Initial square surrounding the center
                n = int(ln / 2)
                for i in range(n + 1):
                    for j in range(n + 1):
                        # 1st point
                        point = self.nearestPoint(surface, [int(cen[2] + i), cen[1], int(cen[0] + j)])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 2nd point
                        point = self.nearestPoint(surface, [int(cen[2] + i), cen[1], int(cen[0] - j)])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 3rd point
                        point = self.nearestPoint(surface, [int(cen[2] - i), cen[1], int(cen[0] + j)])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 4th point
                        point = self.nearestPoint(surface, [int(cen[2] - i), cen[1], int(cen[0] - j)])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False

            # Index edges of the square
            # top right edge
            ed_tr = [int(cen[2] - ln / 2), cen[1], int(cen[0] + ln / 2)]
            # top left edge
            ed_tl = [int(cen[2] - ln / 2), cen[1], int(cen[0] - ln / 2)]
            # bottom right edge
            ed_br = [int(cen[2] + ln / 2), cen[1], int(cen[0] + ln / 2)]
            # bottom left edge
            ed_bl = [int(cen[2] + ln / 2), cen[1], int(cen[0] - ln / 2)]

            # Fill out the 4 triangles
            eg = ln + 1
            for i in range(0, ln + 1):
                for j in range(0, eg):
                    # top right
                    point = self.nearestPoint(surface, [int(ed_tr[0] - i), ed_tr[1], int(ed_tr[2] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # top left
                    point = self.nearestPoint(surface, [int(ed_tl[0] - i), ed_tl[1], int(ed_tl[2] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # bottom right
                    point = self.nearestPoint(surface, [int(ed_br[0] + i), ed_br[1], int(ed_br[2] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # bottom left
                    point = self.nearestPoint(surface, [int(ed_bl[0] + i), ed_bl[1], int(ed_bl[2] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                eg -= 1

            # Finally, fill out the remaining 4 squares
            for i in range(1, ln + 1):
                for j in range(1, ln + 1):
                    # top square
                    point = self.nearestPoint(surface, [int(ed_tl[0] - i), ed_tl[1], int(ed_tl[2] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # left square
                    point = self.nearestPoint(surface, [int(ed_tl[0] + i), ed_tl[1], int(ed_tl[2] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # right square
                    point = self.nearestPoint(surface, [int(ed_br[0] - i), ed_br[1], int(ed_br[2] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # bottom square
                    point = self.nearestPoint(surface, [int(ed_br[0] + i), ed_br[1], int(ed_br[2] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

        # in x-y plane (keep z constant)
        if startPoint[2] == 0 or startPoint[2] == surface.shape[0] - 1:
            # Separate conditions between if the length is odd or even
            # If the length is odd
            if ln % 2 == 1:
                # Initial square surrounding the center
                n = int(ln / 2 + 0.5)
                for i in range(n):
                    for j in range(n):
                        # 1st point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] + (0.5 + i)), int(cen[0] - (0.5 + j))])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 2nd point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] + (0.5 + i)), int(cen[0] + (0.5 + j))])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 3rd point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] - (0.5 + i)), int(cen[0] + (0.5 + j))])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 4th point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] - (0.5 + i)), int(cen[0] - (0.5 + j))])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False

            # If the length is even
            elif ln % 2 == 0:
                # Initial square surrounding the center
                n = int(ln / 2)
                for i in range(n + 1):
                    for j in range(n + 1):
                        # 1st point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] + i), int(cen[0] + j)])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 2nd point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] + i), int(cen[0] - j)])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 3rd point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] - i), int(cen[0] + j)])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 4th point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] - i), int(cen[0] - j)])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False

            # Index edges of the square
            # top right edge
            ed_tr = [cen[2], int(cen[1] - ln / 2), int(cen[0] + ln / 2)]
            # top left edge
            ed_tl = [cen[2], int(cen[1] - ln / 2), int(cen[0] - ln / 2)]
            # bottom right edge
            ed_br = [cen[2], int(cen[1] + ln / 2), int(cen[0] + ln / 2)]
            # bottom left edge
            ed_bl = [cen[2], int(cen[1] + ln / 2), int(cen[0] - ln / 2)]

            # Fill out the 4 triangles
            eg = ln + 1
            for i in range(0, ln + 1):
                for j in range(0, eg):
                    # top right
                    point = self.nearestPoint(surface, [ed_tr[0], int(ed_tr[1] - i), int(ed_tr[2] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # top left
                    point = self.nearestPoint(surface, [ed_tl[0], int(ed_tl[1] - i), int(ed_tl[2] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # bottom right
                    point = self.nearestPoint(surface, [ed_br[0], int(ed_br[1] + i), int(ed_br[2] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # bottom left
                    point = self.nearestPoint(surface, [ed_bl[0], int(ed_bl[1] + i), int(ed_bl[2] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                eg -= 1

            # Finally, fill out the remaining 4 squares
            for i in range(1, ln + 1):
                for j in range(1, ln + 1):
                    # top square
                    point = self.nearestPoint(surface, [ed_tl[0], int(ed_tl[1] - i), int(ed_tl[2] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # left square
                    point = self.nearestPoint(surface, [ed_tl[0], int(ed_tl[1] + i), int(ed_tl[2] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # right square
                    point = self.nearestPoint(surface, [ed_br[0], int(ed_br[1] - i), int(ed_br[2] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # bottom square
                    point = self.nearestPoint(surface, [ed_br[0], int(ed_br[1] + i), int(ed_br[2] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

        return True


    def _generateOctagon(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int, int],
                         charge: int) -> ndarray:
        """
        This function generate octagon shape for surface
        """
        # Rename variables and change startPoint from tuple to list
        ln = domainWidth
        cen = list(startPoint)
        # Find the center of the octagon
        # If the length is an odd number, the center of the octagon should be located between 4 points (ie center point should end as .5)
        # for x
        if cen[0] % 2 == 0 and ln % 2 == 1 and cen[0] != 0 and cen[0] != surface.shape[2] - 1:
            cen[0] = cen[0] - 0.5

        # for y
        if cen[1] % 2 == 0 and ln % 2 == 1 and cen[1] != 0 and cen[1] != surface.shape[1] - 1:
            cen[1] = cen[1] - 0.5

        # for z
        if cen[2] % 2 == 0 and ln % 2 == 1 and cen[2] != 0 and cen[2] != surface.shape[0] - 1:
            cen[2] = cen[2] - 0.5

        # in y-z plane (keep x constant)
        if startPoint[0] == 0 or startPoint[0] == surface.shape[2] - 1:
            # Separate conditions between if the length is odd or even
            # If the length is odd
            if ln % 2 == 1:
                # Initial square surrounding the center
                n = int(ln / 2 + 0.5)
                for i in range(n):
                    for j in range(n):
                        # 1st point
                        point = self.nearestPoint(surface, [int(cen[2] + (0.5 + i)), int(cen[1] - (0.5 + j)), cen[0]])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 2nd point
                        point = self.nearestPoint(surface, [int(cen[2] + (0.5 + i)), int(cen[1] + (0.5 + j)), cen[0]])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 3rd point
                        point = self.nearestPoint(surface, [int(cen[2] - (0.5 + i)), int(cen[1] + (0.5 + j)), cen[0]])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 4th point
                        point = self.nearestPoint(surface, [int(cen[2] - (0.5 + i)), int(cen[1] - (0.5 + j)), cen[0]])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge


            # If the length is even
            elif ln % 2 == 0:
                # Initial square surrounding the center
                n = int(ln / 2)
                for i in range(n + 1):
                    for j in range(n + 1):
                        # 1st points
                        point = self.nearestPoint(surface, [int(cen[2] + i), int(cen[1] + j), cen[0]])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 2nd points
                        point = self.nearestPoint(surface, [int(cen[2] + i), int(cen[1] - j), cen[0]])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 3rd points
                        point = self.nearestPoint(surface, [int(cen[2] - i), int(cen[1] + j), cen[0]])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 4th points
                        point = self.nearestPoint(surface, [int(cen[2] - i), int(cen[1] - j), cen[0]])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

            # Index edges of the square
            # top right edge
            ed_tr = [int(cen[2] - ln / 2), int(cen[1] + ln / 2), cen[0]]
            # top left edge
            ed_tl = [int(cen[2] - ln / 2), int(cen[1] - ln / 2), cen[0]]
            # bottom right edge
            ed_br = [int(cen[2] + ln / 2), int(cen[1] + ln / 2), cen[0]]
            # bottom left edge
            ed_bl = [int(cen[2] + ln / 2), int(cen[1] - ln / 2), cen[0]]

            # Fill out the 4 triangles
            # top right
            eg = ln + 1
            for i in range(0, ln + 1):
                for j in range(0, eg):
                    # top right
                    point = self.nearestPoint(surface, [int(ed_tr[0] - i), int(ed_tr[1] + j), ed_tr[2]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # top left
                    point = self.nearestPoint(surface, [int(ed_tl[0] - i), int(ed_tl[1] - j), ed_tl[2]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom right
                    point = self.nearestPoint(surface, [int(ed_br[0] + i), int(ed_br[1] + j), ed_br[2]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom left
                    point = self.nearestPoint(surface, [int(ed_bl[0] + i), int(ed_bl[1] - j), ed_bl[2]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                eg -= 1

            # Finally, fill out the remaining 4 squares
            for i in range(1, ln + 1):
                for j in range(1, ln + 1):
                    # top square
                    point = self.nearestPoint(surface, [int(ed_tl[0] - i), int(ed_tl[1] + j), ed_tl[2]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # left square
                    point = self.nearestPoint(surface, [int(ed_tl[0] + i), int(ed_tl[1] - j), ed_tl[2]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # right square
                    point = self.nearestPoint(surface, [int(ed_br[0] - i), int(ed_br[1] + j), ed_br[2]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom square
                    point = self.nearestPoint(surface, [int(ed_br[0] + i), int(ed_br[1] - j), ed_br[2]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

        # in x-z plane (keep y constant)
        if startPoint[1] == 0 or startPoint[1] == surface.shape[1] - 1:
            # Separate conditions between if the length is odd or even
            # If the length is odd
            if ln % 2 == 1:
                # Initial square surrounding the center
                n = int(ln / 2 + 0.5)
                for i in range(n):
                    for j in range(n):
                        # 1st point
                        point = self.nearestPoint(surface, [int(cen[2] + (0.5 + i)), cen[1], int(cen[0] - (0.5 + j))])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 2nd point
                        point = self.nearestPoint(surface, [int(cen[2] + (0.5 + i)), cen[1], int(cen[0] + (0.5 + j))])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 3rd point
                        point = self.nearestPoint(surface, [int(cen[2] - (0.5 + i)), cen[1], int(cen[0] + (0.5 + j))])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 4th point
                        point = self.nearestPoint(surface, [int(cen[2] - (0.5 + i)), cen[1], int(cen[0] - (0.5 + j))])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

            # If the length is even
            elif ln % 2 == 0:
                # Initial square surrounding the center
                n = int(ln / 2)
                for i in range(n + 1):
                    for j in range(n + 1):
                        # 1st point
                        point = self.nearestPoint(surface, [int(cen[2] + i), cen[1], int(cen[0] + j)])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 2nd point
                        point = self.nearestPoint(surface, [int(cen[2] + i), cen[1], int(cen[0] - j)])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 3rd point
                        point = self.nearestPoint(surface, [int(cen[2] - i), cen[1], int(cen[0] + j)])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 4th point
                        point = self.nearestPoint(surface, [int(cen[2] - i), cen[1], int(cen[0] - j)])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

            # Index edges of the square
            # top right edge
            ed_tr = [int(cen[2] - ln / 2), cen[1], int(cen[0] + ln / 2)]
            # top left edge
            ed_tl = [int(cen[2] - ln / 2), cen[1], int(cen[0] - ln / 2)]
            # bottom right edge
            ed_br = [int(cen[2] + ln / 2), cen[1], int(cen[0] + ln / 2)]
            # bottom left edge
            ed_bl = [int(cen[2] + ln / 2), cen[1], int(cen[0] - ln / 2)]

            # Fill out the 4 triangles
            eg = ln + 1
            for i in range(0, ln + 1):
                for j in range(0, eg):
                    # top right
                    point = self.nearestPoint(surface, [int(ed_tr[0] - i), ed_tr[1], int(ed_tr[2] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # top left
                    point = self.nearestPoint(surface, [int(ed_tl[0] - i), ed_tl[1], int(ed_tl[2] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom right
                    point = self.nearestPoint(surface, [int(ed_br[0] + i), ed_br[1], int(ed_br[2] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom left
                    point = self.nearestPoint(surface, [int(ed_bl[0] + i), ed_bl[1], int(ed_bl[2] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                eg -= 1

            # Finally, fill out the remaining 4 squares
            for i in range(1, ln + 1):
                for j in range(1, ln + 1):
                    # top square
                    point = self.nearestPoint(surface, [int(ed_tl[0] - i), ed_tl[1], int(ed_tl[2] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # left square
                    point = self.nearestPoint(surface, [int(ed_tl[0] + i), ed_tl[1], int(ed_tl[2] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # right square
                    point = self.nearestPoint(surface, [int(ed_br[0] - i), ed_br[1], int(ed_br[2] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom square
                    point = self.nearestPoint(surface, [int(ed_br[0] + i), ed_br[1], int(ed_br[2] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

        # in x-y plane (keep z constant)
        if startPoint[2] == 0 or startPoint[2] == surface.shape[0] - 1:
            # Separate conditions between if the length is odd or even
            # If the length is odd
            if ln % 2 == 1:
                # Initial square surrounding the center
                n = int(ln / 2 + 0.5)
                for i in range(n):
                    for j in range(n):
                        # 1st point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] + (0.5 + i)), int(cen[0] - (0.5 + j))])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 2nd point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] + (0.5 + i)), int(cen[0] + (0.5 + j))])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 3rd point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] - (0.5 + i)), int(cen[0] + (0.5 + j))])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 4th point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] - (0.5 + i)), int(cen[0] - (0.5 + j))])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

            # If the length is even
            elif ln % 2 == 0:
                # Initial square surrounding the center
                n = int(ln / 2)
                for i in range(n + 1):
                    for j in range(n + 1):
                        # 1st point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] + i), int(cen[0] + j)])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 2nd point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] + i), int(cen[0] - j)])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 3rd point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] - i), int(cen[0] + j)])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 4th point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] - i), int(cen[0] - j)])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

            # Index edges of the square
            # top right edge
            ed_tr = [cen[2], int(cen[1] - ln / 2), int(cen[0] + ln / 2)]
            # top left edge
            ed_tl = [cen[2], int(cen[1] - ln / 2), int(cen[0] - ln / 2)]
            # bottom right edge
            ed_br = [cen[2], int(cen[1] + ln / 2), int(cen[0] + ln / 2)]
            # bottom left edge
            ed_bl = [cen[2], int(cen[1] + ln / 2), int(cen[0] - ln / 2)]

            # Fill out the 4 triangles
            eg = ln + 1
            for i in range(0, ln + 1):
                for j in range(0, eg):
                    # top right
                    point = self.nearestPoint(surface, [ed_tr[0], int(ed_tr[1] - i), int(ed_tr[2] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # top left
                    point = self.nearestPoint(surface, [ed_tl[0], int(ed_tl[1] - i), int(ed_tl[2] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom right
                    point = self.nearestPoint(surface, [ed_br[0], int(ed_br[1] + i), int(ed_br[2] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom left
                    point = self.nearestPoint(surface, [ed_bl[0], int(ed_bl[1] + i), int(ed_bl[2] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                eg -= 1

            # Finally, fill out the remaining 4 squares
            for i in range(1, ln + 1):
                for j in range(1, ln + 1):
                    # top square
                    point = self.nearestPoint(surface, [ed_tl[0], int(ed_tl[1] - i), int(ed_tl[2] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # left square
                    point = self.nearestPoint(surface, [ed_tl[0], int(ed_tl[1] + i), int(ed_tl[2] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # right square
                    point = self.nearestPoint(surface, [ed_br[0], int(ed_br[1] - i), int(ed_br[2] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom square
                    point = self.nearestPoint(surface, [ed_br[0], int(ed_br[1] + i), int(ed_br[2] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

        return surface


    def _singleEmpty(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int, int],
                     possible_charge: List[int]) -> bool:
        """
        This function check the position want to generate single is empty
        """
        # locate the closest valid point
        point = self.nearestPoint(surface, [startPoint[2], startPoint[1], startPoint[0]])
        # if the point is on a domain charge, location is not empty and need to choose new starting point
        if surface[point[0], point[1], point[2]] in possible_charge:
            return False

        return True


    def _generateSingle(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int, int],
                        charge: int) -> ndarray:
        """
        This function generate single shape for surface
        """
        # locate the closest valid point
        point = self.nearestPoint(surface, [startPoint[2], startPoint[1], startPoint[0]])
        # generate charge on the domain
        surface[point[0], point[1], point[2]] = charge

        return surface