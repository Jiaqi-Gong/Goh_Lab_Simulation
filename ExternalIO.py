"""
This file deal with the read/write from the text file
"""
import os
from datetime import datetime
from typing import Dict, IO, List
from multiprocessing import Pool, cpu_count

import numpy as np
from numpy import ndarray
from openpyxl.packaging import workbook
import time
import math

import matplotlib as mpl

mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm

LOG_CACH = []

# INDICATOR record three bool
# first is generate image or not, second is generate log or not, third is write log at last or not
INDICATOR = [False, False, False]


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


def setIndicator(writeImage: bool, recordLog: bool, writeAtLast: bool) -> str:
    """
    This function set indicator
    """

    # get time
    now = datetime.now()
    day = now.strftime("%m_%d")
    current_time = now.strftime("%H_%M_%S")

    # based on pass in, set indicator and generate path
    message = ""

    # if write image
    if writeImage:
        INDICATOR[0] = True

        # generate image folder for save result
        if not os.path.exists("Image"):
            os.mkdir("Image")

        global picFolder
        picFolder = "Image/{}_{}".format(day, current_time)

        if not os.path.exists(picFolder):
            os.mkdir(picFolder)

        message += "Image is saved at: {}\n".format(picFolder)
    else:
        message += "Set to not generate image\n"

    if recordLog:
        INDICATOR[1] = True

        if not os.path.exists("Log"):
            os.mkdir("Log")

        log_name = "Log/log_{}_{}.txt".format(day, current_time)
        _openLog(log_name)

        message += "Log saved as: {}\n".format(log_name)
    else:
        message += "Set not to save Log\n"

    if writeAtLast:
        INDICATOR[2] = True

    return message


def _openLog(log_name) -> None:
    """
    This function open a log file
    """
    global log
    log = open(log_name, "w")


def closeLog() -> None:
    """
    This function close the log file
    """
    if not INDICATOR[1]:
        pass
    else:
        showMessage("Start to close log")
        startTime = time.time()
        if INDICATOR[2]:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")

            info = "Time: {}, {}\n".format(current_time, "Write log at last, start to write it")
            log.write(info)

            for i in LOG_CACH:
                log.write(i)

            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")

            info = "Time: {}, {}\n".format(current_time, "Write log at last done")
            log.write(info)

            endTime = time.time()
            totalTime = endTime - startTime

            showMessage(f"Total time it took to write log is {totalTime} seconds")

        log.close()


def writeLog(message) -> None:
    """
    This function write the message into log
    """
    if INDICATOR[1]:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        info = "Time: {}, {}\n".format(current_time, message)

        # depends on the requirement, write log now or later
        if INDICATOR[2]:
            log.write(info)
        else:
            LOG_CACH.append(info)


def showMessage(message: str) -> None:
    """
    This function take in a message and print it to the screen and record into the log file
    """
    # print to screen
    print(message)

    # write into the log
    writeLog(message)


def saveResult(wb: workbook, path: str) -> None:
    """
    This function take in a wb for the workbook need to save in the path given
    """
    if not os.path.exists("Result"):
        os.mkdir("Result")

    wb.save(path)

    showMessage("Output done, saved at {}".format(path))


def visPlot(array: ndarray, picName: str, dimension: int) -> None:
    """
    THis function based on the dimension of passed in ndarray to call appropriate function
    """
    if INDICATOR[0]:
        writeLog(["This is visplot", array, picName, dimension])
        # based on the dimension call different function to generate image
        if dimension == 2:
            _visPlot2D(array, picName)
        elif dimension == 3:
            _visPlot3D(array, picName)
        else:
            raise RuntimeError("Unknown dimension of array pass in")


