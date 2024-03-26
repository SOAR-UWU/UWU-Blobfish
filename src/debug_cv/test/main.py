import cv2
import numpy as np
import argparse
from cv_engine import cv_engine

def main():

    parser = argparse.ArgumentParser(description="Runs CV Engine")
    parser.add_argument("--show_frame", action="store_true", default=True)
    parser.add_argument("--video_cap", dest="dir", default=".\\pool_test_vid1.mp4")
    parser.add_argument("--show_process", action="store_true", default=False) # for debugging
    parser.add_argument("--mode", dest='mode', default='v')
    parser.add_argument("--img_cap", dest='img', default=".\\imgs\\img_.image_raw_2024-03-20_134828.jpeg")

    args = parser.parse_args()

    if args.mode == 'v':

        cap = cv2.VideoCapture(args.dir)
        en = cv_engine()

        while cap.isOpened():

            _, frame = cap.read()
            f, pr = en.detect_contours(frame)
            # hsv = en.hsv_processing()

            if args.show_frame:
                cv2.imshow('Obstacle Detection', f)

            if args.show_process:
                cv2.imshow('Processed Image', pr)

            # cv2.imshow('HSV', hsv)

            if cv2.waitKey(1) & 0xff == ord('q'):
                cleanup(cap)
                break

    else:

        img = cv2.imread(args.img)
        en = cv_engine()

        f, pr = en.detect_contours(img)
        if args.show_frame:
            cv2.imshow('Obstacle Detection', f)
        if args.show_process:
            cv2.imshow('Processed Frame', pr)

        cv2.waitKey(0)

def cleanup(cap):
    cv2.destroyAllWindows()
    cap.release()

if __name__ == "__main__":
    main()