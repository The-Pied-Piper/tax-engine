"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part A, line 25, "Subtract line 24 from line 23",
as the Quebec take-home manifest wires it.

Line 23 is the taxable amount of the dividends from taxable Canadian corporations (a copy of TP-1
line 128, given on the TP-1 income form) and line 24 their actual amount (an optional input), both
read as 0 when blank. `core/subtract` takes line 24 off line 23,
rounded half-up to the cent; no floor is printed, so the result is signed. The expected figures are
hand-computed from the printed lines.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_qc
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_LINE_128,
    TP1_SCHEDULE_F_LINE_24,
    TP1_SCHEDULE_F_LINE_25,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_schedule_f_support import schedule_f

EXPORT = "ca-qc/tp1_schedule_f_line_25"
PART = (
    Path(tax_engine.jurisdictions.ca_qc.__file__).parent
    / "manifests"
    / "2025"
    / "tp1_schedule_f_line_25.yaml"
)


def _line_25(take_home_service: TakeHomeService, *given: tuple[Any, str]) -> str:
    sheet = schedule_f(take_home_service, "70000", EXPORT, *given)
    return str(sheet.get(TP1_SCHEDULE_F_LINE_25).value)


def test_line_25_with_both_lines_blank_is_zero(take_home_service: TakeHomeService) -> None:
    assert _line_25(take_home_service) == "0.00"


def test_line_25_takes_line_24_off_line_23(take_home_service: TakeHomeService) -> None:
    given = ((TP1_LINE_128, "1380.00"), (TP1_SCHEDULE_F_LINE_24, "1000.00"))

    assert _line_25(take_home_service, *given) == "380.00"


def test_line_25_reads_a_blank_line_24_as_zero(take_home_service: TakeHomeService) -> None:
    assert _line_25(take_home_service, (TP1_LINE_128, "1380.00")) == "1380.00"


def test_line_25_reads_a_blank_line_23_as_zero_and_is_signed(
    take_home_service: TakeHomeService,
) -> None:
    assert _line_25(take_home_service, (TP1_SCHEDULE_F_LINE_24, "100.00")) == "-100.00"


@pytest.mark.parametrize(("line_24", "expected"), [("0.001", "0.00"), ("0.0009", "0.01")])
def test_line_25_rounds_half_up_to_the_cent(
    take_home_service: TakeHomeService, line_24: str, expected: str
) -> None:
    # 0.0059 - 0.001 = 0.0049 rounds down; 0.0059 - 0.0009 = 0.0050 rounds up.
    given = ((TP1_LINE_128, "0.0059"), (TP1_SCHEDULE_F_LINE_24, line_24))

    assert _line_25(take_home_service, *given) == expected


def test_the_part_is_one_subtract_of_line_24_from_line_23() -> None:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    (step,) = part["capabilities"]

    assert step["name"] == "core/subtract"
    assert step["reference"] == "25"
    assert step["consumes"] == {
        "amount": "ca-qc/tp1_schedule_f_line_23",
        "less": "ca-qc/tp1_schedule_f_line_24",
    }
    assert step["blank"] == {"amount": "0", "less": "0"}
    assert step["params"] == {"rounding": "ca-qc/cent_rounding"}
