import openpyxl
from src.vendors.base import VendorAdapter
from src.vendors.cisco.parser import parse_excel
from src.vendors.cisco.normalizer import normalize_cisco_rows


class CiscoAdapter(VendorAdapter):
    def __init__(self, config: dict = None):
        self._config = config or {}

    def can_parse(self, path: str) -> bool:
        wb = openpyxl.load_workbook(path, read_only=True)
        try:
            return "Price Estimate" in wb.sheetnames
        finally:
            wb.close()

    def parse(self, filepath: str):
        return parse_excel(filepath)

    def normalize(self, raw_rows):
        return normalize_cisco_rows(raw_rows)

    def get_rules_file(self):
        vendor_rules = self._config.get("vendor_rules", {})
        return vendor_rules.get("cisco", "rules/cisco_rules.yaml")

    def get_vendor_stats(self, normalized_rows: list) -> dict:
        bundle_roots = [r for r in normalized_rows if getattr(r, "is_bundle_root", False)]
        svc_rows = [r for r in normalized_rows if getattr(r, "service_duration_months", None) is not None]
        depths = []
        for r in normalized_rows:
            ln = getattr(r, "line_number", "")
            if ln:
                depths.append(len(ln.split(".")))
        return {
            "top_level_bundles_count": len(bundle_roots),
            "rows_with_service_duration": len(svc_rows),
            "max_hierarchy_depth": max(depths) if depths else 0,
        }

    def generates_branded_spec(self) -> bool:
        return False
