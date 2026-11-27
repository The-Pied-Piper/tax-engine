"""SK428 (2025) line 19, the senior supplementary amount, over the optional year of birth.

Form text (Form SK428, CRA 5008-C): "Line 19 and line 58220: Senior supplementary amount (if you
were born in 1960 or earlier) Claim $2,028". A flat claim: no worksheet and no income test, so it is
$2,028.00 at every salary when born in 1960 or earlier, and 0.00 when the year is left out or later.
Line 20 adds it with lines 9 and 10.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.jurisdictions.ca_sk import sk428_credits_support as s

D = Decimal
LINES = (
    "sk428_credits_line_9.yaml",
    "sk428_credits_line_10_worksheet_lines_1_to_3.yaml",
    "sk428_credits_line_10_worksheet_lines_4_to_7.yaml",
    "sk428_credits_line_10.yaml",
    "sk428_credits_line_19.yaml",
    "sk428_credits_line_20.yaml",
)
LINE_19 = "ca-sk/sk428_senior_supplementary_amount_line_19"
LINE_20 = "ca-sk/sk428_credits_subtotal_line_20"
EXPORTS = (LINE_19, LINE_20)


def _sheet(tmp_path: Path, salary: str, year: int | None) -> tuple[Decimal, Decimal]:
    given = () if year is None else (Artifact(BIRTH_YEAR, year),)
    sheet = s.sheet(tmp_path, salary, LINES, EXPORTS, given)
    return s.value(sheet, LINE_19), s.value(sheet, LINE_20)


@pytest.mark.parametrize("salary", ["20000", "30000", "70000"])
def test_line_19_is_2028_when_born_in_1960_or_earlier_at_every_salary(
    tmp_path: Path, salary: str
) -> None:
    line_19, _ = _sheet(tmp_path, salary, 1960)

    assert line_19 == D("2028.00")


@pytest.mark.parametrize("year", [None, 1961, 1990])
def test_line_19_is_zero_when_the_year_is_left_out_or_after_1960(
    tmp_path: Path, year: int | None
) -> None:
    line_19, line_20 = _sheet(tmp_path, "30000", year)

    assert line_19 == D("0.00")
    assert line_20 == D("19491.00")


def test_line_20_adds_lines_9_10_and_19(tmp_path: Path) -> None:
    _, line_20 = _sheet(tmp_path, "20000", 1950)

    assert line_20 == D("19491.00") + D("5785.00") + D("2028.00")
