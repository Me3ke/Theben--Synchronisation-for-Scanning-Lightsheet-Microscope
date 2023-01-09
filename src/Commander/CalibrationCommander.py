"""

"""

import logging

from Controller.CameraController import CameraController
from Controller.HardwareController import HardwareController
from Controller.LaserController import LaserController

log = logging.getLogger("log")


class CalibrationCommander:
    hardware_controller = None
    camera_controller = None
    laser_controller = None
    setup = None

    def __init__(self, gui_controller, verificator):
        self.gui_controller = gui_controller
        self.verificator = verificator
        self.verificator.set_commander(self)

    def start_verification(self):
        try:
            self.setup = self.verificator.verify()
            return True
        except Exception as e:
            log.error("Could not verify. Try modifying a setup or create a new one")
            log.error("The corresponding error arises from: ")
            log.critical(str(e))
            return False
        # TODO andere Fehlerbehandlung

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
