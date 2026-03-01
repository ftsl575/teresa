"""
HPE BOM row normalization: raw dicts → HPENormalizedRow (core contract + vendor extension).
"""

from dataclasses import dataclass, field
from typing import List, Optional

from src.core.normalizer import RowKind


def _is_empty(value) -> bool:
    """Treat None, NaN, and blank string as empty."""
    if value is None:
        return True
    if isinstance(value, float) and value != value:  # NaN check
        return True
    return str(value).strip() == ""


@dataclass
class HPENormalizedRow:
    """HPE normalized row — duck-type compatible with core NormalizedRow contract."""

    # === Core Contract ===
    source_row_index: int = 0
    row_kind: RowKind = RowKind.ITEM
    group_name: Optional[str] = None
    group_id: Optional[str] = None
    product_name: Optional[str] = None
    module_name: str = ""
    option_name: str = ""
    option_id: Optional[str] = None
    skus: List[str] = field(default_factory=list)
    qty: int = 1
    option_price: float = 0.0  # strictly float; 0.0 when empty (never None)

    # === Vendor Extension ===
    product_type: str = ""              # HW/SW from 'Product Type' col (optional)
    extended_price: float = 0.0        # from 'Extended List Price (USD)' (optional)
    lead_time: str = ""                 # from 'Estimated Availability Lead Time' (optional)
    config_name: str = ""               # from 'Config Name' = group_name (optional)
    is_factory_integrated: bool = False  # True when description == "Factory Integrated"


def normalize_hpe_rows(raw_rows: List[dict]) -> List[HPENormalizedRow]:
    """
    Normalize raw HPE BOM dicts to HPENormalizedRow list.

    Key rules:
    - option_id: full 'Product #' value (no split)
    - skus: [base_sku] where base_sku = Product # up to first space
    - option_price: 0.0 when empty (contract: float, never None)
    - group_name / module_name: from 'Config Name' if present, else ""
    - group_id: base SKU (same as skus[0] if non-empty)
    - is_factory_integrated: True when option_name == "Factory Integrated" (vendor extension only)
    - entity_type = CONFIG for Factory Integrated: assigned by YAML rule CONFIG-H-001, NOT here
    """
    if not raw_rows:
        return []

    result: List[HPENormalizedRow] = []
    for row in raw_rows:
        source_row_index = int(row.get("__row_index__", 0))

        # option_name from 'Product Description'
        desc = row.get("Product Description")
        option_name = str(desc).strip() if not _is_empty(desc) else ""

        # option_id: full 'Product #' without split
        product_num = row.get("Product #")
        if not _is_empty(product_num):
            option_id = str(product_num).strip()
            # base SKU = part before first space
            base_sku = option_id.split()[0] if option_id else ""
            skus = [base_sku] if base_sku else []
        else:
            option_id = None
            skus = []

        # group_id = base SKU
        group_id = skus[0] if skus else None

        # qty
        qty_val = row.get("Qty")
        try:
            qty = int(float(qty_val)) if not _is_empty(qty_val) else 1
        except (TypeError, ValueError):
            qty = 1

        # option_price: strictly 0.0 when empty (not None) — DATA_CONTRACTS.md §4
        price_val = row.get("Unit Price (USD)")
        try:
            option_price = float(price_val) if not _is_empty(price_val) else 0.0
        except (TypeError, ValueError):
            option_price = 0.0

        # Config Name → group_name and module_name (optional column)
        config_name_val = row.get("Config Name")
        if not _is_empty(config_name_val):
            config_name = str(config_name_val).strip()
        else:
            config_name = ""
        group_name = config_name if config_name else None
        module_name = config_name  # "" if absent

        # vendor extension: product_type
        pt_val = row.get("Product Type")
        product_type = str(pt_val).strip() if not _is_empty(pt_val) else ""

        # vendor extension: extended_price
        ep_val = row.get("Extended List Price (USD)")
        try:
            extended_price = float(ep_val) if not _is_empty(ep_val) else 0.0
        except (TypeError, ValueError):
            extended_price = 0.0

        # vendor extension: lead_time
        lt_val = row.get("Estimated Availability Lead Time")
        lead_time = str(lt_val).strip() if not _is_empty(lt_val) else ""

        # vendor extension: is_factory_integrated
        # NOTE: entity_type = CONFIG is assigned by YAML rule CONFIG-H-001, NOT here
        is_factory_integrated = (option_name == "Factory Integrated")

        result.append(
            HPENormalizedRow(
                source_row_index=source_row_index,
                row_kind=RowKind.ITEM,
                group_name=group_name,
                group_id=group_id,
                product_name=None,  # no separate product name field in HPE BOM
                module_name=module_name,
                option_name=option_name,
                option_id=option_id,
                skus=skus,
                qty=qty,
                option_price=option_price,
                product_type=product_type,
                extended_price=extended_price,
                lead_time=lead_time,
                config_name=config_name,
                is_factory_integrated=is_factory_integrated,
            )
        )

    return result
