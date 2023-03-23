import logging

from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import *
from GUI.ConnectionConfigWindow import ConnectionConfigWindow
from util.FileLoader import *


log = logging.getLogger("log")


ICON_NAME = './resources/thebenlogo.jpg'
WINDOW_TITLE = "Theben: Setup Window"
BACKGROUND_COLOR = "#C4CEFF"
DEFAULT_BOX_HEIGHT = 30
DEFAULT_BOX_WIDTH = 300
BAUD_RATES = ["75", "300", "1200", "2400", "4800", "9600", "14400", "19200", "28800",
              "38400", "57600", "115200"]
PARITIES = ["NONE", "ODD", "EVEN", "MARK", "SPACE"]
STOP_BITS = ["ONE", "ONE_POINT_FIVE", "TWO"]
BYTE_SIZE = ["FIVEBITS", "SIXBITS", "SEVENBITS", "EIGHTBITS"]
VAR_NAMES = ["serial_hc_1_port",
             "serial_hc_1_timeout",
             "serial_hc_1_camera_trigger_pin",
             "serial_hc_1_maxSteps",
             "serial_hc_1_highPos",
             "serial_hc_1_lowPos",
             "serial_hc_1_picHeight",
             "serial_hc_1_calibThreshold",
             "serial_camera_exposure_time",
             "serial_camera_line_time",
             "serial_camera_exposure_lines",
             "serial_laser_port",
             "serial_laser_timeout",
             "serial_laser_power",
             "serial_hc_1_camera_trigger_curve_mode",
             "serial_camera_trigger_curve_mode",
             "serial_laser_channel",
             "serial_hc_1_baudrate",
             "serial_hc_1_parity",
             "serial_hc_1_stopbits",
             "serial_hc_1_bytesize",
             "serial_laser_baudrate",
             "serial_laser_parity",
             "serial_laser_stopbits",
             "serial_laser_bytesize"]

# First lines in the setup that are not used
INITIAL_SETUP_SPACE = 2


