"""
Cisco CCW row normalization: raw dicts → CiscoNormalizedRow (core contract + vendor extension).
"""

from dataclasses import dataclass, field
from typing import List, Optional

from src.core.normalizer import RowKind


def _is_empty(value) -> bool:
    """Treat None, NaN, and blank string as empty."""
    if value is None:
        return True
    if isinstance(value, float) and value != value:
        return True
    return str(value).strip() == ""


@dataclass
class CiscoNormalizedRow:
    """Cisco normalized row — duck-type compatible с Dell NormalizedRow."""

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
    option_price: float = 0.0

    # === Vendor Extension ===
    line_number: str = ""
    bundle_id: str = ""
    is_top_level: bool = False
    is_bundle_root: bool = False
    parent_line_number: Optional[str] = None
    service_duration_months: Optional[int] = None
    smart_account_mandatory: bool = False
    lead_time_days: Optional[int] = None
    unit_net_price: float = 0.0
    disc_pct: float = 0.0
    extended_net_price: float = 0.0


def normalize_cisco_rows(raw_rows: List[dict]) -> List[CiscoNormalizedRow]:
    """
    Двухпроходная нормализация.

    ПРОХОД 1: Собрать метаданные.
    - line_number, bundle_id, is_top_level для каждой строки.
    - bundle_ids_with_children: set bundle_id для строк где is_top_level=False (т.е. есть дочерние).
    - top_level_descriptions: {bundle_id: Description} для строк где is_top_level=True.

    ПРОХОД 2: Создать CiscoNormalizedRow.
    - is_bundle_root = is_top_level AND bundle_id in bundle_ids_with_children
    - parent_line_number по контракту (X.0 → None, X.Y → X.0, X.Y.Z → X.Y).
    - module_name = top_level_descriptions.get(bundle_id, "")
    """
    if not raw_rows:
        return []

    bundle_ids_with_children: set = set()
    top_level_descriptions: dict = {}

    for row in raw_rows:
        ln = str(row.get("Line Number", "")).strip()
        parts = ln.split(".")
        bundle_id = parts[0] if parts else ""
        is_top_level = len(parts) == 2 and parts[1] == "0"

        if is_top_level:
            top_level_descriptions[bundle_id] = str(row.get("Description", "")).strip()
        else:
            if bundle_id:
                bundle_ids_with_children.add(bundle_id)

    result: List[CiscoNormalizedRow] = []
    for row in raw_rows:
        ln = str(row.get("Line Number", "")).strip()
        parts = ln.split(".")
        bundle_id = parts[0] if parts else ""
        is_top_level = len(parts) == 2 and parts[1] == "0"
        is_bundle_root = is_top_level and bundle_id in bundle_ids_with_children

        if is_top_level:
            parent_line_number = None
        elif len(parts) == 2:
            parent_line_number = parts[0] + ".0"
        elif len(parts) >= 3:
            parent_line_number = ".".join(parts[:-1])
        else:
            parent_line_number = None

        module_name = top_level_descriptions.get(bundle_id, "")

        desc = row.get("Description")
        option_name = str(desc).strip() if not _is_empty(desc) else ""

        pn = row.get("Part Number")
        skus = [str(pn).strip().rstrip("=")] if not _is_empty(pn) else []

        qty_val = row.get("Qty")
        try:
            qty = int(float(qty_val)) if not _is_empty(qty_val) else 1
        except (TypeError, ValueError):
            qty = 1

        ulp = row.get("Unit List Price")
        try:
            option_price = float(ulp) if not _is_empty(ulp) else 0.0
        except (TypeError, ValueError):
            option_price = 0.0

        svc = row.get("Service Duration (Months)")
        if _is_empty(svc) or str(svc).strip() == "---":
            service_duration_months = None
        else:
            try:
                service_duration_months = int(float(svc))
            except (TypeError, ValueError):
                service_duration_months = None

        smart_val = row.get("Smart Account Mandatory", "")
        smart_account_mandatory = str(smart_val).strip() == "Yes"

        lead_val = row.get("Estimated Lead Time (Days)")
        try:
            lead_time_days = int(float(lead_val)) if not _is_empty(lead_val) else None
        except (TypeError, ValueError):
            lead_time_days = None

        try:
            unit_net_price = float(row.get("Unit Net Price") or 0) if not _is_empty(row.get("Unit Net Price")) else 0.0
        except (TypeError, ValueError):
            unit_net_price = 0.0

        try:
            disc_pct = float(row.get("Disc(%)") or 0) if not _is_empty(row.get("Disc(%)")) else 0.0
        except (TypeError, ValueError):
            disc_pct = 0.0

        try:
            extended_net_price = float(row.get("Extended Net Price") or 0) if not _is_empty(row.get("Extended Net Price")) else 0.0
        except (TypeError, ValueError):
            extended_net_price = 0.0

        source_row_index = int(row.get("__row_index__", 0))

        result.append(
            CiscoNormalizedRow(
                source_row_index=source_row_index,
                row_kind=RowKind.ITEM,
                group_name=None,
                group_id=None,
                product_name=None,
                module_name=module_name,
                option_name=option_name,
                option_id=None,
                skus=skus,
                qty=qty,
                option_price=option_price,
                line_number=ln,
                bundle_id=bundle_id,
                is_top_level=is_top_level,
                is_bundle_root=is_bundle_root,
                parent_line_number=parent_line_number,
                service_duration_months=service_duration_months,
                smart_account_mandatory=smart_account_mandatory,
                lead_time_days=lead_time_days,
                unit_net_price=unit_net_price,
                disc_pct=disc_pct,
                extended_net_price=extended_net_price,
            )
        )

    return result
