"""ON428 line 72, the additional tax for minimum tax purposes, from a T691 Part 5 line 11 amount.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 72: If you entered an amount on line 11 of Part
5 of Form T691, use Worksheet ON428 to calculate your additional tax for minimum tax purposes." and
"Line 73: Line 71 plus line 72 =". Worksheet ON428 (CRA 5006-d-25e.txt): "Line 1: Amount from line
11 of Part 5 of your Form T691 multiplied by 24.63% =", "Line 2: Amount from line 65 of your Form
ON428", "Line 3: Line 1 plus line 2 =", "Line 4: (Line 3 Minus $5,710) multiplied by 20% (if
negative, enter "0") =", "Line 5: (Line 3 Minus $7,307) multiplied by 36% (if negative, enter "0")
=", "Line 6: Line 4 plus line 5 =", "Line 7: Amount from line 68 of your Form ON428", "Line 8:
Line 6 minus line 7 =" and "Line 9: Line 1 plus line 8 Enter this amount on line 72 of your Form
ON428."

The real registered engine runs the real Ontario 2025 manifest with a gross salary and, as the one
extra figure, the T691 Part 5 line 11 amount the caller types. At a $150,000 salary ON428 line 65 is
11,458.12 and line 68 is 2,644.02, and a T691 Part 5 line 11 of 10,000.00 gives, by hand:
line 1 = 10,000.00 x 24.63% = 2,463.00; line 3 = 2,463.00 + 11,458.12 = 13,921.12;
line 4 = (13,921.12 - 5,710) x 20% = 1,642.224, so 1,642.22;
line 5 = (13,921.12 - 7,307) x 36% = 2,381.0832, so 2,381.08; line 6 = 4,023.30;
line 8 = 4,023.30 - 2,644.02 = 1,379.28; line 9 = 2,463.00 + 1,379.28 = 3,842.28.
Line 73 is line 71 (14,102.14) plus 3,842.28 = 17,944.42.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
PART_5_LINE_11 = "ca/t691_line_7_minus_line_10"
WORKSHEET = {
    "on428_worksheet_basic_additional_tax_line_1": "2463.00",
    "on428_worksheet_surtax_base_line_3": "13921.12",
    "on428_worksheet_surtax_20_percent_tier_line_4": "1642.22",
    "on428_worksheet_surtax_36_percent_tier_line_5": "2381.08",
    "on428_worksheet_surtax_total_line_6": "4023.30",
    "on428_worksheet_surtax_on_additional_tax_line_8": "1379.28",
}


def _on428(salary: str, part_5_line_11: str | None) -> dict[str, Decimal]:
    kinds = bundled_kinds()
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if part_5_line_11 is not None:
        given.append(Artifact(kinds.kind(PART_5_LINE_11), D(part_5_line_11)))
    (sheet,) = build_tax_computation().compute(TaxCalculationRequest(ONTARIO, 2025, tuple(given)))[
        "ca-on/on428"
    ]
    names = [
        *WORKSHEET,
        "on428_additional_tax_for_minimum_tax_line_72",
        "on428_tax_with_minimum_tax_addition_line_73",
        "on428_ontario_tax_reduction_line_80",
        "on428_ontario_tax_line_90",
    ]
    figures = {name: sheet.get(kinds.kind(f"ca-on/{name}")).value for name in names}
    assert all(isinstance(value, Decimal) for value in figures.values())
    return {name: D(str(value)) for name, value in figures.items()}


def test_a_150000_salary_with_10000_on_t691_part_5_line_11_adds_3842_28_at_line_72() -> None:
    figures = _on428("150000", "10000")

    for name, expected in WORKSHEET.items():
        assert figures[name] == D(expected), name
    assert figures["on428_additional_tax_for_minimum_tax_line_72"] == D("3842.28")
    assert figures["on428_tax_with_minimum_tax_addition_line_73"] == D("17944.42")
    assert figures["on428_ontario_tax_line_90"] == D("18694.42")


def test_a_150000_salary_with_no_t691_line_is_unchanged() -> None:
    figures = _on428("150000", None)

    assert figures["on428_additional_tax_for_minimum_tax_line_72"] == D("0.00")
    assert figures["on428_tax_with_minimum_tax_addition_line_73"] == D("14102.14")
    assert figures["on428_ontario_tax_line_90"] == D("14852.14")


def test_a_30000_salary_with_10000_on_line_11_gives_line_1_alone_as_line_3_is_under_5710() -> None:
    # Line 65 is 766.81, so line 3 is 3,229.81, under $5,710: lines 4 to 8 are 0 and line 72 is
    # line 1 (2,463.00). An amount on line 72 makes line 80, the Ontario tax reduction, 0.
    figures = _on428("30000", "10000")

    assert figures["on428_worksheet_basic_additional_tax_line_1"] == D("2463.00")
    assert figures["on428_worksheet_surtax_total_line_6"] == D("0.00")
    assert figures["on428_additional_tax_for_minimum_tax_line_72"] == D("2463.00")
    assert figures["on428_ontario_tax_reduction_line_80"] == D("0.00")


def test_a_negative_t691_part_5_line_11_is_refused() -> None:
    with pytest.raises(NegativeArtifactError):
        _on428("70000", "-1")
