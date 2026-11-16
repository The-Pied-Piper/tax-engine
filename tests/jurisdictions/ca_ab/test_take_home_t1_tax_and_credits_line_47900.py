"""T1 General 2025 (5006-R, Alberta) line 47900 "Provincial or territorial credits": blank.

No Alberta form supplies `ca/provincial_credits.amount` (only British Columbia's BC479 does), and
the T1 part marks that read optional with the blank rule `pass_on`, so line 47900
(`ca/provincial_credits_line_47900`) is blank for the Alberta take-home filer: it has no figure,
and the T1 form still computes. The T1 text for line 47900 is to be confirmed. The real bundled
manifest is run with the salary the only input. Every Alberta figure is unchanged, pinned here by
the $70,000 take-home (salary less CPP, EI and total tax, done outside the engine, as the
README says).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.trace import BlankPassedOnLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds, non_negative

D = Decimal
CODE = JurisdictionCode("CA-AB")
T1_FORM = "ca/t1_tax_and_credits"
RETURN = "ca-ab/return"
LINE_47900 = "ca/provincial_credits_line_47900"
LINE_167 = "ca/refund_or_balance_owing"


def _worksheets(salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return build_tax_computation().compute(CODE, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))


@pytest.mark.parametrize("salary", ["10000", "20000", "70000", "200000"])
def test_line_47900_is_blank_with_no_figure(salary: str) -> None:
    (t1,) = _worksheets(salary)[T1_FORM]

    line_47900 = t1.get(bundled_kinds().kind(LINE_47900))

    assert line_47900.is_blank


def test_line_47900_is_blank_because_the_provincial_credits_are_passed_on() -> None:
    (t1,) = _worksheets("70000")[T1_FORM]
    kind = bundled_kinds().kind(LINE_47900)

    (line,) = [
        each for each in t1.trace if isinstance(each, BlankPassedOnLine) and each.output is kind
    ]
    assert [each.identifier for each in line.because] == ["ca/provincial_credits.amount"]


def test_the_70000_take_home_stays_53782_01() -> None:
    worksheets = _worksheets("70000")
    kinds = bundled_kinds()
    (summary,) = worksheets[RETURN]
    (schedule_8,) = worksheets["ca/schedule_8"]
    (t2204,) = worksheets["ca/t2204"]
    cpp = sum(
        (
            schedule_8.get(kinds.kind(name)).value
            for name in (
                "ca/schedule_8_cpp_base_contributions_on_return",
                "ca/schedule_8_cpp_enhanced_contributions_on_return",
            )
        ),
        D("0"),
    )
    ei = t2204.get(kinds.kind("ca/t2204_premiums_deducted")).value

    assert D("70000") - cpp - ei - summary.get(kinds.kind(LINE_167)).value == D("53782.01")


def test_the_provincial_credits_line_47900_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_47900)

    assert kind.identifier == LINE_47900
    assert non_negative(kind) is True
