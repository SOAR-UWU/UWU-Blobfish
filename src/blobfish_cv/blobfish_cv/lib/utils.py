"""Generic CV utilities. MUST be pure of ROS to support easy testing."""

from typing import Tuple

import numpy as np

__all__ = ["bincount_app", "hue_dist", "hue_dist_im", "ituple", "ftuple"]


def bincount_app(pixels: np.ndarray):
    """Get most common color in list of pixels (can be any color space).

    Taken from:
    https://stackoverflow.com/questions/50899692/most-dominant-color-in-rgb-image-opencv-numpy-python

    Args:
        pixels (np.ndarray): NC list of pixels.

    Returns:
        tuple: Most common color.
    """
    col_range = (256, 256, 256)  # generically : a2D.max(0)+1
    a1D = np.ravel_multi_index(pixels.T, col_range)
    return np.unravel_index(np.bincount(a1D).argmax(), col_range)


def hue_dist(h0: int, h1: int) -> int:
    """Get the distance between two hues."""
    return min(abs(h1 - h0), 360 - abs(h1 - h0))


def hue_dist_im(im: np.ndarray, h: int) -> np.ndarray:
    """Get the distance between two hues."""
    diff = np.abs(im[:, :, 0] - h)
    return np.minimum(diff, 360 - diff)


def ituple(t: Tuple) -> Tuple[int, ...]:
    """Cast tuple elements to int."""
    return tuple(map(int, t))


def ftuple(t: Tuple) -> Tuple[float, ...]:
    """Cast tuple elements to float."""
    return tuple(map(float, t))
