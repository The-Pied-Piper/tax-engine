"""Revenu Quebec TP-1.D-V (2025-12), page 5, lines 432 to 479, as one chain.

The chain runs the real form declaration and the real parts of every line of page 5 and of the
forms they read: the tax form (line 432), Schedule F (line 82), Schedule K (line 98) and Schedule P
(line 90), over the TP-1 net income lines, Schedule U, Schedule B, the credits lines and the two
work charts (the TP-1 slip figures that Schedule U reads are plain starting inputs, as in its own
tests). The salary is $20,000, $70,000 and $200,000. Every optional line is left blank, read as 0;
the answers to "lived alone" and "covered by a group drug plan" are the defaults (not alone, not
covered). Each expected figure is recomputed in the test from the printed lines: line 450 adds lines
432 and 446 to 447, line 465 adds line 456, line 468 adds lines 465 and 466, line 470 is line 450
less line 468, line 474 is line 470 if negative (as a positive figure) and line 475 is line 470 if
positive, line 478 is line 474 less line 476 and line 479 is line 475 less line 477. The expected
figures are hand-computed from the printed forms (not an official example).
"""

from __future__ import annotations

from decimal import Decimal

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_B_LIVED_ALONE_LINE_20,
    TP1_BALANCE_DUE_LINE_479,
    TP1_DRUG_INSURANCE_PREMIUM_LINE_447,
    TP1_HEALTH_SERVICES_FUND_LINE_446,
    TP1_INCOME_TAX_AND_CONTRIBUTIONS_LINE_450,
    TP1_INCOME_TAX_PAID_AND_OTHER_CREDITS_LINE_465,
    TP1_LINE_468,
    TP1_LINE_470,
    TP1_LINE_474,
    TP1_LINE_475,
    TP1_REFUND_LINE_478,
    TP1_TOTALS_LINE_432,
    TP1_WORK_PREMIUM_TAX_CREDITS_LINE_456,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_totals_support import (
    ALL_PARTS,
    EXPECTED,
    FORM,
    SALARIES,
    real_totals_form,
    totals_sheet,
)

D = Decimal
ZERO = D("0")


