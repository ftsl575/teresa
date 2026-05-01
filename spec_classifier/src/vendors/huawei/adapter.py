import openpyxl
from src.vendors.base import VendorAdapter
from src.vendors.huawei.parser import parse_excel
from src.vendors.huawei.normalizer import normalize_huawei_rows


class HuaweiAdapter(VendorAdapter):
    def __init__(self, config: dict = None):
        self._config = config or {}

    def can_parse(self, path: str) -> bool:
        """
        Positive signature:
        1. Sheet "AllInOne" present in workbook.
        2. Cell row 0, col 2 (C1) contains exactly "COL_SORTNO.0".
        """
        wb = openpyxl.load_workbook(path, read_only=True)
        try:
            if "AllInOne" not in wb.sheetnames:
                return False
            ws = wb["AllInOne"]
            row0 = next(ws.iter_rows(max_row=1, values_only=True), ())
            if len(row0) < 3 or row0[2] is None:
                return False
            return str(row0[2]).strip() == "COL_SORTNO.0"
        finally:
            wb.close()

    def parse(self, filepath: str):
        return parse_excel(filepath)

    def normalize(self, raw_rows):
        return normalize_huawei_rows(raw_rows)

    def get_rules_file(self):
        vendor_rules = self._config.get("vendor_rules", {})
        return vendor_rules.get("huawei", "rules/huawei_rules.yaml")

    def get_vendor_stats(self, normalized_rows: list) -> dict:
        return {}

    def get_source_sheet_name(self) -> str | None:
        return "AllInOne"

    def get_extra_cols(self) -> list[tuple[str, str]]:
        return [
            ("position_no",    "position_no"),
            ("unit_qty",       "unit_qty"),
            ("total_price",    "total_price"),
            ("lead_time_days", "lead_time_days"),
            ("eom",            "eom"),
            ("eos",            "eos"),
        ]

    def generates_branded_spec(self) -> bool:
        return True
