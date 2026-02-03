Run Inference
====
Run inference using our pipeline on some data.

This, in principle, is a very general script - it, in principle,
can be pointed to models that run inference to segment out any object
from the scans.  
At the moment, though, it's only set up for use with the jaw segmentation pipeline.

## Usage
To see detailed instructions on how to use this script, run:
```
uv run scripts/3-run_inference.py --help
```

More explanations:
<details>
<summary>Command Line Arguments</summary>
This script accepts a number of command line arguments:

 1. **The locator model**: as a string, just the name of the model in the same way it was provided on the CLI when running `1-train_jaw_locator.py`. The `example_locator` model is provided with this repo.
 2. **The segmentation model**: as a string, with .pkl at the end, in the same way it was provided in `userconf.yml` when
 running `2-train_jaw_segmenter.py`.
 3. **The input data** there are lots of ways to specify this, see below...
 4. Some optional arguments, see below...

It's a bit ugly that the two models are specified in slightly different ways, but you'll get used to it.

</details>

<details>
<summary>Input data</summary>

## Providing Input Data
The input data can be provided in a number of ways.

There are two reasons you might want to do inference:
 1. Run inference on one CT scan - to check the model works, or to explore something.
 2. Run inference on lots of them - to build up a dataset of segmented scans.

### One scan
You the `input_data` argument should just be the path to this scan.

This can be a path to:
<ol type="a">
  <li> a 3D .tif image (ending in .tif) </li>
  <li> a DICOM file (ending in .dcm)    </li>
  <li> a directory holding 2d tif images </li>
</ol>

In this last case, the optional flag `--two-d-images` should also be set.

### Several scans

The input data can also be several images.

This can be specified by providing a path to:
<ol type="a">
  <li> a directory containing multiple 3D scan images (either TIFs, DICOMs or a mixture) </li>
  <li> a text file (see below)
</ol>
You can't provide a directory containing multiple directories of 2D images.

#### Text file format
This is the most reproducible (you get record of what input data you used!)
way to run this script.

The path to the text file must have a `.txt` extension; it can contain:
- paths to input data
- blank lines
- comments (lines starting with `#`).

The input data paths can be any of the above types of data; the only restriction is that it cannot contain a mixture of directories containing 2D TIFs and other data types.
I.e. the text file can contain:
 - a list of paths to 3D TIF and/or DICOM images and/or directories containing them
 - a list of directories which each contain 2D TIF images to be stacked.

In the second of these cases, the `--two-d-images` flag should be set.
</details>

<details>
<summary>Optional arguments</summary>

There are also a series of optional arguments that you *may* want to set, but don't necessarily need to:
- `--two-d-images`: whether the input is a directory(ies) containing 2D TIFs to be stacked
- `--crop-size`: the size of the region that will be cropped out by the locating model. This could, in principle, be attached to the model itself so that it knows what size image to crop out, but that would require some refactoring.
- `--device`/`-d`: whether to run on CUDA (GPU) or CPU.
- `--output-dir`/`-o`: where the cropped images/segmentation masks will go. Note that the results will be stored in `<output_dir>/imgs/<name>.tif` and
`<output_dir>/masks/<name>.tif` for an input file called `<name>.dcm`, `<name>.tif`, `<name>/`, etc.
</details>

## EXAMPLES
> [!TIP]
> The examples in this section assume you have mounted the Zebrafish_Osteoarthritis RDSF at `~/MY_RDSF_MOUNT/`.
> Change it to your actual mount point to run these.

> [!NOTE]
> The `example_locator` and `example_segmenter` models weights are provided as part
> of this git repo.

#### Run on a single 3D TIF image
```
uv run scripts/3-run_inference.py example_locator example_segmenter.pkl ~/MY_RDSF_MOUNT/DATABASE/uCT/Wahab_clean_dataset/TIFS/ak_1.tif --output-dir 3d_tif_example
```

#### Run on a stack of 2D TIF images
```
uv run scripts/3-run_inference.py example_locator example_segmenter.pkl ~/MY_RDSF_MOUNT/DATABASE/uCT/Wahab_clean_dataset/low_res_clean_v3/040/reconstructed_tifs/ --two-d-images --output-dir 2d_stack_example
```

#### Run on several 3D TIF images
```
uv run scripts/3-run_inference.py example_locator example_segmenter.pkl ~/MY_RDSF_MOUNT/DATABASE/uCT/Wahab_clean_dataset/TIFS/ --output-dir several_tifs_example
```

#### Run on several 3D TIF images, using a text file to specify paths
```
uv run scripts/3-run_inference.py example_locator example_segmenter.pkl my_inputs.txt --output-dir 3d_tifs_from_txt_example
```
<details>
<summary>my_inputs.txt</summary>

```
~/MY_RDSF_MOUNT/DATABASE/uCT/Wahab_clean_dataset/TIFS/ak_1.tif
~/MY_RDSF_MOUNT/DATABASE/uCT/Wahab_clean_dataset/TIFS/ak_2.tif
~/MY_RDSF_MOUNT/DATABASE/uCT/Wahab_clean_dataset/TIFS/ak_3.tif
```
</details>

#### Run on several 2D image stacks, using a text file to specify paths
```
uv run scripts/3-run_inference.py example_locator example_segmenter.pkl my_inputs.txt --output-dir 2d_tifs_from_txt_example --two-d-images
```
<details>
<summary>my_inputs.txt</summary>

```
~/MY_RDSF_MOUNT/DATABASE/uCT/Wahab_clean_dataset/low_res_clean_v3/040/reconstructed_tifs/
```
</details>

> [!WARNING]
> This last example only uses one 2D TIF stack as input. This is because all the
> outputs from these images will have the same names.
>
> All the TIFs in the `Wahab_clean_dataset` directory are in subdirectories
> called `reconstructed_tifs`. This means that the segmentations/images will all
> be saved to `reconstructed_tifs.tif`.
>
> If you want to run the inference on all of these 2D stacks, the best thing
> might be to write a script to loop over them saving them to different output
> directories.
