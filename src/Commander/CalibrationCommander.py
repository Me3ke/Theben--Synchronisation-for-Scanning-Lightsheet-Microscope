"""

"""

import logging
import threading
import time
import matplotlib.pyplot as plt

from src.Controller.CameraController import CameraController
from src.Controller.HardwareController import HardwareController
from src.Controller.LaserController import LaserController
from src.Controller.ImageController import *
from src.Exceptions.CameraBlockedException import CameraBlockedException
from src.Exceptions.FailedCommunicationException import FailedCommunicationException
from src.Exceptions.IllegalCameraSetupException import IllegalCameraSetupException
from src.Exceptions.NoProperCalibrationException import NoProperCalibrationException
from src.Exceptions.OpticalDefectException import OpticalDefectException
from src.util.FileLoader import *
from src.Exceptions.TimeoutException import TimeoutException

log = logging.getLogger("log")

TRIGGER_COMMAND = "6"
FINISH_COMMAND = "7"
CONFIRM_COMMAND = "8"
REJECT_COMMAND = "9"

# Adjust this, if maximum picture position is not found (decrease), or is not found correctly (increase)
PIC_POS_INTENSITY_THRESHOLD = 3500

# Describes the maximum distance that the galvanometer position may have from their belonging picture position
PIC_ROW_DISTANCE_THRESHOLD = 50

# TODO ergebnisse in einer parameter datei hinterlegen


