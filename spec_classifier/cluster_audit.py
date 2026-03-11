"""cluster_audit.py — Pattern Mining / Clustering module for Teresa spec classifier.

Reads *_audited.xlsx or *_annotated.xlsx from --output-dir, extracts candidate rows
(UNKNOWN / HW without device_type), clusters them with TF-IDF + HDBSCAN/KMeans,
and produces cluster_summary.xlsx + updates audit_report.json.

Usage:
    python cluster_audit.py --output-dir OUTPUT
    python cluster_audit.py --output-dir OUTPUT --vendor hpe --dry-run
    python cluster_audit.py --output-dir OUTPUT --min-cluster-size 5 --max-clusters 30
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import json

import pandas as pd


# ── CLI ───────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cluster_audit.py",
        description="Cluster unclassified rows from Teresa audit output to discover new rules.",
    )
    p.add_argument(
        "--output-dir",
        required=True,
        metavar="DIR",
        help="Path to folder containing *_audited.xlsx or *_annotated.xlsx files.",
    )
    p.add_argument(
        "--vendor",
        choices=["dell", "hpe", "cisco"],
        default=None,
        metavar="VENDOR",
        help="Optional vendor filter: dell | hpe | cisco.",
    )
    p.add_argument(
        "--min-cluster-size",
        type=int,
        default=3,
        metavar="N",
        help="Minimum number of rows to form a cluster (default: 3).",
    )
    p.add_argument(
        "--max-clusters",
        type=int,
        default=50,
        metavar="N",
        help="Maximum number of clusters to produce (default: 50).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show candidate row counts per vendor and exit without clustering.",
    )
    return p


# ── Step 1: Load candidate rows ───────────────────────────────────────────────

def _detect_vendor_from_path(path: Path) -> str:
    """Infer vendor from file name, parent, or grandparent directory name."""
    stem = path.stem.lower()
    parent = path.parent.name.lower()
    grandparent = path.parent.parent.name.lower()

    for text in (stem, parent, grandparent):
        if "hpe" in text or text.startswith("hp") or "hpe_run" in text:
            return "hpe"
        if "dell" in text or "dell_run" in text:
            return "dell"
        if "cisco" in text or "ccw" in text or "cisco_run" in text:
            return "cisco"
    return "unknown"


def _is_empty(val) -> bool:
    if val is None:
        return True
    if isinstance(val, float):
        import math
        return math.isnan(val)
    return str(val).strip() == ""


def _load_xlsx(path: Path) -> pd.DataFrame:
    """Read xlsx, auto-detecting header row.

    Searches rows 0-4 for a row that contains at least one known column name:
    'pipeline_check', 'entity_type', 'option_name', 'device_type'.
    Falls back to header=0 if none found.
    """
    known_cols = {"pipeline_check", "entity_type", "option_name", "device_type"}
    for header in range(45):
        try:
            df = pd.read_excel(path, engine="openpyxl", dtype=str, header=header)
        except Exception:
            break
        cols_norm = {c.strip().lower().replace(" ", "_") for c in df.columns}
        if cols_norm & known_cols:
            return df
    return pd.read_excel(path, engine="openpyxl", dtype=str, header=0)


def _collect_xlsx_files(output_dir: Path) -> list[Path]:
    """
    Recursively collect xlsx files. Per source stem, prefer *_annotated_audited.xlsx
    over *_annotated.xlsx (pure annotated, not yet audited).
    """
    audited = {
        p.stem.replace("_annotated_audited", ""): p
        for p in output_dir.rglob("*_annotated_audited.xlsx")
    }
    annotated = {
        p.stem.replace("_annotated", ""): p
        for p in output_dir.rglob("*_annotated.xlsx")
        if not p.stem.endswith("_annotated_audited")
    }

    selected: list[Path] = []
    all_stems = set(audited) | set(annotated)
    for stem in sorted(all_stems):
        selected.append(audited.get(stem) or annotated[stem])
    return selected


def load_candidate_rows(output_dir: Path, vendor_filter: str | None = None) -> list[dict]:
    """
    Read *_audited.xlsx (priority) or *_annotated.xlsx files from output_dir.

    Filtering rules:
      Case 1 — file has column 'pipeline_check' (*_audited.xlsx):
        Keep rows where pipeline_check contains "E2:" OR "E17:".
      Case 2 — no 'pipeline_check' column (*_annotated.xlsx):
        Keep rows where:
          - entity_type == "UNKNOWN"  OR
          - entity_type == "HW" AND device_type is empty AND hw_type is empty

    Each returned dict contains:
      option_name, vendor, source_file, entity_type, device_type, hw_type,
      pipeline_check (None if column absent)
    """
    files = _collect_xlsx_files(output_dir)
    if not files:
        return []

    candidates: list[dict] = []

    for path in files:
        vendor = _detect_vendor_from_path(path)
        if vendor_filter and vendor != vendor_filter:
            continue

        try:
            df = _load_xlsx(path)
        except Exception as exc:
            print(f"  [WARN] Cannot read {path.name}: {exc}", file=sys.stderr)
            continue

        cols = {c.strip().lower().replace(" ", "_"): c for c in df.columns}

        has_pipeline_check = "pipeline_check" in cols

        for _, row in df.iterrows():
            def get(col_lower: str) -> str:
                orig = cols.get(col_lower, "")
                if not orig:
                    return ""
                v = row.get(orig, "")
                return "" if _is_empty(v) else str(v).strip()

            entity_type    = get("entity_type")
            device_type    = get("device_type")
            hw_type        = get("hw_type")
            option_name    = (
                get("option_name")            # Dell: Option Name
                or get("product_description") # HPE: Product Description
                or get("description")         # Cisco: Description
                or get("product_name")        # fallback
                or ""
            )
            pipeline_check = get("pipeline_check") if has_pipeline_check else None

            if has_pipeline_check:
                # Case 1: use pipeline_check codes
                if pipeline_check and any(
                    tag in pipeline_check
                    for tag in ("E2:", "E17:", "AI_SUGGEST", "AI_MISMATCH")
                ):
                    pass  # include
                else:
                    continue
            else:
                # Case 2: derive from entity/device columns
                is_unknown = entity_type == "UNKNOWN"
                is_hw_without_type = (
                    entity_type == "HW"
                    and not device_type
                    and not hw_type
                )
                if not (is_unknown or is_hw_without_type):
                    continue

            candidates.append({
                "option_name":    option_name,
                "vendor":         vendor,
                "source_file":    path.name,
                "entity_type":    entity_type,
                "device_type":    device_type,
                "hw_type":        hw_type,
                "pipeline_check": pipeline_check,
            })

    return candidates


# ── Step 2: Normalize text ────────────────────────────────────────────────────

def normalize_text(text: str) -> str:
    import re
    t = text.lower()
    t = re.sub(r'\$[\d,.]+', '', t)
    t = re.sub(r'\b[a-z0-9]{2,}-[a-z0-9-]{3,}\b', '', t, flags=re.IGNORECASE)
    t = re.sub(r'sfp\s*\+', 'sfp_plus', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


# ── Step 3: Vectorize ─────────────────────────────────────────────────────────

def vectorize(normalized_texts: list[str]):
    from sklearn.feature_extraction.text import TfidfVectorizer
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), max_features=5000)
    return vec.fit_transform(normalized_texts)


# ── Step 4: Cluster ───────────────────────────────────────────────────────────

def cluster(vectors, min_cluster_size: int = 3, max_clusters: int = 50) -> list[int]:
    try:
        from hdbscan import HDBSCAN
        labels = HDBSCAN(min_cluster_size=min_cluster_size).fit_predict(vectors.toarray())
    except ImportError:
        from sklearn.cluster import MiniBatchKMeans
        n = min(max_clusters, max(2, vectors.shape[0] // min_cluster_size))
        labels = MiniBatchKMeans(n_clusters=n, random_state=42).fit_predict(vectors)
    return list(labels)


# ── Step 5: Analyze clusters ──────────────────────────────────────────────────

def analyze_clusters(rows: list[dict], labels: list[int]) -> list[dict]:
    from collections import Counter
    import re

    grouped: dict[int, list[dict]] = defaultdict(list)
    for row, label in zip(rows, labels):
        if label == -1:
            continue
        grouped[label].append(row)

    result = []
    for label, members in grouped.items():
        all_words: list[str] = []
        for m in members:
            name = (
                m.get("option_name")
                or m.get("Option Name")
                or m.get("description")
                or m.get("Description")
                or ""
            )
            words = re.findall(r"[a-zA-Z0-9_+]+", name.lower())
            all_words.extend(words)
        top_terms = [w for w, _ in Counter(all_words).most_common(5)]

        result.append({
            "cluster_id":   label,
            "count":        len(members),
            "vendors":      sorted(set(m["vendor"] for m in members)),
            "source_files": sorted(set(m["source_file"] for m in members)),
            "examples":     [m["option_name"] for m in members[:3]],
            "top_terms":    top_terms,
        })

    result.sort(key=lambda c: c["count"], reverse=True)
    return result


# ── Step 6: Heuristic mapping ─────────────────────────────────────────────────

KEYWORD_DEVICE_MAP = {
    "chassis": "chassis",
    "rail": "rail", "rack": "rail", "slide": "rail",
    "fan": "fan", "cooling": "fan",
    "heatsink": "heatsink", "heat sink": "heatsink",
    "cable": "cable", "cord": "cable",
    "backplane": "backplane",
    "riser": "riser",
    "bezel": "bezel",
    "drive cage": "drive_cage", "cage": "drive_cage",
    "battery": "battery",
    "tpm": "tpm",
    "gpu": "gpu", "nvidia": "gpu",
    "transceiver": "transceiver", "sfp": "transceiver", "qsfp": "transceiver", "qsfp2": "transceiver", "gbic": "transceiver", "100g": "transceiver", "40g": "transceiver",
    "memory": "memory", "dimm": "memory",
    "cpu": "cpu", "processor": "cpu",
}


def heuristic_mapping(cluster_info: list[dict]) -> list[dict]:
    import re

    for c in cluster_info:
        search_tokens = set(c.get("top_terms", []))
        for example in c.get("examples", []):
            name = (
                example
                if isinstance(example, str)
                else (
                    example.get("option_name")
                    or example.get("Option Name")
                    or example.get("description")
                    or example.get("Description")
                    or ""
                )
                if isinstance(example, dict)
                else ""
            )
            words = re.findall(r"[a-zA-Z0-9_+]+", name.lower())
            search_tokens.update(words)
        full_text = " ".join([
            (e if isinstance(e, str) else "") for e in c.get("examples", [])
        ]).lower()
        text_blob = " ".join(search_tokens).lower() + " " + full_text

        proposed = ""
        for keyword, device_type in KEYWORD_DEVICE_MAP.items():
            if keyword in text_blob:
                proposed = device_type
                break

        if proposed:
            matching = [t for t in c.get("top_terms", []) if t in KEYWORD_DEVICE_MAP]
            pattern_parts = matching if matching else c.get("top_terms", [])[:3]
            suggested_rule = "|".join(re.escape(p) for p in pattern_parts) if pattern_parts else ""
            c["proposed_device_type"] = proposed
            c["confidence"] = "heuristic"
            c["suggested_yaml_rule"] = suggested_rule
        else:
            c["proposed_device_type"] = ""
            c["confidence"] = "manual_review"
            c["suggested_yaml_rule"] = ""

    return cluster_info


# ── Step 7: Write reports ─────────────────────────────────────────────────────

class _NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        import numpy as np
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def write_cluster_summary(clusters: list[dict], output_dir: Path, min_cluster_size: int = 3) -> None:
    clusters = [c for c in clusters if c["count"] >= min_cluster_size]
    # ── 1. cluster_summary.xlsx ───────────────────────────────────────────────
    rows = []
    for c in clusters:
        examples = c.get("examples", [])
        rows.append({
            "cluster_id":          c.get("cluster_id", ""),
            "count":               c.get("count", 0),
            "vendors":             ", ".join(c.get("vendors", [])),
            "top_terms":           ", ".join(c.get("top_terms", [])),
            "proposed_device_type": c.get("proposed_device_type", ""),
            "confidence":          c.get("confidence", ""),
            "example_1":           examples[0] if len(examples) > 0 else "",
            "example_2":           examples[1] if len(examples) > 1 else "",
            "example_3":           examples[2] if len(examples) > 2 else "",
            "suggested_yaml_rule": c.get("suggested_yaml_rule", ""),
        })

    df = pd.DataFrame(rows)
    xlsx_path = output_dir / "cluster_summary.xlsx"
    df.to_excel(xlsx_path, index=False, engine="openpyxl")
    print(f"[INFO] Written: {xlsx_path}")

    # ── 2. audit_report.json (update if exists) ───────────────────────────────
    json_path = output_dir / "audit_report.json"
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as fh:
                content = fh.read()
            report = json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            print(f"  [WARN] Could not parse {json_path.name}: {exc}", file=sys.stderr)
            report = {}

        report["clusters"] = {
            "total_candidates": sum(c.get("count", 0) for c in clusters),
            "total_clusters":   len(clusters),
            "clusters":         clusters,
        }

        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2, cls=_NumpyEncoder)
        print(f"[INFO] Updated: {json_path}")


# ── Dry-run report ────────────────────────────────────────────────────────────

def print_dry_run_report(candidates: list[dict]) -> None:
    by_vendor: dict[str, int] = defaultdict(int)
    for c in candidates:
        by_vendor[c["vendor"]] += 1

    print(f"\nDry-run: {len(candidates)} candidate row(s) found\n")
    print(f"  {'Vendor':<12} {'Count':>6}")
    print(f"  {'-'*12} {'-'*6}")
    for vendor in sorted(by_vendor):
        print(f"  {vendor:<12} {by_vendor[vendor]:>6}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    if not output_dir.is_dir():
        print(f"[ERROR] --output-dir does not exist or is not a directory: {output_dir}",
              file=sys.stderr)
        return 1

    print(f"[INFO] Scanning: {output_dir}")
    if args.vendor:
        print(f"[INFO] Vendor filter: {args.vendor}")

    # ── Step 1: Load candidates ───────────────────────────────────────────────
    try:
        candidates = load_candidate_rows(output_dir, vendor_filter=args.vendor)
    except Exception as exc:
        print(f"[ERROR] Failed to load candidate rows: {exc}", file=sys.stderr)
        return 1

    if not candidates:
        print("[INFO] No candidate rows found. Nothing to cluster.")
        return 0

    if args.dry_run:
        print_dry_run_report(candidates)
        return 0

    # ── Steps 2–7: Normalize → vectorize → cluster → analyze → report ────────
    print(f"[INFO] {len(candidates)} candidates loaded. Starting clustering pipeline...")

    try:
        normalized = [normalize_text(c["option_name"]) for c in candidates]
        vectors = vectorize(normalized)
        labels = cluster(vectors,
                         min_cluster_size=args.min_cluster_size,
                         max_clusters=args.max_clusters)
        cluster_info = analyze_clusters(candidates, labels)
        cluster_info = heuristic_mapping(cluster_info)
        write_cluster_summary(cluster_info, output_dir, min_cluster_size=args.min_cluster_size)
    except NotImplementedError as exc:
        print(f"[INFO] Clustering pipeline not yet implemented: {exc}")
        print("[INFO] Run with --dry-run to see candidate counts.")
        return 0
    except Exception as exc:
        print(f"[ERROR] Clustering pipeline failed: {exc}", file=sys.stderr)
        return 1

    print("[INFO] Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
