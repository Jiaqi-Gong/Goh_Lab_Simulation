"""
This file contains several function to generate next move of bacteria
"""
from typing import Tuple, Union
from FilmFile.Film import FilmSurface2D, FilmSurface3D
from BacteriaFile.Bacteria import Bacteria2D, Bacteria3D

import numpy as np
import math
from fractions import Fraction

# separate the bacteria movement for when the bacteria is 2D and when bacteria is 3D
# define an abstract class which will be used for the 2D and 3D bacteria class to inherit
class DistributionGenerator:
    """
    This class defines the boltzmann and poisson distribution to be used in the 2 child classes
    """
    # Type declaration
    Lambda: int

    def __init__(self, Lambda: int) -> None:
        self.Lambda = Lambda

    def _poisson(self) -> bool:
        """
        This function uses Poisson distribution to decide stuck or not
        return True for stuck
        :param: Lambda -> average number of events sticking
        """

        # lambda will depend on condition of surface and bacteria -> user will probably have to calculate it or take
        # a guess. Could also write a code to calculate this?

        # since we want to determine the probability for sticking on the surface once, the random variable X will be 1
        X = 1
        # equation for poisson distribution
        probability = ((self.Lambda**X)*(math.exp(-self.Lambda))) / (math.factorial(X))

        # return either true or false based on the probability of sticking
        stick = np.random.choice([True, False], 1, p=[probability, 1-probability])

        return stick


    def _boltzmann(self) -> bool:
        """
        This function uses Boltzmann distribution to decide stuck or not
        return True for stuck
        """

        # Look at the boltzmann distribution first and decide how to relate it to the probability of bacteria stuck
        # or not

        # values needed: Temperature, Energy,
        raise NotImplementedError

    def ratioConstant(self, *args):
        """
        This function takes in ratios and outputs a common multiplier which adds up the ratio to one
        Used for nextposition2D and nextposition3D function in the child classes
        """
        lst = []
        for i in args:
            lst.append(i)
        total = sum(lst)

        return Fraction(str(1 / total)).limit_denominator()


class BacteriaMovementGenerator2D(DistributionGenerator):
    """
    This class is a generator generate next move of 2D bacteria
    """

    # type declaration
    seed: int
    shape: str
    film2D: FilmSurface2D
    bacteria2D: Bacteria2D
    z_restriction: int

    def __init__(self, seed: int, shape: str, film2D: FilmSurface2D, bacteria2D: Bacteria2D, z_restriction: int, Lambda: int) -> None:
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


        # call the super class (DistributionGenerator) to inherit the __init__ of super class
        DistributionGenerator.__init__(self, Lambda)

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
            z_possibility = range(int(0 + self.bacteria2D.height/2), int(self.z_restriction - self.bacteria2D.height))

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

        # since we want the movement of the bacteria to be biased to move forward
        # probability to move forward
        p_f = 0.5
        # probability to stay still
        p_s = 0.25
        # probability to move backward
        p_b = 0.25

        # set up multipliers for the probability to add up to 1
        r_t = self.ratioConstant(p_f, p_s, p_b)
        r_fs = self.ratioConstant(p_f, p_s)
        # r_fb = self.ratioConstant(p_f, p_b)
        r_sb = self.ratioConstant(p_s, p_b)

        movement = False
        while not movement:
            # probability
            prob = r_t * np.array([p_b, p_s, p_f])

            # create variable called "movement" to determine which direction the bacteria will move in
            x_movement = int(np.random.choice([-1, 0, 1], 1, p=prob, replace=False))
            y_movement = int(np.random.choice([-1, 0, 1], 1, p=prob, replace=False))
            z_movement = int(np.random.choice([1, 0, -1], 1, p=prob, replace=False))

            # set restrictions (ie. position can't be off the surface)
            # x direction
            if position[0] == 0 + self.bacteria2D.length/2:
                # probability
                prob = r_fs * np.array([p_s, p_f])
                x_movement = int(np.random.choice([0, 1], 1, p=prob, replace=False))
            elif position[0] == self.film2D.length - self.bacteria2D.length/2:
                # probability
                prob = r_sb * np.array([p_b, p_s])
                x_movement = int(np.random.choice([-1, 0], 1, p=prob, replace=False))

            # y direction
            if position[1] == 0 + self.bacteria2D.width/2:
                # probability
                prob = r_fs * np.array([p_s, p_f])
                y_movement = int(np.random.choice([0, 1], 1, p=prob, replace=False))
            elif position[1] == self.film2D.width - self.bacteria2D.width/2:
                # probability
                prob = r_sb * np.array([p_b, p_s])
                y_movement = int(np.random.choice([-1, 0], 1, p=prob, replace=False))

            # z direction
            if position[2] == 0:
                # probability
                prob = r_fs * np.array([p_s, p_f])
                z_movement = int(np.random.choice([0, 1], 1, p=prob, replace=False))
            elif position[2] == self.z_restriction - self.bacteria2D.height: # the restriction for how far off the bacteria can be from the surface is arbitrary and can be changed
                # probability
                prob = r_sb * np.array([p_b, p_s])
                z_movement = int(np.random.choice([-1, 0], 1, p=prob, replace=False))

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

