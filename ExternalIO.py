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
import time

from vispy import app, visuals, scene, gloo
from vispy.gloo.util import _screenshot
import vispy.io as io
import sys

LOG_CACH = []

# INDICATOR record three bool
# first is generate image or not, second is generate log or not, third is write log at last or not
INDICATOR = [False, False, False]

FRAGMENT_SHADER = """
    // Extensions for WebGL
    #extension GL_OES_standard_derivatives : enable
    #extension GL_OES_element_index_uint : enable
    #include "misc/spatial-filters.frag"
    // Adapted from glumpy with permission
    const float M_SQRT1_2 = 0.707106781186547524400844362104849039;
    uniform sampler2D u_font_atlas;
    uniform vec2 u_font_atlas_shape;
    varying vec4 v_color;
    uniform float u_npix;
    varying vec2 v_texcoord;
    const float center = 0.5;
    float contour(in float d, in float w)
    {
        return smoothstep(center - w, center + w, d);
    }
    float sample(sampler2D texture, vec2 uv, float w)
    {
        return contour(texture2D(texture, uv).r, w);
    }
    void main(void) {
        vec2 uv = v_texcoord.xy;
        vec4 rgb;
        // Use interpolation at high font sizes
        if(u_npix >= 50.0)
            rgb = CatRom(u_font_atlas, u_font_atlas_shape, uv);
        else
            rgb = texture2D(u_font_atlas, uv);
        float distance = rgb.r;
        // GLSL's fwidth = abs(dFdx(uv)) + abs(dFdy(uv))
        float width = 0.5 * fwidth(distance);  // sharpens a bit
        // Regular SDF
        float alpha = contour(distance, width);
        if (u_npix < 30.) {
            // Supersample, 4 extra points
            // Half of 1/sqrt2; you can play with this
            float dscale = 0.5 * M_SQRT1_2;
            vec2 duv = dscale * (dFdx(v_texcoord) + dFdy(v_texcoord));
            vec4 box = vec4(v_texcoord-duv, v_texcoord+duv);
            float asum = sample(u_font_atlas, box.xy, width)
                       + sample(u_font_atlas, box.zw, width)
                       + sample(u_font_atlas, box.xw, width)
                       + sample(u_font_atlas, box.zy, width);
            // weighted average, with 4 extra points having 0.5 weight
            // each, so 1 + 0.5*4 = 3 is the divisor
            alpha = (alpha + 0.5 * asum) / 3.0;
        }
        gl_FragColor = vec4(v_color.rgb, v_color.a * alpha);
    }
    """
