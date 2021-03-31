"""
The Talon actions etc exported by this package
"""

import time

import numpy as np
from talon import actions, screen, ui, canvas, settings, ctrl, Context, Module
from talon.types import Rect as TalonRect

# Import our modules then reset the Python path so as not to pollute the namespace
# of other modules
import sys
import os
orig_path = sys.path
sys.path += [os.path.dirname(os.path.abspath(__file__))]
from src.types import Image
from src.mask import calculate_floodfill_mask
from src.segment import calculate_line_rects, calculate_word_rects
sys.path = orig_path

import marker_ui


mod = Module()
mod.tag("textarea_labels_showing", desc="The floating textarea labels are showing")
ctx = Context()
ctx_active = Context()
ctx_active.matches = r"""
tag: user.textarea_labels_showing
"""

# Contains the currently displayed MarkerUi, or None if none is showing
labels_ui = None


def screencap_to_image(rect: TalonRect) -> Image:
    """
    Captures the given rectangle off the screen and returns an OpenCV style numpy
    array.
    """

    img = screen.capture(rect.x, rect.y, rect.width, rect.height)
    return Image(np.delete(np.array(img), 3, axis=2))


def find_word_rects():
    """
    Produces a list of word rectanges for the currently focussed window
    """

    bounding_rect = ui.active_window().rect
    image = screencap_to_image(bounding_rect)
    mouse_pos = ctrl.mouse_pos()
    mouse_norm_y = mouse_pos[1] - bounding_rect.y
    mouse_norm_x = mouse_pos[0] - bounding_rect.x
    mask = calculate_floodfill_mask(
        image,
        (mouse_norm_x, mouse_norm_y)
    )

    line_rects = calculate_line_rects(mask)
    word_rects = []
    for line_rect in line_rects:
        line_word_rects = calculate_word_rects(
            mask,
            line_rect
        )
        word_rects += line_word_rects

    return bounding_rect, word_rects


def anchor_generator():
    letters = "abcdefghijklmnopqrstuvwxyz"
    for letter in letters:
        yield letter

    for letter1 in letters:
        for letter2 in letters:
            if letter1 != letter2:
                yield f"{letter1}{letter2}"


@mod.action_class
class GeneralActions:
    def textarea_labels_show():
        """
        Locate and show textarea labels
        """

        global labels_ui
        if labels_ui is not None:
            labels_ui.hide()

        bounding_rect, word_rects = find_word_rects()

        labels_ui = marker_ui.MarkerUi(
            [
                marker_ui.MarkerUi.Marker(
                    target_region=TalonRect(
                        bounding_rect.x + rect.x1,
                        bounding_rect.y + rect.y1,
                        rect.x2 - rect.x1,
                        rect.y2 - rect.y1
                    ),
                    label=label
                )
                for rect, label in zip(word_rects, anchor_generator())
            ]
        )
        labels_ui.show()
        ctx.tags = ["user.textarea_labels_showing"]

    def textarea_labels_hide():
        """
        Hide any visible textarea labels
        """

        global labels_ui
        if labels_ui is not None:
            labels_ui.destroy()
            labels_ui = None
        ctx.tags = []


@mod.action_class
class LabelsActiveActions:
    def textarea_labels_select_text(anchor1: str, anchor2: str):
        """
        Selects the text indicated by the given anchors
        """

        global labels_ui

        rect1 = None
        rect2 = None
        for marker in labels_ui.markers:
            if marker.label == anchor1:
                rect1 = marker.target_region
            if marker.label == anchor2:
                rect2 = marker.target_region

        if rect1 is None or rect2 is None:
            # Couldn't find them, quit
            return

        init_mouse_x = actions.mouse_x()
        init_mouse_y = actions.mouse_y()

        actions.mouse_move(
            rect1.x,
            rect1.y + rect1.height / 2,
        )
        actions.mouse_drag(0)
        time.sleep(0.1)
        actions.mouse_move(
            rect2.x + rect2.width,
            rect2.y + rect2.height / 2
        )
        actions.mouse_release(0)

        actions.mouse_move(
            init_mouse_x,
            init_mouse_y
        )

        if labels_ui is not None:
            labels_ui.destroy()
            labels_ui = None
        ctx.tags = []

    def textarea_labels_click_anchor(anchor: str):
        """
        Clicks the given anchor
        """

        global labels_ui

        rect = None
        for marker in labels_ui.markers:
            if marker.label == anchor:
                rect = marker.target_region

        if rect is None:
            # Couldn't find them, quit
            return

        init_mouse_x = actions.mouse_x()
        init_mouse_y = actions.mouse_y()

        actions.mouse_move(
            rect.x + rect.width / 2,
            rect.y + rect.height / 2,
        )
        actions.mouse_click()
        time.sleep(0.1)

        actions.mouse_move(
            init_mouse_x,
            init_mouse_y
        )

        if labels_ui is not None:
            labels_ui.destroy()
            labels_ui = None
        ctx.tags = []


# Some capture groups we need


@mod.capture(rule="{self.letter}+")
def textarea_labels_anchor(m) -> str:
    """
    An anchor (string of letters)
    """
    return "".join(m)
