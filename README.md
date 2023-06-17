# napari-vesuvius

[napari] plugin to work with [Vesuvius Challenge] data

## Current contributions

### A reader to read in points and image data from a .volpkg file

Use it with:

```
napari path/to/data.volpkg
```

It should prompt you to open the data with the napari-vesuvius plugin and load images as a dask array and point clouds as points layers.

<img width="2103" alt="Screenshot 2023-06-15 at 4 44 17 pm" src="https://github.com/jni/napari-vesuvius/assets/492549/33726abf-299c-422b-81b8-86b0efcfee44">

Alternatively, you can use it directly from Python, IPython, or Jupyter:

```python
import napari
viewer = napari.Viewer(ndisplay=3)  # start in 3D view
layers = viewer.open('path/to/data.volpkg', plugin='napari-vesuvius')
napari.run()  # not needed in IPython or Jupyter
```

### Sample data of the vesuvius campfire dataset

You can use napari-vesuvius to quickly have a look at the [campfire demo
dataset](https://gist.github.com/janpaul123/280262ebce904f7366fe4cc155593e90).

To look at the data, you can either use the napari menu at File > Open Sample >
napari-vesuvius > [Campfire raw data / Campfire reconstructed data]:



(This is the raw x-ray tomography data using the 'minip' projection.)

Or you can use the viewer API directly from Python:

```python
import napari
viewer = napari.Viewer(ndisplay=3)  # start in 3D view
layers = viewer.open_sample('napari-vesuvius', 'campfire/raw')
# or
# layers = viewer.open_sample('napari-vesuvius', 'campfire/rec')
napari.run()  # not needed in IPython or Jupyter
```

## TODO

- read meshes
- clipping planes
- create and save segmentations
- unfold meshes

----------------------------------

## Installation

You can install `napari-vesuvius` via [pip]:

    pip install git+https://github.com/jni/napari-vesuvius.git


## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [Mozilla Public License 2.0] license,
"napari-vesuvius" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[file an issue]: https://github.com/jni/napari-vesuvius/issues

[napari]: https://github.com/napari/napari
[Vesuvius Challenge]: https://scrollprize.org/
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
