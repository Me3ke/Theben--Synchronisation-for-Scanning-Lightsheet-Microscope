import matplotlib.pyplot as plt
import pco
import logging

log = logging.getLogger("log")


class CameraController:

    camera = None
    image = None

    def __init__(self, setup):
        self.setup = setup

    def take_picture(self):
        with pco.Camera() as cam:
            cam.sdk.set_trigger_mode('external exposure start & software trigger')
            cam.record()
            self.image, meta = cam.image()
            plt.imshow(self.image, cmap='gray')
            plt.show()
            return self.image

    def config_camera(self):
        self.camera.configuration = {
            'trigger': 'external exposure start & software trigger',
        }
