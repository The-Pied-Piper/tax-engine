"""5005-R (2025) line 156 and line 44000, real parts.

Form text (CRA 5005-R page 8, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Refundable Quebec abatement: Line 156 and line 44000: Amount from Line 42900 multiplied by 16.5% ="
Line 42900 is line 130, the basic federal tax. The figures at 20,000, 70,000 and 200,000 are
hand-computed from the printed forms, not a CRA example. One core/apply_rate over line 130 at the
dataset's printed 16.5%, rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.jurisdictions.ca_qc.catalog import (
    BASIC_FEDERAL_TAX_LINE_130,
    REFUNDABLE_QUEBEC_ABATEMENT_LINE_156,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "23.52"), ("70000", "1241.39"), ("200000", "6498.48")],
)
def test_a_salary_only_line_156_is_the_printed_figure(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(REFUNDABLE_QUEBEC_ABATEMENT_LINE_156).value == D(expected)


def test_line_156_is_16_5_percent_of_line_130(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000")

    assert sheet.get(BASIC_FEDERAL_TAX_LINE_130).value == D("7523.55")
    assert sheet.get(REFUNDABLE_QUEBEC_ABATEMENT_LINE_156).value == D("1241.39")


def test_the_trace_prints_the_line(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000")

    assert (
        "16.5% of line 42900 (CA$7523.55) gives CA$1241.39 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_156_kind_is_non_negative() -> None:
    assert non_negative(REFUNDABLE_QUEBEC_ABATEMENT_LINE_156) is True
