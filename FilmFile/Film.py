"""
This program is used to generate the film used for simulation
"""
import abc
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
    @abc.abstractmethod
    def __init__(self, trail: int, shape: str, size: Tuple[int, int, int], surfaceCharge: int,  seed: int, dimension: int):
        Surface.__init__(self, trail, shape, size, seed, surfaceCharge, dimension)


class FilmSurface2D(Film, ABC):
    """
    This is a 2D net neutral surface, subclass of surface
    """
    # Declare the type of all variable
    height: int

    def __init__(self, trail: int, shape: str, size: Tuple[int, int], surfaceCharge: int, seed: int) -> None:
        showMessage("start to generate Film surface 2D")

        # set the proper dimension and height
        dimension = 2

        # set the proper height
        size = (size[0], size[1], 0)

        # call parent
        Film.__init__(self, trail, shape, size, surfaceCharge, seed, dimension)

        showMessage("Generate Film surface 2D done")
        # writeLog(self.__dict__)

    def _generateSurface(self) -> ndarray:
        """
        Generate the corresponding surface, override in subclass
        """
        print("Start to generating surface with shape: ", self.shape)

        # generate corresponding shape
        if self.shape.upper() == "RECTANGLE":
            return self._generateRec()
        else:
            raise RuntimeError("Film 2D doesn't have this shape")

    def _generateRec(self) -> ndarray:
        """
        This function generate the matrix space based on the size of the surface
        Implement the super class abstract method
        """
        # creating empty matrix space
        return np.zeros((1, self.width, self.length))


class FilmSurface3D(Film, ABC):
    # PAY ATTENTION: set dimension, set proper height, carefully generate the shape
    """
       This is a 3D net neutral surface, subclass of surface
    """
    # Declare the type of all variable
    height: int

    def __init__(self, trail: int, shape: str, size: Tuple[int, int, int], surfaceCharge: int, seed: int) -> None:
        showMessage("start to generate Film surface 3D")

        # set the proper dimension and height
        dimension = 3

        # set the size of film
        size = (size[0], size[1], size[2])

        # call parent
        Film.__init__(self, trail, shape, size, surfaceCharge, seed, dimension)

        showMessage("Generate Film surface 3D done")
        # writeLog(self.__dict__)

    def _generateSurface(self) -> ndarray:
        """
        Generate the corresponding surface, override in subclass
        """
        print("Start to generating surface with shape: ", self.shape)

        # generate corresponding shape
        if self.shape.upper() == "RECTANGLE":
            return self._generateRec()
        else:
            raise RuntimeError("Film 3D doesn't have this shape")

    def _generateRec(self) -> ndarray:
        """
        This function generate the matrix space based on the size of the surface
        Implement the super class abstract method
        """
        # creating empty matrix space
        return np.zeros((self.height, self.width, self.length))
