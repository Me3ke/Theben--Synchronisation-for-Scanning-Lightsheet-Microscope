import threading

from src.Controller.CameraController import CameraController
from src.Controller.HardwareController import HardwareController
from src.Controller.LaserController import LaserController
from src.util.FileLoader import *


class AbstractCommander:

    hardware_controller = None
    camera_controller = None
    laser_controller = None
    gui_controller = None
    init = None
    setup = None
    param = None
    param_path = ""
    setup_path = ""
    verified = False
    stopped = False
    started = False
    mode = ''

    def __init__(self, gui_controller, init, setup_path, param_path=""):
        self.gui_controller = gui_controller
        self.init = init
        self.setup_path = setup_path
        self.param_path = param_path
        try:
            self.setup = load(setup_path, 'setup')
            self.param = load(param_path, 'param')
        except Exception as ex:
            log.error("Could not verify. Try modifying a setup or create a new one. Or parameter file corrupted.")
            log.error("The corresponding error arises from: ")
            log.critical(str(ex))
            raise ex

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
            self.laser_controller.set_commands()
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
        pass

    def stop(self):
        if not self.stopped:
            if self.verified:
                log.info("Stopping...")
                self.stopped = True
                self.started = False
                self.verified = False
                self.camera_controller.stop()
                self.laser_controller.stop()
                self.hardware_controller.stop()
        else:
            log.warning("Already stopped")

    def cont_thread(self):
        thread = threading.Thread(target=self.cont, name='Restart')
        thread.start()

    def cont(self):
        if self.stopped and not self.started and not self.verified:
            log.info("Continue...")
            self.verified = False
            self.run()
            self.stopped = False
        else:
            log.warning("Already continued")
