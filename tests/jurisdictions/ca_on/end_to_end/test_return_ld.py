"""CA-ON 2025 end to end: return ld (Guide T4002's Jennifer, "Personal use of property").

Guide T4002 (2025): "She bought a car in 2025 ... The car cost $20,000 ... she includes the car in
Class 10. ... She enters $20,000 in column 3 and column 5 of Area B. She also enters $20,000 in
column 3 of Area A. By completing the other columns in the chart, she calculates a CCA claim of
$3,000. ... 12,000 (business kilometres) ÷ 18,000 (total kilometres) × $3,000 = $2,000. Jennifer
enters $2,000 on line 9936."

The worked return `returns/2025_return_ld.yaml` (checked by `test_worked_returns.py`) pins the
$3,000 claim and the $2,000 on line 9936. A car bought in 2025 is a RIIP (Area A column 12,
$20,000), so the most the form allows is $9,000 (column 17: $20,000 x 1/2; column 19: $20,000 +
$10,000; $30,000 x 30%); the guide's $3,000 is the half-year rule's maximum ($20,000 x 50% x 30%)
and is a claim below the form's maximum. This module reads the claim, and the most each reading
allows.
"""

from __future__ import annotations

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    BUSINESS_CCA_CLAIM,
    BUSINESS_CCA_TABLE_CLAIM,
    BUSINESS_CLOSING_UCC,
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run


def jennifer(riip: str, claimed: str) -> dict[str, tuple[Worksheet, ...]]:
    """Jennifer's class 10 row: the car's $20,000 in column 3, `riip` in column 12, `claimed`."""
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_part_4_completed=1,
        business_statements=(
            {
                "business": {"gross_sales": "20000", "cca_personal_part": "1000"},
                "business_cca_classes_rows": (
                    ("10", "0", "20000", "0", "0", riip, claimed, 0, "0", "0", "0"),
                ),
            },
        ),
    )


def test_jennifers_claim_of_3000_less_the_personal_third_is_2000_on_line_9936() -> None:
    # 12000 / 18000 x 3000 = 2000 business part: the personal part of 1000 comes off the claim.
    worksheet = jennifer("20000", "3000")["ca/t2125"][0]

    assert worksheet.get(BUSINESS_CCA_TABLE_CLAIM).value == D("3000")
    assert worksheet.get(BUSINESS_CCA_CLAIM).value == D("2000")
    (closing,) = worksheet.get(BUSINESS_CLOSING_UCC).value.records
    assert closing[CCA_CLASS_NUMBER] == D("10")
    assert closing[CCA_UCC_AT_END] == D("17000")


def test_the_car_bought_in_2025_is_a_riip_so_the_maximum_claim_is_9000() -> None:
    assert jennifer("20000", "9000")["ca/t2125"][0].get(BUSINESS_CCA_TABLE_CLAIM).value == D("9000")
    with pytest.raises(InputAboveBoundError, match="above the maximum 9000.00"):
        jennifer("20000", "9000.01")


def test_with_no_riip_the_half_year_rule_gives_the_guides_3000_as_the_maximum() -> None:
    assert jennifer("0", "3000")["ca/t2125"][0].get(BUSINESS_CCA_TABLE_CLAIM).value == D("3000")
    with pytest.raises(InputAboveBoundError, match="above the maximum 3000.00"):
        jennifer("0", "3000.01")
