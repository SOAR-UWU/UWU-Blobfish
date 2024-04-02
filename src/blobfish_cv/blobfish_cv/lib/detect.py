import cv2

from .classify import find_by_hue, find_by_solidity, find_largest
from .describe import describe_opi
from .filter import filter_by_common, filter_by_hsv, postprocess_noise


def detect(
    im,
    *,
    filter_method,
    filter_common_thres,
    filter_common_s_range,
    filter_common_v_range,
    filter_hsv_lower,
    filter_hsv_upper,
    pp_open,
    pp_close,
    pp_blur,
    opi_small,
    opi_large,
    cls_color_flare,
    cls_color_thres_flare,
    cls_sol_gate,
    cls_sol_thres_gate,
    cls_color_blue,
    cls_color_thres_blue,
    cls_color_red,
    cls_color_thres_red,
    cls_color_yellow,
    cls_color_thres_yellow,
):
    im = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

    # Filter out background.
    if filter_method == "common":
        mask = filter_by_common(
            im,
            thres=filter_common_thres,
            s_range=filter_common_s_range,
            v_range=filter_common_v_range,
        )
    elif filter_method == "hsv":
        mask = filter_by_hsv(im, lower=filter_hsv_lower, upper=filter_hsv_upper)

    # Postprocess noise.
    mask = postprocess_noise(mask, open_val=pp_open, close_val=pp_close, blur=pp_blur)

    # Detect & describe objects.
    objs = describe_opi(im, mask, small_thres=opi_small, large_thres=opi_large)

    # Find objects.
    largest = find_largest(objs)
    flare = find_by_hue(objs, cls_color_flare, cls_color_thres_flare)
    gate = find_by_solidity(objs, cls_sol_gate, cls_sol_thres_gate)
    blue = find_by_hue(objs, cls_color_blue, cls_color_thres_blue)
    red = find_by_hue(objs, cls_color_red, cls_color_thres_red)
    yellow = find_by_hue(objs, cls_color_yellow, cls_color_thres_yellow)

    return dict(
        mask=mask,
        objs=objs,
        largest=largest,
        flare=flare,
        gate=gate,
        blue=blue,
        red=red,
        yellow=yellow,
    )
