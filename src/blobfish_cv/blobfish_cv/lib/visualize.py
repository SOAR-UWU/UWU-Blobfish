import cv2

from .utils import ituple


def draw_one(im, obj, color, size):
    cv2.drawContours(im, [obj.contour], -1, color, size)
    cv2.circle(im, ituple(obj.center), size, color, -1)


def visualize(im, res):
    # Image should be BGR.
    im = im.copy()
    for o in res["objs"]:
        draw_one(im, o, (0, 0, 0), 2)  # Black
    if res["largest"] is not None:
        draw_one(im, res["largest"], (0, 128, 0), 3)  # Dark Green
    if res["flare"] is not None:
        draw_one(im, res["flare"], (0, 128, 255), 2)  # Orange
    if res["gate"] is not None:
        draw_one(im, res["gate"], (128, 255, 128), 2)  # Light Green
    if res["blue"] is not None:
        draw_one(im, res["blue"], (255, 0, 0), 2)  # Blue
    if res["red"] is not None:
        draw_one(im, res["red"], (0, 0, 255), 2)  # Red
    if res["yellow"] is not None:
        draw_one(im, res["yellow"], (0, 255, 255), 2)  # Yellow
    return im
