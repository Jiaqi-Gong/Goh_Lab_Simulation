"""
This is an abstract file for simulator
"""
import abc
from abc import ABC
from datetime import datetime
from typing import Tuple, Union, List, Dict

from openpyxl import Workbook
from openpyxl.worksheet._write_only import WriteOnlyWorksheet
from openpyxl.worksheet.worksheet import Worksheet

from ExternalIO import writeLog, showMessage
from Manager.FilmManager import FilmManager
from Manager.BacteriaManager import BacteriaManager


class Simulator(ABC):
    """
    This is an abstract class for all simulator, all simulator are same in generate bacteria and film
    the only different is how to do the interact
    """

    # declare the type of all variable
    trail: int
    dimension: int
    simulationType: int
    simulatorType: int
    bacteriaNum: int
    intervalX: int
    intervalY: int
    parameters: Union[None, Dict]
    filmManager: FilmManager
    bacteriaManager: BacteriaManager
    startTime: datetime
    output: Tuple[Workbook, Union[WriteOnlyWorksheet, Worksheet]]

    def __init__(self, simulationType: int, trail: int, dimension: int, simulatorType: int,
                 filmSeed: int, filmSurfaceSize: Tuple[int, int], filmSurfaceShape: str, filmSurfaceCharge: int,
                 filmDomainSize: Tuple[int, int], filmDomainShape: str, filmDomainConcentration: float,
                 filmDomainChargeConcentration: float,
                 bacteriaSeed: int, bacteriaSize: Union[Tuple[int, int], Tuple[int, int, int]], bacteriaSurfaceShape: str,
                 bacteriaSurfaceCharge: int,
                 bacteriaDomainSize: Tuple[int, int], bacteriaDomainShape: str, bacteriaDomainConcentration: float,
                 bacteriaDomainChargeConcentration: float,
                 filmNum: int, bacteriaNum: int, intervalX: int, intervalY: int, parameters: Dict) -> None:
        """
        Init the simulation class based on the input info
        Description of input info are shown in the HelpFile.txt
        """
        writeLog("This is init in class Simulation")
        showMessage("Start to init the simulation generator")

        # set variables
        self.trail = trail
        self.dimension = dimension
        self.simulationType = simulationType
        self.simulatorType = simulatorType
        self.bacteriaNum = bacteriaNum
        self.intervalX = intervalX
        self.intervalY = intervalY
        self.parameters = parameters

        # init some variable
        self._setExtraParameter()
        self._checkAllSet()
        self.filmManager = FilmManager(trail, dimension, filmSeed, filmSurfaceSize, filmSurfaceShape, filmSurfaceCharge,
                                       filmDomainSize, filmDomainShape, filmDomainConcentration,
                                       filmDomainChargeConcentration, filmNum)

        self.bacteriaManager = BacteriaManager(trail, dimension, simulatorType, bacteriaSeed, bacteriaSize,
                                               bacteriaSurfaceShape, bacteriaSurfaceCharge, bacteriaDomainSize,
                                               bacteriaDomainShape, bacteriaDomainConcentration,
                                               bacteriaDomainChargeConcentration, bacteriaNum)
        self.startTime = datetime.now()
        self.output = self._initOutput()

        # write to log
        writeLog(self.__dict__)

        # generate corresponding variable
        self.filmManager.generateFilm()
        self.bacteriaManager.generateBacteria()

        # write two manager into the log
        writeLog(self.filmManager.__dict__)
        writeLog(self.bacteriaManager.__dict__)

    def _checkAllSet(self) -> None:
        """
        This function uses to check does all parameter for this class is set
        """
        for parameter in self.__dict__:
            if self.__dict__[parameter] is None:
                raise RuntimeError("parameter {} is not set".format(parameter))

    def _setExtraParameter(self, ) -> None:
        """
        This function uses to set extra parameter for the simulator
        parameters is a dictionary, key is parameter name, value is the value want assign to parameter
        """
        for parameter in self.parameters:
            if type(self.parameters[parameter]) == str:
                execString = "self.{} = '{}'".format(parameter, self.parameters[parameter])
            else:
                execString = "self.{} = {}".format(parameter, self.parameters[parameter])

            # execute the assign command
            exec(execString)

    @abc.abstractmethod
    def runSimulate(self) -> None:
        """
        This function do the simulation
        Should be implement in the subclass
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _initOutput(self) -> Tuple[Workbook, Union[WriteOnlyWorksheet, Worksheet]]:
        """
        This function init the format and content need to out put
        Should be implement in the subclass
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _output(self, result: Tuple, currIter: int, end: bool) -> None:
        """
        This function generate the info need to output
        Should be implement in the subclass
        """
        raise NotImplementedError
