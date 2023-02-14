import logging

from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import *

from src.GUI.ConnectionConfigWindow import ConnectionConfigWindow

ICON_NAME = './resources/thebenlogo.jpg'
WINDOW_TITLE = "Theben: Setup Window"
BACKGROUND_COLOR = "#C4CEFF"
DEFAULT_BOX_HEIGHT = 30
DEFAULT_BOX_WIDTH = 300

log = logging.getLogger("log")

"""

"""


class SetupWindow(QWidget):

    # TODO tooltips for all
    hc_button = None
    laser_button = None
    button_box = None

    hc_window = None
    laser_window = None

    hc_1_box_list = None
    hc_1_label_list = None
    laser_box_list = None
    laser_label_list = None

    label_list = None
    box_list = None

    def __init__(self, path, setup):
        self.path = path
        self.setup = setup
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QtGui.QIcon(ICON_NAME))
        self.setContentsMargins(10, 10, 10, 10)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")
        self.init_layout()

    def init_layout(self):
        layout_form = QFormLayout()
        caption = QLabel(self)
        caption.setText("Configure the setup: ")
        caption.setFont(QtGui.QFont('Arial', 15))

        self.init_boxes()
        self.init_labels()
        self.init_buttons()

        hc_layout = QHBoxLayout()
        hc_layout.addWidget(self.box_list[0])
        hc_layout.addWidget(self.hc_button)
        hc_container = QWidget()
        hc_container.setLayout(hc_layout)

        laser_layout = QHBoxLayout()
        laser_layout.addWidget(self.box_list[1])
        laser_layout.addWidget(self.laser_button)
        laser_container = QWidget()
        laser_container.setLayout(laser_layout)

        layout_form.addRow(self.label_list[0], hc_container)
        layout_form.addRow(self.label_list[1], laser_container)

        for i in range(2, len(self.label_list)):
            layout_form.addRow(self.label_list[i], self.box_list[i])

        layout_buttons = QVBoxLayout()
        layout_buttons.addWidget(self.button_box)

        layout_outer = QVBoxLayout()
        layout_outer.addWidget(caption)
        layout_outer.addLayout(layout_form)
        layout_outer.addLayout(layout_buttons)

        self.setLayout(layout_outer)
        self.show()

    def init_boxes(self):
        box_size = QtCore.QSize(DEFAULT_BOX_WIDTH, DEFAULT_BOX_HEIGHT)

        hc_1_port_box = QTextEdit()
        laser_port_box = QTextEdit()

        hc_1_timeout_box = QTextEdit()
        hc_1_camera_trigger_pin_box = QTextEdit()
        hc_1_maxSteps_box = QTextEdit()
        hc_1_highPos_box = QTextEdit()
        hc_1_lowPos_box = QTextEdit()
        hc_1_picHeight_box = QTextEdit()
        hc_1_calibThreshold_box = QTextEdit()

        camera_exposure_time_box = QTextEdit()
        camera_exposure_lines_box = QTextEdit()
        camera_line_time_box = QTextEdit()

        laser_timeout_box = QTextEdit()
        laser_power_box = QTextEdit()

        hc_1_camera_trigger_mode_box = QComboBox()
        camera_trigger_mode_box = QComboBox()
        laser_channel_box = QComboBox()

        text_box_list = [hc_1_port_box, laser_port_box, hc_1_timeout_box, hc_1_camera_trigger_pin_box,
                         hc_1_maxSteps_box, hc_1_highPos_box, hc_1_lowPos_box,
                         hc_1_picHeight_box, hc_1_calibThreshold_box,
                         camera_exposure_time_box, camera_exposure_lines_box, camera_line_time_box,
                         laser_timeout_box, laser_power_box]

        combo_box_list = [hc_1_camera_trigger_mode_box, camera_trigger_mode_box, laser_channel_box]

        for text_box in text_box_list:
            text_box.setFixedSize(box_size)

        # TODO default reinladen

        """
        self.hc_1_port_box.setText("")
        self.hc_1_timeout_box.setText("")
        self.hc_1_camera_trigger_pin_box.setText("")
        self.hc_1_maxSteps_box.setText("")
        self.hc_1_highPos_box.setText("")
        self.hc_1_lowPos_box.setText("")
        self.hc_1_picHeight_box.setText("")
        self.hc_1_calibThreshold_box.setText("")
        self.camera_exposure_time_box.setText("")
        self.camera_line_time_box.setText("")
        self.camera_exposure_lines_box.setText("")
        self.camera_line_time_box.setText("")
        self.laser_port_box.setText("")
        self.laser_timeout_box.setText("")
        self.laser_power_box.setText("")
        """

        hc_1_camera_trigger_mode_box.addItems(["rising", "falling"])
        camera_trigger_mode_box.addItems(["rising", "falling"])
        laser_channel_box.addItems(["1", "2"])

        self.box_list = text_box_list + combo_box_list

        hc_1_baudrate_box = QComboBox()
        hc_1_parity_box = QComboBox()
        hc_1_stopbits_box = QComboBox()
        hc_1_bytesize_box = QComboBox()

        hc_1_baudrate_box.addItems(["rising", "falling"])
        hc_1_parity_box.addItems(["rising", "falling"])
        hc_1_stopbits_box.addItems(["1", "2"])
        hc_1_bytesize_box.addItems(["1", "2"])

        # TODO auslagern

        self.hc_1_box_list = [hc_1_baudrate_box, hc_1_parity_box,
                              hc_1_stopbits_box, hc_1_bytesize_box]



    def init_labels(self):
        hc_1_port_label = QLabel(self)
        hc_1_port_label.setText("Select hardware controller serial port: ")

        laser_port_label = QLabel(self)
        laser_port_label.setText("Select laser serial port")

        hc_1_timeout_label = QLabel(self)
        hc_1_timeout_label.setText("Select hardware controller timeout threshold in s: ")

        hc_1_camera_trigger_pin_label = QLabel(self)
        hc_1_camera_trigger_pin_label.setText("Select hardware controller pin to trigger camera: ")

        hc_1_maxSteps_label = QLabel(self)
        hc_1_maxSteps_label.setText("Select maximum calibration steps: ")

        hc_1_highPos_label = QLabel(self)
        hc_1_highPos_label.setText("Select highest DAC output position: ")

        hc_1_lowPos_label = QLabel(self)
        hc_1_lowPos_label.setText("Select lowest DAC output position: ")

        hc_1_picHeight_label = QLabel(self)
        hc_1_picHeight_label.setText("Select default result picture height in px: ")

        hc_1_calibThreshold_label = QLabel(self)
        hc_1_calibThreshold_label.setText("Select calibration maximum deviation in ms: ")

        camera_exposure_time_label = QLabel(self)
        camera_exposure_time_label.setText("Select camera exposure time for non lightsheet mode pictures in ms")

        camera_line_time_label = QLabel(self)
        camera_line_time_label.setText("Select camera line time in µs")

        camera_exposure_lines_label = QLabel(self)
        camera_exposure_lines_label.setText("Select camera exposure lines")

        laser_timeout_label = QLabel(self)
        laser_timeout_label.setText("Select laser timeout threshold in s: ")

        laser_power_label = QLabel(self)
        laser_power_label.setText("Select laser power: ")

        hc_1_camera_trigger_mode_label = QLabel(self)
        hc_1_camera_trigger_mode_label.setText("Select send camera trigger pulse polarity: ")

        camera_trigger_mode_label = QLabel(self)
        camera_trigger_mode_label.setText("Select received camera trigger pulse polarity: ")

        laser_channel_label = QLabel(self)
        laser_channel_label.setText("Select laser channel: ")

        self.label_list = [hc_1_port_label, hc_1_timeout_label, hc_1_camera_trigger_pin_label, hc_1_maxSteps_label,
                           hc_1_highPos_label, hc_1_lowPos_label, hc_1_picHeight_label, hc_1_calibThreshold_label,
                           camera_exposure_time_label, camera_line_time_label, camera_exposure_lines_label,
                           laser_port_label, laser_timeout_label, laser_power_label,
                           hc_1_camera_trigger_mode_label, camera_trigger_mode_label, laser_channel_label]

        hc_1_baudrate_label = QLabel(self)
        hc_1_parity_label = QLabel(self)
        hc_1_stopbits_label = QLabel(self)
        hc_1_bytesize_label = QLabel(self)
        # TODO auslagern
        hc_1_baudrate_label.setText("Select baudrate: ")
        hc_1_parity_label.setText("Select parity: ")
        hc_1_stopbits_label.setText("Select stopbits: ")
        hc_1_bytesize_label.setText("Select bytesize: ")

        self.hc_1_label_list = [hc_1_baudrate_label, hc_1_parity_label,
                                hc_1_stopbits_label, hc_1_bytesize_label]

    def init_buttons(self):
        self.hc_button = QPushButton("More")
        self.hc_button.clicked.connect(self.show_hc_boxes)

        self.laser_button = QPushButton("More")
        self.laser_button.clicked.connect(self.n)

        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.n)
        self.button_box.rejected.connect(self.close)

    def n(self):
        pass
    # TODO abspeichern im setup

    def show_hc_boxes(self):
        title_text = "Theben: Hardware controller connection window"
        caption_text = "Configure connection for hardware controller: "
        sub_caption_text = "Warning: Connection will not be adjusted in the hardware controller " \
                           "settings. Changing these values can result in a broken connection!"
        self.hc_window = ConnectionConfigWindow(self.hc_1_box_list, self.hc_1_label_list, title_text,
                                                caption_text, sub_caption_text)
        self.hc_window.show()
     # TODO für laser wiederholen











