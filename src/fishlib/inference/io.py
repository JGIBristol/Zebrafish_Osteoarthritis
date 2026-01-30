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
    imgs = [tifffile.imread(path) for path in input_dir.glob("*.tif")]

    if not imgs:
        raise FileNotFoundError(f"No tifs found in {input_dir}")

    retval = np.stack(imgs, axis=0)
    assert retval.ndim == 3, (
        f"Stacked image in {input_dir} have shape {retval.shape}."
        "Did you accidentally pass a directory of 3D TIFs with the --two-d-images flag?"
    )

    return retval


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
        # If it is a directory, then it must contain 2d images
        return _2d_images_to_array(input_path)

    if input_path.suffix == ".dcm":
        # Discard the label
        image, _ = read_dicom(input_path)
        assert image.ndim == 3, f"{input_path} is not a 3D DICOM but has {image.shape=}"
        return image

    if input_path.suffix == ".tif":
        # If it is a single TIF, it must be 3D
        image = tifffile.imread(input_path)
        assert image.ndim == 3, f"{input_path} is not a 3D TIF but has {image.shape=}"
        return image

    raise ValueError(f"Failed to convert {input_path} to array")


def _get_paths(input_data: pathlib.Path) -> list[pathlib.Path]:
    """
    Either return a 1-element list if input_data is a single path to our input data,
    or a list of inputs if if it is a text file
    """
    if input_data.suffix == ".txt":
        with input_data.open("r") as f:
            return [
                pathlib.Path(line.strip())
                for line in f.readlines()
                if (line.strip() and not line.startswith("#"))
            ]
    return [input_data]


def inference_inputs(input_data: pathlib.Path, two_d_images: bool) -> list[np.ndarray]:
    """
    Get the inputs to run inference on as numpy arrays.

    The inputs can be:
        1) A single image, specified as:
            i) The path to a regular file (3D TIF or DICOM)
            ii) The path to a directory containing 2D TIFs
        2) Multiple images, specified as:
            i) A directory containing regular files (3D TIF or DICOM)
            i) A text file containing paths to regular files

    If the input is a single image, will return a 1-item list.

    :param input_data: the input data path (either directory or regular file)
    :param two_d_images: whether the input(s) are directories containing 2D images.

    :raises FileNotFoundError: if we try to stack 2D images but the directory doesn't contain any
    :raises ValueError: if we are passed directory containing no 3D TIFs or DICOMs
    """