@pytest.mark.parametrize("salary", SALARIES)
def test_the_chain_from_line_432_to_the_refund_or_balance_due(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = totals_sheet(take_home_service, salary, real_totals_form(), ALL_PARTS)

    line_432 = sheet.get(TP1_TOTALS_LINE_432).value
    line_446 = sheet.get(TP1_HEALTH_SERVICES_FUND_LINE_446).value
    line_447 = sheet.get(TP1_DRUG_INSURANCE_PREMIUM_LINE_447).value
    line_450 = sheet.get(TP1_INCOME_TAX_AND_CONTRIBUTIONS_LINE_450).value
    line_456 = sheet.get(TP1_WORK_PREMIUM_TAX_CREDITS_LINE_456).value
    line_465 = sheet.get(TP1_INCOME_TAX_PAID_AND_OTHER_CREDITS_LINE_465).value
    line_468 = sheet.get(TP1_LINE_468).value
    line_470 = sheet.get(TP1_LINE_470).value
    assert line_450 == line_432 + line_446 + line_447
    assert line_465 == line_456
    assert line_468 == line_465
    assert line_470 == line_450 - line_468
    assert sheet.get(TP1_LINE_474).value == max(-line_470, ZERO)
    assert sheet.get(TP1_LINE_475).value == max(line_470, ZERO)
    assert sheet.get(TP1_REFUND_LINE_478).value == sheet.get(TP1_LINE_474).value
    assert sheet.get(TP1_BALANCE_DUE_LINE_479).value == sheet.get(TP1_LINE_475).value
    figures = EXPECTED[salary]
    assert str(line_432) == figures["432"]
    assert str(line_446) == figures["446"]
    assert str(line_447) == figures["447"]
    assert str(line_450) == figures["450"]
    assert str(line_456) == figures["456"]
    assert str(line_465) == figures["465"]
    assert str(line_468) == figures["468"]
    assert str(line_470) == figures["470"]
    assert str(sheet.get(TP1_LINE_474).value) == figures["474"]
    assert str(sheet.get(TP1_LINE_475).value) == figures["475"]
    assert str(sheet.get(TP1_REFUND_LINE_478).value) == figures["478"]
    assert str(sheet.get(TP1_BALANCE_DUE_LINE_479).value) == figures["479"]


@pytest.mark.parametrize(
    ("salary", "refund", "balance"),
    [("20000", "575.06", "0.00"), ("70000", "0.00", "8396.16"), ("200000", "0.00", "38757.53")],
)
def test_the_refund_or_the_balance_due_of_a_salary_only_filer(
    take_home_service: TakeHomeService, salary: str, refund: str, balance: str
) -> None:
    sheet = totals_sheet(take_home_service, salary, real_totals_form(), ALL_PARTS)

    assert str(sheet.get(TP1_REFUND_LINE_478).value) == refund
    assert str(sheet.get(TP1_BALANCE_DUE_LINE_479).value) == balance


# Lines 432, 450, 465, 470, 478 and 479 for a person who lived alone: Schedule B line 34 is 0.00 at
# $70,000 and $200,000, so only $20,000 changes (line 432 is floored at 0.00, so line 450 is 0.00).
ALONE = {
    "20000": ("0.00", "0.00", "584.02", "-584.02", "584.02", "0.00"),
    "70000": ("7641.16", "8396.16", "0.00", "8396.16", "0.00", "8396.16"),
    "200000": ("38002.53", "38757.53", "0.00", "38757.53", "0.00", "38757.53"),
}


@pytest.mark.parametrize("salary", SALARIES)
def test_the_chain_for_a_person_who_lived_alone(
    take_home_service: TakeHomeService, salary: str
) -> None:
    given = Artifact(SCHEDULE_B_LIVED_ALONE_LINE_20, 1)
    sheet = totals_sheet(take_home_service, salary, real_totals_form(), ALL_PARTS, given)

    line_432, line_450, line_465, line_470, refund, balance = ALONE[salary]
    assert str(sheet.get(TP1_TOTALS_LINE_432).value) == line_432
    assert str(sheet.get(TP1_INCOME_TAX_AND_CONTRIBUTIONS_LINE_450).value) == line_450
    assert str(sheet.get(TP1_INCOME_TAX_PAID_AND_OTHER_CREDITS_LINE_465).value) == line_465
    assert str(sheet.get(TP1_LINE_470).value) == line_470
    assert str(sheet.get(TP1_REFUND_LINE_478).value) == refund
    assert str(sheet.get(TP1_BALANCE_DUE_LINE_479).value) == balance


@pytest.mark.parametrize("salary", SALARIES)
def test_a_caller_who_gives_no_answer_gets_the_default_not_alone(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = totals_sheet(take_home_service, salary, real_totals_form(), ALL_PARTS)

    assert str(sheet.get(TP1_TOTALS_LINE_432).value) == EXPECTED[salary]["432"]
    assert str(sheet.get(TP1_LINE_470).value) == EXPECTED[salary]["470"]


def test_the_real_form_declaration_exports_lines_450_456_478_and_479() -> None:
    declaration = yaml.safe_load(real_totals_form())

    assert list(declaration["form"]) == ["name", "title", "required", "exports"]
    assert declaration["form"]["name"] == FORM
    assert declaration["form"]["title"] == "Refund or balance due"
    assert declaration["form"]["required"] is True
    assert declaration["form"]["exports"] == [
        "ca-qc/tp1_income_tax_and_contributions_line_450",
        "ca-qc/tp1_work_premium_tax_credits_line_456",
        "ca-qc/tp1_refund_line_478",
        "ca-qc/tp1_balance_due_line_479",
    ]
    assert declaration["capabilities"] == []
