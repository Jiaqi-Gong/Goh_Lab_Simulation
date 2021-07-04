"""
This file contains several function to generate next move of bacteria
"""
from typing import Tuple, Union
from FilmFile.Film import FilmSurface2D, FilmSurface3D
from BacteriaFile.Bacteria import Bacteria2D, Bacteria3D

import numpy as np

# separate the bacteria movement for when the bacteria is 2D and when bacteria is 3D
# define an abstract class which will be used for the 2D and 3D bacteria class to inherit
class BacteriaMovementGenerator:
    """
    This class defines the boltzmann and poisson distribution to be used in the 2 child classes
    """
    def __init__(self) -> None:
        # implement later
        raise NotImplementedError

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


class BacteriaMovementGenerator2D(BacteriaMovementGenerator):
    """
    This class is a generator generate next move of 2D bacteria
    """

    # type declaration
    seed: int
    shape: str
    film2D: FilmSurface2D
    bacteria2D: Bacteria2D
    z_restriction: int

    def __init__(self, seed: int, shape: str, film2D: FilmSurface2D, bacteria2D: Bacteria2D, z_restriction: int) -> None:
        """
        Init the movement generator
        :param: seed for random, if using same seed can repeat the simulation
        :param: shape of the bacteria
        :param: film2D -> gets arguments from film2D class
        :param: bacteria2D -> gets arguments from bacteria2D class
        :param: z_restriction -> sets restriction on how far from the film the bacteria can travel

        """
        self.seed = seed
        self.shape = shape
        self.film2D = film2D
        self.bacteria2D = bacteria2D
        self.z_restriction = z_restriction

    def initPosition2D(self) -> Tuple[int, int, int]:
        """
        This function is used to generate the init position for 2D bacteria
        position points at the center of the bacteria
        """
        # the initial position of the bacteria will be randomly placed on the film
        # however, need to set restrictions on where the bacteria will be placed since bacteria can't go off the surface
        # for 2D bacteria
        if self.shape.upper() == "RECTANGLE":
            x_possibility = range(int(0 + self.bacteria2D.length/2), int(self.film2D.length - self.bacteria2D.length/2))
            y_possibility = range(int(0 + self.bacteria2D.width/2), int(self.film2D.width - self.bacteria2D.width/2))
            z_possibility = range(int(0 + self.bacteria2D.height/2), int(self.z_restriction - self.bacteria2D.height/2))

        # choose a random coordinate for the bacteria to start in
        x = np.random.choice(x_possibility, 1, replace=False)
        y = np.random.choice(y_possibility, 1, replace=False)
        z = np.random.choice(z_possibility, 1, replace=False)

        return (x,y,z)



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
            return self._nextPosition2D(position)

    def _nextPosition2D(self, position: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        This function return new position for 2D bacteria (currently next position is based on random movement of bacteria)
        position points at the center of the bacteria
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
            if position[0] == 0 + self.bacteria2D.length/2:
                x_movement = int(np.random.choice([0, 1], 1, replace=False))
            elif position[0] == self.film2D.length - self.bacteria2D.length/2:
                x_movement = int(np.random.choice([-1, 0], 1, replace=False))

            # y direction
            if position[1] == 0 + self.bacteria2D.width/2:
                y_movement = int(np.random.choice([0, 1], 1, replace=False))
            elif position[1] == self.film2D.width - self.bacteria2D.width/2:
                y_movement = int(np.random.choice([-1, 0], 1, replace=False))

            # z direction
            if position[2] == 0:
                z_movement = int(np.random.choice([0, 1], 1, replace=False))
            elif position[2] == self.z_restriction - self.bacteria2D.height: # the restriction for how far off the bacteria can be from the surface is arbitrary and can be changed
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

class BacteriaMovementGenerator3D(BacteriaMovementGenerator):
    """
    This class is a generator generate next move of 3D bacteria
    """

    # type declaration
    seed: int
    shape: str
    film3D: FilmSurface3D
    bacteria3D: Bacteria3D
    z_restriction: int

    def __init__(self, seed: int, shape: str, film3D: FilmSurface3D, bacteria3D: Bacteria3D, z_restriction: int) -> None:
        """
        Init the movement generator
        :param: seed for random, if using same seed can repeat the simulation
        :param: shape of the bacteria
        :param: film3D -> gets arguments from film3D class
        :param: bacteria3D -> gets arguments from bacteria3D class
        :param: z_restriction -> sets restriction on how far from the film the bacteria can travel
        """
        self.seed = seed
        self.shape = shape
        self.film3D = film3D
        self.bacteria3D = bacteria3D
        self.z_restriction = z_restriction

    def initPosition3D(self) -> Tuple[int, int, int]:
        """
        This function is used to generate the init position for 3D bacteria
        position points at the center of the bacteria
        """
        # the initial position of the bacteria will be randomly placed on the film
        # however, need to set restrictions on where the bacteria will be placed since bacteria can't go off the surface
        # for 3D bacteria
        if self.shape.upper() == "CUBOID":
            # set upperbound and lowerbound possibilites for the position of x,y,z
            x_possibility = range(int(0 + self.bacteria3D.length/2), int(self.film3D.length - self.bacteria3D.length/2))
            y_possibility = range(int(0 + self.bacteria3D.width/2), int(self.film3D.width - self.bacteria3D.width/2))
            z_possibility = range(int(0 + self.bacteria3D.height/2), int(self.z_restriction - self.bacteria3D.height/2))

        # choose a random coordinate for the bacteria to start its position in
        x = np.random.choice(x_possibility, 1, replace=False)
        y = np.random.choice(y_possibility, 1, replace=False)
        z = np.random.choice(z_possibility, 1, replace=False)

        return (x,y,z)

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
            return self._nextPosition3D(position)


    def _nextPosition3D(self, position: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        This function return new position for 3D bacteria (currently next position is based on random movement of bacteria)
        position points at the center of the bacteria
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
            if position[0] == 0 + self.bacteria3D.length/2:
                x_movement = int(np.random.choice([0, 1], 1, replace=False))
            elif position[0] == self.film3D.length - self.bacteria3D.length/2:
                x_movement = int(np.random.choice([-1, 0], 1, replace=False))

            # y direction
            if position[1] == 0 + self.bacteria3D.width/2:
                y_movement = int(np.random.choice([0, 1], 1, replace=False))
            elif position[1] == self.film3D.width - self.bacteria3D.width/2:
                y_movement = int(np.random.choice([-1, 0], 1, replace=False))

            # z direction
            if position[2] == 0 + self.bacteria3D.height/2:
                z_movement = int(np.random.choice([0, 1], 1, replace=False))
            elif position[2] == self.z_restriction - self.bacteria3D.height/2: # the restriction for how far off the bacteria can be from the surface is arbitrary and can be changed
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