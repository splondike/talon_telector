"""
Types used by the scripts
"""


class Image:  # pylint:disable=too-few-public-methods
    """
    A full color image. Contains a numpy array with shape (height, width, 3).
    3 are the RGB channels. This is also the standard OpenCV image format except
    it users BGR.
    """

    def __init__(self, data):
        self.data = data


class Mask:  # pylint:disable=too-few-public-methods
    """
    A bitmap image. Contains a numpy array with shape (height, width) and each
    element is True or False. The convention is that True is a foreground
    pixel, and False is a background one.
    """

    def __init__(self, data):
        self.data = data


class Rect:  # pylint:disable=too-few-public-methods
    """
    A simple rect type
    """

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __repr__(self):
        return f"Rect(({self.x1}, {self.y1}), ({self.x2}, {self.y2}))"
