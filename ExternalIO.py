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
import matplotlib as mpl
# mpl.use('TkAgg')
import sys
from vispy import app, visuals, scene
import vispy.io as io
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import time

log_cache = []


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


def openLog(write_at_last: bool) -> str:
    """
    This function open a log file
    """
    now = datetime.now()
    day = now.strftime("%m_%d")
    current_time = now.strftime("%H_%M_%S")

    if not os.path.exists("Log"):
        os.mkdir("Log")

    log_name = "Log/log_{}_{}.txt".format(day, current_time)

    global log
    log = open(log_name, "w")

    if write_at_last:
        global write_last
        write_last = True

    return log_name


def closeLog() -> None:
    """
    This function close the log file
    """
    showMessage("Start to close log")
    startTime = time.time()
    if "write_last" in globals():
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        info = "Time: {}, {}\n".format(current_time, "Write log at last, start to write it")
        log.write(info)

        for i in log_cache:
            log.write(i)

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        info = "Time: {}, {}\n".format(current_time, "Write log at last done")
        log.write(info)

        endTime = time.time()
        totalTime = endTime - startTime

        showMessage(f"Total time it took to write log is {totalTime} seconds")

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

    info = "Time: {}, {}\n".format(current_time, message)

    # depends on the requirement, write log now or later
    if "write_last" not in globals():
        log.write(info)
    else:
        log_cache.append(info)


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


    # initialize the pandas dataframe
    column_names = ['X', 'Y', 'Legend']
    df = pd.DataFrame(columns=column_names)

    pos = np.where(array == 1)
    neu = np.where(array == 0)
    neg = np.where(array == -1)

    pos_x = pos[0]
    pos_y = pos[1]
    neu_x = neu[0]
    neu_y = neu[1]
    neg_x = neg[0]
    neg_y = neg[1]

    position_x = np.concatenate((pos_x, neu_x, neg_x))
    position_y = np.concatenate((pos_y, neu_y, neg_y))

    colors_pos = np.repeat(np.array(['Positive']), len(pos_x), axis=0)
    colors_neu = np.repeat(np.array(['Neutral']), len(neu_x), axis=0)
    colors_neg = np.repeat(np.array(['Negative']), len(neg_x), axis=0)
    colors = np.concatenate((colors_pos, colors_neu, colors_neg))

    # add list to pandas dataframe
    df['X'] = position_x.tolist()
    df['Y'] = position_y.tolist()
    df['Legend'] = colors.tolist()

    # show it on plotly
    fig = go.Figure(data=px.scatter(df, x='X', y='Y', color='Legend', color_discrete_map={'Positive': 'blue',
                                                                                          'Neutral': 'green',
                                                                                          'Negative': 'red'}))

    # if len(array[0]) > 1000:
    #     img_length = len(array[0]) // 100
    #     img_width = len(array) // 100
    #     size = 1
    # elif len(array[0]) > 100:
    #     img_length = len(array[0]) // 10
    #     img_width = len(array) // 10
    #     size = 10
    # else:
    #     img_length = len(array[0])
    #     img_width = len(array)
    #     size = 100

    # fig = plt.figure(figsize=(img_length, img_width))
    # fig = plt.figure()
    # ax = fig.add_subplot(111)

    # ax.scatter(pos_x, pos_y, s=size, c='blue', label='pos')
    # ax.scatter(neu_x, neu_y, s=size, c='green', label='neu')
    # ax.scatter(neg_x, neg_y, s=size, c='red', label='neg')


    #
    # ax.scatter(pos_x, pos_y, c='blue', label='pos')
    # ax.scatter(neu_x, neu_y, c='green', label='neu')
    # ax.scatter(neg_x, neg_y, c='red', label='neg')
    #
    # ax.legend(loc="upper right")
    # ax.set_xlabel("X")
    # ax.set_ylabel("Y")
    # ax.xaxis.set_ticks_position('top')
    # ax.xaxis.set_label_position('top')
    #
    # # set x limit and y limit
    # max1 = [max(pos[i]) for i in range(len(pos)) if len(pos[i]) != 0]
    # max2 = [max(neu[i]) for i in range(len(neu)) if len(neu[i]) != 0]
    # max3 = [max(neg[i]) for i in range(len(neg)) if len(neg[i]) != 0]
    # maximum = max(max1 + max2 + max3)
    #
    # plt.xlim(0,maximum)
    # plt.ylim(0,maximum)
    #
    # plt.imshow(array, interpolation='nearest')

    global picFolder
    if "picFolder" not in globals():
        # save the image
        if not os.path.exists("Image"):
            os.mkdir("Image")

        picFolder = "Image/{}_{}".format(day, current_time)
        if not os.path.exists(picFolder):
            os.mkdir(picFolder)

    picPath = "{}/{}".format(picFolder, picName)
    if 'film' in picName:
        # set title
        name = "Surface of Film"

    elif 'bacteria' in picName:
        # set title
        name = 'Surface of Bacteria'

    # set camera angle
    fig.update_layout(title=name)

    # save file
    # fig.write_html('{}/{}.html'.format(picFolder, picName), full_html=False)
    fig.write_image('{}/{}.png'.format(picFolder, picName))
    # plt.savefig(picPath, dpi=300, bbox_inches='tight')

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

    # initialize the pandas dataframe
    column_names = ['X','Y','Z','Legend']
    df = pd.DataFrame(columns=column_names)

    # position of positive
    pos = np.where(array == 1)
    pos_z = pos[0]
    pos_y = pos[1]
    pos_x = pos[2]
    # color of positive
    colors_pos = np.repeat(np.array(['Positive']),len(pos_z),axis=0)
    # colors_pos = np.repeat(np.array([[0,0,1,0.8]]),len(pos_z),axis=0)

    # position of neutral
    neu = np.where(array == 0)
    neu_z = neu[0]
    neu_y = neu[1]
    neu_x = neu[2]
    colors_neu = np.repeat(np.array(['Neutral']),len(neu_z),axis=0)
    # colors_neu = np.repeat(np.array([[0,1,0,0.8]]),len(neu_z),axis=0)

    # position of negative
    neg = np.where(array == -1)
    neg_z = neg[0]
    neg_y = neg[1]
    neg_x = neg[2]
    colors_neg = np.repeat(np.array(['Negative']),len(neg_z),axis=0)

    position_x = np.concatenate((pos_x, neu_x, neg_x))
    position_y = np.concatenate((pos_y, neu_y, neg_y))
    position_z = np.concatenate((pos_z, neu_z, neg_z))
    colors = np.concatenate((colors_pos, colors_neu, colors_neg))

    # add list to pandas dataframe
    df['X'] = position_x.tolist()
    df['Y'] = position_y.tolist()
    df['Z'] = position_z.tolist()
    df['Legend'] = colors.tolist()

    # show it on plotly
    fig = go.Figure(data=px.scatter_3d(df, x='X', y='Y', z='Z', color='Legend', color_discrete_map={'Positive': 'blue',
                                                                                                    'Neutral': 'green',
                                                                                                    'Negative': 'red'}))

    # create a folder to store all the images]
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
        name = "Surface of Film"
        camera = dict(eye=dict(x=0, y=0, z=1.5))
        fig.update_layout(scene_camera=camera, title=name)

        # save file
        # fig.write_html('{}/{}.html'.format(picFolder, picName),full_html=False)
        fig.write_image('{}/{}.png'.format(picFolder, picName))

    elif "bacteria" in picName:
        # create folder for bacteria
        global picFolderEach
        picFolderEach = "{}/{}".format(picFolder, picName)
        if not os.path.exists(picFolderEach):
            os.mkdir(picFolderEach)

        # set camera angle for each side of bacteria
        name = ['X-Y plane','X-Z plane','Y-Z plane']
        x = [0,0,2.5]
        y = [0,2.5,0]
        z = [2.5,0,0]
        for i in range(3):
            # set camera angle
            camera = dict(eye=dict(x=x[i], y=y[i], z=z[i]))
            fig.update_layout(scene_camera=camera, title=name[i])
            # save file
            fig.write_image('{}/Position_at_{}.png'.format(picFolderEach, name[i]))

        # name = "Surface of Bacteria"
        # camera = dict(eye=dict(x=0, y=0, z=1.5))
        # fig.update_layout(scene_camera=camera, title=name)

        # save file
        # fig.write_image('{}/{}.png'.format(picFolderEach, picName),full_html=False)

        # global picFolderEach
        # picFolderEach = "{}/{}".format(picFolder, picName)
        # if not os.path.exists(picFolderEach):
        #     os.mkdir(picFolderEach)

        # name = ['X-Y plane','X-Z plane','Y-Z plane']
        # x = [0,0,2.5]
        # y = [0,2.5,0]
        # z = [2.5,0,0]
        # for i in range(3):
        #     # set camera angle
        #     camera = dict(eye=dict(x=x[i], y=y[i], z=z[i]))
        #     fig.update_layout(scene_camera=camera, title=name[i])
        #     # save file
        #     fig.write_image('{}/Position_at_{}.png'.format(picFolderEach, name[i]))


        # # save each side of the picture
        # elevation = [0, 90, -90]
        # azimuth = [0, 90, -90, 180]
        # # if the sides are really small, we don't need to output the sides
        # # first 4 sides
        # for i in range(len(azimuth)):
        #
        #
        #     # name the title
        #     if azim == 90 or azim == -90:
        #         plt.title('X-Z plane')
        #     elif azim == 0 or azim == 180:
        #         plt.title('Y-Z plane')
        #
        #     # save file
        #     plt.savefig('{}/Position_at_elevation={}_azimuth={}.png'.format(picFolderEach, elevation[0], azimuth[i]))
        #
        # # last 2 sides
        # for i in range(len(elevation) - 1):
        #     elev = elevation[i + 1]
        #     azim = azimuth[0]
        #     ax.view_init(elev=elev, azim=azim)
        #     ax.dist = 6
        #
        #     # name the title
        #     plt.title('X-Y plane')
        #
        #     # save file
        #     plt.savefig('{}/Position_at_elevation={}_azimuth={}.png'.format(picFolderEach, elevation[i + 1], azimuth[0]))

    # # graph the 3D visualization
    # # if the array is small, we don't
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    #
    # # position of positive
    # pos = np.where(array == 1)
    # pos_z = pos[0]
    # pos_y = pos[1]
    # pos_x = pos[2]
    # # color of positive
    # # colors_pos = np.repeat(np.array([[0,0,1,0.8]]),len(pos_z),axis=0)
    # ax.scatter3D(pos_x, pos_y, pos_z, marker="o", label='positive', color='blue', depthshade=False)
    #
    # # position of neutral
    # neu = np.where(array == 0)
    # neu_z = neu[0]
    # neu_y = neu[1]
    # neu_x = neu[2]
    # # colors_neu = np.repeat(np.array([[0,1,0,0.8]]),len(neu_z),axis=0)
    # ax.scatter3D(neu_x, neu_y, neu_z, marker="o", label='neutral', color='green', depthshade=False)
    #
    # # position of negative
    # neg = np.where(array == -1)
    # neg_z = neg[0]
    # neg_y = neg[1]
    # neg_x = neg[2]
    # # colors_neg = np.repeat(np.array([[1,0,0,0.8]]),len(neg_z),axis=0)
    # ax.scatter3D(neg_x, neg_y, neg_z, marker="o", label='negative', color='red', depthshade=False)
    #
    # # position_x = np.concatenate((pos_x, neu_x, neg_x))
    # # position_y = np.concatenate((pos_y, neu_y, neg_y))
    # # position_z = np.concatenate((pos_z, neu_z, neg_z))
    # # colors = np.concatenate((colors_pos, colors_neu, colors_neg))
    # # ax.scatter3D(position_x, position_y, position_z, marker="o", label=['neutral','positive','negative'], color=colors, depthshade=False)
    #
    # ax.legend(loc="upper right")
    # ax.set_xlabel("X")
    # ax.set_ylabel("Y")
    # ax.set_zlabel("Z")
    #
    # # set axis limit
    #
    # # get the largest number in all x,y,z scales
    # max1 = [max(pos[i]) for i in range(len(pos)) if len(pos[i])!=0]
    # max2 = [max(neu[i]) for i in range(len(neu)) if len(neu[i])!=0]
    # max3 = [max(neg[i]) for i in range(len(neg)) if len(neg[i])!=0]
    # maximum = max(max1+max2+max3)
    # ax.set_xlim3d(0, maximum)
    # ax.set_ylim3d(0, maximum)
    # ax.set_zlim3d(0, maximum)
    #
    # # create a folder to store all the images]
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
    # global picFolderEach
    # picFolderEach = "{}/{}".format(picFolder, picName)
    # if not os.path.exists(picFolderEach):
    #     os.mkdir(picFolderEach)
    #
    # # if the surface is a film, we only need to see the top
    # if "film" in picName:
    #     # set camera angle
    #     elev = 90
    #     azim = 0
    #     ax.view_init(elev=elev, azim=azim)
    #     ax.dist = 7
    #     plt.title("X-Y plane")
    #
    #     # save file
    #     plt.savefig('{}/Position_at_elevation={}_azimuth={}.png'.format(picFolderEach, elev, azim))
    # elif "bacteria" in picName:
    #     # save each side of the picture
    #     elevation = [0, 90, -90]
    #     azimuth = [0, 90, -90, 180]
    #     # if the sides are really small, we don't need to output the sides
    #     # first 4 sides
    #     for i in range(len(azimuth)):
    #         elev = elevation[0]
    #         azim = azimuth[i]
    #         ax.view_init(elev=elev, azim=azim)
    #         ax.dist = 6
    #
    #         # name the title
    #         if azim == 90 or azim == -90:
    #             plt.title('X-Z plane')
    #         elif azim == 0 or azim == 180:
    #             plt.title('Y-Z plane')
    #
    #         # save file
    #         plt.savefig('{}/Position_at_elevation={}_azimuth={}.png'.format(picFolderEach, elevation[0], azimuth[i]))
    #
    #     # last 2 sides
    #     for i in range(len(elevation) - 1):
    #         elev = elevation[i + 1]
    #         azim = azimuth[0]
    #         ax.view_init(elev=elev, azim=azim)
    #         ax.dist = 6
    #
    #         # name the title
    #         plt.title('X-Y plane')
    #
    #         # save file
    #         plt.savefig('{}/Position_at_elevation={}_azimuth={}.png'.format(picFolderEach, elevation[i + 1], azimuth[0]))
    # plt.show()
    # # build your visuals, that's all
    # Scatter3D = scene.visuals.create_visual_node(visuals.MarkersVisual)
    #
    # # The real-things : plot using scene
    # # build canvas
    # canvas = scene.SceneCanvas(title="{}".format(picName),keys='interactive', show=True, bgcolor="white")
    # view = canvas.central_widget.add_view()
    #
    # # for neutral
    # neu = np.where(array == 0)
    # neu_z = neu[0]
    # neu_y = neu[1]
    # neu_x = neu[2]
    #
    # n_neu = len(neu_z)
    # c_neu = len(neu_z)
    # position_neu = np.zeros((n_neu, 3))
    # colors_neu = np.zeros((c_neu, 4))
    # for i in range(n_neu):
    #     # green
    #     x = neu_x[i]
    #     y = neu_y[i]
    #     z = neu_z[i]
    #     position_neu[i] = x, y, z
    #     colors_neu[i] = (0, 1, 0, 0.8)
    #
    # # for positive
    # pos = np.where(array == 1)
    # pos_z = pos[0]
    # pos_y = pos[1]
    # pos_x = pos[2]
    #
    # n_pos = len(pos_z)
    # c_pos = len(pos_z)
    # position_pos = np.zeros((n_pos, 3))
    # colors_pos = np.zeros((c_pos, 4))
    #
    # for i in range(n_pos):
    #     # blue
    #     x = pos_x[i]
    #     y = pos_y[i]
    #     z = pos_z[i]
    #     position_pos[i] = x, y, z
    #     colors_pos[i] = (0, 0, 1, 0.8)
    #
    # # for negative
    # neg = np.where(array == -1)
    # neg_z = neg[0]
    # neg_y = neg[1]
    # neg_x = neg[2]
    #
    # n_neg = len(neg_z)
    # c_neg = len(neg_z)
    #
    # position_neg = np.zeros((n_neg, 3))
    # colors_neg = np.zeros((c_neg, 4))
    #
    # for i in range(n_neg):
    #     # red
    #     x = neg_x[i]
    #     y = neg_y[i]
    #     z = neg_z[i]
    #     position_neg[i] = x, y, z
    #     colors_neg[i] = (1, 0, 0, 0.8)
    #
    # # concatenate both color and position
    # position = np.concatenate((position_neu, position_pos, position_neg))
    # colors = np.concatenate((colors_neu, colors_pos, colors_neg))
    # # plot ! note the parent parameter
    # p1 = Scatter3D(parent=view.scene)
    # p1.set_gl_state(blend=True, depth_test=True)
    # p1.set_data(position, face_color=colors, symbol='o', size=20,edge_width=0.5,edge_color=colors)
    #
    # # Add a ViewBox to let the user zoom/rotate
    # view.camera = 'turntable'
    # view.camera.fov = 0
    # view.camera.distance = int(array.shape[1])
    # view.camera.center = (int(array.shape[2]/2), int(array.shape[1]/2), int(array.shape[0]/2))
    #
    # # run
    # elevation = 90
    # azimuth = 90
    # view.camera.elevation = elevation
    # view.camera.azimuth = azimuth
    # if sys.flags.interactive != 1:
    #     app.run()
    #
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
    # global picFolderEach
    # picFolderEach = "{}/{}".format(picFolder, picName)
    # if not os.path.exists(picFolderEach):
    #     os.mkdir(picFolderEach)
    #
    # # if the surface is a film, we only need to see the top
    # if "film" in picName:
    #     # set camera angle
    #     elevation = 90
    #     azimuth = 90
    #     view.camera.elevation = elevation
    #     view.camera.azimuth = azimuth
    #     image = canvas.render(bgcolor='white')[:, :, 0:3]
    #
    #     # save file
    #     io.write_png('{}/Position_at_elevation={}_azimuth={}.png'.format(picFolderEach, elevation, azimuth), image)
    # elif "bacteria" in picName:
    #     # save each side of the picture
    #     elevation = [0,90,-90]
    #     azimuth = [0,90,-90,180]
    #     # first 4 sides
    #     for i in range(len(azimuth)):
    #         view.camera.elevation = elevation[0]
    #         view.camera.azimuth = azimuth[i]
    #         image = canvas.render(bgcolor='white')[:, :, 0:3]
    #
    #         # save file
    #         io.write_png('{}/Position_at_elevation={}_azimuth={}.png'.format(picFolderEach, elevation[0], azimuth[i]), image)
    #
    #     # last 2 sides
    #     for i in range(len(elevation)-1):
    #         view.camera.elevation = elevation[i+1]
    #         view.camera.azimuth = azimuth[0]
    #         image = canvas.render(bgcolor='white')[:, :, 0:3]
    #
    #         # save file
    #         io.write_png('{}/Position_at_elevation={}_azimuth={}.png'.format(picFolderEach, elevation[i+1], azimuth[0]),
    #                      image)

    endTime = time.time()
    totalTime = endTime - startTime

    showMessage(f"Total time it took to generate image is {totalTime} seconds")
    showMessage("Image generate done")
