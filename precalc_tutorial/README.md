# *precalc* tutorial

## Description
This is a basic tutorial about `pykeentools.precalc` module.


### 1. Intro
`pykeentools.precalc` module contains methods for computing and working with pre-analysis files (`.precalc`).

Pre-analysis files are used for tracking (e.g. in `GeoTracker` and `FaceTracker`).

### 2. Computing `.precalc` files
Let's start by implementing a function that computes `.precalc` file by a sequence of images:
```python
def _compute_precalc(sequence_dir: str, out_precalc_path: str):
    pass
```


The method we should use for creating pre-analysis files is `pykeentools.precalc.calculate`:
```python
def calculate(file_name: str,
              format_width: int, format_height: int, 
              from: int, to: int, 
              calculation_client: pykeentools.precalc.CalculationClient,
              license_manager: pykeentools.LicenseManager, use_gpu_if_available: bool = True)
```

To run it we should provide it with:
- `file_name` — a file path to save `.precalc` file to (existing files will be overwritten);
- `format_width`x`format_height` — image size (it's expected to be the same for all frames);
- `[from, to]` — frame range used for `.precalc` calculation;
- `calculation_client` — an object used to load images and report calculation progress;
- `license_manager` — a license manager this calculation relates to 
(should be one of the suitable for precalc licenses. Currently `GeoTracker` and `FaceTracker`);
- `use_gpu_if_available` — flag controls if a GPU should be used for calculation.

Let's assume the sequence is small, so we can read it all in memory:
```python
import pykeentools as pkt
import cv2
import os


def _load_image_for_precalc(image_path: str):
    rgb_image = cv2.flip(cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB), 0) / 255.0
    return pkt.prepare_for_precalc(rgb_image)


def _read_sequence(sequence_dir: str):
    frame_to_image = dict()
    for img_file in os.listdir(sequence_dir):
        img_name, _ = os.path.splitext(img_file)
        frame_number = int(img_name)
        img_path = os.path.join(sequence_dir, img_file)
        frame_to_image[frame_number] = _load_image_for_precalc(img_path)
```
Unlike *TextureBuilder*, precalc is expecting `byte_img`, so `_load_image_for_precalc` looks different.
We could have converted bgr to `byte_img` directly using `cv2.cvtColor`, but there is a 
`pkt.prepare_for_precalc` function that is recommended to use for image pre-processing before precalc.
It accepts RGB `img3f` and returns a `byte_img`.

Now we can write our `pykeentools.precalc.CalculationClient`:
```python
class _CalculationClient(pkt.precalc.CalculationClient):
    def __init__(self, frame_to_image):
        super().__init__()
        self.frame_to_image = frame_to_image

    def on_progress(self, progress, progress_message):
        print('Precalc calculation %.1f done (%s)' % (progress * 100, progress_message))
        return True  # return False to stop

    def load_image_at(self, frame):
        assert frame in self.frame_to_image
        return self.frame_to_image[frame]
```
Our `_CalculationClient` returns preloaded images in `load_image_at` and 
prints progress messages in `on_progress`.

Let's combine everything to `_compute_precalc` function:
```python
def _compute_precalc(sequence_dir: str, out_precalc_path: str):
    frame_to_image, frame_from, frame_to = _read_sequence(sequence_dir)
    calculation_client = _CalculationClient(frame_to_image)
    lm = pkt.GeoTracker.license_manager()
    img_shape = frame_to_image[frame_from].shape
    pkt.precalc.calculate(
        out_precalc_path,
        img_shape[1],
        img_shape[0],
        frame_from,
        frame_to,
        calculation_client,
        lm
    )
```


### 3. `pkt.precalc.Info`
`precalc` module also allow us to read some basic information about a `.precalc` file through 
`pkt.precalc.Loader`:
```python
def _print_precalc_info(precalc_file: str):
    precalc_info: pkt.precalc.Info = pkt.precalc.Loader(precalc_file).load_info()
    print('Precalc "%s" info:' % precalc_file)
    print('\tframe range: [%d, %d]' % (precalc_info.left_precalculated_frame, precalc_info.right_precalculated_frame))
    print('\timg format: %dx%d' % (precalc_info.image_w, precalc_info.image_h))
```

### 4. Summary
Now we can combine `_compute_precalc` and `_print_precalc_info` to the next function:
```python
def compute_precalc(sequence_dir: str, out_precalc_path: str):
    _compute_precalc(sequence_dir, out_precalc_path)
    print('Precalc calculation finished!')
    _print_precalc_info(out_precalc_path)
```

In this tutorial we learned how we can pre-analyse a sequence for later tracking with `GeoTracker` or
`FaceTracker`.

This method may be used, for example, to pre-analyse a bunch of sequences on a server to be later used
in any of our tracking tools (e.g. *GeoTracker for Nuke*).

You can find the whole code combined in [src/main.py](./src/main.py). 
Do not forget to [install pykeentools](./../pykeentools_installation_tutorial/README.md) and 
`pip install -r requirements.txt` before running.
