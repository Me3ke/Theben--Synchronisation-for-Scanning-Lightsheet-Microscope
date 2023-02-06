import serial
import time
import logging

log = logging.getLogger("log")

"""
"""


class HardwareController:

    def __init__(self, setup):
        self.serial_connection = serial.Serial(
            port=setup.serial_hc_2_port,
            baudrate=setup.serial_hc_2_baudrate,
            #parity=setup.serial_hc_2_parity,
            #stopbits=setup.serial_hc_2_stopbits,
            #bytesize=setup.serial_hc_2_bytesize,
            #timeout=setup.serial_hc_2_timeout
        )
        #setup.serial_hc_2_trigger_curve_mode = "rising"
        #setup.serial_hc_2_trigger_pin_in = 4
        #setup.serial_hc_2_camera_trigger_pin = 2
        #setup.serial_hc_2_camera_trigger_curve_mode = "rising"
        time.sleep(4) #needs to wait for setup
        status = ""
        #self.send_command('1')
        #time.sleep(3)
        #self.send_command("3400")
        log.warning(status)
        print(status)
        #if status != "Theben1":
        #    # TODO custom exception
        #   raise Exception("not received")

    def set_commands_running(self):
        try:
            time.sleep(2)
            self.send_command('3')
        except Exception as ex:
            log.error(ex)
            self.stop_hc()


    def stop_hc(self):
        log.info("stopping hc")
        self.serial_connection.close()

    def send_command(self, command):
        command_encoded = command.encode()
        if self.serial_connection.is_open:
            self.serial_connection.write(command_encoded)
        else:
            raise Exception("could not send")
            # TODO custom exception
        time.sleep(0.5)
