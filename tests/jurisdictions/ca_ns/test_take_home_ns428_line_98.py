"""NS428 (2025) line 98, the age tax credit.

Form text (Form NS428, CRA 5003-C, PDF): "Line 98: Age tax credit (if you were born in 1960 or
earlier and your taxable income is less than $24,000) Claim $1,000". (CRA's .txt misprints 1959; the
PDF and the information guide say 1960.) Both conditions must hold; the answer left out is not
born in 1960 or earlier.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BORN_IN_1960_OR_EARLIER
from tests.jurisdictions.ca_ns import ns428_credits_support as s

D = Decimal
LINES_98 = (
    "ns428_line_1.yaml",
    "ns428_line_10_input.yaml",
    "ns428_line_10_worksheet_lines_1_to_3.yaml",
    "ns428_line_10_worksheet_lines_4_to_7.yaml",
    "ns428_line_10.yaml",
    "ns428_line_98.yaml",
)
LINE_10 = "ca-ns/ns428_age_amount_line_10"
LINE_98 = "ca-ns/ns428_age_tax_credit_line_98"
BORN = (Artifact(BORN_IN_1960_OR_EARLIER, 1),)


def _line_98(tmp_path: Path, salary: str, given: tuple[Artifact[int], ...]) -> Decimal:
    return s.value(s.sheet(tmp_path, salary, LINES_98, (LINE_10, LINE_98), given), LINE_98)


def test_line_98_is_1000_when_born_in_1960_or_earlier_and_income_is_under_24000(
    tmp_path: Path,
) -> None:
    assert _line_98(tmp_path, "20000", BORN) == D("1000.00")


@pytest.mark.parametrize("salary", ["30000", "70000"])
def test_line_98_is_zero_at_or_above_the_income_limit(tmp_path: Path, salary: str) -> None:
    assert _line_98(tmp_path, salary, BORN) == D("0.00")


def test_line_98_is_zero_when_not_born_in_1960_or_earlier(tmp_path: Path) -> None:
    assert _line_98(tmp_path, "20000", ()) == D("0.00")
