import logging
import threading
import time

from src.Controller.CameraController import CameraController
from src.Controller.HardwareController import HardwareController
from src.Controller.LaserController import LaserController
from src.util.FileLoader import *

log = logging.getLogger("log")

"""

"""


class RunningCommander:

    hardware_controller = None
    camera_controller = None
    laser_controller = None
    setup = None
    verified = False
    stopped = False
    started = False
    max_list = []
    mode = '2'

    def __init__(self, gui_controller, setup_path, param_path):
        self.gui_controller = gui_controller
        try:
            self.setup = load_setup(setup_path)
            self.param = load_param(param_path)
        except Exception as e:
            log.error("Could not verify. Try modifying a setup or create a new one. Or parameter file corrupted.")
            log.error("The corresponding error arises from: ")
            log.critical(str(e))

    def run(self):
        if self.initialize_controllers():
            self.verified = True
            self.gui_controller.set_verified()
            log.info("Finished. Data has been verified")

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
        log.info("Starting...")
        if not self.started:
            if self.stopped:
                log.warning("After stopping the Application, you need to continue first, before restarting.")
            else:
                self.started = True
                self.laser_controller.arm_laser()
                thread = threading.Thread(target=self.hardware_controller.start)
                thread.start()
                image = self.camera_controller.take_picture(False)
                if image is None:
                    log.error("Camera could not make an image.")
                    time.sleep(2)
                    self.stop()
                else:
                    self.gui_controller.update_image(image)
                    try:
                        elapsed_time = self.hardware_controller.get_single_command()
                        log.info("The galvanometer needed " + elapsed_time + "microseconds")
                    except Exception as ex:
                        log.error(ex)
                    finally:
                        self.laser_controller.turn_off()
                        self.started = False
        else:
            log.warning("Already started")

    def stop(self):
        if not self.stopped:
            if self.verified:
                log.info("Stopping...")
                self.stopped = True
                self.started = False
                self.camera_controller.stop()
                self.laser_controller.stop()
                self.hardware_controller.stop()


    def cont_thread(self):
        thread = threading.Thread(target=self.cont, name='Restart')
        thread.start()

    def cont(self):
        if self.stopped and not self.started:
            log.info("Continue...")
            self.verified = False
            self.stopped = False
            self.run()
