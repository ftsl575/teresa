from src.vendors.base import VendorAdapter
from src.vendors.cisco.parser import parse_excel
from src.vendors.cisco.normalizer import normalize_cisco_rows


class CiscoAdapter(VendorAdapter):
    def __init__(self, config: dict = None):
        self._config = config or {}

    def parse(self, filepath: str):
        return parse_excel(filepath)

    def normalize(self, raw_rows):
        return normalize_cisco_rows(raw_rows)

    def get_rules_file(self):
        vendor_rules = self._config.get("vendor_rules", {})
        return vendor_rules.get("cisco", "rules/cisco_rules.yaml")
