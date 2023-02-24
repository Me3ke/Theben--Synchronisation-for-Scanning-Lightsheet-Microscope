import logging
import threading
import time
import os
import matplotlib.pyplot as plt

from src.Commander.AbstractCommander import AbstractCommander
from src.Commander.RunningCommander import RunningCommander
from src.Controller.ImageController import *
from src.Exceptions.CameraBlockedException import CameraBlockedException
from src.Exceptions.FailedCommunicationException import FailedCommunicationException
from src.Exceptions.IllegalCameraSetupException import IllegalCameraSetupException
from src.Exceptions.NoProperCalibrationException import NoProperCalibrationException
from src.Exceptions.OpticalDefectException import OpticalDefectException
from src.util.FileLoader import *
from src.Exceptions.TimeoutException import TimeoutException

log = logging.getLogger("log")

# Commands for hardware controller communication
TRIGGER_COMMAND = "6"
FINISH_COMMAND = "7"
CONFIRM_COMMAND = "8"
REJECT_COMMAND = "9"


# Describes the maximum deviation the max/min picture positions may have in the picture
# (e.g. 5 -> maximum picture position may be between pixel 0 and 5; Minimum between pic_height and pic_height - 5)
PIC_POS_DISTANCE_THRESHOLD = 5

# Describes the number of steps in one process to find max/min positions
MAX_PIC_POS_STEPS = 100

# Describes the number of repeats to find max/min picture positions
MAX_PIC_POS_REPEATS = 3

# Describes the laser maximum intensity value
LASER_MAX_INTENSITY_VALUE = 30000

# Describes the laser minimum intensity value
LASER_MIN_INTENSITY_VALUE = 6000

# Describes the laser intensity decrement if max/min position was not found
LASER_INC = 2000

# Describes the maximum distance that the middle line is off from the expected middle line
OPTICAL_MIDDLE_POS_MAX_DEVIATION = 40

# Describes in how many columns the picture is split before analyzing if the line is straight in the picture
OPTICAL_COLUMN_SPLIT = 100

# Describes the maximum distance that the max in one column may deviate from another
OPTICAL_HORIZONTAL_MAX_DEVIATION = 10

# Describes the maximum distance that the galvanometer position may have from their belonging picture position
PIC_ROW_DISTANCE_THRESHOLD = 40


