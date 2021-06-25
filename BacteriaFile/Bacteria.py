"""
This program is used for generate bacteria
"""
from abc import ABC
from typing import Tuple

import numpy as np
from numpy import ndarray


from SurfaceGenerator.Surface import Surface


class Bacteria(Surface, ABC):
    """
    This class represent a 2D bacteria
    """

    def __init__(self, trail: int, shape: str, size: Tuple[int, int], seed):
        Surface.__init__(self, trail, shape, size, seed)

class Bacteria2D(Bacteria):
    """
    This class represent a 2D bacteria
    """
    # Declare the type of all variable
    surfaceCharge: int
    height: int
    dimension: int

    def __init__(self, trail: int, shape: str, size: Tuple[int, int], surfaceCharge: int, seed: int):

        # set the surface charge
        # -1 for negative, 0 for neutral, 1 for positive
        self.surfaceCharge = surfaceCharge

        # set the proper height
        self.height = 3

        # set the proper dimension
        self.dimension = 2

        # call parent to generate bacteria
        Bacteria.__init__(self, trail, shape, size, seed)


    def _generateRec(self) -> ndarray:
        """
        This function generate the matrix space based on the size of the surface
        """
        # creating empty matrix space
        return np.zeros((self.width, self.length))


class Bacteria3D(Bacteria):
    # PAY ATTENTION: set dimension, set proper height, carefully generate the shape
    pass
