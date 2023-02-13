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
    stopped = False
    max_list = []
    mode = '2'

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
            self.camera_controller = CameraController(self.setup)
            self.hardware_controller = HardwareController(self.setup, self.param)
            self.hardware_controller.init_hc()
            self.hardware_controller.set_commands(self.setup, self.param, self.mode)
            self.hardware_controller.transmit_commands()
            self.laser_controller = LaserController(self.setup)
            self.laser_controller.set_commands_run()
            return True
        except Exception as e:
            log.error("Failed to initialize connections.")
            log.error("The corresponding error arises from: ")
            log.critical(str(e))
            self.verified = False
            self.stopped = True
            return False

    def start_thread(self):
        thread = threading.Thread(target=self.start, name='Start')
        thread.start()

    def start(self):
        log.info("starting now...")
        if self.stopped:
            log.warning("After stopping the Application, you need to continue first, before restarting.")
        else:
            self.laser_controller.arm_laser()
            thread = threading.Thread(target=self.hardware_controller.start)
            thread.start()
            image = self.camera_controller.take_picture()
            if image is None:
                log.error("Camera could not make an image, make sure the parameters are valid.")
            else:
                self.gui_controller.update_image(image)
            elapsed_time = self.hardware_controller.get_single_command()
            log.info("The galvo needed " + elapsed_time + "microseconds")
        """
        center_image = np.sum(image, axis=1)
        max = np.amax(center_image)
        for i in range(0, image.shape[1]):
            if center_image[i] == max:
                self.max_list.append(i)
                print(i)
        """

    def stop(self):
        if self.verified:
            self.laser_controller.stop_laser()
            self.hardware_controller.stop()
            self.stopped = True

    def cont_thread(self):
        thread = threading.Thread(target=self.cont, name='Restart')
        thread.start()

    def cont(self):
        if self.stopped:
            self.hardware_controller.cont()
            self.verified = False
            self.stopped = False
            self.run()


# TODO exit codes