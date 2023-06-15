"""Read .volpkg data."""
from dataclasses import dataclass
from typing import Protocol, Tuple
from pathlib import Path
import imageio.v3 as iio
import dask
import dask.array as da
import toolz as tz
import re
import numpy as np
from vispy.io import read_mesh


def napari_get_reader(path):
    """A basic implementation of a Reader contribution.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # we are only going to look at the first file.
        path = path[0]

    # if we know we cannot read the file, we immediately return None.
    if not path.endswith(".volpkg"):
        return None

    # otherwise we return the *function* that can read ``path``.
    return read_volpkg


def read_volpkg(path):
    path = Path(path)
    list_vpcs = path.glob('paths/*/pointset.vcps')
    points = [read_vcps(p) for p in list_vpcs]
    list_volumes = path.glob('volumes/*')
    images = [(imreads(p), {'name': p.name}, 'image') for p in list_volumes]
    list_meshes = path.glob('paths/*/*.obj')
    surfaces = [read_mesh_extra(p) for p in list_meshes]
    return images + points + surfaces


class ImagePropertiesProto(Protocol):
    shape : Tuple[int]
    dtype : type


@dataclass
class ImageProperties:
    shape : Tuple[int]
    dtype : type


def image_properties(filename) -> ImagePropertiesProto:
    """Return the shape and dtype of the image data in filename.

    This function uses iio.v3.improps."""
    return iio.improps(filename)


@tz.curry
def image_properties_loaded(filename, load_func=iio.imread) -> ImageProperties:
    loaded = load_func(filename)
    return ImageProperties(shape=loaded.shape, dtype=loaded.dtype)


@tz.curry
def _load_block(files_array, block_id=None,
        *,
        n_leading_dim,
        load_func=iio.imread):
    image = np.asarray(load_func(files_array[block_id[:n_leading_dim]]))
    return image[(np.newaxis,) * n_leading_dim]


def _find_shape(file_sequence):
    n_total = len(file_sequence)
    parents = {p.parent for p in file_sequence}
    n_parents = len(parents)
    if n_parents == 1:
        return (n_total,)
    else:
        return _find_shape(parents) + (n_total // n_parents,)


def imreads(root, pattern='*.tif', load_func=iio.imread, props_func=None):
    """Read images from root (heh) folder.

    Parameters
    ----------
    root : str | pathlib.Path
        The root folder containing the hierarchy of image files.
    pattern : str
        A glob pattern with zero or more levels of subdirectories. Each level
        will be counted as a dimension in the output array. Directories *must*
        be specified with a forward slash ("/").
    load_func : Callable[Path | str, np.ndarray]
        The function to load individual arrays from files.
    props_func : Callable[Path | str, ImageProperties]
        A function to get the array shape from a file. If omitted, `load_func`
        is called on the first file to get the shape. In some cases,
        `image_properties` is the most efficient function here and may avoid
        loading a large image into memory.

    Returns
    -------
    stacked : dask.array.Array
        The stacked dask array. The array will have the number of dimensions of
        each image plus one per directory level.
    """
    if props_func is None:
        if load_func is not iio.imread:
            props_func = image_properties_loaded(load_func=load_func)
        else:
            props_func = image_properties
    root = Path(root)
    files = sorted(root.glob(pattern))
    if len(files) == 0:
        raise ValueError(
                f'no files found at path {root} with pattern {pattern}.'
                )
    leading_shape = _find_shape(files)
    n_leading_dim = len(leading_shape)
    props = props_func(files[0])
    lagging_shape = props.shape
    files_array = np.array(list(files)).reshape(leading_shape)
    chunks = tuple((1,) * shp for shp in leading_shape) + lagging_shape
    stacked = da.map_blocks(
            _load_block(n_leading_dim=n_leading_dim, load_func=load_func),
            files_array,
            chunks=chunks,
            dtype=props.dtype,
            )
    return stacked


def extract_dimensions(string):
    """Grab the array dimensions from the .vcps header string."""
    height_match = re.search(r'height: (\d+)', string)
    width_match = re.search(r'width: (\d+)', string)
    ndim_match = re.search(r'dim: (\d+)', string)

    if height_match and width_match and ndim_match:
        height = int(height_match.group(1))
        width = int(width_match.group(1))
        ndim = int(ndim_match.group(1))
        return height, width, ndim
    else:
        return None


def read_until(fin, suffix):
    """Read bytes until we have read some substring or we're out of data."""
    output = b''
    last_read = b'dummy'
    while output[-len(suffix):] != suffix and last_read != b'':
        last_read = fin.read(1)
        output += last_read
    return output.decode()


def read_vcps(path):
    """Read the Volume Cartographer point cloud data

    Parameters
    ----------
    path : str or pathlib.Path
        Path to .vcps file.

    Returns
    -------
    layer_data : tuple(np.ndarray, dict, str)
        layer data containing the point coordinates, the name of the point
        cloud, and the layer type ('points').
    """
    with open(path, mode='rb') as fin:
        prefix = read_until(fin, suffix=b'<>\n')
        shape = extract_dimensions(prefix)
        point_data = np.frombuffer(fin.read(), dtype=np.float64,
                                   count=np.product(shape)).reshape(shape)

    # we transpose to napari pln/row/col coordinates, and discard "rows"
    flipped = np.flip(point_data, axis=-1)
    reshaped = np.reshape(flipped, (-1, shape[-1]))
    name = Path(path).parent.name
    return reshaped, {'name': name}, 'points'


def read_mesh_extra(path):
    """Read a mesh and its associated texture (if present)."""
    p = Path(path)
    vertices, faces, normals, texcoords = read_mesh(p.as_posix())
    texture = None
    image_path = (p.parent / p.stem).with_suffix('.tif')
    if image_path.exists():
        texture = iio.imread(image_path.as_posix())
    layer_data = (vertices, faces)
    layer_data_tuple = (
            layer_data,
            {'name': p.stem, 'texture': texture, 'texcoords': texcoords},
            'surface',
    )
    return layer_data_tuple