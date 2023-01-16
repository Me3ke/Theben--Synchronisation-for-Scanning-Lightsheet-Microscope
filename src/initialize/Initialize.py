"""

"""
import time

from Controller.GUIController import GUIController
from initialize.Verification import Verification
from Commander.CalibrationCommander import CalibrationCommander
from Commander.RunningCommander import RunningCommander

import logging

log = logging.getLogger("log")


class Initialize:

    gui_controller = None
    commander = None
    mode = ""
    sequence = ""
    setup_path = ""
    param_path = ""

    def __init__(self, argv):
        # fange etwas mit den Argumenten an
        self.init_config()

    def init_config(self):
        self.gui_controller = GUIController(self)
        self.gui_controller.add_subscriber_for_main_window_event(self.init_commander)
        self.gui_controller.start_config_window()

    def init_commander(self):
        time.sleep(1)
        self.mode = self.gui_controller.mode
        self.sequence = self.gui_controller.sequence
        self.setup_path = self.gui_controller.setup_path
        self.param_path = self.gui_controller.param_path
        verificator = Verification(self.mode, self.sequence, self.setup_path, self.param_path)
        if self.mode == "running":
            self.commander = RunningCommander(self.gui_controller, verificator)
        else:
            self.commander = CalibrationCommander(self.gui_controller, verificator)
        self.gui_controller.set_commander(self.commander)
        self.commander.run()

    def stop(self):
        if self.commander is None:
            log.critical("quitting without commander")
        else:
            self.commander.stop()

