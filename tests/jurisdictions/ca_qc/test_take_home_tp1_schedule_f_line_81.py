"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part B, line 81, as the Quebec take-home
manifest wires it. Printed as "+ 81 0 00 | 150 00" under "Add lines 80 and 81".

Line 81 is `core/bracket_column_tax_at_start` over line 70 with `ca-qc/tp1_schedule_f_brackets`: the
printed constant of the column the amount falls in (0.00, or 150.00 above $63,060), blank for a
line 70 of $18,130 or less. Line 70 is given straight to the form, as line 76 receives it.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_SCHEDULE_F_COLUMN_CONSTANT_LINE_81,
    TP1_SCHEDULE_F_INCOME_SUBJECT_LINE_70,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal

PARTS = ("tp1_schedule_f_line_81.yaml",)

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
        - ca-qc/tp1_schedule_f_column_constant_line_81
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
        ("40000.00", "0.00"),
        ("63060.00", "0.00"),
        ("63060.01", "150.00"),
        ("100000.00", "150.00"),
        ("200000.00", "150.00"),
    ],
)
def test_line_81_for_a_line_70(
    take_home_service: TakeHomeService, line_70: str, expected: str
) -> None:
    value = part_b(take_home_service, line_70).get(TP1_SCHEDULE_F_COLUMN_CONSTANT_LINE_81).value

    assert str(value) == expected


@pytest.mark.parametrize("line_70", ["-500.00", "0.00", "18130.00"])
def test_line_81_is_blank_for_a_line_70_of_18130_or_less(
    take_home_service: TakeHomeService, line_70: str
) -> None:
    assert part_b(take_home_service, line_70).get(TP1_SCHEDULE_F_COLUMN_CONSTANT_LINE_81).is_blank
