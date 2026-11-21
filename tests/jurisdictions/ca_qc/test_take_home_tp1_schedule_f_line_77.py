"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part B, line 77, as the Quebec take-home
manifest wires it. Printed as "Enter the amount from line 70 above in the appropriate column", then
line 77 "18,130 00 | 63,060 00" under "If $63,060 or less | If more than $63,060".

Line 76 is a copy of line 70 and has no step. Line 77 is one `core/bracket_column_lower_bound` step
over line 70 with `ca-qc/tp1_schedule_f_brackets`: the printed lower bound of the column the amount
falls in, and blank for a line 70 of $18,130 or less, which owes nothing. The parts composed are
the part under test only; line 70 is given straight to the form, as line 76 receives it.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_SCHEDULE_F_INCOME_SUBJECT_LINE_70,
    TP1_SCHEDULE_F_LOWER_BOUND_LINE_77,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal

PARTS = ("tp1_schedule_f_line_77.yaml",)

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
        - ca-qc/tp1_schedule_f_lower_bound_line_77
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
    ("line_70", "line_77"),
    [
        ("18130.01", "18130.00"),
        ("40000.00", "18130.00"),
        ("63060.00", "18130.00"),
        ("63060.01", "63060.00"),
        ("100000.00", "63060.00"),
    ],
)
def test_line_77_is_the_printed_lower_bound_of_the_column(
    take_home_service: TakeHomeService, line_70: str, line_77: str
) -> None:
    value = part_b(take_home_service, line_70).get(TP1_SCHEDULE_F_LOWER_BOUND_LINE_77).value

    assert str(value) == line_77


@pytest.mark.parametrize("line_70", ["-500.00", "0.00", "18130.00"])
def test_line_77_is_blank_for_a_line_70_of_18130_or_less(
    take_home_service: TakeHomeService, line_70: str
) -> None:
    assert part_b(take_home_service, line_70).get(TP1_SCHEDULE_F_LOWER_BOUND_LINE_77).is_blank
