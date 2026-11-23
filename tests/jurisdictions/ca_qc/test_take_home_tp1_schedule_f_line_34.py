"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part A, line 34,
"Add lines 20, 22 and 25 through 33", as the Quebec take-home manifest wires it.

One `core/sum` over the printed lines 20, 22, 25, 26, 28, 29, 30, 31 and 33, rounded half-up to the
cent by `ca-qc/cent_rounding`. Lines 20, 24, 30, 31 and 33 are optional inputs of Schedule F; lines
22, 23, 26, 28 and 29 are copies of TP-1 lines 114, 128, 142, 147 and 148 (given on the TP-1 income
form) and line 25 is a step; each is read as 0 when left out. The expected figures are
hand-computed from the printed lines.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
import yaml

import tax_engine.jurisdictions.ca_qc
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_LINE_114,
    TP1_LINE_128,
    TP1_LINE_142,
    TP1_LINE_147,
    TP1_LINE_148,
    TP1_SCHEDULE_F_LINE_20,
    TP1_SCHEDULE_F_LINE_24,
    TP1_SCHEDULE_F_LINE_30,
    TP1_SCHEDULE_F_LINE_31,
    TP1_SCHEDULE_F_LINE_33,
    TP1_SCHEDULE_F_LINES_20_TO_33_TOTAL_LINE_34,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_schedule_f_support import schedule_f

D = Decimal
EXPORT = "ca-qc/tp1_schedule_f_lines_20_to_33_total_line_34"
PART = (
    Path(tax_engine.jurisdictions.ca_qc.__file__).parent
    / "manifests"
    / "2025"
    / "tp1_schedule_f_line_34.yaml"
)
# The figures behind the printed lines that line 34 adds: lines 22, 23, 26, 28 and 29 are the TP-1
# lines 114, 128, 142, 147 and 148; line 25 comes from lines 23 and 24.
GIVEN: tuple[tuple[AmountKind, str], ...] = (
    (TP1_SCHEDULE_F_LINE_20, "100.10"),
    (TP1_LINE_114, "200.20"),
    (TP1_LINE_128, "1380.50"),
    (TP1_SCHEDULE_F_LINE_24, "1000.00"),
    (TP1_LINE_142, "400.40"),
    (TP1_LINE_147, "500.50"),
    (TP1_LINE_148, "600.60"),
    (TP1_SCHEDULE_F_LINE_30, "700.70"),
    (TP1_SCHEDULE_F_LINE_31, "800.80"),
    (TP1_SCHEDULE_F_LINE_33, "900.90"),
)


def _line_34(take_home_service: TakeHomeService, *given: tuple[AmountKind, str]) -> str:
    sheet = schedule_f(take_home_service, "70000", EXPORT, *given)
    return str(sheet.get(TP1_SCHEDULE_F_LINES_20_TO_33_TOTAL_LINE_34).value)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_salary_only_line_34_is_zero(take_home_service: TakeHomeService, salary: str) -> None:
    sheet = schedule_f(take_home_service, salary, EXPORT)

    assert str(sheet.get(TP1_SCHEDULE_F_LINES_20_TO_33_TOTAL_LINE_34).value) == "0.00"


def test_line_34_adds_lines_20_22_25_26_28_29_30_31_and_33(
    take_home_service: TakeHomeService,
) -> None:
    # 100.10 + 200.20 + (1380.50 - 1000.00) + 400.40 + 500.50 + 600.60 + 700.70 + 800.80 + 900.90
    assert _line_34(take_home_service, *GIVEN) == "4584.70"


@pytest.mark.parametrize("left_out", range(len(GIVEN)))
def test_line_34_reads_each_blank_line_as_zero(
    take_home_service: TakeHomeService, left_out: int
) -> None:
    given = tuple(item for index, item in enumerate(GIVEN) if index != left_out)
    kind, value = GIVEN[left_out]
    # Lines 23 and 24 reach line 34 only as line 25 (the difference).
    contribution = {
        TP1_LINE_128: D(value),
        TP1_SCHEDULE_F_LINE_24: -D(value),
    }.get(kind, D(value))

    assert D(_line_34(take_home_service, *given)) == D("4584.70") - contribution


def test_line_34_is_signed_as_line_25_is(take_home_service: TakeHomeService) -> None:
    assert _line_34(take_home_service, (TP1_SCHEDULE_F_LINE_24, "50.25")) == "-50.25"


@pytest.mark.parametrize(("second", "expected"), [("0.001", "0.01"), ("0.0009", "0.00")])
def test_line_34_rounds_the_sum_half_up_to_the_cent(
    take_home_service: TakeHomeService, second: str, expected: str
) -> None:
    # 0.004 + 0.001 = 0.005 rounds up; 0.004 + 0.0009 = 0.0049 rounds down.
    given = ((TP1_SCHEDULE_F_LINE_20, "0.004"), (TP1_LINE_114, second))

    assert _line_34(take_home_service, *given) == expected


def test_the_part_is_one_sum_of_the_printed_lines_with_blanks_read_as_zero() -> None:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    (step,) = part["capabilities"]
    printed = ["20", "22", "25", "26", "28", "29", "30", "31", "33"]

    assert step["name"] == "core/sum"
    assert step["reference"] == "34"
    assert step["consumes"]["parts"] == [f"ca-qc/tp1_schedule_f_line_{n}" for n in printed]
    assert step["blank"] == {f"ca-qc/tp1_schedule_f_line_{n}": "0" for n in printed if n != "25"}
    assert step["params"] == {"rounding": "ca-qc/cent_rounding"}
    assert step["produces"] == {"output": EXPORT}
