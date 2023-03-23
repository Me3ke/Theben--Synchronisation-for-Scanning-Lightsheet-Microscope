import logging
import threading
import time

from Commander.AbstractCommander import AbstractCommander
from util.FileLoader import *

log = logging.getLogger("log")

START_COMMAND = "2"


class RunningCommander(AbstractCommander):

    # mode is '2' meaning running mode. Is coded to be simpler to transfer to hardware controller
    mode = '2'

    def start(self):
        """
        Start a main routine for a picture in running mode

        If all flags are valid (program was not stopped etc.). Take a picture by starting the laser via Lasercontroller
        send a signal via hardware controller to start and sets up the camera via camera controller.
        After that the program displays the image in the gui via gui controller and finally turns off the laser again.
        """
        log.info("Starting...")
        if not self.started:
            if self.stopped:
                log.warning("After stopping the Application, you need to continue first, before restarting.")
            else:
                # Prevent starting multiple times
                self.started = True
                self.laser_controller.arm_laser()
                # Start a thread because camera blocks and waits for trigger, so getting the hardware controller
                # to trigger and starting the camera has to be simultaneous.
                thread = threading.Thread(target=self.hardware_controller.send_and_receive, args=(START_COMMAND,))
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
