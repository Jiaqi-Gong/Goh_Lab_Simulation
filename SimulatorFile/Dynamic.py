"""
This is dynamic bacteria movement simulator
"""
from typing import Tuple, Union, List, Dict

from openpyxl import Workbook
from openpyxl.worksheet._write_only import WriteOnlyWorksheet
from openpyxl.worksheet.worksheet import Worksheet

from ExternalIO import writeLog, showMessage
from SimulatorFile.Simulator import Simulator


class DynamicSimulator(Simulator):

    def __init__(self, simulationType: int, trail: int, dimension: int,
                 filmSeed: int, filmSurfaceSize: Tuple[int, int], filmSurfaceShape: str, filmSurfaceCharge: int,
                 filmDomainSize: Tuple[int, int], filmDomainShape: str, filmDomainConcentration: float,
                 filmDomainChargeConcentration: float,
                 bacteriaSeed: int, bacteriaSize: Tuple[int, int], bacteriaSurfaceShape: str,
                 bacteriaSurfaceCharge: int,
                 bacteriaDomainSize: Tuple[int, int], bacteriaDomainShape: str, bacteriaDomainConcentration: float,
                 bacteriaDomainChargeConcentration: float,
                 filmNum: int, bacteriaNum: int, intervalX: int, intervalY: int, parameters: Dict) -> None:
        """
        Init the simulation class based on the input info
        Description of input info are shown in the HelpFile.txt
        """
        simulatorType = 2
        Simulator.__init__(self, simulationType, trail, dimension, simulatorType,
                           filmSeed, filmSurfaceSize, filmSurfaceShape, filmSurfaceCharge,
                           filmDomainSize, filmDomainShape, filmDomainConcentration, filmDomainChargeConcentration,
                           bacteriaSeed, bacteriaSize, bacteriaSurfaceShape, bacteriaSurfaceCharge,
                           bacteriaDomainSize, bacteriaDomainShape, bacteriaDomainConcentration,
                           bacteriaDomainChargeConcentration,
                           filmNum, bacteriaNum, intervalX, intervalY, parameters)

        # set some variable
        self.probabilityType = None
        self.timestep = None

        # based on type, set parameter
        if parameters["probabilityType"].upper() == "POISSON":
            self.Lambda = None

    def runSimulate(self) -> None:
        """
        This function do the simulation
        Implement in the super class abstract method
        """
        raise NotImplementedError

    def _initOutput(self) -> Tuple[Workbook, Union[WriteOnlyWorksheet, Worksheet]]:
        """
        This function init the format and content need to out put
        Implement in the super class abstract method
        """
        writeLog("This is _initOutput in Simulation")
        showMessage("Init the output")
        writeLog(self.__dict__)

        # creates excel file
        wb = Workbook()
        ws1 = wb.create_sheet("Results", 0)

        # naming the columns in the worksheet
        ws1.cell(1, 1, "Film shape and size")
        ws1.cell(1, 2, "Film domain shape and size")
        ws1.cell(1, 3, "Bacteria shape and size")
        ws1.cell(1, 4, "Bacteria domain shape and size")
        ws1.cell(1, 5, "Film Seed # ")
        ws1.cell(1, 6, "Bacteria Seed # ")
        ws1.cell(1, 7, "Time step")
        ws1.cell(1, 8, "Probability type")
        ws1.cell(1, 9, "Free bacteria number")
        ws1.cell(1, 10, "Stick bacteria number")


        ws1.cell(1, 11, "Min Energy Gradient Strip")
        ws1.cell(1, 12, "Time used (s)")
        ws1.cell(1, 13, "Interact type")
        raise NotImplementedError

    def _output(self, result: Tuple, currIter: int, end: bool) -> None:
        """
        This function generate the info need to output
        Implement in the super class abstract method
        """
        raise NotImplementedError
