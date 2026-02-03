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
from ..model.model import ModelState, load_model, predict, activation_name
from ..localisation.model import get_model, crop
from ..images.metrics import largest_connected_component


class InferenceError(Exception):
    """
    Something went wrong
    """


@functools.cache
def get_jaw_loc_model(model_name: str, device: str) -> torch.nn.Module:
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


def segment_object(
    segmentor_model: ModelState,
    cropped_ct_scan: np.ndarray,
    *,
    threshold: float | None = 0.5,
    largest_component: bool = True,
) -> np.ndarray:
    """
    Segment an object from a cropped CT scan

    Thresholds the model's output at 0.5, and takes the largest connected component
    after this thresholding.

    :param cropped_ct_scan: 3D CT scan to perform inference on
    :param segmentor_model: trained model for performing segmentation
    :param threshold: either a float, in which case the output is thresholded, or None
                      in which case the model's output is not thresholded and will return
                      a floating-point array rather than a binary mask.
    :param largest_component: whether to take the largest connected component in the
                              predicted mask. A threshold must be provided if this is `True`.

    :returns: a numpy array of model predictions
    :raises: InferenceError if `largest_connected_component` is `True` but no threshold is provided
             (it makes no sense to take the largest connected component of a float image).
    """
    if largest_component and threshold is None:
        raise InferenceError(
            "Cannot take the largest connected component unless model output is thresholded"
        )

    # Get the config from the model
    config = segmentor_model.config

    # Turn the image into a Subject that we can perform inference on
    scaled = data.ints2float(cropped_ct_scan)
    tensor = torch.as_tensor(scaled, dtype=torch.float32).unsqueeze(0)
    subject = tio.Subject(image=tio.Image(tensor=tensor, type=tio.INTENSITY))

    prediction = predict(
        segmentor_model.load_model(set_eval=True),
        subject,
        # Perform inference with the same settings we trained with
        patch_size=data.get_patch_size(config),
        # Hard-code the patch overlap but it would be better if it were
        # in the config
        patch_overlap=(4, 4, 4),
        activation=activation_name(config),
    )

    if threshold is not None:
        prediction = prediction > threshold

    if largest_component:
        prediction = largest_connected_component(prediction)

    return prediction
