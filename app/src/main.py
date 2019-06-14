#===============================================================================
# Brno University of Technology
# Faculty of Information Technology
# Academic year: 2018/2019
# Bachelor thesis: Monitoring Pedestrian by Drone
# Author: Vladimír Dušek
#===============================================================================

import sys
import os
from PyQt4.QtGui import QApplication
from window import Window
from detector import Detector


if __name__ == '__main__':

    # 1) Create Detector with Retinanet trained model
    detector = Detector()

    # 2) Run Qt application
    app = QApplication(sys.argv)

    # 3) Create Qt window
    window = Window(detector, app)

    # 4) Wait for the exit
    exit(app.exec_())
