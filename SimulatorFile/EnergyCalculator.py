"""
This file contains method to calculate the energy of the surface
"""
from copy import deepcopy
from functools import partial
from typing import Tuple, List, Union
import time

import numpy as np
from numpy import ndarray
from ExternalIO import *
import multiprocessing as mp

COULOMB_CONSTANT = 8.99

FIX_2D_HEIGHT = 2


def interact2D(interactType: str, intervalX: int, intervalY: int, film: ndarray, bacteria: ndarray, currIter: int,
               cutoff: int) -> Tuple[Union[float, int], int, int, Union[float, int], Union[float, int], int, int]:
    """
    Do the simulation, scan whole film surface with bacteria for 2D
    the format of ndarray pass to simulator is in format (z,y,x), when make np.ones(1,2,3)
    which means 1 z layer, 2 y layer and 3 x layer.
    """
    writeLog("This is interact2D in Simulation")
    showMessage("Start to interact ......")
    # writeLog("intervalX is: {}, intervalY is: {}, film is: {}, bacteria is: {}".format(
    #     intervalX, intervalY, film, bacteria))

    if interactType.upper() in ["CUTOFF", "CUT-OFF"]:
        # check validity of CUTOFF value
        if cutoff < FIX_2D_HEIGHT:
            raise RuntimeError("cutoff value {} is smaller than FIX_2D_HEIGHT {}".format(cutoff, FIX_2D_HEIGHT))

    startTime = time.time()

    # change the format of film and bacteria
    film = film[0]
    bacteria = bacteria[0]

    # show image of whole film and bacteria
    if currIter == 0:
        visPlot(film, "whole_film_2D_{}".format(currIter), 2)
    visPlot(bacteria, "whole_bacteria_2D_{}".format(currIter), 2)

    # shape of the film
    film_shape = film.shape

    # set the range
    range_x = np.arange(0, film_shape[1], intervalX)
    range_y = np.arange(0, film_shape[0], intervalY)

    writeLog("shape is : {}, range_x is: {}, range_y is: {}".format(film_shape, range_x, range_y))
    showMessage("len(range_x) is:{}".format(len(range_x)))

    # using partial to set all the constant variables
    _calculateEnergyConstant = partial(_calculateEnergy, cutoff=cutoff, interactType=interactType,
                                       bacteriaShape=bacteria.shape)

    # init parameter for multiprocess
    # minus 2 in case of other possible process is running
    ncpus = max(int(os.environ.get('SLURM_CPUS_PER_TASK', default=1)), 1)

    # depends on the interact type, using different methods to set paters
    # this step is caused by numpy is a parallel package, when doing DOT, using np.dot so need to give some cpu for it

    # based on test on Compute Canada beluga server, this method is fastest
    part = len(range_x) // int(np.floor(np.sqrt(ncpus)))
    processNum = part

    # ncpus = 1
    # part = len(range_x) // int(np.floor(np.sqrt(ncpus)))
    # processNum = ncpus

    showMessage("Process number is: {}, ncpu number is: {}, part is: {}".format(processNum, ncpus, part))

    pool = mp.Pool(processes=processNum)

    # change the bacteria surface into 1D
    bacteria_1D = np.reshape(bacteria, (-1))

    # prepare data for multiprocess, data is divided range into various parts, not exceed sqrt of ncpus can use
    data = []

    # double loop to prepare range x and range y
    range_x_list = [range_x[i:i + part] for i in range(0, len(range_x), part)]
    range_y_list = [range_y[i:i + part] for i in range(0, len(range_y), part)]

    # put combination into data
    for x in range_x_list:
        for y in range_y_list:
            data.append((x, y, deepcopy(film), deepcopy(bacteria_1D)))

    # run interact
    result = pool.map(_calculateEnergyConstant, data)

    # get the minimum result
    result.sort()
    result = result.pop(0)
    result, min_film = result[0], result[1]

    writeLog("Result in interact 2D is: {}".format(result))

    # print the min_film
    visPlot(min_film, "film_at_minimum_{}".format(currIter), 2)

    showMessage("Interact done")
    writeLog(result)

    # record time uses
    endTime = time.time()
    totalTime = endTime - startTime
    showMessage(f"Total time it took for calculating energy is {totalTime} seconds")

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
    # writeLog("intervalX is: {}, intervalY is: {}, film is: {}, bacteria is: {}".format(
    #     intervalX, intervalY, film, bacteria))

    if interactType.upper() in ["CUTOFF", "CUT-OFF"]:
        # check validity of CUTOFF value
        if cutoff < FIX_2D_HEIGHT:
            raise RuntimeError("cutoff value {} is smaller than FIX_2D_HEIGHT {}".format(cutoff, FIX_2D_HEIGHT))

    startTime = time.time()

    # show image of whole film and bacteria
    visPlot(film, "whole_film_3D_{}".format(currIter), 3)
    visPlot(bacteria, "whole_bacteria_3D_{}".format(currIter), 3)

    # shape of the film
    film_shape = film.shape

    # shape of bacteria in 2D
    bact_shape = bacteria.shape[1:]

    # currently, all film uses will be convert to 2D, in the future may change
    film = film[0]

    # set the range
    range_x = np.arange(0, film_shape[2], intervalX)
    range_y = np.arange(0, film_shape[1], intervalY)

    writeLog("shape is : {}, range_x is: {}, range_y is: {}".format(film_shape, range_x, range_y))

    # using partial to set all the constant variables
    _calculateEnergyConstant = partial(_calculateEnergy, cutoff=cutoff, interactType=interactType,
                                       bacteriaShape=bact_shape)

    # init parameter for multiprocess
    # minus 2 in case of other possible process is running
    ncpus = max(int(os.environ.get('SLURM_CPUS_PER_TASK', default=1)), 1)

    # depends on the interact type, using different methods to set paters
    # this step is caused by numpy is a parallel package, when doing DOT, using np.dot so need to give some cpu for it

    # based on test on Compute Canada beluga server, this method is fastest
    part = len(range_x) // int(np.floor(np.sqrt(ncpus)))
    processNum = part

    showMessage("Process number is: {}, ncpu number is: {}, part is: {}".format(processNum, ncpus, part))

    pool = mp.Pool(processes=processNum)

    # change the bacteria surface into 1D
    bacteria_1D = _trans3DTo1D(bacteria)

    # prepare data for multiprocess, data is divided range into various parts, not exceed sqrt of ncpus can use
    data = []

    # double loop to prepare range x and range y
    range_x_list = [range_x[i:i + part] for i in range(0, len(range_x), part)]
    range_y_list = [range_y[i:i + part] for i in range(0, len(range_y), part)]

    # put combination into data
    for x in range_x_list:
        for y in range_y_list:
            data.append((x, y, deepcopy(film), deepcopy(bacteria_1D)))

    # run interact
    result = pool.map(_calculateEnergyConstant, data)

    # get the minimum result
    result.sort()
    result = result.pop(0)
    result, min_film = result[0], result[1]

    writeLog("Result in interact 3D is: {}".format(result))

    # print the min_film
    visPlot(min_film, "film_at_minimum_{}".format(currIter), 2)

    showMessage("Interact done")
    writeLog(result)

    # record time uses
    endTime = time.time()
    totalTime = endTime - startTime
    showMessage(f"Total time it took for calculating energy is {totalTime} seconds")

    return result

    # # init some variable
    # # randomly, just not negative
    # min_energy = float("INF")
    # min_charge = float("INF")
    # min_energy_charge = float("INF")
    # min_charge_x = 0
    # min_charge_y = 0
    # min_x = -1
    # min_y = -1
    # min_film = []
    #
    # # get bacteria 1D
    #
    #
    # # calculate the energy
    # # scan through the surface and make calculation
    # for x in range_x:
    #     for y in range_y:
    #         # set the x boundary and y boundary
    #         x_boundary = bact_shape[2] + x
    #         y_boundary = bact_shape[1] + y
    #
    #         writeLog("x_boundary is: {}, y_boundary is: {}, film_shape is:{}, bacteria shape is: {} ".format(
    #             x_boundary, y_boundary, film_shape, bact_shape))
    #
    #         # check if bacteria surface is exceed range of film surface
    #         if x_boundary > film_shape[2] or y_boundary > film_shape[1]:
    #             # if exceed the surface, go to next iteration
    #             writeLog("outside the range, continue")
    #             continue
    #
    #         # do the energy calculation based on the interact type
    #         # dot interact
    #         if interactType.upper() == "DOT":
    #             writeLog("Only consider the lower surface of bacteria for now, may change in the future")
    #             # calculate energy, uses electrostatic energy formula
    #             raise NotImplementedError
    #
    #         # cutoff interact
    #         elif interactType.upper() in ["CUTOFF", "CUT-OFF"]:
    #             # calculate energy by using cutoff calculation function
    #             raise NotImplementedError
    #
    #         else:
    #             raise RuntimeError("Unknown interact type")
    #
    #         # count and unique
    #         unique, counts = np.unique(film_use, return_counts=True)
    #
    #         # record all variables
    #         writeLog("film_use is: {}, energy is: {}, unique is: {}, counts is: {}".format(
    #             film_use, energy, unique, counts))
    #
    #         # check the calculation result and change corresponding value
    #         charge = 0
    #         for i in range(len(unique)):
    #             if unique[i] == -1:
    #                 charge -= counts[i]
    #             elif unique[i] == 1:
    #                 charge += counts[i]
    #             else:
    #                 charge += 0
    #
    #         # below is the way of calculating charge in the old code, however for now we have 0 on the surface while
    #         # in the old code only -1 nad 1 on the surface
    #         # if len(unique) == 1:
    #         #     if unique[0] == -1:
    #         #         charge = -counts[0]
    #         #     else:
    #         #         charge = counts[0]
    #         # elif unique[0] == -1:
    #         #     charge = -counts[0] + counts[1]
    #         # elif unique[0] == 1:
    #         #     charge = counts[0] - counts[1]
    #         # else:
    #         #     showMessage("This is an error, parameter unique is not -1 or 1, it is: {}".format(unique))
    #         #     writeLog(__dict__)
    #         #     raise RuntimeError("Variable 'charge' in _interact2D not init, caused by the error in unique")
    #
    #         if charge < min_charge:
    #             min_charge = charge
    #             min_charge_x = x
    #             min_charge_y = y
    #
    #         # find minimum energy and location
    #         if energy < min_energy:
    #             min_energy = energy
    #             min_x = x
    #             min_y = y
    #             min_energy_charge = charge
    #             min_film = film_use
    #
    # # save the result
    # result = (min_energy, min_x, min_y, min_energy_charge, min_charge, min_charge_x, min_charge_y)
    #
    # # reshape the min_film from 1d to 3d
    # # first reshape it into 2d array
    # min_film = np.array(min_film)

    # min_film = np.reshape(min_film, (bact_shape[1], bact_shape[2]), order='F')
    # # now convert it into 3d, but because film only has a height of 1, we will just add an extra square bracket
    # # around min_film
    # min_film = np.array([min_film])
    #
    # # print the min_film
    # visPlot(min_film, "film_at_minimum_{}".format(currIter), 3)
    #
    # showMessage("Interact done")
    # writeLog(result)
    #
    # return result


