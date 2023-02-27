import logging
import numpy as np

from src.Exceptions.NoProperCalibrationException import NoProperCalibrationException

log = logging.getLogger("log")


def find_max_pos(image):
    """Finds the position of the maximum image value and returns its value and its index along the y-axis"""
    max_value = np.amax(image)
    idx = np.unravel_index(np.argmax(image), image.shape)
    return idx[0], max_value


def analyze_optics(image, threshold_middle, threshold_horizontal, split_columns):
    """
    Check an image for optical defects.

    Starts checking if the middle position is where it is expected to be (half of the height).
    Then splits the image values in columns and checks if all have a common maximum position
    :param image: The image to be investigated. Image should have a maximum in the middle of the picture
    :param threshold_middle: Integer that describes how far the middle line may be off from the expected
    :param threshold_horizontal: Integer that describes how far the horizontal line may be off from the first column
    :param split_columns: Integer that describes in how many columns the image is split to investigate curvature
    :return: True if all conditions are met
    :raise: NoProperCalibrationException if a test fails and a condition is not met
    """
    # Get image height and width from the image array
    h, w = image.shape
    pos, val = find_max_pos(image)
    if pos >= (round(h / 2) + threshold_middle) or pos <= (round(h / 2) - threshold_middle):
        raise NoProperCalibrationException("Middle position is not accurate!")

    counter = h
    index_list = []
    while not (counter % split_columns == 0):
        # Reduce counter so that it is divisible by split_columns
        counter -= 1

    # Count is the count of columns
    count = int(counter / split_columns)
    for i in range(1, count + 1):
        # Make a list that contains the indicis where the array has to be split
        index_list.append(i * split_columns)

    split_arr = np.hsplit(image, index_list)
    # First position is saved ...
    check_position, val = find_max_pos(split_arr[0])
    for arr in split_arr:
        pos, val = find_max_pos(arr)
        # and compared to every other column
        if pos > check_position + threshold_horizontal or pos < check_position - threshold_horizontal:
            raise NoProperCalibrationException("Line is not straight!")
    return True


def analyze_positional_defect(pic_pos, gal_pos, const, max_pic_pos, threshold):
    """Analyses an image to compare galvanometer and corresponding picture position"""
    expected_pos = round((max_pic_pos - gal_pos) * const)
    if pic_pos < expected_pos - threshold or pic_pos > expected_pos + threshold:
        return False
    else:
        return True
