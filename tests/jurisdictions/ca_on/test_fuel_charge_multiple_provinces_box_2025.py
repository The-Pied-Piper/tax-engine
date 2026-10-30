"""Form T2043 box 67062 over small sets of statements (2025 tax year).

Box 67062, "Tick this box if you have multiple farming businesses with one or more permanent
establishments in multiple provinces or territories", is 1 when there is more than one Form T2042
statement and two places each have a statement present in them. A statement is present in a place
when its designated province is that place and no Chart B is in use, or when its Chart B has a row
1 or row 4 amount for that place; outside eight is designated province code 0 with no Chart B in
use. Each case below is a small set of statements, the other inputs being 0 (Return DW's farm
figures are not repeated here; the partnership credits are 0).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    FUEL_CHARGE_FARM_STATEMENT_COUNT,
    FUEL_CHARGE_FARMS_IN_PROVINCE_MB,
    FUEL_CHARGE_FARMS_IN_PROVINCE_ON,
    FUEL_CHARGE_FARMS_OUTSIDE_EIGHT,
    FUEL_CHARGE_MULTIPLE_PROVINCES_BOX,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    CA_ON,
    D,
    service,
    starting,
)

ONTARIO = 1
MANITOBA = 2


def statement(
    *,
    wheat: str = "48250",
    seeds_and_plants: str = "18250",
    province: int = 1,
    chart_b: tuple[tuple[int, str, str], ...] = (),
    also_outside_eight: int = 0,
) -> dict[str, Any]:
    """One Form T2042 statement: `wheat` is the gross income, `seeds_and_plants` the expenses,
    `province` the designated province code, and `chart_b` the Chart B province rows (province code,
    row 1 gross income, row 4 salaries and wages). The fiscal period is 365 days, 184 in 2024."""
    return {
        "farm": {"wheat": wheat, "seeds_and_plants": seeds_and_plants},
        "farm_chart_b_provinces_rows": chart_b,
        "farm_fiscal_period_days_entered": 365,
        "farm_designated_province": province,
        "farm_days_in_2024": 184,
        "farm_also_outside_eight": also_outside_eight,
    }


def chart_b_statement(*rows: tuple[int, str, str], also_outside_eight: int = 0) -> dict[str, Any]:
    """A statement of wheat 100,000 and salaries of 30,000 (line 9659 and 9814) that uses Chart B
    for the provinces of `rows`, with designated province code 0 (Return DW's pattern)."""
    return {
        "farm": {
            "wheat": "100000",
            "seeds_and_plants": "6500",
            "salaries_wages_and_benefits": "30000",
        },
        "farm_chart_b_provinces_rows": rows,
        "farm_fiscal_period_days_entered": 365,
        "farm_designated_province": 0,
        "farm_days_in_2024": 184,
        "farm_also_outside_eight": also_outside_eight,
    }


def run(statements: Sequence[Mapping[str, Any]]) -> dict[str, tuple[Worksheet, ...]]:
    artifacts = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=tuple(statements),
        fuel_charge_partnership_credit_on="0",
        fuel_charge_partnership_credit_mb="0",
        fuel_charge_partnership_credit_sk="0",
        fuel_charge_partnership_credit_ab="0",
        fuel_charge_partnership_credit_ns="0",
        fuel_charge_partnership_credit_pe="0",
        fuel_charge_partnership_credit_nl="0",
        fuel_charge_partnership_credit_nb="0",
    )
    return service().compute(CA_ON, 2025, *artifacts)


def box(statements: Sequence[Mapping[str, Any]]) -> Any:
    (form,) = run(statements)["ca/t2043"]
    return form.get(FUEL_CHARGE_MULTIPLE_PROVINCES_BOX).value


def statement_count(statements: Sequence[Mapping[str, Any]]) -> Any:
    (form,) = run(statements)["ca/t2043"]
    return form.get(FUEL_CHARGE_FARM_STATEMENT_COUNT).value


def test_one_statement_in_two_provinces_by_chart_b_is_0_because_there_is_one_statement() -> None:
    # Chart B lists Ontario and Manitoba on one statement: two places, but only one statement.
    statements = [chart_b_statement((ONTARIO, "60000", "15000"), (MANITOBA, "40000", "15000"))]

    assert statement_count(statements) == 1
    assert box(statements) == 0


def test_one_statement_is_0() -> None:
    assert box([statement(province=ONTARIO)]) == 0


