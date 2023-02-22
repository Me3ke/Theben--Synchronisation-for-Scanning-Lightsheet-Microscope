import matplotlib.pyplot as plt
import pco
import logging

from src.Exceptions.CameraBlockedException import CameraBlockedException

log = logging.getLogger("log")

"""
"""


class CameraController:

    camera = None
    image = None
    exit_info = True
    stopped = False

    def __init__(self, setup):
        self.setup = setup
        self.trigger_mode = "external exposure start & software trigger"

    def take_picture(self, is_global_shutter):
        if not self.stopped:
            self.stopped = False
            try:
                with pco.Camera() as cam:
                    cam.sdk.set_trigger_mode(self.trigger_mode)
                    if is_global_shutter:
                        exposure_time = self.setup.serial_camera_exposure_time * 1e-03
                        cam.set_exposure_time(exposure_time)
                    else:
                        line_time = self.setup.serial_camera_line_time * 1e-06
                        cam.sdk.set_cmos_line_timing('on', line_time)
                        cam.sdk.set_cmos_line_exposure_delay(self.setup.serial_camera_exposure_lines, 0)
                        log.debug(cam.sdk.get_cmos_line_timing())
                        log.debug(cam.sdk.get_cmos_line_exposure_delay())
                    cam.record()
                    self.image, meta = cam.image()
                    if self.stopped:
                        raise CameraBlockedException("Camera was forced to stop")
                    return self.image
            except ValueError:
                log.error("camera is busy. Make sure the camera is not in use and restart the process")
                return None
            except Exception as ex:
                log.error(ex)
                return None
        else:
            return None

    def stop(self):
        self.stopped = True
