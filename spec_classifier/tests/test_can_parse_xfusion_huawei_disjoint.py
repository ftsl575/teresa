import pytest
from src.vendors.xfusion.adapter import XFusionAdapter
from src.vendors.huawei.adapter import HuaweiAdapter
from conftest import get_input_root_xfusion, get_input_root_huawei


@pytest.mark.parametrize(
    "filename,expected_vendor",
    [
        *((f"xf{i}.xlsx", "xfusion") for i in range(1, 11)),
        *((f"hu{i}.xlsx", "huawei") for i in range(1, 6)),
    ],
)
def test_can_parse_disjoint(filename, expected_vendor):
    """
    P0 invariant: every fixture must be claimed by EXACTLY ONE adapter
    in {xfusion, huawei} — never both, never neither.

    Verified empirically over 15 fixtures (5 hu + 10 xf) — see
    VENDOR_FORMAT_SPEC.md (xfusion) §3.5.
    """
    src_root = get_input_root_xfusion() if expected_vendor == "xfusion" else get_input_root_huawei()
    src = src_root / filename
    if not src.exists():
        pytest.skip(f"fixture missing: {src}")
    xf = XFusionAdapter().can_parse(str(src))
    hu = HuaweiAdapter().can_parse(str(src))
    expected = (True, False) if expected_vendor == "xfusion" else (False, True)
    assert (xf, hu) == expected, (
        f"{filename}: xf={xf} hu={hu} (expected vendor {expected_vendor})"
    )
