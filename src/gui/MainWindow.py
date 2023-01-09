import logging
import os
from util.Event import Event
from gui.LogTextEdit import QTextEditLogger
from gui.LogFormatter import CustomFormatter
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import *

DEFAULT_BUTTON_HEIGHT = 150
DEFAULT_BUTTON_WIDTH = 50
FIRST_IMAGE_NAME = 'theben.jpg'
ICON_NAME = 'thebenlogo.jpg'
WINDOW_TITLE = "Theben: Main Window"
BACKGROUND_COLOR = "#F4A999"

log = logging.getLogger("log")
home_dir = os.path.expanduser("~/Desktop")

"""
"""


class MainWindow(QWidget):

    log_textbox = None
    image = None
    pixmap = None

    clear_button = None
    save_button = None
    continue_button = None
    start_button = None
    stop_button = None

    save_image_path = ""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QtGui.QIcon(ICON_NAME))
        self.setContentsMargins(10, 10, 10, 10)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")
        self.init_layout()
        self.on_do_save = Event()
        self.on_do_continue = Event()
        self.on_do_start = Event()
        self.on_do_stop = Event()

    def init_layout(self):
        self.log_textbox = self.init_log_textbox()
        self.image = self.init_image()
        self.init_buttons()

        layout_outer = QVBoxLayout()
        upper = QHBoxLayout()
        lower = QHBoxLayout()
        button_box = QGridLayout()

        layout_outer.addLayout(upper)
        layout_outer.addLayout(lower)

        upper.addWidget(self.log_textbox.widget)
        lower.addWidget(self.image)
        lower.addLayout(button_box)

        button_box.addWidget(self.clear_button, 0, 0, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        button_box.addWidget(self.save_button, 1, 0, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        button_box.addWidget(self.continue_button, 2, 0, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        button_box.addWidget(self.start_button, 3, 0, alignment=QtCore.Qt.AlignmentFlag.AlignBottom)
        button_box.addWidget(self.stop_button, 4, 0, alignment=QtCore.Qt.AlignmentFlag.AlignBottom)
        button_box.setRowStretch(2, 1)

        self.setLayout(layout_outer)
        self.show()

    def init_log_textbox(self):
        log_textbox = QTextEditLogger(self)
        log_textbox.setFormatter(CustomFormatter())
        log.addHandler(log_textbox)
        log.setLevel(logging.DEBUG)
        return log_textbox

    def init_image(self):
        self.image = QLabel(self)
        self.pixmap = QtGui.QPixmap(FIRST_IMAGE_NAME)
        self.image.setPixmap(self.pixmap)
        return self.image

    def init_buttons(self):
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

    def init_button_clicked(self):
        self.clear_button.clicked.connect(self.clear_log)
        self.save_button.clicked.connect(self.save_image)
        self.continue_button.clicked.connect(self.do_continue)
        self.start_button.clicked.connect(self.do_start)
        self.stop_button.clicked.connect(self.do_stop)

    def save_image(self):
        file_name = QFileDialog.getSaveFileName(self, "Save File", home_dir)
        if file_name[0]:
            self.save_image_path = file_name[0]
            self.on_do_save()

    def do_continue(self):
        self.on_do_continue()

    def do_start(self):
        self.on_do_start()

    def do_stop(self):
        self.on_do_stop()

    def update_image(self):
        pass

    def clear_log(self):
        self.log_textbox.widget.clear()

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

    def remove_subscriber_for_save_event(self, obj_method):
        self.on_do_save -= obj_method

    def get_pixmap(self):
        return self.pixmap
