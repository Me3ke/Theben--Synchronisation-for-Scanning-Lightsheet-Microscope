import logging
import numpy as np

log = logging.getLogger("log")

"""

"""


def find_max_pos(image):
    # center_image = np.sum(image, axis=1)
    max_value = np.amax(image)
    idx = np.unravel_index(np.argmax(image), image.shape)
    return idx[0], max_value


def analyze(image):
    # TODO implement
    return True
