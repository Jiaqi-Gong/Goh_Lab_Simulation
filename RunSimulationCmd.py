"""
This is a text interface for running the simulation
Checking all user input is valid at here
"""
import re
from typing import Dict, Union, Tuple

import Simulation


def getArgument() -> None:
    """
    This function take the setting argument from the user and call Simulation file to run the program
    Check all user input valid at here
    :return: None
    """

    # init result for future use
    result = False

    # take simulation type
    while True:
        trail = input("Please enter simulation type: \n")

        # set the name
        helpName = "TYPE"

        # check the validity of input and do reaction
        result = "result =" + execDict[helpName]
        exec(result)

        if result:
            break
        elif trail.upper() == "HELP":
            print(helpDict[helpName], infoDict[helpName])
        else:
            errorInput(helpName)

    # take trail number
    while True:
        trail = input("Please enter trail number: \n")

        # set the name
        helpName = "TRAIL"

        # check the validity of input and do reaction
        result = "result =" + execDict[helpName]
        exec(result)

        if result:
            break
        elif trail.upper() == "HELP":
            print(helpDict[helpName], infoDict[helpName])
        else:
            errorInput(helpName)

    # take seed number
    while True:
        trail = input("Please enter seed number: \n")

        # set the name
        helpName = "SEED"

        # check the validity of input and do reaction
        result = "result =" + execDict[helpName]
        exec(result)

        if result:
            break
        elif trail.upper() == "HELP":
            print(helpDict[helpName], infoDict[helpName])
        else:
            errorInput(helpName)

    # take dimension
    while True:
        # Take user input
        dimension = input("Please enter the dimension you want to simulate (2 for 2D, 3 for 3D, "
                          "help for more information): \n")

        # set the name
        helpName = "DIMENSION"

        # check the validity of input and do reaction
        result = "result =" + execDict[helpName]
        exec(result)

        if result:
            break
        elif dimension.upper() == "HELP":
            print(helpDict[helpName], infoDict[helpName])
        else:
            errorInput(helpName)

    # take shape of the film surface
    while True:
        # Take user input
        filmSurfaceShape = input("Please enter the shape of the surface you want to simulate ("
                                 "help for more information): \n")

        # check the validity of input
        # set the name
        helpName = "DIMENSION"
        shape = filmSurfaceShape

        # check the validity of input and do reaction
        result = "result =" + execDict[helpName]
        exec(result)

        if result:
            break
        elif dimension.upper() == "HELP":
            print(helpDict[helpName], infoDict[helpName])
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
            print(helpDict[helpName], infoDict[helpName])
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

        # check the validity of input and do reaction
        result = "result =" + execDict[helpName]
        exec(result)

        if result:
            break
        elif filmSurfaceSize.upper() == "HELP":
            print(helpDict[helpName], infoDict[helpName])
        else:
            errorInput(helpName)


    # take shape of the bacteria
    while True:
        # Take user input
        bacteriaShape = input("Please enter the shape of the bacteria you want to simulate ("
                              "help for more information): \n")

        # check the validity of input
        if bacteriaShape == "help":
            raise NotImplementedError
        else:
            raise NotImplementedError
            print("Invalid input, please enter again.")

    # take the size of bacteria

    # take charge of the bacteria
    while True:
        # Take user input
        bacteriaCharge = input("Please enter the charge of the bacteria you want to simulate ("
                               "help for more information): \n")

        # check the validity of input
        if bacteriaCharge == "help":
            raise NotImplementedError
        else:
            raise NotImplementedError
            print("Invalid input, please enter again.")

    # take the domain shape

    # take the domain size

    # take the domain concentration

    # take

def getHelp() -> Dict[str, str]:
    """
    This function get the help information in the help file
    :return: a dictionary, key is parameter name, value is word explanation
    """
    file = open("HelpFile.txt", "r")
    content = file.readlines()
    dict = {}

    for line in content:
        # if this line is not empty, read the line and add to dictionary
        if len(line) != 0:
            string = line.split(":")
            dict[string[0].upper()] = string[1]

    file.close()

    return dict


def getRestriction() -> [Dict[str, str], Dict[str, str]]:
    """
    This function get the content in the SpecialRequirement.txt and convert it to two dictionary for checking
    """
    file = open("SpecialRequirement.txt", "r")
    content = file.readlines()
    info_dict = {}
    exec_dict = {}

    for line in content:
        # if this line is not empty, read the line and add to dictionary
        if len(line) != 0:
            string = line.split(":")
            info_dict[string[0].upper()] = string[1][1:]
            exec_dict[string[0].upper()] = string[2][1:]

    file.close()

    return info_dict, exec_dict


def errorInput(helpName: str) -> None:
    """
    This function print the message of user putin not valid input
    """
    print("Invalid input, please enter again. \n", infoDict[helpName])


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
    result = "result =" + execDict[shape.upper()]
    exec(result)

    # check the result
    if not result:
        return False
    else:
        return (length, width)


if __name__ == '__main__':
    # get the help info
    helpDict = getHelp()

    # get special info dict, exec dict
    infoDict, execDict = getRestriction()

    # call the user input function
    getArgument()
