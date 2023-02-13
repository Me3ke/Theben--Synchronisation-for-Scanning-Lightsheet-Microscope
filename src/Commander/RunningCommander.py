"""

"""
import logging
import threading
import numpy as np
from src.Controller.CameraController import CameraController
from src.Controller.HardwareController import HardwareController
from src.Controller.LaserController import LaserController
from src.util.FileLoader import *

log = logging.getLogger("log")


class RunningCommander:

    hardware_controller = None
    camera_controller = None
    laser_controller = None
    setup = None
    verified = False
    max_list = []

    def __init__(self, gui_controller, setup_path, param_path):
        self.gui_controller = gui_controller
        try:
            self.setup = load_setup(setup_path)
            self.param = load_param(param_path)
        except Exception as e:
            log.error("Could not verify. Try modifying a setup or create a new one")
            log.error("The corresponding error arises from: ")
            log.critical(str(e))

    def run(self):
        if self.initialize_controllers():
            self.verified = True
            self.gui_controller.set_verified()

    def initialize_controllers(self):
        try:

            self.hardware_controller = HardwareController(self.setup)
            self.camera_controller = CameraController(self.setup)
            #self.laser_controller = LaserController(self.setup)
            # TODO datentransfer zu arduino etc.....
            return True
        except Exception as e:
            log.error("Failed to initialize connections.")
            log.error("The corresponding error arises from: ")
            log.critical(str(e))
            return False

    def start_thread(self):
        thread = threading.Thread(target=self.start, name='Start')
        thread.start()

    def start(self):
        log.info("starting now...")
        #self.laser_controller.set_commands_run()
        #self.laser_controller.arm_laser()
        thread = threading.Thread(target=self.hardware_controller.set_commands)
        thread.start()
        image = self.camera_controller.take_picture()
        #self.hardware_controller.set_commands_running()
        center_image = np.sum(image, axis=1)
        max = np.amax(center_image)
        for i in range(0, image.shape[1]):
            if center_image[i] == max:
                self.max_list.append(i)
                print(i)
        self.gui_controller.update_image(image)

    def stop(self):
        pass
        #self.laser_controller.stop_laser()
        #self.hardware_controller.stop_hc()
        # TODO other...

    def cont(self):
        # TODO should enable connections again too
        # if not self.verified: run
        pass


# TODO exit codes