def _visPlot2D(array: ndarray, picName: str) -> None:
    """
    This function take in a 2D ndarray and save this array as a image with given name
    """
    showMessage("Start to generate image")

    startTime = time.time()

    now = datetime.now()
    day = now.strftime("%m_%d")
    current_time = now.strftime("%H_%M_%S")

    # locate where the positive, negative, and neutral charges are
    pos = np.where(array == 1)
    neu = np.where(array == 0)
    neg = np.where(array == -1)

    # Calculate maximum
    max1 = [max(pos[i]) for i in range(len(pos)) if len(pos[i]) != 0]
    max2 = [max(neu[i]) for i in range(len(neu)) if len(neu[i]) != 0]
    max3 = [max(neg[i]) for i in range(len(neg)) if len(neg[i]) != 0]
    maximum = max(max1 + max2 + max3)

    # initialize the figure and subplot
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # set the title name
    if 'film' in picName:
        # set title
        name = "Surface of Film"

    else:
        # set title
        name = 'Surface of Bacteria'

    # initialize colors and labels
    colors = [np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1])]
    labels = ["negative", "neutral", "positive"]

    # define color map
    color_map = {-1: np.array([255, 0, 0]),  # red
                 0: np.array([0, 255, 0]),  # green
                 1: np.array([0, 0, 255])}  # blue

    data_3d = np.ndarray(shape=(array.shape[0], array.shape[1], 3), dtype=int)
    for i in range(0, array.shape[0]):
        for j in range(0, array.shape[1]):
            data_3d[i][j] = color_map[array[i][j]]

    # generate the image
    ax.imshow(data_3d, origin='lower')

    # create the legend
    for i in range(len(colors)):
        plt.plot(0, 0, "s", color=colors[i], label=labels[i])

    ax.legend(loc="upper right", bbox_to_anchor=(1.5, 1.0))

    # set x limit and y limit
    ax.set_xlim(0, maximum)
    ax.set_ylim(0, maximum)

    # set x and y labels
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    # set label and tick position
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')

    plt.title(name)

    # create folder to save figure in
    global picFolder
    if "picFolder" not in globals():
        # save the image
        if not os.path.exists("Image"):
            os.mkdir("Image")

        picFolder = "Image/{}_{}".format(day, current_time)
        if not os.path.exists(picFolder):
            os.mkdir(picFolder)

    picPath = "{}/{}.png".format(picFolder, picName)

    plt.savefig(picPath, dpi=300, bbox_inches='tight')
    endTime = time.time()
    totalTime = endTime - startTime

    showMessage(f"Total time it took to generate 2D image is {totalTime} seconds")
    showMessage("Image generate done")


