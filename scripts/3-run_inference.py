"""
Run inference with our segmentation pipeline.

There are two steps to the segmentation:
 - locate the object of interest (e.g. the head) and crop it out
 - segment out the bone (e.g. the jaw)
As such, you will need to provide the names of two models to do these two steps.

Saves the cropped TIF and the segmentation mask to the provided location.

EXAMPLE
    To run it on a large dataset of jaws, run:
    ```
    uv run scripts/3-run_inference.py locator my_cool_model.pkl -d cuda \
    <YOUR RDSF MOUNT POINT>/DATABASE/uCT/Wahab_clean_dataset/TIFS/
    ```
    This will use the `locator` and `my_cool_model` models respectively to crop/segment
    each of the scans in Wahab's directory on the RDSF.

"""

import sys
import pathlib
import argparse
import tifffile

from tqdm import tqdm

from fishlib.util import files, util
from fishlib.inference import models, io
from fishlib.images.transform import CropOutOfBoundsError


def main(
    locator_model: str,
    segmentation_model: str,
    input_data: pathlib.Path,
    two_d_images: bool,
    crop_size: int,
    downsampled_input_size: list[int, int, int],
    device: str,
    output_dir: pathlib.Path,
):
    """
    Segment out the data given the provided models and configuration.

    This will:
     - get the requested models
     - read in the input data
     - crop the image to the right size using the locator model
     - segment the objet out from the cropped image
     - save the cropped image and corresponding segmentation mask

    """
    if len(downsampled_input_size) != 3:
        raise ValueError(f"Must have 3D image size, got {downsampled_input_size}")

    # Get the directories where the outputs will be stored, creating them if
    # necessary
    output_dir.mkdir(parents=True, exist_ok=True)

    img_out_dir = output_dir / "imgs"
    mask_out_dir = output_dir / "masks"

    img_out_dir.mkdir(exist_ok=True)
    mask_out_dir.mkdir(exist_ok=True)

    # Get the models
    # TODO make these generic - we might want to use a non-jaw model...
    locator_net = models.get_jaw_loc_model(locator_model, device=device)
    segmentation_net = models.get_jaw_segment_model(segmentation_model, device=device)

    # Read in input(s)
    for path, image in io.inference_inputs(input_data, two_d_images):
        name = path.name
        img_path = (img_out_dir / name).with_suffix(".tif")
        mask_path = (mask_out_dir / name).with_suffix(".tif")
        if img_path.exists():
            raise FileExistsError(f"{img_path} exists; move or delete it")
        if mask_path.exists():
            raise FileExistsError(f"{mask_path} exists; move or delete it")

        try:
            cropped = models.crop_object(
                locator_net,
                image,
                locator_input_size=downsampled_input_size,
                window_size=tuple([crop_size] * 3),
            )
        except CropOutOfBoundsError as e:
            print(
                f"Error cropping {name}; likely an issue with the localising model\n{str(e)}",
                file=sys.stderr,
            )
            continue

        prediction = models.segment_object(segmentation_net, cropped)

        tifffile.imwrite(img_path, cropped)
        tifffile.imwrite(mask_path, prediction)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "locator_model",
        type=str,
        help="The model name used for doing the initial crop.",
    )
    parser.add_argument(
        "segmentation_model", type=str, help="The model name used for the segmentation."
    )
    parser.add_argument(
        "input_data",
        type=pathlib.Path,
        help="""Which data to run the segmentation pipeline on. Can be:
  - the path to a 3D .tif image (ending in .tif)
  - the path to a DICOM file (ending in .dcm).
    This must have the right attributes set - see `fishlib.images.io.read_dicom` for details.
  - the path to a directory holding 2d tif images*

The input data can also be several images:
  - a text file (file extension .txt) where each line is any of the above (relative to the cwd)
  - the path to a directory holding 3d Images (TIF or DICOM)
A text file cannot contain mixtures of 2D TIF directories and regular files.
It must either contain:
  - only directories of 2D TIFs (in which case --two-d-images should be set)
  - or 3D image files and/or directories of them (in which case --two-d-images is not set)
Empty lines and lines starting with # in this file will be ignored.

*If a directory of 2d images is provided, the slices must be in alphabetical
 order and the `--two-d-images` flag must be provided as well.

 You can't provide a directory of directories of 2D images. Sorry.
             """,
    )

    # Optional args
    parser.add_argument(
        "--two-d-images",
        action="store_true",
        help="Supply this flag if `input_data` points to a directory holding 2D TIF images to be stacked",
    )
    parser.add_argument(
        "--crop-size",
        type=int,
        default=192,
        help="Size of region (in px) to crop around the predicted jaw centre",
    )
    parser.add_argument(
        "--downsampled-input-size",
        type=int,
        nargs="+",
        default=(512, 128, 128),
        help="The locator model downsamples the input before inference - specify this here.",
    )
    parser.add_argument(
        "--device",
        "-d",
        choices={"cpu", "cuda"},
        help="Choose 'cuda' if running on GPU",
        default="cpu",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        help="Directory to store outputs, either absolute or relative to the cwd."
        "Will be created if it doesnt exist."
        "Images and masks will be saved to `imgs/` and `masks/` subdirectories of this dir.",
        default=files.script_out_dir() / "3_inference",
        type=pathlib.Path,
    )

    args = parser.parse_args()
    main(**vars(args))
