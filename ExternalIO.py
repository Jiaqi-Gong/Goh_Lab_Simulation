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
from matplotlib import collections

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


    pos = np.where(array == 1)
    neu = np.where(array == 0)
    neg = np.where(array == -1)

    pos_x = pos[0]
    pos_y = pos[1]
    neu_x = neu[0]
    neu_y = neu[1]
    neg_x = neg[0]
    neg_y = neg[1]
    fig = plt.figure()
    ax = fig.add_subplot(111)

    colors_pos = np.repeat(np.array([[0,0,1,1]]),len(pos_x),axis=0)
    colors_neu = np.repeat(np.array([[0,1,0,1]]),len(neu_x),axis=0)
    colors_neg = np.repeat(np.array([[1,0,0,1]]),len(neg_x),axis=0)

    # # define factor
    # factor = (int(max(array.shape[0], array.shape[1])))
    # size = ((ax.get_window_extent().width / (max(array.shape[0], array.shape[1]) + 1.) * 72. / fig.dpi) ** 2)

    if 'whole_film' in picName:
        # set title
        name = "Surface of Film"

    else:
        # set title
        name = 'Surface of Bacteria'

    # ax.set_aspect(1)
    # fig.canvas.draw()
    #
    # ax.scatter(pos_x, pos_y, c='blue', label='pos', s=size)
    # ax.scatter(neu_x, neu_y, c='green', label='neu', s=size)
    # ax.scatter(neg_x, neg_y, c='red', label='neg', s=size)

    # create a nested list containing position [positive, neutral, negative]
    positive = [pos_x, pos_y, colors_pos]
    neutral = [neu_x, neu_y, colors_neu]
    negative = [neg_x, neg_y, colors_neg]
    nested = [positive, neutral, negative]
    # x_pos = [pos_x, neu_x, neg_x]
    # y_pos = [pos_y, neu_y, neg_y]
    # colors = [colors_pos, colors_neu, colors_neg]

    # use multiprocessing to speed up visualization
    pool = Pool(3)
    c = pool.starmap(_circleAdder, nested)
    # extract the PathCollection for each
    for i in c:
        ax.add_collection(i)
    # # positive
    # circlesPos = [plt.Rectangle((xi, yi), width=1, height=1, linewidth=0) for xi, yi in zip(pos_x, pos_y)]
    # cPos = collections.PatchCollection(circlesPos)
    # cPos.set_facecolor(colors_pos)
    # ax.add_collection(cPos)
    #
    # # neutral
    # circlesNeu = [plt.Rectangle((xi, yi), width=1, height=1, linewidth=0) for xi, yi in zip(neu_x, neu_y)]
    # cNeu = collections.PatchCollection(circlesNeu)
    # cNeu.set_facecolor(colors_neu)
    # ax.add_collection(cNeu)
    #
    # # negative
    # circlesNeg = [plt.Rectangle((xi, yi), width=1, height=1, linewidth=0) for xi, yi in zip(neg_x, neg_y)]
    # cNeg = collections.PatchCollection(circlesNeg)
    # cNeg.set_facecolor(colors_neg)
    # ax.add_collection(cNeg)


    # # positive
    # circlesPos = [plt.Circle((xi, yi), radius=0.5, linewidth=0, color='blue') for xi, yi in zip(pos_x, pos_y)]
    # cPos = collections.PatchCollection(circlesPos)
    # cPos.set_facecolor(colors_pos)
    # ax.add_collection(cPos)
    #
    # # neutral
    # circlesNeu = [plt.Circle((xi, yi), radius=0.5, linewidth=0, color='green') for xi, yi in zip(neu_x, neu_y)]
    # cNeu = collections.PatchCollection(circlesNeu)
    # cNeu.set_facecolor(colors_neu)
    # ax.add_collection(cNeu)
    #
    # # negative
    # circlesNeg = [plt.Circle((xi, yi), radius=0.5, linewidth=0, color='red') for xi, yi in zip(neg_x, neg_y)]
    # cNeg = collections.PatchCollection(circlesNeg)
    # cNeg.set_facecolor(colors_neg)
    # ax.add_collection(cNeg)

    # lgnd = ax.legend(loc="upper right")
    # for handle in lgnd.legendHandles:
    #     handle.set_sizes([10.0])

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')


    # set x limit and y limit
    max1 = [max(pos[i]) for i in range(len(pos)) if len(pos[i]) != 0]
    max2 = [max(neu[i]) for i in range(len(neu)) if len(neu[i]) != 0]
    max3 = [max(neg[i]) for i in range(len(neg)) if len(neg[i]) != 0]
    maximum = max(max1 + max2 + max3)

    plt.xlim(0,maximum)
    plt.ylim(0,maximum)
    plt.title(name)

    plt.imshow(array, interpolation='nearest')

    global picFolder
    if "picFolder" not in globals():
        # save the image
        if not os.path.exists("Image"):
            os.mkdir("Image")

        picFolder = "Image/{}_{}".format(day, current_time)
        if not os.path.exists(picFolder):
            os.mkdir(picFolder)

    picPath = "{}/{}".format(picFolder, picName)

    # plt.savefig(picPath, dpi=300, bbox_inches='tight')
    plt.savefig(picPath)
    endTime = time.time()
    totalTime = endTime - startTime

    showMessage(f"Total time it took to generate 2D image is {totalTime} seconds")
    showMessage("Image generate done")

