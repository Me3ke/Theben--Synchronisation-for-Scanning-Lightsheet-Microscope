import threading

from Controller.CameraController import CameraController
from Controller.HardwareController import HardwareController
from Controller.LaserController import LaserController
from util.FileLoader import *


class AbstractCommander:
    """Abstract Commander class that implements the default method of both commanders"""

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
        """Start all connections to the controllers and set the machine into verified state if successful"""
        if self.initialize_controllers():
            self.verified = True
            self.gui_controller.set_verified()
            log.info("Finished. Data has been verified")

    def initialize_controllers(self):
        """Prepare all controllers for program sequence and check for initializing errors"""
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
        """Call a thread after start button has been pressed"""
        thread = threading.Thread(target=self.start, name='Start')
        thread.start()

    def start(self):
        """Method will be overwritten by either controller"""
        pass

    def stop(self):
        """Stops current controller actions and sets appropriate flags"""
        if not self.stopped:
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
        """Call a thread after continue button has been pressed"""
        thread = threading.Thread(target=self.cont, name='Restart')
        thread.start()

    def cont(self):
        """Continue/Restart current controller actions and sets appropriate flags"""
        if self.stopped and not self.started and not self.verified:
            log.info("Continue...")
            self.verified = False
            self.run()
            self.stopped = False
        else:
            log.warning("Already continued")
