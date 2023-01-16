"""

"""
import logging
import threading
from src.Controller.CameraController import CameraController
from src.Controller.HardwareController import HardwareController
from src.Controller.LaserController import LaserController

log = logging.getLogger("log")


class RunningCommander:

    hardware_controller = None
    camera_controller = None
    laser_controller = None
    setup = None

    def __init__(self, gui_controller, verificator):
        self.gui_controller = gui_controller
        self.verificator = verificator
        self.verificator.set_commander(self)

    def run(self):
        if self.start_verification():
            if self.initialize_controllers():
                self.gui_controller.set_verified()

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

    def initialize_controllers(self):
        try:
            self.hardware_controller = HardwareController()
            self.camera_controller = CameraController(self.setup)
            self.laser_controller = LaserController(self.setup)
            # TODO datentransfer zu arduino etc.....
            return True
        except Exception as e:
            log.error("Could not use setup data. Try modifying a setup or create a new one")
            log.error("The corresponding error arises from: ")
            log.critical(str(e))
            return False

    def start_thread(self):
        thread = threading.Thread(target=self.start, name='Start')
        thread.start()

    def start(self):
        log.info("starting now...")
        self.laser_controller.set_commands_run()
        self.laser_controller.arm_laser()
        image = self.camera_controller.take_picture()
        self.gui_controller.update_image(image)

    def stop(self):
        self.laser_controller.stop_laser()
        # TODO other...

    def cont(self):
        pass
