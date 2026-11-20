"""5005-R (2025) line 85, "Add lines 78 to 84", from the salary alone, real parts.

Form text (CRA 5005-R page 5, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 85: Add lines 78 to 84. =". Line 78 is the basic personal amount; lines 79 to 84 are optional
inputs, each left blank by a salary-only filer and read as 0. One core/sum, rounded half-up to the
cent. Line 86 "Enter the amount from line 85 of the previous page" is a copy and has no step. The
expected figures are the line 78 figures of the hand-calc (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    AGE_AMOUNT_LINE_79,
    BASIC_PERSONAL_AMOUNT,
    CAREGIVER_AMOUNT_INFIRM_CHILDREN_LINE_84,
    CAREGIVER_AMOUNT_INFIRM_DEPENDANTS_LINE_83,
    CAREGIVER_AMOUNT_SPOUSE_LINE_82,
    CREDIT_AMOUNTS_LINE_85,
    ELIGIBLE_DEPENDANT_AMOUNT_LINE_81,
    SPOUSE_AMOUNT_LINE_80,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal
OPTIONAL_LINES = (
    AGE_AMOUNT_LINE_79,
    SPOUSE_AMOUNT_LINE_80,
    ELIGIBLE_DEPENDANT_AMOUNT_LINE_81,
    CAREGIVER_AMOUNT_SPOUSE_LINE_82,
    CAREGIVER_AMOUNT_INFIRM_DEPENDANTS_LINE_83,
    CAREGIVER_AMOUNT_INFIRM_CHILDREN_LINE_84,
)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "16129.00"), ("70000", "16129.00"), ("200000", "15685.73")],
)
def test_a_salary_only_line_85_is_the_basic_personal_amount(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(BASIC_PERSONAL_AMOUNT).value == D(expected)
    assert sheet.get(CREDIT_AMOUNTS_LINE_85).value == D(expected)


@pytest.mark.parametrize("kind", OPTIONAL_LINES)
def test_each_optional_line_is_added_to_line_78(
    take_home_service: TakeHomeService, kind: AmountKind
) -> None:
    _, sheet = sheets(take_home_service, "70000", (kind, "100.10"))

    assert sheet.get(CREDIT_AMOUNTS_LINE_85).value == D("16229.10")


def test_every_optional_line_is_added_in_one_sum(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000", *((kind, "100.10") for kind in OPTIONAL_LINES))

    assert sheet.get(CREDIT_AMOUNTS_LINE_85).value == D("16729.60")


def test_the_trace_names_each_line_and_each_blank_read_as_zero(
    take_home_service: TakeHomeService,
) -> None:
    _, sheet = sheets(take_home_service, "70000")
    trace = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    assert trace.count("Left blank, taken as CA$0.00.") >= len(OPTIONAL_LINES)
    assert (
        "Line 30000 (CA$16129.00) plus line 30100 (CA$0.00) plus line 30300 (CA$0.00) plus line "
        "30400 (CA$0.00) plus line 30425 (CA$0.00) plus line 30450 (CA$0.00) plus line 30500 "
        "(CA$0.00) gives CA$16129.00 (rounded to the nearest cent)."
    ) in trace


def test_the_line_85_kind_is_non_negative() -> None:
    assert non_negative(CREDIT_AMOUNTS_LINE_85) is True
