"""
This program is generating the domain with some charge on it
Can be used for 2D, 3D and for testing surface, bacteria surface
"""
from numpy import ndarray

from Surface import *
from Surface import Surface


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

    def generateDomain(self, surface: Surface, shape: str, size: str, concentration: float, k: int):
        """
        This function takes in a surface, shape and size of domain want to generate on the surface
        :param surface: the surface want to generate the domain
        :param shape: shape of the domain
        :param size: size of the surface, in the format ###x###, in unit micrometer, 1micrometer = 100 points, NOTICE: size of domain must smaller than surface
        :param concentration: concentration of the charge?
        :param k:
        :return: return the surface with wanted domain on it
        """

        # get size
        size = size.split("x")
        domainWidth = int(size[0]) * 100
        domainLength = int(size[1]) * 100

        # calculate how many domain should generate
        domainNum = int((surface.width * surface.length * concentration) / (domainWidth * domainLength))

        # grad_tot number of points per gradient strip
        grad_tot = surface.width * surface.length

        # first, make entire surface positive
        surf_1d = np.ones(grad_tot)

        # init generated domain number
        generated = 0

        # set seed for random
        np.random.seed(self.seed)

        # start to generate the domain on surface
        while generated < domainNum:
            # pick a point as the start of the diamond shape, which point is the toppest point of the diamond shape
            start = np.random.randint(surface.length * 7, grad_tot - (surface.length * 10) - 2)

            # generate the corresponding domain shape
            if shape.upper() == "DIAMOND":
                # diamond should have same width and length

                # check the position of diamond is empty, if not empty, then continue
                if not self._diamondEmpty(surf_1d, domainWidth, start):
                    continue

                # generate diamond domain
                surface = self._generateDiamond(surf_1d, domainWidth, start)

        # more shape coming soon, leave for more extension

        # return the surface generated based on k value
        if k == 0:
            return surface
        else:
            return

    def _diamondEmpty(self, surface: ndarray, domainWidth: int, startPoint: int):
        """
        This function check the position want to generate diamond whether is empty
        This function is adjusted based on:
        https://www.studymite.com/python/examples/program-to-print-diamond-pattern-in-python/
        :return True if all empty, False for no
        """
        # set the new name
        n = domainWidth
        start = surface[startPoint]

        # make upper diamond
        for i in range(0, n + 1):
            for j in range(-i, i + 1):
                if surface[start[0] + i][start[1] + j] != 1:
                    return False

        # make the middle line
        for j in range(-n - 1, n + 2):
            if surface[start[0] + n + 1][start[1] + j] != 1:
                return False

        # make lower diamond
        for i in range(n, 2 * n + 1):
            for j in range(-i + n, i - n + 1):
                if surface[start[0] - i + 1][start[1] - j] != 1:
                    return False

        return True

    def _generateDiamond(self, surface: ndarray, domainWidth: int, startPoint: int):
        """
        This function generate diamond shape domain
        This function is adjusted based on:
        https://www.studymite.com/python/examples/program-to-print-diamond-pattern-in-python/
        :return return the surface with diamond domain on it
        """
        # set the new name
        n = domainWidth
        start = surface[startPoint]

        # make upper diamond
        for i in range(0, n + 1):
            for j in range(-i, i + 1):
                surface[start[0] + i][start[1] + j] = 1

        # make the middle line
        for j in range(-n - 1, n + 2):
            surface[start[0] + n + 1][start[1] + j] = 1

        # make lower diamond
        for i in range(n, 2 * n + 1):
            for j in range(-i + n, i - n + 1):
                surface[start[0] - i + 1][start[1] - j] = 1

        # return the generated surface
        return surface
