import serial

# Hardware controller 1 data
serial_hc_1_port = "COM10"
serial_hc_1_baudrate = 9600
serial_hc_1_parity = serial.PARITY_NONE
serial_hc_1_stopbits = serial.STOPBITS_ONE
serial_hc_1_bytesize = serial.EIGHTBITS
serial_hc_1_timeout = 5
serial_hc_1_camera_trigger_pin = "2"
serial_hc_1_camera_trigger_curve_mode = "rising"
serial_hc_1_maxSteps = "30"
serial_hc_1_highPos = "4000"
serial_hc_1_midPos = "1950"
serial_hc_1_lowPos = "0100"
serial_hc_1_maxPicPos = "3400"
serial_hc_1_minPicPos = "0400"
serial_hc_1_picHeight = "2048"
serial_hc_1_calibThreshold = "1500"

# Camera data
serial_camera_trigger_curve_mode = "rising"
serial_camera_trigger_mode = "external exposure start & software trigger"
serial_camera_exposure_time = 200
serial_camera_line_time = 200
serial_camera_exposure_lines = 50

# Laser data
serial_laser_port = "COM12"
serial_laser_baudrate = 115200
serial_laser_parity = serial.PARITY_NONE
serial_laser_stopbits = serial.STOPBITS_ONE
serial_laser_bytesize = serial.EIGHTBITS
serial_laser_timeout = 2
serial_laser_channel = 2
serial_laser_power = 3




