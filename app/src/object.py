#===============================================================================
# Brno University of Technology
# Faculty of Information Technology
# Academic year: 2018/2019
# Bachelor thesis: Monitoring Pedestrian by Drone
# Author: Vladimír Dušek
#===============================================================================

import random
from keras_retinanet.utils.colors import label_color


class Object:
    """
       Detected object representation.
    """
    def __init__(self, box, score, label):
        """
        Store object's attributes.
        :param box: coordinates of bounding box around object
        :param score: with which probability is object person
        :param label: label number
        """
        self.box = box
        self.score = score
        self.label = label
        self.points = [(int((box[2] + box[0]) / 2), int((box[3] + box[1]) / 2))]
        self.color = label_color(random.randint(1, 79))
        self.cutout = None
        self.hist = None
        self.detected_in_first_frame = False

    def add_cropped(self, cutout):
        """
        Add object's cutout.
        :param cutout: object's cutout
        """
        self.cutout = cutout

    def compute_hist(self, hist_maker, cutout=None):
        """
        Compute histogram for object's cutout
        :param hist_maker: HistogramMaker for computing the histogram
        :param cutout: object's cutout
        """
        if cutout is None:
            cutout = self.cutout
        self.hist = hist_maker.describe(cutout)

    def add_point(self, coordinates):
        """
        Add another seeing of the object.
        :param coordinates: middle of the object
        """
        self.points.append(coordinates)
