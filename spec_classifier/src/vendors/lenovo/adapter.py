from typing import Optional

from src.vendors.base import VendorAdapter
from src.vendors.lenovo.parser import (
    parse_excel_with_sheet,
    workbook_has_lenovo_dcsc_header,
)
from src.vendors.lenovo.normalizer import normalize_lenovo_rows


class LenovoAdapter(VendorAdapter):
    def __init__(self, config: dict = None):
        self._config = config or {}
        # Sheet name actually used by the most recent parse() call; consumed by
        # get_source_sheet_name() so annotated_writer reads from the same sheet.
        self._last_source_sheet: Optional[str] = None

    def can_parse(self, path: str) -> bool:
        """
        True when some non-excluded sheet contains the Lenovo DCSC marker header row
        (Part number, Product Description, Qty, Price, Export Control) in its first
        30 rows -- same criterion as LenovoParser sheet/header detection.
        """
        return workbook_has_lenovo_dcsc_header(path)

    def parse(self, filepath: str):
        self._last_source_sheet = None
        rows, header_row_index, chosen_sheet = parse_excel_with_sheet(filepath)
        self._last_source_sheet = chosen_sheet
        return (rows, header_row_index)

    def normalize(self, raw_rows):
        return normalize_lenovo_rows(raw_rows)

    def get_rules_file(self):
        vendor_rules = self._config.get("vendor_rules", {})
        return vendor_rules.get("lenovo", "rules/lenovo_rules.yaml")

    def get_vendor_stats(self, normalized_rows: list) -> dict:
        cto_count = sum(
            1 for r in normalized_rows
            if getattr(r, "option_id", None) and "CTO" in str(r.option_id).upper()
        )
        export_controlled = sum(
            1 for r in normalized_rows
            if getattr(r, "export_control", "") == "Yes"
        )
        return {
            "cto_count": cto_count,
            "export_controlled_count": export_controlled,
        }

    def get_source_sheet_name(self) -> str | None:
        """
        Sheet name actually used by the most recent parse() call. Returns None if
        parse() has not run yet -- callers (annotated_writer) treat None as "use
        sheet index 0", which matches the legacy default.
        """
        return self._last_source_sheet

    def get_extra_cols(self) -> list[tuple[str, str]]:
        return [("export_control", "export_control")]

    def generates_branded_spec(self) -> bool:
        return True