class CalibrationCommander:

    hardware_controller = None
    camera_controller = None
    laser_controller = None
    setup = None
    verified = False
    stopped = False
    started = False
    calibrated = False
    px_list = []
    v_list = []
    mode = '3'
    max_pic_pos = 0
    min_pic_pos = 0
    t_final = 0
    t_trig = 0

    def __init__(self, gui_controller, setup_path, param_path):
        self.gui_controller = gui_controller
        try:
            self.setup = load(setup_path, 'setup')
        except Exception as e:
            log.error("Could not verify. Try modifying a setup or create a new one")
            log.error("The corresponding error arises from: ")
            log.critical(str(e))

    def run(self):
        if self.initialize_controllers():
            self.verified = True
            self.gui_controller.set_verified()
            log.info("Finished. Data has been verified")

    def initialize_controllers(self):
        try:
            self.camera_controller = CameraController(self.setup)
            self.hardware_controller = HardwareController(self.setup, None)
            self.hardware_controller.init_hc()
            self.hardware_controller.set_commands(self.setup, None, self.mode)
            self.hardware_controller.transmit_commands()
            self.laser_controller = LaserController(self.setup)
            self.laser_controller.set_commands_run()
            return True
        except Exception as e:
            log.error("Failed to initialize connections.")
            log.error("The corresponding error arises from: ")
            log.critical(str(e))
            self.verified = False
            self.stopped = True
            return False

    def start_thread(self):
        thread = threading.Thread(target=self.start, name='Start')
        thread.start()

    def start(self):
        log.info("Starting...")
        if not self.started:
            if self.stopped:
                log.warning("After stopping the Application, you need to continue first, before restarting.")
            else:
                self.started = True
                if self.calibrated:
                    # TODO Do the running here
                    pass
                else:
                    self.laser_controller.arm_laser()
                    self.hardware_controller.start()
                    log.info("Evaluate maximum image position. (Might take a moment)")
                    try:
                        self.max_pic_pos = self.get_pic_pos(0, 5)
                        log.debug(self.max_pic_pos)
                        time.sleep(0.5)
                        log.info("Evaluate minimum image position (Might take a moment)")
                        self.min_pic_pos = self.get_pic_pos(self.setup.serial_hc_1_picHeight, -5)
                        log.debug(self.min_pic_pos)
                        time.sleep(0.5)
                        log.info("Starting optical test")
                        mid_pos = round((self.max_pic_pos + self.min_pic_pos) / 2)
                        self.optical_test(mid_pos)
                        log.info("No optical defects detected")
                        time.sleep(0.5)
                        log.info("Starting picture row test")
                        self.picture_row_test()
                        log.info("No discrepancy found")
                        time.sleep(0.5)
                        #log.info("Starting time calibration")
                        #self.t_final = self.time_calibration()
                        time.sleep(0.5)
                        #self.secure_check()

                        log.info("Found sufficient calibration")
                        # self.save_param() -> save in path or where setup lies
                        #log.info(saved in parameter file)
                        self.started = False
                        self.calibrated = True
                    except Exception as ex:
                        log.critical("Calibration failed!")
                        self.stop()
                        log.critical(ex)
                    finally:
                        self.laser_controller.turn_off()
        else:
            log.warning("Already started")

    def stop(self):
        if not self.stopped:
            if self.verified:
                log.info("Stopping...")
                self.stopped = True
                self.started = False
                self.camera_controller.stop()
                self.laser_controller.stop()
                self.hardware_controller.stop()

    def cont_thread(self):
        thread = threading.Thread(target=self.cont, name='Restart')
        thread.start()

    def cont(self):
        if self.stopped and not self.started:
            log.info("Continue...")
            self.verified = False
            self.stopped = False
            self.run()

    def get_pic_pos(self, start_pos, threshold):
        step = 0
        finished = False
        max_threshold = PIC_POS_INTENSITY_THRESHOLD
        while step < 100:
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
                if pos <= (int(start_pos) + threshold) and val > max_threshold:
                    finished = True
                    break
            time.sleep(0.5)
            step += 1
        if finished:
            self.hardware_controller.send_and_receive(FINISH_COMMAND)
            pic_pos = self.hardware_controller.get_single_command()
            return int(pic_pos)
        else:
            raise Exception("Can't find picture starting or end position. Try adjusting the laser threshold")

    def optical_test(self, mid_pos):
        self.hardware_controller.send_and_receive(str(mid_pos))

        thread = threading.Thread(target=self.hardware_controller.send_and_receive, args=(TRIGGER_COMMAND,))
        thread.start()

        image = self.camera_controller.take_picture(True)
        self.gui_controller.update_image(image)

        if analyze_optics(image):
            self.hardware_controller.send_and_receive(CONFIRM_COMMAND)
        else:
            self.hardware_controller.send_and_receive(REJECT_COMMAND)
            raise Exception("Found optical defects in setup. Please adjust the setup.")

    def picture_row_test(self):
        pic_height = int(self.setup.serial_hc_1_picHeight)
        probability_constant = pic_height / self.max_pic_pos
        picture_count = int((self.max_pic_pos - self.min_pic_pos) / 100)
        counter = 0
        while counter <= picture_count:
            current_pos = self.max_pic_pos - 100
            if current_pos < self.min_pic_pos:
                break
            # TODO does not end?
            thread = threading.Thread(target=self.hardware_controller.send_and_receive, args=(TRIGGER_COMMAND,))
            thread.start()

            image = self.camera_controller.take_picture(True)
            self.gui_controller.update_image(image)

            pos, val = find_max_pos(image)
            self.v_list.append(current_pos)
            self.px_list.append(pos)
            if not analyze_positional_defect(pos, current_pos, probability_constant, pic_height,
                                             PIC_ROW_DISTANCE_THRESHOLD):
                raise OpticalDefectException("Position from galvanometer to current position in picture does not fit")
            counter += 1

    def time_calibration(self):
        answer = self.hardware_controller.get_single_command()
        if answer == '200\r\n':
            raise IllegalCameraSetupException("Parameters for camera setup are not suitable for calibration")
        elif answer == '1\r\n':
            time.sleep(2)
            while True:
                current_t = self.hardware_controller.get_single_command()
                if current_t != 'received\r\n':
                    log.debug(current_t)
                    t_final = current_t
                    answer = self.hardware_controller.get_single_command()
                    log.debug(answer)
                    if answer == '-200\r\n':
                        raise NoProperCalibrationException("There is no calibration found with given parameters")
                    elif answer == '1\r\n':
                        return t_final
                    else:
                        raise FailedCommunicationException("Unknown answer in calibration")
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




