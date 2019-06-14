#===============================================================================
# Brno University of Technology
# Faculty of Information Technology
# Academic year: 2018/2019
# Bachelor thesis: Monitoring Pedestrian by Drone
# Author: Vladimír Dušek
#===============================================================================

import os
from utils import OutputType, InputType


class File:
    """
    Class for manipulation with input/output files.
    """
    def __init__(self, tmp_dir, full_path):
        """
        Initialization of class attributes.
        Name is the name of input file and extension its extension.
        Output type is type of the output (panorama image or video with borders).
        Input type is find out according to extension.
        :param tmp_dir: temporary directory for storing files
        :param full_path: full path to the input file
        """
        self.tmp_dir = tmp_dir
        self.full_path = full_path
        self.name = os.path.splitext(os.path.basename(os.path.normpath(full_path)))[0]
        self.extension = os.path.splitext(full_path)[1]
        self.output_type = None

        if self.extension in ['.jpg', '.jpeg', '.png', '.bmp']:
            self.type = InputType.IMAGE
        elif self.extension in ['.mp4', '.avi', '.wmv', '.mov', '.mkv']:
            self.type = InputType.VIDEO
        else:
            raise ValueError

    def get_output_type(self):
        """
        Get number of output type.
        :return: "1" for video with bounding boxes, "2" for panorama image
        """
        if self.output_type == OutputType.BORDERS:
            return str(1)
        elif self.output_type == OutputType.PANORAMA:
            return str(2)
        else:
            raise ValueError

    def get_output_name(self, output_type):
        """
        Get full name of the output file according to output type.
        :param output_type: type of the output
        :return: full path to the output file
        """
        self.output_type = output_type
        if output_type == OutputType.PANORAMA and self.type == InputType.VIDEO:
            return self.tmp_dir + self.name + '-processed-v' + self.get_output_type() + '.png'
        else:
            return self.tmp_dir + self.name + '-processed-v' + self.get_output_type() + self.extension

    def get_frame_name(self, output_type):
        """
        Get frame name according to output type.
        :param output_type: output type
        :return: frame name
        """
        self.output_type = output_type
        return self.name + '-processed-v' + self.get_output_type()

    def get_frame_dir(self, output_type):
        """
        Get name of the frame directory, sub-directory where processed frames're gonna be stored.
        :param output_type: output type
        :return: name of the frame directory
        """
        self.output_type = output_type
        return self.tmp_dir + self.name + '-processed-v' + self.get_output_type() + '-dir/'
