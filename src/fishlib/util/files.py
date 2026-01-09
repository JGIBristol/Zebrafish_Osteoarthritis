"""
File path operations etc.
"""

import pathlib
from functools import cache

import pandas as pd


@cache
def _mastersheet() -> pd.DataFrame:
    """
    Read the location of the jaw centres from file

    """
    csv_path = pathlib.Path(__file__).parents[2] / "data" / "uCT_mastersheet.csv"
    return pd.read_csv(csv_path)


@cache
def oldn2newn() -> dict[int, int]:
    """
    Get the mapping from old fish numbers to new fish numbers

    """
    df = _mastersheet()
    return pd.Series(df["n"].values, index=df["old_n"]).to_dict()
