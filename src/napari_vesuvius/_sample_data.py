"""
This module is an example of a barebones sample data provider for napari.

It implements the "sample data" specification.
see: https://napari.org/stable/plugins/guides.html?#sample-data

Replace code below according to your needs.
"""
from pathlib import Path
import pooch
from pooch import Unzip
from ._version import version
from ._reader import imreads

fetcher = pooch.create(
    # Use OS default cache folder
    path=pooch.os_cache('napari-vesuvius'),
    base_url='http://dl.ash2txt.org/',
    version=version,
    version_dev='main',
    registry={
        'campfire.zip': 'sha256:5857d1be412b597ce31605100852ddf6ea2946c6c0f7eb5a7cd14bff94cc5324',
    },
)


def fetch_campfire_rec():
    unpack = Unzip(members=['campfire/rec'])
    fnames = fetcher.fetch('campfire.zip', processor=unpack)
    fname = Path(fnames[0]).parent
    image = imreads(fname)
    return [(
        image,
        {'name': 'campfire/rec',
         'metadata': {
             'license': 'CC-BY-NC',
             'license-url': 'https://creativecommons.org/licenses/by-nc/2.0/',
         },
         'rendering': 'attenuated_mip',
         },
        'image',
    )]


def fetch_campfire_raw():
    unpack = Unzip(members=['campfire/raw'])
    fnames = fetcher.fetch('campfire.zip', processor=unpack)
    fname = Path(fnames[0]).parent
    image = imreads(fname)
    return [(
        image,
        {'name': 'campfire/raw',
         'metadata': {
             'license': 'CC-BY-NC',
             'license-url': 'https://creativecommons.org/licenses/by-nc/2.0/',
         },
         'rendering': 'minip',
        },
        'image',
    )]