def _calculateEnergy(data: Tuple[ndarray, ndarray, ndarray, ndarray], interactType: str, bacteriaShape: Tuple, cutoff: int = None):
    """
    This is the multiprocess helper function for calculating energy, need 2D film and 1D bacteria
    """
    # init some variable
    range_x = data[0]
    range_y = data[1]
    film = data[2]
    bacteria = data[3]

    # shape of the film
    film_shape = film.shape

    # shape of bacteria
    bact_shape = bacteriaShape

    # randomly, just not negative
    min_energy = float("INF")
    min_charge = float("INF")
    min_energy_charge = float("INF")
    min_charge_x = 0
    min_charge_y = 0
    min_x = -1
    min_y = -1
    min_film = []

    # loop all point in the range
    for x in range_x:
        for y in range_y:
            # set the x boundary and y boundary
            x_boundary = bact_shape[1] + x
            y_boundary = bact_shape[0] + y

            # writeLog("x_boundary is: {}, y_boundary is: {}, film_shape is:{}, bacteria shape is: {} ".format(
            #     x_boundary, y_boundary, film_shape, bact_shape))

            # check if bacteria surface is exceed range of film surface
            if x_boundary > film_shape[1] or y_boundary > film_shape[0]:
                # if exceed the surface, go to next iteration
                # writeLog("outside the range, continue")
                # writeLog("x_boundary is: {}, y_boundary is: {}, film_shape is:{}, bacteria shape is: {} ".format(
                #     x_boundary, y_boundary, film_shape, bact_shape))
                continue

            # do the energy calculation based on the interact type
            # dot interact
            if interactType.upper() == "DOT":
                # change the corresponding film surface into 1D
                film_use = film[x: x_boundary, y: y_boundary]
                film_1D = np.reshape(film_use, (-1,))

                # calculate energy, uses electrostatic energy formula, assuming that r = 1
                # WARNING: r should be change based on the height difference between film and bacteria in future
                # writeLog(["This is surface and film uses to calculate energy", film_1D, bacteria_1D])

                energy = np.dot(film_1D, bacteria)

            # cutoff interact
            elif interactType.upper() in ["CUTOFF", "CUT-OFF"]:
                # change the corresponding film surface into 1D
                film_use = film[x: x_boundary, y: y_boundary]
                # film_1D = np.reshape(film_use, (-1,))

                # generate all film need to scan for energy
                film_list = _getCutoffFilm1D(film, (x, y), bact_shape, cutoff)
                energy_list = []

                # loop all film in the cutoff range
                for film_1D in film_list:
                    energy_list.append(np.dot(film_1D, bacteria))

                # calculate average energy
                energy = sum(energy_list) / len(energy_list)

            else:
                raise RuntimeError("Unknown interact type: {}".format(interactType))

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
                min_film = film_use
    # save the result
    result = (min_energy, min_x, min_y, min_energy_charge, min_charge, min_charge_x, min_charge_y)

    return (result, min_film)


