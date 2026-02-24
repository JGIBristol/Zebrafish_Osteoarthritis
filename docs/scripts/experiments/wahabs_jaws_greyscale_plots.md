Greyscale Plots
====

Wahab left a big dataset of jaws and some associated metadata.

We can make some exploratory plots of these, to look at how the volume/length/greyscale
etc. of them varies with things like age and mutation. It is also a good sanity check
that the segmentation pipeline is working well - if we get nonsensical results here, it might
be because our segmentation pipeline is failing somewhere.

## Usage
I have segmented (some of) Wahab's jaws and left them on the RDSF. This means that you should be able to run
```
uv run scripts/experiments/wahab_jaws_greyscale_plots.py -i ~/zebrafish_rdsf/DATABASE/uCT/Wahab_clean_dataset/TIFS_autosegmented/
```
Assuming you have mounted the RDSF at `~/zebrafish_rdsf`. If you haven't, change the path to the right thing
and it should work.

## Outputs
This script outputs lots of things:
 - scatter plots of age vs volume + age/vol/length against each other
 - a directory of slices through the jaw
 - a directory of 3D projections of the jaws
