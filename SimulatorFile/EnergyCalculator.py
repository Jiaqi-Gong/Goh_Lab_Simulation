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
    the format of ndarray pass to simulator is in format (z,y,x), when make np.ones(1,2,3)
    which means 1 z layer, 2 y layer and 3 x layer.
    """
    writeLog("This is interact2D in Simulation")
    showMessage("Start to interact ......")
    writeLog("intervalX is: {}, intervalY is: {}, film is: {}, bacteria is: {}".format(
        intervalX, intervalY, film, bacteria))

    # if it's cutoff, change format
    if interactType.upper() in ["CUTOFF", "CUT-OFF"]:
        # change ndarray to dictionary
        filmDict = _ndarrayToDict(film)
        bactDict = _ndarrayToDict(bacteria, isBacteria=True)

    # change the format of film and bacteria
    film = film[0]
    bacteria = bacteria[0]

    # show image of whole film and bacteria
    # visPlot(film, "whole_film_2D_{}".format(currIter))
    visPlot(bacteria, "whole_bacteria_2D_{}".format(currIter))

    # shape of the film
    film_shape = film.shape

    # shape of bacteria
    bact_shape = bacteria.shape

    # set the range
    range_x = np.arange(0, film_shape[1], intervalX)
    range_y = np.arange(0, film_shape[0], intervalY)

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

    # for future multiprocess, init a dict to save value
    # divide x to three parts and divide y to three parts
    # totally 9 subprocess to speed up the calculation
    # key is minimum energy,
    # value is a tuple store the result like (min_energy, min_x, min_y, min_energy_charge, min_charge, min_charge_x, min_charge_y)
    # all process save the result in the dict
    # then loop dict.keys() to find the minimum energy and corresponding result
    # extract below function out as a separate function to do multi process

    # init a result dictionary
    result_dict = {}

    # scan through the surface and make calculation
    if interactType.upper() in ["CUTOFF", "CUT-OFF"]:
        showMessage("Start to calculate cutoff energy, this step is slow")
    else:
        showMessage("Start to calculate energy in dot type")

    for x in range_x:
        for y in range_y:
            # set the x boundary and y boundary
            x_boundary = bact_shape[0] + x
            y_boundary = bact_shape[1] + y

            writeLog("x_boundary is: {}, y_boundary is: {}, film_shape is:{}, bacteria shape is: {} ".format(
                x_boundary, y_boundary, film_shape, bact_shape))

            # check if bacteria surface is exceed range of film surface
            if x_boundary > film_shape[1] or y_boundary > film_shape[0]:
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

                energy = np.dot(film_1D, bacteria_1D)

            # cutoff interact
            elif interactType.upper() in ["CUTOFF", "CUT-OFF"]:
                # calculate energy by using cutoff calculation function

                # get the start point on the film
                startPoint = (x, y)

                # call function to calculate energy
                energy = _twoPointEnergy(filmDict, bactDict, cutoff, startPoint, (film_shape[1], film_shape[0]))

                # all_energy.append(energy)

            else:
                raise RuntimeError("Unknown interact type")

            # count and unique
            unique, counts = np.unique(film_use, return_counts=True)

            # record all variables
            # writeLog("film_use is: {}, film_1D is: {}, energy is: {}, unique is: {}, counts is: {}".format(
            #     film_use, film_1D, energy, unique, counts))

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

    writeLog("Result in interact 2D is: {}".format(result))

    # print the min_film
    # visPlot(min_film, "Film at minimum_{}".format(currIter))

    # for debug, delete later
    # print(all_energy)

    showMessage("Interact done")
    writeLog(result)

    return result


def interact3D(interactType: str, intervalX: int, intervalY: int, film: ndarray, bacteria: ndarray, currIter: int,
               cutoff: int) -> Tuple[Union[float, int], int, int, Union[float, int], Union[float, int], int, int]:
    """
    Do the simulation, scan whole film surface with bacteria for 3D
    the format of ndarray pass to simulator is in format (z,y,x), when make np.ones(1,2,3)
    which means 1 z layer, 2 y layer and 3 x layer.
    """
    writeLog("This is interact3D in Simulation")
    showMessage("Start to interact ......")
    writeLog("intervalX is: {}, intervalY is: {}, film is: {}, bacteria is: {}".format(
        intervalX, intervalY, film, bacteria))

    # change ndarray to dictionary
    filmDict = _ndarrayToDict(film)
    bactDict = _ndarrayToDict(bacteria, isBacteria=True)

    # show image of whole film and bacteria
    # visPlot(film, "whole_film_3D_{}".format(currIter))
    # visPlot(bacteria, "whole_bacteria_3D_{}".format(currIter))

    # shape of the film
    film_shape = film.shape

    # shape of bacteria
    bact_shape = bacteria.shape

    # set the range
    range_x = np.arange(0, film_shape[2], intervalX)
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

    # calculate the energy
    # scan through the surface and make calculation
    for x in range_x:
        for y in range_y:
            # init film use and energy
            film_use = []
            energy = 0

            # set the x boundary and y boundary
            x_boundary = bact_shape[2] + x
            y_boundary = bact_shape[1] + y

            writeLog("x_boundary is: {}, y_boundary is: {}, film_shape is:{}, bacteria shape is: {} ".format(
                x_boundary, y_boundary, film_shape, bact_shape))

            # check if bacteria surface is exceed range of film surface
            if x_boundary > film_shape[2] or y_boundary > film_shape[1]:
                # if exceed the surface, go to next iteration
                writeLog("outside the range, continue")
                continue

            # do the energy calculation based on the interact type
            # dot interact
            if interactType.upper() == "DOT":
                # calculate energy, uses electrostatic energy formula
                for i in range(x, x_boundary):
                    for j in range(y, y_boundary):
                        # get the x,y position of bacteria and film
                        film_pos = (i, j)
                        bact_pos = (i - x, j - y)

                        # get the distance between two charge, only consider the lower surface of bacteria
                        writeLog("Only consider the lower surface of bacteria for now, may change in the future")
                        distance = bactDict[bact_pos][0][0] - filmDict[film_pos][0][0]

                        # get charge on film and bacteria
                        film_charge = filmDict[film_pos][0][1]
                        bact_charge = bactDict[bact_pos][0][1]

                        # save this charge to film_use
                        film_use.append(film_charge)

                        # calculate the energy
                        cur_energy = film_charge * bact_charge / distance
                        energy += cur_energy

            # cutoff interact
            elif interactType.upper() in ["CUTOFF", "CUT-OFF"]:
                # calculate energy by using cutoff calculation function
                raise NotImplementedError

            else:
                raise RuntimeError("Unknown interact type")

            # count and unique
            unique, counts = np.unique(film_use, return_counts=True)

            # record all variables
            writeLog("film_use is: {}, energy is: {}, unique is: {}, counts is: {}".format(
                film_use, energy, unique, counts))

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
    # visPlot(min_film, "Film at minimum_{}".format(currIter))

    # for debug, delete later
    # print(all_energy)

    showMessage("Interact done")
    writeLog(result)

    return result


def _ndarrayToDict(arrayList: ndarray, isFilm: bool = None, isBacteria: bool = None) -> \
        Dict[Tuple[int, int], List[Tuple[int, int]]]:
    """
    This function takes in a ndarray and reshape this array into a dictionary
    Key is a tuple represent (x, y), value is a list [(z, charge)], for 2D length of value is 1, for 3D it can be various
    """
    # init the result
    result = {}

    # init the position at z direction
    z_height = 0

    if isBacteria:
        z_height += 3

    # loop whole dictionary
    for z in range(len(arrayList)):
        for y in range(len(arrayList[z])):
            for x in range(len(arrayList[z][y])):
                # get charge
                charge = arrayList[z][y][x]

                # get key
                key = (x, y)

                # get value
                value = (z + z_height, charge)

                # add into the result dictionary
                if key not in result:
                    result[key] = [value]
                else:
                    result[key].append(value)

    # sort all values in the order of value of z
    for i in result.keys():
        result[i].sort()

    return result


# def _ndarrayToTuple(arrayList: ndarray, dimension: int, isFilm: bool = False, isBacteria: bool = False) -> \
#         List[List[List[Tuple[int, int, int, int]]]]:
#     """
#     This function takes in a ndarray and reshape this array into a nested list
#     Each tuple in list represent (x_coordinate, y_coordinate, z_coordinate, charge)
#     """
#     writeLog("This is ndarrayToTuple")
#     writeLog(arrayList)
#
#     # based on dimension, call appropriate function
#     if dimension == 2:
#         tupleList = _ndarrayToTuple2D(arrayList, isFilm, isBacteria)
#     elif dimension == 3:
#         tupleList = _ndarrayToTuple3D(arrayList)
#     else:
#         raise RuntimeError("Unknown dimension")
#
#     return tupleList
#
#
# def _ndarrayToTuple2D(arrayList: ndarray, isFilm: bool, isBacteria: bool) -> \
#         List[List[List[Tuple[int, int, int, int]]]]:
#     """
#     This is a helper function to rephrase 2D ndarray into tuple format
#     """
#     # init the list
#     tupleList = []
#
#     # based on it's film or bacteria, set appropriate height value
#     if isFilm:
#         height = 0
#     elif isBacteria:
#         height = 3
#     else:
#         raise RuntimeError("Unknown ndarray pass in")
#
#     # rephrase ndarray to tuple
#     for z in range(len(arrayList)):
#         temp1 = []
#         for y in range(len(arrayList[z])):
#             temp2 = []
#             for x in range(len(arrayList[z][y])):
#                 position = (x, y, height, arrayList[z][y][x])
#                 temp2.append(position)
#             temp1.append(temp2)
#         tupleList.append(temp1)
#
#     return tupleList
#
#
# def _ndarrayToTuple3D(arrayList: ndarray) -> List[List[List[Tuple[int, int, int, int]]]]:
#     """
#     This is a helper function to rephrase 3D ndarray into tuple format
#     """
#     # init the list
#     tupleList = []
#
#     # rephrase ndarray to tuple
#     for z in range(len(arrayList)):
#         temp1 = []
#         for y in range(len(arrayList[z])):
#             temp2 = []
#             for x in range(len(arrayList[z][y])):
#                 position = (x, y, z, arrayList[z][y][x])
#                 temp2.append(position)
#             temp1.append(temp2)
#         tupleList.append(temp1)
#
#     return tupleList


