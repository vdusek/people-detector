# ===============================================================================
# Brno University of Technology
# Faculty of Information Technology
# Academic year: 2018/2019
# Bachelor thesis: Monitoring Pedestrian by Drone
# Author: Vladimír Dušek
# ===============================================================================

import time

import cv2
import keras
import numpy as np
import tensorflow as tf
from keras_retinanet import models
from keras_retinanet.utils.colors import label_color
from keras_retinanet.utils.image import preprocess_image, read_image_bgr, resize_image
from keras_retinanet.utils.visualization import draw_box
from PIL import Image

from matcher import Matcher
from object import Object
from utils import InputType, OutputType, create_folder, draw_caption, get_thickness, npimg_to_pixmap

# Path to the Retinanet trained model. If you want to use your own model, change the path.
MODEL_PATH = "../models/resnet50_csv_40-converted.h5"

# Treshold for succesful detection (if detection's score is above the treshold, object is considered as detected)
DETECTION_TRESHOLD = 0.5


class Detector:
    """
    Class for operations with detection network RetinaNet.
    """

    def __init__(self):
        """
        Initialization of Tensorflow session and Retinanet model.
        """
        session = self.get_session()
        keras.backend.tensorflow_backend.set_session(session)
        self.model = models.load_model(MODEL_PATH, backbone_name="resnet50")
        # load label to names mapping for visualization purposes
        self.labels_to_names = {
            0: "person",
            1: "bicycle",
            2: "car",
            3: "motorcycle",
            4: "airplane",
            5: "bus",
            6: "train",
            7: "truck",
            8: "boat",
            9: "traffic light",
            10: "fire hydrant",
            11: "stop sign",
            12: "parking meter",
            13: "bench",
            14: "bird",
            15: "cat",
            16: "dog",
            17: "horse",
            18: "sheep",
            19: "cow",
            20: "elephant",
            21: "bear",
            22: "zebra",
            23: "giraffe",
            24: "backpack",
            25: "umbrella",
            26: "handbag",
            27: "tie",
            28: "suitcase",
            29: "frisbee",
            30: "skis",
            31: "snowboard",
            32: "sports ball",
            33: "kite",
            34: "baseball bat",
            35: "baseball glove",
            36: "skateboard",
            37: "surfboard",
            38: "tennis racket",
            39: "bottle",
            40: "wine glass",
            41: "cup",
            42: "fork",
            43: "knife",
            44: "spoon",
            45: "bowl",
            46: "banana",
            47: "apple",
            48: "sandwich",
            49: "orange",
            50: "broccoli",
            51: "carrot",
            52: "hot dog",
            53: "pizza",
            54: "donut",
            55: "cake",
            56: "chair",
            57: "couch",
            58: "potted plant",
            59: "bed",
            60: "dining table",
            61: "toilet",
            62: "tv",
            63: "laptop",
            64: "mouse",
            65: "remote",
            66: "keyboard",
            67: "cell phone",
            68: "microwave",
            69: "oven",
            70: "toaster",
            71: "sink",
            72: "refrigerator",
            73: "book",
            74: "clock",
            75: "vase",
            76: "scissors",
            77: "teddy bear",
            78: "hair drier",
            79: "toothbrush",
        }

    @staticmethod
    def get_session():
        """
        Get session with allow growth of GPU.
        :return: Tensorflow session
        """
        config = tf.ConfigProto()

        # Dynamically grow the memory used on the GPU
        config.gpu_options.allow_growth = True

        # To log device placement (on which device the operation ran)
        config.log_device_placement = True

        session = tf.Session(config=config)
        return session

    @staticmethod
    def crop_objects(image, objects):
        """
        Crop the objects in the image.
        :param image: the input image (BGR)
        :param objects: the list of the objects to be cropped
        :return: the list of the cropped objects
        """
        # Define list of cropped objects
        objects_cropped = []

        # Convert image to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # For every object compute its cropped part and add it to the list
        for obj in objects:
            box = obj.box
            cropped = image[box[1] : box[3], box[0] : box[2]].copy()
            obj.add_cropped(cropped)
            objects_cropped.append(obj)

        return objects_cropped

    @staticmethod
    def draw_bounding_boxes(image, objects):
        """
        Draw the bounding boxes around the objects in the image.
        :param image: the input image (BGR)
        :param objects: the list of the objects
        :return: the image with the bounding boxes around the objects
        """
        # Get thickness of border lines, font and font size
        x, y = image.shape[0], image.shape[1]
        thickness = get_thickness(x, y)

        # Copy to draw on
        image_draw = image.copy()
        image_draw = cv2.cvtColor(image_draw, cv2.COLOR_BGR2RGB)

        # For every object draw the bounding box and the caption
        for obj in objects:
            box = obj.box
            score = obj.score
            label = obj.label
            color = label_color(label)
            draw_box(image_draw, box, color=color, thickness=thickness)
            caption = "%.1f%%" % (score * 100)
            # For detection various types of objects can be use following caption
            # caption = "%s: %.1f%%" % (self.labels_to_names[label], score * 100)
            draw_caption(image_draw, box, caption, int(thickness * 0.75), int(thickness * 0.75))

        return image_draw

    def detect_objects(self, image):
        """
        Detect the objects in the image.
        :param image: the input image
        :return: the list of detected objects
        """
        # List of the detected objects
        objects_detected = []

        # Preprocess image for network
        image = preprocess_image(image)
        image, scale = resize_image(image)

        # Process image
        start = time.time()
        boxes, scores, labels = self.model.predict_on_batch(np.expand_dims(image, axis=0))
        print("Processing time: ", time.time() - start)

        # Correct for image scale
        boxes /= scale

        # Add detected objects to the list
        for box, score, label in zip(boxes[0], scores[0], labels[0]):
            if score < DETECTION_TRESHOLD:
                continue
            box = box.astype(int)
            objects_detected.append(Object(box, score, label))

        return objects_detected

    def process_image(self, window, file, output_type):
        """
        Process input image.
        :param window: PyQt window
        :param file: the name of the input file
        :param output_type: the type of the output
        :return: the name of the output file
        """
        image = read_image_bgr(file.full_path)
        objects_detected = self.detect_objects(image)
        output_name = file.get_output_name(output_type)

        if output_type == OutputType.BORDERS:
            output_image = self.draw_bounding_boxes(image, objects_detected)

        elif output_type == OutputType.PANORAMA:
            objects_cropped = self.crop_objects(image, objects_detected)
            matcher = Matcher(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            matcher.process_objects(0, objects_cropped)
            matcher.save_objects(output_name.split(".")[0] + "-dir/", 0, objects_cropped)
            output_image = matcher.get_panorama(InputType.IMAGE)
        else:
            raise ValueError

        # Save output image to tmp/
        image = Image.fromarray(output_image)
        image.save(output_name)

        # Visualize output image
        window.actualize_output_label(npimg_to_pixmap(output_image))

        return output_name

    def process_video(self, window, file, output_type):
        """
        Process input video.
        :param window: PyQt window
        :param file: the name of the input file
        :param output_type: the type of the output
        :return: the name of the output file
        """
        # Read input video capture
        in_cap = cv2.VideoCapture(file.full_path)

        # Extract video info (fps, number of frames, resolution)
        fps = int(in_cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(in_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        resolution = (int(in_cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(in_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        output_name = file.get_output_name(output_type)

        # If output is video capture of frames with object boundaries
        if output_type == OutputType.BORDERS:
            # Create output video capture for writing frames
            out_cap = cv2.VideoWriter(output_name, cv2.VideoWriter_fourcc(*"XVID"), fps, resolution)

        # If output is a panorama image with trajectories of objects
        elif output_type == OutputType.PANORAMA:
            # First frame of input video is gonna be used for drawing trajectories
            ret, image = cv2.VideoCapture(file.full_path).read()
            if not ret:
                raise ValueError
            matcher = Matcher(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        else:
            raise ValueError

        # Calculate number of steps for progress bar
        step = 100 / frame_count
        frame_cnt = 0
        completed = 0

        # Create temporary directory for saving processed frames with boundaries
        tmp_frame_dir = file.get_frame_dir(output_type)
        create_folder(tmp_frame_dir)

        # Loop for reading whole video frame by frame
        while in_cap.isOpened():
            # Read single frame
            ret, image = in_cap.read()
            if not ret:
                break

            # Visualize input frame which is gonna be processed
            window.actualize_input_label(npimg_to_pixmap(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)))

            # Detect objects in input frame
            objects_detected = self.detect_objects(image)

            # Draw objects boundaries to the actual frame
            image_with_borders = self.draw_bounding_boxes(image, objects_detected)

            # If output is video with object boundaries
            if output_type == OutputType.BORDERS:
                # Write frame with object boundaries to output video
                out_cap.write(cv2.cvtColor(image_with_borders, cv2.COLOR_BGR2RGB))

            # If output is panorama image
            elif output_type == OutputType.PANORAMA:
                # Crop objects in the frame (get numpy array represantition of objects)
                objects_cropped = self.crop_objects(image, objects_detected)

                # Process objects in the frame
                matcher.process_objects(frame_cnt, objects_cropped)

                # Save objects which were detected in the frame
                matcher.save_objects(output_name.split(".")[0] + "-dir/", frame_cnt, objects_cropped)

            # Save visualized frame to tmp/image-dir/
            image = Image.fromarray(image_with_borders)
            image.save(tmp_frame_dir + file.get_frame_name(output_type) + "-frame" + str(frame_cnt) + ".jpg")

            # Visualize processed frame with detected objects to output label
            window.actualize_output_label(npimg_to_pixmap(image_with_borders))

            # Update progress bar
            completed += step
            window.progress_bar.setValue(completed)

            frame_cnt += 1

        # Release source vid
        in_cap.release()
        if output_type == OutputType.BORDERS:
            out_cap.release()

        # Process panorama image and get its name
        elif output_type == OutputType.PANORAMA:
            img = matcher.get_panorama(InputType.VIDEO)
            window.actualize_output_label(npimg_to_pixmap(img))
            img = Image.fromarray(img)
            img.save(output_name)

        cv2.destroyAllWindows()

        return output_name
