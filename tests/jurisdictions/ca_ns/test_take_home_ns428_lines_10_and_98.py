"""NS428 (2025) line 10, the age amount, and line 98, the age tax credit, over the optional
born-in-1960-or-earlier answer (`ca/born_in_1960_or_earlier`, the federal count, entered once).

Form text (Form NS428, CRA 5003-C, PDF; Worksheet NS428, CRA 5003-D):
  Line 10: "Age amount (if you were born in 1960 or earlier) (use Worksheet NS428)
  (maximum $5,734)".
  Worksheet "Line 58080 - Age amount": line 1 maximum 5,734.00; line 2 amount from line 23600;
  line 3 income threshold 30,828.00; line 4 line 2 minus line 3 (if negative, enter "0"); line 5
  rate 15%; line 6 line 4 times line 5; line 7 line 1 minus line 6 (if negative, enter "0").
  Line 98: "Age tax credit (if you were born in 1960 or earlier and your taxable income is less than
  $24,000) Claim $1,000". (CRA's .txt misprints 1959; the PDF says 1960.)
A request that leaves the answer out is not born in 1960 or earlier: both lines are 0.00.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BORN_IN_1960_OR_EARLIER
from tests.jurisdictions.ca_ns import ns428_credits_support as s

D = Decimal
LINES_10 = ("ns428_line_10_input.yaml", "ns428_line_10.yaml")
LINES_98 = ("ns428_line_1.yaml", *LINES_10, "ns428_line_98.yaml")
LINE_7 = "ca-ns/worksheet_ns428_age_amount_line_7"
LINE_2 = "ca-ns/worksheet_ns428_age_amount_net_income_line_2"
LINE_10 = "ca-ns/ns428_age_amount_line_10"
LINE_98 = "ca-ns/ns428_age_tax_credit_line_98"
BORN = (Artifact(BORN_IN_1960_OR_EARLIER, 1),)


def _line_10(tmp_path: Path, salary: str, given: tuple[Artifact[int], ...]) -> Decimal:
    return s.value(s.sheet(tmp_path, salary, LINES_10, (LINE_10,), given), LINE_10)


def _line_98(tmp_path: Path, salary: str, given: tuple[Artifact[int], ...]) -> Decimal:
    return s.value(s.sheet(tmp_path, salary, LINES_98, (LINE_10, LINE_98), given), LINE_98)


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "5734.00"), ("30000", "5734.00"), ("70000", "0.00")]
)
def test_line_10_born_in_1960_or_earlier(tmp_path: Path, salary: str, expected: str) -> None:
    assert _line_10(tmp_path, salary, BORN) == D(expected)


def test_line_10_in_the_reduction_range_is_the_worksheet_arithmetic(tmp_path: Path) -> None:
    sheet = s.sheet(tmp_path, "40000", LINES_10, (LINE_2, LINE_10), BORN)
    net_income = s.value(sheet, LINE_2)
    expected = s.cent(D("5734") - D("0.15") * (net_income - D("30828")))

    assert D("30828") < net_income < D("69055")
    assert s.value(sheet, LINE_10) == expected


@pytest.mark.parametrize("salary", ["20000", "40000"])
def test_line_10_is_zero_when_the_answer_is_left_out_or_no(tmp_path: Path, salary: str) -> None:
    assert _line_10(tmp_path / "blank", salary, ()) == D("0.00")
    no = (Artifact(BORN_IN_1960_OR_EARLIER, 0),)
    assert _line_10(tmp_path / "no", salary, no) == D("0.00")


def test_a_count_above_one_is_refused(tmp_path: Path) -> None:
    with pytest.raises(InputAboveBoundError):
        _line_10(tmp_path, "20000", (Artifact(BORN_IN_1960_OR_EARLIER, 2),))


def test_line_98_is_1000_when_born_in_1960_or_earlier_and_income_is_under_24000(
    tmp_path: Path,
) -> None:
    assert _line_98(tmp_path, "20000", BORN) == D("1000.00")


@pytest.mark.parametrize("salary", ["30000", "70000"])
def test_line_98_is_zero_at_or_above_the_income_limit(tmp_path: Path, salary: str) -> None:
    assert _line_98(tmp_path, salary, BORN) == D("0.00")


def test_line_98_is_zero_when_not_born_in_1960_or_earlier(tmp_path: Path) -> None:
    assert _line_98(tmp_path, "20000", ()) == D("0.00")
