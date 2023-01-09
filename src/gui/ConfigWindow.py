import logging
import os
from util.Event import Event
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import *

ICON_NAME = 'thebenlogo.jpg'
WINDOW_TITLE = "Theben: Config Window"
BACKGROUND_COLOR = "#C4CEFF"
DEFAULT_BOX_HEIGHT = 35
DEFAULT_BOX_WIDTH = 300

log = logging.getLogger("log")
home_dir = os.path.expanduser("~/Desktop")


class ConfigWindow(QDialog):

    mode_box = None
    sequence_box = None
    setup_box = None
    param_box = None

    setup_button = None
    param_button = None
    button_box = None

    mode = ""
    sequence = ""
    setup_path = ""
    param_path = ""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QtGui.QIcon(ICON_NAME))
        self.setContentsMargins(10, 10, 10, 10)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")
        self.init_layout()
        self.on_finished_check = Event()

    def init_layout(self):
        self.init_widgets()
        self.init_buttons()

        mode_label = QLabel(self)
        mode_label.setText("Select mode: ")
        sequence_label = QLabel(self)
        sequence_label.setText("Select sequence: ")
        setup_label = QLabel(self)
        setup_label.setText("Select path to setup file: ")
        param_label = QLabel(self)
        param_label.setText("Select path to parameter file: ")

        setup_layout = QHBoxLayout()
        setup_layout.addWidget(self.setup_box)
        setup_layout.addWidget(self.setup_button)
        setup_container = QWidget()
        setup_container.setLayout(setup_layout)

        param_layout = QHBoxLayout()
        param_layout.addWidget(self.param_box)
        param_layout.addWidget(self.param_button)
        param_container = QWidget()
        param_container.setLayout(param_layout)

        layout_form = QFormLayout()
        layout_form.addRow(mode_label, self.mode_box)
        layout_form.addRow(sequence_label, self.sequence_box)
        layout_form.addRow(setup_label, setup_container)
        layout_form.addRow(param_label, param_container)

        layout_buttons = QVBoxLayout()
        layout_buttons.addWidget(self.button_box)
        layout_outer = QVBoxLayout()
        layout_outer.addLayout(layout_form)
        layout_outer.addLayout(layout_buttons)

        self.setLayout(layout_outer)
        self.show()

    def init_buttons(self):
        self.setup_button = QPushButton("Browse")
        self.setup_button.clicked.connect(lambda: self.browse(self.setup_box))

        self.param_button = QPushButton("Browse")
        self.param_button.clicked.connect(lambda: self.browse(self.param_box))

        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.check)
        self.button_box.rejected.connect(self.close)

    def init_widgets(self):
        box_size = QtCore.QSize(DEFAULT_BOX_WIDTH, DEFAULT_BOX_HEIGHT)
        self.mode_box = QComboBox()
        self.mode_box.addItems(["running", "calibration"])

        self.sequence_box = QComboBox()
        self.sequence_box.addItems(["continuous", "iterative"])

        self.setup_box = QTextEdit()
        self.setup_box.setFixedSize(box_size)
        self.setup_box.setObjectName('setup')

        self.param_box = QTextEdit()
        self.param_box.setFixedSize(box_size)
        self.param_box.setObjectName('param')

    def browse(self, target):
        file_name = QFileDialog.getOpenFileName(self, "Open File", home_dir)
        if file_name[0]:
            target.setText(file_name[0])

    def check(self):
        self.mode = self.mode_box.currentText()
        self.sequence = self.sequence_box.currentText()
        self.setup_path = self.setup_box.toPlainText()
        self.param_path = self.param_box.toPlainText()
        if self.mode == "running" and self.sequence == "iterative":
            self.show_message_box("Running mode cannot be run with iterative sequence")
        elif not os.path.exists(self.setup_path):
            self.show_message_box("Setup file path not found")
        elif not os.path.exists(self.param_path):
            self.show_message_box("Parameter file path not found")
        else:
            self.on_finished_check()

    def show_message_box(self, text):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setText(text)
        msg_box.setWindowTitle("Error in data processing")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.buttonClicked.connect(msg_box.close)
        msg_box.exec()

    def add_subscriber_for_finished_check_event(self, obj_method):
        self.on_finished_check += obj_method

    def remove_subscriber_for_finished_check_event(self, obj_method):
        self.on_finished_check -= obj_method
