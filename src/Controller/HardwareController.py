import serial
import time
import logging

from src.Exceptions.FailedCommunicationException import FailedCommunicationException
from src.Exceptions.TimeoutException import TimeoutException

log = logging.getLogger("log")

EXIT_COMMAND = '4'


class HardwareController:

    command_list = None

    def __init__(self, setup, param):
        self.setup = setup
        self.param = param
        self.serial_connection = serial.Serial(
            port=setup.serial_hc_1_port,
            baudrate=setup.serial_hc_1_baudrate,
            parity=setup.serial_hc_1_parity,
            stopbits=setup.serial_hc_1_stopbits,
            bytesize=setup.serial_hc_1_bytesize,
            timeout=setup.serial_hc_1_timeout
        )
        self.state = 0
        # Wait for the hardware controller to finish its setup
        time.sleep(2)

    def init_hc(self):
        """Establish a connection to the hardware controller and verify its program"""
        try:
            self.send_command(str(self.state))
            answer = self.get_single_command()
        except Exception:
            raise FailedCommunicationException("HC invalid, probably wrong .ino loaded")
        # Program name (Theben) is default answer in basic state (0)
        if answer == 'Theben\r\n':
            self.state = 1
            log.info("Hardware controller connection established. HC is valid.")
        # The hardware controller has the wrong program or is in a different state
        else:
            raise FailedCommunicationException("HC invalid, probably wrong .ino loaded")

    def set_commands(self, setup, param, mode):
        """
        Set the commands that are transferred to the hardware controller containing all
        variables which the hardware controller needs to run
        :param setup: The loaded setup containing static variables
        :param param: The loaded parameter containing runtime variables in running or None in calibration mode
        :param mode: The current mode, indication running (2) or calibration (3) mode
        """
        # Encode trigger_curve_mode into single digit integers
        if setup.serial_hc_1_camera_trigger_curve_mode == "rising":
            cam_trigger_curve_mode = '1'
        else:
            cam_trigger_curve_mode = '2'

        # Calculate lengths of variables with variable lengths
        line_time_length = len(str(setup.serial_camera_line_time))
        exp_lines_length = len(str(setup.serial_camera_exposure_lines))
        pic_height_length = len(setup.serial_hc_1_picHeight)
        calib_threshold_length = len(setup.serial_hc_1_calibThreshold)
        max_steps_length = len(setup.serial_hc_1_maxSteps)

        self.command_list = [str(self.state), mode, setup.serial_hc_1_camera_trigger_pin, cam_trigger_curve_mode,
                             setup.serial_hc_1_highPos, setup.serial_hc_1_lowPos,
                             str(line_time_length), str(setup.serial_camera_line_time),
                             str(exp_lines_length), str(setup.serial_camera_exposure_lines),
                             str(pic_height_length), setup.serial_hc_1_picHeight,
                             str(calib_threshold_length), setup.serial_hc_1_calibThreshold,
                             str(max_steps_length), setup.serial_hc_1_maxSteps]

        # Add additional runtime variables in running mode
        if mode == '2':
            roi = int(param.serial_hc_1_maxPicPos) - int(param.serial_hc_1_minPicPos)
            roi_length = len(str(roi))
            t_trig_length = len(str(param.tTrig))
            t_final_length = len(str(param.tFinal))
            self.command_list.extend([param.serial_hc_1_maxPicPos, param.serial_hc_1_minPicPos,
                                      str(roi_length), str(roi),
                                      str(t_trig_length), str(param.tTrig), str(t_final_length), str(param.tFinal)])

    def get_single_command(self):
        """
        Get an answer from the hardware controller
        :return: The decoded answer from the hardware controller
        :raise: TimeoutException if the hardware controller exceeds the time limit
        """
        timer = time.time()
        while True:
            if self.serial_connection.in_waiting:
                answer = (self.serial_connection.readline()).decode("ascii")
                break
            cur_time = time.time() - timer
            # Check if time to answer extends timeout limit
            if cur_time >= self.serial_connection.timeout:
                raise TimeoutException("No answer from hardware controller")
            time.sleep(0.5)
        return answer

    def transmit_commands(self):
        """Transmit all commands from the command list to the hardware controller"""
        try:
            log.info("Transmitting variables to hardware controller")
            for command in self.command_list:
                self.send_command(command)
            answer = self.get_single_command()
            # Handshake after every sent command
            if answer != 'received\r\n':
                raise TimeoutException("No answer from hardware controller")
            else:
                self.state = 2
        except Exception as ex:
            log.error(ex)
            # Reset state
            self.state = 0

    def send_and_receive(self, command):
        """Sends the command and receives an answer"""
        try:
            self.send_command(command)
            answer = self.get_single_command()
            log.debug(answer)
            # Handshake not valid
            if answer != 'received\r\n':
                raise TimeoutException("No answer from hardware controller")
        except Exception as ex:
            log.error(ex)
            self.state = 0

    def stop(self):
        """Stops the hardware controller. Resets the state and closes the connection"""
        log.debug("Stopping hardware controller")
        try:
            self.send_command(EXIT_COMMAND)
        except FailedCommunicationException as ex:
            # Other circumstances already lead to a closed connection
            log.warning("Connection was already closed, communication corrupted")
            log.error(ex)
        finally:
            self.state = 0
            self.serial_connection.close()

    def send_command(self, command):
        """Encodes a command and sends it to the hardware controller via serial connection"""
        command_encoded = command.encode()
        if self.serial_connection.is_open:
            self.serial_connection.write(command_encoded)
        else:
            raise FailedCommunicationException("could not send to " + self.serial_connection.name)
        # Time for the hardware controller to distinguish between the commands
        time.sleep(0.2)
