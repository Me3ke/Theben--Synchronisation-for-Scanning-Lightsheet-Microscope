import serial

# Laser data
serial_laser_port = "COM12"
serial_laser_baudrate = 115200
serial_laser_parity = serial.PARITY_NONE
serial_laser_stopbits = serial.STOPBITS_ONE
serial_laser_bytesize = serial.EIGHTBITS
serial_laser_timeout = 2
serial_laser_channel = 2
serial_laser_power = 1

# Hardware controller 2 data (Galvo HC)
serial_hc_2_port = "COM10"
serial_hc_2_baudrate = 9600
serial_hc_2_parity = serial.PARITY_NONE
serial_hc_2_stopbits = serial.STOPBITS_ONE
serial_hc_2_bytesize = serial.EIGHTBITS
serial_hc_2_timeout = 2
serial_hc_2_trigger_curve_mode = "rising"
serial_hc_2_trigger_pin_in = 4
serial_hc_2_camera_trigger_pin = 2
serial_hc_2_camera_trigger_curve_mode = "rising"

# Camera data
serial_camera_trigger_curve_mode = "rising"
serial_camera_trigger_mode = "external exposure start & software trigger"