VERTEX_SHADER = """
    attribute float a_rotation;  // rotation in rad
    attribute vec2 a_position; // in point units
    attribute vec2 a_texcoord;
    attribute vec3 a_pos;  // anchor position
    varying vec2 v_texcoord;
    varying vec4 v_color;
    void main(void) {
        // Eventually "rot" should be handled by SRTTransform or so...
        mat4 rot = mat4(cos(a_rotation), -sin(a_rotation), 0, 0,
                        sin(a_rotation), cos(a_rotation), 0, 0,
                        0, 0, 1, 0, 0, 0, 0, 1);
        vec4 pos = $transform(vec4(a_pos, 1.0)) +
                   vec4($text_scale(rot * vec4(a_position, 0.0, 1.0)).xyz, 0.0);
        gl_Position = pos;
        v_texcoord = a_texcoord;
        v_color = $color;
    }
    """

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

    # build your visuals, that's all
    Scatter3D = scene.visuals.create_visual_node(visuals.MarkersVisual)

    # The real-things : plot using scene
    # build canvas
    canvas = scene.SceneCanvas(title="{}".format(picName), keys='interactive', show=True, bgcolor="white", dpi=128)
    view = canvas.central_widget.add_view()

    # for neutral
    neu = np.where(array == 0)
    neu_y = neu[0]
    neu_x = neu[1]

    n_neu = len(neu_y)
    c_neu = len(neu_y)
    position_neu = np.zeros((n_neu, 2))
    colors_neu = np.zeros((c_neu, 4))
    for i in range(n_neu):
        # green
        x = neu_x[i]
        y = neu_y[i]
        position_neu[i] = x, y
        colors_neu[i] = (0, 1, 0, 0.8)

    # for positive
    pos = np.where(array == 1)
    pos_y = pos[0]
    pos_x = pos[1]

    n_pos = len(pos_y)
    c_pos = len(pos_y)
    position_pos = np.zeros((n_pos, 2))
    colors_pos = np.zeros((c_pos, 4))

    for i in range(n_pos):
        # blue
        x = pos_x[i]
        y = pos_y[i]
        position_pos[i] = x, y
        colors_pos[i] = (0, 0, 1, 0.8)

    # for negative
    neg = np.where(array == -1)
    neg_y = neg[0]
    neg_x = neg[1]

    n_neg = len(neg_y)
    c_neg = len(neg_y)

    position_neg = np.zeros((n_neg, 2))
    colors_neg = np.zeros((c_neg, 4))

    for i in range(n_neg):
        # red
        x = neg_x[i]
        y = neg_y[i]
        position_neg[i] = x, y
        colors_neg[i] = (1, 0, 0, 0.8)

    # concatenate both color and position
    position = np.concatenate((position_neu, position_pos, position_neg))
    colors = np.concatenate((colors_neu, colors_pos, colors_neg))
    # plot ! note the parent parameter
    p1 = Scatter3D(parent=view.scene)
    # p1 = scene.visuals.Markers(fcode=FRAGMENT_SHADER)
    p1.set_gl_state('opaque', blend=True, depth_test=False)

    if 'whole_film' in picName:
        size = 1
    else:
        size = 10

    p1.set_data(position, face_color=colors, symbol='o', size=size, edge_width=0.5, edge_color=colors)
    view.add(p1)

    # Add a ViewBox to let the user zoom/rotate
    view.camera = 'turntable'
    view.camera.fov = 45
    view.camera.distance = int(max(2*array.shape[1], 2*array.shape[0]))
    view.camera.center = (int(array.shape[1] / 2), int(array.shape[0] / 2))

    # plot XYZ axes
    # create a factor number that takes the size of the array and determines the size for font, and tick length
    factor = max(array.shape[0], array.shape[1])/10

    xax = scene.visuals.Axis(pos=[[0, 0], [int(array.shape[1]), 0]], domain=(0, int(array.shape[1])),
                             tick_direction=(0, -1), axis_color='black', tick_color='black', text_color='black',
                             font_size=128*factor, minor_tick_length=100*factor, major_tick_length=200*factor, axis_label='X axis',
                             axis_font_size=128*factor, tick_label_margin=300*factor, axis_label_margin=800*factor, parent=view.scene)
    yax = scene.visuals.Axis(pos=[[0, 0], [0, int(array.shape[0])]], domain=(0, int(array.shape[0])),
                             tick_direction=(-1, 0), axis_color='black', tick_color='black', text_color='black',
                             font_size=128*factor, minor_tick_length=100*factor, major_tick_length=200*factor, axis_label='Y axis',
                             axis_font_size=128*factor, tick_label_margin=300*factor, axis_label_margin=800*factor, parent=view.scene)

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
        # set camera angle
        elevation = 90
        azimuth = 0
        view.camera.elevation = elevation
        view.camera.azimuth = azimuth
        image = canvas.render(bgcolor='white')[:, :, 0:3]

        # save file
        io.write_png('{}/{}.png'.format(picFolder, picName), image)

    elif 'bacteria' in picName:
        # set title
        name = 'Surface of Bacteria'
        # txt = scene.visuals.Text(text=name, font_size=256*factor, pos=(int(array.shape[1]/2), int(3*array.shape[0]/2)),
        #                                                                parent=view.scene)
        # view.add(txt)

        # set camera angle
        elevation = 90
        azimuth = 0
        view.camera.elevation = elevation
        view.camera.azimuth = azimuth
        image = canvas.render(bgcolor='white')[:, :, 0:3]

        # save file
        io.write_png('{}/{}.png'.format(picFolder, picName), image)
    """
    run
    """
    # if sys.flags.interactive != 1:
    #     app.run()
    # fig.update_layout(title=name)
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

    # build your visuals, that's all
    Scatter3D = scene.visuals.create_visual_node(visuals.MarkersVisual)

    # The real-things : plot using scene
    # build canvas
    canvas = scene.SceneCanvas(title="{}".format(picName),keys='interactive', show=True, bgcolor="white", dpi=64)
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
        # green
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
        # blue
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
        # red
        x = neg_x[i]
        y = neg_y[i]
        z = neg_z[i]
        position_neg[i] = x, y, z
        colors_neg[i] = (1, 0, 0, 0.8)

    # concatenate both color and position
    position = np.concatenate((position_neu, position_pos, position_neg))
    colors = np.concatenate((colors_neu, colors_pos, colors_neg))
    # plot ! note the parent parameter
    # p1 = Scatter3D(parent=view.scene)
    p1 = scene.visuals.Markers()
    p1.set_gl_state('opaque', blend=True, depth_test=False)

    if 'whole_film' in picName:
        size = 1
    else:
        size = 10

    p1.set_data(position, face_color=colors, symbol='o', size=size,edge_width=0.5,edge_color=colors)
    view.add(p1)

    # Add a ViewBox to let the user zoom/rotate
    view.camera = 'turntable'
    view.camera.fov = 45
    view.camera.distance = int(max(2*array.shape[2], 2*array.shape[1], 2*array.shape[0]))
    view.camera.center = (int(array.shape[2]/2), int(array.shape[1]/2), int(array.shape[0]/2))

    # plot XYZ axes
    # create a factor number that takes the size of the array and determines the size for font, and tick length
    factor = max(array.shape[0], array.shape[1], array.shape[2]) / 10

    xax = scene.visuals.Axis(pos=[[0, 0], [int(array.shape[2]), 0]], domain=(0, int(array.shape[1])),
                             tick_direction=(0, -1), axis_color='black', tick_color='black', text_color='black',
                             font_size=128 * factor, minor_tick_length=100 * factor, major_tick_length=200 * factor,
                             axis_label='X axis', axis_font_size=128 * factor, tick_label_margin=300 * factor,
                             axis_label_margin=800 * factor, parent=view.scene)
    yax = scene.visuals.Axis(pos=[[0, 0], [0, int(array.shape[1])]], domain=(0, int(array.shape[0])),
                             tick_direction=(-1, 0), axis_color='black', tick_color='black', text_color='black',
                             font_size=128 * factor, minor_tick_length=100 * factor, major_tick_length=200 * factor,
                             axis_label='Y axis', axis_font_size=128 * factor, tick_label_margin=300 * factor,
                             axis_label_margin=800 * factor, parent=view.scene)
    zax = scene.visuals.Axis(pos=[[0, 0], [-int(array.shape[0]), 0]], domain=(0, int(array.shape[0])),
                             tick_direction=(0, -1), axis_color='black', tick_color='black', text_color='black',
                             font_size=128 * factor, minor_tick_length=100 * factor, major_tick_length=200 * factor,
                             axis_label='Z axis', axis_font_size=128 * factor, tick_label_margin=300 * factor,
                             axis_label_margin=800 * factor, parent=view.scene)
    zax.transform = scene.transforms.MatrixTransform()  # its acutally an inverted xaxis
    zax.transform.rotate(90, (0, 1, 0))  # rotate cw around yaxis
    zax.transform.rotate(-45, (0, 0, 1))  # tick direction towards (-1,-1)

    view.add(xax)
    view.add(yax)
    view.add(zax)

    # create shader
    shader = gloo.program.Program(vert=VERTEX_SHADER, frag=FRAGMENT_SHADER)


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
        azimuth = 0
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

    endTime = time.time()
    totalTime = endTime - startTime

    showMessage(f"Total time it took to generate image is {totalTime} seconds")
    showMessage("Image generate done")
