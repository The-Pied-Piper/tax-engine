"""T2204 (2025) line 16 at the Quebec rate: the premium that stays, and 5005-R line 89.

T2204 line 16: "Enter whichever amount is the least: line 7, line 9 or line 12", the least of
line 7 (line 3 less $2,000), line 4 (premiums deducted) and line 10 (required premium). With the
salary alone, line 4 is the Quebec premium and so is line 10, and line 7 is the salary less $2,000,
so line 16 is the Quebec premium at $20,000 and the printed maximum $860.67 above $65,700.
5005-R line 89 (31200) copies line 16, and the take-home return exports `ca/t2204_line_16` for it
(ticket R6). The alone-and-tenant answers are not read by these lines. The figures are
hand-computed from the printed forms, not a CRA example.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.jurisdictions.ca.catalog.refund import T2204_LINE_16
from tests.jurisdictions.ca_qc.test_take_home_t2204_line_4 import t2204

D = Decimal


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "262.00"), ("70000", "860.67"), ("200000", "860.67")],
)
def test_line_16_is_the_quebec_premium_on_the_salary(
    take_home_service: TaxComputationService, salary: str, expected: str
) -> None:
    assert t2204(take_home_service, salary).get(T2204_LINE_16).value == D(expected)


@pytest.mark.parametrize("salary", ["70000", "200000"])
def test_line_16_above_the_limit_is_the_printed_maximum(
    take_home_service: TaxComputationService, salary: str
) -> None:
    assert str(t2204(take_home_service, salary).get(T2204_LINE_16).value) == "860.67"


def test_line_16_at_20000_is_1_31_percent_of_the_salary(
    take_home_service: TaxComputationService,
) -> None:
    assert t2204(take_home_service, "20000").get(T2204_LINE_16).value == D("20000") * D("0.0131")
