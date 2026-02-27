"""
Row normalization and row_kind detection for Dell specification rows.
HEADER = Module Name, Option Name, SKUs all empty; otherwise ITEM.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

# Optional pandas NaN handling without requiring pandas import
def _is_empty(value) -> bool:
    """Treat None, NaN, and blank string as empty."""
    if value is None:
        return True
    if isinstance(value, float) and value != value:  # NaN
        return True
    return str(value).strip() == ""


def _str_val(value) -> str:
    """Normalize value to string, empty if None/NaN."""
    if value is None:
        return ""
    if isinstance(value, float) and value != value:
        return ""
    return str(value).strip()


class RowKind(Enum):
    """Type of row: real line item or section header/separator."""

    ITEM = "ITEM"  # Real position (has SKU or Option Name + Qty)
    HEADER = "HEADER"  # Separator/header (empty key fields)


@dataclass
class NormalizedRow:
    """Single row after normalization, with row_kind and cleaned fields."""

    source_row_index: int
    row_kind: RowKind
    group_name: Optional[str]
    group_id: Optional[str]
    product_name: Optional[str]
    module_name: str
    option_name: str
    option_id: Optional[str]
    skus: List[str]
    qty: int
    option_price: float


def detect_row_kind(raw_row: dict) -> RowKind:
    """
    Determine row type: HEADER or ITEM.

    HEADER if Module Name, Option Name, and SKUs are all empty (None or "" after strip).
    Otherwise ITEM.
    """
    module_empty = _is_empty(raw_row.get("Module Name"))
    option_empty = _is_empty(raw_row.get("Option Name"))
    skus_val = raw_row.get("SKUs")
    skus_empty = _is_empty(skus_val)
    if module_empty and option_empty and skus_empty:
        return RowKind.HEADER
    return RowKind.ITEM


def normalize_row(raw_row: dict) -> NormalizedRow:
    """
    Normalize a raw row from Excel: strip strings, parse SKUs, coerce types.

    - Determines row_kind via detect_row_kind().
    - SKUs: split by comma, strip each, list of non-empty strings.
    - Qty -> int (default 0), Option List Price -> float (default 0.0).
    """
    row_kind = detect_row_kind(raw_row)

    module_name = _str_val(raw_row.get("Module Name"))
    option_name = _str_val(raw_row.get("Option Name"))

    skus_raw = _str_val(raw_row.get("SKUs"))
    skus = [s.strip() for s in skus_raw.split(",") if s.strip()]

    try:
        qty_val = raw_row.get("Qty")
        qty = int(qty_val) if qty_val is not None and not _is_empty(qty_val) else 0
    except (TypeError, ValueError):
        qty = 0

    try:
        price_val = raw_row.get("Option List Price")
        option_price = (
            float(price_val)
            if price_val is not None and not _is_empty(price_val)
            else 0.0
        )
    except (TypeError, ValueError):
        option_price = 0.0

    def opt_str(key: str) -> Optional[str]:
        v = raw_row.get(key)
        if v is None or _is_empty(v):
            return None
        return str(v).strip() or None

    return NormalizedRow(
        source_row_index=int(raw_row["__row_index__"]),
        row_kind=row_kind,
        group_name=opt_str("Group Name"),
        group_id=opt_str("Group ID"),
        product_name=opt_str("Product Name"),
        module_name=module_name,
        option_name=option_name,
        option_id=opt_str("Option ID"),
        skus=skus,
        qty=qty,
        option_price=option_price,
    )
