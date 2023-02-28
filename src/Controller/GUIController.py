import time
import logging
import cv2
import numpy as np
import sys
import imageio
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

log = logging.getLogger("log")
home_dir = os.path.expanduser("~/Desktop")
file_filter = "Python (*.py *.ipynb)"

FIRST_IMAGE_NAME = './resources/default.tif'
DEFAULT_IMAGE_WIDTH = 1024
DEFAULT_IMAGE_HEIGHT = 1024
DEFAULT_IMAGE_MAX_PIXEL_VALUE = 65535
DEFAULT_IMAGE_TYPE = QImage.Format.Format_Grayscale16
DEFAULT_IMAGE_INT_TYPE = np.uint16


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
        """Start the config window via thread and sets up all button events"""
        thread = threading.Thread(target=self.show_config_window, name='Config_Window', args=(setup_path, param_path))
        thread.start()
        # Wait till config window is initialized. If an error occurs start the program with increased time
        time.sleep(1.5)

        self.config_window.add_subscriber_for_finished_check_event(self.start_main_window)
        self.config_window.add_subscriber_for_modify_setup_event(self.modify_setup)
        self.config_window.add_subscriber_for_create_setup_event(self.create_setup)

    def start_main_window(self):
        """
        Close the setup window, start the backend sequence and initialize the main window, and -events.
        :raise: InitializeException if main window cannot be created
        """
        # Save parameters from the config window
        self.mode = self.config_window.mode
        self.setup_path = self.config_window.setup_path
        self.param_path = self.config_window.param_path

        # Start backend program sequence
        thread = threading.Thread(target=self.on_start_main_window, name='Create_Commander')
        thread.start()

        self.config_window.close()
        self.main_window = MainWindow()

        try:
            # Setup first image (default.tif); -1 is IMREAD_UNCHANGED, because IMREAD_GRAYSCALE only supports 8 bit
            image_array = cv2.imread(FIRST_IMAGE_NAME, -1)
            # Make the image fit into the GUI
            self.image_array_resized = resize_and_normalize(image_array)
            pixmap = convert_array_to_pixmap(self.image_array_resized)
            self.main_window.show_image(pixmap)
        except Exception:
            # Will be raised if the default tif cannot be found or is not a 16 bit grayscale image for example.
            raise InitializeException("Could not initialize main window. Probably error with ./resources/default.tif")
        time.sleep(0.5)

        self.main_window.add_subscriber_for_save_event(self.save)
        self.main_window.add_subscriber_for_brightness_event(self.change_brightness)
        self.main_window.add_subscriber_for_contrast_event(self.change_contrast)
        self.main_window.add_subscriber_for_gamma_event(self.change_gamma)

    def show_config_window(self, setup_path, param_path):
        """Starting the PyQt Application with the config window"""
        self.app = QApplication(sys.argv)
        # If window is closed (e.g. by X) make sure all resources are properly closed
        self.app.aboutToQuit.connect(self.initializer.stop)
        self.config_window = ConfigWindow(setup_path, param_path)
        # Pass exit codes from QApplication
        sys.exit(self.app.exec())

    def save(self):
        """Save an image in original size"""
        # Make sure all image values are applied
        result_array = np.zeros((DEFAULT_IMAGE_HEIGHT, DEFAULT_IMAGE_WIDTH))
        normalized_array = cv2.normalize(self.original_array, result_array, 0,
                                         DEFAULT_IMAGE_MAX_PIXEL_VALUE, cv2.NORM_MINMAX)
        # Path will be saved in the main window after the dialog
        path_to_file = self.main_window.save_image_path
        if path_to_file == "":
            log.error("No path specified")
            return
        try:
            imageio.imwrite(path_to_file, normalized_array)
        except Exception as ex:
            log.error("File could not be opened, make sure the file is closed and files may be created")
            log.error(ex)

    def change_brightness(self):
        """On brightness slider released event, the brightness of the current image will be adjusted"""
        self.brightness = self.main_window.brightness_slider.value()
        self.main_window.brightness_label.setText("Brightness: " + str(self.brightness))
        pixmap = self.update_image_values(self.image_array_resized)
        self.main_window.show_image(pixmap)

    def change_contrast(self):
        """On contrast slider released event, the contrast of the current image will be adjusted"""
        self.contrast = self.main_window.contrast_slider.value()
        self.main_window.contrast_label.setText("Contrast: " + str(self.contrast))
        pixmap = self.update_image_values(self.image_array_resized)
        self.main_window.show_image(pixmap)

    def change_gamma(self):
        """On gamma slider released event, the gamma of the current image will be adjusted"""
        self.gamma = self.main_window.gamma_slider.value() / 100
        self.main_window.gamma_label.setText("Gamma: " + str(self.gamma))
        pixmap = self.update_image_values(self.image_array_resized)
        self.main_window.show_image(pixmap)

    def update_image_values(self, image_array):
        """
        Update an image with current brightness, contrast and gamma values.

        The image array is copied and brightness value is added, contrast is
        multiplied and gamma is potentiated regarding the maximum pixel values
        :param image_array: the current image to be processed
        :return: a pixmap of the processed image
        """
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
        """Updates an image, resize and normalize it and reset the image value sliders."""
        self.original_height = new_image.shape[0]
        self.original_width = new_image.shape[1]
        self.original_array = new_image
        self.main_window.brightness_slider.setValue(0)
        self.main_window.brightness_label.setText('Brightness: ' + "0")
        self.main_window.contrast_slider.setValue(1)
        self.main_window.contrast_label.setText('Contrast: ' + "1")
        self.main_window.gamma_slider.setValue(100)
        self.main_window.gamma_label.setText('Gamma: ' + "1")
        self.brightness = 0
        self.contrast = 1
        self.gamma = 1
        self.image_array_resized = resize_and_normalize(new_image)
        pixmap = convert_array_to_pixmap(self.image_array_resized)
        self.main_window.show_image(pixmap)

    def modify_setup(self):
        """
        Starting a setup window to configure a setup.

        Use an open file dialog to select a file that is loaded into
        the GUI. On finishing the setup, the parameters are saved into the same file again.
        """
        setup_path = self.config_window.setup_path
        if setup_path == "":
            # Use FileDialog, starting in home_dir (-> Desktop)
            file_name = QFileDialog.getOpenFileName(None, "Open File", home_dir, file_filter, file_filter)
            if file_name[0]:
                setup = read(file_name[0])
                self.setup_window = SetupWindow(file_name[0], setup)
                # Set the text in the config window to the selected path
                self.config_window.setup_box.setText(file_name[0])
            else:
                log.warning("No path specified")
        else:
            setup = read(setup_path)
            self.setup_window = SetupWindow(setup_path, setup)

    def create_setup(self):
        """
        Starting a setup window to create a setup.

        Use a save file dialog to create a file. The setup window loads the default setup,
        that can be adjusted. On finishing the setup, the parameters are saved into the new file.
        """
        setup_path = self.config_window.setup_path
        if setup_path == "":
            # Use FileDialog, starting in home_dir (-> Desktop)
            file_name = QFileDialog.getSaveFileName(None, "Save File", home_dir, file_filter, file_filter)
            if file_name[0]:
                setup = read('./resources/setups/setup_default.py')
                self.setup_window = SetupWindow(file_name[0], setup)
                # Set the text in the config window to the selected path
                self.config_window.setup_box.setText(file_name[0])
            else:
                log.warning("No path specified")
        else:
            setup = read('./resources/setups/setup_default.py')
            self.setup_window = SetupWindow(setup_path, setup)

    def add_subscriber_for_main_window_event(self, obj_method):
        self.on_start_main_window += obj_method

    def remove_subscriber_for_main_window_event(self, obj_method):
        self.on_start_main_window -= obj_method

    def set_commander(self, commander):
        """
        Set a commander for the GUI controller

        The GUI controller is created before the commander, because the
        config window decides which commander is instantiated and the config
        window needs the GUI controller. Therefore, this method retroactively
        sets a commander in the GUI controller. It also directs the button events
        to the corresponding commander methods. If a calibration commander
        finishes a calibration it will be replaced by a running commander.
        In this case, the button events need to be replaced
        :param commander: The new commander to be set
        :raise: InitializeException if the main window could not be created
        """
        if self.commander is None:
            remove = False
            old_commander = None
        else:
            remove = True
            old_commander = self.commander
        self.commander = commander
        log.debug("Commander has been set")
        if self.main_window is None:
            # Needs to be raised, because event methods can not be set if the
            # main window crashed. If this is raised, the program will terminate
            raise InitializeException("Could not initialize main window")
        else:
            if remove:
                self.main_window.remove_subscriber_for_start_event(old_commander.start_thread)
                self.main_window.remove_subscriber_for_stop_event(old_commander.stop)
                self.main_window.remove_subscriber_for_continue_event(old_commander.cont_thread)
            self.main_window.add_subscriber_for_start_event(self.commander.start_thread)
            self.main_window.add_subscriber_for_stop_event(self.commander.stop)
            self.main_window.add_subscriber_for_continue_event(self.commander.cont_thread)

    def set_verified(self):
        """Signal to verify. Is passed onto the GUI"""
        self.verified = True
        self.main_window.verified = True


def resize_and_normalize(array):
    """Resizing a passed image array and normalizing it using min-max-normalization"""
    image_array_resized = cv2.resize(array, (DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT))
    result_array = np.zeros((DEFAULT_IMAGE_HEIGHT, DEFAULT_IMAGE_WIDTH))
    # Normalizing is necessary due to the poor yield of the camera
    normalized_array = cv2.normalize(image_array_resized, result_array, 0,
                                     DEFAULT_IMAGE_MAX_PIXEL_VALUE, cv2.NORM_MINMAX)
    return normalized_array


def convert_array_to_pixmap(array):
    """Convert an array to a QPixmap"""
    height, width = array.shape
    q_img = QImage(array.data, width, height, DEFAULT_IMAGE_TYPE)
    pixmap = QPixmap(q_img)
    return pixmap
