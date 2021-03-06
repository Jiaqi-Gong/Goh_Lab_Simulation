import os
from copy import deepcopy
from functools import partial
from typing import Tuple, List, Union, Dict
import time

import numpy as np
from numpy import ndarray
import multiprocessing as mp

# following import from parent folder, change path
import sys 
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from SurfaceGenerator.Domain import DomainGenerator
from FilmFile import Film
from BacteriaFile import Bacteria

time_result = []

FIX_2D_HEIGHT = 2


def start(ncpus):
    intervalX = 10
    intervalY = 10
    cutoff = 6
    # interactType = "DOT"
    # tests = [dot_test1]
    interactType = "CUTOFF"
    tests = [1]

    time_result.append("Current ncpus is: {}".format(ncpus))

    domainGenerator = DomainGenerator(10, False)

    # prepare film and bacteria
    trail = 9999
    seed = 10
    shape = 'rectangle'
    filmSize = (10000, 10000)
    bacteriaSize = (100, 100)
    filmSurfaceCharge = 1
    bacteriaSurfaceCharge = -1

    domainShape = 'diamond'
    domainSize = (10, 10)
    domainConc = 0.2
    chargeConc = 0.5

    startTime = time.time()

    film = Film.FilmSurface2D(trail, shape, filmSize, filmSurfaceCharge, seed)
    bacteria = Bacteria.Bacteria2D(trail, shape, bacteriaSize, bacteriaSurfaceCharge, seed)

    film = domainGenerator.generateDomain(film, domainShape, domainSize, domainConc, chargeConc)[0][0]
    bacteria = domainGenerator.generateDomain(bacteria, domainShape, domainSize, domainConc, chargeConc)[0][0]

    endTime = time.time()

    print("***********\nTime uses for generate film and bacteria is: {}\n***********\n".format(endTime - startTime))

    # shape of the film
    film_shape = film.shape

    # shape of bacteria
    bact_shape = bacteria.shape

    # set the range
    range_x = np.arange(0, film_shape[1], intervalX)
    range_y = np.arange(0, film_shape[0], intervalY)

    print("len(range_x) is:{}".format(len(range_x)))

    startTime = time.time()

    # using partial to set all the constant variables
    _calculateEnergyConstant = partial(_calculateEnergy, cutoff=cutoff, interactType=interactType,
                                       bacteriaShape=bacteria.shape)

    # init parameter for multiprocess
    # minus 2 in case of other possible process is running

    for test in tests:
        # depends on the interact type, using different methods to set paters
        # this step is caused by numpy is a parallel package, when doing DOT, using np.dot so need to give some cpu for it
        if interactType.upper() == "DOT":
            part, processNum = test(range_x, ncpus)
        else:
            part = len(range_x) // int(ncpus)
            processNum = ncpus

        print("Process number is: {}, ncpu number is: {}, part is: {}".format(processNum, ncpus, part))

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
        result = pool.map(_calculateEnergyConstant, data)

        # get the minimum result
        result.sort()
        result = result.pop(0)
        result, min_film = result[0], result[1]

        print("Interact done")
        print("result is :{}".format(result))

        # record time uses
        endTime = time.time()
        totalTime = endTime - startTime

        record = "Process number is: {}, ncpu number is: {}, part is: {}, time uses for {} calculate is: {}".format(
            processNum, ncpus, part, test, totalTime)

        print(record)

        time_result.append(record)

    time_result.append("@@@@@@@@@@@@@@@@@@@@@@@@")


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


def dot_test1(range_x, ncpus):
    part = len(range_x) // int(np.floor(np.sqrt(ncpus)))
    processNum = part

    return part, processNum


def dot_test2(range_x, ncpus):
    part = len(range_x) // int(np.floor(np.sqrt(ncpus)))
    processNum = ncpus

    return part, processNum


def dot_test3(range_x, ncpus):
    part = len(range_x) // int((ncpus)) + 1
    processNum = ncpus

    return part, processNum


def print_result():
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    for string in time_result:
        print(string)


class BigList:
    def __init__(self):
        self.content = []

def mpAppendTest(processNum):
    # testClass = BigList()
    print(f"process number is {processNum}")
    # using partial to set all the constant variables
    resultList = []
    data = [100, 200, 300, 400]

    pool = mp.Pool(processes=processNum)
    result = pool.map(mpAppend, data[:processNum])
    print(result)


def mpAppend(startNum: int):
    resultList = []
    for i in range(10):
        n = startNum + i
        resultList.append(n)
    return resultList


if __name__ == '__main__':
    # ncpus = max(int(os.environ.get('SLURM_CPUS_PER_TASK', default=1)), 1)
    ncpus = 4
    print("ncpus is: {}".format(ncpus))

    # for n in range(1, ncpus + 1):
    #     start(n)
    #
    # time_result.append("%%%%%%%%%%%%%%%%%%%")
    #
    # print_result()
    mpAppendTest(ncpus)
