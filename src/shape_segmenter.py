"""
This module loads a given image, prompts the user to identify key points then generates segments
between the selected points

Source for most of the code in ShapeSegmenter:
https://www.tutorialspoint.com/opencv-python-how-to-display-the-coordinates-of-points-clicked-on-an-image

Author: Chris Harris
"""
from pathlib import Path

import cv2

class ShapeSegmenter:
    """
    Given an image, identify key points and divide into straight segments
    """
    def __init__(self, image_location: Path):
        self.img = cv2.imread(str(image_location))
        self.coordinates = []

    def open_coordinate_select_window(self, window_x: int=600, window_y: int=600) -> None:
        """
        Open a window for the user to select key coordinates on their image and store these
        coordinates
        """
        window_name = "Select Coordinates"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, window_x, window_y)

        # bind the callback function to window
        cv2.setMouseCallback(window_name, self._click_event_cb)

        # display the image
        while True:
            cv2.imshow(window_name, self.img)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break
        cv2.destroyAllWindows()

    def _click_event_cb(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            coord = tuple([x, y])
            self.coordinates.append(coord)

            # draw point on the image
            cv2.circle(self.img, (x,y), 3, (0,255,255), -1)

if __name__ == "__main__":
    img_location = Path.home() / "strava-art-generator" / "shape-outlines" / "sunnies.png"
    segmenter = ShapeSegmenter(img_location)
    segmenter.open_coordinate_select_window()
