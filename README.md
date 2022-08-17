![KeenTools logo](./imgs/KeenTools.png "KeenTools")

# Tutorials for *KeenTools core library*
This repository contains basic information and tutorials on [*KeenTools core library*](#keentools-core-library).

## Tutorials list
Tutorials cover *pykeentools*, but can be applied to any *KeenTools core library* API.
1. [*pykeentools* installation tutorial](./pykeentools_installation_tutorial/README.md);
2. [*TextureBuilder* tutorial](./texture_builder_tutorial/README.md);
3. [*FaceBuilder* basic tutorial](./face_builder_tutorial/README.md);
3. [*FaceBuilder* head reconstruction tutorial](./face_builder_reconstruction_tutorial/README.md);
4. [*precalc* tutorial](./precalc_tutorial/README.md).

## Version notice
Those tutorials are for *KeenTools core library* version **2022.2.0**.

## *KeenTools core library*

*KeenTools core library* is a software library containing methods and classes used by 
[KeenTools](https://keentools.io) products.

### *KeenTools core library* contains:
- `FaceBuilder` class — FaceBuilder implementation, used in *FaceBuilder for Blender* and *FaceBuilder for Nuke*;
- `GeoTracker` class — GeoTracker implementation, used in *GeoTracker for Blender* and *GeoTracker for After Effects*;
- `texture_builder` module, implementing texture building capabilities for arbitrary geometry (used in *Nuke TextureBuilder* and texture building function of *FaceBuilder for Blender*);
- `precalc` module, implementing pre-analysis (i.e. `.precalc` files computation) (used in *GeoTracker* and *FaceTracker*);
- utility classes and methods (e.g. `Geo` class, KeenTools `UpdatesChecker`, e.t.c);
- other classes and methods used in all tools, developed and maintained by KeenTools team. 

### *KeenTools core library* supported programming languages

*KeenTools core library* is written in C++. There are also bindings in Python and C.

There are three API available for *KeenTools core library* users:
- Python *KeenTools core library* bindings (a.k.a. *pykeentools*);
- C *KeenTools core library* bindings (a.k.a. *KeenToolsC*);
- C++ *KeenTools core library* primary interface (a.k.a. *KeenToolsCpp*).

Python *KeenTools core library* bindings are available for download from our website:
[https://keentools.io/download/core](https://keentools.io/download/core).
See [Licensing](#licensing) section for license information.  
*KeenToolsC* and *KeenToolsCpp* are not publicly available. Please contact us if you'd like to use them:
[team@keentools.io](mailto:team@keentools.io?subject=KeenTools%20core%20library%20for%20C%20or%20C++)

### *KeenTools core library* supported platforms

#### Operating systems and architecture
*KeenTools core library* supports Windows (x64), Linux (x64) and macOS (x64 and ARM64 a.k.a. Apple Silicon).

#### Supported Python versions
*pykeentools* is currently available for Python 3.7, 3.9 and 3.10. Python 2 is not supported.
Other Python 3 versions support is possible.

#### Binary compatibility
*KeenTools core library* is using [VFX Reference Platform](https://vfxplatform.com/).
*KeenTools core library* comply to *CY2019 VFX Reference Platform* or *CY2020 VFX Reference Platform*.

*pykeentools* available on our [website](https://keentools.io/download/core) comply to 
*CY2020 VFX Reference Platform*.

## Licensing

*KeenTools core library* is a proprietary software (see [EULA](https://link.keentools.io/eula)).
Contact us if you'd like to use KeenTools core library in your projects:
[team@keentools.io](mailto:team@keentools.io?subject=KeenTools%20core%20library) 

All examples and code snippets available in this repository are available under [MIT license](LICENSE).
