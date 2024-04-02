"""Google told me that Objects of Potential Interest (OPI) is a real term in robotics.

J-H: Thanks Aryan M, sorry I've code OCD.

TODO:
- Shape-based matching? https://docs.opencv.org/4.x/d5/d45/tutorial_py_contours_more_functions.html#match_shapes
"""

from typing import List, NamedTuple, Tuple, Union

import cv2
import numpy as np

from .utils import bincount_app

__all__ = ["OPI", "describe_opi"]


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
    color: Union[Tuple[int, int, int], None]  # modal range


def describe_opi(
    im: np.ndarray,
    mask: np.ndarray,
    *,
    small_thres=0.005,
    large_thres=0.7,
):
    """Detect Objects of Potential Interest (OPI).

    Args:
        im (np.ndarray): HWC HSV image.
        mask (np.ndarray): Object bitmask.
        small_thres (float): Filter objects with relative area smaller than this.
        large_thres (float): Filter objects with relative area greater than this.

    Returns:
        List[OPI]: Detected objects.
    """

    too_small = small_thres * im.shape[0] * im.shape[1]
    too_large = large_thres * im.shape[0] * im.shape[1]

    # https://docs.opencv.org/4.x/d9/d8b/tutorial_py_contours_hierarchy.html
    # NOTE: Use CHAIN_APPROX_NONE; Using the exact bounds detected helps...
    # cnt, h = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    cnt, h = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_KCOS)

    # TODO: Is there use for hierarchy?
    # NOTE: "Donut-hole" filtering of contours is possible by AND of contour & bitmask,
    # but unnecessary.

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
        # NOTE: Difficult to tune, too much trouble to filter by stddev.
        # color, sd = cv2.meanStdDev(im, mask=cmask)
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
    return arr
