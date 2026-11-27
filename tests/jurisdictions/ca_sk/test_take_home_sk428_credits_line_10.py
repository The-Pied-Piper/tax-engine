"""SK428 (2025) line 10, the age amount, over the optional year of birth
(`ca/birth_year`, the federal count, entered once).

Form text (Form SK428, CRA 5008-C): "Line 10 and line 58080: Age amount (if you were born in 1960
or earlier) (use Worksheet SK428) (maximum $5,785)". Worksheet SK428 (CRA 5008-D), "Line 58080 -
Age amount": line 1 maximum 5,785.00; line 2 amount from line 23600; line 3 income threshold
43,066.00; line 4 line 2 minus line 3 (if negative, enter "0"); line 5 rate 15%; line 6 line 4 times
line 5; line 7 line 1 minus line 6 (if negative, enter "0"). A request that leaves the year out is
not born in 1960 or earlier: line 10 is 0.00.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.jurisdictions.ca_sk import sk428_credits_support as s

D = Decimal
LINES_10 = (
    "sk428_credits_line_10_worksheet_lines_1_to_3.yaml",
    "sk428_credits_line_10_worksheet_lines_4_to_7.yaml",
    "sk428_credits_line_10.yaml",
)
LINE_2 = "ca-sk/worksheet_sk428_age_amount_net_income_line_2"
LINE_10 = "ca-sk/sk428_age_amount_line_10"
BORN = (Artifact(BIRTH_YEAR, 1960),)


def _line_10(tmp_path: Path, salary: str, given: tuple[Artifact[int], ...]) -> Decimal:
    return s.value(s.sheet(tmp_path, salary, LINES_10, (LINE_10,), given), LINE_10)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("20000", "5785.00"),
        ("30000", "5785.00"),
        ("70000", "1844.65"),
        ("100000", "0.00"),
    ],
)
def test_line_10_born_in_1960_or_earlier(tmp_path: Path, salary: str, expected: str) -> None:
    assert _line_10(tmp_path, salary, BORN) == D(expected)


def test_line_10_in_the_reduction_range_is_the_worksheet_arithmetic(tmp_path: Path) -> None:
    sheet = s.sheet(tmp_path, "60000", LINES_10, (LINE_2, LINE_10), BORN)
    net_income = s.value(sheet, LINE_2)
    expected = s.cent(D("5785") - D("0.15") * (net_income - D("43066")))

    assert D("43066") < net_income < D("81633")
    assert D("0") < expected < D("5785")
    assert s.value(sheet, LINE_10) == expected


@pytest.mark.parametrize("salary", ["20000", "60000"])
def test_line_10_is_zero_when_the_year_is_left_out_or_after_1960(
    tmp_path: Path, salary: str
) -> None:
    assert _line_10(tmp_path / "blank", salary, ()) == D("0.00")
    after = (Artifact(BIRTH_YEAR, 1961),)
    assert _line_10(tmp_path / "after", salary, after) == D("0.00")


def test_line_10_is_claimed_for_any_year_up_to_and_including_1960(tmp_path: Path) -> None:
    for year in (1960, 1959, 1925):
        given = (Artifact(BIRTH_YEAR, year),)
        assert _line_10(tmp_path / str(year), "20000", given) == D("5785.00")
