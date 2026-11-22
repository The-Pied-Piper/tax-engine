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
- TP-1 line 450 "Add lines 432 through 447. Income tax and contributions" (Revenu Quebec
  TP-1.D-V (2025-12), page 5);
- TP-1 line 470 "Subtract line 468 from line 450" (page 5), which already takes the work premium
  (456), the QPIP overpayment (457) and every credit typed on lines 451.2 to 466 off line 450. Tax
  withheld (line 451) is left out of the take-home by ruling and is not on line 468.

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
    FEDERAL_REFUND_OR_BALANCE_OWING_RETURN,
    FEDERAL_TOTAL_PAYABLE_LESS_ABATEMENT_RETURN,
    FEDERAL_TOTAL_PAYABLE_RETURN,
    REFUNDABLE_QUEBEC_ABATEMENT_RETURN,
    SCHEDULE_B_LIVED_ALONE_LINE_20,
    SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50,
    SOLIDARITY_CREDIT,
    SOLIDARITY_LIVED_ALONE_LINE_12,
    SOLIDARITY_TENANT_OR_OWNER_LINES_32_36,
    TOTAL_PAYABLE,
    TP1_FINANCIAL_COMPENSATION_LINE_466,
    TP1_INCOME_TAX_AND_CONTRIBUTIONS_RETURN,
    TP1_LINE_451_2,
    TP1_LINE_452,
    TP1_LINE_462,
    TP1_LINE_470_RETURN,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.return_support import EXPECTED, RETURN_PART, return_sheet
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_totals_support import SALARIES

D = Decimal


# The default answers: every printed figure and each step's figure at the three salaries and at
# $3,000 (a salary below the credits, where the refund survives with no floor). Each row: salary,
# refund or balance owing, total payable, solidarity credit.
DEFAULT_FIGURES = [
    ("3000", "-293.40", "0.00", "363.00"),
    ("20000", "-3135.08", "128.01", "363.00"),
    ("70000", "14678.32", "14678.32", "0.00"),
    ("200000", "71643.79", "71643.79", "0.00"),
]
LESS_ABATEMENT = {"20000": "119.05", "70000": "6282.16", "200000": "32886.26"}


@pytest.mark.parametrize(
    ("salary", "refund_or_balance", "total_payable", "solidarity"), DEFAULT_FIGURES
)
def test_the_three_outputs_at_the_default_answers(
    take_home_service: TakeHomeService,
    salary: str,
    refund_or_balance: str,
    total_payable: str,
    solidarity: str,
) -> None:
    sheet = return_sheet(take_home_service, salary)

    assert str(sheet.get(REFUND_OR_BALANCE_OWING).value) == refund_or_balance
    assert str(sheet.get(TOTAL_PAYABLE).value) == total_payable
    assert str(sheet.get(SOLIDARITY_CREDIT).value) == solidarity


