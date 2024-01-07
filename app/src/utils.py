#===============================================================================
# Brno University of Technology
# Faculty of Information Technology
# Academic year: 2018/2019
# Bachelor thesis: Monitoring Pedestrian by Drone
# Author: Vladimír Dušek
#===============================================================================

import math
import os
from enum import Enum

import cv2
from PyQt4.QtGui import QImage, QPixmap

# Smaller the parameter P is, thicker and bigger captions and borders are, according to a function y = sqrt(x/4P)
P = 0.5


class InputType(Enum):
    """
    Enum for type of input
    """
    VIDEO = 1
    IMAGE = 2


class OutputType(Enum):
    """
    Enum for type of output
    """
    PANORAMA = 1
    BORDERS = 2


class MessageBoxType(Enum):
    """
    Enum for type of PyQt Message Boxes
    """
    ERROR = 1
    WARNING = 2
    INFORMATION = 3


def npimg_to_pixmap(np_img):
    """
    Convert numpy array image to Qt pixmap image for visualization.
    :param np_img: numpy image
    :return: pixmap image
    """
    height, width, channel = np_img.shape
    bytes_per_line = 3 * width
    qimg = QImage(np_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimg)
    return pixmap


def create_folder(directory):
    """
    Create directory, ignore exceptions.
    :param directory: directory path and name
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        pass


def draw_caption(image, box, caption, size, thickness):
    """
    Draw caption of the detected object.
    :param image: where to draw
    :param box: coordinates
    :param caption: caption text
    :param size: font size
    :param thickness: font thickness
    """
    cv2.putText(image, caption, (box[0], box[1] - 10), cv2.FONT_HERSHEY_PLAIN, size, (0, 0, 0), int(thickness * 2.5))
    cv2.putText(image, caption, (box[0], box[1] - 10), cv2.FONT_HERSHEY_PLAIN, size, (255, 255, 255), thickness)


def get_thickness(x, y):
    """
    Get thickness of font or border considering picture resolution, according to function y = sqrt(x/4P).
    :param x: width of image
    :param y: height of image
    :return: thickness
    """
    z = (x * y + 100000) // 100000
    thickness = int(math.sqrt(z / (4 * P) + 1))
    return thickness