def _twoPointEnergy(film: Dict[Tuple[int, int], List[Tuple[int, int]]],
                    bacteria: Dict[Tuple[int, int], List[Tuple[int, int]]],
                    cutoff: int, startPointOnFilm: Tuple[int, int], limit: Tuple[int, int]) -> float:
    """
    This function takes in two point list in tuple format and calculate the energy between every tep points based
    on Coulomb's law
    If the distance excess the cutoff, energy is 0
    startPointOnFilm: This is the start point on the film to react with bacteria
    limit: This is a tuple contain two number, first is the length of film, second is the width of film
    """
    # init variable uses
    total_energy = 0

    # loop the point on the bacteria
    # for z in range(len(bacteria)):
    #     for y in range(len(bacteria[z])):
    #         for x in range(len(bacteria[z][y])):
    #             point1 = list(bacteria[z][y][x])
    #
    #             # generate the point on the surface should interact with this point on the bacteria based on the
    #             # position of current bacteria point and cutoff value
    #             # range on x direction
    #             film_x_start = max(0, point1[2] - cutoff)
    #             film_x_end = min(len(film[z][y]), point1[2] + cutoff)
    #
    #             # range on z direction
    #             film_y_start = max(0, point1[1] - cutoff)
    #             film_y_end = min(len(film[z]), point1[1] + cutoff)
    #
    #             # get film needed
    #             film_list = []
    #
    #             for film_z in range(len(film)):
    #                 for film_y in range(film_y_start, film_y_end):
    #                     for film_x in range(film_x_start, film_x_end):
    #                         point2 = list(film[film_z][film_y][film_x])
    #
    #                         film_list.append(point2)
    #
    #             # calculate distance between current bacteria point and film_list points
    #             for point2 in film_list:
    #                 distance = ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2 +
    #                             (point1[2] - point2[2]) ** 2) ** 0.5
    #
    #                 # if distance bigger than cutoff, ignore it
    #                 if distance > cutoff:
    #                     # print("distance is {}, cutoff is {}".format(distance, cutoff))
    #                     total_energy += 0
    #                 else:
    #                     charge1 = point1[3]
    #                     charge2 = point2[3]
    #                     energy = COULOMB_CONSTANT * charge1 * charge2 / distance
    #
    #                     total_energy += energy

    # set the range on x and y direction
    x_start = max(0, startPointOnFilm[0] - cutoff)
    x_end = min(limit[0] - 1, startPointOnFilm[0] + cutoff)
    y_start = max(0, startPointOnFilm[1] - cutoff)
    y_end = min(limit[1] - 1, startPointOnFilm[1] + cutoff)

    # loop point on the bacteria to do the calculation
    for bact_point in bacteria.keys():
        # loop point in the cutoff range of this bacteria point on the film
        for x in range(max(x_start, bact_point[0] - cutoff), min(x_end, bact_point[0] + cutoff)):
            for y in range(max(y_start, bact_point[1] - cutoff), min(y_end, bact_point[1] + cutoff)):
                # get coordination of point on the film
                film_point = (x, y)

                # calculate distance between two distance
                distance = ((bact_point[0] - film_point[0]) ** 2 + (bact_point[1] - film_point[1]) ** 2 +
                            (bacteria[bact_point][0][0] - film[film_point][0][0]) ** 2) ** 0.5

                # if distance excess cutoff, then don't count energy
                if distance > cutoff:
                    continue
                if distance == 0:
                    continue
                else:
                    # if distance is smaller than cutoff, calculate the energy
                    energy = bacteria[bact_point][0][1] * film[film_point][0][1] / distance
                    total_energy += energy

    return total_energy

def _calculateEnergy(x_start: int, x_end: int, y_start: int, y_end: int, film: ndarray, bacteria: ndarray,
                     result_dict: Dict, interactType: str, cutoff: int = None) -> None:
    """
    This is a helper function for calculate energy in the multi process
    Save the result in a given dictionary
    """
    raise NotImplementedError
