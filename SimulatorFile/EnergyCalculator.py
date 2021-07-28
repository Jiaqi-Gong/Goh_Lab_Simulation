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

    # shape of bacteria
    bact_shape = bacteria.shape

    # set the range
    range_x = np.arange(0, film_shape[1], intervalX)
    range_y = np.arange(0, film_shape[0], intervalY)

    writeLog("shape is : {}, range_x is: {}, range_y is: {}".format(film_shape, range_x, range_y))

    # scan through the surface and make calculation
    if interactType.upper() in ["CUTOFF", "CUT-OFF"]:
        showMessage("Start to calculate cutoff energy, this step is slow")

        # change ndarray to dictionary
        filmDict = _ndarrayToDict(film, x_range=(range_x[0], range_x[-1]), y_range=(range_y[0], range_y[-1]))
        bactDict = _ndarrayToDict(bacteria, isBacteria=True)
    else:
        showMessage("Start to calculate energy in dot type")
        filmDict = None
        bactDict = None

    # using partial to set all the constant variables
    _calculateEnergy2DConstant = partial(_calculateEnergy2D, cutoff=cutoff, interactType=interactType,
                                         bactDict=bactDict, filmDict=filmDict, filmSurface=film, bacteriaSurface=bacteria)

    # init parameter for multiprocess
    # minus 2 in case of other possible process is running
    ncpus = max(int(os.environ.get('SLURM_CPUS_PER_TASK', default=1)), 1)

    showMessage("len(range_x) is:{}".format(len(range_x)))

    # depends on the interact type, using different methods to set paters
    # this step is caused by numpy is a parallel package, when doing DOT, using np.dot so need to give some cpu for it
    if interactType.upper() == "DOT":
        # based on test on Compute Canada beluga server, this method is fastest
        part = len(range_x) // int(np.floor(np.sqrt(ncpus)))
        processNum = part

        # ncpus = 1
        # part = len(range_x) // int(np.floor(np.sqrt(ncpus)))
        # processNum = ncpus

    else:
        part = len(range_x) // int(ncpus)
        processNum = ncpus

    showMessage("Process number is: {}, ncpu number is: {}, part is: {}".format(processNum, ncpus, part))

    pool = mp.Pool(processes=processNum)

    # prepare data for multiprocess, data is divided range into various parts, not exceed sqrt of ncpus can use
    data = []

    # double loop to prepare range x and range y
    range_x_list = [range_x[i:i + part] for i in range(0, len(range_x), part)]
    range_y_list = [range_y[i:i + part] for i in range(0, len(range_y), part)]

    # put combination into data
    for x in range_x_list:
        for y in range_y_list:
            if interactType.upper() == "DOT":
                data.append((x, y, deepcopy(film), deepcopy(bacteria)))
            else:
                data.append((x, y, None, None))

    # run interact
    result = pool.map(_calculateEnergy2DConstant, data)

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