class CalibrationCommander (AbstractCommander):

    px_list = []
    v_list = []
    mode = '3'
    max_pic_pos = 0
    min_pic_pos = 0
    t_final = 0
    t_trig = 0

    def start(self):
        log.info("Starting...")
        if not self.started:
            if self.stopped or not self.verified:
                log.warning("After stopping the Application, you need to continue first, before restarting.")
            else:
                self.started = True
                self.laser_controller.arm_laser()
                self.hardware_controller.start()
                try:
                    log.info("Starting intensity test")
                    intensity = self.intensity_test()
                    log.debug(intensity)
                    log.info("Evaluate maximum image position. (Might take a moment)")
                    self.max_pic_pos = self.get_pic_pos(0, PIC_POS_DISTANCE_THRESHOLD, intensity)
                    log.debug(self.max_pic_pos)
                    time.sleep(0.5)
                    log.info("Evaluate minimum image position (Might take a moment)")
                    self.min_pic_pos = self.get_pic_pos(self.setup.serial_hc_1_picHeight,
                                                        -PIC_POS_DISTANCE_THRESHOLD, intensity)
                    log.debug(self.min_pic_pos)
                    time.sleep(0.5)
                    log.info("Starting optical test")
                    mid_pos = round((self.max_pic_pos + self.min_pic_pos) / 2)
                    mid_pic_pos = self.optical_test(mid_pos)
                    log.info("No optical defects detected")
                    time.sleep(0.5)
                    log.info("Starting picture row test")
                    self.picture_row_test(mid_pic_pos)
                    log.info("No discrepancy found")
                    time.sleep(0.5)
                    # TODO show graph maybe?
                    log.info("Starting time calibration. (Might take a moment)")
                    self.t_final = self.time_calibration()
                    time.sleep(0.5)
                    self.secure_check()
                    log.info("Found sufficient calibration")
                    self.save_param()
                    log.info("Saved parameter in file " + self.param_path)
                except Exception as ex:
                    log.critical("Calibration failed!")
                    self.stop()
                    log.error(ex)
                    return
                finally:
                    self.started = False
                    self.laser_controller.turn_off()
                self.stop()
                log.info("Changing into running mode")
                self.change_running()
        else:
            log.warning("Already started")

    def intensity_test(self):
        thread = threading.Thread(target=self.hardware_controller.send_and_receive, args=(TRIGGER_COMMAND,))
        thread.start()

        image = self.camera_controller.take_picture(True)
        self.gui_controller.update_image(image)

        if image is None:
            raise CameraBlockedException("Camera could not make an image, make sure the parameters are valid.")
        else:
            pos, val = find_max_pos(image)
            if val >= LASER_MAX_INTENSITY_VALUE:
                raise OpticalDefectException("Laser intensity too high")
            elif val <= LASER_MIN_INTENSITY_VALUE:
                raise OpticalDefectException("Laser intensity too low")
            return val

    def get_pic_pos(self, start_pos, threshold, intensity):
        counter = 0
        inc = int(intensity * 2 / 3)
        while counter < MAX_PIC_POS_REPEATS:
            step = 0
            finished = False
            intensity_threshold = intensity - inc
            while step < MAX_PIC_POS_STEPS:
                try:
                    thread = threading.Thread(target=self.hardware_controller.send_and_receive, args=(TRIGGER_COMMAND,))
                    thread.start()
                except TimeoutException:
                    break
                image = self.camera_controller.take_picture(True)
                self.gui_controller.update_image(image)
                if image is None:
                    raise CameraBlockedException("Camera could not make an image, make sure the parameters are valid.")
                else:
                    pos, val = find_max_pos(image)
                    if pos <= (int(start_pos) + threshold) and val >= intensity_threshold:
                        finished = True
                        break
                time.sleep(0.5)
                step += 1
            if finished:
                self.hardware_controller.send_and_receive(FINISH_COMMAND)
                pic_pos = self.hardware_controller.get_single_command()
                return int(pic_pos)
            else:
                self.hardware_controller.send_and_receive(REJECT_COMMAND)
                counter += 1
                inc += LASER_INC
        raise Exception("Can't find picture starting or end position. Try adjusting the laser threshold or intensity")

    def optical_test(self, mid_pos):
        self.hardware_controller.send_and_receive(str(mid_pos))

        thread = threading.Thread(target=self.hardware_controller.send_and_receive, args=(TRIGGER_COMMAND,))
        thread.start()

        image = self.camera_controller.take_picture(True)
        self.gui_controller.update_image(image)
        if analyze_optics(image, OPTICAL_MIDDLE_POS_MAX_DEVIATION, OPTICAL_HORIZONTAL_MAX_DEVIATION,
                          OPTICAL_COLUMN_SPLIT):
            self.hardware_controller.send_and_receive(CONFIRM_COMMAND)
            pos, val = find_max_pos(image)
            return pos
        else:
            self.hardware_controller.send_and_receive(REJECT_COMMAND)
            raise OpticalDefectException("Found optical defects in setup. Please adjust the setup.")

    def picture_row_test(self, mid_pic_pos):
        probability_constant = (2 * mid_pic_pos) / (self.max_pic_pos - self.min_pic_pos)
        picture_count = int((self.max_pic_pos - self.min_pic_pos) / 100)
        counter = 0
        current_pos = self.max_pic_pos
        while counter <= picture_count:
            current_pos -= 100
            if current_pos < self.min_pic_pos:
                break

            thread = threading.Thread(target=self.hardware_controller.send_and_receive, args=(TRIGGER_COMMAND,))
            thread.start()

            image = self.camera_controller.take_picture(True)
            self.gui_controller.update_image(image)

            pos, val = find_max_pos(image)
            self.v_list.append(current_pos)
            self.px_list.append(pos)
            if not analyze_positional_defect(pos, current_pos, probability_constant, self.max_pic_pos,
                                             PIC_ROW_DISTANCE_THRESHOLD):
                raise OpticalDefectException("Position from galvanometer to current position in picture does not fit")
            counter += 1
        self.hardware_controller.send_and_receive(FINISH_COMMAND)

    def time_calibration(self):
        self.hardware_controller.send_and_receive(TRIGGER_COMMAND)
        answer = self.hardware_controller.get_single_command()
        log.debug(answer)
        if answer == '200\r\n':
            raise IllegalCameraSetupException("Parameters for camera setup are not suitable for calibration")
        elif answer == '1\r\n':
            time.sleep(2)
            while True:
                answer = self.hardware_controller.get_single_command()
                log.debug(answer)
                if answer == 'finished\r\n':
                    current_t = self.hardware_controller.get_single_command()
                    log.debug(current_t)
                    t_final = current_t
                    difference = self.hardware_controller.get_single_command()
                    log.debug(difference)
                    result = self.hardware_controller.get_single_command()
                    log.debug(result)

                    if result == '-200\r\n':
                        raise NoProperCalibrationException("No calibration found with given parameters")
                    elif result == '1\r\n':
                        return t_final
                    else:
                        raise FailedCommunicationException("Unknown answer in calibration")
                elif answer != 'received\r\n':
                    raise FailedCommunicationException("Unknown answer in calibration")
                time.sleep(5)
        else:
            raise FailedCommunicationException("Unknown answer in calibration")

    def secure_check(self):
        answer1 = self.hardware_controller.get_single_command()
        answer2 = self.hardware_controller.get_single_command()
        if answer1 == -1 or answer2 == -1:
            raise NoProperCalibrationException("There is no calibration with given parameters")
        else:
            if answer1 == self.t_final:
                self.t_trig = answer2
            else:
                raise NoProperCalibrationException("There is no calibration with given parameters")

    def save_param(self):
        if self.param_path == "":
            parent = os.path.abspath(os.path.join(self.setup_path, os.pardir))
            name = "created_param.py"
            self.param_path = parent + '\\' + name
        text = "related_setup = " + "\"" + self.setup_path + "\"" + '\r' \
               "serial_hc_1_maxPicPos = " + "\"" + str(self.max_pic_pos) + "\"" + '\r' \
               "serial_hc_1_minPicPos = " + "\"" + str(self.min_pic_pos) + "\"" + '\r' \
               "tTrig = " + str(self.t_final) + '\r' \
               "tFinal = " + str(self.t_trig)
        save(self.param_path, text)

    def change_running(self):
        try:
            new_commander = RunningCommander(self.gui_controller, self.init, self.setup_path, self.param_path)
        except FileImportException:
            return
        self.gui_controller.set_commander(new_commander)
        self.init.set_new_commander(new_commander)
        new_commander.run()




