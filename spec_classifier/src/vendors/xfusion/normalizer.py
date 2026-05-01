"""
xFusion eDeal row normalization: raw dicts → XFusionNormalizedRow.

Sheet 'AllInOne', header row 8 (0-based), data from row 9.

Rollup propagation with **level offset +1** vs Huawei (per VENDOR_FORMAT_SPEC.md
(xfusion) §6.2). Hierarchy is keyed on (Position No, Part Number, Model,
Description) shape rather than on a single position-no depth count, because
xFusion uses position numbers only on intermediate level-1/2/3 rows and leaves
both level-0 (site/group) and leaf (ITEM) rows with empty Position No:

  level-0 (site/group)   col2=""     col3=non-empty col4="" col5=""
                         e.g. "Spec_GPU_T4_3_Site1", "5288 V7 Spare Parts Overseas"
                         → set current_group_name (strip trailing "_Site1")
  level-1 (server cfg)   col2="N"    col3=model     col4=model     col5=""
                         → set current_product_name = col4 (CC Q8: populate)
  level-2 (sub-line)     col2="N.M"  col3=model     col4=model     col5=""
                         → no-op (collapsed into product_name)
  level-3 (sub-module)   col2="N.M.K" col3=label    col4=label     col5=""
                         → set current_module_name = col3
  leaf (ITEM)            col2=""     col3=SKU       col4=part-code col5=desc
                         → emit XFusionNormalizedRow(row_kind=ITEM)

Reset rules (CC Q7 — module_name is group-local):
  level-0 boundary  → reset current_product_name AND current_module_name
  level-1 boundary  → reset current_module_name
"""

from dataclasses import dataclass
from typing import List, Optional

from src.core.normalizer import NormalizedRow, RowKind
from src.vendors.xfusion.parser import _is_sku_shape


def _is_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and value != value:  # NaN
        return True
    return str(value).strip() == ""


@dataclass
class XFusionNormalizedRow(NormalizedRow):
    """xFusion normalized row with vendor extensions per VENDOR_FORMAT_SPEC §4."""
    position_no:    str   = ""    # col2 ("" for ITEM, "1.1.3" for HEADER)
    model:          str   = ""    # col4 (vendor part code on ITEM, model name on level-1 HEADER)
    unit_qty:       int   = 0     # col6
    total_price:    float = 0.0   # col9
    lead_time_days: str   = ""    # col10 ("Uncertain" / "-" / numeric — kept verbatim)


def _strip_site_suffix(name: str) -> str:
    """Strip trailing '_Site1' (or '_Site2', …) from standard Spec_*_Site1 group names.
    Spare Parts groups (no suffix) pass through unchanged.
    """
    s = name.strip()
    parts = s.rsplit("_", 1)
    if len(parts) == 2 and parts[1].lower().startswith("site") and parts[1][4:].isdigit():
        return parts[0]
    return s


def normalize_xfusion_rows(raw_rows: List[dict]) -> List[XFusionNormalizedRow]:
    """
    Normalize raw xFusion AllInOne rows into XFusionNormalizedRow objects.
    See module docstring for the level taxonomy.
    """
    if not raw_rows:
        return []

    result: List[XFusionNormalizedRow] = []
    current_group_name:   Optional[str] = None
    current_product_name: Optional[str] = None
    current_module_name:  str           = ""

    for row in raw_rows:
        source_row_index = int(row.get("__row_index__", 0))

        position_no_raw = row.get("Position No")
        part_number_raw = row.get("Part Number")
        model_raw       = row.get("Model")
        description_raw = row.get("Description")
        unit_qty_raw    = row.get("Unit Qty.")
        qty_raw         = row.get("Qty.")
        price_raw       = row.get("Unit Price")
        total_raw       = row.get("Total Price")
        lt_raw          = row.get("production_lt_days")

        position_no = str(position_no_raw).strip() if not _is_empty(position_no_raw) else ""
        part_number = str(part_number_raw).strip() if not _is_empty(part_number_raw) else ""
        model_str   = str(model_raw).strip()       if not _is_empty(model_raw)       else ""
        description = str(description_raw).strip() if not _is_empty(description_raw) else ""

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
            total_price = float(total_raw) if not _is_empty(total_raw) else 0.0
        except (TypeError, ValueError):
            total_price = 0.0

        lead_time_days = str(lt_raw).strip() if not _is_empty(lt_raw) else ""

        # ----- ITEM detection (per §3.2 ITEM rule): col2 empty + col3 SKU-shape + col5 non-empty.
        is_item = (not position_no) and _is_sku_shape(part_number) and bool(description)

        if is_item:
            result.append(
                XFusionNormalizedRow(
                    source_row_index=source_row_index,
                    row_kind=RowKind.ITEM,
                    group_name=current_group_name,
                    group_id=None,
                    product_name=current_product_name,
                    module_name=current_module_name,
                    option_name=description,
                    option_id=part_number,
                    skus=[part_number],
                    qty=qty,
                    option_price=option_price,
                    position_no=position_no,
                    model=model_str,
                    unit_qty=unit_qty,
                    total_price=total_price,
                    lead_time_days=lead_time_days,
                )
            )
            continue

        # ----- HEADER row → update rollup context based on shape.
        # level-0 (site/group): col2 empty, col3 non-empty, col4 empty, col5 empty.
        # level-1 (server config): col2 single integer, col4 non-empty.
        # level-3 (sub-module): col2 has at least 2 dots ("N.M.K"), col3 non-empty.
        # level-2 (sub-line): col2 has exactly 1 dot — no-op.
        if not position_no and part_number and not model_str and not description:
            current_group_name = _strip_site_suffix(part_number) or None
            current_product_name = None
            current_module_name = ""
        elif position_no and "." not in position_no:
            current_product_name = model_str if model_str else None
            current_module_name = ""
        elif position_no.count(".") >= 2:
            current_module_name = part_number

        result.append(
            XFusionNormalizedRow(
                source_row_index=source_row_index,
                row_kind=RowKind.HEADER,
                group_name=current_group_name,
                group_id=None,
                product_name=current_product_name,
                module_name=current_module_name,
                option_name=description,
                option_id=None,
                skus=[],
                qty=qty,
                option_price=option_price,
                position_no=position_no,
                model=model_str,
                unit_qty=unit_qty,
                total_price=total_price,
                lead_time_days=lead_time_days,
            )
        )

    return result
