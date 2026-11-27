"""PE428 (2025) line 87, the low-income tax reduction, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26 from the text version):
Line 87: Line 81 minus line 86 (if negative, enter "0") Prince Edward Island low-income tax
reduction =

One core/subtract_not_below_zero. The printed form has no eligibility test: the arithmetic alone
gives the reduction, 350.00 up to a net income of 22,650 fading to 0 at 29,650. Line 66 is blank
for a single filer, so the instruction under line 67 to enter 0 on line 87 does not apply and the
line is calculated: 350.00 at $20,000, 0.00 at $30,000 and $70,000, and 232.50 at a net income of
25,000.00 (350.00 less 117.50). When an amount is claimed on line 66 (100.10 at $20,000) the line
is 0.00, as the form prints. Four steps, as NL428 line 104.

The test builds the engine over the real federal parts and the real parts of lines 1 to 87 through
the shared `take_home_service` fixture.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_pe
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.trace import ProductLine
from tax_engine.jurisdictions.ca_pe.catalog import PE428_LOW_INCOME_TAX_REDUCTION_LINE_87
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_87,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_87.yaml"
OUTPUT = "ca-pe/pe428_low_income_tax_reduction_line_87"
PARTS = CHAIN_87
EXPORTS = (
    "ca-pe/pe428_tax_line_67",
    "ca-pe/pe428_net_income_line_68",
    "ca-pe/pe428_uccb_repayment_line_69",
    "ca-pe/pe428_family_income_line_70",
    "ca-pe/pe428_uccb_income_line_71",
    "ca-pe/pe428_adjusted_family_income_line_72",
    "ca-pe/low_income_reduction_basic",
    "ca-pe/pe428_low_income_reductions_total_line_81",
    "ca-pe/low_income_reduction_base_amount",
    "ca-pe/pe428_income_over_base_amount_line_84",
    "ca-pe/pe428_reduction_phase_out_line_86",
    "ca-pe/pe428_low_income_tax_reduction_before_line_66_check",
    "ca-pe/pe428_amount_from_spouse_form_claimed_line_66",
    "ca-pe/pe428_line_87_line_66_gate",
    "ca-pe/pe428_low_income_tax_reduction_line_87",
)
CASES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("20000", {}, {"ca-pe/pe428_low_income_tax_reduction_line_87": "350.00"}),
    ("30000", {}, {"ca-pe/pe428_low_income_tax_reduction_line_87": "0.00"}),
    ("70000", {}, {"ca-pe/pe428_low_income_tax_reduction_line_87": "0.00"}),
    ("25217.17", {}, {"ca-pe/pe428_low_income_tax_reduction_line_87": "232.50"}),
    ("22650", {}, {"ca-pe/pe428_low_income_tax_reduction_line_87": "350.00"}),
    (
        "20000",
        {"ca-pe/pe428_amount_from_spouse_or_partner_form_line_66": "100.10"},
        {"ca-pe/pe428_low_income_tax_reduction_line_87": "0.00"},
    ),
]


def _sheet(
    take_home_service: TakeHomeService, salary: str, given: dict[str, str] | None = None
) -> Any:
    service = take_home_service(HEADER, form(*EXPORTS), *PARTS)
    return compute(service, salary, given)


@pytest.mark.parametrize(("salary", "given", "expected"), CASES)
def test_the_line_figures(
    take_home_service: TakeHomeService,
    salary: str,
    given: dict[str, str],
    expected: dict[str, str],
) -> None:
    sheet = _sheet(take_home_service, salary, given)

    for identifier, amount in expected.items():
        assert value(sheet, identifier) == D(amount)


def test_the_trace_is_the_figure_before_the_line_66_rule_times_the_gate(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "20000")
    kinds = prince_edward_island_kinds()

    (line,) = [
        t for t in sheet.trace if isinstance(t, ProductLine) and t.output is kinds.kind(OUTPUT)
    ]
    assert (
        line.multiplicand.identifier == "ca-pe/pe428_low_income_tax_reduction_before_line_66_check"
    )
    assert line.multiplicand_amount == D("350.00")
    assert line.multiplier.identifier == "ca-pe/pe428_line_87_line_66_gate"
    assert line.multiplier_amount == D("1")
    assert line.result == D("350.00")


def _part() -> dict[str, Any]:
    part = yaml.safe_load((PE_PARTS / PART_NAME).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-pe/pe428"}
    return part


def test_the_part_is_the_steps_the_form_prints() -> None:
    assert _part()["capabilities"] == [
        {
            "name": "core/subtract_not_below_zero",
            "title": "Low-income tax reduction before the line 66 rule",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "amount": "ca-pe/pe428_low_income_reductions_total_line_81",
                "less": "ca-pe/pe428_reduction_phase_out_line_86",
            },
            "produces": {"output": "ca-pe/pe428_low_income_tax_reduction_before_line_66_check"},
        },
        {
            "name": "core/sum",
            "title": (
                "Amount from your spouse or common-law partner's Form PE428, "
                "with a blank counted as 0"
            ),
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {"parts": ["ca-pe/pe428_amount_from_spouse_or_partner_form_line_66"]},
            "blank": {"parts": "0"},
            "produces": {"output": "ca-pe/pe428_amount_from_spouse_form_claimed_line_66"},
        },
        {
            "name": "core/amount_by_band",
            "title": "Multiplier that is 0 when you claim an amount from your spouse or common-law "
            "partner's Form PE428",
            "unit": "ca/cad",
            "params": {"table": "ca-pe/low_income_reduction_line_66_gate"},
            "consumes": {"base": "ca-pe/pe428_amount_from_spouse_form_claimed_line_66"},
            "produces": {"output": "ca-pe/pe428_line_87_line_66_gate"},
        },
        {
            "name": "core/multiply",
            "title": "Prince Edward Island low-income tax reduction",
            "reference": "87",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "multiplicand": "ca-pe/pe428_low_income_tax_reduction_before_line_66_check",
                "multiplier": "ca-pe/pe428_line_87_line_66_gate",
            },
            "produces": {"output": "ca-pe/pe428_low_income_tax_reduction_line_87"},
        },
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind(OUTPUT)

    assert kind is PE428_LOW_INCOME_TAX_REDUCTION_LINE_87
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