def _calculateEnergy2D(data: Tuple[ndarray, ndarray, Union[None, Dict], Union[None, Dict]], interactType: str,
                       filmSurface: ndarray, bacteriaSurface: ndarray, filmDict: Union[None, Dict],
                       bactDict: Union[None, Dict], cutoff: int = None,):
    """
    This is the multiprocess helper function for calculating energy for 2D
    """
    # init some variable
    range_x = data[0]
    range_y = data[1]

    if data[2] is not None:
        film = data[2]
        bacteria = data[3]
    else:
        film = filmSurface
        bacteria = bacteriaSurface

    # shape of the film
    film_shape = film.shape

    # shape of bacteria
    bact_shape = bacteria.shape

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

    # loop all point in the range
    for x in range_x:
        for y in range_y:
            # set the x boundary and y boundary
            x_boundary = bact_shape[0] + x
            y_boundary = bact_shape[1] + y

            # writeLog("x_boundary is: {}, y_boundary is: {}, film_shape is:{}, bacteria shape is: {} ".format(
            #     x_boundary, y_boundary, film_shape, bact_shape))

            # check if bacteria surface is exceed range of film surface
            if x_boundary > film_shape[1] or y_boundary > film_shape[0]:
                # if exceed the surface, go to next iteration
                # writeLog("outside the range, continue")
                # writeLog("x_boundary is: {}, y_boundary is: {}, film_shape is:{}, bacteria shape is: {} ".format(
                #     x_boundary, y_boundary, film_shape, bact_shape))
                continue

            # change the corresponding film surface into 1D
            film_use = film[x: x_boundary, y: y_boundary]
            film_1D = np.reshape(film_use, (-1,))

            # do the energy calculation based on the interact type
            # dot interact
            if interactType.upper() == "DOT":
                # calculate energy, uses electrostatic energy formula, assuming that r = 1
                # WARNING: r should be change based on the height difference between film and bacteria in future
                # writeLog(["This is surface and film uses to calculate energy", film_1D, bacteria_1D])

                energy = np.dot(film_1D, bacteria_1D)

            # cutoff interact
            elif interactType.upper() in ["CUTOFF", "CUT-OFF"]:
                # calculate energy by using cutoff calculation function

                # get the start point on the film
                startPoint = (x, y)

                # call function to calculate energy
                energy = _twoPointEnergy(filmDict, bactDict, cutoff, startPoint, (film_shape[1], film_shape[0]))

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
                min_film = film_use
    # save the result
    result = (min_energy, min_x, min_y, min_energy_charge, min_charge, min_charge_x, min_charge_y)

    # return result
    return (result, min_film)


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

    # change ndarray to dictionary
    filmDict = _ndarrayToDict(film)
    bactDict = _ndarrayToDict(bacteria, isBacteria=True)

    # show image of whole film and bacteria
    visPlot(film, "whole_film_3D_{}".format(currIter), 3)
    visPlot(bacteria, "whole_bacteria_3D_{}".format(currIter), 3)

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
                writeLog("Only consider the lower surface of bacteria for now, may change in the future")
                # calculate energy, uses electrostatic energy formula
                for i in range(x, x_boundary):
                    for j in range(y, y_boundary):
                        # get the x,y position of bacteria and film
                        film_pos = (i, j)
                        bact_pos = (i - x, j - y)

                        # get the distance between two charge, only consider the lower surface of bacteria
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
                min_film = film_use

    # save the result
    result = (min_energy, min_x, min_y, min_energy_charge, min_charge, min_charge_x, min_charge_y)

    # reshape the min_film from 1d to 3d
    # first reshape it into 2d array
    min_film = np.array(min_film)

    min_film = np.reshape(min_film, (bact_shape[1], bact_shape[2]), order='F')
    # now convert it into 3d, but because film only has a height of 1, we will just add an extra square bracket
    # around min_film
    min_film = np.array([min_film])

    # print the min_film
    visPlot(min_film, "film_at_minimum_{}".format(currIter), 3)

    showMessage("Interact done")
    writeLog(result)

    return result


def _ndarrayToDict(arrayList: ndarray, isFilm: bool = None, isBacteria: bool = None, x_range: Tuple[int, int] = None,
                   y_range: Tuple[int, int] = None) -> \
        Dict[Tuple[int, int], List[Tuple[int, int]]]:
    """
    This function takes in a ndarray and reshape this array into a dictionary
    Key is a tuple represent (x, y), value is a list [(z, charge)], for 2D length of value is 1, for 3D it can be various
    """
    # init the result
    result = {}

    # init the position at z direction
    z_height = 0

    # if pass in is 2D, add z
    if len(arrayList.shape) == 2:
        arrayList = [arrayList]

    # get x, y range
    if x_range is not None:
        x_start = x_range[0]
        x_end = x_range[1]
    else:
        x_start = float('-INF')
        x_end = float('INF')

    if y_range is not None:
        y_start = x_range[0]
        y_end = x_range[1]
    else:
        y_start = float('-INF')
        y_end = float('INF')

    if isBacteria:
        z_height += 3

    # loop whole dictionary
    for z in range(len(arrayList)):
        for y in range(len(arrayList[z])):
            for x in range(len(arrayList[z][y])):
                # get charge
                charge = arrayList[z][y][x]

                # if charge is 2 means empty, do not save
                if charge == 2:
                    continue

                # if not in range, then continue
                if x < x_start or x > x_end or y < y_start or y > y_end:
                    continue

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
