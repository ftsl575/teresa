"""
Huawei eDeal row normalization: raw dicts → HuaweiNormalizedRow.
Sheet 'AllInOne', header row 8, data from row 9.
Rollup propagation: top-level (position_no depth 1) sets group_name and
resets module_name; mid-level (depth 2) sets module_name; leaf rows
(Part Number present) are RowKind.ITEM and inherit current context.
"""

from dataclasses import dataclass
from typing import List, Optional

from src.core.normalizer import NormalizedRow, RowKind


def _is_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and value != value:  # NaN
        return True
    return str(value).strip() == ""


@dataclass
class HuaweiNormalizedRow(NormalizedRow):
    """Huawei normalized row with vendor extensions per VENDOR_FORMAT_SPEC §4."""
    position_no:    str   = ""
    unit_qty:       int   = 0
    total_price:    float = 0.0
    lead_time_days: str   = ""
    eom:            str   = ""
    eos:            str   = ""


def normalize_huawei_rows(raw_rows: List[dict]) -> List[HuaweiNormalizedRow]:
    if not raw_rows:
        return []

    result: List[HuaweiNormalizedRow] = []
    current_group_name: Optional[str] = None
    current_module_name: str = ""

    for row in raw_rows:
        source_row_index = int(row.get("__row_index__", 0))

        # --- core fields from parser dict ---
        position_no_raw = row.get("Position No")
        part_number_raw = row.get("Part Number")
        description_raw = row.get("Product Description")
        qty_raw         = row.get("Qty")
        price_raw       = row.get("Total Price")
        unit_qty_raw    = row.get("Unit Quantity")
        ext_price_raw   = row.get("Extended Price")
        model_raw       = row.get("_col4_aux")
        lt_raw          = row.get("production_lt_days")
        eom_raw         = row.get("eom")
        eos_raw         = row.get("eos")

        # --- coerce scalars ---
        position_no = str(position_no_raw).strip() if not _is_empty(position_no_raw) else ""
        part_number = str(part_number_raw).strip() if not _is_empty(part_number_raw) else ""
        option_name = str(description_raw).strip() if not _is_empty(description_raw) else ""

        try:
            qty = int(float(qty_raw)) if not _is_empty(qty_raw) else 1
            if qty == 0:
                qty = 1
        except (TypeError, ValueError):
            qty = 1

        try:
            option_price = float(price_raw) if not _is_empty(price_raw) else 0.0
        except (TypeError, ValueError):
            option_price = 0.0

        try:
            unit_qty = int(float(unit_qty_raw)) if not _is_empty(unit_qty_raw) else 0
        except (TypeError, ValueError):
            unit_qty = 0

        try:
            total_price = float(ext_price_raw) if not _is_empty(ext_price_raw) else 0.0
        except (TypeError, ValueError):
            total_price = 0.0

        lead_time_days = str(lt_raw).strip() if not _is_empty(lt_raw) else ""
        eom_val        = str(eom_raw).strip() if not _is_empty(eom_raw) else ""
        eos_val        = str(eos_raw).strip() if not _is_empty(eos_raw) else ""

        product_name_str = str(model_raw).strip() if not _is_empty(model_raw) else ""
        product_name: Optional[str] = product_name_str if product_name_str else None

        # --- rollup propagation (§3.3) ---
        is_leaf = bool(part_number)
        levels = position_no.split(".") if position_no else []
        level_count = len(levels) if position_no else 0

        if not is_leaf:
            if level_count == 1:
                current_group_name = option_name if option_name else None
                current_module_name = ""          # R10: mandatory reset
            elif level_count == 2:
                current_module_name = option_name
            # level 0, 3, 4+ — context unchanged
            row_kind = RowKind.HEADER
        else:
            row_kind = RowKind.ITEM

        option_id = part_number if is_leaf else None
        skus = [part_number] if is_leaf else []

        result.append(
            HuaweiNormalizedRow(
                source_row_index=source_row_index,
                row_kind=row_kind,
                group_name=current_group_name if current_group_name else None,
                group_id=None,
                product_name=product_name,
                module_name=current_module_name,
                option_name=option_name,
                option_id=option_id,
                skus=skus,
                qty=qty,
                option_price=option_price,
                position_no=position_no,
                unit_qty=unit_qty,
                total_price=total_price,
                lead_time_days=lead_time_days,
                eom=eom_val,
                eos=eos_val,
            )
        )

    return result
