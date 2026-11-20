"""The Quebec take-home return summary (2025): the refund or balance owing, the total payable and
the solidarity credit, from the two Quebec returns.

No printed line adds the 5005-R and TP-1 returns, so the summary is the engine's own step, as T1
line 167 is in the other provinces, and its steps print no line of their own. The figures it adds
are printed lines, each read from the form that prints it:
- 5005-R line 172 "Refund or balance owing" (CRA 5005-R, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
  "Line 172: Line 152 minus line 171 ... Refund or balance owing =";
- 5005-R line 151 and line 43500: "Add lines 147 to 150. Total payable =";
- 5005-R line 156 and line 44000: "Amount from Line 42900 multiplied by 16.5% =" (refundable Quebec
  abatement);
- TP-1 line 450 "Add lines 432 through 447. Income tax and contributions" and line 456 "Tax credits
  respecting the work premium" (Revenu Quebec TP-1.D-V (2025-12), page 5).
TP-1 lines 470 to 479 (450 less 468) are not used, because the credits that line 468 collects are
left out of the take-home by ruling, so for this filer only line 456 reduces line 450.

The tests run the real return part over the real parts of the three forms it reads, at a salary
of $20,000, $70,000 and $200,000, and pin the part's shape. The figures are hand-computed from
the printed forms, not a CRA or Revenu Quebec example.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca.catalog.refund import REFUND_OR_BALANCE_OWING
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_B_LIVED_ALONE_LINE_20,
    SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50,
    SOLIDARITY_CREDIT,
    SOLIDARITY_LIVED_ALONE_LINE_12,
    SOLIDARITY_TENANT_OR_OWNER_LINES_32_36,
    TOTAL_PAYABLE,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.return_support import EXPECTED, RETURN_PART, SALARIES, return_sheet
from tests.jurisdictions.ca_qc.support import quebec_kinds

D = Decimal


def _total_payable(salary: str) -> str:
    # Total payable is line 43500 less line 44000 plus TP-1 line 450.
    figures = EXPECTED[salary]
    return str(D(figures["43500"]) - D(figures["44000"]) + D(figures["450"]))


@pytest.mark.parametrize("salary", SALARIES)
def test_refund_or_balance_owing_adds_line_172_to_line_450_less_line_456(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = return_sheet(take_home_service, salary)
    figures = EXPECTED[salary]
    expected = D(figures["172"]) + D(figures["450"]) - D(figures["456"])

    assert sheet.get(REFUND_OR_BALANCE_OWING).value == expected


@pytest.mark.parametrize(("salary", "expected"), [("20000", "-3135.08"), ("70000", "14678.32")])
def test_refund_or_balance_owing_is_signed_positive_owing_negative_a_refund(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = return_sheet(take_home_service, salary)

    assert str(sheet.get(REFUND_OR_BALANCE_OWING).value) == expected


def test_refund_or_balance_owing_at_200000(take_home_service: TakeHomeService) -> None:
    sheet = return_sheet(take_home_service, "200000")

    assert str(sheet.get(REFUND_OR_BALANCE_OWING).value) == "71643.79"


@pytest.mark.parametrize("salary", SALARIES)
def test_total_payable_is_line_43500_less_line_44000_plus_line_450(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = return_sheet(take_home_service, salary)

    assert str(sheet.get(TOTAL_PAYABLE).value) == _total_payable(salary)


@pytest.mark.parametrize(("salary", "expected"), [("20000", "128.01"), ("70000", "14678.32")])
def test_total_payable_figures(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = return_sheet(take_home_service, salary)

    assert str(sheet.get(TOTAL_PAYABLE).value) == expected


def test_total_payable_at_200000(take_home_service: TakeHomeService) -> None:
    assert str(return_sheet(take_home_service, "200000").get(TOTAL_PAYABLE).value) == "71643.79"


@pytest.mark.parametrize("salary", SALARIES)
def test_the_solidarity_credit_is_its_own_amount_not_inside_the_result(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = return_sheet(take_home_service, salary)

    assert str(sheet.get(SOLIDARITY_CREDIT).value) == EXPECTED[salary]["solidarity"]
    assert sheet.get(REFUND_OR_BALANCE_OWING).value == D(EXPECTED[salary]["172"]) + D(
        EXPECTED[salary]["450"]
    ) - D(EXPECTED[salary]["456"])


@pytest.mark.parametrize(
    ("salary", "refund_or_balance", "total_payable", "solidarity"),
    [("20000", "-3144.04", "119.05", "1281.00")],
)
def test_alone_and_a_tenant_at_20000(
    take_home_service: TakeHomeService,
    salary: str,
    refund_or_balance: str,
    total_payable: str,
    solidarity: str,
) -> None:
    # Schedule B line 20 and Schedule D line 12 are the same fact entered on two forms.
    sheet = return_sheet(
        take_home_service,
        salary,
        Artifact(SCHEDULE_B_LIVED_ALONE_LINE_20, 1),
        Artifact(SOLIDARITY_LIVED_ALONE_LINE_12, 1),
        Artifact(SOLIDARITY_TENANT_OR_OWNER_LINES_32_36, 1),
    )

    assert str(sheet.get(REFUND_OR_BALANCE_OWING).value) == refund_or_balance
    assert str(sheet.get(TOTAL_PAYABLE).value) == total_payable
    assert str(sheet.get(SOLIDARITY_CREDIT).value) == solidarity


@pytest.mark.parametrize(
    ("salary", "refund_or_balance", "total_payable"),
    [("70000", "13923.32", "13923.32"), ("200000", "70888.79", "70888.79")],
)
def test_the_group_plan_case_drops_the_755_premium(
    take_home_service: TakeHomeService, salary: str, refund_or_balance: str, total_payable: str
) -> None:
    sheet = return_sheet(
        take_home_service, salary, Artifact(SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50, 1)
    )

    assert str(sheet.get(REFUND_OR_BALANCE_OWING).value) == refund_or_balance
    assert str(sheet.get(TOTAL_PAYABLE).value) == total_payable


def _steps() -> list[dict[str, Any]]:
    part = yaml.safe_load((QUEBEC_PARTS / RETURN_PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["capabilities"]
    steps = part["capabilities"]
    assert isinstance(steps, list)
    return steps


def test_the_part_has_ten_steps_none_with_a_title_or_a_reference() -> None:
    steps = _steps()

    assert [step["name"] for step in steps] == [
        "core/record_total",
        "core/record_total",
        "core/record_total",
        "core/subtract",
        "core/sum",
        "core/record_total",
        "core/record_total",
        "core/subtract",
        "core/sum",
        "core/record_total",
    ]
    assert all(step["unit"] == "ca/cad" for step in steps)
    assert not any("title" in step or "reference" in step for step in steps)


def test_every_figure_comes_in_through_a_record_total_over_an_export() -> None:
    reads = [
        step["consumes"]["records"] for step in _steps() if step["name"] == "core/record_total"
    ]

    assert reads == [
        "ca-qc/t1_tax_and_credits.refund_or_balance_owing_line_172",
        "ca-qc/tp1_totals.tp1_income_tax_and_contributions_line_450",
        "ca-qc/tp1_totals.tp1_work_premium_tax_credits_line_456",
        "ca-qc/t1_tax_and_credits.total_payable_line_151",
        "ca-qc/t1_tax_and_credits.refundable_quebec_abatement_line_156",
        "ca-qc/solidarity_credit.solidarity_credit_after_reduction",
    ]


def test_the_computing_steps_round_half_up_to_the_cent() -> None:
    steps = [step for step in _steps() if step["name"] in ("core/subtract", "core/sum")]

    assert len(steps) == 4
    assert all(step["params"] == {"rounding": "ca-qc/cent_rounding"} for step in steps)


def test_the_two_figures_are_added_with_no_floor() -> None:
    steps = {step["produces"]["output"]: step for step in _steps()}

    assert steps["ca/refund_or_balance_owing"]["consumes"] == {
        "parts": [
            "ca-qc/federal_refund_or_balance_owing_return",
            "ca-qc/tp1_income_tax_less_work_premium_return",
        ]
    }
    assert steps["ca-qc/total_payable"]["consumes"] == {
        "parts": [
            "ca-qc/federal_total_payable_less_abatement_return",
            "ca-qc/tp1_income_tax_and_contributions_return",
        ]
    }


def test_the_solidarity_credit_is_in_neither_sum() -> None:
    sums = [step for step in _steps() if step["name"] == "core/sum"]

    for step in sums:
        assert "ca-qc/solidarity_credit" not in step["consumes"]["parts"]


@pytest.mark.parametrize(
    ("identifier", "non_negative"),
    [
        ("ca-qc/total_payable", False),
        ("ca-qc/solidarity_credit", True),
        ("ca-qc/federal_refund_or_balance_owing_return", False),
        ("ca-qc/tp1_income_tax_less_work_premium_return", False),
        ("ca-qc/federal_total_payable_less_abatement_return", False),
        ("ca-qc/tp1_income_tax_and_contributions_return", True),
        ("ca-qc/tp1_work_premium_tax_credits_return", True),
        ("ca-qc/federal_total_payable_return", True),
        ("ca-qc/refundable_quebec_abatement_return", True),
    ],
)
def test_the_return_kinds_are_registered_amounts_signed_where_the_figure_has_no_floor(
    identifier: str, non_negative: bool
) -> None:
    kind = quebec_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert kind.non_negative is non_negative
