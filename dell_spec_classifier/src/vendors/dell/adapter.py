from src.vendors.base import VendorAdapter
from src.core.parser import parse_excel, find_header_row
from src.core.normalizer import normalize_row


class DellAdapter(VendorAdapter):
    def __init__(self, config: dict = None):
        self._config = config or {}

    def parse(self, filepath: str):
        raw_rows = parse_excel(filepath)
        header_row_index = find_header_row(filepath)
        return (raw_rows, header_row_index)

    def normalize(self, raw_rows):
        return [normalize_row(r) for r in raw_rows]

    def get_rules_file(self):
        vendor_rules = self._config.get("vendor_rules", {})
        return vendor_rules.get("dell", self._config.get("rules_file", "rules/dell_rules.yaml"))
