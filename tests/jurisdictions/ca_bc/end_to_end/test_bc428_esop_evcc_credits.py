"""BC428 lines 86 to 88, the ESOP and EVCC credits, end to end (#1843).

Form text (Form BC428, CRA 5010-C-25e.txt, confirmed): "Line 86 and line 60450: ESOP 20 certificate
number / Tax credit amount indicated on the certificate", "Line 87 and line 60470: EVCC 30
certificate number / Tax credit amount indicated on the certificate", "Line 88: Line 86 plus line 87
(maximum $2,000) =". A sum above the printed maximum is refused, not capped, as line 84 is.
"""

from __future__ import annotations

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tests.jurisdictions.ca_bc.end_to_end._lump_sum import D, figure, sheet

YEARS = [2025, 2026]
LINE_88 = "bc428_esop_evcc_credits_line_88"
LINE_89 = "bc428_tax_after_esop_evcc_line_89"
LINE_85 = "bc428_tax_after_political_credit_line_85"


@pytest.mark.parametrize("year", YEARS)
def test_a_salary_only_caller_has_line_88_of_0(year: int) -> None:
    worksheet = sheet("bc428", year)

    assert figure(worksheet, LINE_88) == D("0.00")
    assert figure(worksheet, LINE_89) == figure(worksheet, LINE_85)


@pytest.mark.parametrize("year", YEARS)
def test_line_88_adds_line_86_and_line_87(year: int) -> None:
    worksheet = sheet(
        "bc428", year, bc428_esop_credit_line_86="300.25", bc428_evcc_credit_line_87="450.50"
    )

    assert figure(worksheet, LINE_88) == D("750.75")
    assert figure(worksheet, LINE_89) == figure(worksheet, LINE_85) - D("750.75")


@pytest.mark.parametrize("year", YEARS)
def test_line_88_alone_from_line_87(year: int) -> None:
    assert figure(sheet("bc428", year, bc428_evcc_credit_line_87="100"), LINE_88) == D("100.00")


@pytest.mark.parametrize("year", YEARS)
def test_a_sum_exactly_at_the_maximum_passes(year: int) -> None:
    worksheet = sheet(
        "bc428", year, bc428_esop_credit_line_86="1500", bc428_evcc_credit_line_87="500"
    )

    assert figure(worksheet, LINE_88) == D("2000.00")


@pytest.mark.parametrize("year", YEARS)
def test_a_sum_one_cent_above_the_maximum_is_refused(year: int) -> None:
    with pytest.raises(InputAboveBoundError):
        sheet("bc428", year, bc428_esop_credit_line_86="1500", bc428_evcc_credit_line_87="500.01")
