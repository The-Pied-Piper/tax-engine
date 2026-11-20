"""5005-R (2025) line 171 and line 48200, real parts.

Form text (CRA 5005-R page 8, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 171 and line 48200: Add lines 155, 156, and 159 to 170. Total credits ="
Lines 155, 160 and 162 to 170 are optional inputs, a blank for a salary-only filer and read as 0;
line 156 is the refundable Quebec abatement, line 159 the net EI overpayment and line 161 the Canada
workers benefit. The figures at 20,000, 70,000 and 200,000 are hand-computed from the printed forms,
not a CRA example. One core/sum, rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    CANADA_TRAINING_CREDIT_LINE_162,
    ELIGIBLE_EDUCATOR_CREDIT_LINE_167,
    FUEL_CHARGE_FARMERS_CREDIT_LINE_169,
    GST_HST_REBATE_LINE_166,
    INCOME_TAX_DEDUCTED_NET_LINE_155,
    INVESTMENT_TAX_CREDIT_REFUND_LINE_164,
    JOURNALISM_LABOUR_CREDIT_LINE_168,
    MULTIGENERATIONAL_HOME_RENOVATION_CREDIT_LINE_163,
    PART_XII_2_TAX_CREDIT_LINE_165,
    REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT_LINE_160,
    TAX_PAID_BY_INSTALMENTS_LINE_170,
    TOTAL_CREDITS_LINE_171,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal
OPTIONAL_LINES = [
    INCOME_TAX_DEDUCTED_NET_LINE_155,
    REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT_LINE_160,
    CANADA_TRAINING_CREDIT_LINE_162,
    MULTIGENERATIONAL_HOME_RENOVATION_CREDIT_LINE_163,
    INVESTMENT_TAX_CREDIT_REFUND_LINE_164,
    PART_XII_2_TAX_CREDIT_LINE_165,
    GST_HST_REBATE_LINE_166,
    ELIGIBLE_EDUCATOR_CREDIT_LINE_167,
    JOURNALISM_LABOUR_CREDIT_LINE_168,
    FUEL_CHARGE_FARMERS_CREDIT_LINE_169,
    TAX_PAID_BY_INSTALMENTS_LINE_170,
]


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "2702.59"), ("70000", "1241.39"), ("200000", "6498.48")],
)
def test_a_salary_only_line_171_is_the_printed_figure(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(TOTAL_CREDITS_LINE_171).value == D(expected)


@pytest.mark.parametrize("kind", OPTIONAL_LINES)
def test_each_optional_line_is_added(take_home_service: TakeHomeService, kind: AmountKind) -> None:
    _, sheet = sheets(take_home_service, "70000", (kind, "100.10"))

    assert sheet.get(TOTAL_CREDITS_LINE_171).value == D("1341.49")


def test_a_negative_line_155_larger_than_the_other_credits_is_taken(
    take_home_service: TakeHomeService,
) -> None:
    # The form prints no floor on line 171: 1,241.39 less 5,000.00 is -3,758.61.
    _, sheet = sheets(take_home_service, "70000", (INCOME_TAX_DEDUCTED_NET_LINE_155, "-5000"))

    assert sheet.get(TOTAL_CREDITS_LINE_171).value == D("-3758.61")


def test_the_trace_prints_the_line(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "20000")

    assert (
        '"Lines 155, 156 and 159 to 161 added up" (CA$2702.59) plus "Lines 162 to 170 added up" (CA$0.00) '
        "gives CA$2702.59 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_171_kind_is_signed() -> None:
    assert non_negative(TOTAL_CREDITS_LINE_171) is False
