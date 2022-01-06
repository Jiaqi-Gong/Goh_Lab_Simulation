"""
This program:
- Calculates the energy of the surface
"""
from copy import deepcopy
from functools import partial
from typing import Tuple, List, Union
import time

from ExternalIO import *
import multiprocessing as mp

FIX_2D_HEIGHT = 2


def interact(interactType: str, intervalX: int, intervalY: int, film: ndarray, bacteria: ndarray, currIter: int,
             cutoff: int, dimension: int) \
        -> Tuple[Union[float, int], int, int, Union[float, int], Union[float, int], int, int]:
    """
    Do the simulation, scan whole film surface with bacteria
    the format of ndarray pass to simulator is in format (z,y,x), when make np.ones(1,2,3)
    which means 1 z layer, 2 y layer and 3 x layer.
    """
    writeLog("This is interact{}D in Simulation".format(dimension))
    showMessage("Start to interact ......")
    # writeLog("intervalX is: {}, intervalY is: {}, film is: {}, bacteria is: {}".format(
    #     intervalX, intervalY, film, bacteria))

    # determine the time to save file in folder
    # get time
    now = datetime.now()
    day = now.strftime("%m_%d")
    current_time = now.strftime("%H_%M_%S")

    # create dictionary of time
    date = {"day":day,
            "current_time": current_time}


    startTime = time.time()

    # based on dimension, do different thing
    if dimension == 2:
        # change the format of film and bacteria, get 2D info
        film = film[0]
        bacteria = bacteria[0]

        # show image of whole film and bacteria
        if currIter == 0:
            visPlot(film, "whole_film_2D_{}".format(currIter), 2, date)
        visPlot(bacteria, "whole_bacteria_2D_{}".format(currIter), 2, date)

        # shape of the film
        film_shape = film.shape

        # shape of bacteria in 2D
        bact_shape = bacteria.shape

        # set the range
        range_x = np.arange(0, film_shape[1], intervalX)
        range_y = np.arange(0, film_shape[0], intervalY)

    elif dimension == 3:
        # show image of whole film and bacteria
        visPlot(film, "whole_film_3D_{}".format(currIter), 3, date)
        visPlot(bacteria, "whole_bacteria_3D_{}".format(currIter), 3, date)

        # shape of the film
        film_shape = film.shape

        # shape of bacteria in 2D
        bact_shape = bacteria.shape[1:]

        # currently, all film uses will be convert to 2D, in the future may change
        film = film[0]

        # set the range
        range_x = np.arange(0, film_shape[2], intervalX)
        range_y = np.arange(0, film_shape[1], intervalY)
    else:
        raise RuntimeError("Unknown dimension in Energy Calculator")

    writeLog("shape is : {}, range_x is: {}, range_y is: {}".format(film_shape, range_x, range_y))
    showMessage("len(range_x) is:{}".format(len(range_x)))

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

    # ncpus = 1
    # part = len(range_x) // int(np.floor(np.sqrt(ncpus)))
    # processNum = ncpus

    showMessage("Process number is: {}, ncpu number is: {}, part is: {}".format(processNum, ncpus, part))

    pool = mp.Pool(processes=processNum)

    # change the bacteria surface into 1D
    if dimension == 2:
        bacteria_1D = np.reshape(bacteria, (-1))
    else:
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
    result, min_film, path = result[0], result[1], result[2]

    writeLog("Result in interact {}D is: {}".format(dimension, result))
    writeLog("Path is: {}".format(path))

    # print the min_film
    visPlot(min_film, "film_at_minimum_{}".format(currIter), 2, date)

    showMessage("Interact done")
    writeLog(result)

    # record time uses
    endTime = time.time()
    totalTime = endTime - startTime
    showMessage(f"Total time it took for calculating energy is {totalTime} seconds")

    return result


def _calculateEnergy(data: Tuple[ndarray, ndarray, ndarray, ndarray], interactType: str, bacteriaShape: Tuple,
                     cutoff: int = None):
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
    path = []

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
                film_1D = film_list[0]

            else:
                raise RuntimeError("Unknown interact type: {}".format(interactType))

            # count and unique
            unique, counts = np.unique(film_use, return_counts=True)

            # record all variables
            path.append("energy is: {}, unique is: {}, counts is: {}, position is:{}".format(
                energy, unique, counts, (x, y)))

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

    return (result, min_film, path)


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
