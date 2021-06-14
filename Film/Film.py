"""
This program is used to generate the film used for simulation
"""
from abc import ABC
from typing import Tuple

import numpy as np

from SurfaceGenerator.Domain import DomainGenerator
from SurfaceGenerator.Surface import Surface
from SurfaceGenerator.Surface import Z_AX_2D
from ExternalIO import showMessage, writeLog



class FilmSurface(Surface, ABC):
    """
    This is an abstract class of net neutral surface, subclass of Surface, should implement by 2D and 3D version
    """

    def __init__(self, trail: str, shape: str, size: Tuple[int, int], domainGenerator: DomainGenerator,
                 domainShape: str, domainSize: Tuple[int, int], domainConcentration: float):
        Surface.__init__(self, trail, shape, size, domainGenerator, domainShape, domainSize, domainConcentration)


class FilmSurface2D(FilmSurface, ABC):
    """
    This is a 2D net neutral surface, subclass of surface
    """

    def __init__(self, trail: str, shape: str, size: Tuple[int, int], surfaceCharge: int, domainGenerator: DomainGenerator,
                 domainShape: str, domainSize: Tuple[int, int], domainConcentration: float):

        showMessage("start to generate Film surface 2D")

        # set the surface charge
        # -1 for negative, 0 for neutral, 1 for positive
        self.charge = surfaceCharge

        # set the proper dimension and height
        self.dimension = 2

        # set the proper height
        self.height = 0

        # call parent
        FilmSurface.__init__(self, trail, shape, size, domainGenerator, domainShape, domainSize,
                             domainConcentration)

        showMessage("Generate Film surface 2D done")
        writeLog(self.__dict__)

    def _generateRec(self):
        """
        This function generate the matrix space based on the size of the surface
        """
        # creating empty matrix space
        return np.zeros((self.width, self.length))


class FilmSurface3D(FilmSurface, ABC):
    # PAY ATTENTION: set dimension, set proper height, carefully generate the shape
    pass