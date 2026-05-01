import openpyxl
from src.vendors.base import VendorAdapter


class XFusionAdapter(VendorAdapter):
    """
    Phase 0 STUB — only `can_parse` is implemented.
    Full implementation lands in Phase 1 (parser/normalizer/registry).
    """

    def __init__(self, config: dict = None):
        self._config = config or {}

    def can_parse(self, path: str) -> bool:
        """
        Positive signature for xFusion FusionServer eDeal export.

        Two-branch discriminator (mutually exclusive with Huawei — see
        VENDOR_FORMAT_SPEC.md (xfusion) §3.2):
          Branch A (Excel Desktop, formula evaluated): cached R8C8 contains
            "USD" but neither "FOB" nor "HONG KONG" -> xFusion
            (QF_SYS_TRADETERMDESC1 is empty in xFusion eDeal templates).
          Branch B (Excel Online, formula unevaluated): cached R8C8 empty AND
            sidecar sheet "Main Equipment Statistic" is PRESENT -> xFusion.

        Note: data_only=True is required — the price-header cell stores a
        formula that resolves differently for Huawei vs xFusion based on the
        injected default for the QF_SYS_TRADETERMDESC1 named range.
        """
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        try:
            if "AllInOne" not in wb.sheetnames:
                return False
            ws = wb["AllInOne"]
            rows = list(ws.iter_rows(min_row=1, max_row=9, values_only=True))
            if len(rows) < 9:
                return False
            r0, r8 = rows[0], rows[8]
            if len(r0) < 3 or r0[2] is None or str(r0[2]).strip() != "COL_SORTNO.0":
                return False
            r8c8 = str(r8[8]).strip() if len(r8) > 8 and r8[8] is not None else ""
            # Branch A: cached header is bare USD (xFusion convention)
            if r8c8 and "FOB" not in r8c8.upper() and "HONG KONG" not in r8c8.upper():
                return True
            # Branch B: hidden prices — sidecar sheet is xFusion-only
            if not r8c8 and "Main Equipment Statistic" in wb.sheetnames:
                return True
            return False
        finally:
            wb.close()

    def parse(self, filepath: str):
        raise NotImplementedError(
            "XFusionAdapter.parse — Phase 1 (xfusion/parser.py not yet created)"
        )

    def normalize(self, raw_rows):
        raise NotImplementedError(
            "XFusionAdapter.normalize — Phase 1 (xfusion/normalizer.py not yet created)"
        )

    def get_rules_file(self):
        raise NotImplementedError(
            "XFusionAdapter.get_rules_file — Phase 1.4 (rules/xfusion_rules.yaml not yet created)"
        )

    def generates_branded_spec(self) -> bool:
        raise NotImplementedError("XFusionAdapter.generates_branded_spec — Phase 1")

    def get_vendor_stats(self, normalized_rows: list) -> dict:
        raise NotImplementedError("XFusionAdapter.get_vendor_stats — Phase 2")
