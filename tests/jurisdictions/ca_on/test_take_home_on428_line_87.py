"""ON428 (2025) line 87, the farmers' food donation credit, computed from the real part files
through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 87 and line 62150: Enter the amount of qualifying
donations that have also been claimed as a charitable donation. ^ / multiplied by 25% = ^". The
input is the qualifying donations (`ca-on/on428_qualifying_food_donations_line_87`), which the
inputs part declares as optional, read as 0 when left out. Line 87 is one calculation: 25% of the
donations, a printed rate held in the `ca-on/farmers_food_donation_rate` dataset, rounded half-up to
the cent. The output is `ca-on/on428_farmers_food_donation_credit_line_87`, read by line 88.

The inputs part and the line 87 part are both loaded from the take-home folder beside a header and a
form of their own, which the shared scaffold makes.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds

D = Decimal
CODE = JurisdictionCode("CA-ON")
DONATIONS = "ca-on/on428_qualifying_food_donations_line_87"
LINE_87 = "ca-on/on428_farmers_food_donation_credit_line_87"
INPUTS_PART = "on428_line_87_inputs.yaml"
PART = "on428_line_87.yaml"

HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: [ca-on/on428_qualifying_food_donations_line_87]
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_87}
capabilities: []
"""


def _line_87(take_home_service: TakeHomeService, donations: str | None) -> Decimal:
    kinds = bundled_kinds()
    given = [] if donations is None else [Artifact(kinds.kind(DONATIONS), D(donations))]
    worksheet = take_home_service(HEADER, FORM, INPUTS_PART, PART).compute(CODE, 2025, *given)[
        "ca-on/on428"
    ][0]
    value = worksheet.get(kinds.kind(LINE_87)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("donations", "credit"),
    [
        # Qualifying donations of 100.00: 25% of 100.00 is 25.00.
        ("100.00", "25.00"),
        # No donation (0): the credit is 0.
        ("0", "0.00"),
        # 0.02 x 25% = 0.005, a tie, rounded half-up to 0.01.
        ("0.02", "0.01"),
        # 10.10 x 25% = 2.525, a tie, rounded half-up to 2.53.
        ("10.10", "2.53"),
    ],
)
def test_line_87_is_25_percent_of_the_donations_rounded_half_up(
    take_home_service: TakeHomeService, donations: str, credit: str
) -> None:
    assert _line_87(take_home_service, donations) == D(credit)


def test_a_salary_only_caller_who_leaves_out_the_donations_gets_0(
    take_home_service: TakeHomeService,
) -> None:
    # The donations are left out, read as 0 by the inputs part, so the credit is 0.00.
    assert _line_87(take_home_service, None) == D("0.00")
