"""
This is dynamic bacteria movement simulator
"""
from datetime import datetime
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
        ws1.cell(1, 6, "Start Bacteria Seed # ")
        ws1.cell(1, 7, "Total bacteria number")
        ws1.cell(1, 8, "Time used (s)")
        ws1.cell(1, 9, "Time step")
        ws1.cell(1, 10, "Probability type")
        ws1.cell(1, 11, "Free bacteria number")
        ws1.cell(1, 12, "Stick bacteria number")

        if self.probabilityType.upper() == "POISSON":
            ws1.cell(1, 13, "Lambda value")
        elif self.probabilityType.upper() == "BOLTZMANN":
            ws1.cell(1, 13, "Temperature")
            ws1.cell(1, 14, "Energy")

        return (wb, ws1)

    def _output(self, result: Tuple, currIter: int, end: bool) -> None:
        """
        This function generate the info need to output
        Implement in the super class abstract method
        """
        writeLog("This is _output in Simulation")
        showMessage("Start to write result into out put")
        writeLog("self is: {}, result is: {}, currIter is: {}, end is: {}".format(
            self.__dict__, result, currIter, end))

        # calculate the time use
        time_consume = (datetime.now() - self.startTime)
        time_consume = time_consume.seconds

        # rename the out put
        wb = self.output[0]
        ws1 = self.output[1]

        # set the row position, 2 for the title of the whole sheet
        row_pos = 2 + currIter

        # get the result


        # write the result
        ws1.cell(row_pos, 1, str(self.filmManager.filmSurfaceShape) + " : " + str(self.filmManager.filmSurfaceSize))
        ws1.cell(row_pos, 2, str(self.filmManager.filmDomainShape) + " : " + str(self.filmManager.filmDomainSize))
        ws1.cell(row_pos, 3,
                 str(self.bacteriaManager.bacteriaSurfaceShape) + " : " + str(self.bacteriaManager.bacteriaSize))
        ws1.cell(row_pos, 4,
                 str(self.bacteriaManager.bacteriaDomainShape) + " : " + str(self.bacteriaManager.bacteriaDomainSize))
        ws1.cell(row_pos, 5, self.filmManager.film[0].seed)
        ws1.cell(row_pos, 6, self.bacteriaManager.bacteria[0].seed)
        ws1.cell(row_pos, 7, self.bacteriaNum)
        ws1.cell(row_pos, 8, time_consume)


        # if this is not the last iterator, update the time and return this
        if not end:
            self.startTime = datetime.now()
            return None