def _circleAdder(x: ndarray, y:ndarray, color:ndarray) -> None:
    # extract the nested list
    # color = nested[2]
    # x = nested[0]
    # y = nested[1]
    circles = [plt.Rectangle((xi, yi), width=1, height=1, linewidth=0) for xi, yi in zip(x, y)]
    c = collections.PatchCollection(circles)
    c.set_facecolor(color)
    return c

def _visPlot3D(array: ndarray, picName: str) -> None:
    """
    This function take in a 3D ndarray and save this array as a image with given name
    """
    showMessage("Start to generate image")

    startTime = time.time()

    now = datetime.now()
    day = now.strftime("%m_%d")
    current_time = now.strftime("%H_%M_%S")
    # graph the 3D visualization
    # if the array is small, we don't
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # define factor
    factor = (int(max(array.shape[0], array.shape[1])))

    if 'whole_film' in picName:
        # set title
        name = "Surface of Film"
        # size = 40 * ((100 / factor) ** 4)

    else:
        # set title
        name = 'Surface of Bacteria'
        # size = 40 * ((100 / factor) ** 4)

    size = ((ax.get_window_extent().width / (max(array.shape[0], array.shape[1]) + 1.) * 72. / fig.dpi) ** 2)
    ax.set_aspect('auto')
    fig.canvas.draw()
    # position of positive
    pos = np.where(array == 1)
    pos_z = pos[0]
    pos_y = pos[1]
    pos_x = pos[2]
    # color of positive
    # colors_pos = np.repeat(np.array([[0,0,1,0.8]]),len(pos_z),axis=0)
    ax.scatter3D(pos_x, pos_y, pos_z, marker="o", label='positive', color='blue', depthshade=False, s=size)

    # position of neutral
    neu = np.where(array == 0)
    neu_z = neu[0]
    neu_y = neu[1]
    neu_x = neu[2]
    # colors_neu = np.repeat(np.array([[0,1,0,0.8]]),len(neu_z),axis=0)
    ax.scatter3D(neu_x, neu_y, neu_z, marker="o", label='neutral', color='green', depthshade=False, s=size)

    # position of negative
    neg = np.where(array == -1)
    neg_z = neg[0]
    neg_y = neg[1]
    neg_x = neg[2]
    # colors_neg = np.repeat(np.array([[1,0,0,0.8]]),len(neg_z),axis=0)
    ax.scatter3D(neg_x, neg_y, neg_z, marker="o", label='negative', color='red', depthshade=False, s=size)

    # position_x = np.concatenate((pos_x, neu_x, neg_x))
    # position_y = np.concatenate((pos_y, neu_y, neg_y))
    # position_z = np.concatenate((pos_z, neu_z, neg_z))
    # colors = np.concatenate((colors_pos, colors_neu, colors_neg))
    # ax.scatter3D(position_x, position_y, position_z, marker="o", label=['neutral','positive','negative'], color=colors, depthshade=False)

    lgnd = ax.legend(loc="upper right")
    for handle in lgnd.legendHandles:
        handle.set_sizes([10.0])

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    # set axis limit

    # get the largest number in all x,y,z scales
    max1 = [max(pos[i]) for i in range(len(pos)) if len(pos[i])!=0]
    max2 = [max(neu[i]) for i in range(len(neu)) if len(neu[i])!=0]
    max3 = [max(neg[i]) for i in range(len(neg)) if len(neg[i])!=0]
    maximum = max(max1+max2+max3)
    ax.set_xlim3d(0, maximum)
    ax.set_ylim3d(0, maximum)
    ax.set_zlim3d(0, maximum)

    # create a folder to store all the images
    global picFolder
    if "picFolder" not in globals():
        # save the image
        if not os.path.exists("Image"):
            os.mkdir("Image")

        picFolder = "Image/{}_{}".format(day, current_time)
        if not os.path.exists(picFolder):
            os.mkdir(picFolder)

    # if the surface is a film, we only need to see the top
    if "film" in picName:
        # set camera angle
        elev = 90
        azim = 0
        ax.view_init(elev=elev, azim=azim)
        ax.dist = 7
        plt.title("X-Y plane")

        # save file
        plt.savefig('{}/{}'.format(picFolder, picName))

    elif "bacteria" in picName:

        global picFolderEach
        picFolderEach = "{}/{}".format(picFolder, picName)
        if not os.path.exists(picFolderEach):
            os.mkdir(picFolderEach)
        # save each side of the picture
        elevation = [0, 90, -90]
        azimuth = [0, 90, -90, 180]
        # if the sides are really small, we don't need to output the sides
        # first 4 sides
        for i in range(len(azimuth)):
            elev = elevation[0]
            azim = azimuth[i]
            ax.view_init(elev=elev, azim=azim)
            ax.dist = 6

            # name the title
            if azim == 90 or azim == -90:
                plt.title('X-Z plane')
            elif azim == 0 or azim == 180:
                plt.title('Y-Z plane')

            # save file
            plt.savefig('{}/Position_at_elevation={}_azimuth={}.png'.format(picFolderEach, elevation[0], azimuth[i]))

        # last 2 sides
        for i in range(len(elevation) - 1):
            elev = elevation[i + 1]
            azim = azimuth[0]
            ax.view_init(elev=elev, azim=azim)
            ax.dist = 6

            # name the title
            plt.title('X-Y plane')

            # save file
            plt.savefig('{}/Position_at_elevation={}_azimuth={}.png'.format(picFolderEach, elevation[i + 1], azimuth[0]))

    endTime = time.time()
    totalTime = endTime - startTime

    showMessage(f"Total time it took to generate image is {totalTime} seconds")
    showMessage("Image generate done")
