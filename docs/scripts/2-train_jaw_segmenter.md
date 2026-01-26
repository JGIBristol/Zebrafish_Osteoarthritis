Train jaw segmentation model
====
Train a model to segment the jaw out from a CT scan.

## Usage
#### 1. Change the right configuration options
The configuration for this model is all in `userconf.yml`.
You probably won't need to change much of it,
The model name is stored in this config file (unlike `1-train_jaw_locator.py`), so you may want to change this in `userconf.yml`.

#### 2. Run the script
Run the script with:
```
uv run scripts/2-train_jaw_segmenter.md
```
This script, again, takes a little while to run, so it might be best to run it in a `screen` or `tmux` session.

If you just want to quickly run it to check that it runs, turn
the number of epochs in `userconf.yml` down.

#### 3. Check the model has been saved
The model should have been saved to a location like
```
script_output/jaw_models/<MY MODEL NAME>/<MY MODEL NAME>.pkl
```

## More information
<details>
<summary> What do the outputs mean? </summary>
The main thing that this script outputs is the segmentation model, at `script_output/jaw_models/&lt;YOUR MODEL NAME&gt;/&lt;YOUR MODEL NAME&gt;.pkl`.

It also produces some diagnostic plots, in `script_output/jaw_models/&lt;YOUR MODEL NAME&gt;/train_output/`:
- `loss.png`: loss per epoch
- `test_pred.png`: image slices showing trained model prediction on the test data
- `test_truth.png`: the ground truth for the above.
- `train_example.png`: an example of what the training data looks like. This lets us see the augmentations applied to the data.
</details>

<details>
<summary> How does the model work? </summary>

This model is less strange than the jaw locating model, but there are still quirks.
It is based on a [U-Net with attention](https://arxiv.org/abs/1804.03999), and is trained on patches of the input CT scan.

## Patch based training
We train on patches of the data because the model has to have a fixed input and output size - using a fixed size might hurt
our ability to fine-tune this model in future if, e.g. we were
to train it on a very long, thin bone such as the spine.
It also allows us to train on much larger images than would otherwise fit in memory.

The downside is that it might be harder for the model to learn from small patches - by splitting into patches, we
are losing some context of what is around our patch.
The default setting in `userconf.yml` is large enough to contain most of the jaw and enough context for the model to learn to segment it.
If we wanted to train the model to segment out larger objects, we might have to increase the patch size.

## Dataloaders
I used the TorchIO (`tio`) library for managing the data loading.
This library handles things like loading, preprocessing, augmentation and patch-based sampling for medical data (3D images).
It also means that we deal with `Subject`s and `SubjectDataset`s, rather than with plain numpy arrays or
torch `Tensor`s.
For more information, see the 

## Augmentation
We use data augmentation to help the model generalise.
This isn't a magic technique, and isn't the same thing as giving us
more training data, but it does help the model to use the available
training data in the most efficient possible way.

Data augmentation can greatly slow down training, though -
faster libraries than the one I've used here exist, but the
one I have used is good enough. You can add augmentations, or
see the ones that are currently used, in the `userconf.yml` file.

## A note on the training data
This isn't very important, but at the moment the training/test/validation data is cropped out using some jaw centres that I found by eye
and stored in the `data/jaw_centres.csv` file.

A better implementation might use a trained jaw location model to find these - you might want to keep this in mind when fine-tuning...

</details>

<details>
<summary>Is the training deterministic?</summary>

**No.**

In the training script we set the seed for both the numpy and torch
random number generators, which means that random numbers generated
by these should be deterministic.

However, I believe there are some random numbers used in the data augmentation
that aren't set using either of these, which means that there will be small random
differences between augmentations in different training runs.
Since model training is chaotic, this might mean that there are non-negligible
differences between different models trained on the same data.

This might actually be a good thing - we can use these differences to assess
the statistical error on our segmentation (i.e. how the performance changes
when we train models on the same data multiple times).
You might want to also randomly set the torch and numpy seeds if you're doing this.

Once the model is trained, however, its performance is fully deterministic.
</details>