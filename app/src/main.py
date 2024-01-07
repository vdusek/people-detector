# ===============================================================================
# Brno University of Technology
# Faculty of Information Technology
# Academic year: 2018/2019
# Bachelor thesis: Monitoring Pedestrian by Drone
# Author: Vladimír Dušek
# ===============================================================================

import sys

from PyQt4.QtGui import QApplication

from detector import Detector
from window import Window

if __name__ == "__main__":
    # 1) Create Detector with Retinanet trained model
    detector = Detector()

    # 2) Run Qt application
    app = QApplication(sys.argv)

    # 3) Create Qt window
    window = Window(detector, app)

    # 4) Wait for the exit
    exit(app.exec_())
