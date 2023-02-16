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
from src.util.FileLoader import *
from src.Exceptions.TimeoutException import TimeoutException

log = logging.getLogger("log")
TRIGGER_COMMAND = "6"
FINISH_COMMAND = "7"
CONFIRM_COMMAND = "8"
REJECT_COMMAND = "9"

# TODO ergebnisse in einer parameter datei hinterlegen


class CalibrationCommander:

    hardware_controller = None
    camera_controller = None
    laser_controller = None
    setup = None
    verified = False
    stopped = False
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
            self.setup = load_setup(setup_path)
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
            self.stop()
            self.verified = False
            self.stopped = True
            return False

    def start_thread(self):
        thread = threading.Thread(target=self.start, name='Start')
        thread.start()

    def start(self):
        log.info("Starting...")
        if self.stopped:
            log.warning("After stopping the Application, you need to continue first, before restarting.")
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
                mid_pos = self.max_pic_pos - self.min_pic_pos
                self.optical_test(mid_pos)
                log.info("No optical defects detected")
                time.sleep(0.5)
                log.info("Starting picture row test")
                self.picture_row_test()
                log.info("No discrepancy found")
                time.sleep(0.5)
                #log.info("Starting time calibration")
                #self.t_final, self.t_trig = self.time_calibration()
                log.info("Found sufficient calibration")
            except Exception as ex:
                log.critical("Calibration failed!")
                self.stop()
                log.critical(ex)


    def stop(self):
        if self.verified:
            log.info("Stopping...")
            self.laser_controller.stop_laser()
            self.hardware_controller.stop()
            self.stopped = True

    def cont_thread(self):
        thread = threading.Thread(target=self.cont, name='Restart')
        thread.start()

    def cont(self):
        if self.stopped:
            log.info("Continue...")
            self.verified = False
            self.stopped = False
            self.run()

    def get_pic_pos(self, start_pos, threshold):
        step = 0
        finished = False
        max_threshold = self.setup.serial_laser_power * 5000
        while step < 100:
            try:
                thread = threading.Thread(target=self.hardware_controller.send_and_receive, args=(TRIGGER_COMMAND,))
                thread.start()
            except TimeoutException:
                break
            image = self.camera_controller.take_picture_global_shutter()
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
            raise Exception("Can't find picture starting or end position. Try adjusting the laser intensity")

    def optical_test(self, mid_pos):
        self.hardware_controller.send_and_receive(str(mid_pos))

        thread = threading.Thread(target=self.hardware_controller.send_and_receive, args=(TRIGGER_COMMAND,))
        thread.start()

        image = self.camera_controller.take_picture_global_shutter()
        self.gui_controller.update_image(image)
        if analyze(image):
            self.hardware_controller.send_and_receive(CONFIRM_COMMAND)
        else:
            self.hardware_controller.send_and_receive(REJECT_COMMAND)
            raise Exception("Found optical defects in setup. Please adjust the setup.")

    def picture_row_test(self):
        current_pos = self.max_pic_pos
        while current_pos >= self.min_pic_pos:

            current_pos = self.max_pic_pos - 100
            # TODO does not end?
            thread = threading.Thread(target=self.hardware_controller.send_and_receive, args=(TRIGGER_COMMAND,))
            thread.start()

            image = self.camera_controller.take_picture_global_shutter()
            self.gui_controller.update_image(image)

            pos, val = find_max_pos(image)
            self.px_list.append(pos)
            self.v_list.append(current_pos)
            plt.plot(self.px_list, self.v_list)


        # TODO imagecontrolller -> is px to v linear ?

    def time_calibration(self):
        # TODO
        return None, None

