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

    # fig = plt.figure(figsize=(img_length, img_width))
    fig = plt.figure()
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
    levels = np.linspace(-2,2,5)

    # separate the cases into 3
    # if no negative is present
    if len(neg[0]) == 0:
        colors.remove('red')
        labels.remove('negative')
        levels = np.delete(levels, 1)
        showMessage('removed negative')
    # if no neutral is present
    if len(neu[0]) == 0:
        colors.remove('green')
        labels.remove('neutral')
        levels = np.delete(levels, 2)
        showMessage('removed neutral')

    # if no positive is present
    if len(pos[0]) == 0:
        colors.remove('blue')
        labels.remove('positive')
        levels = np.delete(levels, 3)
        showMessage('removed positive')

    # initialize colors
    n_bins = len(colors)
    cmap_name = 'my_list'
    cmap = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)

    ax.imshow(array, origin='lower', cmap=cmap, aspect='auto')

    for i in range(len(colors)):
        plt.plot(0, 0, ".", color=colors[i], label=labels[i])

    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.0))

    # # x, y = np.indices((len(array[0]), len(array)))
    # surface = ax.contourf(array, levels=levels, colors=colors, vmin=-1, vmax=1, origin='lower')
    # # surface = ax.contourf(x, y, array, levels=levels, cmap=cmap, vmin=-1, vmax=1)
    #
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

    # if the surface is a film, we only need to see the top
    if "film" in picName:
    # # separate the way to generate images into 2 cases
    # # if the surface is a film, we only need to see the top
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
        # fig = plt.figure(figsize=(img_length, img_width))
        fig = plt.figure()
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
        levels = np.linspace(-2,2,5)

        # remove colors and labels for charge that is not present
        # separate the cases into 3
        # if no negative is present
        if len(neg[0]) == 0:
            colors.remove('red')
            labels.remove('negative')
            levels = np.delete(levels, 1)
            showMessage('removed negative')
        # if no neutral is present
        if len(neu[0]) == 0:
            colors.remove('green')
            labels.remove('neutral')
            levels = np.delete(levels, 2)
            showMessage('removed neutral')

        # if no positive is present
        if len(pos[0]) == 0:
            colors.remove('blue')
            labels.remove('positive')
            levels = np.delete(levels, 3)
            showMessage('removed positive')

        # create the color map
        n_bins = len(colors)
        cmap_name = 'my_list'
        cmap = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)

        ax.imshow(array, origin='lower', cmap=cmap)

        for i in range(len(colors)):
            plt.plot(0, 0, "s", color=colors[i], label=labels[i])

        ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.0))

        # # x, y = np.indices((len(array[0]), len(array)))
        # surface = ax.contourf(array, levels=levels, colors=colors, vmin=-1, vmax=1, origin='lower')
        # # surface = ax.contourf(x, y, array, levels=levels, cmap=cmap, vmin=-1, vmax=1)
        #
        #
        # proxy = [plt.Rectangle((1, 1), 2, 2, fc=pc.get_facecolor()[0]) for pc in
        #          surface.collections]
        #
        # ax.legend(proxy, labels)

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

        extent = max(ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted()).width * fig.dpi,
                     ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted()).height * fig.dpi)

        dimension = ax.get_tightbbox(fig.canvas.get_renderer(),
                                     call_axes_locator=True,
                                     bbox_extra_artists=None)

        showMessage(f"x is {dimension.width - dimension.x0}, y is {dimension.height - dimension.y0}")

        size = ((dimension.width - dimension.x0)/(maximum)) * ((dimension.height - dimension.y0)/(maximum))
        # size = (((extent / (maximum * (fig.dpi / 72.)))) ** 2)
        # size = ((ax.transData.transform([(1, 0, 0)]) - ax.transData.transform([(0, 0, 0)]))[0, 0, 0]) ** 2

        # M = ax.transData.get_matrix()
        # xscale = M[0, 0]
        # yscale = M[1, 1]
        #
        # size = (xscale * yscale)
        showMessage(f"size of marker is {size}")

        # size = ((ax.get_window_extent().width / (max(array.shape[0], array.shape[1]) + 1.) * 72. / fig.dpi) ** 2)
        # order which we plot the points matter
        nPos = len(pos_x)
        nNeu = len(neu_x)
        nNeg = len(neg_x)

        marker = 's'
        depthshade = True

        # if positive is the charge of surface, we plot positive first
        if nPos == max(nPos, nNeu, nNeg):
            ax.scatter3D(neu_x, neu_y, neu_z, marker=marker, label='neutral', color='green', depthshade=depthshade,
                         s=size, linewidths=0)
            ax.scatter3D(neg_x, neg_y, neg_z, marker=marker, label='negative', color='red', depthshade=depthshade,
                         s=size, linewidths=0)
            ax.scatter3D(pos_x, pos_y, pos_z, marker=marker, label='positive', color='blue', depthshade=depthshade,
                         s=size, linewidths=0)

        elif nNeg == max(nPos, nNeu, nNeg):
            ax.scatter3D(xs=neu_x, ys=neu_y, zs=neu_z, marker=marker, label='neutral', color='green', depthshade=depthshade,
                         s=size, linewidths=0)
            ax.scatter3D(xs=pos_x, ys=pos_y, zs=pos_z, marker=marker, label='positive', color='blue', depthshade=depthshade,
                         s=size, linewidths=0)
            ax.scatter3D(xs=neg_x, ys=neg_y, zs=neg_z, marker=marker, label='negative', color='red', depthshade=depthshade,
                         s=size, linewidths=0)

        elif nNeu == max(nPos, nNeu, nNeg):
            ax.scatter3D(pos_x, pos_y, pos_z, marker=marker, label='positive', color='blue', depthshade=depthshade,
                         s=size, linewidths=0)
            ax.scatter3D(neg_x, neg_y, neg_z, marker=marker, label='negative', color='red', depthshade=depthshade,
                         s=size, linewidths=0)
            ax.scatter3D(neu_x, neu_y, neu_z, marker=marker, label='neutral', color='green', depthshade=depthshade,
                         s=size, linewidths=0)

        lgnd = ax.legend(loc="upper right")
        for handle in lgnd.legendHandles:
            handle.set_sizes([10.0])

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

        # save each side of the picture
        elevation = [0, 90, -90]
        azimuth = [0, 90, -90, 180]
        # if the sides are really small, we don't need to output the sides
        # first 4 sides
        for i in range(len(azimuth)):
            elev = elevation[0]
            azim = azimuth[i]
            ax.view_init(elev=elev, azim=azim)
            # ax.dist = 6

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
            elev = elevation[i + 1]
            azim = azimuth[0]
            ax.view_init(elev=elev, azim=azim)
            # ax.dist = 6

            # name the title
            if elev == 90:
                title = 'Above'
            elif elev == -90:
                title = 'Below'
            plt.title(title)
            # save file
            plt.savefig('{}/From_{}_of_Bacteria.png'.format(picFolderEach, title), dpi=300, bbox_inches='tight')













    "/////////////////////////////////////////"

    # # create a folder to store all the images
    # global picFolder
    # if "picFolder" not in globals():
    #     # save the image
    #     if not os.path.exists("Image"):
    #         os.mkdir("Image")
    #
    #     picFolder = "Image/{}_{}".format(day, current_time)
    #     if not os.path.exists(picFolder):
    #         os.mkdir(picFolder)
    #
    # # separate the way to generate images into 2 cases
    # # if the surface is a film, we only need to see the top
    # if "film" in picName:
    #     # we will only look at the x-y plane
    #     array = array[0]
    #
    #     # locate where the positive, negative, and neutral charges are
    #     pos = np.where(array == 1)
    #     neu = np.where(array == 0)
    #     neg = np.where(array == -1)
    #
    #     # digits
    #     cL = -len(str(len(array[0]))) + 1
    #     cW = -len(str(len(array))) + 1
    #
    #     # dividor
    #     dividorL = int(round(len(array[0]), cL) / int(str(round(len(array[0]), cL))[0] + str(round(len(array[0]), cL))[1]))
    #     dividorW = int(round(len(array), cW) / int(str(round(len(array), cW))[0] + str(round(len(array), cW))[1]))
    #
    #     # calculate length and width of image
    #     img_length = len(array[0]) // dividorL
    #     img_width = len(array) // dividorW
    #
    #     # initialize the figure and subplots
    #     # fig = plt.figure(figsize=(img_length, img_width))
    #     fig = plt.figure()
    #     ax = fig.add_subplot(111)
    #     showMessage(f"Length of image is {img_length}, width of image is {img_width}")
    #
    #     # Calculate maximum
    #     max1 = [max(pos[i]) for i in range(len(pos)) if len(pos[i]) != 0]
    #     max2 = [max(neu[i]) for i in range(len(neu)) if len(neu[i]) != 0]
    #     max3 = [max(neg[i]) for i in range(len(neg)) if len(neg[i]) != 0]
    #     maximum = max(max1 + max2 + max3)
    #
    #     # initialize colors and labels
    #     colors = ['red', 'green', 'blue']
    #     labels = ["negative", "neutral", "positive"]
    #     levels = np.linspace(-2,2,5)
    #
    #     # remove colors and labels for charge that is not present
    #     # separate the cases into 3
    #     # if no negative is present
    #     if len(neg[0]) == 0:
    #         colors.remove('red')
    #         labels.remove('negative')
    #         levels = np.delete(levels, 1)
    #         showMessage('removed negative')
    #     # if no neutral is present
    #     if len(neu[0]) == 0:
    #         colors.remove('green')
    #         labels.remove('neutral')
    #         levels = np.delete(levels, 2)
    #         showMessage('removed neutral')
    #
    #     # if no positive is present
    #     if len(pos[0]) == 0:
    #         colors.remove('blue')
    #         labels.remove('positive')
    #         levels = np.delete(levels, 3)
    #         showMessage('removed positive')
    #
    #     # create the color map
    #     n_bins = len(colors)
    #     cmap_name = 'my_list'
    #     cmap = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)
    #
    #     ax.imshow(array, origin='lower', cmap=cmap)
    #
    #     for i in range(len(colors)):
    #         plt.plot(0, 0, ".", color=colors[i], label=labels[i])
    #
    #     ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.0))
    #
    #     # # x, y = np.indices((len(array[0]), len(array)))
    #     # surface = ax.contourf(array, levels=levels, colors=colors, vmin=-1, vmax=1, origin='lower')
    #     # # surface = ax.contourf(x, y, array, levels=levels, cmap=cmap, vmin=-1, vmax=1)
    #     #
    #     #
    #     # proxy = [plt.Rectangle((1, 1), 2, 2, fc=pc.get_facecolor()[0]) for pc in
    #     #          surface.collections]
    #     #
    #     # ax.legend(proxy, labels)
    #
    #     # set x limit and y limit
    #     ax.set_xlim(0, maximum)
    #     ax.set_ylim(0, maximum)
    #
    #     # set x and y labels
    #     ax.set_xlabel("X")
    #     ax.set_ylabel("Y")
    #
    #     # set label and tick position
    #     ax.xaxis.set_ticks_position('top')
    #     ax.xaxis.set_label_position('top')
    #
    #     plt.title("Above the film")
    #
    #     # save file
    #     plt.savefig('{}/{}'.format(picFolder, picName), dpi=300, bbox_inches='tight')
    #
    # elif "bacteria" in picName:
    #
    #     # make a subfolder containing the 6 sides of the surface
    #     global picFolderEach
    #     picFolderEach = "{}/{}".format(picFolder, picName)
    #     if not os.path.exists(picFolderEach):
    #         os.mkdir(picFolderEach)
    #
    #     # initialize the 6 sides
    #     # [z0,z1,y0,y1,x0,x1]
    #     title = ['Above','Below','Front','Behind','Left','Right']
    #     changer = [1,array.shape[0]-1,1,array.shape[1]-1,1,array.shape[2]-1]
    #     axesLabels = [['X','Y'], ['X','Y'], ['X','Z'], ['X','Z'], ['Y','Z'], ['Y','Z']]
    #     ind = [0,0,1,1,2,2]
    #
    #     # define original array
    #     originalArray = array
    #
    #     for i in range(len(title)):
    #         # initialize the range
    #         index = [int(originalArray.shape[0]),0,int(originalArray.shape[1]),0,int(originalArray.shape[2]),0]
    #         # change the array from 3d to 2d
    #         index[i] = changer[i]
    #         array = originalArray[index[1]:index[0],index[3]:index[2],index[5]:index[4]]
    #         if ind[i] == 0:
    #             array = array[0,:,:]
    #         elif ind[i] == 1:
    #             array = array[:,0,:]
    #         elif ind[i] == 2:
    #             array = array[:,:,0]
    #         showMessage(array.shape)
    #
    #         # locate where the positive, negative, and neutral charges are
    #         pos = np.where(array == 1)
    #         neu = np.where(array == 0)
    #         neg = np.where(array == -1)
    #
    #         # digits
    #         cL = -len(str(len(array[0]))) + 1
    #         cW = -len(str(len(array))) + 1
    #
    #         # dividor
    #         dividorL = math.ceil(round(len(array[0]), cL) / int(str(round(len(array[0]), cL))[0] + str(0)))
    #         dividorW = math.ceil(round(len(array), cW) / int(str(round(len(array), cW))[0] + str(0)))
    #
    #         # calculate length and width of image
    #         img_length = len(array[0]) // dividorL
    #         img_width = len(array) // dividorW
    #
    #         # initialize the figure and subplots
    #         # fig = plt.figure(figsize=(img_length, img_width))
    #         fig = plt.figure()
    #         ax = fig.add_subplot(111)
    #         showMessage(f"Length of image is {img_length}, width of image is {img_width}")
    #
    #         # Calculate maximum
    #         max1 = [max(pos[i]) for i in range(len(pos)) if len(pos[i]) != 0]
    #         max2 = [max(neu[i]) for i in range(len(neu)) if len(neu[i]) != 0]
    #         max3 = [max(neg[i]) for i in range(len(neg)) if len(neg[i]) != 0]
    #         maximum = max(max1 + max2 + max3)
    #
    #         # initialize colors and labels
    #         # colors = [(-1/maximum, 'red'), (0/maximum, 'green'), (1/maximum, 'blue')]
    #         colors = ['red', 'green', 'blue', 'white']
    #         labels = ["negative", "neutral", "positive", "spaces"]
    #         levels = np.linspace(-2, 3, 6)
    #
    #         # remove colors and labels for charge that is not present
    #         # separate the cases into 3
    #         # if no negative is present
    #         if len(neg[0]) == 0:
    #             # colors.remove((-1/maximum, 'red'))
    #             # labels.remove('negative')
    #             levels = np.delete(levels, 1)
    #             showMessage('removed negative')
    #
    #         # if no neutral is present
    #         if len(neu[0]) == 0:
    #             # colors.remove((0/maximum, 'green'))
    #             # labels.remove('neutral')
    #             levels = np.delete(levels, 2)
    #             showMessage('removed neutral')
    #
    #         # if no positive is present
    #         if len(pos[0]) == 0:
    #             # colors.remove((1/maximum, 'blue'))
    #             # labels.remove('positive')
    #             levels = np.delete(levels, 3)
    #             showMessage('removed positive')
    #
    #         # create the color map
    #         n_bins = len(colors)
    #         cmap_name = 'my_list'
    #         cmap = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)
    #
    #         ax.imshow(array, origin='lower', cmap=cmap)
    #
    #         for j in range(len(colors)):
    #             plt.plot(0, 0, ".", color=colors[j], label=labels[j])
    #
    #         ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.0))
    #
    #         # # x, y = np.indices((len(array[0]), len(array)))
    #         # surface = ax.contourf(array, levels=levels, colors=colors, vmin=-1, vmax=1, origin='lower')
    #         # # surface = ax.contourf(x, y, array, levels=levels, cmap=cmap, vmin=-1, vmax=1)
    #         #
    #         # proxy = [plt.Rectangle((1, 1), 2, 2, fc=pc.get_facecolor()[0]) for pc in
    #         #          surface.collections]
    #         #
    #         # ax.legend(proxy, labels)
    #
    #         # set x limit and y limit
    #         ax.set_xlim(0, maximum)
    #         ax.set_ylim(0, maximum)
    #
    #         # set x and y labels
    #         ax.set_xlabel(axesLabels[i][0])
    #         ax.set_ylabel(axesLabels[i][1])
    #
    #         # set label and tick position
    #         ax.xaxis.set_ticks_position('top')
    #         ax.xaxis.set_label_position('top')
    #
    #         plt.title(f"From {title[i]} of Bacteria")
    #
    #         plt.savefig('{}/From_{}_of_Bacteria.png'.format(picFolderEach, title[i]), dpi=300, bbox_inches='tight')
    #
    #     # plt.savefig('{}/Bacteria_from_each_side.png'.format(picFolderEach, title[i]), dpi=300, bbox_inches='tight')


    endTime = time.time()
    totalTime = endTime - startTime

    showMessage(f"Total time it took to generate image is {totalTime} seconds")
    showMessage("Image generate done")

# def _generateImage
