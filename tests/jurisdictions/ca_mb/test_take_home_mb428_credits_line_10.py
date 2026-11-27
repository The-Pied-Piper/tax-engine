"""MB428 (2025) line 10, the age amount, over the optional year of birth
(`ca/birth_year`, the T1's input, read from its export).

Form text (Form MB428, CRA 5007-C): "Line 10 and line 58080: Age amount (if you were born in 1960
or earlier) (use Worksheet MB428) (maximum $3,728)". Worksheet MB428 (CRA 5007-D), "Line 58080 -
Age amount (if you were born in 1960 or earlier)": line 1 maximum 3,728.00; line 2 amount from line
23600; line 3 income threshold 27,749.00; line 4 line 2 minus line 3 (if negative, enter "0");
line 5 rate 15%; line 6 line 4 times line 5; line 7 line 1 minus line 6 (if negative, enter "0").
A request that leaves the year out is not born in 1960 or earlier: line 10 is 0.00.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.jurisdictions.ca_mb import age_support as s

D = Decimal
FORM_NAME = "ca-mb/mb428_credits"
LINES_10 = (
    "mb428_credits_line_10_worksheet_lines_1_to_3.yaml",
    "mb428_credits_line_10_worksheet_lines_4_to_7.yaml",
    "mb428_credits_line_10.yaml",
)
LINE_2 = "ca-mb/worksheet_mb428_age_amount_net_income_line_2"
LINE_10 = "ca-mb/mb428_age_amount_line_10"
BORN = (Artifact(BIRTH_YEAR, 1960),)


def _sheet(tmp_path: Path, salary: str, given: tuple[Artifact[int], ...]) -> Worksheet:
    return s.sheet(tmp_path, FORM_NAME, salary, LINES_10, (LINE_2, LINE_10), given)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "3728.00"), ("30000", "3430.10"), ("70000", "0.00")],
)
def test_line_10_born_in_1960_or_earlier(tmp_path: Path, salary: str, expected: str) -> None:
    assert s.value(_sheet(tmp_path, salary, BORN), LINE_10) == D(expected)


def test_line_10_in_the_reduction_range_is_the_worksheet_arithmetic(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "40000", BORN)
    net_income = s.value(sheet, LINE_2)
    expected = s.cent(D("3728") - D("0.15") * (net_income - D("27749")))

    assert D("27749") < net_income < D("52602")
    assert s.value(sheet, LINE_10) == expected


@pytest.mark.parametrize("salary", ["20000", "30000", "70000"])
def test_line_10_is_zero_when_the_year_is_left_out_or_after_1960(
    tmp_path: Path, salary: str
) -> None:
    assert s.value(_sheet(tmp_path / "blank", salary, ()), LINE_10) == D("0.00")
    after = (Artifact(BIRTH_YEAR, 1961),)
    assert s.value(_sheet(tmp_path / "after", salary, after), LINE_10) == D("0.00")


def test_line_10_is_claimed_for_any_year_up_to_and_including_1960(tmp_path: Path) -> None:
    for year in (1960, 1959, 1925):
        given = (Artifact(BIRTH_YEAR, year),)
        assert s.value(_sheet(tmp_path / str(year), "20000", given), LINE_10) == D("3728.00")
