"""ON428 (2025) line 57, the dividend tax credit, from the printed worksheet through the real
engine.

Worksheet 5006-D (2025), "Line 61520 - Ontario dividend tax credit":
"Line A: Amount from line 12000 of your return",
"Line 1: Amount from line 12010 of your return Line B multiplied by 2.9863% =",
"Line 2: Amount A minus amount B Line C = multiplied by 10% =" and "Line 3: Line 1 plus line 2".
Line 57 of ON428 is line 3, so the part is six steps: the two totals of the T1 exports of lines
12000 and 12010 (the T1 owns the two inputs; a form reads another form's export only as a record
list), line 1, line C, line 2 and line 3. Each rate is a printed rate held in its own dataset and
each product rounds half-up to the cent. A caller who gives neither line has a credit of 0.00.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_on
from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import artifact_kinds

D = Decimal
FORM = "ca-on/on428"
PART = Path(tax_engine.jurisdictions.ca_on.__file__).parent / "manifests/2025/on428_line_57.yaml"
DIVIDENDS = "ca/taxable_dividends"
OTHER_THAN_ELIGIBLE = "ca/taxable_dividends_other_than_eligible"
PREFIX = "ca-on/on428_dividend_tax_credit_worksheet_line_"
LINE_57 = "ca-on/on428_dividend_tax_credit_line_57"
RATE = "ca-on/dividend_tax_credit_worksheet_rate_line_"
ROUNDING = "ca-on/cent_rounding"
TITLE = "Ontario dividend tax credit"


def _figure(name: str, dividends: str | None, other: str | None) -> Decimal:
    kinds = artifact_kinds()
    given = [Artifact(EMPLOYMENT_INCOME, D("70000"))]
    if dividends is not None:
        given.append(Artifact(kinds.kind(DIVIDENDS), D(dividends)))
    if other is not None:
        given.append(Artifact(kinds.kind(OTHER_THAN_ELIGIBLE), D(other)))
    worksheets = build_tax_computation().compute(JurisdictionCode("CA-ON"), 2025, *given)
    (sheet,) = worksheets[FORM]
    kind = kinds.kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def test_the_part_is_the_printed_worksheet_in_six_steps() -> None:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert part["form"] == {"name": FORM}
    assert "inputs" not in part
    steps: list[dict[str, Any]] = part["capabilities"]
    assert steps == [
        {
            "name": "core/record_total",
            "title": "Amount from line 12000 of your return",
            "reference": "57 worksheet line A",
            "unit": "ca/cad",
            "consumes": {"records": "ca/t1_lines_copied_by_provinces.taxable_dividends_line_12000"},
            "produces": {"output": PREFIX + "a"},
        },
        {
            "name": "core/record_total",
            "title": "Amount from line 12010 of your return",
            "reference": "57 worksheet line B",
            "unit": "ca/cad",
            "consumes": {
                "records": (
                    "ca/t1_lines_copied_by_provinces.taxable_dividends_other_than_eligible_line_12010"
                )
            },
            "produces": {"output": PREFIX + "b"},
        },
        {
            "name": "core/apply_rate",
            "reference": "57 worksheet line 1",
            "unit": "ca/cad",
            "params": {"rate": RATE + "1"},
            "consumes": {"base": PREFIX + "b"},
            "produces": {"output": PREFIX + "1"},
        },
        {
            "name": "core/subtract",
            "title": "Amount A minus amount B",
            "reference": "57 worksheet line C",
            "unit": "ca/cad",
            "params": {"rounding": ROUNDING},
            "consumes": {"amount": PREFIX + "a", "less": PREFIX + "b"},
            "produces": {"output": PREFIX + "c"},
        },
        {
            "name": "core/apply_rate",
            "reference": "57 worksheet line 2",
            "unit": "ca/cad",
            "params": {"rate": RATE + "2"},
            "consumes": {"base": PREFIX + "c"},
            "produces": {"output": PREFIX + "2"},
        },
        {
            "name": "core/sum",
            "title": TITLE,
            "reference": "57",
            "unit": "ca/cad",
            "params": {"rounding": ROUNDING},
            "consumes": {"parts": [PREFIX + "1", PREFIX + "2"]},
            "produces": {"output": LINE_57},
        },
    ]


def test_lines_12000_of_1000_and_12010_of_400_give_the_worksheet_figures() -> None:
    # Line 1 is 400 at 2.9863%, line C is 600 and line 2 is 600 at 10%.
    assert _figure(PREFIX + "1", "1000", "400") == D("11.95")
    assert _figure(PREFIX + "2", "1000", "400") == D("60.00")
    assert _figure(LINE_57, "1000", "400") == D("71.95")


def test_a_caller_who_gives_line_12000_alone_has_all_of_it_at_the_second_rate() -> None:
    assert _figure(PREFIX + "1", "1000", None) == D("0.00")
    assert _figure(LINE_57, "1000", None) == D("100.00")


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        # With line 12000 equal to line 12010, line C is 0, so line 57 is line 1 alone: a tie
        # at the third decimal, rounded half-up to the cent.
        ("15000", "447.95"),
    ],
)
def test_line_57_is_rounded_half_up_to_the_cent(amount: str, expected: str) -> None:
    assert _figure(LINE_57, amount, amount) == D(expected)


def test_a_caller_who_gives_neither_line_has_no_dividend_tax_credit() -> None:
    assert _figure(LINE_57, None, None) == D("0.00")
