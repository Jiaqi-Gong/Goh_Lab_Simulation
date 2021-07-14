"""
This file contains method to calculate the energy of the surface
"""


from typing import Tuple, List, Union
from numpy import ndarray
from ExternalIO import *

COULOMB_CONSTANT = 8.99


def interact2D(interactType: str, intervalX: int, intervalY: int, film: ndarray, bacteria: ndarray, currIter: int,
               cutoff: int) -> Tuple[Union[float, int], int, int, Union[float, int], Union[float, int], int, int]:
    """
    Do the simulation, scan whole film surface with bacteria for 2D
    """
    writeLog("This is interact2D in Simulation")
    showMessage("Start to interact ......")
    writeLog("intervalX is: {}, intervalY is: {}, film is: {}, bacteria is: {}".format(
        intervalX, intervalY, film, bacteria))

    # if it's cutoff, change format
    if interactType.upper() in ["CUTOFF", "CUT-OFF"]:
        # change ndarray to tuple
        filmTuple = _ndarrayToTuple(film, 2, isFilm=True)
        bacteriaTuple = _ndarrayToTuple(bacteria, 2, isBacteria=True)

    # change the format of film and bacteria
    film = film[0]
    bacteria = bacteria[0]

    # show image of whole film and bacteria
    visPlot(film, "whole_film_{}".format(currIter))
    visPlot(bacteria, "whole_bacteria_{}".format(currIter))

    # shape of the film
    film_shape = film.shape

    # shape of bacteria
    bact_shape = bacteria.shape

    # set the range
    range_x = np.arange(0, film_shape[0], intervalX)
    range_y = np.arange(0, film_shape[1], intervalY)

    writeLog("shape is : {}, range_x is: {}, range_y is: {}".format(film_shape, range_x, range_y))

    # init some variable
    # randomly, just not negative
    min_energy = float("INF")
    min_charge = float("INF")
    min_energy_charge = float("INF")
    min_charge_x = 0
    min_charge_y = 0
    min_x = -1
    min_y = -1
    min_film = []

    # change the bacteria surface into 1D
    bacteria_1D = np.reshape(bacteria, (-1))

    # for debug, delete later
    all_energy = []

    # scan through the surface and make calculation
    for x in range_x:
        for y in range_y:
            # set the x boundary and y boundary
            x_boundary = bact_shape[0] + x
            y_boundary = bact_shape[1] + y

            writeLog("x_boundary is: {}, y_boundary is: {}, film_shape is:{}, bacteria shape is: {} ".format(
                x_boundary, y_boundary, film_shape, bact_shape))

            # check if bacteria surface is exceed range of film surface
            if x_boundary > film_shape[0] or y_boundary > film_shape[1]:
                # if exceed the surface, go to next iteration
                writeLog("outside the range, continue")
                continue

            # change the corresponding film surface into 1D
            film_use = film[x: x_boundary, y: y_boundary]
            film_1D = np.reshape(film_use, (-1,))

            # do the energy calculation based on the interact type
            # dot interact
            if interactType.upper() == "DOT":
                # calculate energy, uses electrostatic energy formula, assuming that r = 1
                # WARNING: r should be change based on the height difference between film and bacteria in future
                writeLog(["This is surface and film uses to calculate energy", film_1D, bacteria_1D])
                writeLog("WARNING: r should be change based on the height difference between film and bacteria in "
                         "future")
                energy = np.dot(film_1D, bacteria_1D)

            # cutoff interact
            elif interactType.upper() in ["CUTOFF", "CUT-OFF"]:
                # calculate energy by using cutoff calculation function

                # prepare bacteria tuple uses
                bacteriaTuple_use = bacteriaTuple

                # prepare film tuple use, the size of film is bigger than the size of bacteria due to cutoff value
                filmTuple_use = []
                for z_pos in range(len(filmTuple)):
                    temp1 = []
                    for y_pos in range(max(y - cutoff, 0), min(y_boundary + cutoff, len(filmTuple[z_pos]))):
                        temp2 = []
                        for x_pos in range(max(x - cutoff, 0), min(x_boundary + cutoff, len(filmTuple[z_pos][y_pos]))):
                            temp2.append(filmTuple[0][y_pos][x_pos])
                        temp1.append(temp2)
                    filmTuple_use.append(temp1)

                # call function to calculate energy
                showMessage("Start to calculate cutoff energy, this step is slow")
                energy = _twoPointEnergy(filmTuple_use, bacteriaTuple_use, cutoff)

                all_energy.append(energy)

            else:
                raise RuntimeError("Unknown interact type")

            # count and unique
            unique, counts = np.unique(film_use, return_counts=True)

            # record all variables
            writeLog("film_use is: {}, film_1D is: {}, energy is: {}, unique is: {}, counts is: {}".format(
                film_use, film_1D, energy, unique, counts))

            # check the calculation result and change corresponding value
            charge = 0
            for i in range(len(unique)):
                if unique[i] == -1:
                    charge -= counts[i]
                elif unique[i] == 1:
                    charge += counts[i]
                else:
                    charge += 0

            # below is the way of calculating charge in the old code, however for now we have 0 on the surface while
            # in the old code only -1 nad 1 on the surface
            # if len(unique) == 1:
            #     if unique[0] == -1:
            #         charge = -counts[0]
            #     else:
            #         charge = counts[0]
            # elif unique[0] == -1:
            #     charge = -counts[0] + counts[1]
            # elif unique[0] == 1:
            #     charge = counts[0] - counts[1]
            # else:
            #     showMessage("This is an error, parameter unique is not -1 or 1, it is: {}".format(unique))
            #     writeLog(__dict__)
            #     raise RuntimeError("Variable 'charge' in _interact2D not init, caused by the error in unique")

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
                min_film = film_use[:]

    # save the result
    result = (min_energy, min_x, min_y, min_energy_charge, min_charge, min_charge_x, min_charge_y)

    # print the min_film
    visPlot(min_film, "Film at minimum_{}".format(currIter))

    # for debug, delete later
    # print(all_energy)

    showMessage("Interact done")
    writeLog(result)

    return result


