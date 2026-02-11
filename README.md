# Zebrafish_Osteoarthritis
Segmentation and analysis of zebrafish bones.

For the scale morphology study, see https://github.com/JGIBristol/scale_morphology/.  
For the less-neat but more complete original jaw segmentation repository, see https://github.com/JGIBristol/zebrafish_jaw_segmentation.

## Background
The Hammond Lab is interested in how bones develop, heal and grow and how this is affected by things like
gene expression, time of day, age, sex...
They're also interested in their morphology and mechanical properties.

Zebrafish are a useful model organism (for a number of reasons), and the group has a large dataset of
CT scanned zebrafish. Segmenting bones from these scans takes a very long time - each CT scan contains
around 2000 2d-image slices, manually labelling of which takes a very long time.

AI methods in image segmentation are well established; this repository stores the code for segmentation.

## Setup Guide
This code was developed and run on Ubuntu 22.04 - it might work on other platforms, but you might need to change some things.
If you're on Windows, I'd suggest using [WSL](https://learn.microsoft.com/en-us/windows/wsl/install).

### Environment
The python environment here is managed with `uv`.
To install `uv`, see [the instructions](https://docs.astral.sh/uv/getting-started/installation/).

Once you have installed `uv`, set up the python environment by running
```
uv sync
```
from the root of this repository.

## Inference
This repository comes with some pre-trained models for segmenting out the jawbone - if you just want to run inference on some
scans, start here.

The user interface is provided here as a collection of python scripts, stored in `scripts/`, see:
- the documentation for the inference script [here](./docs/scripts/3-run_inference.md).
- the source code [here](./scripts/3-run_inference.py).

## Training your own models

### Data
<details>
<summary>
You will need access to the RDSF to train your own models.
</summary>

This is where the raw data lives, and is accessible only to
Univeristy of Bristol researchers. Ask your PI to give you access to the Zebrafish_Osteoarthritis partition.

Mount the RDSF in the usual way - one way that doesn't require superuser is
```
gio mount smb://rdsfcifs.acrc.bris.ac.uk/Zebrafish_Osteoarthritis
```
This will mount the RDSF somewhere like `/run/user/123456/gvfs/smb-share:server=rdsfcifs.acrc.bris.ac.uk,share=zebrafish_osteoarthritis/`.
Have a look in `/run/user/` to find the exact path. You can then create a convenient symlink to this directory using `ln`.
</details>

<details>
<summary>
If you can't access the RDSF
</summary>

If you can't access the RDSF (e.g. you are an external collaborator, reviewer, etc.) then you can still run the code here, but some bits might be more difficult.

### Inference
Running inference on a complete zebrafish scan doesn't require the RDSF.
Pre-trained models are provided with this repo, so you can run inference as normal
with the [inference script](./scripts/3-run_inference.py).

### Model training
Training the models is a little more complicated, since some things are hard-coded relative
to the root of the RDSF.

If you don't have RDSF access but **do** have access to a folder of training data (e.g.
one that was deposited as the data for a publication), then you can use this:
1. unzip this directory of training data somewhere
2. change `rdsf_dir` in `userconf.yml` to point to where you unzipped this directory.

This should work, but I haven't tested it.

If you don't have the training data and you want to train a model, you'll have to get access to the training data first.

</details>

### Hardware
You will likely want to the a GPU to train the models.
As well as the usual BriCS/ACRC computing facilities, the group has a remote machine with an A6000 GPU on it.
Ask the right person to get access to this.

## Training models
See [the documentation](./docs/README.md) for instructions on how to train your first model.

## Contributing
If you're coming on to this project, I've created an Issue with suggested first steps to follow and potential future work.
