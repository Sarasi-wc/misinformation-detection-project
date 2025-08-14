
"""
notebook_utils.py
Small helpers for Jupyter notebooks:
- enable_autosave_plots(): patches matplotlib.pyplot.show() so figures are also saved to ./visualizations
- save_dataframe_preview(): saves the first N rows of a DataFrame to ./artifacts/<name>_preview.csv
"""

from __future__ import annotations

import os
import time
from typing import Optional

import matplotlib.pyplot as plt


__all__ = [
    "enable_autosave_plots",
    "save_dataframe_preview",
]


def _ensure_dir(d: str) -> None:
    """Create directory if it doesn't exist."""
    os.makedirs(d, exist_ok=True)


def enable_autosave_plots(prefix: str = "fig") -> None:
    """
    Monkey-patch matplotlib.pyplot.show so every plotted figure is also saved
    to ./visualizations as a high-res PNG.

    Usage:
        import notebook_utils as nbx
        nbx.enable_autosave_plots(prefix="01_data_collection")
        # ... your plotting code ...
        plt.show()   # will ALSO save a PNG automatically

    Notes:
    - Files are saved as: visualizations/<index>_<prefix>_<name_hint>_<timestamp>.png
    - You can pass a custom name hint when calling plt.show(name_hint="label_dist")
      and it will be used in the filename.
    """
    _ensure_dir("visualizations")
    orig_show = plt.show

    def show_and_save(*args, **kwargs):
        fig = plt.gcf()
        ts = time.strftime("%Y%m%d-%H%M%S")

        # count existing pngs to generate a simple sequence number
        try:
            idx = len([f for f in os.listdir("visualizations") if f.lower().endswith(".png")])
        except FileNotFoundError:
            idx = 0

        # optional name hint to make filenames easier to recognize
        name_hint: str = kwargs.pop("name_hint", "plot")
        path = f"visualizations/{idx:02d}_{prefix}_{name_hint}_{ts}.png"

        try:
            fig.savefig(path, dpi=200, bbox_inches="tight")
            print(f"[saved plot] {path}")
        except Exception as e:
            print(f"[warn] could not save plot: {e}")

        # call the original show (keeps normal behavior/inline display)
        return orig_show(*args, **kwargs)

    plt.show = show_and_save  # type: ignore[assignment]
    print("[autosave] matplotlib.pyplot.show patched to save images to ./visualizations")


def save_dataframe_preview(df, name: str, n: int = 20) -> str:
    """
    Saves the first n rows of a pandas DataFrame to ./artifacts/<name>_preview.csv

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to preview.
    name : str
        Base name for the output file (without extension or directories).
    n : int, default 20
        Number of rows to save.

    Returns
    -------
    str
        The path to the saved CSV file.

    Example
    -------
        nbx.save_dataframe_preview(df, "dataset_head", n=20)
        # -> artifacts/dataset_head_preview.csv
    """
    _ensure_dir("artifacts")
    out_csv = f"artifacts/{name}_preview.csv"
    try:
        df.head(n).to_csv(out_csv, index=False)
        print(f"[saved table] {out_csv}")
    except Exception as e:
        print(f"[warn] could not save table preview: {e}")
    return out_csv
