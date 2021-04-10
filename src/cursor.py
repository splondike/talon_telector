"""
Functions for finding the cursor in screenshots. Not currently used by the interface.
"""

from typing import Optional

import numpy as np

from .types import Mask, Image, Rect


def find_cursor_by_difference(image_one: Image, image_two: Image) -> Optional[Rect]:
    """
    Tries to find the cursor position by finding the difference between
    two images.
    """

    # Find the differences between the two images
    difference = (image_one.data != image_two.data).all(axis=2)

    ys, xs = difference.nonzero()

    if len(ys) == 0:
        return None

    y1 = ys.min()
    y2 = ys.max()
    x1 = xs.min()
    x2 = xs.max()

    if (x2 - x1) > (y2 - y1):
        # Wider than tall, not a cursor
        return None

    return Rect(
        x1,
        y1,
        x2,
        y2
    )
