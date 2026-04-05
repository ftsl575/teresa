"""
Lenovo DCSC row normalization: raw dicts → LenovoNormalizedRow.
"""

import re
from dataclasses import dataclass
from typing import List, Optional

from src.core.normalizer import NormalizedRow, RowKind


def _is_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and value != value:
        return True
    return str(value).strip() == ""


@dataclass
class LenovoNormalizedRow(NormalizedRow):
    """Lenovo normalized row with vendor extension."""
    export_control: str = ""


_CTO_RE = re.compile(r"CTO", re.IGNORECASE)
_CONFIG_PREFIX_RE = re.compile(r"^(.+?)\s*:\s*", re.IGNORECASE)


def normalize_lenovo_rows(raw_rows: List[dict]) -> List[LenovoNormalizedRow]:
    if not raw_rows:
        return []

    result: List[LenovoNormalizedRow] = []
    current_config_name = ""

    for row in raw_rows:
        source_row_index = int(row.get("__row_index__", 0))

        part_number_raw = row.get("Part number")
        description_raw = row.get("Product Description")

        part_number = str(part_number_raw).strip() if not _is_empty(part_number_raw) else None
        option_name = str(description_raw).strip() if not _is_empty(description_raw) else ""

        option_id = part_number
        skus = [part_number] if part_number else []

        qty_val = row.get("Qty")
        try:
            qty = int(float(qty_val)) if not _is_empty(qty_val) else 1
        except (TypeError, ValueError):
            qty = 1

        price_val = row.get("Price")
        try:
            option_price = float(price_val) if not _is_empty(price_val) else 0.0
        except (TypeError, ValueError):
            option_price = 0.0

        export_control_raw = row.get("Export Control")
        export_control = str(export_control_raw).strip() if not _is_empty(export_control_raw) else ""

        if option_id is None and option_name == "":
            row_kind = RowKind.HEADER
        else:
            row_kind = RowKind.ITEM

        # CTO rows define a new server configuration group
        is_cto = part_number is not None and _CTO_RE.search(part_number)
        if is_cto and option_name:
            m = _CONFIG_PREFIX_RE.match(option_name)
            if m:
                current_config_name = m.group(1).strip()
            else:
                current_config_name = option_name

        group_name = current_config_name if current_config_name else None
        module_name = current_config_name if current_config_name else ""

        result.append(
            LenovoNormalizedRow(
                source_row_index=source_row_index,
                row_kind=row_kind,
                group_name=group_name,
                group_id=None,
                product_name=None,
                module_name=module_name,
                option_name=option_name,
                option_id=option_id,
                skus=skus,
                qty=qty,
                option_price=option_price,
                export_control=export_control,
            )
        )

    return result
