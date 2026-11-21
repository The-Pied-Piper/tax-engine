"""Revenu Quebec TP-1 (2025) line 199, "Add lines 101 and 105 through 164. Total income", as the
Quebec take-home manifest part wires it: line 101, the salary, plus the income of lines 105 to
164.

Lines 105 to 164 are one optional input (`ca-qc/tp1_other_income_lines_105_to_164`), read as 0 when
the caller leaves it out, as T1 line 25700 is. The sum is `core/sum`, rounded half-up to the cent
by `ca-qc/cent_rounding`.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_OTHER_INCOME_LINES_105_TO_164,
    TP1_TOTAL_INCOME_LINE_199,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import SALARY_PARTS

D = Decimal

PARTS = (
    *SALARY_PARTS,
    "tp1_income_line_199_input.yaml",
    "tp1_income_line_199.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    """)
FORM = dedent("""\
    form:
      name: ca-qc/tp1_income
      required: true
      exports:
        - ca-qc/tp1_total_income_line_199
    """)


def tp1(take_home_service: TakeHomeService, salary: str, other: str | None = None) -> Worksheet:
    """The TP-1 income worksheet for a salary; lines 105 to 164 are left out unless `other`."""
    starting = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if other is not None:
        starting.append(Artifact(TP1_OTHER_INCOME_LINES_105_TO_164, D(other)))
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"), 2025, *starting
    )["ca-qc/tp1_income"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "20000.00"), ("70000", "70000.00"), ("200000", "200000.00"), ("0", "0.00")],
)
def test_a_salary_only_total_income_is_the_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = tp1(take_home_service, salary).get(TP1_TOTAL_INCOME_LINE_199).value

    assert str(value) == expected


def test_a_blank_lines_105_to_164_are_read_as_zero(take_home_service: TakeHomeService) -> None:
    assert tp1(take_home_service, "70000").get(TP1_TOTAL_INCOME_LINE_199).value == D("70000")


def test_lines_105_to_164_are_added_to_the_salary(take_home_service: TakeHomeService) -> None:
    value = tp1(take_home_service, "70000", "1234.56").get(TP1_TOTAL_INCOME_LINE_199).value

    assert str(value) == "71234.56"


def test_the_sum_is_rounded_half_up_to_the_cent(take_home_service: TakeHomeService) -> None:
    value = tp1(take_home_service, "70000", "0.005").get(TP1_TOTAL_INCOME_LINE_199).value

    assert str(value) == "70000.01"
