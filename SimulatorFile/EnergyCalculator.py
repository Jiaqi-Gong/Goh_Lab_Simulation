"""
This file contains method to calculate the energy of the surface
"""
from typing import Tuple, List
from numpy import ndarray
from ExternalIO import *


def _dotInteract2D(intervalX: int, intervalY: int, film: ndarray, bacteria: ndarray) -> \
        Tuple[int, int, int, int, int, int, int]:
    """
    Do the simulation, scan whole film surface with bacteria
    The energy calculate only between bacteria surface and the film surface directly under the bacteria
    This code is copy from the old code with minor name change
    """
    writeLog("This is _dotInteract2D in Simulation")
    showMessage("Start to interact ......")
    writeLog("intervalX is: {}, intervalY is: {}, film is: {}, bacteria is: {}".format(
        intervalX, intervalY, film, bacteria))

    # show image of whole film and bacteria
    visPlot(film[0], "whole_film")
    visPlot(bacteria[0], "whole_bacteria")

    # shape of the film
    film_shape = film.shape

    # shape of bacteria
    bact_shape = bacteria.shape

    # set the range
    range_x = np.arange(0, film_shape[1], intervalX)
    range_y = np.arange(0, film_shape[2], intervalY)

    writeLog("shape is : {}, range_x is: {}, range_y is: {}".format(film_shape, range_x, range_y))

    # init some variable
    # randomly, just not negative
    min_energy = 999999
    min_charge = 999999
    min_energy_charge = 999999
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
            x_boundary = bact_shape[1] + x
            y_boundary = bact_shape[2] + y

            writeLog("x_boundary is: {}, y_boundary is: {}, film_shape is:{}, bacteria shape is: {} ".format(
                x_boundary, y_boundary, film_shape, bact_shape))
            writeLog("Range check: x_boundary > film_shape[1] - bact_shape[1] is :{}, y_boundary > "
                     "film_shape[2] - bact_shape[2] is: {} ".format(x_boundary > film_shape[1] - bact_shape[1],
                                                                    y_boundary > film_shape[2] - bact_shape[2]))

            # check if bacteria surface is exceed range of film surface
            if x_boundary > film_shape[0] or y_boundary > film_shape[1]:
                # if exceed the surface, go to next iteration
                writeLog("outside the range, continue")
                continue

            # do the calculation

            # change the corresponding film surface into 1D
            film_use = film[x: x_boundary, y: y_boundary]
            film_1D = np.reshape(film_use, (-1,))

            # calculate energy, uses electrostatic energy formula, assuming that r = 1
            # WARNING: r should be change based on the height difference between film and bacteria in future
            writeLog(["This is surface and film uses to calcualte energy", film_1D, bacteria_1D])
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


def _cutoffInteract2D(intervalX: int, intervalY: int, film: ndarray, bacteria: ndarray) -> \
        Tuple[int, int, int, int, int, int, int]:
    """
    Do the simulation, scan whole film surface with bacteria
    The energy calculate only between bacteria surface and the film surface directly under the bacteria
    This code is copy from the old code with minor name change
    """
    writeLog("This is _cutoffInteract2D in Simulation")
    showMessage("Start to interact ......")
    writeLog("intervalX is: {}, intervalY is: {}, film is: {}, bacteria is: {}".format(
        intervalX, intervalY, film, bacteria))

    # shape of the bacteria
    shape = film.shape

    # set the range
    range_x = np.arange(0, shape[0], intervalX)
    range_y = np.arange(0, shape[1], intervalY)

    writeLog("shape is : {}, range_x is: {}, range_y is: {}".format(shape, range_x, range_y))

    # init some variable
    # randomly, just not negative
    min_energy = 999999
    min_charge = 999999
    min_energy_charge = 999999
    min_charge_x = 0
    min_charge_y = 0
    min_x = -1
    min_y = -1

    # change ndarray to tuple
    filmTuple = _ndarrayToTuple(film, len(film.shape))
    bacteriaTuple = _ndarrayToTuple(bacteria, len(bacteria.shape))

    # select proper area on the film to interact with bacteria

    raise NotImplementedError


def _cutoffInteract3D(intervalX: int, intervalY: int, film: ndarray, bacteria: ndarray) -> \
        Tuple[int, int, int, int, int, int, int]:
    """
    Do the simulation, scan whole film surface with bacteria
    The energy calculate only between bacteria surface and the film surface directly under the bacteria
    This code is copy from the old code with minor name change
    """
    raise NotImplementedError


def _ndarrayToTuple(arrayList: ndarray, dimension: int) -> List[List[Tuple[int, int, int, int]]]:
    """
    This function takes in a ndarray and rephase this array into a nested list
    Each tuple in list represent (x_coordinate, y_coordinate, z_coordinate, charge)
    """
    writeLog("This is ndarrayToTuple")
    writeLog(arrayList)

    # init the list
    tupleList = []

    # depends on the dimension rephrase ndarray
    for x in range(len(arrayList)):
        temp = []
        for y in range(len(arrayList[x])):
            if dimension == 2:
                z = 3
                # Note, for 2D, the height of bacteria is fixed to 3, which means z-coordinate is 3
                position = (x, y, z, arrayList[x][y])
                temp.append(position)

            elif dimension == 3:
                raise NotImplementedError
            else:
                raise RuntimeError("Unknown dimension")

        tupleList.append(temp)

    return tupleList
