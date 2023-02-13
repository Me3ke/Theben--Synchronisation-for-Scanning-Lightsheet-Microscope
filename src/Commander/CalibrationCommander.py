"""

"""

import logging

from src.Controller.CameraController import CameraController
from src.Controller.HardwareController import HardwareController
from src.Controller.LaserController import LaserController

log = logging.getLogger("log")


class CalibrationCommander:
    hardware_controller = None
    camera_controller = None
    laser_controller = None
    setup = None

    def __init__(self, gui_controller):
        self.gui_controller = gui_controller

    def initialize(self):
        self.hardware_controller = HardwareController()
        self.camera_controller = CameraController()
        self.laser_controller = LaserController()
        # TODO datentransfer zu arduino etc.....

    def start(self):
        pass

    def stop(self):
        pass

    def cont(self):
        pass
