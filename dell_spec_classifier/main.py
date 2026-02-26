#!/usr/bin/env python3
"""
Dell Specification Classifier — CLI entry point.
Pipeline: Excel → parse → normalize → classify → artifacts + cleaned spec.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import yaml

from src.core.parser import parse_excel
from src.core.normalizer import normalize_row
from src.rules.rules_engine import RuleSet
from src.core.classifier import classify_row
from src.diagnostics.run_manager import (
    create_run_folder,
    get_session_stamp,
    create_total_folder,
    copy_to_total,
)
from src.outputs.json_writer import (
    save_rows_raw,
    save_rows_normalized,
    save_classification,
    save_unknown_rows,
    save_header_rows,
)
from src.diagnostics.stats_collector import collect_stats, save_run_summary, compute_file_hash
from src.outputs.excel_writer import generate_cleaned_spec
from src.outputs.annotated_writer import generate_annotated_source_excel
from src.outputs.branded_spec_writer import generate_branded_spec


def _resolve_path(path: str, base: Path) -> Path:
    p = Path(path)
    return p if p.is_absolute() else (base / p).resolve()


def _load_config(config_path: Path) -> dict:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data is None:
        data = {}
    return data


def _build_golden_rows(normalized_rows, classification_results):
    """Build list of dicts for golden JSONL: source_row_index, row_kind, entity_type, state, matched_rule_id, device_type, hw_type, skus."""
    out = []
    for row, result in zip(normalized_rows, classification_results):
        out.append({
            "source_row_index": row.source_row_index,
            "row_kind": result.row_kind.value,
            "entity_type": result.entity_type.value if result.entity_type else None,
            "state": result.state.value if result.state else None,
            "matched_rule_id": result.matched_rule_id,
            "device_type": getattr(result, "device_type", None),
            "hw_type": getattr(result, "hw_type", None),
            "skus": list(row.skus),
        })
    return out


def _save_golden(golden_rows, golden_path: Path) -> None:
    golden_path.parent.mkdir(parents=True, exist_ok=True)
    with open(golden_path, "w", encoding="utf-8") as f:
        for obj in golden_rows:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _run_single(
    input_path: Path,
    config: dict,
    config_path: Path,
    output_dir: Path,
    session_stamp: str = None,
    total_folder: Path = None,
    save_golden: bool = False,
    update_golden: bool = False,
    cwd: Path = None,
    log=None,
) -> int:
    """Run the full pipeline for one input file. Returns 0 on success, 1 on failure."""
    if cwd is None:
        cwd = Path.cwd()
    if log is None:
        log = logging.getLogger(__name__)
    try:
        log.info("Parsing Excel: %s", input_path)
        raw_rows = parse_excel(str(input_path))
        log.info("Normalizing rows (row_kind)...")
        normalized_rows = [normalize_row(r) for r in raw_rows]

        rules_file = config.get("rules_file", "rules/dell_rules.yaml")
        rules_path = _resolve_path(rules_file, cwd)
        if not rules_path.exists():
            print(f"Error: Rules file not found: {rules_path}", file=sys.stderr)
            return 1
        log.info("Loading rules: %s", rules_path)
        ruleset = RuleSet.load(str(rules_path))

        log.info("Classifying rows...")
        classification_results = [classify_row(r, ruleset) for r in normalized_rows]

        run_folder = create_run_folder(str(output_dir), input_path.name, stamp=session_stamp)
        run_log_path = run_folder / "run.log"
        fh = logging.FileHandler(run_log_path, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        logging.getLogger().addHandler(fh)

        log.info("Saving artifacts to %s", run_folder)
        save_rows_raw(raw_rows, run_folder)
        save_rows_normalized(normalized_rows, run_folder)
        save_classification(classification_results, normalized_rows, run_folder)
        save_unknown_rows(normalized_rows, classification_results, run_folder)
        save_header_rows(normalized_rows, run_folder)

        stats = collect_stats(classification_results)
        stats["rules_file_hash"] = compute_file_hash(str(rules_path))
        stats["input_file"] = input_path.name
        stats["run_timestamp"] = datetime.utcnow().replace(microsecond=0).isoformat()
        save_run_summary(stats, run_folder)

        generate_cleaned_spec(normalized_rows, classification_results, config, run_folder)
        generate_annotated_source_excel(
            raw_rows, normalized_rows, classification_results, input_path, run_folder
        )
        branded_path = run_folder / f"{input_path.stem}_branded.xlsx"
        generate_branded_spec(
            normalized_rows=normalized_rows,
            classification_results=classification_results,
            source_filename=input_path.name,
            output_path=branded_path,
        )

        # Copy to TOTAL if batch mode
        if total_folder is not None:
            copy_to_total(run_folder, total_folder, input_path.stem)
            log.info("Copied to TOTAL: %s", total_folder)

        log.info("Done.")

        save_golden_mode = save_golden or update_golden
        if save_golden_mode:
            golden_dir = _resolve_path("golden", cwd)
            stem = input_path.stem
            golden_path = golden_dir / f"{stem}_expected.jsonl"
            if update_golden:
                try:
                    answer = input("Overwrite golden? [y/N]: ").strip().lower()
                except EOFError:
                    answer = "n"
                if answer != "y":
                    log.info("Golden not updated (skipped or non-interactive).")
                else:
                    golden_rows = _build_golden_rows(normalized_rows, classification_results)
                    _save_golden(golden_rows, golden_path)
                    log.info("Golden updated: %s", golden_path)
            else:
                golden_rows = _build_golden_rows(normalized_rows, classification_results)
                _save_golden(golden_rows, golden_path)
                log.info("Golden saved: %s", golden_path)

        print("Summary:")
        print(f"  total_rows: {stats['total_rows']}")
        print(f"  header_rows_count: {stats['header_rows_count']}")
        print(f"  item_rows_count: {stats['item_rows_count']}")
        print(f"  entity_type_counts: {stats['entity_type_counts']}")
        print(f"  unknown_count: {stats['unknown_count']}")
        print(f"  run_folder: {run_folder}")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML: {e}", file=sys.stderr)
        return 1
    except Exception:
        log.exception("Pipeline failed")
        return 1

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dell Specification Classifier — classify Excel spec, write artifacts and cleaned spec.",
    )
    parser.add_argument("--input", default=None, help="Path to input Excel file (.xlsx) — required in single-file mode")
    parser.add_argument(
        "--batch-dir",
        default=None,
        help="Process all .xlsx files in this directory (batch mode). "
        "Creates per-run folders + a TOTAL aggregation folder.",
    )
    parser.add_argument("--config", default="config.yaml", help="Path to config YAML (default: config.yaml)")
    parser.add_argument("--output-dir", default="output", help="Output directory for run folders (default: output)")
    parser.add_argument("--save-golden", action="store_true", help="Run pipeline and save golden/<stem>_expected.jsonl")
    parser.add_argument("--update-golden", action="store_true", help="Run pipeline and overwrite golden after confirmation (y/n)")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    log = logging.getLogger(__name__)

    cwd = Path.cwd()
    config_path = _resolve_path(args.config, cwd)
    output_dir = _resolve_path(args.output_dir, cwd)

    try:
        config = _load_config(config_path)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in config: {e}", file=sys.stderr)
        return 1

    # Batch mode: process all xlsx in --batch-dir
    if args.batch_dir:
        batch_dir = _resolve_path(args.batch_dir, cwd)
        if not batch_dir.is_dir():
            print(f"Error: --batch-dir is not a directory: {batch_dir}", file=sys.stderr)
            return 1
        xlsx_files = sorted(batch_dir.glob("*.xlsx"))
        if not xlsx_files:
            print(f"Error: no .xlsx files found in {batch_dir}", file=sys.stderr)
            return 1

        session_stamp = get_session_stamp()
        total_folder = create_total_folder(str(output_dir), session_stamp)
        log.info("Batch mode: %d files, TOTAL folder: %s", len(xlsx_files), total_folder)

        exit_codes = []
        for xlsx_path in xlsx_files:
            log.info("--- Batch: processing %s ---", xlsx_path.name)
            code = _run_single(
                input_path=xlsx_path,
                config=config,
                config_path=config_path,
                output_dir=output_dir,
                session_stamp=session_stamp,
                total_folder=total_folder,
                save_golden=getattr(args, "save_golden", False),
                update_golden=getattr(args, "update_golden", False),
                cwd=cwd,
                log=log,
            )
            exit_codes.append(code)

        failed = sum(1 for c in exit_codes if c != 0)
        print(f"Batch complete: {len(xlsx_files)} files, {failed} failed. TOTAL: {total_folder}")
        return 1 if failed else 0

    if not args.input:
        print("Error: either --input or --batch-dir is required", file=sys.stderr)
        return 1

    input_path = _resolve_path(args.input, cwd)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1

    return _run_single(
        input_path=input_path,
        config=config,
        config_path=config_path,
        output_dir=output_dir,
        session_stamp=None,
        total_folder=None,
        save_golden=getattr(args, "save_golden", False),
        update_golden=getattr(args, "update_golden", False),
        cwd=cwd,
        log=log,
    )


if __name__ == "__main__":
    sys.exit(main())
