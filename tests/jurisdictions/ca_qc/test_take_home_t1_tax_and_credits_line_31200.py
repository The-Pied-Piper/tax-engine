"""5005-R (2025) line 89 and line 31200, from the salary alone, real parts.

Form text (CRA 5005-R page 6, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Employment insurance premiums: Line 89 and line 31200: through employment (maximum $860.67)". A
copy of T2204 line 16, the EI premium at the Quebec 1.31% rate to the printed maximum: 262.00 at
20,000, and 860.67 at 70,000 and at 200,000.

The figures are hand-computed from the printed forms (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.jurisdictions.ca_qc.catalog import EI_PREMIUMS_LINE_89
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "262.00"), ("70000", "860.67"), ("200000", "860.67")],
)
def test_line_89_is_the_figure_it_copies(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(EI_PREMIUMS_LINE_89).value == D(expected)


def test_the_trace_names_the_figure_copied(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000")

    assert "Line 16 of T2204 (CA$860.67) gives CA$860.67." in EnglishTraceRenderer().render_all(
        sheet.trace, sheet
    )


def test_the_line_89_kind_is_non_negative() -> None:
    assert non_negative(EI_PREMIUMS_LINE_89) is True
