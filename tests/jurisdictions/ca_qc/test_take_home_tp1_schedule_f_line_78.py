"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part B, line 78, as the Quebec take-home
manifest wires it. Printed as "Subtract line 77 from line 76. If the result is negative, enter 0".

Line 76 is a copy of line 70 and has no step. Line 78 is `core/subtract_not_below_zero` of line 77
from line 70, rounded half-up to the cent. It is blank when line 77 is blank (a line 70 of $18,130
or less). Line 70 is given straight to the form, as line 76 receives it.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_SCHEDULE_F_INCOME_OVER_LOWER_BOUND_LINE_78,
    TP1_SCHEDULE_F_INCOME_SUBJECT_LINE_70,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal

PARTS = ("tp1_schedule_f_line_77.yaml", "tp1_schedule_f_line_78.yaml")

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca-qc/tp1_schedule_f_income_subject_line_70
        required: true
    outputs:
      - ca-qc/tp1_schedule_f_income_subject_line_70
    """)
FORM = dedent("""\
    form:
      name: ca-qc/tp1_schedule_f
      required: true
      exports:
        - ca-qc/tp1_schedule_f_income_over_lower_bound_line_78
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
    ("line_70", "line_78"),
    [
        ("18130.01", "0.01"),
        ("40000.00", "21870.00"),
        ("63060.00", "44930.00"),
        ("63060.01", "0.01"),
        ("100000.00", "36940.00"),
        ("200000.00", "136940.00"),
    ],
)
def test_line_78_is_line_76_less_the_columns_lower_bound(
    take_home_service: TakeHomeService, line_70: str, line_78: str
) -> None:
    value = (
        part_b(take_home_service, line_70).get(TP1_SCHEDULE_F_INCOME_OVER_LOWER_BOUND_LINE_78).value
    )

    assert str(value) == line_78


@pytest.mark.parametrize("line_70", ["-500.00", "0.00", "18130.00"])
def test_line_78_is_blank_for_a_line_70_of_18130_or_less(
    take_home_service: TakeHomeService, line_70: str
) -> None:
    sheet = part_b(take_home_service, line_70)

    assert sheet.get(TP1_SCHEDULE_F_INCOME_OVER_LOWER_BOUND_LINE_78).is_blank
