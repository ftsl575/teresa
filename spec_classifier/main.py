#!/usr/bin/env python3
"""
Spec Classifier — multivendor CLI entry point (Dell, Cisco CCW).
Pipeline: Excel → parse → normalize → classify → artifacts + cleaned spec.
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

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
from src.vendors.dell.adapter import DellAdapter
from src.vendors.cisco.adapter import CiscoAdapter
from src.vendors.hpe.adapter import HPEAdapter

VENDOR_REGISTRY: dict[str, type] = {
    "dell": DellAdapter,
    "cisco": CiscoAdapter,
    "hpe": HPEAdapter,
}


def _get_adapter(vendor: str, config: dict):
    cls = VENDOR_REGISTRY.get(vendor)
    if cls is None:
        raise ValueError(f"Unknown vendor: {vendor!r}. Available: {list(VENDOR_REGISTRY)}")
    return cls(config)


def _resolve_path(path: str, base: Path) -> Path:
    p = Path(path)
    return p if p.is_absolute() else (base / p).resolve()


# Default I/O roots when not in config (repo stays code-only; cwd-relative).
DEFAULT_INPUT_ROOT = Path.cwd() / "input"
DEFAULT_OUTPUT_ROOT = Path.cwd() / "output"


def _load_config(config_path: Path) -> dict:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # Layer 2: config.local.yaml overrides (not committed to git)
    local_path = config_path.parent / "config.local.yaml"
    if local_path.exists():
        with open(local_path, encoding="utf-8") as f:
            local_data = yaml.safe_load(f) or {}
        for key, value in local_data.items():
            if isinstance(value, dict) and isinstance(data.get(key), dict):
                data[key].update(value)
            else:
                data[key] = value

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
    vendor: str = "dell",
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
        adapter = _get_adapter(vendor, config)
        # Create run_folder and run.log before first pipeline log so all stages are captured (OUT-002)
        vendor_base = output_dir / f"{vendor}_run"
        run_folder = create_run_folder(str(vendor_base), input_path.name, stamp=session_stamp)
        run_log_path = run_folder / "run.log"
        fh = logging.FileHandler(run_log_path, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        root_logger = logging.getLogger()
        root_logger.addHandler(fh)
        try:
            log.info("Parsing Excel: %s", input_path)
            raw_rows, header_row_index = adapter.parse(str(input_path))
            log.info("Normalizing rows (row_kind)...")
            normalized_rows = adapter.normalize(raw_rows)

            rules_file = adapter.get_rules_file()
            rules_path = _resolve_path(rules_file, cwd)
            if not rules_path.exists():
                print(f"Error: Rules file not found: {rules_path}", file=sys.stderr)
                return 1
            log.info("Loading rules: %s", rules_path)
            ruleset = RuleSet.load(str(rules_path))

            log.info("Classifying rows...")
            classification_results = [classify_row(r, ruleset) for r in normalized_rows]

            log.info("Saving artifacts to %s", run_folder)
            save_rows_raw(raw_rows, run_folder)
            save_rows_normalized(normalized_rows, run_folder)
            save_classification(classification_results, normalized_rows, run_folder)
            save_unknown_rows(normalized_rows, classification_results, run_folder)
            save_header_rows(normalized_rows, run_folder)

            stats = collect_stats(classification_results)
            stats["rules_file_hash"] = compute_file_hash(str(rules_path))
            stats["input_file"] = input_path.name
            stats["run_timestamp"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

            stats["vendor_stats"] = adapter.get_vendor_stats(normalized_rows)

            save_run_summary(stats, run_folder)

            generate_cleaned_spec(normalized_rows, classification_results, config, run_folder)
            generate_annotated_source_excel(
                raw_rows, normalized_rows, classification_results, input_path, run_folder,
                header_row_index=header_row_index,
            )
            if adapter.generates_branded_spec():
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
        finally:
            root_logger.removeHandler(fh)
            fh.close()

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
        description="Spec Classifier — classify Excel/CCW spec (Dell, Cisco), write artifacts and cleaned spec.",
    )
    parser.add_argument("--input", default=None, help="Path to input Excel file (.xlsx) — required in single-file mode")
    parser.add_argument(
        "--batch-dir",
        default=None,
        help="Process all .xlsx files in this directory (batch mode). "
        "Creates per-run folders + a TOTAL aggregation folder.",
    )
    parser.add_argument("--vendor", choices=list(VENDOR_REGISTRY), default="dell", help="Vendor adapter (default: dell)")
    parser.add_argument("--config", default="config.yaml", help="Path to config YAML (default: config.yaml)")
    parser.add_argument(
        "--output-dir",
        default=str(Path.cwd() / "output"),
        help="Output directory for run folders (default: cwd/output, or config paths.output_root if set)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Batch mode: process all .xlsx in input_root (from config or default). Overrides need for --batch-dir.",
    )
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

    try:
        config = _load_config(config_path)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in config: {e}", file=sys.stderr)
        return 1

    paths_cfg = config.get("paths") or {}
    output_dir_raw = (
        args.output_dir
        or paths_cfg.get("output_root")
        or str(DEFAULT_OUTPUT_ROOT)
    )
    output_dir = Path(output_dir_raw) if Path(output_dir_raw).is_absolute() else _resolve_path(output_dir_raw, cwd)

    # Batch mode: --batch-dir <path> or --batch (use input_root from config or default)
    if args.batch_dir:
        batch_dir = Path(args.batch_dir) if Path(args.batch_dir).is_absolute() else _resolve_path(args.batch_dir, cwd)
    elif args.batch:
        batch_dir_raw = paths_cfg.get("input_root") or str(DEFAULT_INPUT_ROOT)
        batch_dir = Path(batch_dir_raw) if Path(batch_dir_raw).is_absolute() else _resolve_path(batch_dir_raw, cwd)
    else:
        batch_dir = None

    if batch_dir is not None:
        if not batch_dir.is_dir():
            print(f"Error: --batch-dir is not a directory: {batch_dir}", file=sys.stderr)
            return 1
        xlsx_files = sorted(batch_dir.glob("*.xlsx"))
        if not xlsx_files:
            print(f"Error: no .xlsx files found in {batch_dir}", file=sys.stderr)
            return 1

        session_stamp = get_session_stamp()
        vendor_base = output_dir / f"{args.vendor}_run"
        total_folder = create_total_folder(str(vendor_base), session_stamp)
        log.info("Batch mode: %d files, TOTAL folder: %s", len(xlsx_files), total_folder)

        adapter = _get_adapter(args.vendor, config)
        processed = []
        skipped = []
        failed = []
        for xlsx_path in xlsx_files:
            try:
                if not adapter.can_parse(str(xlsx_path)):
                    log.warning("Skipping %s: not a %s file", xlsx_path.name, args.vendor)
                    skipped.append(xlsx_path.name)
                    continue
            except Exception as e:
                log.error("Failed to read %s: %s", xlsx_path.name, e)
                failed.append(xlsx_path.name)
                continue

            log.info("--- Batch: processing %s ---", xlsx_path.name)
            code = _run_single(
                input_path=xlsx_path,
                config=config,
                config_path=config_path,
                output_dir=output_dir,
                vendor=args.vendor,
                session_stamp=session_stamp,
                total_folder=total_folder,
                save_golden=getattr(args, "save_golden", False),
                update_golden=getattr(args, "update_golden", False),
                cwd=cwd,
                log=log,
            )
            if code == 0:
                processed.append(xlsx_path.name)
            else:
                failed.append(xlsx_path.name)

        log.info(
            "Batch complete: %d processed, %d skipped, %d failed",
            len(processed), len(skipped), len(failed),
        )
        print(f"Batch complete: {len(processed)} processed, {len(skipped)} skipped, {len(failed)} failed. TOTAL: {total_folder}")
        return 1 if len(failed) > 0 else 0

    if not args.input:
        print("Error: either --input, --batch-dir, or --batch is required", file=sys.stderr)
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
        vendor=args.vendor,
        session_stamp=None,
        total_folder=None,
        save_golden=getattr(args, "save_golden", False),
        update_golden=getattr(args, "update_golden", False),
        cwd=cwd,
        log=log,
    )


if __name__ == "__main__":
    sys.exit(main())
