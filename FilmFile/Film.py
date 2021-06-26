"""
This program is used to generate the film used for simulation
"""
from abc import ABC
from typing import Tuple

import numpy as np
from numpy import ndarray

from SurfaceGenerator.Surface import Surface
from SurfaceGenerator.Surface import Z_AX_2D
from ExternalIO import showMessage, writeLog


class Film(Surface, ABC):
    """
    This is an abstract class of net neutral surface, subclass of Surface, should implement by 2D and 3D version
    """

    def __init__(self, trail: int, shape: str, size: Tuple[int, int], surfaceCharge: int,  seed: int):
        Surface.__init__(self, trail, shape, size, seed, surfaceCharge)


class FilmSurface2D(Film, ABC):
    """
    This is a 2D net neutral surface, subclass of surface
    """
    # Declare the type of all variable
    dimension: int
    height: int

    def __init__(self, trail: int, shape: str, size: Tuple[int, int], surfaceCharge: int, seed: int) -> None:
        showMessage("start to generate Film surface 2D")

        # set the proper dimension and height
        self.dimension = 2

        # set the proper height
        self.height = 0

        # call parent
        Film.__init__(self, trail, shape, size, surfaceCharge, seed)

        showMessage("Generate Film surface 2D done")
        writeLog(self.__dict__)

    def _generateRec(self) -> ndarray:
        """
        This function generate the matrix space based on the size of the surface
        Implement the super class abstract method
        """
        # creating empty matrix space
        return np.zeros((self.width, self.length))


class FilmSurface3D(Film, ABC):
    # PAY ATTENTION: set dimension, set proper height, carefully generate the shape
    """
       This is a 3D net neutral surface, subclass of surface
    """
    # Declare the type of all variable
    dimension: int
    height: int

    def __init__(self, trail: int, shape: str, size: Tuple[int, int], surfaceCharge: int, seed: int) -> None:
        showMessage("start to generate Film surface 2D")

        # set the proper dimension and height
        self.dimension = 3

        # set the proper height
        self.height = 3

        # call parent
        Film.__init__(self, trail, shape, size, surfaceCharge, seed)

        showMessage("Generate Film surface 3D done")
        writeLog(self.__dict__)

    def _generateRec(self) -> ndarray:
        """
        This function generate the matrix space based on the size of the surface
        Implement the super class abstract method
        """
        # creating empty matrix space
        # TODO:
        raise NotImplementedError
