"""MB479 (2025) line 8, the age credit for self, over the optional year of birth
(`ca/birth_year`, the T1's input, read from its export).

Form text (Form MB479, CRA 5007-TC): "Line 8: Age credit for self (if you were born in 1960 or
earlier) Claim $113". Claimed whole when born in 1960 or earlier, whatever the income; a request
that leaves the year out is not born in 1960 or earlier: line 8 is 0.00. It replaces the typed-in
amount of the same identifier, so it is never blank.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.jurisdictions.ca_mb import age_support as s

D = Decimal
FORM_NAME = "ca-mb/mb479"
LINES = ("mb479_line_8.yaml",)
LINE_8 = "ca-mb/mb479_age_credit_line_8"


def _line_8(tmp_path: Path, salary: str, year: int | None) -> Decimal:
    given = () if year is None else (Artifact(BIRTH_YEAR, year),)
    return s.value(s.sheet(tmp_path, FORM_NAME, salary, LINES, (LINE_8,), given), LINE_8)


@pytest.mark.parametrize("salary", ["20000", "30000", "70000"])
@pytest.mark.parametrize("year", [1960, 1959, 1925])
def test_line_8_is_the_printed_claim_when_born_in_1960_or_earlier(
    tmp_path: Path, salary: str, year: int
) -> None:
    assert _line_8(tmp_path, salary, year) == D("113.00")


@pytest.mark.parametrize("salary", ["20000", "30000", "70000"])
@pytest.mark.parametrize("year", [None, 1961, 1990])
def test_line_8_is_zero_when_the_year_is_left_out_or_after_1960(
    tmp_path: Path, salary: str, year: int | None
) -> None:
    assert _line_8(tmp_path, salary, year) == D("0.00")
