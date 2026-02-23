Transfer Learning
====
Try to fine-tune the model on a new dataset.

Intent
----
We wanted to show that you'd need less training data to fine-tune a model than you would to
train a brand new one on different data. We didn't have a lot of other bones segmented out
at the time though, so this example shows fine-tuning the model on Wahab's quadrates (these are
jawbones that Felix didn't label in his training set, but Wahab did).

You might want to use a different bone if another one is available.

Usage
----
There are two subparsers here; one for training a new model and one for fine-tuning.
Get help output on the two by running:

```
uv run scripts/experiments/quadrate_transfer_learning.py train -h
```
or
```
uv run scripts/experiments/quadrate_transfer_learning.py fine_tune -h
```

I think this should run the right thing to fine-tune a model...
```
uv run scripts/experiments/quadrate_transfer_learning.py fine_tune --train-all example_segmenter.pkl
```
This should run and output some results to `script_output/transfer_learning/quadrate/fine_tune/`.

You might want to turn the learning rate down when fine-tuning the model, otherwise it will just "forget"
all the previous information that it has learned.