@pytest.mark.parametrize("salary", SALARIES)
def test_each_printed_line_is_read_as_the_form_prints_it(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = return_sheet(take_home_service, salary)
    figures = EXPECTED[salary]

    assert str(sheet.get(FEDERAL_REFUND_OR_BALANCE_OWING_RETURN).value) == figures["172"]
    assert str(sheet.get(FEDERAL_TOTAL_PAYABLE_RETURN).value) == figures["43500"]
    assert str(sheet.get(REFUNDABLE_QUEBEC_ABATEMENT_RETURN).value) == figures["44000"]
    assert str(sheet.get(TP1_INCOME_TAX_AND_CONTRIBUTIONS_RETURN).value) == figures["450"]
    assert str(sheet.get(TP1_LINE_470_RETURN).value) == figures["470"]


@pytest.mark.parametrize("salary", SALARIES)
def test_the_summary_adds_line_172_and_line_470(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = return_sheet(take_home_service, salary)

    less_abatement = sheet.get(FEDERAL_TOTAL_PAYABLE_LESS_ABATEMENT_RETURN)
    assert str(less_abatement.value) == LESS_ABATEMENT[salary]
    assert sheet.get(REFUND_OR_BALANCE_OWING).value == (
        sheet.get(FEDERAL_REFUND_OR_BALANCE_OWING_RETURN).value
        + sheet.get(TP1_LINE_470_RETURN).value
    )
    assert sheet.get(TOTAL_PAYABLE).value == (
        sheet.get(FEDERAL_TOTAL_PAYABLE_LESS_ABATEMENT_RETURN).value
        + sheet.get(TP1_INCOME_TAX_AND_CONTRIBUTIONS_RETURN).value
    )


@pytest.mark.parametrize(
    ("salary", "line_470", "refund_or_balance"),
    [("1000", "-4.94", "-4.94"), ("1999", "-9.88", "-9.88"), ("2000", "0.00", "-26.20")],
)
def test_the_qpip_overpayment_reduces_the_refund_or_balance_owing(
    take_home_service: TakeHomeService, salary: str, line_470: str, refund_or_balance: str
) -> None:
    # Line 457 refunds the premium below $2,000 of work income ($1,000 x 0.494% = $4.94). It is on
    # TP-1 line 468, so line 470 is lower by it; the total payable (lines 43500, 44000 and 450) is
    # not reduced by it.
    sheet = return_sheet(take_home_service, salary)

    assert str(sheet.get(TP1_LINE_470_RETURN).value) == line_470
    assert str(sheet.get(REFUND_OR_BALANCE_OWING).value) == refund_or_balance
    assert sheet.get(TOTAL_PAYABLE).value == (
        sheet.get(FEDERAL_TOTAL_PAYABLE_LESS_ABATEMENT_RETURN).value
        + sheet.get(TP1_INCOME_TAX_AND_CONTRIBUTIONS_RETURN).value
    )


@pytest.mark.parametrize(
    ("line", "kind"),
    [
        ("451.2", TP1_LINE_451_2),
        ("452", TP1_LINE_452),
        ("462", TP1_LINE_462),
        ("466", TP1_FINANCIAL_COMPENSATION_LINE_466),
    ],
)
def test_a_credit_typed_on_lines_451_2_to_466_moves_the_refund_or_balance_owing(
    take_home_service: TakeHomeService, line: str, kind: AmountKind
) -> None:
    # $500 on any of the optional credit lines lowers TP-1 line 470 (8,396.16 at $70,000) and so
    # the Quebec half of the summary by $500; the federal half and the total payable do not move.
    sheet = return_sheet(take_home_service, "70000", Artifact(kind, D("500")))

    assert str(sheet.get(TP1_LINE_470_RETURN).value) == "7896.16"
    assert str(sheet.get(REFUND_OR_BALANCE_OWING).value) == "14178.32"
    assert str(sheet.get(TOTAL_PAYABLE).value) == "14678.32"


@pytest.mark.parametrize(
    ("salary", "refund_or_balance", "total_payable"),
    [
        ("20000", "-3135.08", "128.01"),
        ("70000", "13923.32", "13923.32"),
        ("200000", "70888.79", "70888.79"),
    ],
)
def test_the_group_plan_case_drops_the_755_premium(
    take_home_service: TakeHomeService, salary: str, refund_or_balance: str, total_payable: str
) -> None:
    sheet = return_sheet(
        take_home_service, salary, Artifact(SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50, 1)
    )

    assert str(sheet.get(REFUND_OR_BALANCE_OWING).value) == refund_or_balance
    assert str(sheet.get(TOTAL_PAYABLE).value) == total_payable


@pytest.mark.parametrize(
    ("salary", "refund_or_balance", "total_payable", "solidarity"),
    [
        ("20000", "-3144.04", "119.05", "1281.00"),
        ("70000", "14678.32", "14678.32", "0.00"),
        ("200000", "71643.79", "71643.79", "0.00"),
    ],
)
def test_alone_and_a_tenant(
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


def test_a_tenant_answer_changes_the_solidarity_credit_only(
    take_home_service: TakeHomeService,
) -> None:
    # The housing component raises the solidarity credit; it is in neither sum, so the refund or
    # balance owing and the total payable stay at the default's figures.
    sheet = return_sheet(
        take_home_service, "20000", Artifact(SOLIDARITY_TENANT_OR_OWNER_LINES_32_36, 1)
    )

    assert str(sheet.get(REFUND_OR_BALANCE_OWING).value) == "-3135.08"
    assert str(sheet.get(TOTAL_PAYABLE).value) == "128.01"
    assert sheet.get(SOLIDARITY_CREDIT).value > D("363.00")


def _steps() -> list[dict[str, Any]]:
    part = yaml.safe_load((QUEBEC_PARTS / RETURN_PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["capabilities"]
    steps = part["capabilities"]
    assert isinstance(steps, list)
    return steps


def _read(records: str, output: str) -> dict[str, Any]:
    return {
        "name": "core/record_total",
        "unit": "ca/cad",
        "consumes": {"records": records},
        "produces": {"output": output},
    }


def _computed(name: str, consumes: dict[str, Any], output: str) -> dict[str, Any]:
    return {
        "name": name,
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": consumes,
        "produces": {"output": output},
    }


# Each step of the part, exactly, by the figure it produces: one case per step. No step carries a
# title or a reference, because the summary prints no line of its own.
STEPS = {
    "ca-qc/federal_refund_or_balance_owing_return": _read(
        "ca-qc/t1_tax_and_credits.refund_or_balance_owing_line_172",
        "ca-qc/federal_refund_or_balance_owing_return",
    ),
    "ca-qc/tp1_income_tax_and_contributions_return": _read(
        "ca-qc/tp1_totals.tp1_income_tax_and_contributions_line_450",
        "ca-qc/tp1_income_tax_and_contributions_return",
    ),
    "ca-qc/tp1_line_470_return": _read(
        "ca-qc/tp1_totals.tp1_line_470", "ca-qc/tp1_line_470_return"
    ),
    "ca/refund_or_balance_owing": _computed(
        "core/sum",
        {
            "parts": [
                "ca-qc/federal_refund_or_balance_owing_return",
                "ca-qc/tp1_line_470_return",
            ]
        },
        "ca/refund_or_balance_owing",
    ),
    "ca-qc/federal_total_payable_return": _read(
        "ca-qc/t1_tax_and_credits.total_payable_line_151",
        "ca-qc/federal_total_payable_return",
    ),
    "ca-qc/refundable_quebec_abatement_return": _read(
        "ca-qc/t1_tax_and_credits.refundable_quebec_abatement_line_156",
        "ca-qc/refundable_quebec_abatement_return",
    ),
    "ca-qc/federal_total_payable_less_abatement_return": _computed(
        "core/subtract",
        {
            "amount": "ca-qc/federal_total_payable_return",
            "less": "ca-qc/refundable_quebec_abatement_return",
        },
        "ca-qc/federal_total_payable_less_abatement_return",
    ),
    "ca-qc/total_payable": _computed(
        "core/sum",
        {
            "parts": [
                "ca-qc/federal_total_payable_less_abatement_return",
                "ca-qc/tp1_income_tax_and_contributions_return",
            ]
        },
        "ca-qc/total_payable",
    ),
    "ca-qc/solidarity_credit": _read(
        "ca-qc/solidarity_credit.solidarity_credit_after_reduction", "ca-qc/solidarity_credit"
    ),
}


def test_the_part_is_the_nine_steps_and_nothing_else() -> None:
    steps = {step["produces"]["output"]: step for step in _steps()}

    assert len(_steps()) == len(STEPS) == 9
    assert set(steps) == set(STEPS)


@pytest.mark.parametrize("output", list(STEPS))
def test_each_step_is_exactly_as_built(output: str) -> None:
    steps = {step["produces"]["output"]: step for step in _steps()}

    assert steps[output] == STEPS[output]


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
        ("ca-qc/tp1_line_470_return", False),
        ("ca-qc/federal_total_payable_less_abatement_return", False),
        ("ca-qc/tp1_income_tax_and_contributions_return", True),
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
