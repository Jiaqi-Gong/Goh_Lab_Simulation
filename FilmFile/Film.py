"""
This program:
- Generates the bacteria's film (2D or 3D)
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
    This is an abstract class of net neutral surface; subclass of Surface
    Should implement a 2D and 3D version
    """
    @abc.abstractmethod
    def __init__(self, trail: int, shape: str, size: Tuple[int, int, int], surfaceCharge: int,  seed: int, dimension: int):
        Surface.__init__(self, trail, shape, size, seed, surfaceCharge, dimension)


class FilmSurface2D(Film, ABC):
    """
    This is a 2D net neutral surface; subclass of surface
    """
    # Declares the type of all variables
    height: int

    def __init__(self, trail: int, shape: str, size: Tuple[int, int], surfaceCharge: int, seed: int) -> None:
        showMessage("Generating 2D Film surface...")

        # Sets the dimension to 2D
        dimension = 2

        # Sets the film size
        size = (size[0], size[1], 0)

        # Calls parent
        Film.__init__(self, trail, shape, size, surfaceCharge, seed, dimension)

        showMessage("2D Film surface: Complete.")
        # writeLog(self.__dict__)

    def _generateSurface(self) -> ndarray:
        """
        Generates the corresponding surface; override in subclass
        """
        print("Beginning surface generation with shape: ", self.shape)

        # Generates corresponding shape
        if self.shape.upper() == "RECTANGLE":
            return self._generateRec()
        else:
            raise RuntimeError("This is not a valid shape for a 2D Film.")

    def _generateRec(self) -> ndarray:
        """
        This function generates the matrix space based on the size of the surface
        Implements the super class abstract method
        """
        # Creates empty matrix space
        return np.zeros((1, self.width, self.length))


class FilmSurface3D(Film, ABC):
    # PAY ATTENTION: set dimension, set proper height, carefully generate the shape
    """
       This is a 3D net neutral surface; subclass of surface
    """
    # Declares the type of all variables
    height: int

    def __init__(self, trail: int, shape: str, size: Tuple[int, int, int], surfaceCharge: int, seed: int) -> None:
        showMessage("Generating 3D Film surface...")

        # Sets the dimension to 3D
        dimension = 3

        # Sets the film size
        size = (size[0], size[1], size[2])

        # Calls parent
        Film.__init__(self, trail, shape, size, surfaceCharge, seed, dimension)

        showMessage("3D Film surface: Complete.")
        # writeLog(self.__dict__)

    def _generateSurface(self) -> ndarray:
        """
        Generates the corresponding surface; override in subclass
        """
        print("Beginning surface generation with shape: ", self.shape)

        # Generate corresponding shape
        if self.shape.upper() == "RECTANGLE":
            return self._generateRec()
        else:
            raise RuntimeError("This is not a valid shape for a 3D Film.")

    def _generateRec(self) -> ndarray:
        """
        This function generates the matrix space based on the size of the surface
        Implements the super class abstract method
        """
        # Creates empty matrix space
        return np.zeros((self.height, self.width, self.length))
