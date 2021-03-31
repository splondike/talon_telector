from typing import List, NamedTuple

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

    def __init__(self, markers: List[Marker]=[], screen_idx=0):
        self.markers = markers
        self.can = canvas.Canvas.from_screen(ui.screens()[screen_idx])
        self.can.register("draw", self._draw)
        self.can.hide()
        self.visible = False
        self.marker_rects = []

    def show(self):
        self.can.show()
        # Freeze stops draw being called at 60Hz and just uses the initial paint
        self.can.freeze()
        self.visible = True

    def hide(self):
        self.can.hide()
        self.visible = False
        self.marker_rects = []

    def destroy(self):
        self.can.close()

    def set_markers(self, markers):
        self.markers = markers
        if self.visible:
            # Trigger a redraw of the markers. But calling it when hidden makes us
            # visible, so don't do that.
            self.can.freeze()

    def get_marker_rects(self):
        return self.marker_rects

    def _draw(self, canvas):
        paint = canvas.paint
        paint.textsize = 12
        paint.typeface = Typeface.from_name('monospace')
        padding = 2
        min_width = 10
        min_height = 10
        self.marker_rects = []
        for marker in self.markers:
            region = marker.target_region

            # trect.x and .y are the offsets the text is printed at
            _, trect = paint.measure_text(marker.label)

            # Draw the box
            height = max(trect.height, min_height) + 2*padding
            width = max(trect.width, min_width) + 2*padding
            bg_rect = Rect(
                region.x + (region.width - width) // 2 + 0.5,
                region.y + (region.height - height) // 2 + 0.5,
                width,
                height
            )

            paint.style = paint.Style.FILL
            paint.color = 'aaffffff'
            canvas.draw_rect(bg_rect)
            paint.color = 'black'
            # paint.stroke_width = 1
            # paint.style = paint.Style.STROKE
            # canvas.draw_rect(bg_rect)

            # Draw the label
            paint.style = paint.Style.FILL
            canvas.draw_text(
                marker.label,
                bg_rect.x - trect.x + (bg_rect.width - trect.width) / 2,
                bg_rect.y - trect.y + (bg_rect.height - trect.height) / 2
            )

            # Make a note of where we've drawn the markers
            self.marker_rects.append(bg_rect)

if False:
    # Testing code, set above to True to activate
    def _make_markers():
        import random
        random.seed(0)
        return [
            MarkerUi.Marker(
                target_region=Rect(random.randint(10, 800), random.randint(0, 900), 100, 10),
                label=c
            )
            for c in "abcdefghijklmnopqrstuvwxyz"
        ]

    marker_ui = MarkerUi(_make_markers())
    marker_ui.show()
