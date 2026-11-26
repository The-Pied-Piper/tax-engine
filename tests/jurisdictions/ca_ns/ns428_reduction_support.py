"""What the NS428 low-income reduction line tests (lines 65 to 85, 2025) share: the kind
identifiers of the lines, the figures the form arithmetic gives for a salary-only filer, and helpers
over the composed real parts (see `ns428_tax_support`).

Form NS428 (CRA 5003-C): adjusted family income is line 70 (line 69 while the spouse column is
deferred, #1999); the basic reduction is $300 less 5% of the income over $15,000, so it is gone at
$21,000. Salary-only figures are hand-derived from the form's arithmetic and equal the ticket's.
"""

from __future__ import annotations

from decimal import Decimal
from itertools import count
from pathlib import Path
from typing import Any

from tests.jurisdictions.ca_ns import ns428_tax_support as s
from tests.jurisdictions.ca_ns.support import nova_scotia_kinds

D = Decimal
LINE_65 = "ca-ns/ns428_net_income_line_65"
LINE_66_A = "ca-ns/ns428_uccb_repayment_line_21300"
LINE_66_B = "ca-ns/ns428_rdsp_income_repayment_line_23200"
LINE_66 = "ca-ns/ns428_uccb_rdsp_repayments_line_66"
LINE_67 = "ca-ns/ns428_family_income_line_67"
LINE_68_A = "ca-ns/ns428_uccb_income_line_11700"
LINE_68_B = "ca-ns/ns428_rdsp_income_line_12500"
LINE_68 = "ca-ns/ns428_uccb_rdsp_income_line_68"
LINE_69 = "ca-ns/ns428_family_income_less_uccb_rdsp_line_69"
LINE_71 = "ca-ns/low_income_reduction_basic"
LINE_74 = "ca-ns/ns428_low_income_reduction_line_74"
LINE_80 = "ca-ns/low_income_reduction_base_amount"
LINE_81 = "ca-ns/ns428_line_81"
LINE_83 = "ca-ns/ns428_line_83"
LINE_84 = "ca-ns/ns428_low_income_reduction_line_84"
LINE_85 = "ca-ns/ns428_tax_line_85"
LINE_64 = s.LINE_64
_RUNS = count()
INPUTS = {
    "uccb_repayment": "ca/uccb_repayment",
    "rdsp_income_repayment": "ca/rdsp_income_repayment",
    "uccb_income": "ca/uccb_income",
    "rdsp_income": "ca/rdsp_income",
}

# (salary, line 69 = adjusted family income, line 81, line 83, line 84, line 85): the ticket's
# figures.
CASES = [
    ("20000", "19835.00", "4835.00", "241.75", "58.25", "552.33"),
    ("30000", "29735.00", "14735.00", "736.75", "0.00", "1422.86"),
    ("70000", "69335.00", "54335.00", "2716.75", "0.00", "7213.10"),
]
# Boundaries: a salary whose adjusted family income is exactly 15,000.00 (reduction 300.00) and
# exactly 21,000.00 (reduction 0.00).
AT_BASE = ("15116.16", "15000.00", "0.00", "0.00", "300.00")
AT_GONE = ("21176.77", "21000.00", "6000.00", "300.00", "0.00")


def line(
    tmp_path: Path, salary: str, identifier: str, given: dict[str, str] | None = None
) -> Decimal:
    """The figure of the kind `identifier` on the form's sheet for `salary`. Each call composes in
    a folder of its own, so a test may read several figures."""
    return s.line(tmp_path / f"run{next(_RUNS)}", salary, identifier, given)


def part(name: str) -> dict[str, Any]:
    return s.part(name)


def kinds() -> Any:
    return nova_scotia_kinds()
