"""
This program is used to save and manage all bacteria
"""
from typing import Tuple, Union

from BacteriaFile.Bacteria import Bacteria2D, Bacteria3D
from BacteriaFile.BacteriaMovement import BacteriaMovementGenerator
from SurfaceGenerator.Domain import DomainGenerator
from ExternalIO import showMessage, writeLog


class BacteriaManager:
    """
    This class saves all bacteria used in this simulation and generate all corresponding film
    """

    # Declare the type of all variable
    trail: int
    dimension: int
    simulatorType: int
    bacteriaSeed: int
    bacteriaSize: Union[Tuple[int, int], Tuple[int, int, int]]
    bacteriaSurfaceShape: str
    bacteriaSurfaceCharge: int
    bacteriaDomainSize: Tuple[int, int]
    bacteriaDomainShape: str
    bacteriaDomainConcentration: float
    bacteriaNum: int
    bacteriaDomainGenerator: DomainGenerator
    bacteriaMovementGenerator: BacteriaMovementGenerator
    bacteria: list

    def __init__(self, trail: int, dimension: int, simulatorType: int,
                 bacteriaSeed: int, bacteriaSize: Tuple[int, int, int], bacteriaSurfaceShape: str,
                 bacteriaSurfaceCharge: int,
                 bacteriaDomainSize: Tuple[int, int], bacteriaDomainShape: str, bacteriaDomainConcentration: float,
                 bacteriaDomainChargeConcentration: float, bacteriaNum: int):
        """
        Init the film manager, take in the
        """
        self.trail = trail
        self.dimension = dimension
        self.simulatorType = simulatorType

        # set bacteria variable
        self.bacteriaNum = bacteriaNum
        self.bacteriaSeed = bacteriaSeed
        self.bacteriaSurfaceShape = bacteriaSurfaceShape
        self.bacteriaSurfaceCharge = bacteriaSurfaceCharge
        self.bacteriaDomainSize = bacteriaDomainSize
        self.bacteriaDomainShape = bacteriaDomainShape
        self.bacteriaDomainConcentration = bacteriaDomainConcentration
        self.bacteriaDomainChargeConcentration = bacteriaDomainChargeConcentration

        # depends on the dimension, set bacteria size
        if dimension == 2:
            self.bacteriaSize = bacteriaSize[:2]
        else:
            self.bacteriaSize = bacteriaSize

        # generate domain generator
        self.bacteriaDomainGenerator = DomainGenerator(self.bacteriaSeed)

        # if this is dynamic simulator, generate bacteria movement generator
        if self.simulatorType == 2:
            self.bacteriaMovementGenerator = BacteriaMovementGenerator()

        # init a variable to store all bacteria
        self.bacteria = []
        self.stuckBacteria = []
        self.freeBacteria = self.bacteria

        # show message
        showMessage("Bacteria manager init done")
        writeLog(self.__dict__)

    def generateBacteria(self) -> None:
        """
        This function generate corresponding bacteria need based on the number wanted
        """

        for i in range(self.bacteriaNum):
            seed = self.bacteriaSeed + i

            # generate domain generator
            bacteriaDomainGenerator = DomainGenerator(seed)

            if self.dimension == 2:
                self._generate2DBacteria(bacteriaDomainGenerator)

            elif self.dimension == 3:
                self._generate3DBacteria(bacteriaDomainGenerator)

            else:
                raise RuntimeError("Unknown dimension of bacteria")

    def _generate2DBacteria(self, domainGenerator: DomainGenerator) -> None:
        """
        Generate 2D bacteria
        """
        showMessage("Generate 2D bacteria")
        # generate 2D bacteria Surface
        bacteria = Bacteria2D(self.trail, self.bacteriaSurfaceShape, self.bacteriaSize, self.bacteriaSurfaceCharge,
                              domainGenerator.seed)

        showMessage("Generate 2D bacteria with domain")
        bacteria.surfaceWithDomain = domainGenerator.generateDomain(bacteria, self.bacteriaDomainShape,
                                                                    self.bacteriaDomainSize,
                                                                    self.bacteriaDomainConcentration,
                                                                    self.bacteriaDomainChargeConcentration)

        # save the bacteria into manager
        self.bacteria.append(bacteria)

        # write into log
        showMessage("2D bacteria generate done")
        writeLog(self.bacteria)

    def _generate3DBacteria(self, domainGenerator: DomainGenerator) -> None:
        """
        Generate 3D bacteria
        """
        showMessage("Generate 3D bacteria")

        # depends on the simulator type, generate position for bacteria
        if self.simulatorType == 1:
            position = None
        elif self.simulatorType == 2:
            position = self.bacteriaMovementGenerator.initPosition()
        else:
            raise RuntimeError("Unknown simulator type")

        # generate 3D bacteria Surface
        bacteria = Bacteria3D(self.trail, self.bacteriaSurfaceShape, self.bacteriaSize, self.bacteriaSurfaceCharge,
                              domainGenerator.seed, position)

        showMessage("Generate 3D bacteria with domain")
        bacteria.surfaceWithDomain = domainGenerator.generateDomain(bacteria, self.bacteriaDomainShape,
                                                                    self.bacteriaDomainSize,
                                                                    self.bacteriaDomainConcentration,
                                                                    self.bacteriaDomainChargeConcentration)

        # save the bacteria into manager
        self.bacteria.append(bacteria)

        # write into log
        showMessage("3D bacteria generate done")
        writeLog(self.bacteria)
