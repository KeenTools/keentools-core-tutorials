# *TextureBuilder* tutorial

## Description
This tutorial covers basic *KeenTools core library* data types (like `img` and transformation matrices) 
and basic example of using *TextureBuilder*.

## Recap
1. Problem statement;
2. `img` data type;
3. `pykeentools.Geo` class;
4. *pykeentools* transformation and projection matrices;
5. `pykeentools.ProgressCallback` class;
6. `pykeentools.texture_builder.build_texture` function;
7. Summarize.


## *TextureBuilder* step-by-step tutorial
### 1. Problem statement
We have an image of a known geometry taken with a known camera from a known position:
![rendered plane image](./src/rendered_plane.jpg "rendered plana")

We need to get a texture for that geometry from the image:
![result texture](./built_texture_example.jpg "texture")

We can use `pykeentools.texture_builder` module to do so.

### 2. `img` data types
*KeenTools core library* uses images for different applications, including *TextureBuilder*.

#### The most common image types are:
- `byte_img` — 1 channel `uint8` `np.array` (e.g. `np.zeros((480, 640, 1), dtype=np.uint8)`);
- `img3f` — 3 channel RGB `float32` `np.array` (e.g. `np.zeros((480, 640, 3), dtype=np.np.float32)`);
- `img` — 4 channel RGBA `float32` `np.array` (e.g. `np.zeros((480, 640, 4), dtype=np.np.float32)`).

#### Values and colors
Values in `float32` images are expected to be in range `[0.0, 1.0]`. 
Color, where applicable, is expected in sRGB colour-space.

Values in `uint8` images are expected to be in range `[0, 255]`. 

#### Image orientation
*KeenTools core library* expects `x` image axis by columns and `y` axis by rows
(e.g. FullHD image will have 1080 rows and 1920 columns).

**Pixel `(0, 0)` should be in the lower left corner** of the image.
Like in Nuke, Blender and other software. Doesn't match other software (like opencv). 

#### Loading images for *TextureBuilder*
*TextureBuilder* works with 4 channel RGBA `img`. And returns a 4 channel RGBA `img` as the result.

In this tutorial to load `img` for *TextureBuilder* we will use `cv2` (opencv).

When images are loaded by opencv their channels are in BGR order (instead on RGB).
Also, opencv orients images differently. In opencv pixel `(0, 0)` is in the upper left corner.

To convert image from format used by opencv to format used by *pykeentools* we need to 
flip image vertically and change channels from BGR to RGB.

Here is a function to load an RGB image with opencv and convert in to image expected by *TextureBuilder*.
We load image, add alpha channel, change channels order and flip the image:
```python
import cv2

def _load_image(image_path: str):
    return cv2.flip(cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGBA), 0)
```

And here is the function that saves image in *pykeentools* format to a file. 
We do the same transformations backwards:
```python
import cv2

def _write_image(image_path: str, img: np.array):
    cv2.imwrite(image_path, cv2.flip(cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA), 0))
```


### 3. `pykeentools.Geo` class

`pykeentools.Geo` class is used to represent geometry in *pykeentools* 
(for example in `pykeentools.FaceBuilder`).

`pykeentools.Geo` consists of multiple `pykeentools.Mesh`-es.

`pykeentools.Mesh` is a simple geometry, consisting of:
- points;
- faces;
- attributes (uvs and normals),

`pykeentools.Mesh` is a non-modifiable object so there is also a helped class to create `Mesh` called
`pykeentools.MeshBuilder`.

#### Creating plane geometry for *TextureBuilder*

Here is a function that builds a single face, XY axis oriented, 1x1 sized plane geometry with uv 
coordinates to be used in *TextureBuilder*:
```python
import numpy as np
import pykeentools as pkt

def _build_plane_geo() -> pkt.Geo:
    mesh_builder = pkt.MeshBuilder()
    mesh_builder.add_point(np.array([0.5, -0.5, 0]))
    mesh_builder.add_point(np.array([0.5, 0.5, 0]))
    mesh_builder.add_point(np.array([-0.5, 0.5, 0]))
    mesh_builder.add_point(np.array([-0.5, -0.5, 0]))
    mesh_builder.add_face([0, 1, 2, 3])
    mesh_builder.set_uvs_attribute(
        attribute_type='POINT_BASED',
        uvs=[
            np.array([1.0, 0.0]),
            np.array([1.0, 1.0]),
            np.array([0.0, 1.0]),
            np.array([0.0, 0.0])
        ])

    geo = pkt.Geo()
    geo.add_mesh(mesh_builder.mesh())

    return geo
```

