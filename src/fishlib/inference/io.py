"""
Input/output helper functions.
"""

import pathlib

import tifffile
import numpy as np

from ..images.io import read_dicom


def _2d_images_to_array(input_dir: pathlib.Path):
    """
    Convert a directory of TIF images to an array
    """


def convert_input_to_array(input_path: pathlib.Path):
    """
    Convert an input, which could take many forms, into a numpy
    array that we can use for inference.

    The input might either be:
     - a dicom file or 3d TIF (which are easy)
     - a directory containing 2d TIFs (which is a bit harder)

    :param input_path: the input filepath. If this ends in .dcm or .tif we
                       will assume it is a single 3d image; if it is a directory
                       we will assume it contains 2d tif images. 2d images
                       must be stored in lexographical order. Non-TIF files
                       in this directory will be ignored.
    :returns: a 3d array representing the image.

    """
    if input_path.is_dir():
        ...

    if input_path.suffix == ".dcm":
        image, _ = read_dicom(input_path)
        return image

    if input_path.suffix == ".tif":
        return tifffile.imread(input_path)

    raise ValueError(f"Failed to convert {input_path} to array")
