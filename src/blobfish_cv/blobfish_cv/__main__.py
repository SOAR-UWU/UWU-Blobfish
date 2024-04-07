import argparse
import os

import cv2
import yaml

from .lib.detect import detect
from .lib.visualize import visualize


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
                key = chr(cv2.waitKey(500 // fps) & 0xFF)
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
