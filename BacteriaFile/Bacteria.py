"""
This program:
- Sets the bacteria's dimension (2D or 3D)
- Generates the bacteria's surface & shape
"""
import abc
from abc import ABC
from typing import Tuple, Union
from ExternalIO import showMessage, writeLog
import numpy as np
from numpy import ndarray
from SurfaceGenerator.Surface import Surface


class Bacteria(Surface, ABC):
    """
    This initializes and defines the Bacteria class
    """

    @abc.abstractmethod
    def __init__(self, trail: int, shape: str, size: Tuple[int, int, int], seed: int, surfaceCharge: int, dimension: int):
        Surface.__init__(self, trail, shape, size, seed, surfaceCharge, dimension)


class Bacteria2D(Bacteria, ABC):
    """
    This class represents a 2D bacteria
    """
    # Declares the type of all variables

    def __init__(self, trail: int, shape: str, size: Tuple[int, int], surfaceCharge: int, seed: int):
        # Sets the proper height
        size = (size[0], size[1], 3)

        # Sets the proper dimension
        dimension = 2

        # Calls parent to generate the bacteria
        Bacteria.__init__(self, trail, shape, size, seed, surfaceCharge, dimension)

    def _generateSurface(self) -> ndarray:
        """
        Generate the corresponding surface, override in subclass
        """
        writeLog("Generating surface with shape: ".format(self.shape))

        # Generates corresponding shape
        if self.shape.upper() == "RECTANGLE":
            return self._generateRec()
        else:
            raise RuntimeError("2D Bacteria can not have this shape: {}.".format(self.shape))

    def _generateRec(self) -> ndarray:
        """
        Generates the matrix space based on the size of the surface
        """
        # Creates empty matrix space
        return np.zeros((1, self.width, self.length))


