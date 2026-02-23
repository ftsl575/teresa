"""
Run folder management: create a unique output directory per pipeline run.
"""

from datetime import datetime
from pathlib import Path


def create_run_folder(base_dir: str, input_filename: str) -> Path:
    """
    Create a unique run folder under base_dir: run_YYYYMMDD_HHMMSS/
    If the folder already exists (e.g. same second), append _1, _2, ... for uniqueness.
    """
    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"run_{stamp}"
    folder = base_path / name
    suffix = 0
    while folder.exists():
        suffix += 1
        folder = base_path / f"{name}_{suffix}"
    folder.mkdir(parents=True)
    return folder
