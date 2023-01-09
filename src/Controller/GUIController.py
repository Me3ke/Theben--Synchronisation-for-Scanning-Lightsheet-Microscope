import time
import logging
import sys
import threading

from PyQt6.QtCore import QFile, QIODeviceBase
from PyQt6.QtWidgets import QApplication, QFileDialog
from GUI.MainWindow import MainWindow
from GUI.ConfigWindow import ConfigWindow
from GUI.SetupWindow import SetupWindow
from util.Event import Event
from util.FileLoader import *

log = logging.getLogger("log")
home_dir = os.path.expanduser("~/Desktop")

"""
"""


class GUIController:
    # TODO macht ein controller interface sinn?

    main_window = None
    config_window = None
    setup_window = None

    app = None
    commander = None
    verified = False

    mode = ""
    sequence = ""
    setup_path = ""
    param_path = ""

    setup_to_modify = None

    def __init__(self, initializer):
        self.on_start_main_window = Event()
        self.initializer = initializer

    def start_config_window(self):
        thread = threading.Thread(target=self.show_config_window, name='Config_Window')
        thread.start()
        time.sleep(1)

        self.config_window.add_subscriber_for_finished_check_event(self.start_main_window)
        self.config_window.add_subscriber_for_modify_setup_event(self.modify_setup)
        self.config_window.add_subscriber_for_create_setup_event(self.create_setup)

    def start_main_window(self):
        self.mode = self.config_window.mode
        self.sequence = self.config_window.sequence
        self.setup_path = self.config_window.setup_path
        self.param_path = self.config_window.param_path

        thread = threading.Thread(target=self.on_start_main_window, name='Create_Commander')
        thread.start()

        self.config_window.close()
        self.main_window = MainWindow()
        self.main_window.show()

        time.sleep(1)

        self.main_window.add_subscriber_for_save_event(self.save)
        self.test_log()

    def show_config_window(self):
        app = QApplication(sys.argv)
        app.aboutToQuit.connect(self.initializer.stop)
        self.config_window = ConfigWindow()
        sys.exit(app.exec())

    def save(self):
        pixmap = self.main_window.get_pixmap()
        path_to_file = self.main_window.save_image_path
        if path_to_file == "":
            log.error("No path specified")
        else:
            file = QFile(path_to_file)
            if file.open(QIODeviceBase.OpenModeFlag.WriteOnly):
                pixmap.save(file)
            else:
                log.error("File could not be opened, make sure the file is closed and files may be created")

    def test_log(self):
        log.debug('damn, a bug')
        log.info('something to remember')
        log.warning('that\'s not right')
        log.error('foobar')
        log.critical("theben")

    def modify_setup(self):
        file_name = QFileDialog.getOpenFileName(None, "Open File", home_dir)
        if file_name[0]:
            setup = read_setup(file_name[0])
            self.setup_window = SetupWindow(file_name[0], setup)
            self.config_window.setup_box.setText(file_name[0])
            self.setup_window.show()

    def create_setup(self):
        file_name = QFileDialog.getSaveFileName(None, "Save File", home_dir)
        if file_name[0]:
            self.setup_window = SetupWindow(file_name[0], None)
            self.config_window.setup_box.setText(file_name[0])
            self.setup_window.show()

    def add_subscriber_for_main_window_event(self, obj_method):
        self.on_start_main_window += obj_method

    def remove_subscriber_for_main_window_event(self, obj_method):
        self.on_start_main_window -= obj_method

    def set_commander(self, commander):
        self.commander = commander
        log.info("commander has been set")
        self.main_window.add_subscriber_for_start_event(self.commander.start)
        self.main_window.add_subscriber_for_stop_event(self.commander.stop)
        self.main_window.add_subscriber_for_continue_event(self.commander.cont)

    def set_verified(self):
        self.verified = True
        self.main_window.verified = True
        log.info("Data has been verified")

