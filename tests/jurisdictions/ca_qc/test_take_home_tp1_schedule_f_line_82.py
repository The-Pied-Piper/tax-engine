"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part B, line 82, as the Quebec take-home
manifest wires it. Printed as "Add lines 80 and 81", with "Maximum: $150 | Maximum: $1,000" and
"Carry the result to line 446 of your return. Contribution to the health services fund".

Line 82 is three steps: `core/sum` of lines 80 and 81 (a blank read as 0), `core/amount_by_band`
over line 77 for the printed maximum of the column, and `core/lesser_of` of the two, which carries
the reference. A line 70 of $18,130 or less leaves Part B blank and line 82 is 0.00. Line 70 is
given straight to the form, as line 76 receives it; the last tests run the whole Schedule F from a
salary.
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
    TP1_FOREST_PRODUCER_AVERAGING_LINE_276,
    TP1_SCHEDULE_F_CONTRIBUTION_LINE_82,
    TP1_SCHEDULE_F_INCOME_SUBJECT_LINE_70,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal

PARTS = (
    "tp1_schedule_f_line_77.yaml",
    "tp1_schedule_f_line_78.yaml",
    "tp1_schedule_f_column_rate.yaml",
    "tp1_schedule_f_line_80.yaml",
    "tp1_schedule_f_line_81.yaml",
    "tp1_schedule_f_line_82.yaml",
)

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
        - ca-qc/tp1_schedule_f_contribution_line_82
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
        ("20000.00", "18.70"),
        ("40000.00", "150.00"),
        ("63060.00", "150.00"),
        ("63060.01", "150.00"),
        ("100000.00", "519.40"),
        ("200000.00", "1000.00"),
    ],
)
def test_line_82_for_a_line_70(
    take_home_service: TakeHomeService, line_70: str, expected: str
) -> None:
    value = part_b(take_home_service, line_70).get(TP1_SCHEDULE_F_CONTRIBUTION_LINE_82).value

    assert str(value) == expected


@pytest.mark.parametrize("line_70", ["-500.00", "0.00", "18130.00"])
def test_line_82_is_zero_for_a_line_70_of_18130_or_less(
    take_home_service: TakeHomeService, line_70: str
) -> None:
    value = part_b(take_home_service, line_70).get(TP1_SCHEDULE_F_CONTRIBUTION_LINE_82).value

    assert str(value) == "0.00"


SCHEDULE_F_PARTS = (
    "salary.yaml",
    "tp1_income.yaml",
    "tp1_income_line_105_input.yaml",
    "tp1_income_line_107_input.yaml",
    "tp1_income_line_box_211_input.yaml",
    "tp1_income_line_199_input.yaml",
    "tp1_income_line_199.yaml",
    "tp1_income_line_97_input.yaml",
    "tp1_income_line_97.yaml",
    "tp1_income_line_98_input.yaml",
    "tp1_income_line_98.yaml",
    "tp1_income_line_98_1_input.yaml",
    "tp1_income_line_98_1.yaml",
    "tp1_income_line_98_2_input.yaml",
    "tp1_income_line_98_2.yaml",
    "tp1_schedule_f_line_10_input.yaml",
    "tp1_schedule_f_line_10.yaml",
    "tp1_schedule_f_line_12.yaml",
    "tp1_schedule_f_line_14_input.yaml",
    "tp1_schedule_f_line_16.yaml",
    "tp1_schedule_f_line_18.yaml",
    "tp1_schedule_f_line_34_inputs.yaml",
    "tp1_schedule_f_line_25_inputs.yaml",
    "tp1_schedule_f_line_25.yaml",
    "tp1_schedule_f_line_34.yaml",
    "tp1_schedule_f_line_36.yaml",
    "tp1_schedule_f_line_68_inputs.yaml",
    "tp1_schedule_f_line_68.yaml",
    "tp1_schedule_f_line_70.yaml",
    *PARTS,
)
SALARY_HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    """)
SALARY_FORM = dedent("""\
    form:
      name: ca-qc/tp1_schedule_f
      required: true
      exports:
        - ca-qc/tp1_schedule_f_contribution_line_82
    """)


def from_salary(
    take_home_service: TakeHomeService, salary: str, forest_averaging: str | None = None
) -> Worksheet:
    """The whole Schedule F worksheet for a salary, with the optional line 276 amount if given."""
    starting = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if forest_averaging is not None:
        starting.append(Artifact(TP1_FOREST_PRODUCER_AVERAGING_LINE_276, D(forest_averaging)))
    (sheet,) = take_home_service(SALARY_HEADER, SALARY_FORM, *SCHEDULE_F_PARTS).compute(
        JurisdictionCode("CA-QC"), 2025, *starting
    )["ca-qc/tp1_schedule_f"]
    return sheet


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_salary_only_line_82_is_zero(take_home_service: TakeHomeService, salary: str) -> None:
    value = from_salary(take_home_service, salary).get(TP1_SCHEDULE_F_CONTRIBUTION_LINE_82).value

    assert str(value) == "0.00"


@pytest.mark.parametrize(
    ("forest_averaging", "line_82"),
    [("18130.00", "0.00"), ("18130.01", "0.00"), ("30000.00", "118.70"), ("100000.00", "519.40")],
)
def test_the_whole_schedule_carries_line_82_from_a_salary(
    take_home_service: TakeHomeService, forest_averaging: str, line_82: str
) -> None:
    sheet = from_salary(take_home_service, "70000", forest_averaging)

    assert str(sheet.get(TP1_SCHEDULE_F_CONTRIBUTION_LINE_82).value) == line_82
