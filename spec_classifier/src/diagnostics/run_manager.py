"""
Run folder management: create and prepare per-spec output directories.

Naming convention:
  Spec folder: <output_root>/<bucket>/<vendor>/<spec>/  (e.g. SPLIT/dell/dl1/)
"""

import shutil
from pathlib import Path


def create_spec_folder(output_root: Path, bucket: str, vendor: str, spec: str) -> Path:
    """
    Create (or wipe-and-recreate) <output_root>/<bucket>/<vendor>/<spec>/.

    Wipe-first: if the directory already exists it is deleted before recreation,
    ensuring no stale artifacts from a previous run survive.

    Args:
        output_root: top-level output directory (e.g. C:\\...\\OUTPUT)
        bucket:      bucket name ("READY" or "SPLIT")
        vendor:      registry key, lowercase (e.g. "dell", "hpe")
        spec:        input file stem (e.g. "dl1")

    Returns:
        Path to the freshly created directory.
    """
    output_root = Path(output_root)
    folder = output_root / bucket / vendor / spec
    # CR-01 guard: never rmtree outside output_root. Guards against a pathological
    # spec/vendor/bucket token (e.g. a ".." stem) resolving the target above the
    # intended spec directory before the wipe.
    if not folder.resolve().is_relative_to(output_root.resolve()):
        raise ValueError(
            f"Refusing to create/wipe {folder!r}: resolves outside output_root {output_root!r}"
        )
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)
    return folder
