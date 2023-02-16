import matplotlib.pyplot as plt
import pco
import logging

log = logging.getLogger("log")

"""
"""


class CameraController:

    camera = None
    image = None
    exit_info = True

    def __init__(self, setup):
        self.setup = setup
        self.trigger_mode = "external exposure start & software trigger"

    def take_picture_rolling_shutter(self):
        try:
            with pco.Camera() as cam:
                # TODO output for all lines
                cam.sdk.set_trigger_mode(self.trigger_mode)
                line_time = self.setup.serial_camera_line_time * 1e-06
                cam.sdk.set_cmos_line_timing('on', line_time)
                cam.sdk.set_cmos_line_exposure_delay(self.setup.serial_camera_exposure_lines, 0)
                log.debug(cam.sdk.get_cmos_line_timing())
                log.debug(cam.sdk.get_cmos_line_exposure_delay())
                # TODO solution for blocking camera
                cam.record()
                self.image, meta = cam.image()
                plt.imshow(self.image, cmap='gray')
                plt.show()
                # TODO remove later
                return self.image
        except ValueError:
            # TODO examine if this is right
            log.error("camera is busy. Make sure the camera is not in use and restart the process")
            return None
        except Exception as ex:
            log.error(ex)
            return None

    def take_picture_global_shutter(self):
        try:
            with pco.Camera() as cam:
                cam.sdk.set_trigger_mode(self.trigger_mode)
                exposure_time = self.setup.serial_camera_exposure_time * 1e-03
                cam.set_exposure_time(exposure_time)
                cam.record()
                self.image, meta = cam.image()
                #plt.imshow(self.image, cmap='gray')
                #plt.show()
                # TODO remove later
                return self.image
        except ValueError:
            # TODO examine if this is right
            log.error("camera is busy. Make sure the camera is not in use and restart the process")
            return None
        except Exception as ex:
            log.error(ex)
            return None

    # TODO remove?
    def config_camera(self):
        self.camera.configuration = {
            'trigger': 'external exposure start & software trigger',
        }
