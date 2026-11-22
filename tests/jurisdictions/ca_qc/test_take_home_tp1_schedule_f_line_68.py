"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part A, line 68, "Add lines 41 through 62.
Deductions", as the Quebec take-home manifest wires it.

One `core/sum` over the printed lines 41, 42, 43, 43.1, 44, 45, 46, 54, 56, 58, 60 and 62, rounded
half-up to the cent by `ca-qc/cent_rounding`. The printed lines are optional inputs, read as 0 when
left out. The expected figures are hand-computed from the printed lines.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
import yaml

import tax_engine.jurisdictions.ca_qc
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_SCHEDULE_F_DEDUCTIONS_LINE_68,
    TP1_SCHEDULE_F_LINE_41,
    TP1_SCHEDULE_F_LINE_42,
    TP1_SCHEDULE_F_LINE_43,
    TP1_SCHEDULE_F_LINE_43_1,
    TP1_SCHEDULE_F_LINE_44,
    TP1_SCHEDULE_F_LINE_45,
    TP1_SCHEDULE_F_LINE_46,
    TP1_SCHEDULE_F_LINE_54,
    TP1_SCHEDULE_F_LINE_56,
    TP1_SCHEDULE_F_LINE_58,
    TP1_SCHEDULE_F_LINE_60,
    TP1_SCHEDULE_F_LINE_62,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_schedule_f_support import (
    LINE_68_INPUTS,
    LINE_70,
    LINE_70_PARTS,
    schedule_f,
)

D = Decimal
EXPORT = "ca-qc/tp1_schedule_f_deductions_line_68"
PART = (
    Path(tax_engine.jurisdictions.ca_qc.__file__).parent
    / "manifests"
    / "2025"
    / "tp1_schedule_f_line_68.yaml"
)
# One figure per printed line, each different, so a line left out or counted twice shows.
GIVEN: tuple[tuple[AmountKind, str], ...] = (
    (TP1_SCHEDULE_F_LINE_41, "100.01"),
    (TP1_SCHEDULE_F_LINE_42, "200.02"),
    (TP1_SCHEDULE_F_LINE_43, "300.03"),
    (TP1_SCHEDULE_F_LINE_43_1, "400.04"),
    (TP1_SCHEDULE_F_LINE_44, "500.05"),
    (TP1_SCHEDULE_F_LINE_45, "600.06"),
    (TP1_SCHEDULE_F_LINE_46, "700.07"),
    (TP1_SCHEDULE_F_LINE_54, "800.08"),
    (TP1_SCHEDULE_F_LINE_56, "900.09"),
    (TP1_SCHEDULE_F_LINE_58, "1000.10"),
    (TP1_SCHEDULE_F_LINE_60, "1100.11"),
    (TP1_SCHEDULE_F_LINE_62, "1200.12"),
)
TOTAL = D("7800.78")


def _line_68(take_home_service: TakeHomeService, *given: tuple[AmountKind, str]) -> str:
    sheet = schedule_f(take_home_service, "70000", EXPORT, *given, parts=LINE_70_PARTS, end=LINE_70)
    return str(sheet.get(TP1_SCHEDULE_F_DEDUCTIONS_LINE_68).value)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_salary_only_line_68_is_zero(take_home_service: TakeHomeService, salary: str) -> None:
    sheet = schedule_f(take_home_service, salary, EXPORT, parts=LINE_70_PARTS, end=LINE_70)

    assert str(sheet.get(TP1_SCHEDULE_F_DEDUCTIONS_LINE_68).value) == "0.00"


def test_line_68_adds_every_printed_line_from_41_to_62(take_home_service: TakeHomeService) -> None:
    assert D(_line_68(take_home_service, *GIVEN)) == TOTAL


@pytest.mark.parametrize("left_out", range(len(GIVEN)))
def test_line_68_reads_each_blank_line_as_zero(
    take_home_service: TakeHomeService, left_out: int
) -> None:
    given = tuple(item for index, item in enumerate(GIVEN) if index != left_out)

    assert D(_line_68(take_home_service, *given)) == TOTAL - D(GIVEN[left_out][1])


@pytest.mark.parametrize(("second", "expected"), [("0.001", "0.01"), ("0.0009", "0.00")])
def test_line_68_rounds_the_sum_half_up_to_the_cent(
    take_home_service: TakeHomeService, second: str, expected: str
) -> None:
    # 0.004 + 0.001 = 0.005 rounds up; 0.004 + 0.0009 = 0.0049 rounds down.
    given = ((GIVEN[0][0], "0.004"), (GIVEN[1][0], second))

    assert _line_68(take_home_service, *given) == expected


def test_the_part_is_one_sum_of_the_printed_lines_with_blanks_read_as_zero() -> None:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    (step,) = part["capabilities"]
    names = [f"ca-qc/tp1_schedule_f_line_{line}" for line in LINE_68_INPUTS]

    assert step["name"] == "core/sum"
    assert step["reference"] == "68"
    assert step["title"] == "Deductions"
    assert step["consumes"]["parts"] == names
    assert step["blank"] == {name: "0" for name in names}
    assert step["params"] == {"rounding": "ca-qc/cent_rounding"}
    assert step["produces"] == {"output": EXPORT}
