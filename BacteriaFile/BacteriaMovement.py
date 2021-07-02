"""
This file contains several function to generate next move of bacteria
"""
from typing import Tuple, Union


class BacteriaMovementGenerator:
    """
    This class is a generator generate next move of bacteria
    """

    # type declaration

    def __init__(self) -> None:
        """
        Init the movement generator
        """
        # depends on do you need new variable for poisson distribution or boltzmann distribution, init your class
        # since I don't known the detail on how you guys implement these functions, so I left blank at here
        raise NotImplementedError

    def initPosition(self) -> Tuple[int, int, int]:
        """
        This function is used to generate the init position of bacteria
        """
        raise NotImplementedError

    def nextPosition(self, probabilityType: str, position: Tuple[int, int, int]) -> Union[bool, Tuple[int, int, int]]:
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
            return self._nextPosition(position)

    def _poisson(self) -> bool:
        """
        This function uses Poisson distribution to decide stuck or not
        return True for stuck
        """

        # Should consider how to get the value of lambda, fix it or ask user to input and how this probability
        # connect to decide bacteria stuck or not
        raise NotImplementedError

    def _boltzmann(self) -> bool:
        """
        This function uses Boltzmann distribution to decide stuck or not
        return True for stuck
        """

        # Look at the boltzmann distribution first and decide how to relate it to the probability of bacteria stuck
        # or not
        raise NotImplementedError

    def _nextPosition(self, position: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        This function return new position
        """

        # should judge the input is 2D or 3D or if decide dynamic simulation is only for 3D
        # then only accept 3D coordinate input,
        # change position: Union[Tuple[int, int], Tuple[int, int, int]] to position: Tuple[int, int, int]
        # change -> Union[Tuple[int, int], Tuple[int, int, int]]: to -> Tuple[int, int, int]
        raise NotImplementedError
