Train jaw locator model
====
Train a model to locate the jaw in a CT scan.

## Usage
#### 1. Change the right configuration options
The configuration options for the jaw locator model are in `userconf.yml`, near the bottom of the file
in the `jaw_loc_config` mapping.
You likely won't need to change any of these settings.

#### 2. Run the script
Run the script with:

```
uv run scripts/1-train_jaw_locator.py --model-name <MY_JAW_LOCATING_MODEL>
```
You can, of course, choose your own model name (or omit it entirely to use the default name).

This script takes quite a long time to run (depending on the training data and number of epochs);
possibly around **2 hours** using the default settings.
You might want to use `screen` or `tmux` to make sure your process doesn't die if you lose internet
connection or if you laptop goes to sleep.
I've forgotten why it takes so long to run.

The first time you run the script it will take around **10 additional minutes** to create some new DICOM files and save them to disk.
See the section below if you're wondering why we have to do this.

#### 3. Check the model has been saved
The model should have been saved to `script_output/jaw_location/<model_name>/<model_name>.pth`.

The name can be chosen with the above command line argument; it defaults to `locator`.

## More information
<details>
<summary> What do the outputs mean? </summary>
The script will output a load of stuff to the `script_output/jaw_location/&lt;YOUR MODEL NAME&gt;` directory.

The most important output is the model, located at `<YOUR MODEL NAME>.pth`.

We also have outputs to check the training setup, progress during training, final performance on the training and validation data and some holdout test data.

We train on all but two of the images, and validate on one of these holdout images.

#### Training setup
 - `train_heatmap_example.png`, `val_heatmap_example.png`: examples of what the heatmap looks like at the start of training.

#### Progress during training
 - `heatmap_epoch_N_sigma_M.png`: images showing what the target heatmap (this is what the model is trying to learn) looks like at each epoch.
 Useful because the heatmap can shrink during training, so we might want to track this.
 - `losses.png`: training and validation loss.
 - `metrics.png`: some accuracy metrics with epoch; KL divergence, Dice score and Mean Square Error
 - `train_heatmap_example.png`

 #### Final performance on train/val data
 - `train_heatmap_pred`, `val_heatmap_pred.png`: the final performance of the model on a training/validation image.
  Check these against `train_heatmap_example.png` and `val_heatmap_example.png`.

 #### Final performance on test data
 - `test_centroid_downsampled.png`: where the predicted centroid is on the downsampled test image.
 - `test_centroid_truth.png`: where the ground truth centroid is on the full-res test image.
 - `test_centroid.png`: where the predicted centroid is on the full-res image. Check that this is similar to `test_centroid_truth.png`.
 - `test_cropped.png`: the cropped-out head, using our predicted centroid. The jaw is highlighted in red, so you can easily see if it's been missed out of the image.
 Check this against `truth_cropped.png`.
 - `test_heatmap.png`: the predicted heatmap on the test image.
 - `truth_cropped.png`: the test image, cropped around the ground truth centroid.

</details>

<details>
<summary> Why cache the DICOMs again? </summary>

`0-create_dicoms.py` creates DICOM files from the images and labels on the RDSF.
This saves us time since it means we only need to read from the network drive once.

However, these aren't the right inputs for the jaw location model - the jaw
locator operates on downsampled images, since we don't need the full resolution scans
just to find the jaw.

For the same reasons as before, we will create new downsampled DICOM files for our
jaw locator training data.
This was mostly useful when I was training multiple locator models (i.e. when I was
trying to get it to work in the first place).
</details>

<details>
<summary> How does the model work? </summary>

__This is quite a strange model.__

### Object Location
The task of finding the zebrafish head is basically object location - there is an object
in our image with some co-ordinates, and we want our model to learn these co-ordinates from
the image.

In our case, we get the co-ordinates of the object from the jaw segmentation training data;
we take the centroid of the segmentation mask, and use that as the location we want to learn.

The simplest model would take an image as input and output the predicted location as `(x, y, z)`
co-ordinates.
However, this type of model is hard to train. It is hard for the model to figure out the spatial
meaning of the error signal, and it is hard for a model to figure out the right mapping from
pixels -> co-ordinates.

Luckily, we can turn this problem into an easier one.

### Heatmap Based Object Location
Segmentation is a much easier problem for CNNs.

This is because CNNs have certain "inductive biases" which line up nicely with the segmentation
task - e.g. if an object in an image moves, a CNN can deal with that easily because of the mathematical
form of the convolution operation.

We can turn our object location problem into a segmentation problem by tasking the model to segment a
Gaussian out from the image, where the Gaussian lives at the object's centroid.

This has a number of advantages:
- the model will actually learn
- we get a natural measure of uncertainty in the object's location
- we can get sub-pixel accuracy (if the Gaussian we are learning is small)
- in future, this model could be trained to find multiple objects in one image; potentially useful if we want to
  segment out multiple things from one CT scan.

### Curriculum Learning
We're now faced with a decision - how wide should the Gaussian be?
If it's wide, the model can learn easily but we don't get a good idea of where the object is.
If it is small, the model will find it hard to learn (in the limit of a tiny Gaussian, we are basically back to
locating a point).

We can get the best of both of these by using curriculum learning - first, train the model on an easy task (find a wide Gaussian),
then progressively train it to solves harder and harder tasks.

In our case, this means first training the model to find a wide Gaussian, then once it has we will decrease the size of the Gaussian.
We can choose whether the model has learned to locate the Gaussian by e.g. choosing a threshold on the loss.

This makes the loss function look funny:
- first, the loss decreases as the model learns (like you might expect)
- then the loss will plateu as the Gaussian shrinks, the model learns to find this new Gaussian, then the process repeats
- once the Gaussian has reached a predefined minimum size, the loss will decrease again.

</details>
