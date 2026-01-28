"""
Read in full-size CT scans from Wahab's 3D TIF directory, locate the
jaw and segment it out

Saves the cropped jaw TIF and segmentation mask
"""
import argparse


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

    args = parser.parse_args()
    main(**vars(args))
