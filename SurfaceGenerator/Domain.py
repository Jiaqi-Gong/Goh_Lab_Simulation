"""
This program is generating the domain with some charge on it
Can be used for 2D, 3D and for testing surface, bacteria surface
"""
from numpy import ndarray
import numpy as np
from SurfaceGenerator.Surface import Surface
from typing import Tuple, List, Union
from ExternalIO import showMessage, writeLog, visPlot
import math
import time
from multiprocessing import Pool, cpu_count
from functools import partial
import os

WAIT_TIME = 10

class DomainGenerator:
    """
    This class is used to generate the domain on the surface passed in
    """
    # Declare the type of all variable
    seed: int
    neutral: bool

    def __init__(self, seed: int, neutral: bool):
        """
        Init this domain generate
        :param seed: seed for random, if using same seed can repeat the simulation
        :param domainNumChar: a list containing

        """
        self.seed = seed
        self.neutral = neutral
        # set the seed for random
        np.random.seed(self.seed)

    def generateDomain(self, surface: Surface, shape: str, size: Tuple[int, int], concentration: float,
                       charge_concentration: float) -> [ndarray, float, float]:
        """
        This function takes in a surface, shape and size of domain want to generate on the surface
        :param surface: the surface want to generate the domain
        :param shape: shape of the domain
        :param size: size of the surface, in the format ###x###, in unit micrometer, 1micrometer = 100 points, NOTICE: size of domain must smaller than surface
        :param concentration: concentration of the charge?
        :param k:
        :return: return the surface with wanted domain on it
        """
        writeLog("This is function generateDomain in Domain.py")
        showMessage("Start to generate domain ......")
        writeLog([self.__dict__, surface.__dict__, shape, size, concentration])

        startTime = time.time()

        # get size
        domainLength = size[0]
        domainWidth = size[1]

        # calculate how many domain should generate
        # calculation for the number of domains which needs to be generated depends on the shape of the domain
        # set corresponding check and generate function
        # generate the corresponding domain shape

        # generate the surface
        newSurface = surface.originalSurface

        # more shape coming soon, leave for more extension
        if shape.upper() == "DIAMOND":
            generateShape = self._generateDiamond
            checkEmpty = self._diamondEmpty
            # Number of domains
            # if the surface is 2d, only 1 domain number should be present
            domainNum = int((surface.length * surface.width * concentration) / int(4*((1+domainWidth)/2)*domainWidth+1))
            restriction = domainWidth + 1
            # showMessage("concentration = {}".format(concentration))
        elif shape.upper() == "CROSS":
            generateShape = self._generateCross
            checkEmpty = self._crossEmpty
            # Number of domains
            domainNum = int((surface.length * surface.width * concentration) / int(domainWidth*2+domainLength*2+1))
            restriction = max(domainWidth+1, domainLength+1)
        elif shape.upper() == "OCTAGON":
            generateShape = self._generateOctagon
            checkEmpty = self._octagonEmpty
            # Number of domains
            domainNum = int((surface.length * surface.width * concentration) / int((domainWidth+1 + domainWidth*2)**2 -
                                                                                   4*((1+domainWidth)/2)*domainWidth))
            restriction = (3/2)*domainWidth
        elif shape.upper() == "SINGLE":
            generateShape = self._generateSingle
            checkEmpty = self._singleEmpty
            # Number of domains
            domainNum = int(surface.length * surface.width * concentration)
            restriction = 0
        else:
            raise RuntimeError("Unknown shape")

        if surface.height >= 4:
            # calculate total number of available points on each side of bacteria
            # the domain number will be formatted as a list
            # domainNum will contain number of domains on each side
            # domainNum = [x0, x1, y0, y1, z0, z1]
            if shape.upper() == "DIAMOND":
                domainNum = [int((number*concentration)/int(4*((1+domainWidth)/2)*domainWidth+1))
                             for number in self._allPoints(newSurface)]
            elif shape.upper() == "CROSS":
                domainNum = [int((number*concentration)/int(domainWidth*2+domainLength*2+1))
                             for number in self._allPoints(newSurface)]
            elif shape.upper() == "OCTAGON":
                domainNum = [int((number*concentration)/int((domainWidth+1+domainWidth*2)**2-4*((1+domainWidth)/2)*domainWidth))
                             for number in self._allPoints(newSurface)]
            elif shape.upper() == "SINGLE":
                domainNum = [int((number*concentration)) for number in self._allPoints(newSurface)]

        showMessage("Total Domain is: {}".format(domainNum))

        np.set_printoptions(threshold=np.inf)

        # initalize the charge of the surface
        surfaceCharge = surface.surfaceCharge

        # initialize all the possible charges
        possible_charge = [1,-1,0]

        # depending on what the surface charge the user inputs, the domain charge will be the other 2 possible charges
        # therefore, remove the surfaceCharge from possible_charge
        possible_charge.remove(surfaceCharge)

        # make the new surface either all positive or all negative
        newSurface[newSurface == 0] = surfaceCharge

        # record info into log
        showMessage("generate new surface done")
        # writeLog(newSurface)
        writeLog("Charge of the surface is {}".format(surfaceCharge))
        writeLog("Charge of domain is {} and {}".format(possible_charge[0], possible_charge[1]))

        # Determine all the possible points allowed to be chosen as the start point to begin generating the domain
        possiblePoint = self._allPossiblePoint(newSurface, surface, surface.length, surface.width, surface.height, domainLength,
                                               domainWidth, shape)

        # if there are no possible points, either domain is too large or surface is too small
        if len(possiblePoint) == 0:
            raise RuntimeError("Either Domain is too large or Surface is too small")


        # now for the multiprocessing, separate the surface by the number of CPUs in the computer
        # realistically, we only need multiprocessing for the film
        # since the film ALWAYS has a height of 1, we will use this multiprocessing method when the height of surface is 1
        if surface.height < 4:
            # set how many domains we should make for each CPU
            # find the number of CPUs on the computer
            # therefore if the cpu_number is greater than 12, we will just return 12
            # minus 2 in case of other possible process is running

            ncpus = max(int(os.environ.get('SLURM_CPUS_PER_TASK', default=1)) - 2, 1)
            if ncpus == 1:
                ncpus = cpu_count()

            if ncpus <= 16:
                cpu_number = ncpus
            else:
                cpu_number = 16

            showMessage(f"number of CPUs is {ncpus} but we will use {cpu_number}")

            domainNumEach = int(domainNum / cpu_number)

            # if we want neutral charges on the surface, we can define domainNumChar2, otherwise, it will be zero
            if self.neutral:
                domainNumChar1 = math.ceil(
                    domainNumEach * charge_concentration)  # this will have the first charge from the possible_charge list
                domainNumChar2 = domainNumEach - domainNumChar1  # this will have the second charge from the possible_charge list
            elif not self.neutral:
                domainNumChar1 = domainNumEach
                domainNumChar2 = 0

            # we will find 2 numbers that are closest to each other that multiply to the number of CPUs
            # first, find the square root of that number
            squareRoot = math.sqrt(cpu_number)

            # then, split the number into lower and upper half
            upper = math.ceil(squareRoot)
            lower = int(squareRoot)

            # use a for loop to see when the 2 numbers multiply to each other
            # based on how we separate the CPUs, we will separate the surface based on this separation
            # (column, row)
            # use this one if surface.width is greater than surface.length
            # tuple -> (number of x separations, number of y separations)
            separate = [(i,j) for i in reversed(range(lower+1)) for j in range(upper, cpu_number+1) if i*j == cpu_number][0]

            if surface.length > surface.width:
                # reverse the order of separate
                separate = (separate[1], separate[0])

            # bacteria dimension that is smaller will be divided up by the first number in separate
            # create a list of tuple which indicates which values will be divided by what number
            # tuple -> (x,y)
            dividor = [[(i/separate[0],j/separate[1]) for i in range(0, separate[0]+1)] for j in range(0, separate[1]+1)]

            # initialize nested list
            possiblePointNested = []
            # this defines the number of columns
            for i in range(separate[0]):
                # this defines the number of rows
                for j in range(separate[1]):
                    points = [tup for tup in possiblePoint
                              if tup[0] > int(surface.length*dividor[0][i][0] + restriction)
                              and tup[0] < int(surface.length*dividor[0][i+1][0] - restriction)
                              and tup[1] > int(surface.width*dividor[j][0][1] + restriction)
                              and tup[1] < int(surface.width*dividor[j+1][0][1] - restriction)]
                    possiblePointNested.append(points)

        # for 3D, separate each side of the surface into 2 parts
        # elif surface.dimension == 3:
        #     # initialize nested list
        #     possiblePointNested = []
        #
        #     # first separate conditions into 2 parts
        #     # if the cpu_number is less than or equal to 6, divide surface by each side
        #     if cpu_number<=6:
        #         # the variable separate will tell how many separations we do on x,y,z faces
        #
        #         # separate -> [[x0, x1],[y0, y1],[z0, z1]]
        #         separator = [[False, False], [False, False], [False, False]]
        #         separate = [[1, 1], [1, 1], [1, 1]]
        #         for i in range(cpu_number - 1):
        #             v = int(i / 2)
        #             a = i % 2
        #             separator[v][a] = True
        #
        #             # by default, if there are 6 cpus, then the last surface will also be separated
        #             if separator[2][0] == True:
        #                 separator[2][1] = True
        #
        #         # now separate the points into the surfaces
        #         for axis in range(len(separator)):
        #             for i in range(len(separator[axis])):
        #                 # if we wish to separate the axis, execute the following
        #                 if separator[axis][i] == True:
        #                     # if the constant axis is on 0:
        #                     if i == 0:
        #                         points = [tup for tup in possiblePoint if tup[axis] == i]
        #                     # if the constant axis is on edge:
        #                     elif i == 1:
        #                         points = [tup for tup in possiblePoint if tup[axis] != 0]
        #
        #                     possiblePoint = list(set(possiblePoint) - set(points))
        #
        #                     # append the points to the possiblePointNested list
        #                     possiblePointNested.append(points)
        #
        #         # lastly, append the remaining possiblePoint into possiblePointNested list
        #         possiblePointNested.append(possiblePoint)


            # use partial to set all the constant variables
            _generateDomainMultiprocessingConstant = partial(self._generateDomainMultiprocessing, newSurface=newSurface,
                                                             domainWidth=domainWidth, domainLength=domainLength,
                                                             possible_charge=possible_charge, domainNumEach=domainNumEach,
                                                             generateShape=generateShape, checkEmpty=checkEmpty,
                                                             domainNumChar1=domainNumChar1, domainNumChar2=domainNumChar2)
            newSurfaceMPList = []
            generatedList = []
            with Pool(cpu_number) as pool:
                newSurfaceMP_generated = pool.map(_generateDomainMultiprocessingConstant, possiblePointNested)
                # extract the new surface and the number of generated domains for that surface
                for i in range(cpu_number):
                    newSurfaceMP = newSurfaceMP_generated[i][0]
                    generated = newSurfaceMP_generated[i][1]

                    # append both to a list
                    newSurfaceMPList.append(newSurfaceMP)
                    generatedList.append(generated)

            # now combine the arrays
            k = 0
            # this defines the number of columns
            for i in range(separate[0]):
                # this defines the number of rows
                for j in range(separate[1]):
                    newSurface[0, int(surface.width*dividor[j][0][1]):int(surface.width*dividor[j+1][0][1]),
                    int(surface.length*dividor[0][i][0]):int(surface.length*dividor[0][i+1][0])] = \
                        newSurfaceMPList[k][0, int(surface.width*dividor[j][0][1]):int(surface.width*dividor[j+1][0][1]),
                    int(surface.length*dividor[0][i][0]):int(surface.length*dividor[0][i+1][0])]
                    k += 1

            # current number of domains that have been generated
            # showMessage(generatedList)
            currentdomainNum = sum(generatedList)
            if domainNum > currentdomainNum:
                domainRemaining = domainNum - currentdomainNum
                if self.neutral:
                    domainNumChar1 = math.ceil(
                        domainRemaining * charge_concentration)  # this will have the first charge from the possible_charge list
                    domainNumChar2 = domainRemaining - domainNumChar1  # this will have the second charge from the possible_charge list
                elif not self.neutral:
                    domainNumChar1 = domainRemaining
                    domainNumChar2 = 0
                _generateDomainMultiprocessingConstant = partial(self._generateDomainMultiprocessing,
                                                                 newSurface=newSurface,
                                                                 domainWidth=domainWidth, domainLength=domainLength,
                                                                 possible_charge=possible_charge,
                                                                 domainNumEach=domainRemaining,
                                                                 generateShape=generateShape, checkEmpty=checkEmpty,
                                                                 domainNumChar1=domainNumChar1,
                                                                 domainNumChar2=domainNumChar2)
                [newSurface, generated] = _generateDomainMultiprocessingConstant(possiblePoint)
                generatedList.append(generated)

        # if the surface is a bacteria, we don't need multiprocessing since bacterias are small
        elif surface.height >= 4:
            # initialize all lists
            possiblePointx0 = []
            possiblePointx1 = []
            possiblePointy0 = []
            possiblePointy1 = []
            possiblePointz0 = []
            possiblePointz1 = []

            # create all possible point into a nested list
            for tup in possiblePoint:
                # x0
                if tup[0] == 0:
                    possiblePointx0.append(tup)
                # x1
                elif tup[0] == int(surface.length-1):
                    possiblePointx1.append(tup)
                # y0
                elif tup[1] == 0:
                    possiblePointy0.append(tup)
                # y1
                elif tup[1] == int(surface.width-1):
                    possiblePointy1.append(tup)
                # z0
                elif tup[2] == 0:
                    possiblePointz0.append(tup)
                # z1
                elif tup[2] == int(surface.height - 1):
                    possiblePointz1.append(tup)
            possiblePointSide = [possiblePointx0, possiblePointx1, possiblePointy0, possiblePointy1, possiblePointz0, possiblePointz1]

            # possiblePointSide = [[tup if tup[0] == 0], [tup if tup[0] == surface.length-1],
            #                      [tup if tup[1] == 0], [tup if tup[1] == surface.width-1],
            #                      [tup if tup[2] == 0], [tup if tup[2] == surface.height-1]for tup in possiblePoint]
            for i in range(len(possiblePointSide)):
                # determine how many neutral or charged domains for the surface
                if self.neutral:
                    domainNumChar1 = math.ceil(
                        domainNum * charge_concentration)  # this will have the first charge from the possible_charge list
                    domainNumChar2 = domainNum[i] - domainNumChar1  # this will have the second charge from the possible_charge list
                elif not self.neutral:
                    domainNumChar1 = domainNum[i]
                    domainNumChar2 = 0

                newSurfaceGenerated = self._generateDomainMultiprocessing(possiblePoint=possiblePointSide[i], newSurface=newSurface,
                                                                 domainWidth=domainWidth, domainLength=domainLength,
                                                                 possible_charge=possible_charge, domainNumEach=domainNum[i],
                                                                 generateShape=generateShape, checkEmpty=checkEmpty,
                                                                 domainNumChar1=domainNumChar1, domainNumChar2=domainNumChar2)
                newSurface = newSurfaceGenerated[0]

        # now, we will determine where
        concentration_charge = (len(np.where(newSurface == possible_charge[0])[0])) / (surface.length * surface.width)
        concentration_neutral = (len(np.where(newSurface == possible_charge[1])[0])) / (surface.length * surface.width)

        endTime = time.time()
        totalTime = endTime - startTime
        showMessage(f"Total time it took for generating domain is {totalTime} seconds")
        return newSurface, (concentration_charge, concentration_neutral)

    def _generateDomainMultiprocessing(self, possiblePoint: List[int], newSurface: ndarray, domainWidth: int,
                                       domainLength: int,possible_charge: List[int], domainNumEach: int,
                                       generateShape, checkEmpty, domainNumChar1: int, domainNumChar2: int) -> [ndarray, int]:
        """
        This function actually generates the domains
        It was implemented as a test for multiprocessing
        Return the number of generated domains as well as the film
        """
        # initialize totalDomainChar
        totalDomainChar = [0,0]

        # initialize how long we want the code to run
        # if its running for too long, that means we most likely reached the maximum amount of domains on the surface and
        # end the while loop
        timeout = time.time() + WAIT_TIME  # 60 seconds from now

        # initialize generated
        generated = 0

        # start to generate the domain on surface
        # to generate the domains on the surface, we will be using multiprocessing to take advantage of all 4 CPUS
        while generated < domainNumEach:
            # if the while loop has been running for too long, break the while loop
            if time.time() > timeout or len(possiblePoint) == 0:
                break
            # initialize a random point on the surface with restrictions and the updated possiblePoint
            [start, possiblePoint] = self._randomPoint(possiblePoint)

            # check the position of this shape is empty, if not empty, then continue
            if not checkEmpty(newSurface, domainWidth, domainLength, start, possible_charge):
                continue

            # we will first generate all the domainNumChar1
            if domainNumChar1 > totalDomainChar[0]:
                charge = possible_charge[0]
            # once that has fully generated, we will move onto domainNumChar2
            elif domainNumChar2 > totalDomainChar[1]:
                charge = possible_charge[1]

            # generate this shape's domain
            newSurface = generateShape(newSurface, domainWidth, domainLength, start, charge)

            # update the generated number in totalDomainChar
            if charge == possible_charge[0]:
                totalDomainChar[0] += 1
            elif charge == possible_charge[1]:
                totalDomainChar[1] += 1

            # update generated number
            generated += 1

            # initialize how long we want the code to run
            # if its running for too long, that means we most likely reached the maximum amount of domains on the surface and
            # end the while loop
            timeout = time.time() + WAIT_TIME  # 60 seconds from now

        # combine the new surface and total number of domains generated into a list
        surface_generated = [newSurface, generated]
        return surface_generated

    def _allPoints(self, newSurface: ndarray) -> List[int]:
        """
        This function calculates all points on the surface on each plane
        _allPoints -> [x0, x1, y0, y1, z0, z1]
        """
        return [len(np.where(newSurface[:,:,0] != 2)[0]), len(np.where(newSurface[:,:,newSurface.shape[2]-1] != 2)[0]),
                   len(np.where(newSurface[:,0,:] != 2)[0]), len(np.where(newSurface[:,newSurface.shape[1]-1,:] != 2)[0]),
                   len(np.where(newSurface[0,:,:] != 2)[0]), len(np.where(newSurface[newSurface.shape[0]-1,:,:] != 2)[0])]

    def _allPossiblePoint(self, newSurface: ndarray, surface: Surface, surfaceLength: int, surfaceWidth: int, surfaceHeight: int,
                          domainLength: int, domainWidth: int, shape: str) -> List[Tuple[int, int, int]]:
        """
        This function determines all the possible points the random point can start
        This function was created for 2 reasons:
            1. Function _randomPoint was getting too long
            2. It increases speed of the code since it now only chooses positions that has not already been chosen and
            avoids going through for loops each time _randomPoint function is called
        """
        # For diamond shape domain
        if shape.upper() == "DIAMOND":
            # Set restrictions on where the starting position can be
            # for 2D surface
            if surface.dimension == 2:
                # if the dimension is 2, we don't have to worry about z since it will just be zero
                x_possibility = range(domainLength + 1, surfaceLength - domainLength - 1)
                y_possibility = range(domainWidth + 1, surfaceWidth - domainWidth - 1)
                z_possibility = [0]
                # create list with all possible coordinates using list comprehension
                possibleCoordinate = [(i, j, k) for i in x_possibility for j in y_possibility for k in z_possibility]

            # for 3D surface
            elif surface.dimension == 3:
                # define all the possible coordinates where domain can be generated
                x_possibility = range(domainLength + 2 + min(np.where(newSurface != 2)[2]),
                                      max(np.where(newSurface != 2)[2]) - domainLength - 2)
                y_possibility = range(domainWidth + 2 + min(np.where(newSurface != 2)[1]),
                                      max(np.where(newSurface != 2)[1]) - domainWidth - 2)
                z_possibility = range(domainWidth + 2 + min(np.where(newSurface != 2)[0]),
                                      max(np.where(newSurface != 2)[0]) - domainWidth - 2)

                if surface.shape.upper() == "CUBOID" or surface.shape.upper() == "RECTANGLE":
                    # create list with all possible coordinates using list comprehension
                    # when x is constant
                    possibleCoordinate1 = [(i, j, k) for i in [0, int(surface.length) - 1] for j in y_possibility for k
                                           in z_possibility]
                    # when y is constant
                    possibleCoordinate2 = [(i, j, k) for i in x_possibility for j in [0, int(surface.width) - 1] for k
                                           in z_possibility]
                    # when z is constant
                    possibleCoordinate3 = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                           [0, int(surface.height) - 1]]

                elif surface.shape.upper() == "SPHERE":
                    # initalize the center point of the circles
                    # center = (x,y,z)
                    center = (int(np.floor(surface.length/2)), int(np.floor(surface.width/2)), int(np.floor(surface.height/2)))
                    radius = min(np.floor(surface.length/2) - domainWidth, np.floor(surface.width/2) - domainWidth,
                                 np.floor(surface.height/2) - domainWidth)

                    # create list with all possible coordinates using list comprehension
                    # when x is constant
                    possibleCoordinate1 = [(i, j, k) for i in [0, int(surface.length) - 1] for j in y_possibility for k in
                                           z_possibility if (j-center[1])**2 + (k-center[2])**2 < radius**2]
                    # when y is constant
                    possibleCoordinate2 = [(i, j, k) for i in x_possibility for j in [0, int(surface.width) - 1] for k in
                                           z_possibility if (i-center[0])**2 + (k-center[2])**2 < radius**2]
                    # when z is constant
                    possibleCoordinate3 = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                           [0, int(surface.height) - 1] if (i-center[0])**2 + (j-center[1])**2 < radius**2]

                elif surface.shape.upper() == "CYLINDER":
                    # initalize the center point of the circles
                    # center = (x,y,z)
                    center = (int(np.floor(surface.length / 2)), int(np.floor(surface.width / 2)),
                              int(np.floor(surface.height / 2)))
                    radius = min(np.floor(surface.length / 2) - domainWidth, np.floor(surface.width / 2) - domainWidth,
                                 np.floor(surface.height / 2) - domainWidth) - 1

                    # create list with all possible coordinates using list comprehension
                    # when x is constant
                    possibleCoordinate1 = [(i, j, k) for i in [0, int(surface.length) - 1] for j in y_possibility for k
                                           in z_possibility]
                    # when y is constant
                    possibleCoordinate2 = [(i, j, k) for i in x_possibility for j in [0, int(surface.width) - 1] for k
                                           in z_possibility]
                    # when z is constant
                    possibleCoordinate3 = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                           [0, int(surface.height) - 1] if
                                           (i - center[0]) ** 2 + (j - center[1]) ** 2 < radius ** 2]

                elif surface.shape.upper() == "ROD":
                    # initalize the center point of the circles
                    rod_dim = min(surface.length, surface.width, surface.height)

                    # center = (x,y,z)
                    if rod_dim % 2 == 1:
                        center = (int(np.floor(surface.length / 2)), int(np.floor(surface.width / 2)),
                                  int(np.floor(surface.height / 2)))
                    else:
                        center = (int(np.floor(surface.length / 2) - 1), int(np.floor(surface.width / 2)),
                                   int(np.floor(surface.height / 2)))

                    radius = np.floor(rod_dim/5)

                    # create list with all possible coordinates using list comprehension
                    # when x is constant
                    possibleCoordinate1 = [(i, j, k) for i in [0, int(surface.length) - 1] for j in y_possibility for k
                                           in z_possibility]
                    # when y is constant
                    possibleCoordinate2 = [(i, j, k) for i in x_possibility for j in [0, int(surface.width) - 1] for k
                                           in z_possibility]
                    # when z is constant
                    possibleCoordinate3 = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                           [0, int(surface.height) - 1] if
                                           (i - center[0]) ** 2 + (j - center[1]) ** 2 < radius ** 2]

                # add all possible coordinates for each axis to get all possible coordinates
                possibleCoordinate = possibleCoordinate1 + possibleCoordinate2 + possibleCoordinate3


        # for cross shape domain
        elif shape.upper() == "CROSS":
            # Set restrictions on where the starting positions can be
            # for 2D surface
            if surface.dimension == 2:
                x_possibility = range(domainLength + 1, surfaceLength - domainLength - 1)
                y_possibility = range(domainWidth + 1, surfaceWidth - domainWidth - 1)
                z_possibility = [0]
                # create list with all possible coordinates using list comprehension
                possibleCoordinate = [(i, j, k) for i in x_possibility for j in y_possibility for k in z_possibility]

            # for 3D surface
            elif surface.dimension == 3:
                # define all the possible coordinates where domain can be generated
                x_possibility = range(domainLength + 2 + min(np.where(newSurface != 2)[2]),
                                      max(np.where(newSurface != 2)[2]) - domainLength - 2)
                y_possibility = range(domainWidth + 2 + min(np.where(newSurface != 2)[1]),
                                      max(np.where(newSurface != 2)[1]) - domainWidth - 2)
                z_possibility = range(domainWidth + 2 + min(np.where(newSurface != 2)[0]),
                                      max(np.where(newSurface != 2)[0]) - domainWidth - 2)

                if surface.shape.upper() == "CUBOID" or surface.shape.upper() == "RECTANGLE":
                    # create list with all possible coordinates using list comprehension
                    # when x is constant
                    possibleCoordinate1 = [(i, j, k) for i in [0, int(surface.length) - 1] for j in y_possibility for k
                                           in
                                           z_possibility]
                    # when y is constant
                    possibleCoordinate2 = [(i, j, k) for i in x_possibility for j in [0, int(surface.width) - 1] for k
                                           in
                                           z_possibility]
                    # when z is constant
                    possibleCoordinate3 = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                           [0, int(surface.height) - 1]]

                elif surface.shape.upper() == "SPHERE":
                    # initalize the center point of the circles
                    # center = (x,y,z)
                    center = (int(np.floor(surface.length / 2)), int(np.floor(surface.width / 2)),
                              int(np.floor(surface.height / 2)))
                    radius = min(np.floor(surface.length / 2) - domainLength, np.floor(surface.width / 2) - domainWidth,
                                 np.floor(surface.height / 2) - domainWidth) - 1

                    # create list with all possible coordinates using list comprehension
                    # when x is constant
                    possibleCoordinate1 = [(i, j, k) for i in [0, int(surface.length) - 1] for j in y_possibility for k
                                           in
                                           z_possibility if (j - center[1]) ** 2 + (k - center[2]) ** 2 < radius ** 2]
                    # when y is constant
                    possibleCoordinate2 = [(i, j, k) for i in x_possibility for j in [0, int(surface.width) - 1] for k
                                           in
                                           z_possibility if (i - center[0]) ** 2 + (k - center[2]) ** 2 < radius ** 2]
                    # when z is constant
                    possibleCoordinate3 = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                           [0, int(surface.height) - 1] if
                                           (i - center[0]) ** 2 + (j - center[1]) ** 2 < radius ** 2]

                elif surface.shape.upper() == "CYLINDER":
                    # initalize the center point of the circles
                    # center = (x,y,z)
                    center = (int(np.floor(surface.length / 2)), int(np.floor(surface.width / 2)),
                              int(np.floor(surface.height / 2)))
                    radius = min(np.floor(surface.length / 2) - domainLength, np.floor(surface.width / 2) - domainWidth,
                                 np.floor(surface.height / 2) - domainWidth) - 1

                    # create list with all possible coordinates using list comprehension
                    # when x is constant
                    possibleCoordinate1 = [(i, j, k) for i in [0, int(surface.length) - 1] for j in y_possibility for k
                                           in z_possibility]
                    # when y is constant
                    possibleCoordinate2 = [(i, j, k) for i in x_possibility for j in [0, int(surface.width) - 1] for k
                                           in z_possibility]
                    # when z is constant
                    possibleCoordinate3 = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                           [0, int(surface.height) - 1] if
                                           (i - center[0]) ** 2 + (j - center[1]) ** 2 < radius ** 2]

                elif surface.shape.upper() == "ROD":
                    # initalize the center point of the circles
                    rod_dim = min(surface.length, surface.width, surface.height)

                    # center = (x,y,z)
                    if rod_dim % 2 == 1:
                        center = (int(np.floor(surface.length / 2)), int(np.floor(surface.width / 2)),
                                  int(np.floor(surface.height / 2)))
                    else:
                        center = (int(np.floor(surface.length / 2) - 1), int(np.floor(surface.width / 2)),
                                   int(np.floor(surface.height / 2)))

                    radius = np.floor(rod_dim/5)

                    # create list with all possible coordinates using list comprehension
                    # when x is constant
                    possibleCoordinate1 = [(i, j, k) for i in [0, int(surface.length) - 1] for j in y_possibility for k
                                           in z_possibility]
                    # when y is constant
                    possibleCoordinate2 = [(i, j, k) for i in x_possibility for j in [0, int(surface.width) - 1] for k
                                           in z_possibility]
                    # when z is constant
                    possibleCoordinate3 = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                           [0, int(surface.height) - 1] if
                                           (i - center[0]) ** 2 + (j - center[1]) ** 2 < radius ** 2]

                # add all possible coordinates for each axis to get all possible coordinates
                possibleCoordinate = possibleCoordinate1 + possibleCoordinate2 + possibleCoordinate3


        # for octagon shape domain
        elif shape.upper() == "OCTAGON":
            # Set restriction on where the starting positions can be
            # for 2D surface
            if surface.dimension == 2:
                # Separate cases for when domainLength/domainWidth are either even or odd
                if domainLength % 2 == 0:
                    x_possibility = range(int(domainLength + (domainLength / 2) + 1),
                                          int(surfaceLength - domainLength - (domainLength / 2) - 1))
                    y_possibility = range(int(domainWidth + (domainWidth / 2) + 1),
                                          int(surfaceWidth - domainWidth - (domainWidth / 2) - 1))
                    z_possibility = [0]
                elif domainLength % 2 == 1:
                    x_possibility = range(int(domainLength + ((domainLength + 1) / 2) + 1),
                                          int(surfaceLength - domainLength - ((domainLength + 1) / 2) - 1))
                    y_possibility = range(int(domainWidth + ((domainWidth + 1) / 2) + 1),
                                          int(surfaceWidth - domainWidth - ((domainWidth + 1) / 2) - 1))
                    z_possibility = [0]
                # create list with all possible coordinates using list comprehension
                possibleCoordinate = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                      z_possibility]

            # for 3D surface
            elif surface.dimension == 3:
                # Set restriction on where the starting positions can be
                # Separate cases for when domainLength/domainWidth are either even or odd
                # if the domainLength is an even number
                if domainLength % 2 == 0:
                    # define all the possible coordinates where domain can be generated
                    x_possibility = range(int(3*domainLength/2) + 2 + min(np.where(newSurface != 2)[2]),
                                          int(max(np.where(newSurface != 2)[2]) - (3*domainLength/2) - 2))
                    y_possibility = range(int(3*domainWidth/2) + 2 + min(np.where(newSurface != 2)[1]),
                                          int(max(np.where(newSurface != 2)[1]) - (3*domainWidth/2) - 2))
                    z_possibility = range(int(3*domainWidth/2) + 2 + min(np.where(newSurface != 2)[0]),
                                          int(max(np.where(newSurface != 2)[0]) - (3*domainWidth/2) - 2))
                # if the domainLength is an odd number
                elif domainLength % 2 == 1:
                    x_possibility = range(int((3*domainLength+1)/2) + 2 + min(np.where(newSurface != 2)[2]),
                                          int(max(np.where(newSurface != 2)[2]) - (3*domainLength+1)/2 - 2))
                    y_possibility = range(int((3 * domainWidth + 1) / 2) + 2 + min(np.where(newSurface != 2)[1]),
                                          int(max(np.where(newSurface != 2)[1]) - (3 * domainWidth + 1) / 2 - 2))
                    z_possibility = range(int((3 * domainWidth + 1) / 2) + 2 + min(np.where(newSurface != 2)[0]),
                                          int(max(np.where(newSurface != 2)[0]) - (3 * domainWidth + 1) / 2 - 2))

                # for 3D surface
                if surface.shape.upper() == "CUBOID" or surface.shape.upper() == "RECTANGLE":
                    # create list with all possible coordinates using list comprehension
                    # when x is constant
                    possibleCoordinate1 = [(i, j, k) for i in [0, int(surface.length) - 1] for j in y_possibility for k
                                           in z_possibility]
                    # when y is constant
                    possibleCoordinate2 = [(i, j, k) for i in x_possibility for j in [0, int(surface.width) - 1] for k
                                           in z_possibility]
                    # when z is constant
                    possibleCoordinate3 = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                           [0, int(surface.height) - 1]]

                elif surface.shape.upper() == "SPHERE":
                    # initalize the center point of the circles
                    # center = (x,y,z)
                    center = (int(np.floor(surface.length / 2)), int(np.floor(surface.width / 2)),
                              int(np.floor(surface.height / 2)))
                    radius = min(np.floor(surface.length / 2) - (3/2)*domainWidth, np.floor(surface.width / 2) - (3/2)*domainWidth,
                                 np.floor(surface.height / 2) - (3/2)*domainWidth) - 1

                    # create list with all possible coordinates using list comprehension
                    # when x is constant
                    possibleCoordinate1 = [(i, j, k) for i in [0, int(surface.length) - 1] for j in y_possibility for k
                                           in z_possibility if (j - center[1]) ** 2 + (k - center[2]) ** 2 < radius ** 2]
                    # when y is constant
                    possibleCoordinate2 = [(i, j, k) for i in x_possibility for j in [0, int(surface.width) - 1] for k
                                           in z_possibility if (i - center[0]) ** 2 + (k - center[2]) ** 2 < radius ** 2]
                    # when z is constant
                    possibleCoordinate3 = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                           [0, int(surface.height) - 1] if
                                           (i - center[0]) ** 2 + (j - center[1]) ** 2 < radius ** 2]

                elif surface.shape.upper() == "CYLINDER":
                    # initalize the center point of the circles
                    # center = (x,y,z)
                    center = (int(np.floor(surface.length / 2)), int(np.floor(surface.width / 2)),
                              int(np.floor(surface.height / 2)))
                    radius = min(np.floor(surface.length / 2) - (3/2)*domainWidth, np.floor(surface.width / 2) - (3/2)*domainWidth,
                                 np.floor(surface.height / 2) - (3/2)*domainWidth) - 1

                    # create list with all possible coordinates using list comprehension
                    # when x is constant
                    possibleCoordinate1 = [(i, j, k) for i in [0, int(surface.length) - 1] for j in y_possibility for k
                                           in z_possibility]
                    # when y is constant
                    possibleCoordinate2 = [(i, j, k) for i in x_possibility for j in [0, int(surface.width) - 1] for k
                                           in z_possibility]
                    # when z is constant
                    possibleCoordinate3 = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                           [0, int(surface.height) - 1] if
                                           (i - center[0]) ** 2 + (j - center[1]) ** 2 < radius ** 2]

                elif surface.shape.upper() == "ROD":
                    # initalize the center point of the circles
                    rod_dim = min(surface.length, surface.width, surface.height)

                    # center = (x,y,z)
                    if rod_dim % 2 == 1:
                        center = (int(np.floor(surface.length / 2)), int(np.floor(surface.width / 2)),
                                  int(np.floor(surface.height / 2)))
                    else:
                        center = (int(np.floor(surface.length / 2) - 1), int(np.floor(surface.width / 2)),
                                   int(np.floor(surface.height / 2)))

                    radius = np.floor(rod_dim/5)

                    # create list with all possible coordinates using list comprehension
                    # when x is constant
                    possibleCoordinate1 = [(i, j, k) for i in [0, int(surface.length) - 1] for j in y_possibility for k
                                           in z_possibility]
                    # when y is constant
                    possibleCoordinate2 = [(i, j, k) for i in x_possibility for j in [0, int(surface.width) - 1] for k
                                           in z_possibility]
                    # when z is constant
                    possibleCoordinate3 = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                           [0, int(surface.height) - 1] if
                                           (i - center[0]) ** 2 + (j - center[1]) ** 2 < radius ** 2]
                # add all possible coordinates for each axis to get all possible coordinates
                possibleCoordinate = possibleCoordinate1 + possibleCoordinate2 + possibleCoordinate3


        # for single shape domain
        elif shape.upper() == "SINGLE":
            # Set restriction on where the starting positions can be
            # for 2D surface
            if surface.dimension == 2:
                # If the surface is 2D, x and y just has to be on the rectangle surface
                # define all the possible coordinates where domain can be generated
                x_possibility = range(2, surfaceLength - 2)
                y_possibility = range(2, surfaceWidth - 2)
                z_possibility = [0]
                # create list with all possible coordinates using list comprehension
                possibleCoordinate = [(i, j, k) for i in x_possibility for j in y_possibility for k in z_possibility]

            # for 3D surface
            elif surface.dimension == 3:
                # define all the possible coordinates where domain can be generated
                x_possibility = range(min(np.where(newSurface != 2)[2]),
                                      max(np.where(newSurface != 2)[2]))
                y_possibility = range(min(np.where(newSurface != 2)[1]),
                                      max(np.where(newSurface != 2)[1]))
                z_possibility = range(min(np.where(newSurface != 2)[0]),
                                      max(np.where(newSurface != 2)[0]))
                if surface.shape.upper() == "RECTANGLE" or surface.shape.upper() == "CUBOID":
                    # create list with all possible coordinates using list comprehension
                    # when x is constant
                    possibleCoordinate1 = [(i, j, k) for i in [0, int(surface.length) - 1] for j in y_possibility for k
                                           in
                                           z_possibility]
                    # when y is constant
                    possibleCoordinate2 = [(i, j, k) for i in x_possibility for j in [0, int(surface.width) - 1] for k
                                           in
                                           z_possibility]
                    # when z is constant
                    possibleCoordinate3 = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                           [0, int(surface.height) - 1]]

                elif surface.shape.upper() == "SPHERE":
                    # initalize the center point of the circles
                    # center = (x,y,z)
                    center = (int(np.floor(surface.length / 2)), int(np.floor(surface.width / 2)),
                              int(np.floor(surface.height / 2)))
                    radius = min(np.floor(surface.length/2), np.floor(surface.width/2), np.floor(surface.height/2)) - 1

                    # create list with all possible coordinates using list comprehension
                    # when x is constant
                    possibleCoordinate1 = [(i, j, k) for i in [0, int(surface.length) - 1] for j in y_possibility for k
                                           in z_possibility if
                                           (j - center[1]) ** 2 + (k - center[2]) ** 2 < radius ** 2]
                    # when y is constant
                    possibleCoordinate2 = [(i, j, k) for i in x_possibility for j in [0, int(surface.width) - 1] for k
                                           in z_possibility if
                                           (i - center[0]) ** 2 + (k - center[2]) ** 2 < radius ** 2]
                    # when z is constant
                    possibleCoordinate3 = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                           [0, int(surface.height) - 1] if
                                           (i - center[0]) ** 2 + (j - center[1]) ** 2 < radius ** 2]

                elif surface.shape.upper() == "CYLINDER":
                    # initalize the center point of the circles
                    # center = (x,y,z)
                    center = (int(np.floor(surface.length / 2)), int(np.floor(surface.width / 2)),
                              int(np.floor(surface.height / 2)))
                    radius = min(np.floor(surface.length/2), np.floor(surface.width/2), np.floor(surface.height/2)) - 1

                    # create list with all possible coordinates using list comprehension
                    # when x is constant
                    possibleCoordinate1 = [(i, j, k) for i in [0, int(surface.length) - 1] for j in y_possibility for k
                                           in z_possibility]
                    # when y is constant
                    possibleCoordinate2 = [(i, j, k) for i in x_possibility for j in [0, int(surface.width) - 1] for k
                                           in z_possibility]
                    # when z is constant
                    possibleCoordinate3 = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                           [0, int(surface.height) - 1] if
                                           (i - center[0]) ** 2 + (j - center[1]) ** 2 < radius ** 2]

                elif surface.shape.upper() == "ROD":
                    # # define all the possible coordinates where domain can be generated
                    # initalize the center point of the circles
                    rod_dim = min(surface.length, surface.width, surface.height)

                    # center = (x,y,z)
                    if rod_dim % 2 == 1:
                        center = (int(np.floor(surface.length / 2)), int(np.floor(surface.width / 2)),
                                  int(np.floor(surface.height / 2)))
                    else:
                        center = (int(np.floor(surface.length / 2) - 1), int(np.floor(surface.width / 2)),
                                   int(np.floor(surface.height / 2)))

                    # initalize center of semicircles
                    radius = int(np.floor(rod_dim/5))
                    center_bottom = (center[0], center[1], int(min(np.where(newSurface != 2)[0]) + radius))

                    center_top = (center[0], center[1], int(max(np.where(newSurface != 2)[0]) - radius))


                    # create list with all possible coordinates using list comprehension
                    # when x is constant
                    possibleCoordinate1 = [(i, j, k) for i in [0, int(surface.length) - 1] for j in y_possibility for k
                                           in z_possibility if ((k>center_top[2] and (j - center_top[1]) ** 2 + (k - center_top[2]) ** 2 < radius ** 2)
                                           or (k<center_bottom[2] and (j - center_bottom[1]) ** 2 + (k - center_bottom[2]) ** 2 < radius ** 2) or
                                            (k<=center_top[2] and k>=center_bottom[2]))]
                    # when y is constant
                    possibleCoordinate2 = [(i, j, k) for i in x_possibility for j in [0, int(surface.width) - 1] for k
                                           in z_possibility if ((k>center_top[2] and (i - center_top[0]) ** 2 + (k - center_top[2]) ** 2 < radius ** 2)
                                           or (k<center_bottom[2] and (i - center_bottom[0]) ** 2 + (k - center_bottom[2]) ** 2 < radius ** 2) or
                                            (k<=center_top[2] and k>=center_bottom[2]))]
                    # when z is constant
                    possibleCoordinate3 = [(i, j, k) for i in x_possibility for j in y_possibility for k in
                                           [0, int(surface.height) - 1] if
                                           (i - center[0]) ** 2 + (j - center[1]) ** 2 < radius ** 2]

                # add all possible coordinates for each axis to get all possible coordinates
                possibleCoordinate = possibleCoordinate1 + possibleCoordinate2 + possibleCoordinate3

        else:
            raise RuntimeError("Wrong shape in the function _allPossiblePoint")

        return possibleCoordinate

    def _randomPoint(self, possiblePoint: List[Tuple[int, int, int]]) \
            -> [Tuple[int, int, int], List[Tuple[int, int, int]]]:
        """
        Randomly pick a point on the surface given
        :return a tuple represent a point in the surface in the matrix
        NOTE: For the 2D surface, it is currently under the assumption that it is a RECTANGLE. Therefore need to change
        for different shape for 2D
        """
        # writeLog("This is _randomPoint in Domain.py")
        # writeLog([self.__dict__, surfaceLength, surfaceWidth, domainLength, domainWidth, shape])
        # choose a random index
        index = np.random.randint(len(possiblePoint))
        # return the coordinate
        coordinate = possiblePoint[index]
        # remove the chosen coordinate from all possiblepoints
        try:
            possiblePoint.pop(index)
        except AttributeError:
            print(len(possiblePoint))

        # writeLog("Point picked is: {}".format(coordinate))

        # return the result as tuple
        return coordinate, possiblePoint

    def nearestPoint(self, surface: Surface, point: List[Union[int, int, int]]) -> List[Union[int, int, int]]:
        """
        This function takes in a point and returns a point closest to that point on the surface
        NOTE: the function takes in point differently than other functions
        point = Tuple[z,y,x]
        nearestPoint = Tuple[z,y,x]
        charge = charge of domain
        """

        # for a 2D surface, return the point since we don't need to traverse through the z-axis
        if surface.shape[0] == 1:
            return point

        # if the point is already on the surface, return the point
        if surface[point[0], point[1], point[2]] != 2:
            return point

        # define condition where closest point is found
        found = False

        # Split the condition into different scenarios
        # if the point is generated on the far right side of the array
        if point[2] == int(surface.shape[2]) - 1:
            while not found:
                # search by moving left
                point[2] -= 1
                # check if the point is on the surface
                if surface[point[0], point[1], point[2]] != 2:
                    found = True

        # if the point is generated on the far left side of the array
        elif point[2] == 0:
            while not found:
                # search by moving right
                point[2] += 1
                # check if the point is on the surface
                if surface[point[0], point[1], point[2]] != 2:
                    found = True

        # if the point is generated on the far behind the array
        if point[1] == 0:
            while not found:
                # search by moving down
                point[1] += 1
                # check if the point is on the surface
                if surface[point[0], point[1], point[2]] != 2:
                    found = True

        # if the point is generated on the far infront the array
        elif point[1] == int(surface.shape[1]) - 1:
            while not found:
                # search by moving up
                point[1] -= 1
                # check if the point is on the surface
                if surface[point[0], point[1], point[2]] != 2:
                    found = True

        # if the point is generated on the far above the array
        elif point[0] == 0:
            while not found:
                # search by moving below
                point[0] += 1
                # check if the point is on the surface
                if surface[point[0], point[1], point[2]] != 2:
                    found = True

        # if the point is generated on the far below the array
        elif point[0] == int(surface.shape[0]) - 1:
            while not found:
                # search by moving below
                point[0] -= 1
                # check if the point is on the surface
                if surface[point[0], point[1], point[2]] != 2:
                    found = True
        return point

    def _diamondEmpty(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int, int],
                      possible_charge: List[int]) -> bool:
        """
        This function check the position we want to generate diamond is empty
        :return True if all empty, False for no
        charge -> the charge of the domain
        possible_charge -> all possible charges the domain can have (a tuple with 2 integers either 0,1,-1)
        """

        ln = domainWidth
        # Fill out diamond triangles
        eg = domainWidth + 1

        # in x-z plane:
        if startPoint[1] == 0 or startPoint[1] == int(surface.shape[1]) - 1:
            for i in range(0, ln + 1):
                for j in range(0, eg):

                    # top right
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), startPoint[1], int(startPoint[0] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                    # top left
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), startPoint[1], int(startPoint[0] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                    # bottom right
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), startPoint[1], int(startPoint[0] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                    # bottom left
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), startPoint[1], int(startPoint[0] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                eg -= 1

        # in x-y plane
        if startPoint[2] == 0 or startPoint[2] == int(surface.shape[0]) - 1:
            for i in range(0, ln + 1):
                for j in range(0, eg):

                    # top right
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] - i), int(startPoint[0] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                    # top left
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] - i), int(startPoint[0] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                    # bottom right
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] + i), int(startPoint[0] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                    # bottom left
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] + i), int(startPoint[0] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                eg -= 1

        # in y-z plane
        if startPoint[0] == 0 or startPoint[0] == int(surface.shape[2]) - 1:
            for i in range(0, ln + 1):
                for j in range(0, eg):

                    # top right
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), int(startPoint[1] + j), startPoint[0]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                    # top left
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), int(startPoint[1] - j), startPoint[0]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                    # bottom right
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), int(startPoint[1] + j), startPoint[0]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                    # bottom left
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), int(startPoint[1] - j), startPoint[0]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                eg -= 1

        return True

    def _generateDiamond(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int, int],
                         charge: int) -> ndarray:
        """
        This function generate diamond shape domain
        :return return the surface with diamond domain on it
        """
        ln = domainWidth
        # Fill out diamond triangles
        eg = domainWidth + 1

        # in x-z plane:
        if startPoint[1] == 0 or startPoint[1] == int(surface.shape[1]) - 1:
            for i in range(0, ln + 1):
                for j in range(0, eg):

                    # top right
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), startPoint[1], int(startPoint[0] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                    # top left
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), startPoint[1], int(startPoint[0] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                    # bottom right
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), startPoint[1], int(startPoint[0] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                    # bottom left
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), startPoint[1], int(startPoint[0] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1


                eg -= 1

        # in x-y plane
        if startPoint[2] == 0 or startPoint[2] == int(surface.shape[0]) - 1:
            for i in range(0, ln + 1):
                for j in range(0, eg):

                    # top right
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] - i), int(startPoint[0] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                    # top left
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] - i), int(startPoint[0] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                    # bottom right
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] + i), int(startPoint[0] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                    # bottom left
                    point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] + i), int(startPoint[0] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                eg -= 1

        # in y-z plane
        if startPoint[0] == 0 or startPoint[0] == int(surface.shape[2]) - 1:
            for i in range(0, ln + 1):
                for j in range(0, eg):

                    # top right
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), int(startPoint[1] + j), startPoint[0]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                    # top left
                    point = self.nearestPoint(surface, [int(startPoint[2] - i), int(startPoint[1] - j), startPoint[0]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                    # bottom right
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), int(startPoint[1] + j), startPoint[0]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                    # bottom left
                    point = self.nearestPoint(surface, [int(startPoint[2] + i), int(startPoint[1] - j), startPoint[0]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge
                    # count_charge += 1

                eg -= 1
        return surface

    def _crossEmpty(self, surface: Surface, domainWidth: int, domainLength: int, startPoint: Tuple[int, int, int],
                    possible_charge: List[int]) -> bool:
        """
        This function check the position we want to generate cross is empty
        :return True if all empty, False for no
        """

        # in the y-z plane (keep x constant)
        if startPoint[0] == 0 or startPoint[0] == int(surface.shape[2]) - 1:
            # create the vertical line of the cross
            for i in range(domainWidth + 1):
                # bottom line
                point = self.nearestPoint(surface, [int(startPoint[2] + i), int(startPoint[1]), startPoint[0]])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

                # top line
                point = self.nearestPoint(surface, [int(startPoint[2] - i), int(startPoint[1]), startPoint[0]])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

            # create the horizontal line of the cross
            for j in range(domainLength + 1):
                # right line
                point = self.nearestPoint(surface, [int(startPoint[2]), int(startPoint[1] + j), startPoint[0]])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

                # left line
                point = self.nearestPoint(surface, [int(startPoint[2]), int(startPoint[1] - j), startPoint[0]])
                if surface[point[0], point[1], point[2]] == 0:
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        return False

        # in the x-z plane (keep y constant)
        if startPoint[1] == 0 or startPoint[1] == int(surface.shape[1]) - 1:
            # create the vertical line of the cross
            for i in range(domainWidth + 1):
                # bottom line
                point = self.nearestPoint(surface, [int(startPoint[2] + i), startPoint[1], int(startPoint[0])])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

                # top line
                point = self.nearestPoint(surface, [int(startPoint[2] - i), startPoint[1], int(startPoint[0])])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

            # create the horizontal line of the cross
            for j in range(domainLength + 1):
                # right line
                point = self.nearestPoint(surface, [int(startPoint[2]), startPoint[1], int(startPoint[0] + j)])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

                # left line
                point = self.nearestPoint(surface, [int(startPoint[2]), startPoint[1], int(startPoint[0] - j)])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

        # in the x-y plane (keep z constant)
        if startPoint[2] == 0 or startPoint[2] == int(surface.shape[0]) - 1:
            # create the vertical line of the cross
            for i in range(domainWidth + 1):
                # bottom line
                point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] + i), int(startPoint[0])])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

                # top line
                point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] - i), int(startPoint[0])])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

            # create the horizontal line of the cross
            for j in range(domainLength + 1):
                # right line
                point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1]), int(startPoint[0] + j)])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False

                # left line
                point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1]), int(startPoint[0] - j)])
                if surface[point[0], point[1], point[2]] in possible_charge:
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    return False
        return True
    def _generateCross(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int, int],
                       charge: int) -> ndarray:
        """
        This function generate cross shape for surface
        """
        # in the y-z plane (keep x constant)
        if startPoint[0] == 0 or startPoint[0] == int(surface.shape[2]) - 1:
            # create the vertical line of the cross
            for i in range(domainWidth + 1):
                # bottom line
                point = self.nearestPoint(surface, [int(startPoint[2] + i), int(startPoint[1]), startPoint[0]])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

                # top line
                point = self.nearestPoint(surface, [int(startPoint[2] - i), int(startPoint[1]), startPoint[0]])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

            # create the horizontal line of the cross
            for j in range(domainLength + 1):
                # right line
                point = self.nearestPoint(surface, [int(startPoint[2]), int(startPoint[1] + j), startPoint[0]])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

                # left line
                point = self.nearestPoint(surface, [int(startPoint[2]), int(startPoint[1] - j), startPoint[0]])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

        # in the x-z plane (keep y constant)
        if startPoint[1] == 0 or startPoint[1] == int(surface.shape[1]) - 1:
            # create the vertical line of the cross
            for i in range(domainWidth + 1):
                # bottom line
                point = self.nearestPoint(surface, [int(startPoint[2] + i), startPoint[1], int(startPoint[0])])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

                # top line
                point = self.nearestPoint(surface, [int(startPoint[2] - i), startPoint[1], int(startPoint[0])])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

            # create the horizontal line of the cross
            for j in range(domainLength + 1):
                # right line
                point = self.nearestPoint(surface, [int(startPoint[2]), startPoint[1], int(startPoint[0] + j)])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

                # left line
                point = self.nearestPoint(surface, [int(startPoint[2]), startPoint[1], int(startPoint[0] - j)])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

        # in the x-y plane (keep z constant)
        if startPoint[2] == 0 or startPoint[2] == int(surface.shape[0]) - 1:
            # create the vertical line of the cross
            for i in range(domainWidth + 1):
                # bottom line
                point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] + i), int(startPoint[0])])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

                # top line
                point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1] - i), int(startPoint[0])])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

            # create the horizontal line of the cross
            for j in range(domainLength + 1):
                # right line
                point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1]), int(startPoint[0] + j)])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge

                # left line
                point = self.nearestPoint(surface, [startPoint[2], int(startPoint[1]), int(startPoint[0] - j)])
                # generate charge on the domain
                surface[point[0], point[1], point[2]] = charge
        return surface

    def _octagonEmpty(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int, int],
                      possible_charge: List[int]) -> bool:
        """
        This function check the position want to generate cross is empty
        """
        # Rename variables and change startPoint from tuple to list
        ln = domainWidth
        cen = list(startPoint)
        # Find the center of the octagon
        # If the length is an odd number, the center of the octagon should be located between 4 points (ie center point should end as .5)
        # for x
        if cen[0] % 2 == 0 and ln % 2 == 1 and cen[0] != 0 and cen[0] != surface.shape[2] - 1:
            cen[0] = cen[0] - 0.5

        # for y
        if cen[1] % 2 == 0 and ln % 2 == 1 and cen[1] != 0 and cen[1] != surface.shape[1] - 1:
            cen[1] = cen[1] - 0.5

        # for z
        if cen[2] % 2 == 0 and ln % 2 == 1 and cen[2] != 0 and cen[2] != surface.shape[0] - 1:
            cen[2] = cen[2] - 0.5

        # in y-z plane (keep x constant)
        if startPoint[0] == 0 or startPoint[0] == int(surface.shape[2]) - 1:
            # Separate conditions between if the length is odd or even
            # If the length is odd
            if ln % 2 == 1:
                # Initial square surrounding the center
                n = int(ln / 2 + 0.5)
                for i in range(n):
                    for j in range(n):
                        # 1st point
                        point = self.nearestPoint(surface, [int(cen[2] + (0.5 + i)), int(cen[1] - (0.5 + j)), cen[0]])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 2nd point
                        point = self.nearestPoint(surface, [int(cen[2] + (0.5 + i)), int(cen[1] + (0.5 + j)), cen[0]])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 3rd point
                        point = self.nearestPoint(surface, [int(cen[2] - (0.5 + i)), int(cen[1] + (0.5 + j)), cen[0]])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 4th point
                        point = self.nearestPoint(surface, [int(cen[2] - (0.5 + i)), int(cen[1] - (0.5 + j)), cen[0]])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False

            # If the length is even
            elif ln % 2 == 0:
                # Initial square surrounding the center
                n = int(ln / 2)
                for i in range(n + 1):
                    for j in range(n + 1):
                        # 1st points
                        point = self.nearestPoint(surface, [int(cen[2] + i), int(cen[1] + j), cen[0]])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 2nd points
                        point = self.nearestPoint(surface, [int(cen[2] + i), int(cen[1] - j), cen[0]])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 3rd points
                        point = self.nearestPoint(surface, [int(cen[2] - i), int(cen[1] + j), cen[0]])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 4th points
                        point = self.nearestPoint(surface, [int(cen[2] - i), int(cen[1] - j), cen[0]])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False

            # Index edges of the square
            # top right edge
            ed_tr = [int(cen[2] - ln / 2), int(cen[1] + ln / 2), cen[0]]
            # top left edge
            ed_tl = [int(cen[2] - ln / 2), int(cen[1] - ln / 2), cen[0]]
            # bottom right edge
            ed_br = [int(cen[2] + ln / 2), int(cen[1] + ln / 2), cen[0]]
            # bottom left edge
            ed_bl = [int(cen[2] + ln / 2), int(cen[1] - ln / 2), cen[0]]

            # Fill out the 4 triangles
            # top right
            eg = ln + 1
            for i in range(0, ln + 1):
                for j in range(0, eg):
                    # top right
                    point = self.nearestPoint(surface, [int(ed_tr[0] - i), int(ed_tr[1] + j), ed_tr[2]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # top left
                    point = self.nearestPoint(surface, [int(ed_tl[0] - i), int(ed_tl[1] - j), ed_tl[2]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # bottom right
                    point = self.nearestPoint(surface, [int(ed_br[0] + i), int(ed_br[1] + j), ed_br[2]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # bottom left
                    point = self.nearestPoint(surface, [int(ed_bl[0] + i), int(ed_bl[1] - j), ed_bl[2]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                eg -= 1

            # Finally, fill out the remaining 4 squares
            for i in range(1, ln + 1):
                for j in range(1, ln + 1):
                    # top square
                    point = self.nearestPoint(surface, [int(ed_tl[0] - i), int(ed_tl[1] + j), ed_tl[2]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # left square
                    point = self.nearestPoint(surface, [int(ed_tl[0] + i), int(ed_tl[1] - j), ed_tl[2]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # right square
                    point = self.nearestPoint(surface, [int(ed_br[0] - i), int(ed_br[1] + j), ed_br[2]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # bottom square
                    point = self.nearestPoint(surface, [int(ed_br[0] + i), int(ed_br[1] - j), ed_br[2]])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

        # in x-z plane (keep y constant)
        if startPoint[1] == 0 or startPoint[1] == surface.shape[1] - 1:
            # Separate conditions between if the length is odd or even
            # If the length is odd
            if ln % 2 == 1:
                # Initial square surrounding the center
                n = int(ln / 2 + 0.5)
                for i in range(n):
                    for j in range(n):
                        # 1st point
                        point = self.nearestPoint(surface, [int(cen[2] + (0.5 + i)), cen[1], int(cen[0] - (0.5 + j))])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 2nd point
                        point = self.nearestPoint(surface, [int(cen[2] + (0.5 + i)), cen[1], int(cen[0] + (0.5 + j))])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 3rd point
                        point = self.nearestPoint(surface, [int(cen[2] - (0.5 + i)), cen[1], int(cen[0] + (0.5 + j))])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 4th point
                        point = self.nearestPoint(surface, [int(cen[2] - (0.5 + i)), cen[1], int(cen[0] - (0.5 + j))])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False

            # If the length is even
            elif ln % 2 == 0:
                # Initial square surrounding the center
                n = int(ln / 2)
                for i in range(n + 1):
                    for j in range(n + 1):
                        # 1st point
                        point = self.nearestPoint(surface, [int(cen[2] + i), cen[1], int(cen[0] + j)])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 2nd point
                        point = self.nearestPoint(surface, [int(cen[2] + i), cen[1], int(cen[0] - j)])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 3rd point
                        point = self.nearestPoint(surface, [int(cen[2] - i), cen[1], int(cen[0] + j)])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 4th point
                        point = self.nearestPoint(surface, [int(cen[2] - i), cen[1], int(cen[0] - j)])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False

            # Index edges of the square
            # top right edge
            ed_tr = [int(cen[2] - ln / 2), cen[1], int(cen[0] + ln / 2)]
            # top left edge
            ed_tl = [int(cen[2] - ln / 2), cen[1], int(cen[0] - ln / 2)]
            # bottom right edge
            ed_br = [int(cen[2] + ln / 2), cen[1], int(cen[0] + ln / 2)]
            # bottom left edge
            ed_bl = [int(cen[2] + ln / 2), cen[1], int(cen[0] - ln / 2)]

            # Fill out the 4 triangles
            eg = ln + 1
            for i in range(0, ln + 1):
                for j in range(0, eg):
                    # top right
                    point = self.nearestPoint(surface, [int(ed_tr[0] - i), ed_tr[1], int(ed_tr[2] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # top left
                    point = self.nearestPoint(surface, [int(ed_tl[0] - i), ed_tl[1], int(ed_tl[2] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # bottom right
                    point = self.nearestPoint(surface, [int(ed_br[0] + i), ed_br[1], int(ed_br[2] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # bottom left
                    point = self.nearestPoint(surface, [int(ed_bl[0] + i), ed_bl[1], int(ed_bl[2] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                eg -= 1

            # Finally, fill out the remaining 4 squares
            for i in range(1, ln + 1):
                for j in range(1, ln + 1):
                    # top square
                    point = self.nearestPoint(surface, [int(ed_tl[0] - i), ed_tl[1], int(ed_tl[2] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # left square
                    point = self.nearestPoint(surface, [int(ed_tl[0] + i), ed_tl[1], int(ed_tl[2] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # right square
                    point = self.nearestPoint(surface, [int(ed_br[0] - i), ed_br[1], int(ed_br[2] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # bottom square
                    point = self.nearestPoint(surface, [int(ed_br[0] + i), ed_br[1], int(ed_br[2] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

        # in x-y plane (keep z constant)
        if startPoint[2] == 0 or startPoint[2] == surface.shape[0] - 1:
            # Separate conditions between if the length is odd or even
            # If the length is odd
            if ln % 2 == 1:
                # Initial square surrounding the center
                n = int(ln / 2 + 0.5)
                for i in range(n):
                    for j in range(n):
                        # 1st point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] + (0.5 + i)), int(cen[0] - (0.5 + j))])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 2nd point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] + (0.5 + i)), int(cen[0] + (0.5 + j))])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 3rd point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] - (0.5 + i)), int(cen[0] + (0.5 + j))])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 4th point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] - (0.5 + i)), int(cen[0] - (0.5 + j))])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False

            # If the length is even
            elif ln % 2 == 0:
                # Initial square surrounding the center
                n = int(ln / 2)
                for i in range(n + 1):
                    for j in range(n + 1):
                        # 1st point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] + i), int(cen[0] + j)])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 2nd point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] + i), int(cen[0] - j)])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 3rd point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] - i), int(cen[0] + j)])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False
                        # 4th point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] - i), int(cen[0] - j)])
                        # if the point is on a domain charge, location is not empty and need to choose new starting point
                        if surface[point[0], point[1], point[2]] in possible_charge:
                            return False

            # Index edges of the square
            # top right edge
            ed_tr = [cen[2], int(cen[1] - ln / 2), int(cen[0] + ln / 2)]
            # top left edge
            ed_tl = [cen[2], int(cen[1] - ln / 2), int(cen[0] - ln / 2)]
            # bottom right edge
            ed_br = [cen[2], int(cen[1] + ln / 2), int(cen[0] + ln / 2)]
            # bottom left edge
            ed_bl = [cen[2], int(cen[1] + ln / 2), int(cen[0] - ln / 2)]

            # Fill out the 4 triangles
            eg = ln + 1
            for i in range(0, ln + 1):
                for j in range(0, eg):
                    # top right
                    point = self.nearestPoint(surface, [ed_tr[0], int(ed_tr[1] - i), int(ed_tr[2] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # top left
                    point = self.nearestPoint(surface, [ed_tl[0], int(ed_tl[1] - i), int(ed_tl[2] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # bottom right
                    point = self.nearestPoint(surface, [ed_br[0], int(ed_br[1] + i), int(ed_br[2] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # bottom left
                    point = self.nearestPoint(surface, [ed_bl[0], int(ed_bl[1] + i), int(ed_bl[2] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

                eg -= 1

            # Finally, fill out the remaining 4 squares
            for i in range(1, ln + 1):
                for j in range(1, ln + 1):
                    # top square
                    point = self.nearestPoint(surface, [ed_tl[0], int(ed_tl[1] - i), int(ed_tl[2] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # left square
                    point = self.nearestPoint(surface, [ed_tl[0], int(ed_tl[1] + i), int(ed_tl[2] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # right square
                    point = self.nearestPoint(surface, [ed_br[0], int(ed_br[1] - i), int(ed_br[2] + j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False
                    # bottom square
                    point = self.nearestPoint(surface, [ed_br[0], int(ed_br[1] + i), int(ed_br[2] - j)])
                    # if the point is on a domain charge, location is not empty and need to choose new starting point
                    if surface[point[0], point[1], point[2]] in possible_charge:
                        return False

        return True
    def _generateOctagon(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int, int],
                         charge: int) -> ndarray:
        """
        This function generate octagon shape for surface
        """
        # Rename variables and change startPoint from tuple to list
        ln = domainWidth
        cen = list(startPoint)
        # Find the center of the octagon
        # If the length is an odd number, the center of the octagon should be located between 4 points (ie center point should end as .5)
        # for x
        if cen[0] % 2 == 0 and ln % 2 == 1 and cen[0] != 0 and cen[0] != surface.shape[2] - 1:
            cen[0] = cen[0] - 0.5

        # for y
        if cen[1] % 2 == 0 and ln % 2 == 1 and cen[1] != 0 and cen[1] != surface.shape[1] - 1:
            cen[1] = cen[1] - 0.5

        # for z
        if cen[2] % 2 == 0 and ln % 2 == 1 and cen[2] != 0 and cen[2] != surface.shape[0] - 1:
            cen[2] = cen[2] - 0.5

        # in y-z plane (keep x constant)
        if startPoint[0] == 0 or startPoint[0] == surface.shape[2] - 1:
            # Separate conditions between if the length is odd or even
            # If the length is odd
            if ln % 2 == 1:
                # Initial square surrounding the center
                n = int(ln / 2 + 0.5)
                for i in range(n):
                    for j in range(n):
                        # 1st point
                        point = self.nearestPoint(surface, [int(cen[2] + (0.5 + i)), int(cen[1] - (0.5 + j)), cen[0]])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 2nd point
                        point = self.nearestPoint(surface, [int(cen[2] + (0.5 + i)), int(cen[1] + (0.5 + j)), cen[0]])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 3rd point
                        point = self.nearestPoint(surface, [int(cen[2] - (0.5 + i)), int(cen[1] + (0.5 + j)), cen[0]])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 4th point
                        point = self.nearestPoint(surface, [int(cen[2] - (0.5 + i)), int(cen[1] - (0.5 + j)), cen[0]])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge


            # If the length is even
            elif ln % 2 == 0:
                # Initial square surrounding the center
                n = int(ln / 2)
                for i in range(n + 1):
                    for j in range(n + 1):
                        # 1st points
                        point = self.nearestPoint(surface, [int(cen[2] + i), int(cen[1] + j), cen[0]])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 2nd points
                        point = self.nearestPoint(surface, [int(cen[2] + i), int(cen[1] - j), cen[0]])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 3rd points
                        point = self.nearestPoint(surface, [int(cen[2] - i), int(cen[1] + j), cen[0]])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 4th points
                        point = self.nearestPoint(surface, [int(cen[2] - i), int(cen[1] - j), cen[0]])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

            # Index edges of the square
            # top right edge
            ed_tr = [int(cen[2] - ln / 2), int(cen[1] + ln / 2), cen[0]]
            # top left edge
            ed_tl = [int(cen[2] - ln / 2), int(cen[1] - ln / 2), cen[0]]
            # bottom right edge
            ed_br = [int(cen[2] + ln / 2), int(cen[1] + ln / 2), cen[0]]
            # bottom left edge
            ed_bl = [int(cen[2] + ln / 2), int(cen[1] - ln / 2), cen[0]]

            # Fill out the 4 triangles
            # top right
            eg = ln + 1
            for i in range(0, ln + 1):
                for j in range(0, eg):
                    # top right
                    point = self.nearestPoint(surface, [int(ed_tr[0] - i), int(ed_tr[1] + j), ed_tr[2]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # top left
                    point = self.nearestPoint(surface, [int(ed_tl[0] - i), int(ed_tl[1] - j), ed_tl[2]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom right
                    point = self.nearestPoint(surface, [int(ed_br[0] + i), int(ed_br[1] + j), ed_br[2]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom left
                    point = self.nearestPoint(surface, [int(ed_bl[0] + i), int(ed_bl[1] - j), ed_bl[2]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge


                eg -= 1

            # Finally, fill out the remaining 4 squares
            for i in range(1, ln + 1):
                for j in range(1, ln + 1):
                    # top square
                    point = self.nearestPoint(surface, [int(ed_tl[0] - i), int(ed_tl[1] + j), ed_tl[2]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # left square
                    point = self.nearestPoint(surface, [int(ed_tl[0] + i), int(ed_tl[1] - j), ed_tl[2]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # right square
                    point = self.nearestPoint(surface, [int(ed_br[0] - i), int(ed_br[1] + j), ed_br[2]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom square
                    point = self.nearestPoint(surface, [int(ed_br[0] + i), int(ed_br[1] - j), ed_br[2]])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

        # in x-z plane (keep y constant)
        if startPoint[1] == 0 or startPoint[1] == surface.shape[1] - 1:
            # Separate conditions between if the length is odd or even
            # If the length is odd
            if ln % 2 == 1:
                # Initial square surrounding the center
                n = int(ln / 2 + 0.5)
                for i in range(n):
                    for j in range(n):
                        # 1st point
                        point = self.nearestPoint(surface, [int(cen[2] + (0.5 + i)), cen[1], int(cen[0] - (0.5 + j))])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 2nd point
                        point = self.nearestPoint(surface, [int(cen[2] + (0.5 + i)), cen[1], int(cen[0] + (0.5 + j))])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 3rd point
                        point = self.nearestPoint(surface, [int(cen[2] - (0.5 + i)), cen[1], int(cen[0] + (0.5 + j))])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 4th point
                        point = self.nearestPoint(surface, [int(cen[2] - (0.5 + i)), cen[1], int(cen[0] - (0.5 + j))])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

            # If the length is even
            elif ln % 2 == 0:
                # Initial square surrounding the center
                n = int(ln / 2)
                for i in range(n + 1):
                    for j in range(n + 1):
                        # 1st point
                        point = self.nearestPoint(surface, [int(cen[2] + i), cen[1], int(cen[0] + j)])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 2nd point
                        point = self.nearestPoint(surface, [int(cen[2] + i), cen[1], int(cen[0] - j)])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 3rd point
                        point = self.nearestPoint(surface, [int(cen[2] - i), cen[1], int(cen[0] + j)])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 4th point
                        point = self.nearestPoint(surface, [int(cen[2] - i), cen[1], int(cen[0] - j)])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

            # Index edges of the square
            # top right edge
            ed_tr = [int(cen[2] - ln / 2), cen[1], int(cen[0] + ln / 2)]
            # top left edge
            ed_tl = [int(cen[2] - ln / 2), cen[1], int(cen[0] - ln / 2)]
            # bottom right edge
            ed_br = [int(cen[2] + ln / 2), cen[1], int(cen[0] + ln / 2)]
            # bottom left edge
            ed_bl = [int(cen[2] + ln / 2), cen[1], int(cen[0] - ln / 2)]

            # Fill out the 4 triangles
            eg = ln + 1
            for i in range(0, ln + 1):
                for j in range(0, eg):
                    # top right
                    point = self.nearestPoint(surface, [int(ed_tr[0] - i), ed_tr[1], int(ed_tr[2] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # top left
                    point = self.nearestPoint(surface, [int(ed_tl[0] - i), ed_tl[1], int(ed_tl[2] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom right
                    point = self.nearestPoint(surface, [int(ed_br[0] + i), ed_br[1], int(ed_br[2] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom left
                    point = self.nearestPoint(surface, [int(ed_bl[0] + i), ed_bl[1], int(ed_bl[2] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                eg -= 1

            # Finally, fill out the remaining 4 squares
            for i in range(1, ln + 1):
                for j in range(1, ln + 1):
                    # top square
                    point = self.nearestPoint(surface, [int(ed_tl[0] - i), ed_tl[1], int(ed_tl[2] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # left square
                    point = self.nearestPoint(surface, [int(ed_tl[0] + i), ed_tl[1], int(ed_tl[2] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # right square
                    point = self.nearestPoint(surface, [int(ed_br[0] - i), ed_br[1], int(ed_br[2] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom square
                    point = self.nearestPoint(surface, [int(ed_br[0] + i), ed_br[1], int(ed_br[2] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

        # in x-y plane (keep z constant)
        if startPoint[2] == 0 or startPoint[2] == surface.shape[0] - 1:
            # Separate conditions between if the length is odd or even
            # If the length is odd
            if ln % 2 == 1:
                # Initial square surrounding the center
                n = int(ln / 2 + 0.5)
                for i in range(n):
                    for j in range(n):
                        # 1st point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] + (0.5 + i)), int(cen[0] - (0.5 + j))])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 2nd point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] + (0.5 + i)), int(cen[0] + (0.5 + j))])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 3rd point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] - (0.5 + i)), int(cen[0] + (0.5 + j))])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 4th point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] - (0.5 + i)), int(cen[0] - (0.5 + j))])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

            # If the length is even
            elif ln % 2 == 0:
                # Initial square surrounding the center
                n = int(ln / 2)
                for i in range(n + 1):
                    for j in range(n + 1):
                        # 1st point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] + i), int(cen[0] + j)])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 2nd point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] + i), int(cen[0] - j)])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 3rd point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] - i), int(cen[0] + j)])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

                        # 4th point
                        point = self.nearestPoint(surface, [cen[2], int(cen[1] - i), int(cen[0] - j)])
                        # generate charge on the domain
                        surface[point[0], point[1], point[2]] = charge

            # Index edges of the square
            # top right edge
            ed_tr = [cen[2], int(cen[1] - ln / 2), int(cen[0] + ln / 2)]
            # top left edge
            ed_tl = [cen[2], int(cen[1] - ln / 2), int(cen[0] - ln / 2)]
            # bottom right edge
            ed_br = [cen[2], int(cen[1] + ln / 2), int(cen[0] + ln / 2)]
            # bottom left edge
            ed_bl = [cen[2], int(cen[1] + ln / 2), int(cen[0] - ln / 2)]

            # Fill out the 4 triangles
            eg = ln + 1
            for i in range(0, ln + 1):
                for j in range(0, eg):
                    # top right
                    point = self.nearestPoint(surface, [ed_tr[0], int(ed_tr[1] - i), int(ed_tr[2] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # top left
                    point = self.nearestPoint(surface, [ed_tl[0], int(ed_tl[1] - i), int(ed_tl[2] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom right
                    point = self.nearestPoint(surface, [ed_br[0], int(ed_br[1] + i), int(ed_br[2] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom left
                    point = self.nearestPoint(surface, [ed_bl[0], int(ed_bl[1] + i), int(ed_bl[2] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                eg -= 1

            # Finally, fill out the remaining 4 squares
            for i in range(1, ln + 1):
                for j in range(1, ln + 1):
                    # top square
                    point = self.nearestPoint(surface, [ed_tl[0], int(ed_tl[1] - i), int(ed_tl[2] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # left square
                    point = self.nearestPoint(surface, [ed_tl[0], int(ed_tl[1] + i), int(ed_tl[2] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # right square
                    point = self.nearestPoint(surface, [ed_br[0], int(ed_br[1] - i), int(ed_br[2] + j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

                    # bottom square
                    point = self.nearestPoint(surface, [ed_br[0], int(ed_br[1] + i), int(ed_br[2] - j)])
                    # generate charge on the domain
                    surface[point[0], point[1], point[2]] = charge

        return surface

    def _singleEmpty(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int, int],
                     possible_charge: List[int]) -> bool:
        """
        This function check the position want to generate single is empty
        """
        # locate the closest valid point
        point = self.nearestPoint(surface, [startPoint[2], startPoint[1], startPoint[0]])
        # if the point is on a domain charge, location is not empty and need to choose new starting point
        if surface[point[0], point[1], point[2]] in possible_charge:
            return False

        return True

    def _generateSingle(self, surface: ndarray, domainWidth: int, domainLength: int, startPoint: Tuple[int, int, int],
                        charge: int) -> ndarray:
        """
        This function generate single shape for surface
        """
        # locate the closest valid point
        point = self.nearestPoint(surface, [startPoint[2], startPoint[1], startPoint[0]])
        # generate charge on the domain
        surface[point[0], point[1], point[2]] = charge

        return surface
