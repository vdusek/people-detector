#===============================================================================
# Brno University of Technology
# Faculty of Information Technology
# Academic year: 2018/2019
# Bachelor thesis: Monitoring Pedestrian by Drone
# Author: Vladimír Dušek
#===============================================================================

import math
import sys
import cv2
from PIL import Image
from scipy.spatial import distance
from keras_retinanet.utils.visualization import draw_box
from describer import Describer
from utils import InputType, get_thickness, draw_caption, create_folder


# Object histogram comparison will be compute only for the objects which are closer to each other than this treshold
EUCLIDEAN_DISTANCE_TRESHOLD = 50

# If histogram distance between two objects is less than this treshold, it's considered as reidentified
HIST_SIMILARITY_TRESHOLD = 5

# If first and last seeing of the person is under this treshold, it's not considered as person
FIRST_AND_LAST_POINT_TRESHOLD = 20


class Matcher:
    """
    Class for processing detected people, identifying them and finnaly creating panorama map with their trajectories.
    """
    def __init__(self, image):
        """
        Store the image for drawing, create instance of histogram maker and create empty list for identified objects.
        :param image: image (RGB numpy array) where the trajectories are gonna be draw
        """
        self.describer = Describer(channels=[0, 1, 2], bins=[8, 8, 8], ranges=[0, 256, 0, 256, 0, 256])
        self.image = image
        self.known_objects = list()

    @staticmethod
    def compute_points_distance(p1, p2):
        """
        Compute the Euclidean distance between two points (x, y).
        :param p1: first point
        :param p2: second point
        :return: the distance
        """
        x1, y1 = p1
        x2, y2 = p2
        dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return dist

    def process_objects(self, frame, objects):
        """
        Process all objects from the frame. Compute their histograms and compare them.
        :param frame: number of processing frame
        :param objects: list of detected objects in the frame
        """
        for obj in objects:
            # If it's processing first frame, for all objects compute their histograms and store them
            if frame == 0:
                obj.compute_hist(self.describer)
                obj.detected_in_first_frame = True
                self.known_objects.append(obj)

            # Otherwise compare every object from the processing frame with all known objects
            else:
                # For every processing object compute its histogram
                obj.compute_hist(self.describer)
                most_similar_obj = None
                shortest_hist_distance = sys.maxsize

                # And compare it to every known object's histogram
                for known_obj in self.known_objects:
                    euclidean_distance = self.compute_points_distance(obj.points[0], known_obj.points[-1])

                    # If a distance in 2D space between them is less than the treshold, compare histograms
                    if euclidean_distance < EUCLIDEAN_DISTANCE_TRESHOLD:
                        # Computes the correlation between the two histograms
                        hist_distance = distance.correlation(obj.hist, known_obj.hist)

                        # Save the most similar known object in the region REAL_DISTANCE_TRESHOLD around object
                        if hist_distance < shortest_hist_distance:
                            shortest_hist_distance = hist_distance
                            most_similar_obj = known_obj

                # If shortest histogram distance is less than treshold, object is considered as reidentified
                if shortest_hist_distance < HIST_SIMILARITY_TRESHOLD:
                    most_similar_obj.compute_hist(self.describer, obj.cutout)
                    most_similar_obj.add_point(obj.points[0])

                # Else it's completely new object
                else:
                    self.known_objects.append(obj)

    @staticmethod
    def save_objects(path, frame, objects):
        """
        Save cutout objects to tmp/ directory.
        :param path: save objects to this path
        :param frame: what frame are the objects from
        :param objects: list of cutout objects (RGB numpy array)
        """
        full_path = path + str(frame) + '/'
        create_folder(full_path)
        cnt = 0
        for obj in objects:
            img = Image.fromarray(obj.cutout)
            img.save(full_path + 'obj-' + str(cnt) + '.png')
            cnt += 1

    def get_panorama(self, input_type):
        """
        Draw trajectories to the panorama map and return the image.
        :return: image with trajectories
        """
        # Print how many unique people were seen
        print("Detected pedestrians: " + str(len(self.known_objects)))

        # Create copy to draw in
        image = self.image.copy()
        x, y = image.shape[0], image.shape[1]
        thickness = get_thickness(x, y)
        person_cnt = 0

        # For every known object
        for obj in self.known_objects:

            if input_type == InputType.VIDEO:
                # Find out if object is moving, if not it's not considered as a person
                if self.compute_points_distance(obj.points[0], obj.points[-1]) < FIRST_AND_LAST_POINT_TRESHOLD:
                    continue

            person_cnt += 1

            if input_type == InputType.VIDEO:
                # If object was not detected in the first frame, its cutout will be inserted into the final panorama
                # image
                if not obj.detected_in_first_frame:
                    y_offset = obj.box[1]
                    x_offset = obj.box[0]
                    image[y_offset:y_offset+obj.cutout.shape[0], x_offset:x_offset+obj.cutout.shape[1]] = obj.cutout

            # Draw bounding box around person and its caption
            draw_box(image, obj.box, color=obj.color, thickness=thickness)
            caption = "Person %d" % person_cnt
            draw_caption(image, obj.box, caption, int(thickness * 0.75), int(thickness * 0.75))

            if input_type == InputType.VIDEO:
                # Draw trajectories, connect all objects seeing
                prev_point = obj.points.pop(0)
                for point in obj.points:
                    image = cv2.line(image, prev_point, point, obj.color, thickness=thickness)
                    prev_point = point

            if input_type == InputType.VIDEO:
                # Print how many unique moving people were seen
                print("Detected moving pedestrians: " + str(person_cnt))

        return image
