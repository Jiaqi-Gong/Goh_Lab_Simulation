"""
This program is used for generate bacteria
"""
import abc
from abc import ABC
from typing import Tuple, Union

import numpy as np
from numpy import ndarray

from SurfaceGenerator.Surface import Surface


class Bacteria(Surface, ABC):
    """
    This class represent a 2D bacteria
    """

    @abc.abstractmethod
    def __init__(self, trail: int, shape: str, size: Tuple[int, int], seed: int, surfaceCharge: int, dimension: int):
        Surface.__init__(self, trail, shape, size, seed, surfaceCharge, dimension)


class Bacteria2D(Bacteria, ABC):
    """
    This class represent a 2D bacteria
    """
    # Declare the type of all variable
    height: int

    def __init__(self, trail: int, shape: str, size: Tuple[int, int], surfaceCharge: int, seed: int):
        # set the proper height
        self.height = 3

        # set the proper dimension
        dimension = 2

        # call parent to generate bacteria
        Bacteria.__init__(self, trail, shape, size, seed, surfaceCharge, dimension)

    def _generateSurface(self) -> ndarray:
        """
        Generate the corresponding surface, override in subclass
        """
        print("Start to generating surface with shape: ", self.shape)

        # generate corresponding shape
        if self.shape.upper() == "RECTANGLE" or self.shape.upper() == "CUBOID":
            return self._generateRec()
        else:
            raise RuntimeError("Bacteria 2D doesn't have this shape")

    def _generateRec(self) -> ndarray:
        """
        This function generate the matrix space based on the size of the surface
        Implement the super class abstract method
        """
        # creating empty matrix space
        return np.zeros((self.width, self.length))


class Bacteria3D(Bacteria, ABC):
    # PAY ATTENTION: set dimension, set proper height, carefully generate the shape
    """
        This class represent a 3D bacteria
        """
    # Declare the type of all variable
    height: int
    position: Union[None, Tuple[int, int, int]]

    def __init__(self, trail: int, shape: str, size: Tuple[int, int], surfaceCharge: int, seed: int,
                 position: Union[None, Tuple[int, int, int]] = None) -> None:
        # set the proper height of the bacteria
        # set the height of bacteria here or generate a height in the BacteriaManager, consider it and
        # talk with Rei
        # TODO:
        self.height = self.length

        # set the proper dimension
        dimension = 3

        # set position
        # can be none if use this bacteria for energy scan simulation
        self.position = position

        # call parent to generate bacteria
        Bacteria.__init__(self, trail, shape, size, seed, surfaceCharge, dimension)

    def _generateSurface(self) -> ndarray:
        """
        Generate the corresponding surface, override in subclass
        """
        print("Start to generating surface with shape: ", self.shape)

        # generate corresponding shape
        if self.shape.upper() == "CUBOID":
            return self._generateRec()
        elif self.shape.upper() == "SPHERE":
            return self._generateSphere()
        elif self.shape.upper() == "CYLINDER":
            return self._generateCyl()
        elif self.shape.upper() == "ROD":
            return self._generateRod()

    def _generateRec(self) -> ndarray:
        """
        This function generate cubic shape of the matrix space based on the size of the surface
        Implement the super class abstract method
        """
        # creating empty matrix space
        return np.zeros(self.length, self.width, self.height)

    def _generateSphere(self, radius):
        # finds center of array
        center = int(np.floor(self.length / 2)), int(np.floor(self.width / 2)), int(np.floor(self.height / 2))
        # indexes the array
        index_x, index_y, index_z = np.indices((self.length, self.width, self.height))
        dist = ((index_x - center[0]) ** 2 + (index_y - center[1]) ** 2 + (index_z - center[2]) ** 2) ** 0.5
        return 1 * (dist <= radius)

    def _generateCyl(self, r, l):
        center = int(np.floor(self.length / 2)), int(np.floor(self.width / 2)), int(np.floor(self.height / 2))
        # set semi-length
        sl = int(l * 0.5)
        index_x, index_y, index_z = np.indices((self.length, self.width, self.height))
        # calculates distance from center to any point on the x-axis
        d = np.floor(index_x - center[0])
        circle = ((index_y - center[1]) ** 2 + (index_z - center[2]) ** 2) ** 0.5
        # for odd length, a symmetric cylinder is generated. for even length, cylinder is longer on the right
        if l % 2 == 1:
            return np.ones(shape=(self.length, self.width, self.height)) * (circle <= r) * (abs(d) <= sl)
        else:
            return np.ones(shape=(self.length, self.width, self.height)) * (circle <= r) * (abs(d) <= sl) * (d != -sl)

    # unfinished below

    def _generateRod(self, r, l):
        center = int(np.floor(self.length / 2)), int(np.floor(self.width / 2)), int(np.floor(self.height / 2))
        # set semi-length
        sl = int(l * 0.5)
        index_x, index_y, index_z = np.indices((self.length, self.width, self.height))
        d = index_x - center[0]
        rbound = center[0] + sl, center[1], center[2]
        lbound = rbound[0] - l + 1, center[1], center[2]
        distl = ((index_x - lbound[0]) ** 2 + (index_y - lbound[1]) ** 2 + (index_z - lbound[2]) ** 2) ** 0.5
        distr = ((index_x - rbound[0]) ** 2 + (index_y - rbound[1]) ** 2 + (index_z - rbound[2]) ** 2) ** 0.5
        circle = ((index_y - center[1]) ** 2 + (index_z - center[2]) ** 2) ** 0.5
        if l % 2 == 1:
            return (np.ones(shape=(self.length, self.width, self.height)) * (abs(d) <= sl) * (circle <= r) + np.ones(
                shape=(self.length, self.width, self.height)) * (distl <= r) + np.ones(
                shape=(self.length, self.width, self.height)) * (distr <= r))
        else:
            return (np.ones(shape=(self.length, self.width, self.height)) * (circle <= r) * (abs(d) <= sl) * (
                        d != -sl) + np.ones(shape=(self.length, self.width, self.height)) * (distl <= r) + np.ones(
                shape=(self.length, self.width, self.height)) * (distr <= r))

    # to generate more shape, add new function below, start with def _generateXXX, replace XXX with the new shape you
    # want to generate, update your new shape in _generateSurface in Surface.py or inform Jiaqi to do update
