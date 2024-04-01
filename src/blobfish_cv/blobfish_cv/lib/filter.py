"""Filter out background using various techniques."""

from typing import Tuple, Union

import cv2
import numpy as np

from .utils import bincount_app, hue_dist_im

# TODO:
# - Consider adaptive thresholding: https://docs.opencv.org/4.x/d7/d1b/group__imgproc__misc.html#gae8a4a146d1ca78c626a53577199e9c57
# - since opencv bg removers suck for non-moving target, rembg: https://github.com/danielgatis/rembg
# - barring perf issues, SAM should be best: https://github.com/MrSyee/SAM-remove-background

__all__ = ["filter_by_common", "filter_by_hsv", "postprocess_noise"]


def filter_by_common(im: np.ndarray, thres: Union[int, Tuple[int, int, int]] = 10):
    """Get object bitmask by filtering out most common color.

    Args:
        im (np.ndarray): HWC HSV image.
        thres (int | tuple): Hue difference threshold. If tuple, filter saturation and value too.

    Returns:
        np.ndarray: Object bitmask.
    """
    hthres = thres if isinstance(thres, int) else thres[0]
    sthres = None if isinstance(thres, int) else thres[1]
    vthres = None if isinstance(thres, int) else thres[2]

    h, s, v = bincount_app(im.reshape(-1, 3))

    mask = hue_dist_im(im, h) > hthres
    if sthres is not None:
        mask &= np.abs(im[:, :, 1] - s) > sthres
    if vthres is not None:
        mask &= np.abs(im[:, :, 2] - v) > vthres

    return mask.astype(np.uint8) * 255


def filter_by_hsv(
    im: np.ndarray, lower: Tuple[int, int, int], upper: Tuple[int, int, int]
):
    """Filter out objects by HSV range.

    Args:
        im (np.ndarray): HWC HSV image.
        lower (tuple): Lower bound HSV.
        upper (tuple): Upper bound HSV.

    Returns:
        np.ndarray: Object bitmask.
    """
    # Account for weird cv2 HSV range.
    lower = (lower[0] // 2, *lower[1:])
    upper = (upper[0] // 2, *upper[1:])
    mask = ~cv2.inRange(im, lower, upper)
    return mask


# NOTE: J-H: Masking affects the tightness of the contours, & hence color detection accuracy.
# NOTE: 5 seems best for flare, but too much for gate.
def postprocess_noise(
    mask: np.ndarray, *, open_val: int = 2, close_val: int = 5, blur: int = 0
):
    """Post-process mask.

    Args:
        mask (np.ndarray): HW bitmask.
        open_val (int): Morphological open kernel size.
        close_val (int): Morphological close kernel size.
        blur (int): Blur kernel size.
    """
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

    return mask
