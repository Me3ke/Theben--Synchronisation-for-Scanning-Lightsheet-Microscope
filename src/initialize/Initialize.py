import time
import logging

from PyQt6.QtWidgets import QApplication

from src.Controller.GUIController import GUIController
from src.Commander.CalibrationCommander import CalibrationCommander
from src.Commander.RunningCommander import RunningCommander
from src.util.FileLoader import *
from src.Exceptions.InitializeException import InitializeException

log = logging.getLogger("log")


class Initialize:
    """
    Initializing gui controller and creating commander
    after setup has been configured.
    """

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
        # When config window's okay button is pressed, create a commander
        self.gui_controller.add_subscriber_for_main_window_event(self.init_commander)
        if len(argv) == 3:
            # Program arguments can load default paths into the setup and param text fields
            self.gui_controller.start_config_window(argv[1], argv[2])
        else:
            self.gui_controller.start_config_window("", "")

    def init_commander(self):
        """
        Create a commander given the mode and run verification of commander.
        After that the commander has all responsibilities.
        """
        time.sleep(1)
        # Transfer info from config window to commander
        self.mode = self.gui_controller.mode
        self.setup_path = self.gui_controller.setup_path
        self.param_path = self.gui_controller.param_path
        try:
            if self.mode == "running":
                self.commander = RunningCommander(self.gui_controller, self, self.setup_path, self.param_path)
            else:
                self.commander = CalibrationCommander(self.gui_controller, self, self.setup_path, self.param_path)
        except FileImportException:
            return
        try:
            self.gui_controller.set_commander(self.commander)
            self.commander.run()
        except InitializeException as ex:
            # Exception is thrown if main window could not be created
            log.critical("Could not initialize main window: ")
            log.critical(ex)
            exit(100)

    def stop(self):
        """Call before terminating to make sure all resources are reset"""
        if self.commander is None:
            log.warning("Terminating program")
            exit()
        else:
            # Direct stop command to commander
            self.commander.stop()

    def set_new_commander(self, commander):
        """Sets a new commander"""
        self.commander = commander