# noinspection PyUnresolvedReferences
class SetupWindow(QWidget):

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

    lines = None
    start_hc = 0
    start_laser = 0

    def __init__(self, path, setup):
        self.path = path
        self.setup = setup
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QtGui.QIcon(ICON_NAME))
        self.setContentsMargins(10, 10, 10, 10)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")
        self.init_layout()
        self.create_hc_1_connection_widgets()
        self.create_laser_connection_widgets()
        self.load(self.setup)
        self.show()
        self.activateWindow()

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

    def init_boxes(self):
        box_size = QtCore.QSize(DEFAULT_BOX_WIDTH, DEFAULT_BOX_HEIGHT)

        hc_1_port_box = QTextEdit()
        laser_port_box = QTextEdit()
        hc_1_timeout_box = QTextEdit()
        hc_1_camera_trigger_pin_box = QTextEdit()
        hc_1_max_steps_box = QTextEdit()
        hc_1_high_pos_box = QTextEdit()
        hc_1_low_pos_box = QTextEdit()
        hc_1_pic_height_box = QTextEdit()
        hc_1_calib_threshold_box = QTextEdit()

        camera_exposure_time_box = QTextEdit()
        camera_exposure_lines_box = QTextEdit()
        camera_line_time_box = QTextEdit()

        laser_timeout_box = QTextEdit()
        laser_power_box = QTextEdit()

        hc_1_camera_trigger_mode_box = QComboBox()
        camera_trigger_mode_box = QComboBox()
        laser_channel_box = QComboBox()

        text_box_list = [hc_1_port_box, laser_port_box, hc_1_timeout_box, hc_1_camera_trigger_pin_box,
                         hc_1_max_steps_box, hc_1_high_pos_box, hc_1_low_pos_box,
                         hc_1_pic_height_box, hc_1_calib_threshold_box,
                         camera_exposure_time_box, camera_exposure_lines_box, camera_line_time_box,
                         laser_timeout_box, laser_power_box]

        combo_box_list = [hc_1_camera_trigger_mode_box, camera_trigger_mode_box, laser_channel_box]

        for text_box in text_box_list:
            text_box.setFixedSize(box_size)

        hc_1_camera_trigger_mode_box.addItems(["rising", "falling"])
        camera_trigger_mode_box.addItems(["rising", "falling"])
        laser_channel_box.addItems(["1", "2"])

        self.box_list = text_box_list + combo_box_list

    def init_labels(self):
        hc_1_port_label = QLabel(self)
        hc_1_port_label.setText("Select hardware controller serial port: ")

        laser_port_label = QLabel(self)
        laser_port_label.setText("Select laser serial port: ")

        hc_1_timeout_label = QLabel(self)
        hc_1_timeout_label.setText("Select hardware controller timeout threshold in s: ")

        hc_1_camera_trigger_pin_label = QLabel(self)
        hc_1_camera_trigger_pin_label.setText("Select hardware controller pin to trigger camera: ")

        hc_1_max_steps_label = QLabel(self)
        hc_1_max_steps_label.setText("Select maximum calibration steps: ")

        hc_1_high_pos_label = QLabel(self)
        hc_1_high_pos_label.setText("Select highest DAC output position: ")

        hc_1_low_pos_label = QLabel(self)
        hc_1_low_pos_label.setText("Select lowest DAC output position: ")

        hc_1_pic_height_label = QLabel(self)
        hc_1_pic_height_label.setText("Select default result picture height in px: ")

        hc_1_calib_threshold_label = QLabel(self)
        hc_1_calib_threshold_label.setText("Select calibration maximum deviation in µs: ")

        camera_exposure_time_label = QLabel(self)
        camera_exposure_time_label.setText("Select camera exposure time for non lightsheet mode pictures in ms: ")

        camera_line_time_label = QLabel(self)
        camera_line_time_label.setText("Select camera line time in µs: ")

        camera_exposure_lines_label = QLabel(self)
        camera_exposure_lines_label.setText("Select camera exposure lines: ")

        laser_timeout_label = QLabel(self)
        laser_timeout_label.setText("Select laser timeout threshold in s: ")

        laser_power_label = QLabel(self)
        laser_power_label.setText("Select laser power in mW: ")

        hc_1_camera_trigger_mode_label = QLabel(self)
        hc_1_camera_trigger_mode_label.setText("Select send camera trigger pulse polarity: ")

        camera_trigger_mode_label = QLabel(self)
        camera_trigger_mode_label.setText("Select received camera trigger pulse polarity: ")

        laser_channel_label = QLabel(self)
        laser_channel_label.setText("Select laser channel: ")

        self.label_list = [hc_1_port_label, hc_1_timeout_label, hc_1_camera_trigger_pin_label, hc_1_max_steps_label,
                           hc_1_high_pos_label, hc_1_low_pos_label, hc_1_pic_height_label, hc_1_calib_threshold_label,
                           camera_exposure_time_label, camera_line_time_label, camera_exposure_lines_label,
                           laser_port_label, laser_timeout_label, laser_power_label,
                           hc_1_camera_trigger_mode_label, camera_trigger_mode_label, laser_channel_label]

    def create_hc_1_connection_widgets(self):
        hc_1_baudrate_label = QLabel(self)
        hc_1_parity_label = QLabel(self)
        hc_1_stopbits_label = QLabel(self)
        hc_1_bytesize_label = QLabel(self)

        hc_1_baudrate_label.setText("Select baudrate: ")
        hc_1_parity_label.setText("Select parity: ")
        hc_1_stopbits_label.setText("Select stopbits: ")
        hc_1_bytesize_label.setText("Select bytesize: ")

        self.hc_1_label_list = [hc_1_baudrate_label, hc_1_parity_label,
                                hc_1_stopbits_label, hc_1_bytesize_label]

        hc_1_baudrate_box = QComboBox()
        hc_1_parity_box = QComboBox()
        hc_1_stopbits_box = QComboBox()
        hc_1_bytesize_box = QComboBox()

        hc_1_baudrate_box.addItems(BAUD_RATES)
        hc_1_parity_box.addItems(PARITIES)
        hc_1_stopbits_box.addItems(STOP_BITS)
        hc_1_bytesize_box.addItems(BYTE_SIZE)

        self.hc_1_box_list = [hc_1_baudrate_box, hc_1_parity_box,
                              hc_1_stopbits_box, hc_1_bytesize_box]

    def create_laser_connection_widgets(self):
        laser_baudrate_label = QLabel(self)
        laser_parity_label = QLabel(self)
        laser_stopbits_label = QLabel(self)
        laser_bytesize_label = QLabel(self)

        laser_baudrate_label.setText("Select baudrate: ")
        laser_parity_label.setText("Select parity: ")
        laser_stopbits_label.setText("Select stopbits: ")
        laser_bytesize_label.setText("Select bytesize: ")

        self.laser_label_list = [laser_baudrate_label, laser_parity_label,
                                 laser_stopbits_label, laser_bytesize_label]

        laser_baudrate_box = QComboBox()
        laser_parity_box = QComboBox()
        laser_stopbits_box = QComboBox()
        laser_bytesize_box = QComboBox()

        laser_baudrate_box.addItems(BAUD_RATES)
        laser_parity_box.addItems(PARITIES)
        laser_stopbits_box.addItems(STOP_BITS)
        laser_bytesize_box.addItems(BYTE_SIZE)

        self.laser_box_list = [laser_baudrate_box, laser_parity_box,
                               laser_stopbits_box, laser_bytesize_box]

    def init_buttons(self):
        self.hc_button = QPushButton("More")
        self.hc_button.setToolTip("Configure connection")
        self.hc_button.clicked.connect(self.show_hc_boxes)

        self.laser_button = QPushButton("More")
        self.laser_button.setToolTip("Configure connection")
        self.laser_button.clicked.connect(self.show_laser_boxes)

        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.save)
        self.button_box.rejected.connect(self.close)

    def load(self, setup):
        self.lines = setup.split('\n')
        self.start_hc = load_part(self.lines, INITIAL_SETUP_SPACE, self.box_list)
        self.start_laser = load_part(self.lines, self.start_hc, self.hc_1_box_list)
        load_part(self.lines, self.start_laser, self.laser_box_list)

    def save(self):
        text = "import serial\n\n"
        self.box_list.extend(self.hc_1_box_list)
        self.box_list.extend(self.laser_box_list)
        boxes = self.box_list
        string_matches = ["port", "trigger_pin", "maxSteps", "highPos", "lowPos", "picHeight", "calibThreshold",
                          "curve_mode"]
        special_matches = ["parity", "stopbits", "bytesize"]
        if len(boxes) != len(VAR_NAMES):
            self.close()
            raise Exception("Cannot save file, because the nuber of vars is different to the"
                            " number of actual input boxes")
        else:
            for i in range(0, len(VAR_NAMES)):
                var = VAR_NAMES[i]
                box = boxes[i]
                if "baudrate" in var:
                    text += '\n'
                content = ''
                if type(box) == QTextEdit:
                    content += box.toPlainText()
                elif type(box) == QComboBox:
                    if any([x in var for x in special_matches]):
                        content = "serial."
                        if "parity" in var:
                            content += "PARITY_"
                            content += box.currentText()
                        if "stopbits" in var:
                            content += "STOPBITS_"
                            content += box.currentText()
                        if "bytesize" in var:
                            content += box.currentText()
                    else:
                        content += box.currentText()

                if any([x in var for x in string_matches]):
                    temp = var + " = " + "\"" + content + "\"" + '\r'
                    text += temp
                else:
                    temp = var + " = " + content + '\r'
                    text += temp
        save(self.path, text)
        self.close()

    def show_hc_boxes(self):
        title_text = "Theben: Hardware Controller Connection Window"
        caption_text = "Configure connection for hardware controller: "
        sub_caption_text = "Warning: Connection will not be adjusted in the hardware controller " \
                           "settings. Changing these values can result in a broken connection!"
        self.hc_window = ConnectionConfigWindow(self.hc_1_box_list, self.hc_1_label_list, title_text,
                                                caption_text, sub_caption_text, self)

    def show_laser_boxes(self):
        title_text = "Theben: Laser Connection Window"
        caption_text = "Configure connection for laser: "
        sub_caption_text = "Warning: Connection will not be adjusted in the laser " \
                           "settings. Changing these values can result in a broken connection!"
        self.laser_window = ConnectionConfigWindow(self.laser_box_list, self.laser_label_list, title_text,
                                                   caption_text, sub_caption_text, self)

    def reject(self, window):
        if window == 'laser':
            self.laser_window.close()
            load_part(self.lines, self.start_laser, self.laser_box_list)
        elif window == 'hc':
            self.hc_window.close()
            load_part(self.lines, self.start_hc, self.hc_1_box_list)


def load_part(lines, start_line, obj_list):
    for i in range(start_line, start_line + len(obj_list)):
        if lines[i] == "":
            return i + 1
        value = ((lines[i].split(' = '))[1]).replace('"', '')
        if value.startswith('serial'):
            value = ((value.split('serial.'))[1])
            if '_' in value:
                value = ((value.split('_'))[1])
        box = obj_list[i - start_line]
        if type(box) == QTextEdit:
            box.setText(value)
        elif type(box) == QComboBox:
            index = box.findText(value)
            if index != -1:
                box.setCurrentIndex(index)
    return start_line + len(obj_list) + 1




