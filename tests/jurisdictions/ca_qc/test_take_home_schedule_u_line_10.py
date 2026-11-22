"""Revenu Quebec Schedule U (2025, TP-1.D.U-V), line 10, as the Quebec take-home manifest part wires
it.

Schedule U line 10 "QPP contribution (line 98 of your return)": the TP-1 line 98 figure, read from
the TP-1 income form as a record list of one, so the one step is `core/record_total`. The salary
is the starting input; the figures are hand-computed from the printed TP-1 lines, not an official
example.
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
    SCHEDULE_U_LINE_10,
    TP1_QPP_CONTRIBUTION_GIVEN_LINE_98,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import TP1_INCOME_PARTS

D = Decimal

PARTS = (
    *TP1_INCOME_PARTS,
    "tp1_schedule_u_line_10_base.yaml",
    "tp1_schedule_u_line_10.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-qc/tp1_schedule_u
      required: true
      exports:
        - ca-qc/schedule_u_line_10
    capabilities: []
    """)


def schedule_u(take_home_service: TakeHomeService, salary: str, line_98: str = "") -> Worksheet:
    """The Schedule U worksheet for a salary, with line 98 given when `line_98` is not empty."""
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"),
        2025,
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        *([Artifact(TP1_QPP_CONTRIBUTION_GIVEN_LINE_98, D(line_98))] if line_98 else []),
    )["ca-qc/tp1_schedule_u"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "1056.00"), ("70000", "4256.00"), ("200000", "4339.20")],
)
def test_line_10_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = schedule_u(take_home_service, salary).get(SCHEDULE_U_LINE_10).value

    assert str(value) == expected


@pytest.mark.parametrize(
    ("line_98", "expected"),
    [("4339.20", "4339.20"), ("4339.21", "4339.20"), ("5000", "4339.20"), ("1000", "1000.00")],
)
def test_line_10_stops_at_the_printed_maximum_for_a_given_line_98(
    take_home_service: TakeHomeService, line_98: str, expected: str
) -> None:
    value = schedule_u(take_home_service, "70000", line_98).get(SCHEDULE_U_LINE_10).value

    assert str(value) == expected
