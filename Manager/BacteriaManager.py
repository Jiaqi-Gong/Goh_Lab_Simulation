"""
This program is used to save and manage all bacteria
"""
from typing import Tuple

from BacteriaFile.Bacteria import Bacteria2D
from SurfaceGenerator.Domain import DomainGenerator
from ExternalIO import showMessage, writeLog


class BacteriaManager:
    """
    This class saves all bacteria used in this simulation and generate all corresponding film
    """

    # Declare the type of all variable
    trail: int
    dimension: int
    bacteriaSeed: int
    bacteriaSize: Tuple[int, int]
    bacteriaSurfaceShape: str
    bacteriaSurfaceCharge: int
    bacteriaDomainSize: Tuple[int, int]
    bacteriaDomainShape: str
    bacteriaDomainConcentration: float
    bacteriaNum: int
    bacteriaDomainGenerator: DomainGenerator
    bacteria: list

    def __init__(self, trail: int, dimension: int,
                 bacteriaSeed: int, bacteriaSize: Tuple[int, int], bacteriaSurfaceShape: str,
                 bacteriaSurfaceCharge: int,
                 bacteriaDomainSize: Tuple[int, int], bacteriaDomainShape: str, bacteriaDomainConcentration: float, bacteriaDomainChargeConcentration: float,
                 bacteriaNum: int):
        """
        Init the film manager, take in the
        """
        self.trail = trail
        self.dimension = dimension
        self.seed = bacteriaSeed

        # set bacteria variable
        self.bacteriaNum = bacteriaNum
        self.bacteriaSeed = bacteriaSeed
        self.bacteriaSize = bacteriaSize
        self.bacteriaSurfaceShape = bacteriaSurfaceShape
        self.bacteriaSurfaceCharge = bacteriaSurfaceCharge
        self.bacteriaDomainSize = bacteriaDomainSize
        self.bacteriaDomainShape = bacteriaDomainShape
        self.bacteriaDomainConcentration = bacteriaDomainConcentration
        self.bacteriaDomainChargeConcentration = bacteriaDomainChargeConcentration

        # generate domain generator
        self.bacteriaDomainGenerator = DomainGenerator(self.bacteriaSeed)

        # init a variable to store all bacteria
        self.bacteria = []

        # show message
        showMessage("Bacteria manager init done")
        writeLog(self.__dict__)

    def generateBacteria(self) -> None:
        """
        This function generate corresponding bacteria need based on the number wanted
        """
        if self.dimension == 2:
            for i in range(self.bacteriaNum):
                seed = self.bacteriaSeed + i

                # generate domain generator
                bacteriaDomainGenerator = DomainGenerator(seed)
                self._generate2DFilm(bacteriaDomainGenerator)

        elif self.dimension == 3:
            raise NotImplementedError

    def _generate2DFilm(self, domainGenerator: DomainGenerator) -> None:
        """
        Generate 2D film
        """
        showMessage("Generate 2D bacteria")
        # generate 2D Film Surface
        bacteria = Bacteria2D(self.trail, self.bacteriaSurfaceShape, self.bacteriaSize, self.bacteriaSurfaceCharge)

        showMessage("Generate 2D bacteria with domain")
        bacteria.surfaceWithDomain = domainGenerator.generateDomain(bacteria, self.bacteriaDomainShape,
                                                                    self.bacteriaDomainSize,
                                                                    self.bacteriaDomainConcentration,
                                                                    self.bacteriaDomainChargeConcentration)

        # save the film into manager
        self.bacteria.append(bacteria)

        # write into log
        showMessage("2D bacteria generate done")
        writeLog(self.bacteria)
