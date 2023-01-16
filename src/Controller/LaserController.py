import serial
import time
import logging

log = logging.getLogger("log")

"""
"""


class LaserController:

    command_list = None

    def __init__(self, setup):
        self.serial_connection = serial.Serial(
            port=setup.serial_laser_port,
            baudrate=setup.serial_laser_baudrate,
            parity=setup.serial_laser_parity,
            stopbits=setup.serial_laser_stopbits,
            bytesize=setup.serial_laser_bytesize,
            timeout=setup.serial_laser_timeout
        )

        self.laser_power = setup.serial_laser_power
        self.laser_channel = setup.serial_laser_channel

    def set_commands_calib(self):
        # TODO respects analog modulation input
        self.command_list = ["ch " + str(self.laser_channel) + " pow " + str(self.laser_power) + "\r",
                             "en " + str(self.laser_channel) + "\r", "en ext\r", "la on\r"]

    def set_commands_run(self):
        self.command_list = ["ch " + str(self.laser_channel) + " pow " + str(self.laser_power) + "\r",
                             "en " + str(self.laser_channel) + "\r", "la on\r"]

    def stop_laser(self):
        try:
            self.send_command("la off\r")
        except Exception as ex:
            log.error(ex)
            raise ex
        finally:
            self.serial_connection.close()

    def arm_laser(self):
        try:
            for command in self.command_list:
                self.send_command(command)
        except Exception as ex:
            log.error(ex)
            raise ex

    def send_command(self, command):
        command_encoded = command.encode()
        self.serial_connection.write(command_encoded)
        time.sleep(0.5)