def _trans3DTo1D(arrayList: ndarray) -> ndarray:
    """
    This helper function take in a 3D ndarray list and transfer to 1D ndarray, divide value by it's height
    """
    # init a indicator for 2D
    is2D = False
    visited_size = 0

    # if pass in is 2D, using fix height and one layer to make it 3D
    # init a new array to store info
    if len(arrayList.shape) == 2:
        array_2D = np.zeros_like(arrayList)
        arrayList = [arrayList]
        is2D = True
    else:
        array_2D = np.zeros(arrayList.shape[1:])

    # loop whole array
    for z in range(len(arrayList)):
        for y in range(len(arrayList[z])):
            for x in range(len(arrayList[z][y])):
                # check if this (x, y) has been visited, if visited, pass
                new_value = array_2D[y][x]

                # get current value
                value = arrayList[z][y][x]

                # if new_value is not 0, means it has visited
                # if value is 2 means empty, do not save
                if new_value != 0 or value == 2:
                    continue

                # calculate new value
                if is2D:
                    height = FIX_2D_HEIGHT
                else:
                    # +1 to avoid divide 0
                    height = z + 1

                # change value
                array_2D[y][x] = value / height
                visited_size += 1

                if visited_size == arrayList.size:
                    return np.reshape(array_2D, (-1,))

    # return a 1D array
    return np.reshape(array_2D, (-1,))


