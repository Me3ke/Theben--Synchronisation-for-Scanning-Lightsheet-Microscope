import matplotlib.pyplot as plt
import pco
import logging
import random

log = logging.getLogger("log")


class CameraController:

    camera = None
    image = None

    def __init__(self, setup):
        self.setup = setup

    def take_picture(self):
        try:
            with pco.Camera() as cam:
                cam.sdk.set_trigger_mode(self.setup.serial_camera_trigger_mode)
                line_time = self.setup.serial_camera_line_time * 1e-06
                cam.sdk.set_cmos_line_timing('on', line_time)
                cam.sdk.set_cmos_line_exposure_delay(self.setup.serial_camera_exposure_lines, 0)
                print(cam.sdk.get_cmos_line_timing())
                print(cam.sdk.get_cmos_line_exposure_delay())
                cam.record()
                self.image, meta = cam.image()
                plt.imshow(self.image, cmap='gray')
                plt.show()
                # TODO remove later
                return self.image
        except ValueError:
            log.error("camera is busy. Make sure the camera is not in use and restart the process")
            return None
        except Exception as ex:
            log.error(ex)
            return None

    def config_camera(self):
        self.camera.configuration = {
            'trigger': 'external exposure start & software trigger',
        }
