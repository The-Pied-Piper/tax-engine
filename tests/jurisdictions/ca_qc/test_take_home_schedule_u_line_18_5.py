"""Revenu Quebec Schedule U (2025, TP-1.D.U-V), line 18.5, as the Quebec take-home manifest part
wires it.

Schedule U line 18.5 "Pensionable salary or wages (QPP) (line 98.1 of your return)": the TP-1 line
98.1 figure, read from the TP-1 income form as a record list of one, so the one step is
`core/record_total`. The salary is the starting input; the figures are hand-computed from the
printed TP-1 lines, not an official example.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_U_LINE_18_5,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import TP1_INCOME_PARTS

D = Decimal

PARTS = (
    *TP1_INCOME_PARTS,
    "tp1_schedule_u_line_18_5.yaml",
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
        - ca-qc/schedule_u_line_18_5
    capabilities: []
    """)


def schedule_u(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The Schedule U worksheet for a salary."""
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-QC"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        ),
    )["ca-qc/tp1_schedule_u"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "20000.00"), ("70000", "70000.00"), ("200000", "81200.00")],
)
def test_line_18_5_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = schedule_u(take_home_service, salary).get(SCHEDULE_U_LINE_18_5).value

    assert str(value) == expected
