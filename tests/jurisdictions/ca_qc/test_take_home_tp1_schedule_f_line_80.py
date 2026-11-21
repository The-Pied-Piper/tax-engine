"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part B, line 80, as the Quebec take-home
manifest wires it. Printed as "Multiply line 78 by 1%".

Line 80 is `core/multiply_by_rate` of line 78 by the column's rate, rounded half-up to the cent.
It is blank for a line 70 of $18,130 or less. Line 70 is given straight to the form, as line 76
receives it.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_SCHEDULE_F_CONTRIBUTION_ON_EXCESS_LINE_80,
    TP1_SCHEDULE_F_INCOME_SUBJECT_LINE_70,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal

PARTS = (
    "tp1_schedule_f_line_77.yaml",
    "tp1_schedule_f_line_78.yaml",
    "tp1_schedule_f_column_rate.yaml",
    "tp1_schedule_f_line_80.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    """)
FORM = dedent("""\
    form:
      name: ca-qc/tp1_schedule_f
      required: true
      exports:
        - ca-qc/tp1_schedule_f_contribution_on_excess_line_80
    inputs:
      - name: ca-qc/tp1_schedule_f_income_subject_line_70
        required: true
    """)


def part_b(take_home_service: TakeHomeService, line_70: str) -> Worksheet:
    """The Schedule F worksheet for a line 70 given straight to Part B."""
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"),
        2025,
        Artifact(TP1_SCHEDULE_F_INCOME_SUBJECT_LINE_70, D(line_70)),
    )["ca-qc/tp1_schedule_f"]
    return sheet


@pytest.mark.parametrize(
    ("line_70", "expected"),
    [
        ("18130.01", "0.00"),
        ("40000.00", "218.70"),
        ("63060.00", "449.30"),
        ("63060.01", "0.00"),
        ("100000.00", "369.40"),
        ("200000.00", "1369.40"),
    ],
)
def test_line_80_for_a_line_70(
    take_home_service: TakeHomeService, line_70: str, expected: str
) -> None:
    value = (
        part_b(take_home_service, line_70).get(TP1_SCHEDULE_F_CONTRIBUTION_ON_EXCESS_LINE_80).value
    )

    assert str(value) == expected


@pytest.mark.parametrize("line_70", ["-500.00", "0.00", "18130.00"])
def test_line_80_is_blank_for_a_line_70_of_18130_or_less(
    take_home_service: TakeHomeService, line_70: str
) -> None:
    assert (
        part_b(take_home_service, line_70)
        .get(TP1_SCHEDULE_F_CONTRIBUTION_ON_EXCESS_LINE_80)
        .is_blank
    )
