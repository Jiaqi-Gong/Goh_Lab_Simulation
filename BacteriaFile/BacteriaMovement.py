"""
This file contains several function to generate next move of bacteria
"""
from typing import Tuple, Union

import numpy as np
import math
from fractions import Fraction


# define an abstract class which will be used for the 2D and 3D bacteria class to inherit
class BacteriaMovementGenerator:
    """
    This class is a generator generate next move of bacteria
    """
    # Type declaration
    z_restriction: int
    seed: int
    shape: str
    filmSize: Tuple[int, int, int]
    bacteriaSize: Tuple[int, int, int]

    def __init__(self, z_restriction: int, seed: int, bacteriaShape: str, filmSize: Tuple[int, int, int],
                 bacteriaSize: Tuple[int, int, int]):
        """
        The size of film and bacteria pass in is in format [length, width, height]
        """
        self.z_restriction = z_restriction
        self.seed = seed
        self.bacteriaShape = bacteriaShape
        self.filmSize = filmSize
        self.bacteriaSize = bacteriaSize

        # set seed for random
        np.random.seed(self.seed)

    # try with number 0.1 ... first then poisson

    def _simple(self, probability: float) -> bool:
        # check does probability set
        if probability is None:
            raise RuntimeError("Probability is not given")

        stick = np.random.choice([1, 0], 1, p=[probability, 1 - probability])

        return stick

    def _poisson(self, Lambda: float) -> bool:
        # Consider change to binomial
        """
        This function uses Poisson distribution to decide stuck or not
        return True for stuck
        :param: Lambda -> average number of events sticking
        """

        # lambda will depend on condition of surface and bacteria -> user will probably have to calculate it or take
        # a guess. Could also write a code to calculate this?

        # check does Lambda set
        if Lambda is None:
            raise RuntimeError("Lambda is not given")

        # since we want to determine the probability for sticking on the surface once, the random variable X will be 1
        X = 1
        # equation for poisson distribution
        probability = ((Lambda ** X) * (math.exp(-Lambda))) / (math.factorial(X))

        # return either true or false based on the probability of sticking
        stick = np.random.choice([1, 0], 1, p=[probability, 1 - probability])

        return stick

    def _boltzmann(self, temperature: float, energy: float) -> bool:
        """
        This function uses Boltzmann distribution to decide stuck or not
        return True for stuck
        """
        # energy

        # Look at the boltzmann distribution first and decide how to relate it to the probability of bacteria stuck
        # or not

        # values needed: Temperature, Energy,
        if temperature is None or energy is None:
            raise RuntimeError("Temperature or energy is not set")

        raise NotImplementedError

    def _ratioConstant(self, *args) -> int:
        """
        This function takes in ratios and outputs a common multiplier which adds up the ratio to one
        Used for _nextPosition function
        """
        lst = []
        for i in args:
            lst.append(i)
        total = sum(lst)

        return int(Fraction(str(1 / total)).limit_denominator())

    def initPosition(self) -> Tuple[int, int, int]:
        """
        This function is used to generate the init position for 3D bacteria
        position points at the center of the bacteria
        """
        # the initial position of the bacteria will be randomly placed on the film
        # however, need to set restrictions on where the bacteria will be placed since bacteria can't go off the surface
        # for 3D bacteria

        if self.bacteriaShape.upper() in ["CUBOID", "SPHERE", "CYLINDER", "ROD"]:
            # set upperbound and lowerbound possibilities for the position of x,y,z
            x_possibility = range(int(0 + self.bacteriaSize[0] / 2),
                                  int(self.filmSize[0] - self.bacteriaSize[0] / 2))
            y_possibility = range(int(0 + self.bacteriaSize[1] / 2),
                                  int(self.filmSize[1] - self.bacteriaSize[1] / 2))
            z_possibility = range(int(0 + self.bacteriaSize[2] / 2),
                                  int(self.z_restriction - self.bacteriaSize[2] / 2))
        else:
            raise RuntimeError("Unknown bacteria shape")

        # choose a random coordinate for the bacteria to start its position in
        x = np.random.choice(x_possibility, 1, replace=False)
        y = np.random.choice(y_possibility, 1, replace=False)
        z = np.random.choice(z_possibility, 1, replace=False)

        return (x, y, z)

    def nextPosition(self, probabilityType: str, position: Tuple[int, int, int], Lambda: float = None,
                     temperature: float = None, energy: float = None, probability: float = None) \
            -> Union[bool, Tuple[int, int, int]]:
        """
        This function take in probability type, position
        return False if this bacteria is stuck
        return a tuple contain new position if not stuck
        """

        # call appropriate probability function to decide stuck or not
        if probabilityType == "SIMPLE":
            result = self._simple(probability)
        elif probabilityType == "POISSON":
            result = self._poisson(Lambda)
        elif probabilityType == "BOLTZMANN":
            result = self._boltzmann(temperature, energy)
        else:
            raise RuntimeError("Unknown probability type")

        # check stuck or not
        # if stuck, result == 1, return false
        if result == 1:
            return False
        else:
            return self._nextPositionHelper(position)

    def unstuckBacteria(self, probabilityType: str, probability: float) -> bool:
        """
        This function is used to decide stuck bacteria free or not
        If free, return True
        """

        # call appropriate probability function to decide free or not
        if probabilityType == "SIMPLE":
            result = self._simple(probability)
        else:
            raise RuntimeError("Unknown probability type")

        # check free or not
        # if free, result == 1, return True
        if result == 1:
            return True
        else:
            return False



    def _nextPositionHelper(self, position: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        This function return new position for 3D bacteria (next position is based on random movement of bacteria)
        position points at the center of the bacteria
        """
        # since we want the movement of the bacteria to be biased to move forward
        # probability to move forward
        p_f = 0.5
        # probability to stay still
        p_s = 0.25
        # probability to move backward
        p_b = 0.25

        # set up multipliers for the probability to add up to 1
        r_t = self._ratioConstant(p_f, p_s, p_b)
        r_fs = self._ratioConstant(p_f, p_s)
        r_sb = self._ratioConstant(p_s, p_b)

        while True:
            # probability
            prob = r_t * np.array([p_b, p_s, p_f])

            # create variable called "movement" to determine which direction the bacteria will move in
            x_movement = int(np.random.choice([-1, 0, 1], 1, p=prob, replace=False))
            y_movement = int(np.random.choice([-1, 0, 1], 1, p=prob, replace=False))
            z_movement = int(np.random.choice([1, 0, -1], 1, p=prob, replace=False))

            # set restrictions (ie. position can't be off the film)
            # x direction
            if position[0] == 0 + self.bacteriaSize[0] / 2:
                # probability
                prob = r_fs * np.array([p_s, p_f])
                prob /= prob.sum()
                x_movement = int(np.random.choice([0, 1], 1, p=prob, replace=False))
            elif position[0] == self.filmSize[0] - self.bacteriaSize[0] / 2:
                # probability
                prob = r_sb * np.array([p_b, p_s])
                prob /= prob.sum()
                x_movement = int(np.random.choice([-1, 0], 1, p=prob, replace=False))

            # y direction
            if position[1] == 0 + self.bacteriaSize[1] / 2:
                # probability
                prob = r_fs * np.array([p_s, p_f])
                prob /= prob.sum()
                y_movement = int(np.random.choice([0, 1], 1, p=prob, replace=False))
            elif position[1] == self.filmSize[1] - self.bacteriaSize[1] / 2:
                # probability
                prob = r_sb * np.array([p_b, p_s])
                prob /= prob.sum()
                y_movement = int(np.random.choice([-1, 0], 1, p=prob, replace=False))

            # z direction
            if position[2] == 0 + self.bacteriaSize[2] / 2:
                # probability
                prob = r_fs * np.array([p_s, p_f])
                prob /= prob.sum()
                z_movement = int(np.random.choice([0, 1], 1, p=prob, replace=False))
            elif position[2] == self.z_restriction - self.bacteriaSize[2] / 2:  # the restriction for how far off
                # the bacteria can be from the surface is arbitrary and can be changed
                # probability
                prob = r_sb * np.array([p_b, p_s])
                prob /= prob.sum()
                z_movement = int(np.random.choice([-1, 0], 1, p=prob, replace=False))

            # if all three movement is 0, rerun the movements
            if x_movement != 0 and y_movement != 0 and z_movement != 0:
                break

        # create new position for the bacteria
        # directions
        x = position[0] + x_movement
        y = position[1] + y_movement
        z = position[2] + z_movement

        return (x, y, z)
