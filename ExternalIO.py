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
from matplotlib.colors import LinearSegmentedColormap

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

    # showMessage(array)

    # digits
    cL = -len(str(len(array[0]))) + 1
    cW = -len(str(len(array))) + 1

    # dividor
    dividorL = int(round(len(array[0]), cL) / int(str(round(len(array[0]), cL))[0]+str(round(len(array[0]), cL))[1]))
    dividorW = int(round(len(array), cW) / int(str(round(len(array), cW))[0]+str(round(len(array), cW))[1]))

    # calculate length and width of image
    img_length = len(array[0]) // dividorL
    img_width = len(array) // dividorW

    showMessage(f"Length of image is {img_length}, width of image is {img_width}")

    # Calculate maximum
    max1 = [max(pos[i]) for i in range(len(pos)) if len(pos[i]) != 0]
    max2 = [max(neu[i]) for i in range(len(neu)) if len(neu[i]) != 0]
    max3 = [max(neg[i]) for i in range(len(neg)) if len(neg[i]) != 0]
    maximum = max(max1 + max2 + max3)

    fig = plt.figure(figsize=(img_length, img_width))
    # fig = plt.figure()
    ax = fig.add_subplot(111)


    # ax.set_aspect(1)
    # fig.canvas.draw()

    if 'film' in picName:
        # set title
        name = "Surface of Film"

    else:
        # set title
        name = 'Surface of Bacteria'

    # initialize colors and labels
    colors = ['red','green','blue']
    labels = ["negative", "neutral", "positive"]
    # levels = np.linspace(-2,2,5)

    # separate the cases into 3
    # if no negative is present
    if len(neg[0]) == 0:
        colors.remove('red')
        labels.remove('negative')
        # levels = np.delete(levels, 1)
        showMessage('removed negative')
    # if no neutral is present
    if len(neu[0]) == 0:
        colors.remove('green')
        labels.remove('neutral')
        # levels = np.delete(levels, 2)
        showMessage('removed neutral')

    # if no positive is present
    if len(pos[0]) == 0:
        colors.remove('blue')
        labels.remove('positive')
        # levels = np.delete(levels, 3)
        showMessage('removed positive')

    # initialize colors
    n_bins = len(colors)
    cmap_name = 'my_list'
    cmap = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)

    ax.imshow(array, origin='lower', cmap=cmap)

    for i in range(len(colors)):
        plt.plot(0, 0, "-", color=colors[i], label=labels[i])

    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.0))
    # proxy = [plt.Rectangle((1, 1), 2, 2, fc=pc.get_facecolor()[0]) for pc in
    #          surface.collections]
    #
    # ax.legend(proxy, labels)

    # lgnd = ax.legend(loc="upper right")
    # for handle in lgnd.legendHandles:
    #     handle.set_sizes([10.0])


    # set x limit and y limit
    ax.set_xlim(0, maximum)
    ax.set_ylim(0, maximum)

    # set x and y labels
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    # set label and tick position
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')


    # plt.xlim(0,maximum)
    # plt.ylim(0,maximum)
    # plt.xlabel('X')
    # plt.ylabel('Y')
    plt.title(name)

    global picFolder
    if "picFolder" not in globals():
        # save the image
        if not os.path.exists("Image"):
            os.mkdir("Image")

        picFolder = "Image/{}_{}".format(day, current_time)
        if not os.path.exists(picFolder):
            os.mkdir(picFolder)

    picPath = "{}/{}".format(picFolder, picName)

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

    showMessage(array)
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

        # digits
        cL = -len(str(len(array[0]))) + 1
        cW = -len(str(len(array))) + 1

        # dividor
        dividorL = int(round(len(array[0]), cL) / int(str(round(len(array[0]), cL))[0] + str(round(len(array[0]), cL))[1]))
        dividorW = int(round(len(array), cW) / int(str(round(len(array), cW))[0] + str(round(len(array), cW))[1]))

        # calculate length and width of image
        img_length = len(array[0]) // dividorL
        img_width = len(array) // dividorW

        # initialize the figure and subplots
        fig = plt.figure(figsize=(img_length, img_width))
        # fig = plt.figure()
        ax = fig.add_subplot(111)
        showMessage(f"Length of image is {img_length}, width of image is {img_width}")

        # Calculate maximum
        max1 = [max(pos[i]) for i in range(len(pos)) if len(pos[i]) != 0]
        max2 = [max(neu[i]) for i in range(len(neu)) if len(neu[i]) != 0]
        max3 = [max(neg[i]) for i in range(len(neg)) if len(neg[i]) != 0]
        maximum = max(max1 + max2 + max3)

        # initialize colors and labels
        colors = ['red', 'green', 'blue']
        labels = ["negative", "neutral", "positive"]

        # remove colors and labels for charge that is not present
        # separate the cases into 3
        # if no negative is present
        if len(neg[0]) == 0:
            colors.remove('red')
            labels.remove('negative')
            showMessage('removed negative')
        # if no neutral is present
        if len(neu[0]) == 0:
            colors.remove('green')
            labels.remove('neutral')
            showMessage('removed neutral')

        # if no positive is present
        if len(pos[0]) == 0:
            colors.remove('blue')
            labels.remove('positive')
            showMessage('removed positive')

        # create the color map
        n_bins = len(colors)
        cmap_name = 'my_list'
        cmap = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)

        ax.imshow(array, origin='lower', cmap=cmap)

        for i in range(len(colors)):
            plt.plot(0, 0, "-", color=colors[i], label=labels[i])

        ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.0))

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

        # make a subfolder containing the 6 sides of the surface
        global picFolderEach
        picFolderEach = "{}/{}".format(picFolder, picName)
        if not os.path.exists(picFolderEach):
            os.mkdir(picFolderEach)

        # initialize the 6 sides
        # [z0,z1,y0,y1,x0,x1]
        title = ['Above','Below','Front','Behind','Left','Right']
        changer = [1,array.shape[0]-1,1,array.shape[1],1,array.shape[2]]
        axesLabels = [['X','Y'], ['X','Y'], ['X','Z'], ['X','Z'], ['Y','Z'], ['Y','Z']]

        for i in range(len(title)):
            # initialize the range
            range = [array.shape[0],0,array.shape[1],0,array.shape[2],0]
            # change the array
            range[i] = changer[i]
            array = array[range[1]:range[0],range[3]:range[2],range[5]:range[4]]

            # locate where the positive, negative, and neutral charges are
            pos = np.where(array == 1)
            neu = np.where(array == 0)
            neg = np.where(array == -1)

            # digits
            cL = -len(str(len(array[0]))) + 1
            cW = -len(str(len(array))) + 1

            # dividor
            dividorL = int(round(len(array[0]), cL) / int(str(round(len(array[0]), cL))[0] + str(round(len(array[0]), cL))[1]))
            dividorW = int(round(len(array), cW) / int(str(round(len(array), cW))[0] + str(round(len(array), cW))[1]))

            # calculate length and width of image
            img_length = len(array[0]) // dividorL
            img_width = len(array) // dividorW

            # initialize the figure and subplots
            fig = plt.figure(figsize=(img_length, img_width))
            # fig = plt.figure()
            ax = fig.add_subplot(111)
            showMessage(f"Length of image is {img_length}, width of image is {img_width}")

            # Calculate maximum
            max1 = [max(pos[i]) for i in range(len(pos)) if len(pos[i]) != 0]
            max2 = [max(neu[i]) for i in range(len(neu)) if len(neu[i]) != 0]
            max3 = [max(neg[i]) for i in range(len(neg)) if len(neg[i]) != 0]
            maximum = max(max1 + max2 + max3)

            # initialize colors and labels
            colors = ['red', 'green', 'blue']
            labels = ["negative", "neutral", "positive"]

            # remove colors and labels for charge that is not present
            # separate the cases into 3
            # if no negative is present
            if len(neg[0]) == 0:
                colors.remove('red')
                labels.remove('negative')
                showMessage('removed negative')
            # if no neutral is present
            if len(neu[0]) == 0:
                colors.remove('green')
                labels.remove('neutral')
                showMessage('removed neutral')

            # if no positive is present
            if len(pos[0]) == 0:
                colors.remove('blue')
                labels.remove('positive')
                showMessage('removed positive')

            # create the color map
            n_bins = len(colors)
            cmap_name = 'my_list'
            cmap = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)

            ax.imshow(array, origin='lower', cmap=cmap)

            for i in range(len(colors)):
                plt.plot(0, 0, "-", color=colors[i], label=labels[i])

            ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.0))

            # set x limit and y limit
            ax.set_xlim(0, maximum)
            ax.set_ylim(0, maximum)

            # set x and y labels
            ax.set_xlabel(axesLabels[i][0])
            ax.set_ylabel(axesLabels[i][1])

            # set label and tick position
            ax.xaxis.set_ticks_position('top')
            ax.xaxis.set_label_position('top')

            plt.title(title[i])

            plt.savefig('{}/From_{}_of_Bacteria.png'.format(picFolderEach, title), dpi=300, bbox_inches='tight')


    endTime = time.time()
    totalTime = endTime - startTime

    showMessage(f"Total time it took to generate image is {totalTime} seconds")
    showMessage("Image generate done")

# def _generateImage