def interact3D(interactType: str, intervalX: int, intervalY: int, film: ndarray, bacteria: ndarray, currIter: int,
               cutoff: int) -> Tuple[Union[float, int], int, int, Union[float, int], Union[float, int], int, int]:
    """
    Do the simulation, scan whole film surface with bacteria for 3D
    """


def _ndarrayToTuple(arrayList: ndarray, dimension: int, isFilm: bool = False, isBacteria: bool = False) -> \
        List[List[List[Tuple[int, int, int, int]]]]:
    """
    This function takes in a ndarray and rephase this array into a nested list
    Each tuple in list represent (x_coordinate, y_coordinate, z_coordinate, charge)
    """
    writeLog("This is ndarrayToTuple")
    writeLog(arrayList)

    # based on dimension, call appropriate function
    if dimension == 2:
        tupleList = _ndarrayToTuple2D(arrayList, isFilm, isBacteria)
    elif dimension == 3:
        tupleList = _ndarrayToTuple3D(arrayList)
    else:
        raise RuntimeError("Unknown dimension")

    return tupleList


def _ndarrayToTuple2D(arrayList: ndarray, isFilm: bool, isBacteria: bool) -> \
        List[List[List[Tuple[int, int, int, int]]]]:
    """
    This is a helper function to rephrase 2D ndarray into tuple format
    """
    # init the list
    tupleList = []

    # based on it's film or bacteria, set appropriate height value
    if isFilm:
        height = 0
    elif isBacteria:
        height = 3
    else:
        raise RuntimeError("Unknown ndarray pass in")

    # rephrase ndarray to tuple
    for z in range(len(arrayList)):
        temp1 = []
        for y in range(len(arrayList[z])):
            temp2 = []
            for x in range(len(arrayList[z][y])):
                position = (x, y, height, arrayList[z][y][x])
                temp2.append(position)
            temp1.append(temp2)
        tupleList.append(temp1)

    return tupleList


def _ndarrayToTuple3D(arrayList: ndarray) -> List[List[List[Tuple[int, int, int, int]]]]:
    """
    This is a helper function to rephrase 3D ndarray into tuple format
    """
    # init the list
    tupleList = []

    # rephrase ndarray to tuple
    for z in range(len(arrayList)):
        temp1 = []
        for y in range(len(arrayList[z])):
            temp2 = []
            for x in range(len(arrayList[z][y])):
                position = (x, y, z, arrayList[z][y][x])
                temp2.append(position)
            temp1.append(temp2)
        tupleList.append(temp1)

    return tupleList


def _twoPointEnergy(film: List[List[List[Tuple[int, int, int, int]]]],
                    bacteria: List[List[List[Tuple[int, int, int, int]]]],
                    cutoff: int) -> float:
    """
    This function takes in two point list in tuple format and calculate the energy between every tep points based
    on Coulomb's law
    If the distance excess the cutoff, energy is 0
    """
    # init variable uses
    total_energy = 0

    # loop the point on the bacteria
    for z in range(len(bacteria)):
        for y in range(len(bacteria[z])):
            for x in range(len(bacteria[z][y])):
                point1 = list(bacteria[z][y][x])

                # generate the point on the surface should interact with this point on the bacteria based on the
                # position of current bacteria point and cutoff value
                # range on x direction
                film_x_start = max(0, point1[2] - cutoff)
                film_x_end = min(len(film[z][y]), point1[2] + cutoff)

                # range on z direction
                film_y_start = max(0, point1[1] - cutoff)
                film_y_end = min(len(film[z]), point1[1] + cutoff)

                # get film needed
                film_list = []

                for film_z in range(len(film)):
                    for film_y in range(film_y_start, film_y_end):
                        for film_x in range(film_x_start, film_x_end):
                            point2 = list(film[film_z][film_y][film_x])

                            film_list.append(point2)

                # calculate distance between current bacteria point and film_list points
                for point2 in film_list:
                    distance = ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2 +
                                (point1[2] - point2[2]) ** 2) ** 0.5

                    # if distance bigger than cutoff, ignore it
                    if distance > cutoff:
                        # print("distance is {}, cutoff is {}".format(distance, cutoff))
                        total_energy += 0
                    else:
                        charge1 = point1[3]
                        charge2 = point2[3]
                        energy = COULOMB_CONSTANT * charge1 * charge2 / distance

                        total_energy += energy

    return total_energy
