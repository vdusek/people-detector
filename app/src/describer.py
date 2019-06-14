#===============================================================================
# Brno University of Technology
# Faculty of Information Technology
# Academic year: 2018/2019
# Bachelor thesis: Monitoring Pedestrian by Drone
# Author: Vladimír Dušek
#===============================================================================

import cv2


class Describer:
    """
    Three-dimensional histogram in the RGB colorspace.
    """
    def __init__(self, channels, bins, ranges, mask=None):
        """
        Store the list of channel indexes, number of bins, ranges of possible pixel values and the mask
        the histogram will use.
        :param channels: list of indexes, where we specify the index of the channel we want to compute a histogram for
        :param bins: this is the number of bins we want to use when computing a histogram
        :param ranges: the range of possible pixel values
        :param mask: mask image
        """
        self.channels = channels
        self.bins = bins
        self.ranges = ranges
        self.mask = mask

    def describe(self, image):
        """
        Compute a 3D histogram in the RGB colorspace, then normalize the histogram so that images with the same content,
        but either scaled larger or smaller will have (roughly) the same histogram.
        :param image: image for computing histogram
        :return: 3D histogram as a flattened array
        """
        hist = cv2.calcHist([image], self.channels, self.mask, self.bins, self.ranges)
        hist = cv2.normalize(hist, hist)
        hist = hist.flatten()
        return hist
