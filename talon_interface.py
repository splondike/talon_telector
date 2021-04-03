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
from src.mask import calculate_floodfill_mask, calculate_explicit_mask
from src.segment import calculate_line_rects, calculate_word_rects
sys.path = orig_path

import marker_ui


mod = Module()
mod.tag("telector_showing", desc="The text selection helper labels are showing")
ctx = Context()
ctx_active = Context()
ctx_active.matches = r"""
tag: user.telector_showing
"""

setting_bounding_box = mod.setting(
    "telector_bounding_box",
    type=str,
    desc="Customise the area telector looks for text in",
    default="active_window"
)
setting_background_detector = mod.setting(
    "telector_background_detector",
    type=str,
    desc="Customise the way telector looks for text",
    default="mouse_fill"
)
setting_selection_background = mod.setting(
    "telector_selection_background",
    type=str,
    desc="The color that is used as the background for text selection",
    default=None
)
setting_target_mode = mod.setting(
    "telector_target_mode",
    type=str,
    desc="The type of target you want to find, one of lines or words",
    default="words"
)
setting_debug_mode = mod.setting(
    "telector_debug_mode",
    type=int,
    desc="Turns on permanent word detection overlay",
    default=0
)

# Contains the currently displayed MarkerUi, or None if none is showing
labels_ui = None


def screencap_to_image(rect: TalonRect) -> Image:
    """
    Captures the given rectangle off the screen and returns an OpenCV style numpy
    array.
    """

    img = screen.capture(rect.x, rect.y, rect.width, rect.height)
    return Image(np.delete(np.array(img), 3, axis=2))


def calculate_relative(modifier, start, end):
    """
    Helper method for settings. Lets you specify numbers relative to a
    range. For example:

        calculate_relative("-10", 0, 100) == 90
        calculate_relative("10", 0, 100) == 10
        calculate_relative("-0", 0, 100) == 100
    """
    if modifier.startswith("-"):
        modifier_ = int(modifier[1:])
        rel_end = True
    else:
        modifier_ = int(modifier)
        rel_end = False

    if rel_end:
        return end - modifier_
    else:
        return start + modifier_


def find_bounding_rect(config=None):
    """
    Finds a bounding box to search for text in either based on an
    explicit argument or on setting_bounding_box
    """

    bounding_box_setting = config if config is not None else setting_bounding_box.get()

    if bounding_box_setting.startswith("active_window"):
        bits = bounding_box_setting.split(":")
        mods = bits[1].split(" ") if len(bits) > 1 else ["0", "0", "-0", "-0"]
        base_rect = ui.active_window().rect
        _calc_pos = calculate_relative

        x = _calc_pos(mods[0], base_rect.x, base_rect.x + base_rect.width)
        y = _calc_pos(mods[1], base_rect.y, base_rect.y + base_rect.height)
        rect = TalonRect(
            x,
            y,
            _calc_pos(mods[2], 0, base_rect.width) - x,
            _calc_pos(mods[3], 0, base_rect.height) - y,
        )

    return rect


def find_mask(image, bounding_rect, config=None):
    """
    Finds a foreground/background mask for use as input to the segmenter
    in the given image (with the given bounding box). Can be given
    explicit configuration, or pull it from setting_background_detector.
    """

    background_detector_setting = config if config is not None else setting_background_detector.get()

    if background_detector_setting == "mouse_fill":
        mouse_pos = ctrl.mouse_pos()
        mouse_norm_y = mouse_pos[1] - bounding_rect.y
        mouse_norm_x = mouse_pos[0] - bounding_rect.x
        mask = calculate_floodfill_mask(
            image,
            (mouse_norm_x, mouse_norm_y)
        )
    elif background_detector_setting.startswith("pixel_fill"):
        bits = background_detector_setting.split(":")
        mods = bits[1].split(" ") if len(bits) > 1 else ["0", "0"]
        mask = calculate_floodfill_mask(
            image,
            (
                calculate_relative(mods[0], 0, bounding_rect.width),
                calculate_relative(mods[1], 0, bounding_rect.height),
            )
        )
    elif background_detector_setting.startswith("explicit_colors"):
        _, colors_str = background_detector_setting.split(":")
        colors = colors_str.split(" ")
        mask = calculate_explicit_mask(
            image,
            colors
        )

    return mask


def find_rects(bounding_rect, mask_config=None, target_mode=None):
    """
    Produces a list of selectable rectangles
    """

    image = screencap_to_image(bounding_rect)
    mask = find_mask(image, bounding_rect, mask_config)
    target_mode_ = \
        setting_target_mode.get() if target_mode is None else target_mode

    line_rects = calculate_line_rects(mask)
    if target_mode_ == "lines":
        return line_rects
    else:
        word_rects = []
        for line_rect in line_rects:
            line_word_rects = calculate_word_rects(
                mask,
                line_rect
            )
            word_rects += line_word_rects

        return word_rects


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
    def telector_show(
            bounding_rect_config: str="",
            mask_config: str="",
            target_mode: str=""):
        """
        Locate and show labels on text. Can be given explicit search
        parameters or will pull them from settings.
        """

        global labels_ui
        if labels_ui is not None:
            labels_ui.hide()

        bounding_rect_config_ = \
            None if bounding_rect_config == "" else bounding_rect_config
        mask_config_ = \
            None if mask_config == "" else mask_config
        target_mode_ = \
            None if target_mode == "" else target_mode
        bounding_rect = find_bounding_rect(bounding_rect_config_)
        target_rects = find_rects(bounding_rect, mask_config_, target_mode_)

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
                for rect, label in zip(target_rects, anchor_generator())
            ]
        )
        labels_ui.show()
        ctx.tags = ["user.telector_showing"]

    def telector_hide():
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
    def telector_select(anchor1: str, anchor2: str):
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
            # The bounding box looks fine in a screenshot but +2 helps to get
            # the whole word with my terminal and seems to work OK elsewhere.
            # Guess it's up to the application how it responds.
            rect2.x + rect2.width+2,
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

    def telector_click(anchor: str, button:int = 0):
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
        actions.mouse_click(button)
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
def telector_anchor(m) -> str:
    """
    An anchor (string of letters)
    """
    return "".join(m)


# Debugging stuff, enable by the setting "user.selector_debug_mode = 1"

debug_canvas = None
debug_bounding_rect = None
debug_word_rects = None

def _debug_draw(canvas):
    global debug_bounding_rect, debug_word_rects

    paint = canvas.paint
    paint.stroke_width = 1
    paint.style = paint.Style.STROKE
    paint.color = 'green'
    canvas.draw_rect(debug_bounding_rect)
    paint.color = 'red'
    for rect in debug_word_rects:
        # skia canvas positions are always relative to the screen
        canvas.draw_rect(TalonRect(
            debug_bounding_rect.x + rect.x1,
            debug_bounding_rect.y + rect.y1,
            rect.x2 - rect.x1,
            rect.y2 - rect.y1
        ))


def _debug_helper(*args):
    global debug_canvas, debug_bounding_rect, debug_word_rects
    if debug_canvas:
        # Destroy all debugging stuff on settings change, we'll rebuild it if
        # neccessary in _debug_recapture_rects
        debug_canvas.close()
        debug_canvas = None

    try:
        debug_on = setting_debug_mode.get()
        if debug_on != 1:
            return
    except KeyError:
        return

    debug_bounding_rect = find_bounding_rect()
    debug_word_rects = find_rects(debug_bounding_rect)
    debug_canvas = canvas.Canvas.from_rect(debug_bounding_rect)

    debug_canvas.register("draw", _debug_draw)


settings.register("", _debug_helper)