def _getCutoffFilm1D(film: ndarray, startPoint: Tuple[int, int], bacteriaSize: Tuple[int, int], cutoff: int) \
        -> List[ndarray]:
    """
    This function based on the start point and cut off value, general a list of film in 1D need to calculate energy
    """
    # init a empty list
    film_list = []

    # get the size of film
    if len(film.shape) == 2:
        filmSize = film.shape
    else:
        filmSize = film.shape[1:]
    # get the range on x and y axis
    x_start = max(0, startPoint[0] - cutoff)
    x_end = min(filmSize[1] - 1 - bacteriaSize[1], startPoint[0] + cutoff)
    y_start = max(0, startPoint[1] - cutoff)
    y_end = min(filmSize[0] - 1 - bacteriaSize[0], startPoint[1] + cutoff)

    # append corresponding film into list in 1D
    for x_s in range(x_start, x_end + 1):
        for y_s in range(y_start, y_end + 1):
            film_list.append(np.reshape(film[y_s: y_s + bacteriaSize[1], x_s: x_s + bacteriaSize[1]], (-1,)))

    return film_list

# def _calculateEnergy2D(data: Tuple[ndarray, ndarray, Union[None, Dict], Union[None, Dict]], interactType: str,
#                        filmSurface: ndarray, bacteriaSurface: ndarray, filmDict: Union[None, Dict],
#                        bactDict: Union[None, Dict], cutoff: int = None,):
#     """
#     This is the multiprocess helper function for calculating energy for 2D
#     """
#     # init some variable
#     range_x = data[0]
#     range_y = data[1]
#
#     if data[2] is not None:
#         film = data[2]
#         bacteria = data[3]
#     else:
#         film = filmSurface
#         bacteria = bacteriaSurface
#
#     # shape of the film
#     film_shape = film.shape
#
#     # shape of bacteria
#     bact_shape = bacteria.shape
#
#     # randomly, just not negative
#     min_energy = float("INF")
#     min_charge = float("INF")
#     min_energy_charge = float("INF")
#     min_charge_x = 0
#     min_charge_y = 0
#     min_x = -1
#     min_y = -1
#     min_film = []
#
#     # change the bacteria surface into 1D
#     bacteria_1D = np.reshape(bacteria, (-1))
#
#     # loop all point in the range
#     for x in range_x:
#         for y in range_y:
#             # set the x boundary and y boundary
#             x_boundary = bact_shape[0] + x
#             y_boundary = bact_shape[1] + y
#
#             # writeLog("x_boundary is: {}, y_boundary is: {}, film_shape is:{}, bacteria shape is: {} ".format(
#             #     x_boundary, y_boundary, film_shape, bact_shape))
#
#             # check if bacteria surface is exceed range of film surface
#             if x_boundary > film_shape[1] or y_boundary > film_shape[0]:
#                 # if exceed the surface, go to next iteration
#                 # writeLog("outside the range, continue")
#                 # writeLog("x_boundary is: {}, y_boundary is: {}, film_shape is:{}, bacteria shape is: {} ".format(
#                 #     x_boundary, y_boundary, film_shape, bact_shape))
#                 continue
#
#             # change the corresponding film surface into 1D
#             film_use = film[x: x_boundary, y: y_boundary]
#             film_1D = np.reshape(film_use, (-1,))
#
#             # do the energy calculation based on the interact type
#             # dot interact
#             if interactType.upper() == "DOT":
#                 # calculate energy, uses electrostatic energy formula, assuming that r = 1
#                 # WARNING: r should be change based on the height difference between film and bacteria in future
#                 # writeLog(["This is surface and film uses to calculate energy", film_1D, bacteria_1D])
#
#                 energy = np.dot(film_1D, bacteria_1D)
#
#             # cutoff interact
#             elif interactType.upper() in ["CUTOFF", "CUT-OFF"]:
#                 # calculate energy by using cutoff calculation function
#
#                 # get the start point on the film
#                 startPoint = (x, y)
#
#                 # call function to calculate energy
#                 energy = _twoPointEnergy(filmDict, bactDict, cutoff, startPoint, (film_shape[1], film_shape[0]))
#
#             else:
#                 raise RuntimeError("Unknown interact type: {}".format(interactType))
#
#             # count and unique
#             unique, counts = np.unique(film_use, return_counts=True)
#
#             # record all variables
#             # writeLog("film_use is: {}, film_1D is: {}, energy is: {}, unique is: {}, counts is: {}".format(
#             #     film_use, film_1D, energy, unique, counts))
#
#             # check the calculation result and change corresponding value
#             charge = 0
#             for i in range(len(unique)):
#                 if unique[i] == -1:
#                     charge -= counts[i]
#                 elif unique[i] == 1:
#                     charge += counts[i]
#                 else:
#                     charge += 0
#
#             # below is the way of calculating charge in the old code, however for now we have 0 on the surface while
#             # in the old code only -1 nad 1 on the surface
#             # if len(unique) == 1:
#             #     if unique[0] == -1:
#             #         charge = -counts[0]
#             #     else:
#             #         charge = counts[0]
#             # elif unique[0] == -1:
#             #     charge = -counts[0] + counts[1]
#             # elif unique[0] == 1:
#             #     charge = counts[0] - counts[1]
#             # else:
#             #     showMessage("This is an error, parameter unique is not -1 or 1, it is: {}".format(unique))
#             #     writeLog(__dict__)
#             #     raise RuntimeError("Variable 'charge' in _interact2D not init, caused by the error in unique")
#
#             if charge < min_charge:
#                 min_charge = charge
#                 min_charge_x = x
#                 min_charge_y = y
#
#             # find minimum energy and location
#             if energy < min_energy:
#                 min_energy = energy
#                 min_x = x
#                 min_y = y
#                 min_energy_charge = charge
#                 min_film = film_use
#     # save the result
#     result = (min_energy, min_x, min_y, min_energy_charge, min_charge, min_charge_x, min_charge_y)
#
#     # return result
#     return (result, min_film)