def _visPlot3D(array: ndarray, picName: str) -> None:
    """
    This function take in a 3D ndarray and save this array as a image with given name
    """
    showMessage("Start to generate image")

    startTime = time.time()

    now = datetime.now()
    day = now.strftime("%m_%d")
    current_time = now.strftime("%H_%M_%S")

    # create a folder to store all the images
    global picFolder
    if "picFolder" not in globals():
        # save the image
        if not os.path.exists("Image"):
            os.mkdir("Image")

        picFolder = "Image/{}_{}".format(day, current_time)
        if not os.path.exists(picFolder):
            os.mkdir(picFolder)

    # separate the way to generate images into 2 cases
    # if the surface is a film, we only need to see the top
    if "film" in picName:
        # we will only look at the x-y plane
        array = array[0]

        # locate where the positive, negative, and neutral charges are
        pos = np.where(array == 1)
        neu = np.where(array == 0)
        neg = np.where(array == -1)

        # initialize the figure and subplots
        fig = plt.figure()
        ax = fig.add_subplot(111)

        # Calculate maximum
        max1 = [max(pos[i]) for i in range(len(pos)) if len(pos[i]) != 0]
        max2 = [max(neu[i]) for i in range(len(neu)) if len(neu[i]) != 0]
        max3 = [max(neg[i]) for i in range(len(neg)) if len(neg[i]) != 0]
        maximum = max(max1 + max2 + max3)

        # initialize colors and labels
        colors = [np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1])]
        labels = ["negative", "neutral", "positive"]

        # define color map
        color_map = {-1: np.array([255, 0, 0]),  # red
                     0: np.array([0, 255, 0]),  # green
                     1: np.array([0, 0, 255])}  # blue

        data_3d = np.ndarray(shape=(array.shape[0], array.shape[1], 3), dtype=int)
        for i in range(0, array.shape[0]):
            for j in range(0, array.shape[1]):
                data_3d[i][j] = color_map[array[i][j]]

        # generate the image
        ax.imshow(data_3d, origin='lower')

        # create the legend
        for i in range(len(colors)):
            plt.plot(0, 0, "s", color=colors[i], label=labels[i])

        ax.legend(loc="upper right", bbox_to_anchor=(1.5, 1.0))

        # set x limit and y limit
        ax.set_xlim(0, maximum)
        ax.set_ylim(0, maximum)

        # set x and y labels
        ax.set_xlabel("X")
        ax.set_ylabel("Y")

        # set label and tick position
        ax.xaxis.set_ticks_position('top')
        ax.xaxis.set_label_position('top')

        plt.title("Above the film")

        # save file
        plt.savefig('{}/{}'.format(picFolder, picName), dpi=300, bbox_inches='tight')

    elif "bacteria" in picName:

        global picFolderEach
        picFolderEach = "{}/{}".format(picFolder, picName)
        if not os.path.exists(picFolderEach):
            os.mkdir(picFolderEach)

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # position of positive
        pos = np.where(array == 1)
        pos_z = pos[0]
        pos_y = pos[1]
        pos_x = pos[2]

        # position of neutral
        neu = np.where(array == 0)
        neu_z = neu[0]
        neu_y = neu[1]
        neu_x = neu[2]

        # position of negative
        neg = np.where(array == -1)
        neg_z = neg[0]
        neg_y = neg[1]
        neg_x = neg[2]

        # set axis limit

        # get the largest number in all x,y,z scales
        max1 = [max(pos[i]) for i in range(len(pos)) if len(pos[i]) != 0]
        max2 = [max(neu[i]) for i in range(len(neu)) if len(neu[i]) != 0]
        max3 = [max(neg[i]) for i in range(len(neg)) if len(neg[i]) != 0]
        maximum = max(max1 + max2 + max3)
        ax.set_xlim3d(0, maximum)
        ax.set_ylim3d(0, maximum)
        ax.set_zlim3d(0, maximum)

        ax.set_aspect('auto')
        fig.canvas.draw()

        dimension = ax.get_tightbbox(fig.canvas.get_renderer(),
                                     call_axes_locator=True,
                                     bbox_extra_artists=None)

        showMessage(f"x is {dimension.width - dimension.x0}, y is {dimension.height - dimension.y0}")

        size = ((dimension.width - dimension.x0) / (maximum)) * ((dimension.height - dimension.y0) / (maximum))
        showMessage(f"size of marker is {size}")

        # order which we plot the points matter
        nPos = len(pos_x)
        nNeu = len(neu_x)
        nNeg = len(neg_x)

        # initialize shape and depthshade of the marker
        marker = 's'
        depthshade = True
        colors = [np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1])]

        # if positive is the charge of surface, we plot positive first
        if nPos == max(nPos, nNeu, nNeg):
            ax.scatter3D(neu_x, neu_y, neu_z, marker=marker, label='neutral', color=colors[1], depthshade=depthshade,
                         s=size, linewidths=0)
            ax.scatter3D(neg_x, neg_y, neg_z, marker=marker, label='negative', color=colors[0], depthshade=depthshade,
                         s=size, linewidths=0)
            ax.scatter3D(pos_x, pos_y, pos_z, marker=marker, label='positive', color=colors[2], depthshade=depthshade,
                         s=size, linewidths=0)

        # if negative is the charge of surface, we plot negative first
        elif nNeg == max(nPos, nNeu, nNeg):
            ax.scatter3D(neu_x, neu_y, neu_z, marker=marker, label='neutral', color=colors[1], depthshade=depthshade,
                         s=size, linewidths=0)
            ax.scatter3D(pos_x, pos_y, pos_z, marker=marker, label='positive', color=colors[2], depthshade=depthshade,
                         s=size, linewidths=0)
            ax.scatter3D(neg_x, neg_y, neg_z, marker=marker, label='negative', color=colors[0], depthshade=depthshade,
                         s=size, linewidths=0)

        # if neutral is the charge of surface, we plot neutral first
        elif nNeu == max(nPos, nNeu, nNeg):
            ax.scatter3D(pos_x, pos_y, pos_z, marker=marker, label='positive', color=colors[2], depthshade=depthshade,
                         s=size, linewidths=0)
            ax.scatter3D(neg_x, neg_y, neg_z, marker=marker, label='negative', color=colors[0], depthshade=depthshade,
                         s=size, linewidths=0)
            ax.scatter3D(neu_x, neu_y, neu_z, marker=marker, label='neutral', color=colors[1], depthshade=depthshade,
                         s=size, linewidths=0)

        # create the legend
        lgnd = ax.legend(loc="upper right")
        for handle in lgnd.legendHandles:
            handle.set_sizes([10.0])

        # set label names
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

        # save each side of the picture
        elevation = [0, 90, -90]
        azimuth = [0, 90, -90, 180]
        # if the sides are really small, we don't need to output the sides
        # first 4 sides
        for i in range(len(azimuth)):
            # initialize camera angle
            elev = elevation[0]
            azim = azimuth[i]
            ax.view_init(elev=elev, azim=azim)

            # name the title
            if azim == 0:
                title = 'Front'
            elif azim == 180:
                title = 'Behind'
            elif azim == 90:
                title = 'Right'
            elif azim == -90:
                title = 'Left'

            plt.title(title)
            # save file
            plt.savefig('{}/From_{}_of_Bacteria.png'.format(picFolderEach, title), dpi=300, bbox_inches='tight')

        # last 2 sides
        for i in range(len(elevation) - 1):
            # initialize the camera angle
            elev = elevation[i + 1]
            azim = azimuth[0]
            ax.view_init(elev=elev, azim=azim)

            # name the title
            if elev == 90:
                title = 'Above'
            elif elev == -90:
                title = 'Below'
            plt.title(title)
            # save file
            plt.savefig('{}/From_{}_of_Bacteria.png'.format(picFolderEach, title), dpi=300, bbox_inches='tight')

    endTime = time.time()
    totalTime = endTime - startTime

    showMessage(f"Total time it took to generate image is {totalTime} seconds")
    showMessage("Image generate done")


def importSurface(filepath: str) -> List[List, ndarray]:
    """
    This function read in the pre-generated surface structure
    :param filepath: file path to the surface structure want to import
    """

    # should be implement here, but not done for now
    raise NotImplementedError