class Bacteria3D(Bacteria, ABC):
    # IMPORTANT: Set dimension, set proper height, carefully generate the shape
    """
    This class represents a 3D bacteria
    """
    # Declares the type of all variable
    position: Union[None, Tuple[int, int, int]]

    def __init__(self, trail: int, shape: str, size: Tuple[int, int, int], surfaceCharge: int, seed: int,
                 position: Union[None, Tuple[int, int, int]] = None) -> None:
        # Sets the height of bacteria here, or generates a height in the BacteriaManager

        # Sets the proper dimension
        dimension = 3

        # Sets position; Position can be null for the EnergyScan.py simulation.
        self.position = position

        # Calls parent to generate bacteria
        Bacteria.__init__(self, trail, shape, size, seed, surfaceCharge, dimension)

    def _generateSurface(self) -> ndarray:
        """
        Generate the corresponding surface, override in subclass
        """
        writeLog("Generating surface with shape: ".format(self.shape))

        # Generates corresponding shape
        if self.shape.upper() == "CUBOID":
            return self._generateRec()
        elif self.shape.upper() == "SPHERE":
            return self._generateSphere()
        elif self.shape.upper() == "CYLINDER":
            return self._generateCyl()
        elif self.shape.upper() == "ROD":
            return self._generateRod()
        else:
            raise RuntimeError("3D Bacteria can not have this shape: {}.".format(self.shape))

    def _generateRec(self) -> ndarray:
        """
        Generates a cubic matrix space, based on the size of the surface
        """
        # Creates empty matrix space
        surface = np.full((self.height, self.width, self.length),2)
        # Fills outside of surface with zeros
        surface[:,:,self.length-1] = 0
        surface[:,:,0] = 0
        surface[:,self.width-1,:] = 0
        surface[:,0,:] = 0
        surface[self.height-1,:,:] = 0
        surface[0,:,:] = 0

        return surface


    def _generateSphere(self) -> ndarray:
        """
        Generates a hollow spherical matrix space, based on the size of the surface
        """
        # Finds center of array
        center = int(np.floor(self.length / 2)), int(np.floor(self.width / 2)), int(np.floor(self.height / 2))
        radius = min(np.floor(self.length / 2), np.floor(self.width / 2), np.floor(self.height / 2))
        # Indexes the array
        index_z, index_y, index_x = np.indices((self.height, self.width, self.length))
        dist = ((index_x - center[0]) ** 2 + (index_y - center[1]) ** 2 + (index_z - center[2]) ** 2) ** 0.5
        # Defines solid spheres of different radii
        reg1 = 1 * (dist <= radius)
        reg2 = 1 * (dist <= radius - 1)
        # A hollow sphere is generated by subtracting reg2 from reg1
        sph = 2 * reg1 - reg2
        # Sets surface = 0, empty space = 2
        sph[sph <= 1] = 0
        sph[sph >= 2] = 1
        sph[sph == 0] = 2
        sph[sph == 1] = 0
        return sph

    def _generateCyl(self) -> ndarray:
        """
        Generates a cylindrical matrix space, based on the size of the surface
        """
        center = int(np.floor(self.length / 2)), int(np.floor(self.width / 2)), int(np.floor(self.height / 2))
        # Sets radius, length, semi-length based on array size
        r = min(np.floor(self.length / 2), np.floor(self.width / 2), np.floor(self.height / 2)) - 1
        l = min(self.length, self.width, self.height) + 1
        sl = int(l * 0.5)
        index_x, index_y, index_z = np.indices((self.length, self.width, self.height))
        # Calculates distance from center to any point on the x-axis
        d = np.floor(index_x - center[0])
        circle = ((index_y - center[1]) ** 2 + (index_z - center[2]) ** 2) ** 0.5
        # For odd length, a symmetric cylinder is generated.
        # For even length, the cylinder is longer on the right.
        # Defines outer and inner cylinders
        outerone = np.ones(shape=(self.length, self.width, self.height)) * (circle <= r) * (abs(d) <= sl)
        innerone = np.ones(shape=(self.length, self.width, self.height)) * (circle <= r-1) * (abs(d) <= sl-1)
        outertwo = np.ones(shape=(self.length, self.width, self.height)) * (circle <= r) * (abs(d) <= sl-1) * (d != 1-sl)
        innertwo = np.ones(shape=(self.length, self.width, self.height)) * (circle <= r-1) * (abs(d) <= sl-2) * (d != 2-sl)
        odd = outerone - innerone
        even = outertwo - innertwo
        # sets surface = 0, empty space = 2
        odd[odd == 0] = 2
        odd[odd == 1] = 0
        even[even == 0] = 2
        even[even == 1] = 0
        if l % 2 == 1:
            return odd
        else:
            return even

    def _generateRod(self) -> ndarray:
        """
        Generates a rod-shaped matrix space, based on the size of the surface
        """
        rod_dim = min(self.length, self.width, self.height)
        center_odd = int(np.floor(self.length / 2)), int(np.floor(self.width / 2)), int(np.floor(self.height / 2))
        center_even = int(np.floor(self.length / 2) - 1), int(np.floor(self.width / 2)), int(np.floor(self.height / 2))
        # Sets length & radius based on array size
        # Length is fixed as 3x the radius, so the array must be at least 5x3x3
        r = rod_dim / 5
        l = int(3 * r) + 2
        sl = int(l * 0.5)
        index_x, index_y, index_z = np.indices((self.length, self.width, self.height))
        if rod_dim % 2 == 1:
            center = center_odd
        else:
            center = center_even
        d = index_x - center[0]
        rbound = center[0] + sl, center[1], center[2]
        lbound = rbound[0] - l + 1, center[1], center[2]
        distl = ((index_x - lbound[0]) ** 2 + (index_y - lbound[1]) ** 2 + (index_z - lbound[2]) ** 2) ** 0.5
        distr = ((index_x - rbound[0]) ** 2 + (index_y - rbound[1]) ** 2 + (index_z - rbound[2]) ** 2) ** 0.5
        circle = ((index_y - center[1]) ** 2 + (index_z - center[2]) ** 2) ** 0.5
        odd_outer = (np.ones(shape=(self.length, self.width, self.height)) * (abs(d) <= sl) * (circle <= r) + np.ones(
            shape=(self.length, self.width, self.height)) * (distl <= r) + np.ones(
            shape=(self.length, self.width, self.height)) * (distr <= r))
        odd_inner = (np.ones(shape=(self.length, self.width, self.height)) * (abs(d) <= sl) * (
                    circle <= r - 1) + np.ones(
            shape=(self.length, self.width, self.height)) * (distl <= r - 1) + np.ones(
            shape=(self.length, self.width, self.height)) * (distr <= r - 1))
        even_outer = (np.ones(shape=(self.length, self.width, self.height)) * (circle <= r) * (abs(d) <= sl) * (
                d != -sl) + np.ones(shape=(self.length, self.width, self.height)) * (distl <= r) + np.ones(
            shape=(self.length, self.width, self.height)) * (distr <= r))
        even_inner = (np.ones(shape=(self.length, self.width, self.height)) * (circle <= r - 1) * (abs(d) <= sl - 1) * (
                d != 1 - sl) + np.ones(shape=(self.length, self.width, self.height)) * (distl <= r - 1) + np.ones(
            shape=(self.length, self.width, self.height)) * (distr <= r - 1))
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

        if rod_dim % 2 == 1:
            return odd
        else:
            return even

"""
To include additional shape generations:
    1. Create a new function below, following the naming convention above.
        ex., _generateX, where X is the new shape.
    2. Add your shape option to _generateSurface above, under either 2DBacteria or 3DBacteria.
"""