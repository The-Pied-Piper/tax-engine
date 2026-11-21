"""BC479 lines 17 to 25 (venture capital) and 31 to 34 (training and shipbuilding), end to end
(#1843).

Form text (Form BC479, CRA 5010-TC-25e.txt, confirmed): "Line 20: Add lines 17 and 18. (maximum
$120,000) =", "Line 25: Add lines 20, 21, and 23. (maximum $300,000) =", "Line 34: Add lines 31 to
33. =", "Line 35: Add lines 16, 25, 26, 30 and 34. =". A sum above its printed maximum is refused,
not capped. A salary-only caller gives none of the inputs, and every line is 0.00.
"""

from __future__ import annotations

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tests.jurisdictions.ca_bc.end_to_end._lump_sum import D, figure, sheet

YEARS = [2025, 2026]
LINE_15 = "bc479_page_1_total_line_15"
LINE_20 = "bc479_venture_capital_credit_line_20"
LINE_25 = "bc479_venture_capital_credit_line_25"
LINE_34 = "bc479_training_credits_line_34"
LINE_35 = "bc479_page_2_total_line_35"
L17 = "bc479_venture_capital_unused_credit_line_17"
L18 = "bc479_venture_capital_credit_line_18"
L21 = "bc479_venture_capital_credit_line_21"
L23 = "bc479_venture_capital_credit_line_23"


@pytest.mark.parametrize("year", YEARS)
def test_a_salary_only_caller_has_zero_on_every_line(year: int) -> None:
    worksheet = sheet("bc479", year)

    assert figure(worksheet, LINE_20) == D("0.00")
    assert figure(worksheet, LINE_25) == D("0.00")
    assert figure(worksheet, LINE_34) == D("0.00")
    assert figure(worksheet, LINE_35) == figure(worksheet, LINE_15)


@pytest.mark.parametrize("year", YEARS)
def test_line_20_adds_lines_17_and_18(year: int) -> None:
    assert figure(sheet("bc479", year, **{L17: "1000.10", L18: "2000.20"}), LINE_20) == D("3000.30")


@pytest.mark.parametrize("year", YEARS)
def test_line_25_adds_lines_20_21_and_23(year: int) -> None:
    worksheet = sheet("bc479", year, **{L17: "1000", L18: "2000", L21: "3000.50", L23: "400"})

    assert figure(worksheet, LINE_20) == D("3000.00")
    assert figure(worksheet, LINE_25) == D("6400.50")


@pytest.mark.parametrize("year", YEARS)
def test_line_20_at_its_maximum_passes_and_above_it_is_refused(year: int) -> None:
    assert figure(sheet("bc479", year, **{L17: "100000", L18: "20000"}), LINE_20) == D("120000.00")
    with pytest.raises(InputAboveBoundError):
        sheet("bc479", year, **{L17: "100000", L18: "20000.01"})


@pytest.mark.parametrize("year", YEARS)
def test_line_25_at_its_maximum_passes_and_above_it_is_refused(year: int) -> None:
    given = {L17: "100000", L18: "20000", L21: "150000", L23: "30000"}
    assert figure(sheet("bc479", year, **given), LINE_25) == D("300000.00")
    with pytest.raises(InputAboveBoundError):
        sheet("bc479", year, **{**given, L23: "30000.01"})


@pytest.mark.parametrize("year", YEARS)
def test_line_34_adds_lines_31_to_33_and_line_35_reads_it(year: int) -> None:
    worksheet = sheet(
        "bc479",
        year,
        bc479_training_credit_individuals_line_31="10.10",
        bc479_training_credit_employers_line_32="20.20",
        bc479_shipbuilding_credit_line_33="30.30",
    )

    assert figure(worksheet, LINE_34) == D("60.60")
    assert figure(worksheet, LINE_35) == figure(worksheet, LINE_15) + D("60.60")


@pytest.mark.parametrize("year", YEARS)
def test_line_35_reads_line_25(year: int) -> None:
    worksheet = sheet("bc479", year, **{L21: "500"})

    assert figure(worksheet, LINE_35) == figure(worksheet, LINE_15) + D("500.00")