class BacteriaMovementGenerator3D(DistributionGenerator):
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
        if self.shape.upper() == "CUBOID" or self.shape.upper() == "SPHERE" or self.shape.upper() == "CYLINDER" \
                or self.shape.upper() == "ROD":
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
        This function return new position for 3D bacteria (next position is based on random movement of bacteria)
        position points at the center of the bacteria
        """
        # set seed for random
        np.random.seed(self.seed)

        # since we want the movement of the bacteria to be biased to move forward
        # probability to move forward
        p_f = 0.5
        # probability to stay still
        p_s = 0.25
        # probability to move backward
        p_b = 0.25

        # set up multipliers for the probability to add up to 1
        r_t = self.ratioConstant(p_f, p_s, p_b)
        r_fs = self.ratioConstant(p_f, p_s)
        # r_fb = self.ratioConstant(p_f, p_b)
        r_sb = self.ratioConstant(p_s, p_b)

        movement = False
        while not movement:
            # probability
            prob = r_t * np.array([p_b, p_s, p_f])

            # create variable called "movement" to determine which direction the bacteria will move in
            x_movement = int(np.random.choice([-1, 0, 1], 1, p=prob, replace=False))
            y_movement = int(np.random.choice([-1, 0, 1], 1, p=prob, replace=False))
            z_movement = int(np.random.choice([1, 0, -1], 1, p=prob, replace=False))

            # set restrictions (ie. position can't be off the film)
            # x direction
            if position[0] == 0 + self.bacteria3D.length/2:
                # probability
                prob = r_fs * np.array([p_s, p_f])
                x_movement = int(np.random.choice([0, 1], 1, p=prob, replace=False))
            elif position[0] == self.film3D.length - self.bacteria3D.length/2:
                # probability
                prob = r_sb * np.array([p_b, p_s])
                x_movement = int(np.random.choice([-1, 0], 1, p=prob, replace=False))

            # y direction
            if position[1] == 0 + self.bacteria3D.width/2:
                # probability
                prob = r_fs * np.array([p_s, p_f])
                y_movement = int(np.random.choice([0, 1], 1, p=prob, replace=False))
            elif position[1] == self.film3D.width - self.bacteria3D.width/2:
                # probability
                prob = r_sb * np.array([p_b, p_s])
                y_movement = int(np.random.choice([-1, 0], 1, p=prob, replace=False))

            # z direction
            if position[2] == 0 + self.bacteria3D.height/2:
                # probability
                prob = r_fs * np.array([p_s, p_f])
                z_movement = int(np.random.choice([0, 1], 1, p=prob, replace=False))
            elif position[2] == self.z_restriction - self.bacteria3D.height/2: # the restriction for how far off the bacteria can be from the surface is arbitrary and can be changed
                # probability
                prob = r_sb * np.array([p_b, p_s])
                z_movement = int(np.random.choice([-1, 0], 1, p=prob, replace=False))

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