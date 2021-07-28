import os
from copy import deepcopy
from functools import partial
from typing import Tuple, List, Union, Dict
import time

import numpy as np
from numpy import ndarray
import multiprocessing as mp

from SurfaceGenerator.Domain import DomainGenerator
from FilmFile import Film
from BacteriaFile import Bacteria

time_result = []


def start(ncpus):
    intervalX = 10
    intervalY = 10
    cutoff = 6
    interactType = "DOT"

    time_result.append("Current ncpus is: {}".format(ncpus))
    for test in [test1, test2, test3]:
        film, bacteria, result, _calculateEnergy2DConstant, range_x, range_y, pool, data = \
            None, None, None, None, None, None, None, None
        domainGenerator = DomainGenerator(10, False)

        # prepare film and bacteria
        trail = 9999
        seed = 10
        shape = 'rectangle'
        filmSize = (1000, 1000)
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

        film = domainGenerator.generateDomain(film, domainShape, domainSize, domainConc, chargeConc)[0]
        bacteria = domainGenerator.generateDomain(bacteria, domainShape, domainSize, domainConc, chargeConc)[0]

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

        # scan through the surface and make calculation
        filmDict = None
        bactDict = None

        startTime = time.time()
        # using partial to set all the constant variables
        _calculateEnergy2DConstant = partial(_calculateEnergy2D, cutoff=cutoff, interactType=interactType,
                                             bactDict=bactDict, filmDict=filmDict, filmSurface=film,
                                             bacteriaSurface=bacteria)

        # init parameter for multiprocess
        # minus 2 in case of other possible process is running

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
        result = pool.map(_calculateEnergy2DConstant, data)

        # get the minimum result
        result.sort()
        result = result.pop(0)
        result, min_film = result[0], result[1]

        print("Interact done")

        # record time uses
        endTime = time.time()
        totalTime = endTime - startTime

        time_result.append(
            "Process number is: {}, ncpu number is: {}, part is: {}, time uses for {} calculate is: {}".format(
                processNum, ncpus, part, test, totalTime))

    time_result.append("@@@@@@@@@@@@@@@@@@@@@@@@")


def _calculateEnergy2D(data: Tuple[ndarray, ndarray, Union[None, Dict], Union[None, Dict]], interactType: str,
                       filmSurface: ndarray, bacteriaSurface: ndarray, filmDict: Union[None, Dict],
                       bactDict: Union[None, Dict], cutoff: int = None, ):
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
                # energy = _twoPointEnergy(filmDict, bactDict, cutoff, startPoint, (film_shape[1], film_shape[0]))

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


def test1(range_x, ncpus):
    part = len(range_x) // int(np.floor(np.sqrt(ncpus)))
    processNum = part

    return part, processNum


def test2(range_x, ncpus):
    part = len(range_x) // int(np.floor(np.sqrt(ncpus)))
    processNum = ncpus

    return part, processNum


def test3(range_x, ncpus):
    part = len(range_x) // int((ncpus)) + 1
    processNum = ncpus

    return part, processNum


def print_result():
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    for string in time_result:
        print(string)


if __name__ == '__main__':
    ncpus = max(int(os.environ.get('SLURM_CPUS_PER_TASK', default=1)), 1)
    print("ncpus is: {}".format(ncpus))

    for n in range(1, ncpus + 1):
        start(n)

    time_result.append("%%%%%%%%%%%%%%%%%%%")

    print_result()
