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

```
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
