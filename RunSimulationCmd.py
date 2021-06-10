"""
This is a text interface for running the simulation
"""
import re
from typing import Dict

import Simulation


def get_arguement() -> None:
    """
    This function take the seeting arguement from the user and call Simulation file to run the program
    :return: None
    """
    # take the help info
    helpDict = getHelp()

    # take dimension
    while True:
        # Take user input
        dimension = input("Please enter the dimension you want to simulate (2 for 2D, 3 for 3D, "
                          "help for more information): \n")

        # check the validity of input
        if dimension == "2" or dimension == "3":
            break
        elif dimension == "help":
            print("This is the dimension you want to simulate")
        else:
            print("Invalid input, please enter again.")

    # take surface area size
    while True:
        # Take user input
        filmSurfaceSize = input("Please enter the film surface area you want to simulate (small, medium, large "
                            "or enter in format: ###x### \n"
                            "help for more information): \n")

        # check the validity of input
        if filmSurfaceSize == "help":
            raise NotImplementedError
            # print("This is the area of the surface you want to simulate, small for:")
        elif filmSurfaceSize == "small":
            raise NotImplementedError
        elif filmSurfaceSize == "medium":
            raise NotImplementedError
        elif filmSurfaceSize == "large":
            raise NotImplementedError
        else:
            # check the format of the input
            if bool(re.match("\d+[x]\d+", filmSurfaceSize)):
                break
            else:
                print("Invalid input, please enter again.")

    # take shape of the surface
    while True:
        # Take user input
        filmSurfaceShape = input("Please enter the shape of the surface you want to simulate ("
                          "help for more information): \n")


        # check the validity of input
        if filmSurfaceShape == "help":
            raise NotImplementedError
        else:
            raise NotImplementedError
            print("Invalid input, please enter again.")

    # take charge of the surface
    while True:
        # Take user input
        filmSurfaceCharge = input("Please enter the charge of the surface you want to simulate ("
                             "help for more information): \n")

        # check the validity of input
        if filmSurfaceCharge == "help":
            raise NotImplementedError
        else:
            raise NotImplementedError
            print("Invalid input, please enter again.")

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

    # take number of bacteria want
    while True:
        # Take user input
        bacteriaCon = input("Please enter the concentration of the bacteria you want to simulate ("
                             "help for more information): \n")

        # check the validity of input
        if bacteriaCon == "help":
            raise NotImplementedError
        else:
            raise NotImplementedError
            print("Invalid input, please enter again.")


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
            dict[string[0]] = string[1]

    file.close()

    return dict



if __name__ == '__main__':
    get_arguement()
