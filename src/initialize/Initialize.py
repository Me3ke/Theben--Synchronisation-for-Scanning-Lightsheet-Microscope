import time
import logging

from src.Controller.GUIController import GUIController
from src.Commander.CalibrationCommander import CalibrationCommander
from src.Commander.RunningCommander import RunningCommander
from src.util.FileLoader import *
from src.Exceptions.InitializeException import InitializeException

log = logging.getLogger("log")

"""

"""


class Initialize:

    gui_controller = None
    commander = None
    setup = None
    param = None

    mode = ""
    sequence = ""
    setup_path = ""
    param_path = ""

    def __init__(self, argv):
        self.gui_controller = GUIController(self)
        self.gui_controller.add_subscriber_for_main_window_event(self.init_commander)
        if len(argv) == 3:
            self.gui_controller.start_config_window(argv[1], argv[2])
        else:
            self.gui_controller.start_config_window("", "")

    def init_commander(self):
        time.sleep(1)
        self.mode = self.gui_controller.mode
        self.setup_path = self.gui_controller.setup_path
        self.param_path = self.gui_controller.param_path
        if self.mode == "running":
            self.commander = RunningCommander(self.gui_controller, self.setup_path, self.param_path)
        else:
            self.commander = CalibrationCommander(self.gui_controller, self.setup_path, self.param_path)
        try:
            self.gui_controller.set_commander(self.commander)
            self.commander.run()
        except InitializeException as ex:
            log.critical("Could not initialize main window: ")
            log.critical(ex)
            exit(100)

    def stop(self):
        if self.commander is None:
            log.warning("Terminating program")
            exit
        else:
            self.commander.stop()

