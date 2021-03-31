"""
Functions for converting an Image to a Mask. The Mask has False for
background pixels and True for foreground pixels.
"""

from typing import Tuple

import cv2
import numpy as np

from .types import Image, Mask


def calculate_floodfill_mask(
        image: Image,
        start_point: Tuple[int, int],
        selection_colors=None) -> Mask:
    """
    Calculates a mask by floodfilling from the given pixel.
    """

    # Take a copy because floodFill is going to destroy its input
    img = np.copy(image.data)

    start_x, start_y = start_point

    height, width, _ = img.shape
    mask = np.zeros((height+2, width+2), np.uint8)
    # N.b. this destroys img, by floodfilling
    cv2.floodFill(img, mask, (start_x, start_y), 1)

    # Floodfill uses the extra pixels to make a border. Get rid of that
    trimmed_mask = mask[1:-1, 1:-1]

    # Take a note of the coords found by flood fill for bounding box usage later
    filled_coords = np.asarray(np.where(trimmed_mask == 1)).T

    # Turn any extra selection colors into background and their contained
    # contents into foreground. This is primarily expected to be used to handle
    # selected text.
    if selection_colors is not None:
        for color in selection_colors:
            # Assume we have at most one region of each color. Otherwise if
            # we loop we can take hundreds of ms doing each leftover pixel inside
            # each of the letter 'o's for example
            ys, xs = (img == _decode_hex(color)).all(axis=2).nonzero()
            if len(ys) > 0:
                cv2.floodFill(img, mask, (xs[0], ys[0]), 1)

    # Floodfill has found the extent of the textbox background. Mark all rows above and
    # below that as background also.
    trimmed_mask[0:filled_coords[0][0]+1, :] = 1
    trimmed_mask[filled_coords[-1][0]:, :] = 1
    # And mark all rows to the left and right of the found background as background also.
    trimmed_mask[:, 0:filled_coords[0][1]+1] = 1
    trimmed_mask[:, filled_coords[-1][1]:] = 1

    return Mask(trimmed_mask == 0)


def _decode_hex(hexstr):
    """
    Turns a RGB hex string like #aabbff into a BGR array [255, 187, 170]
    """

    return [
        (int(hexstr[i], 16) << 4) + int(hexstr[i+1], 16)
        for i in (1, 3, 5)
    ]