def test_no_statements_is_0() -> None:
    assert statement_count([]) == 0
    assert box([]) == 0


def test_two_statements_both_in_ontario_are_one_place_so_0() -> None:
    statements = [statement(province=ONTARIO), statement(province=ONTARIO, wheat="50000")]

    assert statement_count(statements) == 2
    assert box(statements) == 0


def test_two_statements_both_outside_the_eight_provinces_are_one_place_so_0() -> None:
    statements = [statement(province=0), statement(province=0, wheat="50000")]

    assert statement_count(statements) == 2
    assert box(statements) == 0


def test_two_statements_one_in_ontario_and_one_outside_the_eight_provinces_is_1() -> None:
    statements = [statement(province=ONTARIO), statement(province=0, wheat="50000")]

    assert statement_count(statements) == 2
    assert box(statements) == 1


@pytest.mark.parametrize(
    "statements",
    [
        [statement(province=ONTARIO), statement(province=MANITOBA)],
        [statement(province=MANITOBA), statement(province=ONTARIO)],
    ],
    ids=["ontario_first", "manitoba_first"],
)
def test_two_statements_one_in_ontario_and_one_in_manitoba_is_1_whichever_is_first(
    statements: list[dict[str, Any]],
) -> None:
    assert box(statements) == 1


def test_a_chart_b_statement_in_ontario_and_manitoba_with_a_second_ontario_statement_is_1() -> None:
    # The first statement uses Chart B for Ontario and Manitoba (two places); the second is in
    # Ontario. Two statements, and Ontario and Manitoba each have a statement present in them.
    statements = [
        chart_b_statement((ONTARIO, "60000", "15000"), (MANITOBA, "40000", "15000")),
        statement(province=ONTARIO),
    ]

    assert statement_count(statements) == 2
    assert box(statements) == 1


def test_the_place_totals_count_each_statement_present_in_each_place() -> None:
    # A Chart B statement in Ontario and Manitoba and a second statement in Ontario: Ontario has two
    # statements present, Manitoba one, and outside eight none.
    statements = [
        chart_b_statement((ONTARIO, "60000", "15000"), (MANITOBA, "40000", "15000")),
        statement(province=ONTARIO),
    ]
    (form,) = run(statements)["ca/t2043"]

    assert form.get(FUEL_CHARGE_FARMS_IN_PROVINCE_ON).value == D("2")
    assert form.get(FUEL_CHARGE_FARMS_IN_PROVINCE_MB).value == D("1")
    assert form.get(FUEL_CHARGE_FARMS_OUTSIDE_EIGHT).value == D("0")


def test_a_chart_b_statement_in_ontario_also_outside_the_eight_with_an_ontario_statement_is_1() -> (
    None
):
    # Return DW: the first statement is Ontario $60,000 of $100,000 plus a share outside the eight
    # (Quebec), the second is Ontario only: outside eight is now a second place.
    statements = [
        chart_b_statement((ONTARIO, "60000", "15000"), also_outside_eight=1),
        statement(province=ONTARIO),
    ]
    (form,) = run(statements)["ca/t2043"]

    assert statement_count(statements) == 2
    assert box(statements) == 1
    assert form.get(FUEL_CHARGE_FARMS_IN_PROVINCE_ON).value == D("2")
    assert form.get(FUEL_CHARGE_FARMS_OUTSIDE_EIGHT).value == D("1")


def test_a_chart_b_statement_in_ontario_not_also_outside_the_eight_with_an_ontario_one_is_0() -> (
    None
):
    statements = [
        chart_b_statement((ONTARIO, "60000", "15000"), also_outside_eight=0),
        statement(province=ONTARIO),
    ]

    assert box(statements) == 0


def test_one_chart_b_statement_also_outside_the_eight_is_0_because_there_is_one_statement() -> None:
    assert box([chart_b_statement((ONTARIO, "60000", "15000"), also_outside_eight=1)]) == 0


def test_two_ontario_statements_one_also_outside_the_eight_is_1() -> None:
    statements = [statement(province=ONTARIO, also_outside_eight=1), statement(province=ONTARIO)]

    assert box(statements) == 1


def test_an_also_outside_the_eight_answer_above_1_is_refused() -> None:
    statements = [statement(province=ONTARIO, also_outside_eight=2), statement(province=ONTARIO)]

    with pytest.raises(InputAboveBoundError):
        run(statements)
