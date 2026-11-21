"""Revenu Quebec Schedule K (TP-1.D.K-V, 2025-12), Part A, line 48, as the Quebec take-home manifest
wires it. Printed as "Subtract line 46 from line 40. If the result is negative, enter 0. In this
case, you do not have to pay a premium. Income used to calculate the premium".

`core/subtract_not_below_zero` takes line 46 from line 40, rounded half-up to the cent by
`ca-qc/cent_rounding`. The real Schedule K chain (lines 36 to 46) is composed under a test-local
header and form declaration, and the real form declaration is checked on its own: it exports line
48. The expected figures are hand-computed from the printed lines, not an official example.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
import yaml

from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_K_DEPENDENT_CHILDREN_LINE_44,
    SCHEDULE_K_PREMIUM_INCOME_LINE_48,
    TP1_SPOUSE_NET_INCOME_LINE_275,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_k_support import FORM_NAME, schedule_k_sheet
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

D = Decimal
LINE_48 = "ca-qc/schedule_k_premium_income_line_48"
PARTS = (
    "tp1_schedule_k_line_36.yaml",
    "tp1_schedule_k_line_37.yaml",
    "tp1_schedule_k_line_40.yaml",
    "tp1_schedule_k_line_41.yaml",
    "tp1_schedule_k_line_44_input.yaml",
    "tp1_schedule_k_line_44_amounts.yaml",
    "tp1_schedule_k_line_44.yaml",
    "tp1_schedule_k_line_46.yaml",
    "tp1_schedule_k_line_48.yaml",
)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "0.00"), ("70000", "48025.00"), ("200000", "177616.00")],
)
def test_line_48_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = schedule_k_sheet(take_home_service, salary, LINE_48, PARTS)

    assert str(sheet.get(SCHEDULE_K_PREMIUM_INCOME_LINE_48).value) == expected


def test_the_spouse_amount_raises_line_48(take_home_service: TakeHomeService) -> None:
    given = (TP1_SPOUSE_NET_INCOME_LINE_275, "1000.50")
    sheet = schedule_k_sheet(take_home_service, "70000", LINE_48, PARTS, given)

    assert str(sheet.get(SCHEDULE_K_PREMIUM_INCOME_LINE_48).value) == "49025.50"


@pytest.mark.parametrize(("children", "expected"), [("1", "35675.00"), ("2", "31455.00")])
def test_a_dependent_child_lowers_line_48(
    take_home_service: TakeHomeService, children: str, expected: str
) -> None:
    given = (SCHEDULE_K_DEPENDENT_CHILDREN_LINE_44, children)
    sheet = schedule_k_sheet(take_home_service, "70000", LINE_48, PARTS, given)

    assert str(sheet.get(SCHEDULE_K_PREMIUM_INCOME_LINE_48).value) == expected


def test_a_negative_result_is_entered_as_zero(take_home_service: TakeHomeService) -> None:
    """At $20,000, line 40 is 18,635.00 and line 46 is 19,890.00: the result is -1,255.00, so 0."""
    sheet = schedule_k_sheet(take_home_service, "20000", LINE_48, PARTS)

    assert str(sheet.get(SCHEDULE_K_PREMIUM_INCOME_LINE_48).value) == "0.00"


def test_the_part_is_one_subtraction_of_line_46_from_line_40() -> None:
    part = yaml.safe_load((QUEBEC_PARTS / "tp1_schedule_k_line_48.yaml").read_text("utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "title": "Income used to calculate the premium",
        "reference": "48",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {
            "amount": "ca-qc/schedule_k_income_line_40",
            "less": "ca-qc/schedule_k_total_line_46",
        },
        "produces": {"output": LINE_48},
    }


def test_the_form_declaration_exports_line_48() -> None:
    declaration = yaml.safe_load((QUEBEC_PARTS / "tp1_schedule_k.yaml").read_text("utf-8"))

    assert declaration["form"]["name"] == FORM_NAME
    assert LINE_48 in declaration["form"]["exports"]


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = quebec_kinds().kind(LINE_48)

    assert kind is SCHEDULE_K_PREMIUM_INCOME_LINE_48
    assert non_negative(kind)
