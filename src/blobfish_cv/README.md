# Tuning Instructions

Video/image:

```sh
pip install -r requirements.txt
python -m blobfish_cv -m v -i ./video.mp4
python -m blobfish_cv -i ./image.jpeg
```

Controls:

- `q` to quit
- (video) hold `d` to go forwards
- (video) hold `a` to go backwards
- (video) press `j` to trigger `input()` for frame number
- modify `params.yaml` to live-tune
  - Yes, everything can be changed live without needing to restart or press any keys

Help text:

```txt
usage: __main__.py [-h] [-m MODE] [-c CFGPATH] [-i PATH]

Runs CV Engine

optional arguments:
  -h, --help            show this help message and exit
  -m MODE, --mode MODE  Either p for picture or v for video. Defaults to p.
  -c CFGPATH, --config CFGPATH
                        Path to config file. Defaults to ./params.yaml.
  -i PATH, --input PATH
                        Path to video/image file. Defaults to ./image.jpeg.
```

Colors used:

```py
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
```
