"""
This program is used for generate bacteria
"""
from abc import ABC

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
    # TODO:
    raise NotImplementedError
