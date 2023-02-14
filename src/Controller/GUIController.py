import time
import logging
import cv2
import numpy as np
import sys
import threading

from PyQt6.QtCore import QFile, QIODeviceBase
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtGui import QImage, QPixmap
from src.GUI.MainWindow import MainWindow
from src.GUI.ConfigWindow import ConfigWindow
from src.GUI.SetupWindow import SetupWindow
from src.util.Event import Event
from src.util.FileLoader import *
from src.Exceptions.InitializeException import InitializeException

FIRST_IMAGE_NAME = './resources/default.tif'
DEFAULT_IMAGE_WIDTH = 1024
DEFAULT_IMAGE_HEIGHT = 512
DEFAULT_IMAGE_MAX_PIXEL_VALUE = 65535
DEFAULT_IMAGE_TYPE = QImage.Format.Format_Grayscale16
DEFAULT_IMAGE_INT_TYPE = np.uint16
log = logging.getLogger("log")
home_dir = os.path.expanduser("~/Desktop")

"""
"""


class GUIController:

    main_window = None
    config_window = None
    setup_window = None

    app = None
    commander = None
    verified = False

    mode = ""
    setup_path = ""
    param_path = ""

    image_array_resized = None
    original_array = None
    original_height = 0
    original_width = 0

    brightness = 0
    contrast = 1
    gamma = 1

    def __init__(self, initializer):
        self.on_start_main_window = Event()
        self.initializer = initializer

    def start_config_window(self, setup_path, param_path):
        thread = threading.Thread(target=self.show_config_window, name='Config_Window', args=(setup_path, param_path))
        thread.start()
        time.sleep(0.5)

        self.config_window.add_subscriber_for_finished_check_event(self.start_main_window)
        self.config_window.add_subscriber_for_modify_setup_event(self.modify_setup)
        self.config_window.add_subscriber_for_create_setup_event(self.create_setup)

    def start_main_window(self):
        self.mode = self.config_window.mode
        self.setup_path = self.config_window.setup_path
        self.param_path = self.config_window.param_path

        thread = threading.Thread(target=self.on_start_main_window, name='Create_Commander')
        thread.start()

        self.config_window.close()
        self.main_window = MainWindow()
        try:
            image_array = cv2.imread(FIRST_IMAGE_NAME, -1)
            self.image_array_resized = resize_and_normalize(image_array)
            pixmap = convert_array_to_pixmap(self.image_array_resized)
            self.main_window.show_image(pixmap)
        except Exception:
            raise InitializeException("Could not initialize main window. Probably error with ./resources/default.tif")
        time.sleep(0.5)
        self.main_window.add_subscriber_for_save_event(self.save)
        self.main_window.add_subscriber_for_brightness_event(self.change_brightness)
        self.main_window.add_subscriber_for_contrast_event(self.change_contrast)
        self.main_window.add_subscriber_for_gamma_event(self.change_gamma)

    def show_config_window(self, setup_path, param_path):
        app = QApplication(sys.argv)
        app.aboutToQuit.connect(self.initializer.stop)
        self.config_window = ConfigWindow(setup_path, param_path)
        sys.exit(app.exec())

    def save(self):
        result_array = np.zeros((DEFAULT_IMAGE_HEIGHT, DEFAULT_IMAGE_WIDTH))
        normalized_array = cv2.normalize(self.original_array, result_array, 0,
                                         DEFAULT_IMAGE_MAX_PIXEL_VALUE, cv2.NORM_MINMAX)
        pixmap = self.update_image_values(normalized_array)
        path_to_file = self.main_window.save_image_path
        if path_to_file == "":
            log.error("No path specified")
        else:
            file = QFile(path_to_file)
            if file.open(QIODeviceBase.OpenModeFlag.WriteOnly):
                pixmap.save(file)
                log.info("File saved")
            else:
                log.error("File could not be opened, make sure the file is closed and files may be created")

    # TODO add useful logs
    # TODO adjust contrast brightness etc values
    def change_brightness(self):
        self.brightness = self.main_window.brightness_slider.value()
        self.main_window.brightness_label.setText("Brightness: " + str(self.brightness))
        pixmap = self.update_image_values(self.image_array_resized)
        self.main_window.show_image(pixmap)

    def change_contrast(self):
        self.contrast = self.main_window.contrast_slider.value()
        self.main_window.contrast_label.setText("Contrast: " + str(self.contrast))
        pixmap = self.update_image_values(self.image_array_resized)
        self.main_window.show_image(pixmap)

    def change_gamma(self):
        self.gamma = self.main_window.gamma_slider.value() / 100
        self.main_window.gamma_label.setText("Gamma: " + str(self.gamma))
        pixmap = self.update_image_values(self.image_array_resized)
        self.main_window.show_image(pixmap)

    def update_image_values(self, image_array):
        new_array = image_array.copy()
        lim = int(DEFAULT_IMAGE_MAX_PIXEL_VALUE / self.contrast - self.brightness)
        new_array[new_array > lim] = DEFAULT_IMAGE_MAX_PIXEL_VALUE
        new_array[new_array <= lim] *= self.contrast
        new_array[new_array <= lim] += self.brightness
        result_array = np.power(new_array, self.gamma).clip(0, DEFAULT_IMAGE_MAX_PIXEL_VALUE)\
            .astype(DEFAULT_IMAGE_INT_TYPE)
        pixmap = convert_array_to_pixmap(result_array)
        return pixmap

    def update_image(self, new_image):
        self.original_height = new_image.shape[0]
        self.original_width = new_image.shape[1]
        self.original_array = new_image
        self.main_window.brightness_slider.setValue(0)
        self.main_window.contrast_slider.setValue(1)
        self.main_window.gamma_slider.setValue(1)
        self.brightness = 0
        self.contrast = 1
        self.gamma = 1
        self.image_array_resized = resize_and_normalize(new_image)
        pixmap = convert_array_to_pixmap(self.image_array_resized)
        self.main_window.show_image(pixmap)

    def modify_setup(self):
        setup_path = self.config_window.setup_path
        if setup_path == "":
            file_name = QFileDialog.getOpenFileName(None, "Open File", home_dir)
            if file_name[0]:
                setup = read_setup(file_name[0])
                self.setup_window = SetupWindow(file_name[0], setup)
                self.config_window.setup_box.setText(file_name[0])
            else:
                log.warning("No path specified")
        else:
            setup = read_setup(setup_path)
            self.setup_window = SetupWindow(setup_path, setup)

    def create_setup(self):
        setup_path = self.config_window.setup_path
        if setup_path == "":
            file_name = QFileDialog.getSaveFileName(None, "Save File", home_dir)
            if file_name[0]:
                setup = read_setup('./resources/setups/setup_default.py')
                self.setup_window = SetupWindow(file_name[0], setup)
                self.config_window.setup_box.setText(file_name[0])
            else:
                log.warning("No path specified")
        else:
            setup = read_setup('./resources/setups/setup_default.py')
            self.setup_window = SetupWindow(setup_path, setup)

    def add_subscriber_for_main_window_event(self, obj_method):
        self.on_start_main_window += obj_method

    def remove_subscriber_for_main_window_event(self, obj_method):
        self.on_start_main_window -= obj_method

    def set_commander(self, commander):
        self.commander = commander
        log.debug("Commander has been set")
        if self.main_window is None:
            raise InitializeException("Could not initialize main window")
        else:
            self.main_window.add_subscriber_for_start_event(self.commander.start_thread)
            self.main_window.add_subscriber_for_stop_event(self.commander.stop)
            self.main_window.add_subscriber_for_continue_event(self.commander.cont_thread)

    def set_verified(self):
        self.verified = True
        self.main_window.verified = True


def resize_and_normalize(array):
    image_array_resized = cv2.resize(array, (DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT))
    result_array = np.zeros((DEFAULT_IMAGE_HEIGHT, DEFAULT_IMAGE_WIDTH))
    normalized_array = cv2.normalize(image_array_resized, result_array, 0,
                                     DEFAULT_IMAGE_MAX_PIXEL_VALUE, cv2.NORM_MINMAX)
    return normalized_array


def convert_array_to_pixmap(array):
    height, width = array.shape
    q_img = QImage(array.data, width, height, DEFAULT_IMAGE_TYPE)
    pixmap = QPixmap(q_img)
    return pixmap
