import logging
import os

from util.Event import Event
from GUI.LogTextEdit import QTextEditLogger
from GUI.LogFormatter import CustomFormatter
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import *

DEFAULT_BUTTON_HEIGHT = 150
DEFAULT_BUTTON_WIDTH = 50
ICON_NAME = './resources/thebenlogo.jpg'
WINDOW_TITLE = "Theben: Main Window"
BACKGROUND_COLOR = "#F4A999"

log = logging.getLogger("log")
home_dir = os.path.expanduser("~/Desktop")


# noinspection PyUnresolvedReferences
class MainWindow(QWidget):
    """
    Main Window of the application.
    Features creating all widgets and creating Events
    for their use.
    """

    # If not verified the program will not start
    verified = False

    log_textbox = None
    image_widget = None
    # The actual image
    pixmap = None

    clear_button = None
    save_button = None
    continue_button = None
    start_button = None
    stop_button = None

    brightness_slider = None
    contrast_slider = None
    gamma_slider = None

    brightness_label = None
    contrast_label = None
    gamma_label = None

    # Path that is transferred from the File Dialog
    save_image_path = ""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QtGui.QIcon(ICON_NAME))
        self.setContentsMargins(10, 10, 10, 10)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")
        # The current picture from the camera
        self.image_widget = QLabel(self)
        self.init_layout()

        self.on_do_save = Event()
        self.on_do_continue = Event()
        self.on_do_start = Event()
        self.on_do_stop = Event()
        self.on_brightness_changed = Event()
        self.on_contrast_changed = Event()
        self.on_gamma_changed = Event()

        self.show()
        self.activateWindow()

    def init_layout(self):
        """Initializes the layout of the main window."""

        self.log_textbox = self.init_log_textbox()
        self.init_buttons()
        self.init_sliders()

        layout_outer = QVBoxLayout()
        upper = QHBoxLayout()
        lower = QHBoxLayout()
        button_box = QVBoxLayout()

        layout_outer.addLayout(upper)
        layout_outer.addLayout(lower)

        upper.addWidget(self.log_textbox.widget)
        lower.addWidget(self.image_widget)
        lower.addLayout(button_box)

        self.brightness_label = QLabel(self)
        self.brightness_label.setText('Brightness: ' + "0")
        self.contrast_label = QLabel(self)
        self.contrast_label.setText('Contrast: ' + "1")
        self.gamma_label = QLabel(self)
        self.gamma_label.setText('Gamma: ' + "1")

        button_box.addWidget(self.clear_button)
        button_box.addWidget(self.save_button)
        button_box.addWidget(self.continue_button)
        button_box.addWidget(self.brightness_label)
        button_box.addWidget(self.brightness_slider)
        button_box.addWidget(self.contrast_label)
        button_box.addWidget(self.contrast_slider)
        button_box.addWidget(self.gamma_label)
        button_box.addWidget(self.gamma_slider)
        button_box.addWidget(self.start_button)
        button_box.addWidget(self.stop_button)

        self.setLayout(layout_outer)

    def init_log_textbox(self):
        """Initializes the text box where logs are presented."""
        log_textbox = QTextEditLogger(self)
        log_textbox.setFormatter(CustomFormatter())
        log.addHandler(log_textbox)
        log.setLevel(logging.INFO)
        return log_textbox

    def show_image(self, image):
        """Shows the image in the image widget."""
        self.pixmap = image
        self.image_widget.setPixmap(self.pixmap)

    def init_buttons(self):
        """Initializes clear, save, continue, start and stop buttons."""
        button_size = QtCore.QSize(DEFAULT_BUTTON_HEIGHT, DEFAULT_BUTTON_WIDTH)
        self.clear_button = QPushButton("Clear")
        self.clear_button.setStyleSheet("background-color: gray")
        self.clear_button.setFixedSize(button_size)

        self.save_button = QPushButton("Save")
        self.save_button.setStyleSheet("background-color: violet")
        self.save_button.setFixedSize(button_size)

        self.continue_button = QPushButton("Continue")
        self.continue_button.setStyleSheet("background-color: blue")
        self.continue_button.setFixedSize(button_size)

        self.start_button = QPushButton("Start")
        self.start_button.setStyleSheet("background-color: green")
        self.start_button.setFixedSize(button_size)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet("background-color: red")
        self.stop_button.setFixedSize(button_size)
        self.init_button_clicked()

    def init_sliders(self):
        """Initializes brightness, contrast and gamma sliders."""
        self.brightness_slider = QSlider(QtCore.Qt.Orientation.Horizontal, self)
        self.brightness_slider.setMaximum(10000)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setTickInterval(100)
        self.brightness_slider.sliderReleased.connect(self.change_brightness)

        self.contrast_slider = QSlider(QtCore.Qt.Orientation.Horizontal, self)
        self.contrast_slider.setMaximum(3)
        self.contrast_slider.setMinimum(1)
        self.contrast_slider.sliderReleased.connect(self.change_contrast)

        self.gamma_slider = QSlider(QtCore.Qt.Orientation.Horizontal, self)
        self.gamma_slider.setMaximum(110)
        self.gamma_slider.setMinimum(90)
        self.gamma_slider.setValue(100)
        self.gamma_slider.sliderReleased.connect(self.change_gamma)

    def init_button_clicked(self):
        """Connect button pushes to the corresponding methods."""
        self.clear_button.clicked.connect(self.clear_log)
        self.save_button.clicked.connect(self.save_image)
        self.continue_button.clicked.connect(self.do_continue)
        self.start_button.clicked.connect(self.do_start)
        self.stop_button.clicked.connect(self.do_stop)

    def save_image(self):
        """Use OpenFileDialog to get an image path and call the save event."""
        file_name = QFileDialog.getSaveFileName(self, "Save File", home_dir)
        if file_name[0]:
            self.save_image_path = file_name[0]
            self.on_do_save()

    def do_continue(self):
        self.on_do_continue()

    def do_start(self):
        if self.verified:
            self.on_do_start()
        else:
            QMessageBox.information(self, "Data not verified", "The setup is not verified (yet)")

    def do_stop(self):
        self.on_do_stop()

    def change_brightness(self):
        self.on_brightness_changed()

    def change_contrast(self):
        self.on_contrast_changed()

    def change_gamma(self):
        self.on_gamma_changed()

    def clear_log(self):
        self.log_textbox.widget.clear()

    def get_pixmap(self):
        return self.pixmap

    def add_subscriber_for_start_event(self, obj_method):
        self.on_do_start += obj_method

    def remove_subscriber_for_start_event(self, obj_method):
        self.on_do_start -= obj_method

    def add_subscriber_for_stop_event(self, obj_method):
        self.on_do_stop += obj_method

    def remove_subscriber_for_stop_event(self, obj_method):
        self.on_do_stop -= obj_method

    def add_subscriber_for_continue_event(self, obj_method):
        self.on_do_continue += obj_method

    def remove_subscriber_for_continue_event(self, obj_method):
        self.on_do_continue -= obj_method

    def add_subscriber_for_save_event(self, obj_method):
        self.on_do_save += obj_method

    def add_subscriber_for_brightness_event(self, obj_method):
        self.on_brightness_changed += obj_method

    def add_subscriber_for_contrast_event(self, obj_method):
        self.on_contrast_changed += obj_method

    def add_subscriber_for_gamma_event(self, obj_method):
        self.on_gamma_changed += obj_method
