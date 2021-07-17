"""
This file deal with the read/write from the text file
"""
import os
from datetime import datetime
from typing import Dict, IO
import logging

from PIL import Image
import numpy as np
from numpy import ndarray
from openpyxl.packaging import workbook
from matplotlib import pyplot as plt
import sys



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


def openLog() -> str:
    """
    This function open a log file
    """
    now = datetime.now()
    day = now.strftime("%m_%d")
    current_time = now.strftime("%H_%M_%S")

    if not os.path.exists("Log"):
        os.mkdir("Log")

    log_path = "Log/log_{}_{}.txt".format(day, current_time)

    global log
    log = open(log_path, "w")

    return log_path


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
    THis function based on the dimension of passed in ndarray to call appropriate function
    """
    # based on the dimension call different function to generate image
    dimension = len(array)
    if dimension == 2:
        _visPlot2D(array, picName)
    elif dimension == 3:
        pass
        # _visPlot3D(array, picName)
    else:
        raise RuntimeError("Unknown dimension of array pass in")

def _visPlot2D(array: ndarray, picName: str) -> None:
    """
    This function take in a 2D ndarray and save this array as a image with given name
    """
    showMessage("Start to generate image")

    pos = np.where(array == 1)
    neu = np.where(array == 0)
    neg = np.where(array == -1)

    pos_x = pos[0]
    pos_y = pos[1]
    neu_x = neu[0]
    neu_y = neu[1]
    neg_x = neg[0]
    neg_y = neg[1]

    if len(array[0]) > 1000:
        img_length = len(array[0]) // 100
        img_width = len(array) // 100
        size = 1
    elif len(array[0]) > 100:
        img_length = len(array[0]) // 10
        img_width = len(array) // 10
        size = 10
    else:
        img_length = len(array[0])
        img_width = len(array)
        size = 100

    fig = plt.figure(figsize=(img_length, img_width))
    ax = fig.add_subplot(111)

    ax.scatter(pos_x, pos_y, s=size, c='blue', label='pos')
    ax.scatter(neu_x, neu_y, s=size, c='green', label='neu')
    ax.scatter(neg_x, neg_y, s=size, c='red', label='neg')

    ax.legend(loc="upper right")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')

    plt.imshow(array, interpolation='nearest')

    now = datetime.now()
    day = now.strftime("%m_%d")
    current_time = now.strftime("%H_%M_%S")

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

    showMessage("Image generate done")

    # plt.show()


def _visPlot3D(array: ndarray, picName: str) -> None:
    """
    This function take in a 3D ndarray and save this array as a image with given name
    """
    showMessage("Start to generate image")

    now = datetime.now()
    day = now.strftime("%m_%d")
    current_time = now.strftime("%H_%M_%S")

    # build your visuals, that's all
    Scatter3D = scene.visuals.create_visual_node(visuals.MarkersVisual)

    # The real-things : plot using scene
    # build canvas
    canvas = scene.SceneCanvas(title="{}".format(picName),keys='interactive', show=True, bgcolor="white")
    view = canvas.central_widget.add_view()

    # for neutral
    neu = np.where(array == 0)
    neu_z = neu[0]
    neu_y = neu[1]
    neu_x = neu[2]

    n_neu = len(neu_z)
    c_neu = len(neu_z)
    position_neu = np.zeros((n_neu, 3))
    colors_neu = np.zeros((c_neu, 4))
    for i in range(n_neu):
        x = neu_x[i]
        y = neu_y[i]
        z = neu_z[i]
        position_neu[i] = x, y, z
        colors_neu[i] = (0, 1, 0, 0.8)

    # for positive
    pos = np.where(array == 1)
    pos_z = pos[0]
    pos_y = pos[1]
    pos_x = pos[2]

    n_pos = len(pos_z)
    c_pos = len(pos_z)
    position_pos = np.zeros((n_pos, 3))
    colors_pos = np.zeros((c_pos, 4))

    for i in range(n_pos):
        x = pos_x[i]
        y = pos_y[i]
        z = pos_z[i]
        position_pos[i] = x, y, z
        colors_pos[i] = (0, 0, 1, 0.8)

    # for negative
    neg = np.where(array == -1)
    neg_z = neg[0]
    neg_y = neg[1]
    neg_x = neg[2]

    n_neg = len(neg_z)
    c_neg = len(neg_z)

    position_neg = np.zeros((n_neg, 3))
    colors_neg = np.zeros((c_neg, 4))

    for i in range(n_neg):
        x = neg_x[i]
        y = neg_y[i]
        z = neg_z[i]
        position_neg[i] = x, y, z
        colors_neg[i] = (1, 0, 0, 0.8)

    # concatenate both color and position
    position = np.concatenate((position_neu, position_pos, position_neg))
    colors = np.concatenate((colors_neu, colors_pos, colors_neg))
    # plot ! note the parent parameter
    p1 = Scatter3D(parent=view.scene)
    p1.set_gl_state(blend=True, depth_test=True)
    p1.set_data(position, face_color=colors, symbol='o', size=20,edge_width=0.5,edge_color=colors)

    # Add a ViewBox to let the user zoom/rotate
    view.camera = 'turntable'
    view.camera.fov = 0
    view.camera.distance = int(array.shape[1])
    view.camera.center = (int(array.shape[2]/2), int(array.shape[1]/2), int(array.shape[0]/2))

    global picFolder
    if "picFolder" not in globals():
        # save the image
        if not os.path.exists("Image"):
            os.mkdir("Image")

        picFolder = "Image/{}_{}".format(day, current_time)
        if not os.path.exists(picFolder):
            os.mkdir(picFolder)

    global picFolderEach
    picFolderEach = "{}/{}".format(picFolder, picName)
    if not os.path.exists(picFolderEach):
        os.mkdir(picFolderEach)

    # if the surface is a film, we only need to see the top
    if "film" in picName:
        # set camera angle
        elevation = 90
        azimuth = 90
        view.camera.elevation = elevation
        view.camera.azimuth = azimuth
        image = canvas.render(bgcolor='white')[:, :, 0:3]

        # save file
        io.write_png('{}/Position_at_elevation={}_azimuth={}.png'.format(picFolderEach, elevation, azimuth), image)
    elif "bacteria" in picName:
        # save each side of the picture
        elevation = [0,90,-90]
        azimuth = [0,90,-90,180]
        # first 4 sides
        for i in range(len(azimuth)):
            view.camera.elevation = elevation[0]
            view.camera.azimuth = azimuth[i]
            image = canvas.render(bgcolor='white')[:, :, 0:3]

            # save file
            io.write_png('{}/Position_at_elevation={}_azimuth={}.png'.format(picFolderEach, elevation[0], azimuth[i]), image)

        # last 2 sides
        for i in range(len(elevation)-1):
            view.camera.elevation = elevation[i+1]
            view.camera.azimuth = azimuth[0]
            image = canvas.render(bgcolor='white')[:, :, 0:3]

            # save file
            io.write_png('{}/Position_at_elevation={}_azimuth={}.png'.format(picFolderEach, elevation[i+1], azimuth[0]),
                         image)
    showMessage("Image generate done")
