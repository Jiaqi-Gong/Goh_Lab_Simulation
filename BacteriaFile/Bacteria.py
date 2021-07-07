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
    def __init__(self, trail: int, shape: str, size: Tuple[int, int, int], seed: int, surfaceCharge: int, dimension: int):
        Surface.__init__(self, trail, shape, size, seed, surfaceCharge, dimension)


class Bacteria2D(Bacteria, ABC):
    """
    This class represent a 2D bacteria
    """
    # Declare the type of all variable

    def __init__(self, trail: int, shape: str, size: Tuple[int, int], surfaceCharge: int, seed: int):
        # set the proper height
        size = (size[0], size[1], 3)

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
        return np.zeros((1, self.width, self.length))


class Bacteria3D(Bacteria, ABC):
    # PAY ATTENTION: set dimension, set proper height, carefully generate the shape
    """
        This class represent a 3D bacteria
        """
    # Declare the type of all variable
    position: Union[None, Tuple[int, int, int]]

    def __init__(self, trail: int, shape: str, size: Tuple[int, int, int], surfaceCharge: int, seed: int,
                 position: Union[None, Tuple[int, int, int]] = None) -> None:
        # set the proper height of the bacteria's size
        # set the height of bacteria here or generate a height in the BacteriaManager

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
        else:
            raise RuntimeError("Bacteria 2D doesn't have this shape")

    def _generateRec(self) -> ndarray:
        """
        This function generate cubic shape of the matrix space based on the size of the surface
        Implement the super class abstract method
        """
        # creating empty matrix space
        return np.zeros(self.length, self.width, self.height)

    def _generateSphere(self):
        # finds center of array
        center = int(np.floor(self.length / 2)), int(np.floor(self.width / 2)), int(np.floor(self.height / 2))
        radius = min(np.floor(self.length / 2), np.floor(self.width / 2), np.floor(self.height / 2))
        # indexes the array
        index_z, index_y, index_x = np.indices((self.height+1, self.width+1, self.length+1))
        dist = ((index_x - center[0]) ** 2 + (index_y - center[1]) ** 2 + (index_z - center[2]) ** 2) ** 0.5
        return 1 * (dist <= radius) - 1 * (dist <= radius-1)

    def _generateCyl(self):
        center = int(np.floor(self.length / 2)), int(np.floor(self.width / 2)), int(np.floor(self.height / 2))
        # set semi-length
        r = min(np.floor(self.length / 2), np.floor(self.width / 2), np.floor(self.height / 2))
        l = max(self.length, self.width, self.height)
        sl = int(l * 0.5)
        index_x, index_y, index_z = np.indices((self.length, self.width, self.height))
        # calculates distance from center to any point on the x-axis
        d = np.floor(index_x - center[0])
        circle = ((index_y - center[1]) ** 2 + (index_z - center[2]) ** 2) ** 0.5
        # for odd length, a symmetric cylinder is generated. for even length, cylinder is longer on the right
        # define outer and inner cylinders
        outerone = np.ones(shape=(self.length, self.width, self.height)) * (circle <= r) * (abs(d) <= sl)
        innerone = np.ones(shape=(self.length, self.width, self.height)) * (circle <= r-1) * (abs(d) <= sl-1)
        outertwo = np.ones(shape=(self.length, self.width, self.height)) * (circle <= r) * (abs(d) <= sl) * (d != -sl)
        innertwo = np.ones(shape=(self.length, self.width, self.height)) * (circle <= r-1) * (abs(d) <= sl-1) * (d != 1-sl)
        odd = outerone - innerone
        even = outertwo - innertwo
        # surface value converter: 0 is surface, 2 is empty
        odd[odd == 0] = 2
        odd[odd == 1] = 0
        even[even == 0] = 2
        even[even == 1] = 0
        if l % 2 == 1:
            return odd
        else:
            return even

    def _generateRod(self):
        center = int(np.floor(self.length / 2)), int(np.floor(self.width / 2)), int(np.floor(self.height / 2))
        # set length, radius based on array size
        r = min(np.floor(self.length / 2), np.floor(self.width / 2), np.floor(self.height / 2))
        l = min(self.length, self.width, self.height) - 2*r - 1
        sl = int(l * 0.5)
        index_x, index_y, index_z = np.indices((self.length, self.width, self.height))
        d = index_x - center[0]
        rbound = center[0] + sl, center[1], center[2]
        lbound = rbound[0] - l + 1, center[1], center[2]
        distl = ((index_x - lbound[0]) ** 2 + (index_y - lbound[1]) ** 2 + (index_z - lbound[2]) ** 2) ** 0.5
        distr = ((index_x - rbound[0]) ** 2 + (index_y - rbound[1]) ** 2 + (index_z - rbound[2]) ** 2) ** 0.5
        circle = ((index_y - center[1]) ** 2 + (index_z - center[2]) ** 2) ** 0.5
        odd_outer = (np.ones(shape=(self.length, self.width, self.height)) * (abs(d) <= sl) * (circle <= r) + np.ones(
                shape=(self.length, self.width, self.height)) * (distl <= r) + np.ones(
                shape=(self.length, self.width, self.height)) * (distr <= r))
        odd_inner = (np.ones(shape=(self.length, self.width, self.height)) * (abs(d) <= sl-1) * (circle <= r-1) + np.ones(
                shape=(self.length, self.width, self.height)) * (distl <= r-1) + np.ones(
                shape=(self.length, self.width, self.height)) * (distr <= r-1))
        even_outer = (np.ones(shape=(self.length, self.width, self.height)) * (circle <= r) * (abs(d) <= sl) * (
                        d != -sl) + np.ones(shape=(self.length, self.width, self.height)) * (distl <= r) + np.ones(
                shape=(self.length, self.width, self.height)) * (distr <= r))
        even_inner = (np.ones(shape=(self.length, self.width, self.height)) * (circle <= r-1) * (abs(d) <= sl-1) * (
                        d != 1-sl) + np.ones(shape=(self.length, self.width, self.height)) * (distl <= r-1) + np.ones(
                shape=(self.length, self.width, self.height)) * (distr <= r-1))
        odd_outer[odd_outer >= 1] = 1
        odd_inner[odd_inner >= 1] = 1
        even_outer[even_outer >= 1] = 1
        even_inner[even_inner >= 1] = 1
        odd = odd_outer - odd_inner
        even = even_outer - even_inner
        odd[odd == 0] = 2
        odd[odd == 1] = 0
        even[even == 0] = 2
        even[even == 1] = 0

        if l % 2 == 1:
            return odd
        else:
            return even

    # to generate more shape, add new function below, start with def _generateXXX, replace XXX with the new shape you
    # want to generate, update your new shape in _generateSurface in Surface.py or inform Jiaqi to do update
