import pco
import logging

from Exceptions.CameraBlockedException import CameraBlockedException

log = logging.getLogger("log")


class CameraController:

    camera = None
    image = None
    stopped = False

    def __init__(self, setup):
        self.setup = setup
        self.trigger_mode = "external exposure start & software trigger"

    def take_picture(self, is_global_shutter):
        """
        Take a picture with the camera with the settings from the setup
        :param is_global_shutter: indicates if a global or rolling shutter image should be taken
        :return: The image or None if either there is no image, or the image is not relevant (e.g. stop was called)
        :raise: CameraBlockedException if camera was forced to stop recording
        """
        # Prevent reusing the camera if it is recording an image.
        if not self.stopped:
            self.stopped = False
            try:
                with pco.Camera() as cam:
                    cam.sdk.set_trigger_mode(self.trigger_mode)
                    if is_global_shutter:
                        # Global shutter sets exposure time while...
                        exposure_time = self.setup.serial_camera_exposure_time * 1e-03
                        cam.set_exposure_time(exposure_time)
                    else:
                        # Rolling shutter sets line time and exposure lines
                        line_time = self.setup.serial_camera_line_time * 1e-06
                        cam.sdk.set_cmos_line_timing('on', line_time)
                        cam.sdk.set_cmos_line_exposure_delay(self.setup.serial_camera_exposure_lines, 0)
                        log.debug(cam.sdk.get_cmos_line_timing())
                        log.debug(cam.sdk.get_cmos_line_exposure_delay())
                    cam.record()
                    # Returns a numpy ndarray and its metadata. Metadate is not in use here
                    self.image, meta = cam.image()
                    if self.stopped:
                        # If the commander sets the stop flag while camera is taking an image
                        # The camera will be released from the blocking record method and
                        # an exception is raised
                        raise CameraBlockedException("Camera was forced to stop")
                    return self.image
            except ValueError:
                # If camera is in use, cam.record will raise a ValueError
                log.error("camera is busy. Make sure the camera is not in use and restart the process")
                return None
            except Exception as ex:
                # No exceptions should be thrown to the commander except for the CameraBlockedException
                # All other exceptions will only be logged-
                log.error(ex)
                return None
        else:
            return None

    def stop(self):
        """Sets the stop flag"""
        self.stopped = True
