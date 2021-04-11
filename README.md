Text selection helper for [Talon](https://talonvoice.com/), mainly intended to help with editing prose. Attempts to locate and label words on the screen so you can indicate which you want to select.

# Installation

The script relies on the [knausj](https://github.com/knausj85/knausj_talon/) repository. You can just clone this one and drop it in next to that.

# Usage

You start by editing text in your program or website using normal commands. At some point you want to change a word or reposition the cursor. The `telector` command shows a overlay on the screen that indicates each word in your text widget. You are then able to use the `select`, `click`, or `cursor [before]` commands to select word(s), click on one, or reposition the cursor. For example you might say `click air` to click the word indicated by the letter 'a', or `select air through cap` to select all the words between 'a' and 'c'. Each of these actions will hide the overlay, but you can also say `telector hide` to hide it explicitly.

The default configuration requires you to hover the mouse cursor over the background of the textarea that you are editing. It fills in identically colored pixels from this point to work out the extent of your textarea.

You are also able to configure the system more explicitly, which is probably more useful for applications that use frequently. The video below demonstrates the scripts using an explicitly configured application.

![Video demonstrating telector](doc/demo.gif)

## Configuration

The scripts come with a number of different ways of determining the textarea bounding box and word positions:

1. Flood filling from the mouse cursor position (default).
2. Flood filling from an explicit coordinate relative to the active window.
3. An explicit bounding box relative to the active window and explicit background colours. This is probably the one you'd use for your frequently used applications.

These options and their parameters can be configured via settings, which allows you to have different settings for each application/context. For example, here's how you might configure an application using method 3. This would go in a file called `gedit.talon`.

    title: /gedit/
    -
    # tag(): user.telector_ui_underline
    settings():
        user.telector_bounding_box = "active_window:42 52 -7 -35"
        user.telector_background_detector = "explicit_colors:#eeeeec #ffffff"

The `telector_bounding_box` setting says the box where the text is contained is the active window offset 42 pixels from the left and -7 pixels from the right, 52 pixels from the top and -35 pixels from the bottom. `telector_background_detector` says that the background colours within this region are #eeeeec and #ffffff, all other colours are considered text.

The scripts actually come with two different marker UIs, the `tag()` line (if uncommented) activates the alternative UI. In the alternative you first indicate the line you want to edit and then the word number within the line. For example `select air eleven` would select the 11th word on the first line (indicted with an 'a').

The complete list of settings are as follows. You can also view them by running the command `settings.list()` in the Talon REPL and looking for those prefixed with the word 'telector'.

* `user.telector_debug_mode` - Helpful when manually specifying bounding boxes and background colours. Draws a persistent blue border and red boxes around the bounding box and word rectangles detected on the active window.
* `user.telector_bounding_box` - Either `active_window` or `active_window:<offset left> <offset top> <offset right> <offset bottom>`. In the offset version you're specifying the top left and bottom right coordinates of the box. If the numbers are positive then they are relative to the top left of the active window box, if negative, then they're relative to the bottom right of the same.
* `user.telector_background_detector` - How the system works out which pixels are foreground and background within the given bounding box. Either `mouse_fill`, `pixel_fill: <offset x> <offset y>`, or `explicit_colors:#<hex one> #<hex two> ...`. The first foodfills from the mouse cursor. The second floodfills from the explicit coordinates given, these use the same positive/negative system as the bounding box. `explicit_colors` says to treat the given colours as background. The colors are formatted CSS style, e.g. `#ff0000` for pure red.
* `user.telector_target_mode` - Whether to allow selection of `words` or just whole `lines`.
* `user.telector_enable_marker_ui_offset` - Either '0' or '1'. If one, then the default marker UI will be offset down a bit which can make words readable even when markers are shown.
* `user.telector_word_spacing` - When '-1' attempts to automatically work out the spacing between words in a line. Can also be given an explicit width in pixels.
* `user.telector_enable_win_rect_workaround` - There is a bug in Talon on linux currently where it gives an incorrect bounding rectangle for active windows. Change this setting to '1' to enable a workaround based on the xdotool command.

# Developing the algorithm

If you would like to try developing a better algorithm for word detection there is a script `segment_test.py` to help with this. This script lets you run the detection system outside of the Talon environment, which allows for quicker iteration.
