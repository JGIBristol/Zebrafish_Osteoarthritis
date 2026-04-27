"""
One of the reviewers has suggested that we should better describe the effect of changing alpha on the combined Dice-Hausdorff score.

We can do this by taking one of our samples, finding the Dice and Hausdorff scores and showing a table of how the combined score depends on alpha.

This script looks at the scores in `logs/` (if these don't exist yet, create them by running `./train_lots_of_models.sh`), finds the five runs with the extreme/quartile/median
values of the combined score,
"""

import pathlib
import argparse

import pandas as pd

from repeat_training_summary import extract_table_from_file


def main():
    """
    Choose the runs to display based on their combined Dice-Hausdorff score in the table,
    then re-calculate the combined scores for these using alpha values of 0.05, 0.1, 0.25, 0.5, 0.75, 0.90 and 0.95
    Then print a table of these values, with the alpha values as columns and the run number as rows
    """
    log_dir = pathlib.Path("logs/")
    alphas = [0.05, 0.1, 0.25, 0.5, 0.75, 0.90, 0.95]

    rows = []
    for file in sorted(log_dir.glob("*_inference.log")):
        df = extract_table_from_file(file)
        row = df.loc["inference"].copy()
        row.name = file.stem
        rows.append(row)

    all_runs = pd.DataFrame(rows)

    # Select 5 representative runs by the stored Hausdorff_Dice_0.5 (alpha=0.25)
    quantiles = all_runs["Hausdorff_Dice_0.5"].quantile([0.0, 0.25, 0.5, 0.75, 1.0])
    selected_idx = [
        (all_runs["Hausdorff_Dice_0.5"] - q).abs().idxmin() for q in quantiles
    ]
    selected = all_runs.loc[selected_idx]

    sweep = pd.DataFrame(index=selected.index)
    for alpha in alphas:
        sweep[alpha] = alpha * selected["Dice"] + (1 - alpha) * selected["1-Hausdorff_0.5"]

    print(sweep.to_markdown(floatfmt=".4f"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    main()
