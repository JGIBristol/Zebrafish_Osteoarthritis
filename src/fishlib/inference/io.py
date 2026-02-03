"""
Input/output helper functions.
"""

import pathlib
from typing import Generator

import tifffile
import numpy as np

from ..images.io import read_dicom


def _2d_images_to_array(input_dir: pathlib.Path):
    """
    Convert a directory of TIF images to an array
    """
    imgs = [
        tifffile.imread(path)
        for path in sorted(
            list(input_dir.glob("*.tif")) + list(input_dir.glob("*.tiff"))
        )
    ]

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
                pathlib.Path(line.strip()).expanduser().resolve()
                for line in f.readlines()
                if (line.strip() and not line.startswith("#"))
            ]
    return [input_data]


def inference_inputs(
    input_data: pathlib.Path, two_d_images: bool
) -> Generator[tuple[pathlib.Path, np.ndarray], None, None]:
    """
    Get the inputs to run inference on as numpy arrays - both the path and the
    image as a numpy array.

    The inputs can be:
        1) A single image, specified as:
            i) The path to a regular file (3D TIF or DICOM)
            ii) The path to a directory containing 2D TIFs
        2) Multiple images, specified as:
            i) A directory containing regular files (3D TIF or DICOM)
            i) A text file containing paths to regular files

    Yields image arrays one at a time.

    :param input_data: the input data path (either directory or regular file)
    :param two_d_images: whether the input(s) are directories containing 2D images.

    :raises FileNotFoundError: the input file doesn't exist
    :raises FileNotFoundError: if we try to stack 2D images but the directory doesn't contain any
    :raises ValueError: if we are passed a regular file but --two-d-images is set
    :raises ValueError: if we are passed directory containing no 3D TIFs or DICOMs
    """
    if not input_data.exists():
        raise FileNotFoundError(str(input_data))

    for path in _get_paths(input_data):
        if not path.exists():
            raise FileNotFoundError(str(path))

        # Case 1 - regular file
        if path.is_file():
            if two_d_images:
                raise ValueError(
                    f"{path} is not a directory - two-d-images flag supplied with a regular 3D file."
                    "This might be because you tried to supply a text file with a mixture of directories of 2D"
                    "TIFs and 3D images."
                )
            yield path, convert_input_to_array(path)

        # Case 2 - dir of 2D images
        elif two_d_images:
            yield path, convert_input_to_array(path)

        # Case 3 - dir of regular files
        else:
            img_paths = sorted(list(path.glob("*.dcm")) + list(path.glob("*.tif")))
            if not img_paths:
                raise FileNotFoundError(f"No .dcm or .tif files found in {path}")

            for image_path in img_paths:
                yield image_path, convert_input_to_array(image_path)
