"""T2204 (2025) line 4 at the Quebec rate: the total premiums deducted, computed from the salary.

T2204 line 4 (the shared form, titled "Residents of other than Quebec"): "Total premiums deducted:
... (box 18 and box 55 of your T4 slips)". The take-home caller has no T4, so a blank line 4 is the
EI premium on line 1 by `ca/given_or_contribution_tier` reading `ca/ei_premium`. The Quebec manifest
swaps that dataset for `ca-qc/ei_premium` (1.31%, at most $860.67; 5005-R line 89 and 5005-S10
lines 18 to 20), so a Quebec salary gets the Quebec premium. Which T2204 line prints the Quebec rate
is a listed check on the ticket. The figures are hand-computed from the printed forms, not a CRA
example: 20,000 x 1.31% = 262.00; 70,000 and 200,000 are above $65,700, so the printed maximum.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.refund import (
    T2204_PREMIUMS_DEDUCTED,
    T2204_PREMIUMS_DEDUCTED_GIVEN,
)

D = Decimal


def t2204(service: TaxComputationService, salary: str, given: str | None = None) -> Worksheet:
    """The Quebec T2204 worksheet for a salary; line 4 is left blank unless `given` is passed."""
    starting = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if given is not None:
        starting.append(Artifact(T2204_PREMIUMS_DEDUCTED_GIVEN, D(given)))
    (sheet,) = service.compute(JurisdictionCode("CA-QC"), 2025, *starting)["ca/t2204"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "262.00"), ("70000", "860.67"), ("200000", "860.67")],
)
def test_a_blank_line_4_is_the_quebec_ei_premium_on_the_salary(
    take_home_service: TaxComputationService, salary: str, expected: str
) -> None:
    assert t2204(take_home_service, salary).get(T2204_PREMIUMS_DEDUCTED).value == D(expected)


def test_a_given_line_4_is_the_output_unchanged(take_home_service: TaxComputationService) -> None:
    # 70,000 would give 860.67; the figure typed from the T4 is line 4 as it is.
    assert (
        str(t2204(take_home_service, "70000", "900.00").get(T2204_PREMIUMS_DEDUCTED).value)
        == "900.00"
    )
