"""
This program:
- Generates a domain with charge (positive/negative/neutral)
- Can be used for 2D/3D, or for testing surface & bacteria surface
"""
from numpy import ndarray
import numpy as np
from SurfaceGenerator.Surface import Surface
import SurfaceGenerator.DomainShape as ds
from typing import Tuple, List, Union
from ExternalIO import showMessage, writeLog, visPlot
import math
import time
from multiprocessing import Pool, cpu_count
from functools import partial
import os

WAIT_TIME = 10
FILM_HEIGHT = 1
BACTERIA_2D_HEIGHT = 3

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
            generateShape = ds._generateDiamond
            checkEmpty = ds._diamondEmpty
            restriction = domainWidth + 1
            # Number of domains
            # if the surface is eiter a 2D shape bacteria or a film, we only need 1 domain num
            if surface.height < 4:
                # if the surface is 2d, only 1 domain number should be present
                domainNum = int((surface.length * surface.width * concentration) / int(
                    4 * ((1 + domainWidth) / 2) * domainWidth + 1))
            # if the surface is a 3D bacteria
            else:
                # calculate total number of available points on each side of bacteria
                # the domain number will be formatted as a list
                # domainNum will contain number of domains on each side
                # domainNum = [x0, x1, y0, y1, z0, z1]

                # define total number of points of 3d shape
                # first get all location of possible points using _allPossiblePoint function
                allPoints = self._allPossiblePoint(newSurface, surface, surface.length, surface.width, surface.height,
                                                   0, 0, 'SINGLE')
                # then, separate them into each plane
                allPointsSeparated = self._allPoints(surface, allPoints)
                # lastly, find the length of the lists for each plane
                allPointsLength = [len(allPointsSeparated[i]) for i in range(len(allPointsSeparated))]

                domainNum = [int((number*concentration)/int(4*((1+domainWidth)/2)*domainWidth+1))
                             for number in allPointsLength]

            # showMessage("concentration = {}".format(concentration))
        elif shape.upper() == "CROSS":
            generateShape = ds._generateCross
            checkEmpty = ds._crossEmpty
            restriction = max(domainWidth + 1, domainLength + 1)

            # Number of domains
            # if the surface is eiter a 2D shape bacteria or a film, we only need 1 domain num
            if surface.height < 4:
                domainNum = int(
                    (surface.length * surface.width * concentration) / int(domainWidth * 2 + domainLength * 2 + 1))
            # if the surface is a 3D bacteria
            else:
                # calculate total number of available points on each side of bacteria
                # the domain number will be formatted as a list
                # domainNum will contain number of domains on each side
                # domainNum = [x0, x1, y0, y1, z0, z1]

                # define total number of points of 3d shape
                # first get all location of possible points using _allPossiblePoint function
                allPoints = self._allPossiblePoint(newSurface, surface, surface.length, surface.width, surface.height,
                                                   0, 0, 'SINGLE')
                # then, separate them into each plane
                allPointsSeparated = self._allPoints(surface, allPoints)
                # lastly, find the length of the lists for each plane
                allPointsLength = [len(allPointsSeparated[i]) for i in range(len(allPointsSeparated))]

                domainNum = [int((number * concentration) / int(domainWidth * 2 + domainLength * 2 + 1))
                             for number in allPointsLength]

        elif shape.upper() == "OCTAGON":
            generateShape = ds._generateOctagon
            checkEmpty = ds._octagonEmpty
            restriction = (3 / 2) * domainWidth
            # Number of domains
            # if the surface is eiter a 2D shape bacteria or a film, we only need 1 domain num
            if surface.height < 4:
                domainNum = int(
                    (surface.length * surface.width * concentration) / int((domainWidth + 1 + domainWidth * 2) ** 2 -
                                                                           4 * ((1 + domainWidth) / 2) * domainWidth))
            # if the surface is a 3D bacteria
            else:
                # calculate total number of available points on each side of bacteria
                # the domain number will be formatted as a list
                # domainNum will contain number of domains on each side
                # domainNum = [x0, x1, y0, y1, z0, z1]

                # define total number of points of 3d shape
                # first get all location of possible points using _allPossiblePoint function
                allPoints = self._allPossiblePoint(newSurface, surface, surface.length, surface.width, surface.height,
                                                   0, 0, 'SINGLE')
                # then, separate them into each plane
                allPointsSeparated = self._allPoints(surface, allPoints)
                # lastly, find the length of the lists for each plane
                allPointsLength = [len(allPointsSeparated[i]) for i in range(len(allPointsSeparated))]

                domainNum = [int((number * concentration) / int(
                    (domainWidth + 1 + domainWidth * 2) ** 2 - 4 * ((1 + domainWidth) / 2) * domainWidth))
                             for number in allPointsLength]

        elif shape.upper() == "SINGLE":
            generateShape = ds._generateSingle
            checkEmpty = ds._singleEmpty
            restriction = 0

            # Number of domains
            # if the surface is eiter a 2D shape bacteria or a film, we only need 1 domain num
            if surface.height < 4:
                domainNum = int(surface.length * surface.width * concentration)
                # if the surface is a 3D bacteria
            else:
                # calculate total number of available points on each side of bacteria
                # the domain number will be formatted as a list
                # domainNum will contain number of domains on each side
                # domainNum = [x0, x1, y0, y1, z0, z1]

                # define total number of points of 3d shape
                # first get all location of possible points using _allPossiblePoint function
                allPoints = self._allPossiblePoint(newSurface, surface, surface.length, surface.width, surface.height,
                                                   0, 0, 'SINGLE')
                # then, separate them into each plane
                allPointsSeparated = self._allPoints(surface, allPoints)
                # lastly, find the length of the lists for each plane
                allPointsLength = [len(allPointsSeparated[i]) for i in range(len(allPointsSeparated))]

                domainNum = [int((number * concentration)) for number in allPointsLength]


        else:
            raise RuntimeError("Unknown shape")

        # # if surface.height >= 4:
        # # if the surface is a bacteria, we will redefine the domainNum variable
        # else:
        #     # calculate total number of available points on each side of bacteria
        #     # the domain number will be formatted as a list
        #     # domainNum will contain number of domains on each side
        #     # domainNum = [x0, x1, y0, y1, z0, z1]
        #
        #     # define total number of points of 3d shape
        #     # first get all location of possible points using _allPossiblePoint function
        #     allPoints = self._allPossiblePoint(newSurface, surface, surface.length, surface.width, surface.height, 0, 0, 'SINGLE')
        #     # then, separate them into each plane
        #     allPointsSeparated = self._allPoints(surface, allPoints)
        #     # lastly, find the length of the lists for each plane
        #     allPointsLength = [len(allPointsSeparated[i]) for i in range(len(allPointsSeparated))]
        #
        #     # find the number of domains for each side of the bacteria
        #     if shape.upper() == "DIAMOND":
        #         domainNum = [int((number*concentration)/int(4*((1+domainWidth)/2)*domainWidth+1))
        #                      for number in allPointsLength]
        #     elif shape.upper() == "CROSS":
        #         domainNum = [int((number*concentration)/int(domainWidth*2+domainLength*2+1))
        #                      for number in allPointsLength]
        #     elif shape.upper() == "OCTAGON":
        #         domainNum = [int((number*concentration)/int((domainWidth+1+domainWidth*2)**2-4*((1+domainWidth)/2)*domainWidth))
        #                      for number in allPointsLength]
        #     elif shape.upper() == "SINGLE":
        #         domainNum = [int((number*concentration)) for number in allPointsLength]
        #     else:
        #         raise RuntimeError("Unknown shape")

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
        if surface.height <= 2:
            # set how many domains we should make for each CPU
            # find the number of CPUs on the computer
            # minus 2 in case of other possible process is running
            ncpus = max(int(os.environ.get('SLURM_CPUS_PER_TASK', default=1)) - 2, 1)

            # if the ncpus is 1, that means we are running this on our local computer and thus, we will recalculate the
            # ncpus to the number of cpus on the computer
            if ncpus == 1:
                ncpus = cpu_count()

            # when the cpu number is less than 16, we will set the number of usable cpu to that number
            if ncpus <= 16:
                cpu_number = ncpus

            # if the cpu number is greater than 16, we will just use 16 cpus to make things simple
            else:
                cpu_number = 16

            showMessage(f"number of CPUs is {ncpus} but we will use {cpu_number}")

            # first separate the grid into different sections
            separate = self._separateGrid(cpu_number)

            # if the surface length is larger than surface width, reverse the order of separate
            if surface.length > surface.width:
                # reverse the order of separate
                separate = (separate[1], separate[0])

            # bacteria dimension that is smaller will be divided up by the first number in separate
            # create a list of tuple which indicates which values will be divided by what number
            # tuple -> (x,y)
            dividor = [[(i / separate[0], j / separate[1]) for i in range(0, separate[0] + 1)] for j in
                       range(0, separate[1] + 1)]

            # determine the area which will be not be covered due to multiprocessing
            # don't need the first and last numbers from the list
            boundary = [[i / separate[0] for i in range(1, separate[0])],
                        [i / separate[1] for i in range(1, separate[1])]]
            # now determine which positions were rejected during multiprocessing
            pointsNotCovered = [tup for tup in possiblePoint for i in range(len(boundary[0])) for j in range(len(boundary[1]))
                         if (tup[0] > surface.length * boundary[0][i] - restriction
                             and tup[0] < surface.length * boundary[0][i] + restriction)
                         or (tup[1] > surface.width * boundary[1][j] - restriction
                             and tup[1] < surface.width * boundary[1][j] + restriction)]

            # remove duplicates
            pointsNotCovered = list(dict.fromkeys(pointsNotCovered))

            # determine ratio which will be used to calculate number of domains that will be generated using multiprocessing
            ratio = 1 - len(pointsNotCovered)/int(surface.length*surface.width)

            showMessage(ratio)

            # calculate how many domains each cpu will handle
            # however, if the domain number is less than the cpu number, that is not good since each cpu would not generate
            # any domains
            # therefore, since the domain concentration is small, we will set cpu number to 1
            if cpu_number < domainNum:
                # we will only generate a specified number of the domains using multiprocessing, based on the ratio variable
                # the rest will be generated using regular method to prevent grid like pattern
                domainNumEach = int((domainNum * ratio) / cpu_number)

            else:
                cpu_number = 1
                domainNumEach = int(domainNum / cpu_number)

            # if we want neutral charges on the surface, we can define domainNumChar2, otherwise, it will be zero
            if self.neutral:
                domainNumChar1 = math.ceil(
                    domainNumEach * charge_concentration)  # this will have the first charge from the possible_charge list
                domainNumChar2 = domainNumEach - domainNumChar1  # this will have the second charge from the possible_charge list
            elif not self.neutral:
                domainNumChar1 = domainNumEach
                domainNumChar2 = 0

            # create the nested points
            possiblePointNested = self._separateNestedPoints(separate, dividor, possiblePoint, restriction, surface)

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
            currentdomainNum = sum(generatedList)

            # if the total number of domains does not equal the current number of domains, we will continue generating
            # domains until the total domain number equals the required number of domains on the surface
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

                # now change the only possible positions to be only located on the boundaries when multiprocessing
                # if the cpu number is only 1, then the rest of the points will be carried out with all the possible points
                if cpu_number == 1:
                    pointRest = possiblePoint
                # if the cpu number is greater than 1, the rest of the points will be on the boundaries
                else:
                    pointRest = pointsNotCovered

                [newSurface, generated] = _generateDomainMultiprocessingConstant(pointRest)
                generatedList.append(generated)

        # if the surface is a bacteria 2d, we don't need multiprocessing since bacterias are small
        elif surface.height == 3:
            # determine how many neutral or charged domains for the surface
            if self.neutral:
                domainNumChar1 = math.ceil(domainNum * charge_concentration)  # this will have the first charge from the possible_charge list
                domainNumChar2 = domainNum - domainNumChar1  # this will have the second charge from the possible_charge list
            elif not self.neutral:
                domainNumChar1 = domainNum
                domainNumChar2 = 0


            newSurfaceGenerated = self._generateDomainMultiprocessing(possiblePoint=possiblePoint,
                                                                      newSurface=newSurface,
                                                                      domainWidth=domainWidth,
                                                                      domainLength=domainLength,
                                                                      possible_charge=possible_charge,
                                                                      domainNumEach=domainNum,
                                                                      generateShape=generateShape,
                                                                      checkEmpty=checkEmpty,
                                                                      domainNumChar1=domainNumChar1,
                                                                      domainNumChar2=domainNumChar2)
            newSurface = newSurfaceGenerated[0]

        # if the surface is a bacteria 3d, we don't need multiprocessing since bacterias are small
        elif surface.height >= 4:
            # separate the coordinates to their respective planes
            possiblePointSide = self._allPoints(surface, possiblePoint)

            # calculate the total number of domains necessairy for both neutral and charge
            # this will dictate the number of neutral and
            if self.neutral:
                domainNumChar1Tot = math.ceil(sum(domainNum) * charge_concentration)  # this will have the first charge from the possible_charge list
                domainNumChar2Tot = sum(domainNum) - domainNumChar1Tot  # this will have the second charge from the possible_charge list
            elif not self.neutral:
                domainNumChar1Tot = sum(domainNum)
                domainNumChar2Tot = 0

            # initialize the total number of domains for each charge generated
            domainNumCharTot = [0,0]

            # now generate the domains on each side of the bacteria
            for i in range(len(possiblePointSide)):
                # determine how many neutral or charged domains for the surface
                if self.neutral:
                    domainNumChar1 = math.ceil(
                        domainNum[i] * charge_concentration)  # this will have the first charge from the possible_charge list
                    domainNumChar2 = domainNum[i] - domainNumChar1  # this will have the second charge from the possible_charge list

                elif not self.neutral:
                    domainNumChar1 = domainNum[i]
                    domainNumChar2 = 0

                # append to domainNumCharTot
                domainNumCharTot[0] += domainNumChar1
                domainNumCharTot[1] += domainNumChar2
                # if the total number of domains for either charge exceeds, we will set the first domainNumChar
                if domainNumCharTot[0] > domainNumChar1Tot:
                    # convert one domain from charge 1 to charge 2
                    domainNumChar1 -= 1
                    domainNumCharTot[0] -= 1
                    domainNumChar2 += 1
                    domainNumCharTot[1] += 1

                if domainNumCharTot[1] > domainNumChar2Tot:
                    # convert one domain from charge 2 to charge 1
                    domainNumChar2 -= 1
                    domainNumCharTot[1] -= 1
                    domainNumChar1 += 1
                    domainNumCharTot[0] += 1

                # generate the domains onto the surface
                newSurfaceGenerated = self._generateDomainMultiprocessing(possiblePoint=possiblePointSide[i], newSurface=newSurface,
                                                                 domainWidth=domainWidth, domainLength=domainLength,
                                                                 possible_charge=possible_charge, domainNumEach=domainNum[i],
                                                                 generateShape=generateShape, checkEmpty=checkEmpty,
                                                                 domainNumChar1=domainNumChar1, domainNumChar2=domainNumChar2)
                newSurface = newSurfaceGenerated[0]

        # now, we will determine the actual concentration of charged and neutral
        totalSize = len(np.where(newSurface!=2)[0])
        concentration_charge = (len(np.where(newSurface == possible_charge[0])[0])) / totalSize
        concentration_neutral = (len(np.where(newSurface == possible_charge[1])[0])) / totalSize

        showMessage(f"concentration_charge is {concentration_charge}")
        showMessage(f"concentration_neutral is {concentration_neutral}")

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

        'if running on the computer, uncomment time.sleep to not make computer laggy (optional)'
        # time.sleep(1)

        # initialize of times randomPoint is called
        # [incorrect, correct]
        rP = [0,0]

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
                # add to incorrect
                rP[0] += 1
                continue

            # add to correct
            rP[1] += 1

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

        # determine efficiency of randomPoint
        efficiency = (rP[1] / sum(rP)) * 100
        showMessage(f"Efficiency of _randomPoint function was {efficiency}%")

        # combine the new surface and total number of domains generated into a list
        surface_generated = [newSurface, generated]
        return surface_generated

    def _separateGrid(self, cpu_number: int) -> Tuple[int, int]:
        """
        This function returns a tuple (x,y) for how many sections to separate the film into
        """
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
        separate = [(i, j) for i in reversed(range(lower + 1)) for j in range(upper, cpu_number + 1) if i * j == cpu_number][0]

        return separate

    def _separateNestedPoints(self, separate: Tuple[int,int], dividor: List[Tuple[int, int]],
                              possiblePoint: List[Tuple[int, int]], restriction: int, surface: Surface):
        """
        This function creates all the possible points for each cpu
        """

        # initialize nested list
        possiblePointNested = []
        # this defines the number of columns
        for i in range(separate[0]):
            # this defines the number of rows
            for j in range(separate[1]):
                points = [tup for tup in possiblePoint
                          if tup[0] > int(surface.length * dividor[0][i][0] + restriction)
                          and tup[0] < int(surface.length * dividor[0][i + 1][0] - restriction)
                          and tup[1] > int(surface.width * dividor[j][0][1] + restriction)
                          and tup[1] < int(surface.width * dividor[j + 1][0][1] - restriction)]
                possiblePointNested.append(points)

        return possiblePointNested

    def _allPoints(self, surface: Surface, possiblePoint: List[Tuple[int,int,int]]) -> List[int]:
        """
        This function calculates all points on the surface on each plane
        _allPoints -> [x0, x1, y0, y1, z0, z1]
        """
        # define all possible location
        # initialize all lists
        possiblePointx0 = []
        possiblePointx1 = []
        possiblePointy0 = []
        possiblePointy1 = []
        possiblePointz0 = []
        possiblePointz1 = []

        # traverse through all points and add each point to 1 of the 6 lists depending on their location
        for tup in possiblePoint:
            # x0
            if tup[0] == 0:
                possiblePointx0.append(tup)
            # x1
            elif tup[0] == int(surface.length - 1):
                possiblePointx1.append(tup)
            # y0
            elif tup[1] == 0:
                possiblePointy0.append(tup)
            # y1
            elif tup[1] == int(surface.width - 1):
                possiblePointy1.append(tup)
            # z0
            elif tup[2] == 0:
                possiblePointz0.append(tup)
            # z1
            elif tup[2] == int(surface.height - 1):
                possiblePointz1.append(tup)

        # combine the 6 lists into 1 nested list
        possiblePointSide = [possiblePointx0, possiblePointx1, possiblePointy0, possiblePointy1, possiblePointz0,
                             possiblePointz1]

        return possiblePointSide

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
        index = np.random.RandomState().randint(len(possiblePoint))
        # return the coordinate
        coordinate = possiblePoint[index]
        # remove the chosen coordinate from all possiblepoints
        possiblePoint.pop(index)

        # return the result as tuple
        return coordinate, possiblePoint