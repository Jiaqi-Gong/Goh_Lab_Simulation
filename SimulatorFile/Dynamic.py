"""
This is dynamic bacteria movement simulator
"""
from typing import Tuple, Union

from openpyxl import Workbook
from openpyxl.worksheet._write_only import WriteOnlyWorksheet
from openpyxl.worksheet.worksheet import Worksheet

from Simulator import Simulator


class DynamicSimulator(Simulator):

    def runSimulate(self, timestep: int=None, probabilityType: str=None) -> None:
        """
        This function do the simulation
        Should be implement in the subclass
        """
        raise NotImplementedError

    def _initOutput(self) -> Tuple[Workbook, Union[WriteOnlyWorksheet, Worksheet]]:
        """
        This function init the format and content need to out put
        Should be implement in the subclass
        """
        raise NotImplementedError

    def _output(self, result: Tuple, currIter: int, end: bool) -> None:
        """
        This function generate the info need to output
        Should be implement in the subclass
        """
        raise NotImplementedError


