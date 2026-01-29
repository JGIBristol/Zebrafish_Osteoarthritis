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

import pathlib
import argparse


def main(
    locator_model: str,
    segmentation_model: str,
    input_data: str,
    two_d_images: bool,
    crop_size: int,
    device: str,
    output_dir: pathlib.Path,
):
    """
    """
    # Make out_dir if we need to
    output_dir.mkdir(parents=True, exist_ok=True)



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
        type=str,
        help="""Which data to run the segmentation pipeline on. Can be:
  - the path to a DICOM file (ending in .dcm)
  - the path to a .tif image (ending in .tif)
  - the path to a directory holding 3d tif images
  - the path to a directory holding 2d tif images*
  - a text file containing paths to .tif images, either:
        - paths to 3D tif images
        - paths to directories containing 2D tif images*

*If a directory of 2d images is provided, the slices must be in alphabetical
 order and the --two-d-images flag must be provided below.
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
