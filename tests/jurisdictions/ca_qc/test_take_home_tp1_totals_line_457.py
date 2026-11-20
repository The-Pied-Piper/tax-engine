"""Revenu Quebec TP-1 (2025) line 457, "QPIP overpayment", as the Quebec take-home manifest wires
it.

Guide TP-1.G-V (2025-12), line 457: "If the total of your net business income, your employment
income subject to the QPIP and your insurable earnings as a person responsible for a family-type
resource or an intermediate resource is less than $2,000, carry the amount from line 97 to line
457. If the amount on line 97 is more than $484.12, enter the overpayment (that is, the excess) on
line 457." The line is eight steps (see the part's header), none rounded, so the figure is line 97
as it is or the excess over $484.12. Line 97 is computed from the salary as 0.494% (half-up to the
cent) unless the caller gives the slip figure. The expected figures are hand-computed from the
printed lines, not an official example: 0.494% of $1,000 is $4.94.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_FAMILY_RESOURCE_EARNINGS_SCHEDULE_L_LINE_40,
    TP1_LINE_97_WITHIN_MAXIMUM_FOR_LINE_457,
    TP1_LINE_457,
    TP1_LINE_457_EXCESS,
    TP1_LINE_457_INCOME_TOTAL,
    TP1_LINE_457_MAXIMUM_PREMIUM,
    TP1_LINE_457_UNDER_THRESHOLD_COUNT,
    TP1_NET_BUSINESS_INCOME_SCHEDULE_L_LINE_27,
    TP1_QPIP_PREMIUM_GIVEN_LINE_97,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_totals_support import (
    FORM,
    LINE_457_PARTS,
    totals_form,
    totals_sheet,
)

D = Decimal
ZERO = D("0")
PART = "tp1_totals_line_457.yaml"
IDENTIFIER = "ca-qc/tp1_line_457"


def _line_457(take_home_service: TakeHomeService, salary: str, *given: Artifact[Any]) -> Decimal:
    sheet = totals_sheet(take_home_service, salary, totals_form(IDENTIFIER), LINE_457_PARTS, *given)
    return sheet.get(TP1_LINE_457).value


@pytest.mark.parametrize(
    ("salary", "line_457"),
    [
        ("1", "0.00"),
        ("500", "2.47"),
        ("1000", "4.94"),
        ("1469", "7.26"),
        ("1999", "9.88"),
        ("1999.99", "9.88"),
        # $2,000 is not "less than $2,000": the premium is not refunded.
        ("2000", "0.00"),
        ("2000.01", "0.00"),
        ("20000", "0.00"),
        ("70000", "0.00"),
        ("200000", "0.00"),
    ],
)
def test_line_457_refunds_the_premium_when_the_total_is_under_2000(
    take_home_service: TakeHomeService, salary: str, line_457: str
) -> None:
    assert _line_457(take_home_service, salary) == D(line_457)


@pytest.mark.parametrize(
    ("kind", "amount", "line_457"),
    [
        (TP1_NET_BUSINESS_INCOME_SCHEDULE_L_LINE_27, "999.99", "4.94"),
        (TP1_NET_BUSINESS_INCOME_SCHEDULE_L_LINE_27, "1000", "0"),
        (TP1_FAMILY_RESOURCE_EARNINGS_SCHEDULE_L_LINE_40, "999.99", "4.94"),
        (TP1_FAMILY_RESOURCE_EARNINGS_SCHEDULE_L_LINE_40, "1000", "0"),
    ],
)
def test_the_two_schedule_l_amounts_count_towards_the_2000(
    take_home_service: TakeHomeService, kind: AmountKind, amount: str, line_457: str
) -> None:
    # A salary of $1,000 and an amount of $1,000 make exactly $2,000: no refund.
    given = Artifact(kind, D(amount))

    assert _line_457(take_home_service, "1000", given) == D(line_457)


@pytest.mark.parametrize(
    ("salary", "given", "line_457"),
    [
        # Under $2,000 the whole of line 97 is carried, even above the maximum.
        ("1000", "500", "500"),
        # At $2,000 or more only the excess over $484.12 is.
        ("70000", "484.12", "0"),
        ("70000", "484.13", "0.01"),
        ("70000", "500", "15.88"),
        ("70000", "100", "0"),
    ],
)
def test_a_line_97_given_from_the_slips_is_carried_or_its_excess_over_484_12(
    take_home_service: TakeHomeService, salary: str, given: str, line_457: str
) -> None:
    slip = Artifact(TP1_QPIP_PREMIUM_GIVEN_LINE_97, D(given))

    assert _line_457(take_home_service, salary, slip) == D(line_457)


def test_every_step_is_traced_at_1000(take_home_service: TakeHomeService) -> None:
    sheet = totals_sheet(take_home_service, "1000", totals_form(IDENTIFIER), LINE_457_PARTS)

    assert str(sheet.get(TP1_LINE_457_INCOME_TOTAL).value) == "1000"
    assert sheet.get(TP1_LINE_457_UNDER_THRESHOLD_COUNT).value == 1
    assert str(sheet.get(TP1_LINE_457_MAXIMUM_PREMIUM).value) == "484.12"
    assert str(sheet.get(TP1_LINE_97_WITHIN_MAXIMUM_FOR_LINE_457).value) == "4.94"
    assert sheet.get(TP1_LINE_457_EXCESS).value == ZERO
    assert str(sheet.get(TP1_LINE_457).value) == "4.94"


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def _read(records: str, output: str) -> dict[str, object]:
    return {
        "name": "core/record_total",
        "unit": "ca/cad",
        "consumes": {"records": records},
        "produces": {"output": output},
    }


def test_the_part_is_the_eight_steps_of_line_457() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    assert part["capabilities"] == [
        _read("ca-qc/tp1_income.employment_income", "ca-qc/tp1_employment_income_for_line_457"),
        _read(
            "ca-qc/tp1_income.tp1_qpip_premium_line_97",
            "ca-qc/tp1_line_97_for_line_457",
        ),
        {
            "name": "core/sum",
            "title": "Employment income, net business income and family-resource earnings added up",
            "unit": "ca/cad",
            "params": {"rounding": "ca-qc/exact_rounding"},
            "consumes": {
                "parts": [
                    "ca-qc/tp1_employment_income_for_line_457",
                    "ca-qc/tp1_net_business_income_schedule_l_line_27",
                    "ca-qc/tp1_family_resource_earnings_schedule_l_line_40",
                ]
            },
            "blank": {
                "ca-qc/tp1_net_business_income_schedule_l_line_27": "0",
                "ca-qc/tp1_family_resource_earnings_schedule_l_line_40": "0",
            },
            "produces": {"output": "ca-qc/tp1_line_457_income_total"},
        },
        {
            "name": "ca/count_by_conditions",
            "title": "The total is less than $2,000",
            "params": {"conditions": "ca-qc/tp1_line_457_conditions"},
            "consumes": {"counts": [], "amounts": ["ca-qc/tp1_line_457_income_total"]},
            "produces": {"output": "ca-qc/tp1_line_457_under_threshold_count"},
        },
        {
            "name": "core/credit_amount",
            "unit": "ca/cad",
            "params": {"amount": "ca-qc/tp1_line_457_maximum_premium"},
            "produces": {"output": "ca-qc/tp1_line_457_maximum_premium"},
        },
        {
            "name": "core/lesser_of",
            "title": "QPIP premium up to the maximum",
            "unit": "ca/cad",
            "consumes": {
                "amounts": [
                    "ca-qc/tp1_line_97_for_line_457",
                    "ca-qc/tp1_line_457_maximum_premium",
                ]
            },
            "produces": {"output": "ca-qc/tp1_line_97_within_maximum_for_line_457"},
        },
        {
            "name": "core/subtract",
            "title": "QPIP premium above the maximum",
            "unit": "ca/cad",
            "params": {"rounding": "ca-qc/exact_rounding"},
            "consumes": {
                "amount": "ca-qc/tp1_line_97_for_line_457",
                "less": "ca-qc/tp1_line_97_within_maximum_for_line_457",
            },
            "produces": {"output": "ca-qc/tp1_line_457_excess"},
        },
        {
            "name": "core/choose_by_count",
            "title": "QPIP overpayment",
            "reference": "457",
            "unit": "ca/cad",
            "consumes": {
                "count": "ca-qc/tp1_line_457_under_threshold_count",
                "when_none": "ca-qc/tp1_line_457_excess",
                "when_any": "ca-qc/tp1_line_97_for_line_457",
            },
            "produces": {"output": IDENTIFIER},
        },
    ]


@pytest.mark.parametrize(
    ("identifier", "kind_class"),
    [
        ("ca-qc/tp1_line_457", AmountKind),
        ("ca-qc/tp1_line_457_under_threshold_count", CountKind),
        ("ca-qc/tp1_line_457_income_total", AmountKind),
        ("ca-qc/tp1_line_457_excess", AmountKind),
    ],
)
def test_the_kinds_are_registered_and_non_negative(
    identifier: str, kind_class: type[AmountKind] | type[CountKind]
) -> None:
    kind = quebec_kinds().kind(identifier)

    assert kind is not None and isinstance(kind, kind_class)
    assert kind.non_negative
