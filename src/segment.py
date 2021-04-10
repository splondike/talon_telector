"""
Functions for segmenting a Mask into lines and words.
"""

from typing import List

import numpy as np

from .types import Mask, Rect


def calculate_line_rects(mask: Mask) -> List[Rect]:
    """
    Finds all the line bounding boxes in the Mask
    """
    img_mask = mask.data

    # Find the first non-background pixel in each line
    start_columns = np.argmax(img_mask, axis=1)
    # And the last non-background pixel (counting from the right side)
    end_columns_inverses = np.argmax(np.flip(img_mask, axis=1), axis=1)

    start_y = -1
    start_cols = []
    end_cols = []
    height, width = img_mask.shape
    rtn = []
    for y, start_col, end_col_inverse in zip(range(height), start_columns, end_columns_inverses):
        if start_col == 0:
            # We've hit some white space, emit a line box
            if start_y > -1:
                # Minimum line height.
                # TODO: This could be done better by merging small gaps into the above
                # line. This would deal with lines of ==== and _ in the Terminus font.
                # (x1, y1), (x2, y2) of line bounding box
                if y - start_y > 2:
                    rtn.append(
                        Rect(
                            min(start_cols),
                            start_y,
                            max(end_cols),
                            y
                        )
                    )
                start_y = -1
                start_cols = []
                end_cols = []
            else:
                # Skip, we haven't found the first line yet
                continue
        else:
            if start_y == -1:
                start_y = max(y - 1, 0)

            start_cols.append(start_col)
            end_cols.append(
                width - end_col_inverse - 1
            )

    return rtn


def calculate_word_rects(
        mask: Mask,
        line_rect: Rect,
        word_whitespace_threshold=None) -> List[Rect]:
    """
    Finds all the word bounding boxes in the Mask contained within the given
    line.
    """

    line_slice = mask.data[
        line_rect.y1:line_rect.y2,
        line_rect.x1:line_rect.x2
    ]
    line_height = line_slice.shape[0]

    # Start by converting the line into a list of segments (blobs) describing
    # the start and end index of a set of columns which contain no white space.
    # Also take a note of the distribution of whitespace widths we see

    col_histograms = line_slice.sum(axis=0)

    start_word_x = 0
    end_word_x = 0
    state = 'word'
    blobs = []
    whitespace_widths = []
    for curr_x, val in enumerate(col_histograms):
        is_empty_col = val == 0

        if is_empty_col and state == 'word':
            state = 'whitespace'
            end_word_x = curr_x - 1
        elif not is_empty_col and state == 'whitespace':
            blobs.append((
                start_word_x,
                end_word_x,
            ))
            start_word_x = curr_x
            whitespace_widths.append(start_word_x - end_word_x)

            state = 'word'

    # And add the final blob
    blobs.append((start_word_x, line_slice.shape[1]))

    # If we havent' got an explicit word_whitespace_threshold then guess one based
    # on the distribution of whitespace widths we saw.
    if word_whitespace_threshold is None:
        if len(whitespace_widths) < 2:
            # Just take a wild guess for the threshold for lines without many
            # blobs whitespace
            word_whitespace_threshold = line_height // 7
        else:
            # Half the largest whitespace block seems to work OK as a threshold
            biggest = min(max(*whitespace_widths), line_height)
            word_whitespace_threshold = max(biggest // 2, 4)

    # Now join together the blobs which are less than the whitespace threshold
    # into words
    rtn = []
    accumulating_blob = None
    for blob in blobs:
        if accumulating_blob is None:
            accumulating_blob = blob
        else:
            whitespace_width = (blob[0] - accumulating_blob[1])
            if (whitespace_width < word_whitespace_threshold):
                accumulating_blob = (accumulating_blob[0], blob[1])
            else:
                rtn.append(Rect(
                    line_rect.x1 + accumulating_blob[0],
                    line_rect.y1,
                    line_rect.x1 + accumulating_blob[1],
                    line_rect.y2
                ))
                accumulating_blob = blob

    rtn.append(Rect(
        line_rect.x1 + accumulating_blob[0],
        line_rect.y1,
        line_rect.x1 + accumulating_blob[1],
        line_rect.y2
    ))

    return rtn
