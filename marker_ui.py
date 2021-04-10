"""
The GUI code
"""

from typing import List, NamedTuple, Optional

import re

from talon import screen, canvas, ui, ctrl
from talon import cron
from talon.types import Rect
from talon.skia.bitmap import Bitmap
from talon.skia.typeface import Typeface


class MarkerUi:
    """
    Draws some markers pointing to particular locations on the screen
    """

    class Marker(NamedTuple):
        target_region: Rect
        label: str

    def __init__(self, markers: List[Marker]=[], offset_downward=False, screen_idx=0):
        """
        Args:

            markers: List of marker locations and labels to show
            offset_downward: If true, then shift the markers so they don't cover the top
              half of the target region. This can make text readable even when the marker
              is showing.
            screen_idx: The Talon screen index we're showing the markers on.
        """

        self.markers = markers
        self.can = canvas.Canvas.from_screen(ui.screens()[screen_idx])
        self.can.register("draw", self._draw)
        self.can.hide()
        self.offset_downward = offset_downward
        self.visible = False

    def show(self):
        self.can.show()
        # Freeze stops draw being called at 60Hz and just uses the initial paint
        self.can.freeze()
        self.visible = True

    def hide(self):
        self.can.hide()
        self.visible = False

    def destroy(self):
        self.can.close()

    def find_rect(self, identifier: str) -> Optional[Rect]:
        """
        Finds the rectangle corresponding to the given identifier, or None if
        it couldn't be found.
        """

        for marker in self.markers:
            if marker.label == identifier:
                return marker.target_region

        return None

    def _draw(self, canvas):
        paint = canvas.paint
        paint.textsize = 12
        paint.typeface = Typeface.from_name('monospace')
        min_width = 10
        min_height = 10
        for marker in self.markers:
            region = marker.target_region

            # trect.x and .y are the offsets the text is printed at
            _, trect = paint.measure_text(marker.label)

            # Draw the box
            height = max(trect.height, min_height) + 2
            width = max(trect.width, min_width) + 2
            ypos = \
                region.y + height // 2 if self.offset_downward \
                else region.y + (region.height - height) // 2
            bg_rect = Rect(
                region.x + (region.width - width) // 2,
                ypos,
                width,
                height
            )

            paint.style = paint.Style.FILL
            paint.color = 'aaffffff'
            canvas.draw_rect(bg_rect)
            paint.color = 'black'

            # Draw the label
            paint.style = paint.Style.FILL
            canvas.draw_text(
                marker.label,
                bg_rect.x - trect.x + (bg_rect.width - trect.width) / 2,
                bg_rect.y - trect.y + (bg_rect.height - trect.height) / 2
            )


class UnderlineMarkerUi:
    """
    An interface allowing you to select anchors by line label and word/item position
    """

    class Group(NamedTuple):
        label: str
        line_rect: Rect
        item_rects: List[Rect]

    def __init__(self, groups: List[Group]=[], screen_idx=0):
        """
        Args:
            groups: List of groups of item rectangles with a label for the whole group.
            screen_idx: The Talon screen index we're showing the markers on.
        """
        self.groups = groups
        self.can = canvas.Canvas.from_screen(ui.screens()[screen_idx])
        self.can.register("draw", self._draw)
        self.can.hide()
        self.visible = False

    def show(self):
        self.can.show()
        # Freeze stops draw being called at 60Hz and just uses the initial paint
        self.can.freeze()
        self.visible = True

    def hide(self):
        self.can.hide()
        self.visible = False

    def destroy(self):
        self.can.close()

    def find_rect(self, identifier: str) -> Optional[Rect]:
        """
        Finds the rectangle corresponding to the given identifier, or None if
        it couldn't be found.
        """

        maybe_match = re.search(r'\d', identifier)
        if not maybe_match:
            return None

        letters = identifier[:maybe_match.start()]
        number = int(identifier[maybe_match.start():])
        for group in self.groups:
            if group.label == letters:
                if len(group.item_rects) >= number:
                    return group.item_rects[number - 1]
                else:
                    return None

        return None

    def _draw(self, canvas):
        paint = canvas.paint
        paint.style = paint.Style.STROKE

        # Should we draw line labels on the left or the right of the line?
        labels_on_left = all(
            (group.line_rect.x - 20) > 0
            for group in self.groups
        )

        highlight_colors = [
            '0000ffff',
            'ff6600ff',
            'ff00ffff',
        ]
        for group in self.groups:
            self._draw_label(canvas, group, labels_on_left)
            for i, word_rect in enumerate(group.item_rects):
                paint.color = 'aaaaaaff'
                if i > 0 and (i+1) % 5 == 0:
                    paint.color = highlight_colors[
                        (i // 5) % len(highlight_colors)
                    ]

                paint.stroke_width = 2
                canvas.draw_line(
                    word_rect.x,
                    word_rect.y + word_rect.height + 1,
                    word_rect.x + word_rect.width,
                    word_rect.y + word_rect.height + 1
                )

    def _draw_label(self, canvas, group, labels_on_left):
        paint = canvas.paint
        paint.textsize = 12
        paint.typeface = Typeface.from_name('monospace')
        paint.stroke_width = 1
        padding = 2
        min_width = 10
        min_height = 10
        region = group.line_rect

        # trect.x and .y are the offsets the text is printed at
        _, trect = paint.measure_text(group.label)

        # Draw the box
        height = max(trect.height, min_height) + 2*padding
        width = max(trect.width, min_width) + 2*padding
        xpos_offset = (-1 * width - 5) if labels_on_left else (region.width + 5)
        bg_rect = Rect(
            region.x + xpos_offset + 0.5,
            region.y + (region.height - height) // 2 + 0.5,
            width,
            height
        )

        paint.style = paint.Style.FILL
        paint.color = 'ffffffff'
        canvas.draw_rect(bg_rect)
        paint.color = 'black'
        paint.style = paint.Style.STROKE
        canvas.draw_rect(bg_rect)

        paint.style = paint.Style.FILL
        canvas.draw_text(
            group.label,
            bg_rect.x - trect.x + (bg_rect.width - trect.width) / 2,
            bg_rect.y - trect.y + (bg_rect.height - trect.height) / 2
        )

if False:
    # Testing code, set above to True to activate
    def _make_markers():
        import random
        random.seed(0)
        return [
            MarkerUi.Marker(
                target_region=Rect(random.randint(10, 600), random.randint(0, 700), 100, 10),
                label=c
            )
            for c in "abcdefghijklmnopqrstuvwxyz"
        ]

    marker_ui = MarkerUi(_make_markers())
    marker_ui.show()


    def _make_groups():
        import random
        random.seed(0)
        return [
            UnderlineMarkerUi.Group(
                line_rect=line_rect,
                label=c,
                item_rects=[
                    Rect(
                        line_rect.x + w*25,
                        line_rect.y,
                        20,
                        20
                    )
                    for w in range(word_count)
                ]
            )
            for i, c in enumerate("abcdefg")
            for word_count in (random.randint(1, 20),)
            for line_rect in (Rect(
                100,
                i*30,
                word_count*25 - 5,
                20
            ),)
        ]
    marker_ui = UnderlineMarkerUi(_make_groups())
    marker_ui.show()
