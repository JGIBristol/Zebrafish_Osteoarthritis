Train lots of models
====
We might want to train the same jaw segmentation model lots of times, to see the effect it has
on the segmentation. This is because we investigated inter- and intra-human segmentation reliability,
so it makes sense to do it for the automated model too.

To train 20 segmentation models and run inference with them, run
```
./scripts/paper_scripts/train_lots_of_models.sh
```
This will make some log files containing a markdown-formatted table of dice score etc.
It'll probably take a while so you might want to run it overnight.

Then, to make the plots summarising this training, run
```
uv run scripts/paper_scripts/repeat_training_summary.py
```
This will make a histogram from the tables above.
