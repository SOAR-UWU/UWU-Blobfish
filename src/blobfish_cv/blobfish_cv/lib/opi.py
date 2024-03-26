"""Google told me that Objects of Potential Interest (OPI) is a real term in robotics.

J-H: Thanks Aryan M, sorry I've code OCD.

TODO:
- Shape-based matching? https://docs.opencv.org/4.x/d5/d45/tutorial_py_contours_more_functions.html#match_shapes
"""

from typing import List, NamedTuple, Tuple, Union

import cv2
import numpy as np

__all__ = ["filter_by_hsv", "OPI", "detect_opi"]


# https://stackoverflow.com/questions/50899692/most-dominant-color-in-rgb-image-opencv-numpy-python
def bincount_app(pixels):  # NC pixels
    col_range = (256, 256, 256)  # generically : a2D.max(0)+1
    a1D = np.ravel_multi_index(pixels.T, col_range)
    return np.unravel_index(np.bincount(a1D).argmax(), col_range)


def filter_by_hsv(
    im, lower_bound: Tuple[int, int, int], upper_bound: Tuple[int, int, int]
):
    # NOTE: J-H: Masking affects the tightness of the contours, & hence color detection accuracy.
    blur = 0  # 27
    # NOTE: 5 seems best for flare, but too much for gate.
    open_val = 2
    close_val = 5

    # See: https://docs.opencv.org/4.x/de/d25/imgproc_color_conversions.html#color_convert_rgb_hsv
    im = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

    # Account for weird cv2 HSV range.
    lower_bound = (lower_bound[0] // 2, *lower_bound[1:])
    upper_bound = (upper_bound[0] // 2, *upper_bound[1:])
    mask = ~cv2.inRange(im, lower_bound, upper_bound)

    # Remove noise (the pool lines)
    if open_val > 0:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_val, open_val))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Fix the gate "strips are boundaries" issue
    if close_val > 0:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_val, close_val))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    if blur > 0:
        mask = cv2.GaussianBlur(mask, (blur, blur), 0)

    return im, mask


# J-H: checked the types below are correct based on latest cv2 4.x docs.
class OPI(NamedTuple):
    contour: np.ndarray  # ND: N is points, D is 2.
    area: float
    center: Tuple[float, float]
    convex: np.ndarray  # ND: N is points, D is 2.
    convex_area: float
    # NOTE: We use upright bbox assuming the submersible is always upright.
    bbox: Tuple[int, int, int, int]  # xywh
    solidity: float  # I expect the gate will have very low solidity.
    mask: np.ndarray  # bitmask
    color: Union[Tuple[int, int, int], None]  # mean


def detect_opi(
    im, lower_bound: Tuple[int, int, int], upper_bound: Tuple[int, int, int]
):
    im, mask = filter_by_hsv(im, lower_bound, upper_bound)
    too_large = 0.7 * im.shape[0] * im.shape[1]
    too_small = 0.005 * im.shape[0] * im.shape[1]
    color_sd_thres = 90

    # https://docs.opencv.org/4.x/d9/d8b/tutorial_py_contours_hierarchy.html
    # NOTE: Use CHAIN_APPROX_NONE; Using the exact bounds detected helps...
    cnt, h = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    # TODO: Is there use for hiearchy instead of default to external?
    # TODO: Contours describe only the boundary, can I filter out contours that "don't contain anything"?

    # Extract information useful for classification.
    # See: https://docs.opencv.org/4.x/dd/d49/tutorial_py_contour_features.html
    # See: https://docs.opencv.org/4.x/d1/d32/tutorial_py_contour_properties.html
    arr: List[OPI] = []
    for c in cnt:
        M = cv2.moments(c)
        area = M["m00"]
        if area < too_small or area > too_large:
            continue

        center = (M["m10"] / M["m00"], M["m01"] / M["m00"])
        convex = cv2.convexHull(c)
        convex_area = cv2.contourArea(convex)
        bbox = cv2.boundingRect(c)
        solidity = area / convex_area

        cmask = np.zeros_like(mask)
        cv2.drawContours(cmask, [c], 0, 255, -1)
        # NOTE: Difficult to tune, too much trouble.
        # color, sd = cv2.meanStdDev(im, mask=cmask)
        # if sd[0] > color_sd_thres:  # NOTE: cv2's hue range is halved, this affects sd
        #     color = None
        # else:
        #     h, s, v = bincount_app(im[cmask.astype(bool)])
        #     color = (h * 2, s, v)
        h, s, v = bincount_app(im[cmask.astype(bool)])
        color = (h * 2, s, v)

        arr.append(
            OPI(
                contour=c,
                area=area,
                center=center,
                convex=convex,
                convex_area=convex_area,
                bbox=bbox,
                solidity=solidity,
                mask=cmask,
                color=color,
            )
        )
    return arr, mask
