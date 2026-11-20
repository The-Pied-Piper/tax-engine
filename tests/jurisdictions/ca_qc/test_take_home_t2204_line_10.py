"""T2204 (2025) line 10 at the Quebec rate: the required EI premium on line 1.

T2204 line 10: "Amount from line 1 x rate = (maximum)", a contribution tier read from
`ca/ei_premium`; the Quebec manifest swaps it for `ca-qc/ei_premium` (1.31%, from $0 up to $65,700,
at most $860.67; 5005-R line 89 and 5005-S10 lines 18 to 20), so line 10 is the line 1 amount times
1.31% capped at the printed maximum. Which T2204 line prints the Quebec rate is a listed check on
the ticket. Line 1 is the salary here (no self-employment earnings, and 20,000 is not under the
$2,000 of note (1)). The figures are hand-computed from the printed forms, not a CRA example.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.jurisdictions.ca.catalog.refund import T2204_LINE_10
from tests.jurisdictions.ca_qc.test_take_home_t2204_line_4 import t2204

D = Decimal


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # 20,000 x 1.31% = 262.00.
        ("20000", "262.00"),
        # Above the $65,700 limit the premium is the printed maximum 860.67, not 1.31% of salary.
        ("70000", "860.67"),
        ("200000", "860.67"),
        # 1.31% of 65,700 is exactly the printed maximum, and just above it stays there.
        ("65700", "860.67"),
        ("65700.01", "860.67"),
    ],
)
def test_line_10_is_1_31_percent_of_line_1_up_to_the_maximum(
    take_home_service: TaxComputationService, salary: str, expected: str
) -> None:
    assert t2204(take_home_service, salary).get(T2204_LINE_10).value == D(expected)


def test_line_10_is_not_the_federal_premium(take_home_service: TaxComputationService) -> None:
    # The federal tier (1.64%) would give 328.00 on 20,000 and 1,077.48 on 70,000.
    assert t2204(take_home_service, "20000").get(T2204_LINE_10).value != D("328.00")
    assert t2204(take_home_service, "70000").get(T2204_LINE_10).value != D("1077.48")
