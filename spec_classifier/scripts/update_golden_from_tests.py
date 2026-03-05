"""
Regenerate golden/*_expected.jsonl using same pipeline as regression tests.
Run from spec_classifier: python scripts/update_golden_from_tests.py
Uses config.local.yaml for input_root (dell/cisco/hpe subdirs or direct).
"""
import json
import sys
from pathlib import Path

# Run from spec_classifier
repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from conftest import project_root, get_input_root_dell, get_input_root_cisco, get_input_root_hpe, load_config
from tests.helpers import run_pipeline_in_memory, build_golden_rows
from src.diagnostics.stats_collector import collect_stats

GOLDEN_DIR = project_root() / "golden"


def save_golden(rows: list, stem: str) -> None:
    path = GOLDEN_DIR / f"{stem}_expected.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for obj in rows:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    print(f"Written {path}")


def main():
    root = project_root()
    config = load_config()

    # Dell
    dell_root = get_input_root_dell()
    for name in ["dl1.xlsx", "dl2.xlsx", "dl3.xlsx", "dl4.xlsx", "dl5.xlsx"]:
        p = dell_root / name
        if not p.exists():
            print(f"Skip (not found): {p}")
            continue
        norm, res = run_pipeline_in_memory("dell", p, root / "rules" / "dell_rules.yaml")
        save_golden(build_golden_rows(norm, res), p.stem)

    # Cisco
    cisco_root = get_input_root_cisco()
    for name in ["ccw_1.xlsx", "ccw_2.xlsx"]:
        p = cisco_root / name
        if not p.exists():
            print(f"Skip (not found): {p}")
            continue
        norm, res = run_pipeline_in_memory("cisco", p, root / "rules" / "cisco_rules.yaml")
        save_golden(build_golden_rows(norm, res), p.stem)

    # HPE
    hpe_root = get_input_root_hpe()
    for name in [f"hp{i}.xlsx" for i in range(1, 9)]:
        p = hpe_root / name
        if not p.exists():
            print(f"Skip (not found): {p}")
            continue
        norm, res = run_pipeline_in_memory("hpe", p, root / "rules" / "hpe_rules.yaml", config)
        save_golden(build_golden_rows(norm, res), p.stem)

    # Print dl1 hw_type_counts for test_stats_hw_type.py
    dl1 = dell_root / "dl1.xlsx"
    if dl1.exists():
        _, res = run_pipeline_in_memory("dell", dl1, root / "rules" / "dell_rules.yaml")
        stats = collect_stats(res)
        print("\n# EXPECTED_DL1_HW_TYPE_COUNTS (paste into test_stats_hw_type.py):")
        print(repr(stats["hw_type_counts"]))


if __name__ == "__main__":
    main()
