"""
This is dynamic bacteria movement simulator
"""
from typing import Tuple, Union, List, Dict

from openpyxl import Workbook
from openpyxl.worksheet._write_only import WriteOnlyWorksheet
from openpyxl.worksheet.worksheet import Worksheet

from Simulator import Simulator


class DynamicSimulator(Simulator):

    def __init__(self, simulationType: int, trail: int, dimension: int,
                 filmSeed: int, filmSurfaceSize: Tuple[int, int], filmSurfaceShape: str, filmSurfaceCharge: int,
                 filmDomainSize: Tuple[int, int], filmDomainShape: str, filmDomainConcentration: float,
                 filmDomainChargeConcentration: float,
                 bacteriaSeed: int, bacteriaSize: Tuple[int, int], bacteriaSurfaceShape: str,
                 bacteriaSurfaceCharge: int,
                 bacteriaDomainSize: Tuple[int, int], bacteriaDomainShape: str, bacteriaDomainConcentration: float,
                 bacteriaDomainChargeConcentration: float,
                 filmNum: int, bacteriaNum: int, intervalX: int, intervalY: int) -> None:
        """
        Init the simulation class based on the input info
        Description of input info are shown in the HelpFile.txt
        """
        Simulator.__init__(self, simulationType, trail, dimension,
                           filmSeed, filmSurfaceSize, filmSurfaceShape, filmSurfaceCharge,
                           filmDomainSize, filmDomainShape, filmDomainConcentration, filmDomainChargeConcentration,
                           bacteriaSeed, bacteriaSize, bacteriaSurfaceShape, bacteriaSurfaceCharge,
                           bacteriaDomainSize, bacteriaDomainShape, bacteriaDomainConcentration,
                           bacteriaDomainChargeConcentration,
                           filmNum, bacteriaNum, intervalX, intervalY)

        # set some variable
        self.probabilityType = None
        self.timestep = None

    def runSimulate(self) -> None:
        """
        This function do the simulation
        Implement in the super class abstract method
        """
        # check does all parameter is set
        self.checkAllSet()
        raise NotImplementedError

    def _initOutput(self) -> Tuple[Workbook, Union[WriteOnlyWorksheet, Worksheet]]:
        """
        This function init the format and content need to out put
        Implement in the super class abstract method
        """
        raise NotImplementedError

    def _output(self, result: Tuple, currIter: int, end: bool) -> None:
        """
        This function generate the info need to output
        Implement in the super class abstract method
        """
        raise NotImplementedError
