"""
This program:
- Saves and manages all bacteria
"""
import os
from typing import Tuple, Union, List

from Bacteria import Bacteria2D, Bacteria3D
from BacteriaFile.Bacteria import Bacteria2D, Bacteria3D
from BacteriaFile.BacteriaMovement import BacteriaMovementGenerator
from SurfaceGenerator.Domain import DomainGenerator
from ExternalIO import showMessage, writeLog, timeMonitor
import multiprocessing as mp


class BacteriaManager:
    """
    This class saves all bacteria used in this simulation, and generates all corresponding films
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
    neutralDomain: bool

    def __init__(self, trail: int, dimension: int, simulatorType: int,
                 bacteriaSeed: int, bacteriaSize: Tuple[int, int, int], bacteriaSurfaceShape: str,
                 bacteriaSurfaceCharge: int,
                 bacteriaDomainSize: Tuple[int, int], bacteriaDomainShape: str, bacteriaDomainConcentration: float,
                 bacteriaDomainChargeConcentration: float, bacteriaNum: int, neutralDomain: bool):
        """
        Initializes the film manager
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
        self.neutralDomain = neutralDomain

        # depends on the dimension, set bacteria size
        if dimension == 2:
            self.bacteriaSize = bacteriaSize[:2]
        else:
            self.bacteriaSize = bacteriaSize

        # init a variable to store all bacteria
        self.bacteria = []
        self.stuckBacteria = []
        self.freeBacteria = self.bacteria

        # show message
        showMessage("Bacteria manager initialization: Complete.")

    @timeMonitor
    def generateBacteria(self) -> None:
        """
        This function generates corresponding bacteria need based on the desired dimension.
        """

        # using mp to speed up generate
        ncpus = max(int(os.environ.get('SLURM_CPUS_PER_TASK', default=1)), 1)
        # ncpus = 8

        # original version
        # for i in range(self.bacteriaNum):
        #     seed = self.bacteriaSeed + i
        #
        #     # generate domain generator
        #     bacteriaDomainGenerator = DomainGenerator(seed, self.neutralDomain)
        #
        #     if self.dimension == 2:
        #         self._generate2DBacteria(bacteriaDomainGenerator)
        #
        #     elif self.dimension == 3:
        #         self._generate3DBacteria(bacteriaDomainGenerator)
        #
        #     else:
        #         raise RuntimeError("This is not a valid bacteria dimension.")

        # mp version
        # setup mp pool
        pool = mp.Pool(processes=ncpus)

        # setup data
        data = []

        # calculate the number for each process with floor
        eachBactNum = int(self.bacteriaNum / ncpus)
        lastBactNum = self.bacteriaNum - eachBactNum * (ncpus - 1)

        # append data
        for i in range(ncpus - 1):
            temp_data = [eachBactNum, self.bacteriaSeed + eachBactNum * i]
            data.append(temp_data)

        # append last one
        temp_data = [lastBactNum, self.bacteriaSeed + self.bacteriaNum - lastBactNum ]
        data.append(temp_data)

        result = pool.map(self._mpGenerateBacteria, data)
        bacteria_lst = [item for sublist in result for item in sublist]
        self.bacteria.extend(bacteria_lst)

    def _mpGenerateBacteria(self, data: List[int]) -> List:
        """
        A multiprocess function for generate bacteria
        Take in data, first is bacteria number and second is seed
        """
        bacteriaNum, seed = data

        # init a list save bact
        bact_lst = []

        for i in range(bacteriaNum):
            seed = seed + i

            # generate domain generator
            bacteriaDomainGenerator = DomainGenerator(seed, self.neutralDomain)

            if self.dimension == 2:
                bact_lst.append(self._generate2DBacteria(bacteriaDomainGenerator))
            elif self.dimension == 3:
                bact_lst.append(self._generate3DBacteria(bacteriaDomainGenerator))
            else:
                raise RuntimeError("This is not a valid bacteria dimension.")

        return bact_lst

    def _generate2DBacteria(self, domainGenerator: DomainGenerator) -> Bacteria2D:
        """
        Generates 2D bacteria
        """
        showMessage("Generating 2D bacteria...")
        # generate 2D bacteria Surface
        bacteria = Bacteria2D(self.trail, self.bacteriaSurfaceShape, self.bacteriaSize, self.bacteriaSurfaceCharge,
                              domainGenerator.seed)

        showMessage("Generating 2D bacteria with domain...")
        bacteria.surfaceWithDomain, bacteria.realDomainConc = domainGenerator.generateDomain(bacteria,
                                                                                             self.bacteriaDomainShape,
                                                                                             self.bacteriaDomainSize,
                                                                                             self.bacteriaDomainConcentration,
                                                                                             self.bacteriaDomainChargeConcentration)

        # save the bacteria into manager
        # no mp method
        # self.bacteria.append(bacteria)

        # write into log
        showMessage("2D bacteria generation: Complete.")
        writeLog(self.bacteria)

        # save the bacteria into manager
        # mp method
        return bacteria

    def _generate3DBacteria(self, domainGenerator: DomainGenerator) -> Bacteria3D:
        """
        Generate 3D bacteria
        """
        showMessage("Generating 3D bacteria...")

        # depends on the simulator type, generate position for bacteria
        # if self.simulatorType == 1:
        #     position = None
        # elif self.simulatorType == 2:
        #     position = self.bacteriaMovementGenerator.initPosition()
        # else:
        #     raise RuntimeError("Unknown simulator type")

        # generate 3D bacteria Surface
        bacteria = Bacteria3D(self.trail, self.bacteriaSurfaceShape, self.bacteriaSize, self.bacteriaSurfaceCharge,
                              domainGenerator.seed)

        showMessage("Generating 3D bacteria with domain...")
        bacteria.surfaceWithDomain, bacteria.realDomainConc = domainGenerator.generateDomain(bacteria, self.bacteriaDomainShape,
                                                                    self.bacteriaDomainSize,
                                                                    self.bacteriaDomainConcentration,
                                                                    self.bacteriaDomainChargeConcentration)

        # save the bacteria into manager
        # np mp method
        # self.bacteria.append(bacteria)

        # write into log
        showMessage("3D bacteria generation: Complete.")
        writeLog(self.bacteria)

        # save the bacteria into manager
        # mp method
        return bacteria