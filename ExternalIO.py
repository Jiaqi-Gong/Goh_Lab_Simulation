"""
This file deal with the read/write from the text file
"""
from datetime import datetime
from typing import Dict, IO
import logging

from openpyxl.packaging import workbook


def getHelp() -> Dict[str, str]:
    """
    This function get the help information in the help file
    :return: a dictionary, key is parameter name, value is word explanation
    """
    file = open("TextFile/HelpFile.txt", "r")
    content = file.readlines()
    dict = {}

    for line in content:
        # if this line is not empty, read the line and add to dictionary
        if len(line) != 0:
            string = line.split(":")
            dict[string[0].upper()] = string[1][1:]

    file.close()

    return dict


def getRestriction() -> [Dict[str, str], Dict[str, str]]:
    """
    This function get the content in the SpecialRequirement.txt and convert it to two dictionary for checking
    """
    file = open("TextFile/SpecialRequirement.txt", "r")
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


def openLog() -> None:
    """
    This function open a log file
    """
    now = datetime.now()
    current_time = now.strftime("%H_%M_%S")

    global log
    log = open("Log/log_{}.txt".format(current_time), "w")


def closeLog() -> None:
    """
    This function close the log file
    """
    log.close()


def showMessage(message: str) -> None:
    """
    This function take in a message and print it to the screen and record into the log file
    """
    # print to screen
    print(message)

    # write into the log
    writeLog(message)


def writeLog(message) -> None:
    """
    This function write the message into log
    """
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    log.write("Time: {}, {}\n".format(current_time, message))


def saveResult(wb: workbook, path: str) -> None:
    """
    This function take in a wb for the workbook need to save in the path given
    """
    wb.save(path)

    showMessage("Output done, saved at {}".format(path))
