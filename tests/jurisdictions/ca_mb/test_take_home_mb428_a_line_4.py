"""Schedule MB428-A (2025) line 4, the age amount for self, over the optional year of birth
(`ca/birth_year`, the T1's input, read from its export).

Form text (Schedule MB428-A, CRA 5007-A): "Line 4: Age amount for self if you were born in 1960 or
earlier Claim $2,065". Claimed whole when born in 1960 or earlier, whatever the income; a request
that leaves the year out is not born in 1960 or earlier: line 4 is 0.00. Line 10 (the sum of lines
1 to 9) adds it to the basic amount of line 1.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.jurisdictions.ca_mb import age_support as s

D = Decimal
FORM_NAME = "ca-mb/mb428_a"
LINES = (
    "mb428_a_line_1.yaml",
    "mb428_a_line_4.yaml",
    "mb428_a_line_10.yaml",
)
LINE_4 = "ca-mb/mb428_a_age_amount_line_4"
LINE_10 = "ca-mb/mb428_a_line_10"


def _value(tmp_path: Path, salary: str, year: int | None, identifier: str) -> Decimal:
    given = () if year is None else (Artifact(BIRTH_YEAR, year),)
    sheet = s.sheet(tmp_path, FORM_NAME, salary, LINES, (LINE_4, LINE_10), given)
    return s.value(sheet, identifier)


@pytest.mark.parametrize("salary", ["20000", "30000", "70000"])
@pytest.mark.parametrize("year", [1960, 1959, 1925])
def test_line_4_is_the_printed_claim_when_born_in_1960_or_earlier(
    tmp_path: Path, salary: str, year: int
) -> None:
    assert _value(tmp_path, salary, year, LINE_4) == D("2065.00")


@pytest.mark.parametrize("salary", ["20000", "30000", "70000"])
@pytest.mark.parametrize("year", [None, 1961, 1990])
def test_line_4_is_zero_when_the_year_is_left_out_or_after_1960(
    tmp_path: Path, salary: str, year: int | None
) -> None:
    assert _value(tmp_path, salary, year, LINE_4) == D("0.00")


def test_line_10_adds_line_4_to_the_basic_amount(tmp_path: Path) -> None:
    assert _value(tmp_path / "born", "20000", 1958, LINE_10) == D("4130.00")
    assert _value(tmp_path / "blank", "20000", None, LINE_10) == D("2065.00")
