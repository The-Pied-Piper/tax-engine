"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part B, the row "x 1%" below line 78, as the
Quebec take-home manifest wires it. The row has no line number and prints 1% in each column.

The row is one `core/bracket_column_rate` step over line 70 with `ca-qc/tp1_schedule_f_brackets`:
the printed rate of the column the amount falls in, blank for a line 70 of $18,130 or less. Line 70
is given straight to the form, as line 76 receives it.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_SCHEDULE_F_COLUMN_RATE,
    TP1_SCHEDULE_F_INCOME_SUBJECT_LINE_70,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal

PARTS = ("tp1_schedule_f_column_rate.yaml",)

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
        - ca-qc/tp1_schedule_f_column_rate
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
        ("18130.01", "0.01"),
        ("40000.00", "0.01"),
        ("63060.00", "0.01"),
        ("63060.01", "0.01"),
        ("200000.00", "0.01"),
    ],
)
def test_the_column_rate_for_a_line_70(
    take_home_service: TakeHomeService, line_70: str, expected: str
) -> None:
    value = part_b(take_home_service, line_70).get(TP1_SCHEDULE_F_COLUMN_RATE).value

    assert str(value) == expected


@pytest.mark.parametrize("line_70", ["-500.00", "0.00", "18130.00"])
def test_the_column_rate_is_blank_for_a_line_70_of_18130_or_less(
    take_home_service: TakeHomeService, line_70: str
) -> None:
    assert part_b(take_home_service, line_70).get(TP1_SCHEDULE_F_COLUMN_RATE).is_blank
