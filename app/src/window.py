#===============================================================================
# Brno University of Technology
# Faculty of Information Technology
# Academic year: 2018/2019
# Bachelor thesis: Monitoring Pedestrian by Drone
# Author: Vladimír Dušek
#===============================================================================

import shutil
import sys

import cv2
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from file import File
from utils import InputType, MessageBoxType, OutputType, create_folder, npimg_to_pixmap


class Window(QMainWindow):
    """
    Class for PyQt window managing.
    """
    def __init__(self, detector, app):
        """
        Initialization of the window.
        :param detector: Detector with Retinanet model
        :param app: QApplication
        """
        super(Window, self).__init__()

        self.files = []
        self.output_name = None
        self.output_type = None
        self.detector = detector
        self.app = app
        self.tmp_dir = 'tmp/'

        self.setMinimumSize(800, 480)
        self.setWindowTitle('People Detector')
        self.setWindowIcon(QIcon('../icon/agent.jpg'))
        self.statusBar()

        create_folder(self.tmp_dir)

        open_action = QAction('&Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Select input image or video for people detection')
        open_action.triggered.connect(self.select_input)

        save_action = QAction('&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save output image/video as')
        save_action.triggered.connect(self.save_output)

        run_action = QAction('&Run', self)
        run_action.setShortcut('Ctrl+R')
        run_action.setStatusTip('Run recognition')
        run_action.triggered.connect(self.run_recognition)

        # help_action = QAction('&Help', self)
        # help_action.setShortcut('Ctrl+H')
        # help_action.setStatusTip('Show help contents')
        # help_action.triggered.connect(self.show_help)

        # settings_action = QAction('&Settings', self)
        # settings_action.setShortcut('Ctrl+Alt+S')
        # settings_action.setStatusTip('Edit application settings')
        # settings_action.triggered.connect(self.settings)

        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Quit People Detector')
        exit_action.triggered.connect(self.closeEvent)

        main_menu = self.menuBar()
        menu = main_menu.addMenu('&Menu')
        menu.addAction(open_action)
        menu.addAction(save_action)
        menu.addAction(run_action)
        # menu.addAction(help_action)
        # menu.addAction(settings_action)
        menu.addAction(exit_action)

        window = QWidget()

        grid = QGridLayout()
        grid.setColumnMinimumWidth(1, 320)
        grid.setColumnMinimumWidth(2, 320)

        self.input_label = QLabel()
        self.input_label.setFrameShape(QFrame.Box)
        self.input_label.setMinimumSize(320, 180)
        self.input_label.setObjectName('InputImage')

        self.output_label = QLabel()
        self.output_label.setFrameShape(QFrame.Box)
        self.output_label.setMinimumSize(320, 180)
        self.output_label.setObjectName('OutputImage')

        open_btn = QPushButton('Select Input')
        open_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        open_btn.setFixedHeight(35)
        open_btn.setStatusTip('Select input image or video for people detection')
        open_btn.clicked.connect(self.select_input)

        save_btn = QPushButton('Save Output As')
        save_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        save_btn.setFixedHeight(35)
        save_btn.setStatusTip('Save output image/video as')
        save_btn.clicked.connect(self.save_output)

        head_path_label = QLabel('Temporary output path:')
        head_path_label.setObjectName('HeadingOutputPath')

        self.path_label = QLabel()
        self.path_label.setObjectName('OutputPath')

        run_btn = QPushButton('Run Recognition')
        run_btn.setStatusTip('Run recognition')
        run_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        run_btn.setFixedHeight(35)
        run_btn.clicked.connect(self.run_recognition)

        video_btn = QRadioButton('Image/video with borders around people')
        video_btn.setStatusTip('Output will be image or video with borders around people')
        video_btn.clicked.connect(self.set_output_type_video)
        video_btn.setChecked(True)
        self.output_type = OutputType.BORDERS
        img_btn = QRadioButton('Panorama image with trajectories of people')
        img_btn.setStatusTip('Output will be panorama image with trajectories of people')
        img_btn.clicked.connect(self.set_output_type_img)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(35)
        self.progress_bar.setValue(0)

        grid.addWidget(self.input_label, 1, 1)
        grid.addWidget(self.output_label, 1, 2)

        grid.addWidget(open_btn, 2, 1)
        grid.addWidget(save_btn, 2, 2)

        grid.addWidget(video_btn, 3, 1)
        grid.addWidget(img_btn, 4, 1)

        grid.addWidget(head_path_label, 3, 2)
        grid.addWidget(self.path_label, 4, 2)

        grid.addWidget(run_btn, 5, 1, 1, 2)
        grid.addWidget(self.progress_bar, 6, 1, 1, 2)

        self.message_box = QMessageBox()

        # Just temporarily settings

        # combo_box = QComboBox(self)
        # combo_box.addItem("CDE")
        # combo_box.addItem("Cleanlooks")
        # combo_box.addItem("GTK+")
        # combo_box.addItem("Motif")
        # combo_box.addItem("Plastique")
        # combo_box.addItem("Windows")
        # combo_box.move(500, 100)
        # combo_box.activated[str].connect(self.style_choice)

        # grid.addWidget(combo_box, 7, 2)

        window.setLayout(grid)

        self.setCentralWidget(window)
        self.show()

    @staticmethod
    def style_choice(name):
        """
        Change Qt style.
        :param name: name of the style
        """
        QApplication.setStyle(QStyleFactory.create(name))

    def actualize_input_label(self, image):
        """
        Actualize the input label with the new image.
        :param image: the new image
        """
        pixmap = QPixmap(image)
        pixmap = pixmap.scaled(self.input_label.width(), self.input_label.height(), Qt.KeepAspectRatio)
        self.input_label.setPixmap(pixmap)
        self.input_label.setAlignment(Qt.AlignCenter)
        self.input_label.repaint()
        self.app.processEvents()

    def actualize_output_label(self, image):
        """
        Actualize the output label with the new image.
        :param image: the new image
        """
        pixmap = QPixmap(image)
        pixmap = pixmap.scaled(self.output_label.width(), self.output_label.height(), Qt.KeepAspectRatio)
        self.output_label.setPixmap(pixmap)
        self.output_label.setAlignment(Qt.AlignCenter)
        self.output_label.repaint()
        self.app.processEvents()

    def set_output_type_img(self):
        """
        Set output type to PANORAMA.
        """
        self.output_type = OutputType.PANORAMA
        if self.files:
            self.path_label.setText(self.files[0].get_output_name(self.output_type))

    def set_output_type_video(self):
        """
        Set output type to BORDERS.
        """
        self.output_type = OutputType.BORDERS
        if self.files:
            self.path_label.setText(self.files[0].get_output_name(self.output_type))

    def select_input(self):
        """
        Save the name of the input file, clear output label, set progress bar to zero and actualize input label.
        When Select Input button is trigerred the method is invoked.
        """
        full_paths = QFileDialog.getOpenFileNames(None, 'Open File', '',
                                                  '*.jpg *.jpeg *.png *.bmp *.mp4 *.avi *.wmv *.mov *.mkv')
        if full_paths:
            # Clear input files list
            self.files.clear()
            self.output_name = None
            for full_path in full_paths:
                file = File(self.tmp_dir, full_path)

                # Clear output label image, progress bar and label text
                self.output_label.clear()
                self.progress_bar.setValue(0)
                self.path_label.setText(file.get_output_name(self.output_type))

                # Actualize input label image
                if file.type == InputType.IMAGE:
                    image = file.full_path
                elif file.type == InputType.VIDEO:
                    ret, image = cv2.VideoCapture(file.full_path).read()
                    if not ret:
                        raise ValueError
                    image = npimg_to_pixmap(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                else:
                    raise ValueError
                self.actualize_input_label(image)

                # Add input file to a list of files
                self.files.append(file)

    def save_output(self):
        """
        Save the processed output file to the user's selected path.
        When Save Output As button is trigerred the method is invoked.
        """
        if self.progress_bar.value() != 100:
            self.show_message_box(MessageBoxType.ERROR, 'Error', 'There is no processed file.')
        else:
            src = self.output_name
            dst = QFileDialog.getSaveFileName(None, 'Save File', src.split('/')[1])
            if dst:
                shutil.copyfile(src, dst)

    def run_recognition(self):
        """
        Run recognition, process input file.
        When Run Recognition button is trigerred the method is invoked.
        """
        if len(self.files) == 0:
            self.show_message_box(MessageBoxType.ERROR, 'Error', 'There is no input image or video to be processed.')
        elif self.output_type is None:
            self.show_message_box(MessageBoxType.ERROR, 'Error', 'Output type has to be specified.')
        else:
            self.output_label.clear()
            self.output_label.repaint()

            for file in self.files[::-1]:
                # Reset progress bar and output label
                self.progress_bar.setValue(0)
                self.app.processEvents()
                self.path_label.setText(file.get_output_name(self.output_type))

                # Actualize input label image because of input stacking
                if file.type == InputType.IMAGE:
                    image = file.full_path
                elif file.type == InputType.VIDEO:
                    ret, image = cv2.VideoCapture(file.full_path).read()
                    if not ret:
                        raise ValueError
                    image = npimg_to_pixmap(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                else:
                    raise ValueError
                self.actualize_input_label(image)

                if file.type == InputType.IMAGE:
                    self.output_name = self.detector.process_image(self, file, self.output_type)

                elif file.type == InputType.VIDEO:
                    self.output_name = self.detector.process_video(self, file, self.output_type)

                else:
                    raise ValueError

                self.progress_bar.setValue(100)
                self.app.processEvents()

                if file.type == InputType.VIDEO:
                    self.show_message_box(MessageBoxType.INFORMATION, 'Information', 'Detection is done')

    def show_message_box(self, box_type, title, text):
        """
        Show message box.
        :param box_type: type of the box
        :param title: box title
        :param text: box text
        """
        if box_type == MessageBoxType.ERROR:
            self.message_box.setIcon(QMessageBox.Critical)
            self.message_box.setStandardButtons(QMessageBox.Close)
        elif box_type == MessageBoxType.WARNING:
            self.message_box.setIcon(QMessageBox.Warning)
            self.message_box.setStandardButtons(QMessageBox.Close)
        elif box_type == MessageBoxType.INFORMATION:
            self.message_box.setIcon(QMessageBox.Information)
            self.message_box.setStandardButtons(QMessageBox.Ok)
        else:
            raise ValueError
        self.message_box.setWindowTitle(title)
        self.message_box.setText(text)
        self.message_box.exec_()

    @staticmethod
    def show_help():
        """
        Show help (ToDo)
        """
        print('ToDo: showing help')

    @staticmethod
    def settings():
        """
        Show settings (ToDo)
        """
        print('ToDo: showing settings')

    def closeEvent(self, event):
        """
        Close the event.
        :param event: event to be closed
        """
        choice = QMessageBox.question(self, 'Confirm Exit', 'Are you sure you want to exit People Detector?',
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        try:
            if choice == QMessageBox.Yes:
                try:
                    shutil.rmtree(self.tmp_dir)
                    event.accept()
                except AttributeError:
                    sys.exit(0)
            else:
                try:
                    event.ignore()
                except AttributeError:
                    pass
        # In case user have already deleted tmp/ directory
        except FileNotFoundError:
            pass
