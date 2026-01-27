"""
Get and use the different models for inference

This should be the only interface needed to interact with the models;
some of the functions here are just thin wrappers around other helper
functions, they're just here to keep everything in one place
"""

import pathlib
import functools

import torch
import numpy as np
import torchio as tio

from ..util import files
from ..model import data
from ..model.model import ModelState, load_model, predict
from ..localisation.model import get_model, crop
from ..images.metrics import largest_connected_component


class InferenceError(Exception):
    """
    Something went wrong
    """


@functools.cache
def get_jaw_loc_model(model_name: str*, device: str) -> torch.nn.Module:
    """
    Get the network used to locate the jaw in a CT scan

    Returned in evaluation mode - i.e. suitable for inference but not
    training.

    :param model_name: name of the jaw locator model, as provided when
                       training the model.
    :param device: "cuda" to run on GPU, else "cpu"

    :returns: the trained model for locating the jaw
    """
    # Get the right architecture
    model = get_model(device)

    # Load the weights into it
    with open(files.jaw_locator_model_path(model_name), "rb") as f:
        model.load_state_dict(torch.load(f))

    # Set into eval mode - we don't need to update weights or anything during
    # inference
    model.eval()
    return model


@functools.cache
def get_jaw_segment_model(segment_model_name: str, *, device: str) -> ModelState:
    """
    Get a segmentation model.

    :param segment_model_name: the name of the segmentation model, as chosen when the model
                               was trained.
    :param device: either "cuda" to run on GPU or "cpu"
    :returns: trained jaw segmentation model
    """
    return load_model(segment_model_name)


def crop_object(
    locator_model: torch.nn.Module,
    ct_scan: np.ndarray,
    *,
    locator_input_size: tuple[int, int, int],
    window_size: tuple[int, int, int],
) -> np.ndarray:
    """
    Crop the region of interest from the CT scan using the model.

    Performs inference on the device that the model is on - this might
    give unexpected results if the model is on multiple devices.

    :param jaw_loc_model: the model used to locate an object in a CT scan
    :param ct_scan: 3D greyscale numpy array - the input data
    :param locator_input_size: the size of the input to the locator model.
                               This model is trained on downsampled images,
                               so we need to downsample the input to this size
                               when we run inference.
    :param window_size: size of the returned cropped image.

    :returns: 3D numpy array of the cropped image
    """
    return crop(
        locator_model,
        ct_scan,
        model_input_size=locator_input_size,
        window_size=window_size,
    )

