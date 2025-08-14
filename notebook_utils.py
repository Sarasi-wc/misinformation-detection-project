"""
notebook_utils.py
Small helpers for Jupyter notebooks:
- enable_autosave_plots(): patches matplotlib.pyplot.show() so figures are also saved
- save_dataframe_preview(): saves the first N rows of a DataFrame as CSV

Defaults:
- Visuals -> results/visualizations
- Tables  -> results/artifacts
Can be overridden via function args or env vars NBX_VIS_DIR / NBX_ARTIFACTS_DIR.
"""

from __future__ import annotations
import os, time
from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt

__all__ = ["enable_autosave_plots", "save_dataframe_preview"]

# Defaults (can be overridden by env or function args)
DEFAULT_VIS_DIR = Path(os.environ.get("NBX_VIS_DIR", "results/visualizations"))
DEFAULT_ARTIFACTS_DIR = Path(os.environ.get("NBX_ARTIFACTS_DIR", "results/artifacts"))

def _ensure_dir(p: Path | str) -> Path:
    p = Path(p)
    p.mkdir(parents=True, exist_ok=True)
    return p

def enable_autosave_plots(prefix: str = "fig",
                          output_dir: Optional[str | Path] = None) -> None:
    """
    Monkey-patch matplotlib.pyplot.show so every plotted figure is ALSO saved
    to output_dir (default results/visualizations) as a high-res PNG.

    Usage:
        import notebook_utils as nbx
        nbx.enable_autosave_plots(prefix="01_data_collection", output_dir=VIS_DIR)
        # ... do plots ...
        plt.show(name_hint="label_dist")

    Filenames:
        <index>_<prefix>_<name_hint>_<timestamp>.png
    """
    vis_dir = _ensure_dir(output_dir or DEFAULT_VIS_DIR)
    orig_show = plt.show

    def show_and_save(*args, **kwargs):
        fig = plt.gcf()
        ts = time.strftime("%Y%m%d-%H%M%S")
        try:
            idx = len(list(vis_dir.glob("*.png")))
        except Exception:
            idx = 0
        name_hint: str = kwargs.pop("name_hint", "plot")
        path = vis_dir / f"{idx:02d}_{prefix}_{name_hint}_{ts}.png"
        try:
            fig.savefig(path, dpi=200, bbox_inches="tight")
            print(f"[saved plot] {path}")
        except Exception as e:
            print(f"[warn] could not save plot: {e}")
        return orig_show(*args, **kwargs)

    plt.show = show_and_save  # type: ignore[assignment]
    print(f"[autosave] matplotlib.pyplot.show patched -> {vis_dir}")

def save_dataframe_preview(df,
                           name: str,
                           n: int = 20,
                           output_dir: Optional[str | Path] = None) -> str:
    """
    Saves df.head(n) to output_dir/<name>_preview.csv
    output_dir defaults to results/artifacts.
    """
    art_dir = _ensure_dir(output_dir or DEFAULT_ARTIFACTS_DIR)
    out_csv = art_dir / f"{name}_preview.csv"
    try:
        df.head(n).to_csv(out_csv, index=False)
        print(f"[saved table] {out_csv}")
    except Exception as e:
        print(f"[warn] could not save table preview: {e}")
    return str(out_csv)