# def _ndarrayToDict(arrayList: ndarray, isFilm: bool = None, isBacteria: bool = None, x_range: Tuple[int, int] = None,
#                    y_range: Tuple[int, int] = None) -> \
#         Dict[Tuple[int, int], List[Tuple[int, int]]]:
#     """
#     This function takes in a ndarray and reshape this array into a dictionary
#     Key is a tuple represent (x, y), value is a list [(z, charge)], for 2D length of value is 1, for 3D it can be various
#     """
#     # init the result
#     result = {}
#
#     # init the position at z direction
#     z_height = 0
#
#     # if pass in is 2D, add z
#     if len(arrayList.shape) == 2:
#         arrayList = [arrayList]
#
#     # get x, y range
#     if x_range is not None:
#         x_start = x_range[0]
#         x_end = x_range[1]
#     else:
#         x_start = float('-INF')
#         x_end = float('INF')
#
#     if y_range is not None:
#         y_start = x_range[0]
#         y_end = x_range[1]
#     else:
#         y_start = float('-INF')
#         y_end = float('INF')
#
#     if isBacteria:
#         z_height += FIX_2D_HEIGHT
#
#     # loop whole dictionary
#     for z in range(len(arrayList)):
#         for y in range(len(arrayList[z])):
#             for x in range(len(arrayList[z][y])):
#                 # get charge
#                 charge = arrayList[z][y][x]
#
#                 # if charge is 2 means empty, do not save
#                 if charge == 2:
#                     continue
#
#                 # if not in range, then continue
#                 if x < x_start or x > x_end or y < y_start or y > y_end:
#                     continue
#
#                 # get key
#                 key = (x, y)
#
#                 # get value
#                 value = (z + z_height, charge)
#
#                 # add into the result dictionary
#                 if key not in result:
#                     result[key] = [value]
#                 else:
#                     result[key].append(value)
#
#     # sort all values in the order of value of z
#     for i in result.keys():
#         result[i].sort()
#
#     return result
#
#
# def _twoPointEnergy(film: Dict[Tuple[int, int], List[Tuple[int, int]]],
#                     bacteria: Dict[Tuple[int, int], List[Tuple[int, int]]],
#                     cutoff: int, startPointOnFilm: Tuple[int, int], limit: Tuple[int, int]) -> float:
#     """
#     This function takes in two point list in tuple format and calculate the energy between every tep points based
#     on Coulomb's law
#     If the distance excess the cutoff, energy is 0
#     startPointOnFilm: This is the start point on the film to react with bacteria
#     limit: This is a tuple contain two number, first is the length of film, second is the width of film
#     """
#     # init variable uses
#     total_energy = 0
#
#     x_start = max(0, startPointOnFilm[0] - cutoff)
#     x_end = min(limit[0] - 1, startPointOnFilm[0] + cutoff)
#     y_start = max(0, startPointOnFilm[1] - cutoff)
#     y_end = min(limit[1] - 1, startPointOnFilm[1] + cutoff)
#
#     # loop point on the bacteria to do the calculation
#     for bact_point in bacteria.keys():
#         # loop point in the cutoff range of this bacteria point on the film
#         for x in range(max(x_start, bact_point[0] - cutoff + FIX_2D_HEIGHT), min(x_end, bact_point[0] + cutoff - FIX_2D_HEIGHT)):
#             for y in range(max(y_start, bact_point[1] - cutoff + FIX_2D_HEIGHT), min(y_end, bact_point[1] + cutoff - FIX_2D_HEIGHT)):
#                 # get coordination of point on the film
#                 film_point = (x, y)
#
#                 # calculate distance between two distance
#                 distance = ((bact_point[0] - film_point[0]) ** 2 + (bact_point[1] - film_point[1]) ** 2 +
#                             (bacteria[bact_point][0][0] - film[film_point][0][0]) ** 2) ** 0.5
#
#                 # if distance excess cutoff, then don't count energy
#                 if distance > cutoff:
#                     continue
#                 if distance == 0:
#                     continue
#                 else:
#                     # if distance is smaller than cutoff, calculate the energy
#                     energy = bacteria[bact_point][0][1] * film[film_point][0][1] / distance
#                     total_energy += energy
#
#     return total_energy
