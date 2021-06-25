"""
This file contains several function to generate next move of bacteria
"""
from typing import Tuple, Union


class BacteriaMovementGenerator:
    """
    This class is a generator generate next move of bacteria
    """

    # type declaration





    def nextMove(self, probabilityType: str, position: Union[Tuple[int, int], Tuple[int, int, int]]) -> \
            Union[bool, Tuple[int, int], Tuple[int, int, int]]:
        """
        This function take in probability type, position
        return False if this bacteria is stuck
        return a tuple contain new position if not stuck
        """

        # call appropriate probability function to decide stuck or not
        if probabilityType == "POISSON":
            result = self._poisson()
        elif probabilityType == "BOLTZMANN":
            result = self._boltzmann()
        else:
            raise RuntimeError("Unknown probability type")

        # check stuck or not
        # if stuck, return false
        if result is True:
            return False
        else:
            return self._nextPosition()

    def _poisson(self) -> bool:
        """
        This function uses Poisson distribution to decide stuck or not
        return True for stuck
        """
        raise NotImplementedError

    def _boltzmann(self) -> bool:
        """
        This function uses Boltzmann distribution to decide stuck or not
        return True for stuck
        """
        raise NotImplementedError

    def _nextPosition(self) -> Union[Tuple[int, int], Tuple[int, int, int]]:
        """
        This function return new position
        """
        raise NotImplementedError