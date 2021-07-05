"""
This file deal with the read/write from the text file
"""
import os
from datetime import datetime
from typing import Dict, IO
import logging

import numpy as np
from numpy import ndarray
from openpyxl.packaging import workbook
from matplotlib import pyplot as plt


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
    day = now.strftime("%m_%d")
    current_time = now.strftime("%H_%M_%S")

    if not os.path.exists("Log"):
        os.mkdir("Log")

    global log
    log = open("Log/log_{}_{}.txt".format(day, current_time), "w")


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
    if not os.path.exists("Result"):
        os.mkdir("Result")

    wb.save(path)

    showMessage("Output done, saved at {}".format(path))


def visPlot(array: ndarray, picName: str) -> None:
    """
    This function take in a ndarray and save this array as a image with given name
    """
    pos = np.where(array == 1)
    neu = np.where(array == 0)
    neg = np.where(array == -1)

    pos_x = pos[0]
    pos_y = pos[1]
    neu_x = neu[0]
    neu_y = neu[1]
    neg_x = neg[0]
    neg_y = neg[1]

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111)

    ax.scatter(pos_x, pos_y, c='blue', label='pos')
    ax.scatter(neu_x, neu_y, c='green', label='neu')
    ax.scatter(neg_x, neg_y, c='red', label='neg')
    ax.legend(loc="upper right")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')

    plt.imshow(array, interpolation='nearest')

    # save the image
    if not os.path.exists("Image"):
        os.mkdir("Image")

    now = datetime.now()
    day = now.strftime("%m_%d")
    current_time = now.strftime("%H_%M_%S")

    picFolder = "Image/{}_{}".format(day, current_time)
    if not os.path.exists(picFolder):
        os.mkdir(picFolder)

    picPath = "{}/{}".format(picFolder, picName)
    plt.savefig(picPath)

    plt.show()


