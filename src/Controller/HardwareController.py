import serial
import time
import logging

log = logging.getLogger("log")

"""
"""


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
            timeout= 10 #setup.serial_hc_1_timeout
        )
        self.state = 0
        time.sleep(2)

    def init_hc(self):
        self.send_command(str(self.state))
        answer = self.get_single_command()
        if answer == 'Theben\r\n':
            self.state = 1
            log.info("Hardware controller connection established. HC is valid.")
        else:
            # TODO custom exception
            raise Exception("HC invalid")

    def set_commands(self, setup, param, mode):
        if setup.serial_hc_1_camera_trigger_curve_mode == "rising":
            cam_trigger_curve_mode = '1'
        else:
            cam_trigger_curve_mode = '2'
        roi = int(setup.serial_hc_1_maxPicPos) - int(setup.serial_hc_1_minPicPos)
        roi_length = len(str(roi))
        line_time_length = len(str(setup.serial_camera_line_time))
        exp_lines_length = len(str(setup.serial_camera_exposure_lines))
        pic_height_length = len(setup.serial_hc_1_picHeight)
        calib_threshold_length = len(setup.serial_hc_1_calibThreshold)
        max_steps_length = len(setup.serial_hc_1_maxSteps)

        # if mode is '2' (running)
        t_trig_length = len(str(param.tTrig))
        t_final_length = len(str(param.tFinal))

        self.command_list = [str(self.state), mode, setup.serial_hc_1_camera_trigger_pin, cam_trigger_curve_mode,
                             setup.serial_hc_1_midPos, setup.serial_hc_1_highPos, setup.serial_hc_1_lowPos,
                             setup.serial_hc_1_maxPicPos, setup.serial_hc_1_minPicPos, str(roi_length), str(roi),
                             str(line_time_length), str(setup.serial_camera_line_time),
                             str(exp_lines_length), str(setup.serial_camera_exposure_lines),
                             str(pic_height_length), setup.serial_hc_1_picHeight,
                             str(calib_threshold_length), setup.serial_hc_1_calibThreshold,
                             str(max_steps_length), setup.serial_hc_1_maxSteps,
                             str(t_trig_length), str(param.tTrig), str(t_final_length), str(param.tFinal)]

    def get_single_command(self):
        timer = time.time()
        while True:
            if self.serial_connection.in_waiting:
                answer = (self.serial_connection.readline()).decode("ascii")
                break
            cur_time = time.time() - timer
            if cur_time >= self.serial_connection.timeout:
                # TODO custom exception
                raise Exception("timeout")
            time.sleep(0.5)
        return answer

    def transmit_commands(self):
        try:
            log.info("Transmitting variables to hardware controller")
            for command in self.command_list:
                self.send_command(command)
            answer = self.get_single_command()
            if answer != 'received\r\n':
                # TODO custom exception
                raise Exception("no answer from hardware controller")
            else:
                self.state = 2
        except Exception as ex:
            log.error(ex)
            self.state = 0

    def start(self):
        log.debug("Starting hardware controller")
        try:
            self.send_command("2")
            answer = self.get_single_command()
            if answer != 'received\r\n':
                # TODO custom exception
                raise Exception("no answer from hardware controller")
        except Exception as ex:
            log.error(ex)
            self.state = 0

    def stop(self):
        log.debug("Stopping hardware controller")
        try:
            self.send_command('4')
        except:
            log.warning("Connection was already closed")
        finally:
            self.serial_connection.close()

    def cont(self):
        try:
            self.send_command(0)
        except:
            log.warning("Connection was already closed")

    def send_command(self, command):
        command_encoded = command.encode()
        if self.serial_connection.is_open:
            self.serial_connection.write(command_encoded)
        else:
            raise Exception("could not send to", self.serial_connection.name)
            # TODO custom exception
        time.sleep(0.2)
