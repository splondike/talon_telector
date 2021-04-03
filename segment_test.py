"""
A file for testing the line and word segmentation algorithm. Not actually used
by Talon
"""

if __name__ == "__main__":
    import cv2
    import numpy as np

    from src.types import Image, Mask, Rect
    from src.mask import calculate_floodfill_mask, calculate_explicit_mask
    from src.cursor import find_cursor_by_difference
    from src.segment import calculate_line_rects, calculate_word_rects


    def load_image(input_filename):
        return Image(cv2.imread(input_filename))


    def save_image(image: Image, output_filename):
        return cv2.imwrite(output_filename, image.data)


    def save_mask(mask: Mask, output_filename):
        # Couldn't work out how to easily turn a mask bitmap into the OpenCV image
        # format with numpy directly... This is fast enough.
        output = np.zeros((mask.data.shape[0], mask.data.shape[1], 3))
        for y in range(mask.data.shape[0]):
            for x in range(mask.data.shape[1]):
                output[y,x,:] = [255, 255, 255] if mask.data[y,x] else [0, 0, 0]
        return cv2.imwrite(output_filename, output)


    def draw_rect(image: Image, rect: Rect):
        cv2.rectangle(image.data, (rect.x1, rect.y1), (rect.x2, rect.y2), (0, 0, 255), 1)


    def draw_word_rectangles(input_filename, output_filename):
        """
        Test function for word bounding box calculations.
        """

        image = load_image(input_filename)
        # mask = calculate_floodfill_mask(
        #     image,
        #     (image.data.shape[1]-10, image.data.shape[0]-10),
        #     # Note that this is BGR, whereas in Talon it will be RGB. Who know's why
        #     # OpenCV does this differenty.
        #     selection_colors=["#e48434"]
        # )
        mask = calculate_explicit_mask(
            image,
            ["#ffffff"],
            # OpenCV does this differenty.
            selection_colors=["#e48434"]
        )
        line_rects = calculate_line_rects(mask)
        word_rects = []
        for line_rect in line_rects:
            line_word_rects = calculate_word_rects(
                mask,
                line_rect
            )
            word_rects += line_word_rects

        for word_rect in word_rects:
            draw_rect(image, word_rect)

        save_image(image, output_filename)


    def find_cursor_position(screenshot_one_filename, screenshot_two_filename, output_filename):
        """
        Test function for determining where the blinking cursor is positioned based on a
        couple of screenshots.
        """

        image_one = load_image(screenshot_one_filename)
        image_two = load_image(screenshot_two_filename)

        maybe_rect = find_cursor_by_difference(image_one, image_two)

        if maybe_rect:
            draw_rect(image_one, maybe_rect)

        save_image(image_one, output_filename)


    draw_word_rectangles("examples/selected-text.png", "/tmp/output.png")
    # find_cursor_position(
    #     "examples/with-cursor.png",
    #     "examples/without-cursor.png",
    #     "/tmp/output.png"
    # )
