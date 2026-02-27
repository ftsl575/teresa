"""
Run folder management: create unique output directories per pipeline run and batch session.

Naming conventions:
  Single run:  run-YYYY-MM-DD__HH-MM-SS-<stem>   (e.g. run-2026-02-26__06-09-53-dl1)
  Batch TOTAL: run-YYYY-MM-DD__HH-MM-SS-TOTAL
"""

import shutil
from datetime import datetime
from pathlib import Path


def get_session_stamp() -> str:
    """Return current timestamp in run folder format: YYYY-MM-DD__HH-MM-SS."""
    return datetime.now().strftime("%Y-%m-%d__%H-%M-%S")


def create_run_folder(base_dir: str, input_filename: str, stamp: str = None) -> Path:
    """
    Create a unique run folder: <base_dir>/run-<stamp>-<stem>/
    If folder already exists (same second), append _1, _2, ... for uniqueness.

    Args:
        base_dir: base output directory
        input_filename: input file name (e.g. "dl1.xlsx"); stem is extracted
        stamp: timestamp string from get_session_stamp(); if None, generates new one
    """
    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)
    if stamp is None:
        stamp = get_session_stamp()
    stem = Path(input_filename).stem
    name = f"run-{stamp}-{stem}"
    folder = base_path / name
    suffix = 0
    while folder.exists():
        suffix += 1
        folder = base_path / f"{name}_{suffix}"
    folder.mkdir(parents=True)
    return folder


def create_total_folder(base_dir: str, stamp: str) -> Path:
    """
    Create (or return existing) TOTAL aggregation folder: <base_dir>/run-<stamp>-TOTAL/
    Idempotent: does not fail if already exists.
    """
    base_path = Path(base_dir)
    folder = base_path / f"run-{stamp}-TOTAL"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def copy_to_total(run_folder: Path, total_folder: Path, stem: str) -> None:
    """
    Copy the three presentation files from run_folder to total_folder with stem prefix.

    Copies:
      cleaned_spec.xlsx         → <stem>_cleaned_spec.xlsx
      <stem>_annotated.xlsx     → <stem>_annotated.xlsx   (already prefixed)
      <stem>_branded.xlsx       → <stem>_branded.xlsx     (already prefixed)
    """
    copies = [
        (run_folder / "cleaned_spec.xlsx",         total_folder / f"{stem}_cleaned_spec.xlsx"),
        (run_folder / f"{stem}_annotated.xlsx",    total_folder / f"{stem}_annotated.xlsx"),
        (run_folder / f"{stem}_branded.xlsx",      total_folder / f"{stem}_branded.xlsx"),
    ]
    for src, dst in copies:
        if src.exists():
            shutil.copy2(src, dst)
