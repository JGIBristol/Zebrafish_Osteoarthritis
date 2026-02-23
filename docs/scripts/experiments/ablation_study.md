Ablation Study
====
As an experiment, we might want to investigate the effect of the different layers of the model.

We have a feeling that some of the layers will be responsible for thresholding and others for
morphology, although it's possible that these functions are mixed up and shared between the different
layers (which makes sense as they operate on different spatial scales).

To investigate this, we have a script that turns off the attention mechanism in each layer and makes
some plots. The input data for these is a bit strange (its handled by the `inference.read` library,
which is a bit strange because I wrote it before we had the jaw location model).

I think this should work:
```
uv run scripts/experiments/ablation_study.py 273 example_segmenter.pkl
```
The 273 means use "inference subject 273" - I think what this does is:
 - read jaw number 273 from the RDSF (`rdsf_dir` needs to be correctly specified in `userconf.yml`)
 - crop it out (hard-coded jaw location)
 - feed this into the model, do the ablation study
