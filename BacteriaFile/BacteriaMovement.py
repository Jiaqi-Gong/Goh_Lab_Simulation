"""
This file contains several function to generate next move of bacteria
"""
from typing import Tuple, Union
from SurfaceGenerator.Surface import Surface
from BacteriaFile.Bacteria import Bacteria2D, Bacteria3D
import numpy as np

class BacteriaMovementGenerator:
    """
    This class is a generator generate next move of bacteria
    """

    # type declaration
    seed: int

    def __init__(self, seed: int) -> None:
        """
        Init the movement generator
        :param: seed for random, if using same seed can repeat the simulation
        """
        self.seed = seed
        # depends on do you need new variable for poisson distribution or boltzmann distribution, init your class
        # since I don't known the detail on how you guys implement these functions, so I left blank at here

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

    def _nextPosition2D(self, position: Tuple[int, int, int], surface: Surface, z_restriction: int) -> Tuple[int, int, int]:
        """
        This function return new position for 2D bacteria (currently next position is based on random movement of bacteria)
        position is based on the left-lower most part of the bacteria (ie. closest to the origin if the bacteria was in
        the first quadrant in a 3D cartesian coordinate system)
        """
        # set seed for random
        np.random.seed(self.seed)

        movement = False
        while not movement:
            # create variable called "movement" to determine which direction the bacteria will move in
            x_movement = int(np.random.choice([-1, 0, 1], 1, replace=False))
            y_movement = int(np.random.choice([-1, 0, 1], 1, replace=False))
            z_movement = int(np.random.choice([-1, 0, 1], 1, replace=False))

            # set restrictions (ie. position can't be off the surface)
            # x direction
            if position[0] == 0:
                x_movement = int(np.random.choice([0, 1], 1, replace=False))
            elif position[0] == surface.length - Bacteria2D.size[0]:
                x_movement = int(np.random.choice([-1, 0], 1, replace=False))

            # y direction
            if position[1] == 0:
                y_movement = int(np.random.choice([0, 1], 1, replace=False))
            elif position[1] == surface.width - Bacteria2D.size[1]:
                y_movement = int(np.random.choice([-1, 0], 1, replace=False))

            # z direction
            if position[2] == 0:
                z_movement = int(np.random.choice([0, 1], 1, replace=False))
            elif position[2] == z_restriction - 3: # the restriction for how far off the bacteria can be from the surface is arbitrary and can be changed
                z_movement = int(np.random.choice([-1, 0], 1, replace=False))

            # if all three movement is 0, rerun the movements
            if x_movement == 0 and y_movement == 0 and z_movement == 0:
                movement = False
            else:
                movement = True

        # create new position for the bacteria
        # directions
        x = position[0] + x_movement
        y = position[1] + y_movement
        z = position[2] + z_movement

        return (x,y,z)

    def _nextPosition3D(self, position: Tuple[int, int, int], surface: Surface, z_restriction: int) -> Tuple[int, int, int]:
        """
        This function return new position for 3D bacteria (currently next position is based on random movement of bacteria)
        position is based on the left-lower most part of the bacteria (ie. closest to the origin if the bacteria was in
        the first quadrant in a 3D cartesian coordinate system)
        """
        # set seed for random
        np.random.seed(self.seed)

        movement = False
        while not movement:
            # create variable called "movement" to determine which direction the bacteria will move in
            x_movement = int(np.random.choice([-1, 0, 1], 1, replace=False))
            y_movement = int(np.random.choice([-1, 0, 1], 1, replace=False))
            z_movement = int(np.random.choice([-1, 0, 1], 1, replace=False))

            # set restrictions (ie. position can't be off the surface)
            # x direction
            if position[0] == 0:
                x_movement = int(np.random.choice([0, 1], 1, replace=False))
            elif position[0] == surface.length - Bacteria3D.size[0]:
                x_movement = int(np.random.choice([-1, 0], 1, replace=False))

            # y direction
            if position[1] == 0:
                y_movement = int(np.random.choice([0, 1], 1, replace=False))
            elif position[1] == surface.width - Bacteria3D.size[1]:
                y_movement = int(np.random.choice([-1, 0], 1, replace=False))

            # z direction
            if position[2] == 0:
                z_movement = int(np.random.choice([0, 1], 1, replace=False))
            elif position[2] == z_restriction - Bacteria3D.size[2]: # the restriction for how far off the bacteria can be from the surface is arbitrary and can be changed
                z_movement = int(np.random.choice([-1, 0], 1, replace=False))

            # if all three movement is 0, rerun the movements
            if x_movement == 0 and y_movement == 0 and z_movement == 0:
                movement = False
            else:
                movement = True

        # create new position for the bacteria
        # directions
        x = position[0] + x_movement
        y = position[1] + y_movement
        z = position[2] + z_movement

        return (x,y,z)

