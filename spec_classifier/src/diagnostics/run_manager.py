"""
Run folder management: create and prepare per-spec output directories.

Naming convention:
  Spec folder: <output_root>/<bucket>/<vendor>/<spec>/  (e.g. SPLIT/dell/dl1/)
"""

import shutil
import sys
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


# README content is defined at module level so write_manifest stays a thin writer.
_MANIFEST_CONTENT = """\
# Выходные артефакты классификатора

Папка содержит результаты классификации аппаратных спецификаций.
Артефакты сгруппированы по трём директориям (`READY/`, `SPLIT/`, `AUDIT/`).
Структура вложения: `<bucket>/<vendor>/<spec>/`.

---

## READY — Готовые документы для заказчика

| Файл | Директория | Назначение |
|------|-----------|------------|
| `Коммерческое предложение_<spec>.xlsx` | `READY/<vendor>/<spec>/` | Готовое коммерческое предложение для заказчика |

---

## SPLIT — Технические артефакты классификации

| Файл | Директория | Назначение |
|------|-----------|------------|
| `cleaned_spec.xlsx` | `SPLIT/<vendor>/<spec>/` | Очищенная спецификация (исходные данные без служебных строк) |
| `classification.jsonl` | `SPLIT/<vendor>/<spec>/` | Результаты классификации строк в формате JSONL |
| `<spec>_annotated.xlsx` | `SPLIT/<vendor>/<spec>/` | Аннотированная спецификация с классификацией каждой строки |
| `rows_raw.json` | `SPLIT/<vendor>/<spec>/` | Сырые данные строк до нормализации |
| `rows_normalized.json` | `SPLIT/<vendor>/<spec>/` | Нормализованные данные строк |
| `run_summary.json` | `SPLIT/<vendor>/<spec>/` | Сводка по запуску (статистика, хэши файлов) |
| `unknown_rows.csv` | `SPLIT/<vendor>/<spec>/` | Строки с неопределённым типом сущности |
| `header_rows.csv` | `SPLIT/<vendor>/<spec>/` | Заголовочные строки из спецификации |
| `run.log` | `SPLIT/<vendor>/<spec>/` | Лог выполнения классификатора |

---

## AUDIT — Результаты аудита и кластеризации

| Файл | Директория | Назначение |
|------|-----------|------------|
| `<spec>_annotated_audited.xlsx` | `AUDIT/<vendor>/<spec>/` | Аннотированная спецификация с результатами E-code аудита |
| `audit_report.json` | `AUDIT/` | Сводный отчёт аудита по всем спецификациям |
| `audit_summary.xlsx` | `AUDIT/` | Таблица результатов аудита (все ошибки по всем файлам) |
| `cluster_summary.xlsx` | `AUDIT/` | Сводка кластеризации неизвестных и неклассифицированных строк |
"""


def write_manifest(output_root: Path) -> None:
    """Write a static README.md artifact index at output_root.

    The table lists every v1.2 artifact type grouped under READY / SPLIT / AUDIT,
    with file pattern, bucket/path, and purpose in Russian.

    Idempotent: subsequent calls overwrite the file with identical bytes.

    Args:
        output_root: top-level output directory (sibling of READY/, SPLIT/, AUDIT/).
    """
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    readme = output_root / "README.md"
    readme.write_text(_MANIFEST_CONTENT, encoding="utf-8")


def detect_vendor_from_path(path: Path, known_vendors: list[str]) -> str:
    """Detect vendor from path components using known vendor list.

    Checks for /<vendor>/ as a path segment in the full path string (case-insensitive).
    known_vendors is required — the caller resolves it from config.

    Returns:
        vendor string if found in path, "unknown" otherwise (with a WARN to stderr).
    """
    s = str(path).lower()
    for vendor in known_vendors:
        if f"/{vendor}/" in s or f"\\{vendor}\\" in s:
            return vendor
    print(f"  [WARN] Cannot detect vendor from path: {path}", file=sys.stderr)
    return "unknown"