### 4. *pykeentools* transformation and projection matrices
*KeenTools core library* uses 4x4 matrices to represent both 
transformations in 3D space (rotations, translations) and
projection matrices (camera inner parameters). Similar to OpenGL and many other software and libraries.

You may read more on matrices in 
[OpenGL Matrices tutorial](https://www.opengl-tutorial.org/beginners-tutorials/tutorial-3-matrices/).

#### Scale and skew
Almost everywhere in *KeenTools core library* transformation matrices (model, view matrices)
are expected to contain rotation and translation transformations only (no scale or skew).

#### Projection matrices
Camera in *KeenTools core library* is oriented like in Nuke, Blender, OpenGL and other software.
Z axis points backwards, X — right, Y — up.  
Doesn't match other software (like opencv).

Projection matrix should transform from camera space to image space (in pixels).

#### Building model, view and projection matrices for *TextureBuilder*

We are going to use identity `np.eye(4)` as a model matrix as we know our geometry is not transformed.

This function creates view matrix given known camera position (0, 0, 5) and z-axis rotation (45°):
```python
import numpy as np
import math

def _build_view_matrix():
    return np.array(
        [[math.cos(-math.pi / 4), -math.sin(-math.pi / 4), 0, 0],
         [math.sin(-math.pi / 4), math.cos(-math.pi / 4), 0, 0],
         [0, 0, 1, -5],
         [0, 0, 0, 1]])
```
Notice how view matrix is inverse to camera position.

This function uses `pykeentools.math.proj_mat` function to build a projection matrix from known camera
focal length, horizontal aperture and image format:
```python
import pykeentools as pkt

def _build_proj_matrix():
    return pkt.math.proj_mat(fl_to_haperture=50.0/36, w=1280.0, h=720.0,
                             pixel_aspect_ratio=1.0, near=0.1, far=1000.0)
```

### 5. `pykeentools.ProgressCallback` class

`ProgressCallback` is a simple class you should derive to get progress callbacks from some functions in
*KeenTools core library*.

Here is a `ProgressCallback` class we're going to use for texture building in this tutorial:
```python
import pykeentools as pkt

class ProgressCallback(pkt.ProgressCallback):
    def set_progress_and_check_abort(self, progress):
        print('building texture ...%2.1f%% done' % (progress * 100, ))
        return False  # return True if operation should be cancelled
```

### `pykeentools.texture_builder.build_texture` function
`pykeentools.texture_builder.build_texture` function is used to build texture. Here is its signature:
```python
def build_texture(
        frames_count: int,
        frame_data_loader: Callable[[int], Optional[pykeentools.texture_builder.FrameData]],
        progress_callback: pykeentools.ProgressCallback,
        texture_h: int = 1080, texture_w: int = 1920,
        face_angles_affection: float = 10.0,
        uv_expand_percents: float = 0.1,
        back_face_culling: bool = True,
        equalize_brightness: bool = False, equalize_colour: bool = False,
        fill_face_texture: bool = False) -> Optional[img]:
    pass
```

It has a lot of configuration parameters like `face_angles_affection`. You may read about them in
[TextureBuilder knob reference](https://keentools.io/help/nuke-knobs) on our website.

The main parameters are:
- `frame_count` — how many frames are going to be used to build a texture.
You may use multiple frames to build texture from multiple view angles;
- `frame_data_loader` — a function that should load all data for specified frame index. 
Or `None` if something goes wrong (e.g. failed to read image).

Here is `frame_data_loader` we are going to use:
```python
def frame_data_loader(frame: int) -> typing.Optional[pkt.texture_builder.FrameData]:
    assert(frame == 0)  # only one frame should be requested
    frame_data = pkt.texture_builder.FrameData()
    frame_data.geo = _build_plane_geo()
    frame_data.image = _load_image(rendered_card_path)
    frame_data.model = np.eye(4)
    frame_data.view = _build_view_matrix()
    frame_data.projection = _build_proj_matrix()
    return frame_data
```
It loads:
- geometry (which can be animated. Fo example in `FaceBuider` with non-neutral expressions enabled);
- image (in example we only have one frame);
- model, view and projection matrices in that frame (can all be different in different frames).

### 7. Summarize
Now we have all the building blocks we need to load image, create plane geometry, create model, view 
and projecting matrices and build a texture using `pykeentools.texture_builder.build_texture` function.

You can find the whole code combined in [src/main.py](./src/main.py). 
Do not forget to [install pykeentools](./../pykeentools_installation_tutorial/README.md) and 
`pip install -r requirements.txt` before running.
