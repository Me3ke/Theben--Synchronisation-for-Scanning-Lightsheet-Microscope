import logging
import threading
import time

from src.Commander.AbstractCommander import AbstractCommander
from src.util.FileLoader import *

log = logging.getLogger("log")


class RunningCommander(AbstractCommander):

    mode = '2'

    def start(self):
        log.info("Starting...")
        if not self.started:
            if self.stopped:
                log.warning("After stopping the Application, you need to continue first, before restarting.")
            else:
                self.started = True
                self.laser_controller.arm_laser()
                thread = threading.Thread(target=self.hardware_controller.start)
                thread.start()
                image = self.camera_controller.take_picture(False)
                if image is None:
                    log.error("Camera could not make an image.")
                    time.sleep(2)
                    self.stop()
                else:
                    self.gui_controller.update_image(image)
                    try:
                        elapsed_time = self.hardware_controller.get_single_command()
                        log.info("The galvanometer needed " + elapsed_time + "microseconds")
                    except Exception as ex:
                        log.error(ex)
                    finally:
                        self.laser_controller.turn_off()
                        self.started = False
        else:
            log.warning("Already started")
