"""T2204 (2025) line 4, the total premiums deducted, as the Ontario take-home manifest part wires
it: the amount given when the filer has it, else computed from line 1 at the EI rate.

T2204 line 4: "Total premiums deducted: Residents of other than Quebec (box 18 and box 55 of your
T4 slips)". The caller has no T4, so the input `ca/t2204_premiums_deducted_given` is optional: a
request that gives it has that figure as line 4, unchanged; a request that leaves it out has line
4 computed by `ca/given_or_contribution_tier` from line 1 with the `ca/ei_premium` dataset (1.64%,
at most $1,077.48), the same as line 10 of the form.

The real line 1 part and the line 4 part are loaded under test-local headers, as the take-home
header is another part's. The line 1 part is the real one; the $2,000 of line 7
(`ca/t2204_exemption`) is produced by another part, so the header declares it as a
required starting input.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.refund import (
    T2204_EXEMPTION,
    T2204_PREMIUMS_DEDUCTED,
    T2204_PREMIUMS_DEDUCTED_GIVEN,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal

LINE_1_PART = "t2204_line_1.yaml"
LINE_4_PART = "t2204_line_4.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
      - name: ca/t2204_exemption
        required: true
      - name: ca/t2204_self_employment_earnings
        required: false
        default: null
        basis: "Total self-employment and other earnings eligible for the EI program
          for access to EI special benefits"
      - name: ca/t2204_premiums_deducted_given
        required: false
        default: null
        basis: "Total premiums deducted: Residents of other than Quebec (box 18 and box 55
          of your T4 slips)"
    outputs:
      - ca/employment_income
    """)
FORM = dedent("""\
    form:
      name: ca/t2204
      required: true
      exports:
        - ca/t2204_premiums_deducted
    """)


def t2204(take_home_service: TakeHomeService, salary: str, given: str | None = None) -> Worksheet:
    """The T2204 worksheet for a salary; line 4 is left out unless `given` is passed."""
    starting = [
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        Artifact(T2204_EXEMPTION, D("2000.00")),
    ]
    if given is not None:
        starting.append(Artifact(T2204_PREMIUMS_DEDUCTED_GIVEN, D(given)))
    (sheet,) = take_home_service(HEADER, FORM, LINE_1_PART, LINE_4_PART).compute(
        JurisdictionCode("CA-ON"), 2025, *starting
    )["ca/t2204"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # 70,000: line 1 is 70,000; 1.64% is 1,148.00, capped at the printed maximum 1,077.48.
        ("70000", "1077.48"),
        # 2,010: line 1 is 2,010 (not under $2,000); 1.64% of 2,010 is 32.964, half-up 32.96.
        ("2010", "32.96"),
        # 30,000: 1.64% of 30,000 is 492.00, under the maximum.
        ("30000", "492.00"),
        # 1,500: line 1 is "0" under note (1), so line 4 is 0.
        ("1500", "0"),
    ],
)
def test_a_blank_line_4_is_the_ei_premium_on_line_1(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert t2204(take_home_service, salary).get(T2204_PREMIUMS_DEDUCTED).value == D(expected)


def test_a_blank_line_4_is_computed_to_the_cent(take_home_service: TakeHomeService) -> None:
    assert str(t2204(take_home_service, "70000").get(T2204_PREMIUMS_DEDUCTED).value) == "1077.48"


@pytest.mark.parametrize("given", ["1148.00", "0", "2500.00"])
def test_a_given_line_4_is_the_output_unchanged(
    take_home_service: TakeHomeService, given: str
) -> None:
    assert str(t2204(take_home_service, "70000", given).get(T2204_PREMIUMS_DEDUCTED).value) == given


def test_a_given_line_4_is_not_computed_from_line_1(take_home_service: TakeHomeService) -> None:
    # Line 1 would be 2,010 and the EI premium 32.96; the given figure is line 4 as it is.
    assert (
        str(t2204(take_home_service, "2010", "1148.00").get(T2204_PREMIUMS_DEDUCTED).value)
        == "1148.00"
    )
