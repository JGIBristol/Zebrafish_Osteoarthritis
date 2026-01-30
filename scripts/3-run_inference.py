"""
Run inference with our segmentation pipeline.

There are two steps to the segmentation:
 - locate the object of interest (e.g. the head) and crop it out
 - segment out the bone (e.g. the jaw)
As such, you will need to provide the names of two models to do these two steps.

Saves the cropped TIF and the segmentation mask to the provided location.

To run it on a large dataset of jaws, run:
```
uv run scripts/3-run_inference.py locator my_cool_model -d cuda \
<YOUR RDSF MOUNT POINT>/zebrafish_rdsf/DATABASE/uCT/Wahab_clean_dataset/TIFS/
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
from fishlib.inference import models
from fishlib.images.transform import CropOutOfBoundsError


def main(
    locator_model: str,
    segmentation_model: str,
    input_data: pathlib.Path,
    two_d_images: bool,
    crop_size: int,
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
    # Make out_dir if we need to
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get the models

    # We have multiple input if we have a text file
    # OR if we have a directory not containing 2d images
    # A directory containing 2d images is a single input
    multiple_inputs = (input_data.suffix == "txt") or (
        input_data.is_dir() and not two_d_images
    )

    # Read in input(s)
    #   - turn 2d into array
    #   - turn 3d into array
    #   - turn dicom into array
    # or a list of the above
    # Iterate over objects; make 1-item list if we need to
    # Find object
    # Crop it out
    # Save images

    img_out_dir = out_dir / "imgs"
    mask_out_dir = out_dir / "masks"

    img_out_dir.mkdir(parents=True, exist_ok=True)
    mask_out_dir.mkdir(parents=True, exist_ok=True)

    # Get the input dir
    # TODO this should be provided on the CLI
    config = util.userconf()
    input_dir = (
        pathlib.Path(config["rdsf_dir"])
        / "DATABASE"
        / "uCT"
        / "Wahab_clean_dataset"
        / "TIFS"
    )

    # Get the models
    loc_model = models.get_jaw_loc_model(locator_model_name, device=device)
    seg_model = models.get_jaw_segment_model(device=device)

    for img_path in tqdm(sorted(list(input_dir.glob("*.tif")))):
        name = img_path.name
        if (img_out_dir / name).exists() and (mask_out_dir / name).exists():
            print(f"Skipping {name}")
            continue

        try:
            scan = tifffile.imread(img_path)
        except ValueError as e:
            print(
                f"Error reading {name}; is the tiff file incomplete?\n{str(e)}",
                file=sys.stderr,
            )
            continue

        # Crop the image
        try:
            cropped = models.crop_object(
                loc_model, scan, window_size=tuple([crop_size] * 3)
            )
        except CropOutOfBoundsError as e:
            print(
                f"Error cropping {name}; likely an issue with the jaw localising model\n{str(e)}",
                file=sys.stderr,
            )
            continue

        # Run inference
        prediction = models.segment_jaw(cropped, seg_model)

        # Save
        tifffile.imwrite(img_out_dir / name, cropped)
        tifffile.imwrite(mask_out_dir / name, prediction)


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

*If a directory of 2d images is provided, the slices must be in alphabetical
 order and the `--two-d-images` flag must be provided as well.

 You can't provide a directory of directories of 2D images. Sorry.
             """,
    )

    # Optional args
    parser.add_argument(
        "--two-d-images",
        action="store_true",
        help="Supply this flag if `input_data` points to a directory holding",
    )
    parser.add_argument(
        "--crop-size",
        type=int,
        default=192,
        help="Size of region (in px) to crop around the predicted jaw centre",
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
        "Will be created if it doesnt exist.",
        default=files.script_out_dir() / "3_inference",
        type=pathlib.Path,
    )

    args = parser.parse_args()
    main(**vars(args))
