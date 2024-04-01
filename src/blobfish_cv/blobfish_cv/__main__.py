import argparse
import os

import cv2
import yaml

from .lib.classify import find_by_hue, find_by_solidity, find_largest
from .lib.describe import describe_opi
from .lib.filter import filter_by_common, filter_by_hsv, postprocess_noise
from .lib.utils import ituple


def detect(
    im,
    *,
    filter_method,
    filter_common_thres,
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
        mask = filter_by_common(im, thres=filter_common_thres)
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


def draw_one(im, obj, color, size):
    cv2.drawContours(im, [obj.contour], -1, color, size)
    cv2.circle(im, ituple(obj.center), size, color, -1)


def visualize(im, res):
    # Image should be BGR.
    im = im.copy()
    for o in res["objs"]:
        draw_one(im, o, (0, 0, 0), 2)  # Black
    if res["largest"] is not None:
        draw_one(im, res["largest"], (0, 255, 0), 3)  # Green
    if res["flare"] is not None:
        draw_one(im, res["flare"], (0, 128, 255), 2)  # Orange
    if res["gate"] is not None:
        draw_one(im, res["gate"], (128, 255, 128), 2)  # Light Green
    if res["blue"] is not None:
        draw_one(im, res["blue"], (255, 0, 0), 2)  # Blue
    if res["red"] is not None:
        draw_one(im, res["red"], (0, 0, 255), 2)  # Red
    if res["yellow"] is not None:
        draw_one(im, res["yellow"], (255, 255, 0), 2)  # Yellow
    return im


def get_mtime(path):
    return os.path.getmtime(path)


def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f), get_mtime(path)


def play_vid(args):
    cfg, mtime = load_config(args.cfgpath)
    cap = cv2.VideoCapture(args.path)
    assert cap.isOpened(), "Failed to open video file."
    print("""Controls:
- q: Quit
- d: Next frame (hold)
- a: Previous frame (hold)
- j: Jump to frame (input in terminal)
""")

    try:
        nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        while cap.isOpened():
            _, frame = cap.read()
            cur_idx = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            print(f"FRAME {cur_idx}/{nframes}")

            while True:
                key = chr(cv2.waitKey(1000 // fps) & 0xFF)
                if key == "q":
                    raise KeyboardInterrupt
                elif key == "d":
                    break
                elif key == "a":
                    cap.set(cv2.CAP_PROP_POS_FRAMES, max(cur_idx - 2, 0))
                    break
                elif key == "j":
                    frame = input("Enter frame number here: ")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, int(frame) - 1)
                    break

                if get_mtime(args.cfgpath) > mtime:
                    cfg, mtime = load_config(args.cfgpath)

                res = detect(frame, **cfg)
                mask = res["mask"]
                im = visualize(frame, res)
                cv2.imshow("Detection", im)
                cv2.imshow("Mask", mask)

    finally:
        cap.release()
        cv2.destroyAllWindows()


def play_img(args):
    cfg, mtime = load_config(args.cfgpath)
    frame = cv2.imread(args.path)
    assert frame is not None, "Failed to open image file."

    try:
        while True:
            key = chr(cv2.waitKey(1) & 0xFF)
            if key == "q":
                raise KeyboardInterrupt

            if get_mtime(args.cfgpath) > mtime:
                cfg, mtime = load_config(args.cfgpath)

            res = detect(frame, **cfg)
            mask = res["mask"]
            im = visualize(frame, res)
            cv2.imshow("Detection", im)
            cv2.imshow("Mask", mask)
    finally:
        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="Runs CV Engine")
    parser.add_argument(
        "-m",
        "--mode",
        dest="mode",
        default="p",
        help="Either p for picture or v for video. Defaults to p.",
    )
    parser.add_argument(
        "-c",
        "--config",
        dest="cfgpath",
        default="./params.yaml",
        help="Path to config file. Defaults to ./params.yaml.",
    )
    parser.add_argument(
        "-i",
        "--input",
        dest="path",
        default="./image.jpeg",
        help="Path to video/image file. Defaults to ./image.jpeg.",
    )

    args = parser.parse_args()

    if args.mode == "v":
        play_vid(args)

    else:
        play_img(args)


if __name__ == "__main__":
    main()
