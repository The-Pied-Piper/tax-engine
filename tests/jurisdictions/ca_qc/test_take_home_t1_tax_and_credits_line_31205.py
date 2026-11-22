"""5005-R (2025) line 91 and line 31205, from the salary alone, real parts.

Form text (CRA 5005-R page 6, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 91 and line 31205: Provincial parental insurance plan (PPIP) premiums paid (box 55 of all T4
slips) (maximum $484.12)". A copy of the PPIP premium figure (0.494% of the salary to $98,000, at
most $484.12): 98.80 at 20,000, 345.80 at 70,000 and the printed maximum 484.12 at 200,000. Line 92
(line 31210) is an optional input, 0 for a Quebec employee, so line 91 is the whole PPIP credit.

The figures are hand-computed from the printed forms (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.jurisdictions.ca_qc.catalog import PPIP_PREMIUMS_LINE_91
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "98.80"), ("70000", "345.80"), ("200000", "484.12")],
)
def test_line_91_is_the_figure_it_copies(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(PPIP_PREMIUMS_LINE_91).value == D(expected)


def test_the_trace_names_the_figure_copied(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000")

    assert (
        "Line 91 of T1 Income Tax and Benefit Return (CA$345.80) gives CA$345.80."
        in EnglishTraceRenderer().render_all(sheet.trace, sheet)
    )


def test_the_line_91_kind_is_non_negative() -> None:
    assert non_negative(PPIP_PREMIUMS_LINE_91) is True
