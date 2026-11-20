"""5005-R (2025) line 87 and line 30800, from the salary alone, real parts.

Form text (CRA 5005-R page 6, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Base CPP or QPP contributions (complete Schedule 8 or Form RC381, whichever applies): Line 87 and
line 30800: through employment income (maximum $3,661.20)". A copy of Schedule 8 line 25, which is
the QPP at 5.4% to the printed maximum: 5.4% of 20,000 less the 3,500 exemption is 891.00, of 70,000
is 3,591.00, and 200,000 is at the maximum 3,661.20.

The figures are hand-computed from the printed forms (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.jurisdictions.ca_qc.catalog import QPP_BASE_CONTRIBUTIONS_LINE_87
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "891.00"), ("70000", "3591.00"), ("200000", "3661.20")],
)
def test_line_87_is_the_figure_it_copies(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(QPP_BASE_CONTRIBUTIONS_LINE_87).value == D(expected)


def test_the_trace_names_the_figure_copied(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000")

    assert (
        "Line 25 of Schedule 8 (CA$3591.00) gives CA$3591.00."
        in EnglishTraceRenderer().render_all(sheet.trace, sheet)
    )


def test_the_line_87_kind_is_non_negative() -> None:
    assert non_negative(QPP_BASE_CONTRIBUTIONS_LINE_87) is True
