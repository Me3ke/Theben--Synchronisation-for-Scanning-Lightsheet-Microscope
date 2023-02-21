import logging
import numpy as np

from src.Exceptions.NoProperCalibrationException import NoProperCalibrationException

log = logging.getLogger("log")

"""

"""


def find_max_pos(image):
    max_value = np.amax(image)
    idx = np.unravel_index(np.argmax(image), image.shape)
    return idx[0], max_value


def analyze_optics(image, threshold):
    h, w = image.shape
    pos, val = find_max_pos(image)
    if pos >= (round(h / 2) + threshold) or pos <= (round(h / 2) - threshold):
        raise NoProperCalibrationException("Positions are not accurate!")
    return True


def analyze_positional_defect(pic_pos, gal_pos, const, max_pic_pos, threshold):
    expected_pos = round((max_pic_pos - gal_pos) * const)
    if pic_pos <= expected_pos - threshold or pic_pos > expected_pos + threshold:
        return False
    else:
        return True
