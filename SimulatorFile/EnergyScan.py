"""
This is energy scan simulator
"""
from datetime import datetime
from typing import Tuple, Union, List, Dict

import numpy as np
from numpy import ndarray
from openpyxl.worksheet._write_only import WriteOnlyWorksheet
from openpyxl.worksheet.worksheet import Worksheet

from ExternalIO import showMessage, writeLog, saveResult
from openpyxl import Workbook
from openpyxl.utils import get_column_letter  # allows access to letters of each column

from SimulatorFile.Simulator import Simulator


class EnergySimulator(Simulator):
    """
    This class is used for bacteria scan film surface energy simulation
    """
    interactType: Union[None, str]

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
        simulatorType = 1
        Simulator.__init__(self, simulationType, trail, dimension, simulatorType,
                           filmSeed, filmSurfaceSize, filmSurfaceShape, filmSurfaceCharge,
                           filmDomainSize, filmDomainShape, filmDomainConcentration, filmDomainChargeConcentration,
                           bacteriaSeed, bacteriaSize, bacteriaSurfaceShape, bacteriaSurfaceCharge,
                           bacteriaDomainSize, bacteriaDomainShape, bacteriaDomainConcentration,
                           bacteriaDomainChargeConcentration,
                           filmNum, bacteriaNum, intervalX, intervalY)

        # set some variable
        self.interactType = None

    def runSimulate(self) -> None:
        """
        Based on the simulation type, do the corresponding simulation
        """
        writeLog("This is runSimulation in Simulation")
        showMessage("Start to run simulation baed on simulation type")
        writeLog(self.__dict__)

        # check does all parameter is assigned
        self.checkAllSet()

        # record the number of simulation did
        currIter = 0

        # init the end of iterator
        end = False

        # type 1 simulation
        # only one film and one bacteria
        if self.simulationType == 1:
            end = True
            self._simulate(currIter, self.filmManager.film[0].surfaceWithDomain,
                           self.bacteriaManager.bacteria[0].surfaceWithDomain, end)

        # type 2 simulation
        elif self.simulationType == 2:
            # One film, multiple different bacteria, every bacteria scan the surface once
            for i in range(self.bacteriaManager.bacteriaNum):
                showMessage("This is type 2 simulation with simulation #: {}".format({i}))

                # change end indicator
                if i == self.bacteriaManager.bacteriaNum - 1:
                    end = True

                # start simulation
                self._simulate(currIter, self.filmManager.film[0].surfaceWithDomain,
                               self.bacteriaManager.bacteria[currIter].surfaceWithDomain, end)
                currIter += 1

        # type 3 simulation
        elif self.simulationType == 3:
            # multiple different film, one bacteria, bacteria scan every surface once
            for i in range(self.filmManager.filmNum):
                showMessage("This is type 3 simulation with simulation #: {}".format({i}))

                # change end indicator
                if i == self.filmManager.filmNum - 1:
                    end = True

                # start simulation
                self._simulate(currIter, self.filmManager.film[currIter].surfaceWithDomain,
                               self.bacteriaManager.bacteria[0].surfaceWithDomain, end)
                currIter += 1

        else:
            raise RuntimeError("Wrong simulation type")

    def _simulate(self, currIter: int, film: ndarray, bacteria: ndarray, end: bool) -> None:
        """
        This is the simulation function in this program, call function do the simulation and output the result
        Prerequisite: surface already generated
        """
        writeLog("This is _simulate in Simulation")
        showMessage("Start to run simulation")
        writeLog("self is: {}, currIter is: {}, film is: {}, bacteria is: {}, end is: {}".format(
            self.__dict__, currIter, film, bacteria, end))

        # call simulation based on the simulation type
        if self.dimension == 2:
            if self.interactType.upper() == "DOT":
                result = self._dotInteract2D(self.intervalX, self.intervalY, film, bacteria)
            elif self.interactType.upper() in ["CUTOFF", "CUT-OFF"]:
                result = self._cutoffInteract2D(self.intervalX, self.intervalY, film, bacteria)
            else:
                raise RuntimeError("Unknown interact type")
        elif self.dimension == 3:
            if self.interactType.upper() == "DOT":
                result = self._dotInteract3D()
            elif self.interactType.upper() in ["CUTOFF", "CUT-OFF"]:
                result = self._cutoffInteract3D(self.intervalX, self.intervalY, film, bacteria)
            else:
                raise RuntimeError("Unknown interact type")
        else:
            raise RuntimeError("Wrong dimension in _simulate")

        # set the output
        self._output(result, currIter, end)

    def _initOutput(self) -> Tuple[Workbook, Union[WriteOnlyWorksheet, Worksheet]]:
        """
        Init the out put excel file
        copy from the old code with separate seed into film seed and bacteria seed
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
        ws1.cell(1, 7, "Min Energy")
        ws1.cell(1, 8, "Min X")
        ws1.cell(1, 9, "Min Y")
        ws1.cell(1, 10, "Surface Charge at Min Energy")
        ws1.cell(1, 11, "Min Energy Gradient Strip")
        ws1.cell(1, 12, "Time used (s)")
        ws1.cell(1, 13, "Interact type")
        ws1.cell(1, 14, "Histogram")

        # create numbering for histogram plot
        count = 0
        for i in range(15, 31):
            ws1.cell(1, i, count)
            ws1.cell(2, i, 0)
            count += 1

        # adjust column width to text length
        for i in range(ws1.max_column):
            text = ws1.cell(1, i + 1).value
            if type(text) == int:
                text = str(text)
                column_width = len(text) + 1
            else:
                column_width = len(text)
            ws1.column_dimensions[get_column_letter(i + 1)].width = column_width

        return (wb, ws1)

    def _output(self, result: Tuple, currIter: int, end: bool) -> None:
        """
        Output the simulation result into a file
        Copy from old code with minor change
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

        # split the result
        min_energy, min_x, min_y, min_energy_charge, min_charge, min_charge_x, min_charge_y = result

        # shows the gradient lines position
        grad_strip = min_x // 500

        # set the row position, 2 for the title of the whole sheet
        row_pos = 2 + currIter

        # write the result
        ws1.cell(row_pos, 1, str(self.filmManager.filmSurfaceShape) + " : " + str(self.filmManager.filmSurfaceSize))
        ws1.cell(row_pos, 2, str(self.filmManager.filmDomainShape) + " : " + str(self.filmManager.filmDomainSize))
        ws1.cell(row_pos, 3,
                 str(self.bacteriaManager.bacteriaSurfaceShape) + " : " + str(self.bacteriaManager.bacteriaSize))
        ws1.cell(row_pos, 4,
                 str(self.bacteriaManager.bacteriaDomainShape) + " : " + str(self.bacteriaManager.bacteriaDomainSize))
        ws1.cell(row_pos, 5, self.filmManager.film[currIter].seed)
        ws1.cell(row_pos, 6, self.bacteriaManager.bacteria[currIter].seed)
        ws1.cell(row_pos, 7, min_energy)
        ws1.cell(row_pos, 8, min_x)
        ws1.cell(row_pos, 9, min_x)
        ws1.cell(row_pos, 10, min_energy_charge)
        ws1.cell(row_pos, 11, grad_strip)
        ws1.cell(row_pos, 12, time_consume)
        ws1.cell(row_pos, 13, self.interactType)

        # if this is not the last iterator, update the time and return this
        if not end:
            self.startTime = datetime.now()
            return None

        # special count for simulation type 2
        # count number of min_energy locations at each gradient strip
        if self.simulationType == 2:
            showMessage("WARNING: Potential bug here")
            for row_num in range(self.bacteriaManager.bacteriaNum):
                row = 2 + row_num
                val_id = ws1.cell(row, 11).value
                val = ws1.cell(2, 14 + int(val_id)).value
                ws1.cell(2, 14 + int(val_id), int(val) + 1)

        # save the excel file into folder result
        name = "Type_{}_trail_{}-{}-{}.xlsx".format(str(self.simulationType), self.trail,
                                                    datetime.now().strftime("%m_%d"),
                                                    datetime.now().strftime("%H-%M-%S"))
        file_path = "Result/" + name

        # call function in ExternalIO to save workbook
        saveResult(wb, file_path)

    def _dotInteract2D(self, intervalX: int, intervalY: int, film: ndarray, bacteria: ndarray) -> \
            Tuple[int, int, int, int, int, int, int]:
        """
        Do the simulation, scan whole film surface with bacteria
        The energy calculate only between bacteria surface and the film surface directly under the bacteria
        This code is copy from the old code with minor name change
        """
        writeLog("This is _interact2D in Simulation")
        showMessage("Start to interact ......")
        writeLog("intervalX is: {}, intervalY is: {}, film is: {}, bacteria is: {}".format(
            intervalX, intervalY, film, bacteria))

        # shape of the bacteria
        shape = bacteria.shape

        # set the range
        range_x = np.arange(0, shape[0], intervalX)
        range_y = np.arange(0, shape[1], intervalY)

        writeLog("shape is : {}, range_x is: {}, range_y is: {}".format(shape, range_x, range_y))

        # init some variable
        # randomly, just not negative
        min_energy = 1000
        min_charge = 1000
        min_energy_charge = 1000
        min_charge_x = 0
        min_charge_y = 0
        min_x = -1
        min_y = -1

        # change the bacteria surface into 1D
        bacteria_1D = np.reshape(bacteria, (-1))

        # scan through the surface and make calculation
        for x in range_x:
            for y in range_y:
                # set the x boundary and y boundary
                x_boundary = shape[0] + x
                y_boundary = shape[1] + y

                writeLog("x_boundary is: {}, y_boundary is: {}".format(x_boundary, y_boundary))

                # check if bacteria surface is exceed range of film surface
                if x_boundary > shape[0] or y_boundary > shape[1]:
                    # if exceed the surface, go to next iteration
                    continue

                # do the calculation

                # change the corresponding film surface into 1D
                film_use = film[x: x_boundary, y: y_boundary]
                film_1D = np.reshape(film_use, (-1))

                # calculate energy, uses electrostatic energy formula, assuming that r = 1
                # WARNING: r should be change based on the height difference between film and bacteria in future
                energy = np.dot(film_1D, bacteria_1D)
                writeLog("WARNING: r should be change based on the height difference between film and bacteria in "
                         "future")

                # count and unique
                unique, counts = np.unique(film_use, return_counts=True)

                # record all variables
                writeLog("film_use is: {}, film_1D is: {}, energy is: {}, unique is: {}, counts is: {}".format(
                    film_use, film_1D, energy, unique, counts))

                # check the calculation result and change corresponding value
                if len(unique) == 1:
                    if unique[0] == -1:
                        charge = -counts[0]
                    else:
                        charge = counts[0]
                elif unique[0] == -1:
                    charge = -counts[0] + counts[1]
                elif unique[0] == 1:
                    charge = counts[0] - counts[1]
                else:
                    raise RuntimeError("Variable 'charge' in _interact2D not init, caused by the error in unique")

                if charge < min_charge:
                    min_charge = charge
                    min_charge_x = x
                    min_charge_y = y

                # find minimum energy and location
                if energy < min_energy:
                    min_energy = energy
                    min_x = x
                    min_y = y
                    min_energy_charge = charge

        # save the result
        result = (min_energy, min_x, min_y, min_energy_charge, min_charge, min_charge_x, min_charge_y)

        showMessage("Interact done")
        writeLog(result)

        return result

    def _dotInteract3D(self) -> Tuple[int, int, int, int, int, int, int]:
        raise NotImplementedError

    def _cutoffInteract2D(self, intervalX: int, intervalY: int, film: ndarray, bacteria: ndarray) -> \
            Tuple[int, int, int, int, int, int, int]:
        """
        Do the simulation, scan whole film surface with bacteria
        The energy calculate only between bacteria surface and the film surface directly under the bacteria
        This code is copy from the old code with minor name change
        """
        raise NotImplementedError

    def _cutoffInteract3D(self, intervalX: int, intervalY: int, film: ndarray, bacteria: ndarray) -> \
            Tuple[int, int, int, int, int, int, int]:
        """
        Do the simulation, scan whole film surface with bacteria
        The energy calculate only between bacteria surface and the film surface directly under the bacteria
        This code is copy from the old code with minor name change
        """
        raise NotImplementedError
