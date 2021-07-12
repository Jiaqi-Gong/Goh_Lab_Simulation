"""
This is dynamic bacteria movement simulator
"""
from datetime import datetime
from typing import Tuple, Union, List, Dict

from openpyxl import Workbook
from openpyxl.worksheet._write_only import WriteOnlyWorksheet
from openpyxl.worksheet.worksheet import Worksheet

from ExternalIO import writeLog, showMessage, saveResult
from SimulatorFile.Simulator import Simulator
from BacteriaFile.BacteriaMovement import BacteriaMovementGenerator


class DynamicSimulator(Simulator):

    def __init__(self, trail: int, dimension: int,
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
        # set some variable
        self.probabilityType = None
        self.timeStep = None
        self.bacteriaMovementSeed = None
        self.dumpStep = None

        # simulation type is not applicable for dynamic simulator
        simulationType = -1

        # based on type, set parameter
        if parameters["probabilityType"].upper() == "POISSON":
            self.Lambda = None
        elif parameters["probabilityType"].upper() == "BOLTZMANN":
            self.temperature = None
            self.energy = None

        # call parent to generate simulator
        simulatorType = 2
        Simulator.__init__(self, simulationType, trail, dimension, simulatorType,
                           filmSeed, filmSurfaceSize, filmSurfaceShape, filmSurfaceCharge,
                           filmDomainSize, filmDomainShape, filmDomainConcentration, filmDomainChargeConcentration,
                           bacteriaSeed, bacteriaSize, bacteriaSurfaceShape, bacteriaSurfaceCharge,
                           bacteriaDomainSize, bacteriaDomainShape, bacteriaDomainConcentration,
                           bacteriaDomainChargeConcentration,
                           filmNum, bacteriaNum, intervalX, intervalY, parameters)



    def runSimulate(self) -> None:
        """
        This function do the simulation
        Implement in the super class abstract method
        """

        raise NotImplementedError

        # set some variable, will replaced by user input
        z_restriction = 4
        self.bacteriaMovementSeed = 10
        bacteriaShape = self.bacteriaManager.bacteriaSurfaceShape

        # create bacteria movement generator
        # film and bacteria should be 3D and all film and bacteria should be same, only diff is domain distribution
        film = self.filmManager.film[0]
        bacteria = self.bacteriaManager.bacteria[0]

        # check film and bacteria type
        if film.dimension != 3 or bacteria.dimension != 3:
            raise RuntimeError("The film and bacteria dimension should be 3D for dynamic simulation")

        filmSize = (film.length, film.width, film.height)
        bacteriaSize = (bacteria.length, bacteria.width, bacteria.height)
        bactMoveGenerator = BacteriaMovementGenerator(z_restriction, self.bacteriaMovementSeed, bacteriaShape,
                                                      filmSize, bacteriaSize)

        # init position for every bacteria
        for bacteria in self.bacteriaManager.bacteria:
            bacteria.position = bactMoveGenerator.initPosition()

        # do the simulation
        end = False
        for currIter in range(self.timeStep):
            # check the end of timeStep
            if currIter == self.timeStep - 1:
                end = True

            # do the simulate
            self._simulate(bactMoveGenerator)
            result = [len(self.bacteriaManager.freeBacteria), len(self.bacteriaManager.stuckBacteria)]

            # update the output based on the dump step
            if currIter % self.dumpStep == 0:
                self._output(result, currIter, end)

        # save the last simulate, if it is not saved in the loop
        if (self.timeStep - 1) % self.dumpStep != 0:
            self._output(result, currIter, end)

        showMessage("Simulation done")


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
        ws1.cell(1, 8, "Bacteria Movement generator seed")
        ws1.cell(1, 9, "Time used (s)")
        ws1.cell(1, 10, "Probability type")
        ws1.cell(1, 11, "Time step")
        ws1.cell(1, 12, "Free bacteria number")
        ws1.cell(1, 13, "Stuck bacteria number")

        if self.probabilityType.upper() == "POISSON":
            ws1.cell(1, 14, "Lambda value")
        elif self.probabilityType.upper() == "BOLTZMANN":
            ws1.cell(1, 14, "Temperature")
            ws1.cell(1, 15, "Energy")

        return (wb, ws1)

    def _output(self, result: List[int], currIter: int, end: bool) -> None:
        """
        This function generate the info need to output
        Implement in the super class abstract method
        """
        writeLog("This is _output in dynamic simulator")
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
        freeBactNum, stuckBactNum = result

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
        ws1.cell(row_pos, 8, self.bacteriaMovementSeed)
        ws1.cell(row_pos, 9, time_consume)
        ws1.cell(row_pos, 10, self.probabilityType)
        ws1.cell(row_pos, 11, currIter)
        ws1.cell(row_pos, 12, freeBactNum)
        ws1.cell(row_pos, 13, stuckBactNum)

        if self.probabilityType.upper() == "POISSON":
            ws1.cell(1, 14, self.Lambda)
        elif self.probabilityType.upper() == "BOLTZMANN":
            ws1.cell(1, 14, self.temperature)
            ws1.cell(1, 15, self.energy)

        # if this is not the last iterator, update the time and return this
        if not end:
            self.startTime = datetime.now()
            return None

        # save the excel file into folder result
        name = "Type_{}_trail_{}-{}-{}.xlsx".format(str(self.simulationType), self.trail,
                                                    datetime.now().strftime("%m_%d"),
                                                    datetime.now().strftime("%H-%M-%S"))
        file_path = "Result/" + name

        # call function in ExternalIO to save workbook
        saveResult(wb, file_path)

    def _simulate(self, bactMoveGenerator: BacteriaMovementGenerator) -> None:
        """
        This function do the simulate
        """
        """
        1. Call initposition function in bact movement give all bacteria an init position
        2. Do a loop, in each loop, call stickOrNot and give new position unti the end of timeStep
        3. If bacteria is stick, change it from free list to stick list
        4. At the end, give the length of free and length of stick
        """
        # raise NotImplementedError

        writeLog("Start simulation in dynamic simulator")

        # if no free bacteria, do nothing
        if len(self.bacteriaManager.freeBacteria) == 0:
            return None

        # if probability type is Boltzmann, need to update self.temperature and self.energy
        # how to implement it wait until next meeting

        # loop all free bacteria
        for bact in self.bacteriaManager.freeBacteria:
            # get next position
            bactNextPos = bactMoveGenerator.nextPosition(self.probabilityType, bact.position, self.Lambda,
                                                         self.temperature, self.energy)

            # based on next position, move the bacteria
            if not bactNextPos:
                # bacteria is stuck, move from free list to stuck list
                self.bacteriaManager.freeBacteria.remove(bact)
                self.bacteriaManager.stuckBacteria.append(bact)
            else:
                # bacteria is not stuck, update the position
                bact.position = bactNextPos

