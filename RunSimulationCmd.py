"""
This is a text interface for running the simulation
Checking all user input is valid at here
"""
import re
from typing import Union, Tuple

from EnergyScan import EnergySimulator
from ExternalIO import getHelp, getRestriction, openLog, showMessage, closeLog, writeLog
from Simulator import EnergyScan


def getArgument() -> None:
    """
    This function take the setting argument from the user and call Simulation file to run the program
    Check all user input valid at here
    :return: None
    """
    #### taking general info ####

    # take simulation type
    while True:
        simulationType = input("Please enter simulation type: \n")

        # set the name
        helpName = "TYPE"

        # if enter help
        if simulationType.upper() == "HELP":
            helpMessage(helpName)
            continue

        # check the validity of input and do reaction
        result = eval(execDict[helpName])

        if result:
            simulationType = int(simulationType)
            break
        else:
            errorInput(helpName)

    # take trail number
    while True:
        trail = input("Please enter trail number: \n")

        # set the name
        helpName = "TRAIL"

        # if enter help
        if trail.upper() == "HELP":
            helpMessage(helpName)
            continue

        # check the validity of input and do reaction
        result = eval(execDict[helpName])

        # check is it a number
        if not checkNum(trail):
            errorInput(helpName)
        elif result:
            trail = int(trail)
            break
        else:
            errorInput(helpName)

    # take dimension
    while True:
        # Take user input
        dimension = input("Please enter the dimension you want to simulate (2 for 2D, 3 for 3D, "
                          "help for more information): \n")

        # set the name
        helpName = "DIMENSION"

        # if enter help
        if dimension.upper() == "HELP":
            helpMessage(helpName)
            continue

        # check the validity of input and do reaction
        result = eval(execDict[helpName])

        if result:
            dimension = int(dimension)
            break
        elif dimension.upper() == "HELP":
            helpMessage(helpName)
        else:
            errorInput(helpName)

    #### taking film info ####

    # take film seed number
    while True:
        filmSeed = input("Please enter film seed number: \n")

        # set the name
        helpName = "SEED"
        seed = filmSeed

        # if enter help
        if filmSeed.upper() == "HELP":
            helpMessage(helpName)
            continue

        # check the validity of input and do reaction
        result = eval(execDict[helpName])

        if not checkNum(seed):
            errorInput(helpName)
        elif result:
            filmSeed = int(filmSeed)
            break
        else:
            errorInput(helpName)

    # take shape of the film surface
    while True:
        # Take user input
        filmSurfaceShape = input("Please enter the shape of the surface you want to simulate ("
                                 "help for more information): \n")

        # set the name
        helpName = "SURFACESHAPE"

        if filmSurfaceShape.upper() == "HELP":
            helpMessage(helpName)
            continue

        # set the variable for check
        shape = filmSurfaceShape

        # check the validity of input and do reaction
        result = eval(execDict[helpName])

        if result:
            break
        else:
            errorInput(helpName)

    # take film surface area size
    while True:
        # Take user input
        filmSurfaceSize = input("Please enter the film surface area you want to simulate  "
                                "(in format: ###x### (length x width) or "
                                "help for more information): \n")

        # set the name
        helpName = "SIZE"

        # check the validity of input
        if filmSurfaceSize.upper() == "HELP":
            helpMessage(helpName)
        else:
            # check the format of the input
            if bool(re.match("\d+[x]\d+", filmSurfaceSize)):
                # check this input size if valid
                valid = checkSize(filmSurfaceShape, filmSurfaceSize)

                # if not valid
                if not valid:
                    errorInput(filmSurfaceShape)
                    continue

                # if valid, record and break
                else:
                    filmSurfaceSize = valid
                    break
            else:
                errorInput(helpName)

    # take charge of the surface
    while True:
        # Take user input
        filmSurfaceCharge = input("Please enter the charge of the surface you want to simulate ("
                                  "help for more information): \n")
        # set the name
        helpName = "CHARGE"

        if filmSurfaceCharge.upper() == "HELP":
            helpMessage(helpName)
            continue
        # set the variable for check
        charge = filmSurfaceCharge

        # check the validity of input and do reaction
        result = eval(execDict[helpName])

        if result:
            filmSurfaceCharge = int(filmSurfaceCharge)
            break
        else:
            errorInput(helpName)

    # take domain concentration of film
    while True:
        # Take user input
        filmDomainCon = input("Please enter the domain concentration of the surface you want to simulate ("
                              "help for more information): \n")
        # set the name
        helpName = "CONCENTRATION"

        if filmDomainCon.upper() == "HELP":
            helpMessage(helpName)
            continue

        # set the variable for check
        concentration = filmDomainCon

        # check the validity of input and do reaction
        result = eval(execDict[helpName])

        if result:
            filmDomainCon = float(filmDomainCon)
            break
        else:
            errorInput(helpName)

    # take domain shape of film
    while True:
        # Take user input
        filmDomainShape = input("Please enter the shape of the domain on the surface you want to simulate ("
                                "help for more information): \n")

        # check the validity of input
        # set the name
        helpName = "DOMAINSHAPE"

        if filmDomainShape.upper() == "HELP":
            helpMessage(helpName)
            continue

        # set the variable for check
        shape = filmDomainShape

        # check the validity of input and do reaction
        result = eval(execDict[helpName])

        if result:
            break
        else:
            errorInput(helpName)

    # take domain size of film
    while True:
        # Take user input
        filmDomainSize = input("Please enter the domain area on the film you want to simulate  "
                               "(in format: ###x### (length x width) or "
                               "help for more information): \n")

        # set the name
        helpName = "SIZE"

        # check the validity of input
        if filmDomainSize.upper() == "HELP":
            helpMessage(helpName)
        else:
            # check the format of the input
            if bool(re.match("\d+[x]\d+", filmDomainSize)):
                # check this input size if valid
                valid = checkSize(filmDomainShape, filmDomainSize)

                # if not valid
                if not valid:
                    errorInput(filmDomainShape)
                    continue

                # if valid, record and break
                else:
                    filmDomainSize = valid
                    break
            else:
                errorInput(helpName)

    #### taking bacteria info ####

    # take seed of bacteria
    while True:
        bacteriaSeed = input("Please enter bacteria seed number: \n")

        # set the name
        helpName = "SEED"
        seed = bacteriaSeed

        # if type help
        if bacteriaSeed.upper() == "HELP":
            helpMessage(helpName)
            continue

        # check the validity of input and do reaction
        result = eval(execDict[helpName])

        if not checkNum(seed):
            errorInput(helpName)
        elif result:
            bacteriaSeed = int(bacteriaSeed)
            break
        else:
            errorInput(helpName)

    # take shape of the bacteria
    while True:
        # Take user input
        bacteriaSurfaceShape = input("Please enter the shape of the bacteria you want to simulate ("
                                     "help for more information): \n")

        # set the name
        helpName = "SURFACESHAPE"

        # if type help
        if bacteriaSurfaceShape.upper() == "HELP":
            helpMessage(helpName)
            continue

        # set the variable for check
        shape = bacteriaSurfaceShape

        # check the validity of input and do reaction
        result = eval(execDict[helpName])

        if result:
            break
        else:
            errorInput(helpName)

    # take the area size of bacteria
    while True:
        # Take user input
        bacteriaSize = input("Please enter the bacteria surface area you want to simulate  "
                             "(in format: ###x### (length x width) or "
                             "help for more information): \n")

        # set the name
        helpName = "SIZE"

        # check the validity of input
        if bacteriaSize.upper() == "HELP":
            helpMessage(helpName)
        else:
            # check the format of the input
            if bool(re.match("\d+[x]\d+", bacteriaSize)):
                # check this input size if valid
                valid = checkSize(bacteriaSurfaceShape, bacteriaSize)

                # if not valid
                if not valid:
                    errorInput(bacteriaSurfaceShape)
                    continue

                # if valid check bacteria size is smaller than surface size
                elif (valid[0] * valid[1]) >= (filmSurfaceSize[0] * filmSurfaceSize[1]):
                    print("BacteriaFile size should smaller than surface size.")

                # if valid, record and break
                else:
                    bacteriaSize = valid
                    break
            else:
                errorInput(helpName)

    # take charge of the bacteria
    while True:
        # Take user input
        bacteriaSurfaceCharge = input("Please enter the charge of the bacteria you want to simulate ("
                                      "help for more information): \n")
        # set the name
        helpName = "CHARGE"

        # if type help
        if bacteriaSurfaceCharge.upper() == "HELP":
            helpMessage(helpName)
            continue

        # set the variable for check
        charge = bacteriaSurfaceCharge

        # check the validity of input and do reaction
        result = eval(execDict[helpName])

        if result:
            bacteriaSurfaceCharge = int(bacteriaSurfaceCharge)
            break
        else:
            errorInput(helpName)

    # take the domain concentration of bacteria
    while True:
        # Take user input
        bacteriaDomainCon = input("Please enter the domain concentration of the bacteria you want to simulate ("
                                  "help for more information): \n")
        # set the name
        helpName = "CONCENTRATION"

        # if type help
        if bacteriaDomainCon.upper() == "HELP":
            helpMessage(helpName)
            continue

        # set the variable for check
        concentration = bacteriaDomainCon

        # check the validity of input and do reaction
        result = eval(execDict[helpName])

        if result:
            bacteriaDomainCon = float(bacteriaDomainCon)
            break
        else:
            errorInput(helpName)

    # take the domain shape of bacteria
    while True:
        # Take user input
        bacteriaDomainShape = input("Please enter the shape of the domain on the bacteria you want to simulate ("
                                    "help for more information): \n")

        # set the name
        helpName = "DOMAINSHAPE"

        # if type help
        if bacteriaDomainShape.upper() == "HELP":
            helpMessage(helpName)
            continue

        # set the variable for check
        shape = bacteriaDomainShape

        # check the validity of input and do reaction
        result = eval(execDict[helpName])

        if result:
            break
        else:
            errorInput(helpName)

    # take the domain size of bacteria
    while True:
        # Take user input
        bacteriaDomainSize = input("Please enter the domain area on the bacteria you want to simulate  "
                                   "(in format: ###x### (length x width) or help for more information): \n")

        # set the name
        helpName = "SIZE"

        # check the validity of input
        if bacteriaDomainSize.upper() == "HELP":
            helpMessage(helpName)
        else:
            # check the format of the input
            if bool(re.match("\d+[x]\d+", bacteriaDomainSize)):
                # check this input size if valid
                valid = checkSize(bacteriaDomainShape, bacteriaDomainSize)

                # if not valid
                if not valid:
                    errorInput(bacteriaDomainShape)
                    continue

                # if valid, record and break
                else:
                    bacteriaDomainSize = valid
                    break
            else:
                errorInput(helpName)

    # get the interval
    while True:
        # Take user input
        interval = input("Please enter the interval on x-direction and y direction you want to simulate, "
                         "enter in format ###x###, first number is x and second number is y"
                         " (type help for more information): \n")

        # set the name
        helpName = "INTERVAL"

        # if type help
        if interval.upper() == "HELP":
            helpMessage(helpName)
            continue

        # check if the format of input
        if not bool(re.match("\d+[x]\d+", interval)):
            print("Wrong format\n")
            errorInput(helpName)

        # check the validity of input and do reaction
        interval = interval.split("x")
        result = eval(execDict[helpName])

        if result:
            interval_x = int(interval[0])
            interval_y = int(interval[1])
            break
        else:
            errorInput(helpName)

    # if simulation type is not 1, take in extra info
    while True:

        # check the simulation type
        if simulationType == 1:
            filmNum = "1"
            bacteriaNum = "1"
            break

        elif simulationType == 2:
            filmNum = "1"
            bacteriaNum = input("Please enter the number of bacteria you want to test or help for more information: ")
            number = bacteriaNum

        elif simulationType == 3:
            filmNum = input("Please enter the number of bacteria you want to test or help for more information: ")
            bacteriaNum = "1"
            number = filmNum
        else:
            raise RuntimeError("Wrong simulation type, causes get bacteria/film number error")

        # set the name
        helpName = "NUMBER"

        # if type help
        if bacteriaNum.upper() == "HELP" or filmNum.upper() == "HELP":
            helpMessage(helpName)
            continue

        # check the validity of input and do reaction
        result = eval(execDict[helpName])

        if not checkNum(bacteriaNum) or not checkNum(filmNum):
            errorInput(helpName)
        elif result:
            filmNum = int(filmNum)
            bacteriaNum = int(bacteriaNum)
            break
        else:
            errorInput(helpName)

    # generate simulation program
    showMessage("Start to generate the simulation simulator ......")
    writeLog([simulationType, trail, dimension,
              filmSeed, filmSurfaceSize, filmSurfaceShape, filmSurfaceCharge,
              filmDomainSize, filmDomainShape, filmDomainCon,
              bacteriaSeed, bacteriaSize, bacteriaSurfaceShape, bacteriaSurfaceCharge,
              bacteriaDomainSize, bacteriaDomainShape, bacteriaDomainCon, filmNum, bacteriaNum,
              interval_x, interval_y])

    sim = EnergySimulator(simulationType, trail, dimension,
                     filmSeed, filmSurfaceSize, filmSurfaceShape, filmSurfaceCharge,
                     filmDomainSize, filmDomainShape, filmDomainCon,
                     bacteriaSeed, bacteriaSize, bacteriaSurfaceShape, bacteriaSurfaceCharge,
                     bacteriaDomainSize, bacteriaDomainShape, bacteriaDomainCon, filmNum, bacteriaNum,
                     interval_x, interval_y)

    showMessage("Simulator generate done")

    # run the simulation
    showMessage("Start to run simulate ......")
    sim.runSimulate()

    # finish whole simulation
    showMessage("Whole simulation done")


def errorInput(helpName: str) -> None:
    """
    This function print the message of user putin not valid input
    """
    print("Invalid input, please enter again.\n")
    print(infoDict[helpName].replace("\\n", "\n"))


def checkSize(shape: str, size: str) -> Union[bool, Tuple[int, int]]:
    """
    This function checks the size input is satisfied the restriction of the shape
    return False if not satisfy, else return a Tuple with (length, width)
    """
    # get the size
    size = size.split("x")

    length = int(size[0])
    width = int(size[1])

    # set the checker
    result = eval(execDict[shape.upper()])

    # check the result
    if not result:
        return False
    else:
        return (length, width)


def helpMessage(helpName: str) -> None:
    """
    This function print the help message
    """
    print(helpDict[helpName].replace("\\n", "\n"))
    print(infoDict[helpName].replace("\\n", "\n"))


def checkNum(input: str) -> bool:
    """
    This function take in a string and test does it can be convert to number
    """
    try:
        int(input)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    # get the help info
    helpDict = getHelp()

    # get special info dict, exec dict
    infoDict, execDict = getRestriction()

    # get log file
    openLog()

    # call the user input function
    getArgument()

    # close
    closeLog()
