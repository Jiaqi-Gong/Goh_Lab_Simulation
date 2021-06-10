"""
This program is used for generate bacteria
"""
from abc import ABC

import numpy as np

from SurfaceGenerator.Domain import DomainGenerator
from SurfaceGenerator.Surface import Surface


class Bacteria(Surface, ABC):
    """
    This class represent a 2D bacteria
    """

    def __init__(self, trail: int, shape: str, size: str, domainGenerator: DomainGenerator,
                 domainShape: str, domainSize: str, domainConcentration: float):
        Surface.__init__(self, trail, shape, size, domainGenerator, domainShape, domainSize, domainConcentration)

        # do we have this?
        self.totalCharge = 0

class Bacteria2D(Bacteria):
    """
    This class represent a 2D bacteria
    """

    def __init__(self, trail: int, shape: str, size: str, domainGenerator: DomainGenerator,
                 domainShape: str, domainSize: str, domainConcentration: float):
        Bacteria.__init__(self, trail, shape, size, domainGenerator, domainShape, domainSize, domainConcentration)

        # set the proper height
        self.height = 3

        # set the proper dimension
        self.dimension = 2

    def _generateRec(self):
        """
        This function generate the matrix space based on the size of the surface
        """
        # creating empty matrix space
        return np.zeros((self.width, self.length))


class Bacteria3D(Bacteria):
    # PAY ATTENTION: set dimension, set proper height, carefully generate the shape
    pass
