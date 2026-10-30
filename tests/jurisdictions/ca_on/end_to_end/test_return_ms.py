"""CA-ON 2025 end to end: return ms, Form T1139 "Reconciliation of 2025 Business Income for Tax
Purposes" as its own form, and its amount G or L in place of the statements' line 9946 on T1 lines
13500 to 14300.

The worked return `returns/2025_return_ms.yaml` (Return BB's business with a Form T1139 whose last
year's additional business income cancels this year's) is checked by `test_worked_returns.py`. This
module computes the examples of the form: Karim's, amounts A of 45,000.00 with 275 of 365 days
(formula B, formula C, the designated amount, last year's form), Part 5 (amounts H and I) and the
refusals. The row form `ca/t1139` runs once for each business listed and the summary form
`ca/t1139_return` once, for the five lines of the return.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import pytest

from tax_engine.domain.errors import InputAboveBoundError, InputOutOfRangeError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    BUSINESS_INCOME,
    COMMISSION_INCOME,
    FARMING_INCOME,
    FISHING_INCOME,
    PROFESSIONAL_INCOME,
    T1139_AMOUNT_2C,
    T1139_AMOUNT_2D,
    T1139_AMOUNT_3H,
    T1139_AMOUNT_A,
    T1139_AMOUNT_B,
    T1139_AMOUNT_C,
    T1139_AMOUNT_D,
    T1139_AMOUNT_E,
    T1139_AMOUNT_G,
    T1139_AMOUNT_H,
    T1139_AMOUNT_I,
    T1139_AMOUNT_J,
    T1139_AMOUNT_L,
    T1139_BUSINESS_INCOME_ON_RETURN,
    T1139_COMMISSION_INCOME_ON_RETURN,
    T1139_PROFESSIONAL_INCOME_ON_RETURN,
    T1139_REPLACED_ON_BUSINESS_LINE,
    T1139_REPORTED_ON_BUSINESS_LINE,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    CA_ON,
    D,
    routed_statement,
    service,
    starting,
)

T1139 = "ca/t1139"
T1139_RETURN = "ca/t1139_return"
RETURN = "ca-on/return"

# Karim's example (Form T1139 page 6): a net income of 45,000.00 for the fiscal period ending in
# 2025, 275 of its 365 days after it.
KARIM = {"line": 1, "formula": 1, "a": (1,), "2e": "275", "2f": "365"}


def run(
    businesses: Iterable[Mapping[str, Any]] = (KARIM,),
    statements: tuple[Mapping[str, Any], ...] = (routed_statement("45000", 1),),
    **starting_kwargs: Any,
) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of a return with the statements given (by default Karim's one
    business statement of 45,000.00) and the Forms T1139 given, and no other income."""
    artifacts = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=tuple(statements),
        t1139_businesses=list(businesses),
        **starting_kwargs,
    )
    return service().compute(CA_ON, 2025, *artifacts)


def form(**overrides: Any) -> Worksheet:
    """The worksheet of Karim's one Form T1139, with `overrides` on its entered figures."""
    (worksheet,) = run([{**KARIM, **overrides}])[T1139]
    return worksheet


def lines(**overrides: Any) -> Worksheet:
    """The summary form's worksheet, which gives the five lines of the return."""
    (worksheet,) = run([{**KARIM, **overrides}])[T1139_RETURN]
    return worksheet


def return_form(businesses: Iterable[Mapping[str, Any]] = (KARIM,), **kwargs: Any) -> Worksheet:
    (worksheet,) = run(businesses, **kwargs)[RETURN]
    return worksheet


# --- formula B (Part 2, a fiscal period ending in 2025) -------------------------------------------


def test_formula_b_gives_33904_11_for_45000_over_275_of_365_days() -> None:
    worksheet = form()

    assert worksheet.get(T1139_AMOUNT_A).value == D("45000.00")
    assert worksheet.get(T1139_AMOUNT_2C).value == D("0")
    assert worksheet.get(T1139_AMOUNT_2D).value == D("45000.00")
    assert worksheet.get(T1139_AMOUNT_B).value == D("33904.11")


def test_amount_g_adds_amount_d_to_amount_a_and_t1_line_13500_takes_it() -> None:
    worksheet = form()

    assert worksheet.get(T1139_AMOUNT_D).value == D("33904.11")
    assert worksheet.get(T1139_AMOUNT_E).value == D("78904.11")
    assert worksheet.get(T1139_AMOUNT_G).value == D("78904.11")
    assert worksheet.get(T1139_REPORTED_ON_BUSINESS_LINE).value == D("78904.11")
    assert worksheet.get(T1139_REPLACED_ON_BUSINESS_LINE).value == D("45000.00")
    assert lines().get(T1139_BUSINESS_INCOME_ON_RETURN).value == D("78904.11")
    assert return_form().get(BUSINESS_INCOME).value == D("78904.11")
    assert return_form().get(TOTAL_INCOME).value == D("78904.11")


def test_last_years_additional_business_income_is_taken_off_amount_e() -> None:
    worksheet = form(last_year="33904.11")

    assert worksheet.get(T1139_AMOUNT_E).value == D("78904.11")
    assert worksheet.get(T1139_AMOUNT_G).value == D("45000.00")
    assert return_form([{**KARIM, "last_year": "33904.11"}]).get(BUSINESS_INCOME).value == D(
        "45000.00"
    )


def test_the_capital_gains_deduction_limits_what_is_taken_off_amount_a() -> None:
    # 2A 10,000.00 of capital gains in amount A, 2B deduction 4,000.00: 2C is the lesser, 4,000.00,
    # so amount 2D is 41,000.00 and amount B is 41,000.00 x 275 / 365 = 30,890.41.
    worksheet = form(**{"2a": "10000", "2b": "4000"})

    assert worksheet.get(T1139_AMOUNT_2C).value == D("4000.00")
    assert worksheet.get(T1139_AMOUNT_2D).value == D("41000.00")
    assert worksheet.get(T1139_AMOUNT_B).value == D("30890.41")


def test_a_negative_result_of_the_formula_is_additional_income_of_zero() -> None:
    # A loss of 5,000.00 in the period: the formula's negative result is 0 for amount D.
    result = run(
        [KARIM],
        statements=({"business": {"gross_sales": "0", "office_expenses": "5000"}},),
    )
    (worksheet,) = result[T1139]

    assert worksheet.get(T1139_AMOUNT_A).value == D("-5000.00")
    assert worksheet.get(T1139_AMOUNT_D).value == D("0")
    assert worksheet.get(T1139_AMOUNT_G).value == D("-5000.00")


# --- formula C (Part 2, a business that started in 2025) ------------------------------------------


def test_formula_c_gives_33904_11_for_an_estimated_45000_over_275_of_365_days() -> None:
    worksheet = form(a=(), formula=2, **{"2h": "45000", "2m": "275", "2n": "365"})

    assert worksheet.get(T1139_AMOUNT_C).value == D("33904.11")
    assert worksheet.get(T1139_AMOUNT_D).value == D("33904.11")


def test_the_designated_amount_replaces_formula_c_when_it_is_less() -> None:
    worksheet = form(
        a=(),
        formula=2,
        designates=1,
        designated="20000",
        **{"2h": "45000", "2m": "275", "2n": "365"},
    )

    assert worksheet.get(T1139_AMOUNT_C).value == D("20000.00")
    assert worksheet.get(T1139_AMOUNT_D).value == D("20000.00")


def test_a_designated_amount_above_the_formula_is_not_used() -> None:
    worksheet = form(
        a=(),
        formula=2,
        designates=1,
        designated="50000",
        **{"2h": "45000", "2m": "275", "2n": "365"},
    )

    assert worksheet.get(T1139_AMOUNT_C).value == D("33904.11")


# --- the formula used (Part 2 "Use only one of the formulas below") and Part 3 -----------------


def test_only_the_formula_used_counts_and_the_boxes_of_the_others_are_ignored() -> None:
    # Formula B chosen with the boxes of formula C filled too (2H 45,000.00, 2M 275, 2N 365): D is
    # amount B, 33,904.11, and amount C is not added.
    worksheet = form(**{"2h": "45000", "2m": "275", "2n": "365"})

    assert worksheet.get(T1139_AMOUNT_B).value == D("33904.11")
    assert worksheet.get(T1139_AMOUNT_C).value == D("33904.11")
    assert worksheet.get(T1139_AMOUNT_D).value == D("33904.11")
    assert worksheet.get(T1139_AMOUNT_G).value == D("78904.11")


def test_with_no_formula_used_amount_d_is_0_so_amount_g_is_amount_a() -> None:
    worksheet = form(formula=0)

    assert worksheet.get(T1139_AMOUNT_D).value == D("0")
    assert worksheet.get(T1139_AMOUNT_G).value == D("45000.00")


def test_part_3_gives_amount_3h_as_amount_d_for_the_death_of_a_proprietor() -> None:
    # Amount A 45,000.00, 3A and 3B 0, 275 of 365 days up to the date of death: 3D 45,000.00 and
    # 3H = 45,000.00 x 275 / 365 = 33,904.11.
    worksheet = form(formula=3, **{"3e": "275", "3f": "365"})

    assert worksheet.get(T1139_AMOUNT_3H).value == D("33904.11")
    assert worksheet.get(T1139_AMOUNT_D).value == D("33904.11")
    assert worksheet.get(T1139_AMOUNT_G).value == D("78904.11")


def test_a_formula_number_above_3_is_refused() -> None:
    with pytest.raises(InputOutOfRangeError):
        run([{**KARIM, "formula": 4}])


def test_a_line_number_outside_1_to_5_is_refused() -> None:
    for line in (0, 6):
        with pytest.raises(InputOutOfRangeError):
            run([{**KARIM, "line": line}])


# --- the farming and fishing lines ---------------------------------------------------------------


def test_the_farming_line_takes_amount_g_in_place_of_the_t2042_net_income() -> None:
    # One T2042 statement of 70.00 of wheat sales, half the period's days after it: B = 35.00.
    businesses = [{"line": 4, "formula": 1, "a": (1,), "2e": "1", "2f": "2"}]
    result = run(businesses, statements=(), farm_statements=({"farm": {"wheat": "70"}},))

    assert result[RETURN][0].get(FARMING_INCOME).value == D("105.00")


def test_the_fishing_line_takes_amount_g_in_place_of_the_t2121_net_income() -> None:
    businesses = [{"line": 5, "formula": 1, "a": (1,), "2e": "1", "2f": "2"}]
    result = run(businesses, statements=(), fish_statements=({"fish": {"fish_products": "50"}},))

    assert result[RETURN][0].get(FISHING_INCOME).value == D("75.00")


# --- Part 5 (changing back to a fiscal period ending on December 31) -----------------------------


def test_part_5_adds_amounts_h_and_i_and_takes_off_last_years_amount() -> None:
    statements = (routed_statement("45000", 1), routed_statement("30000", 1))
    businesses = [{"line": 1, "h": (1,), "i": (2,), "cancelling": 1}]
    (worksheet,) = run(businesses, statements=statements)[T1139]

    assert worksheet.get(T1139_AMOUNT_H).value == D("45000.00")
    assert worksheet.get(T1139_AMOUNT_I).value == D("30000.00")
    assert worksheet.get(T1139_AMOUNT_J).value == D("75000.00")
    assert worksheet.get(T1139_AMOUNT_L).value == D("75000.00")
    assert return_form(businesses, statements=statements).get(BUSINESS_INCOME).value == D(
        "75000.00"
    )


# --- the lines of the return ----------------------------------------------------------------------


def test_the_line_of_the_business_picks_the_line_of_the_return() -> None:
    professional = {**KARIM, "line": 2}
    result = run([professional], statements=(routed_statement("45000", 2),))
    (summary,) = result[T1139_RETURN]

    assert summary.get(T1139_PROFESSIONAL_INCOME_ON_RETURN).value == D("78904.11")
    assert summary.get(T1139_BUSINESS_INCOME_ON_RETURN).value == D("0")
    (worksheet,) = result[RETURN]
    assert worksheet.get(PROFESSIONAL_INCOME).value == D("78904.11")


def test_a_statement_no_form_takes_the_place_of_stays_on_its_line() -> None:
    # Two business statements, the form names the first: the second one's 10,000.00 stays.
    statements = (routed_statement("45000", 1), routed_statement("10000", 1))
    worksheet = return_form(statements=statements)

    assert worksheet.get(BUSINESS_INCOME).value == D("88904.11")


def test_other_lines_are_the_statements_as_before() -> None:
    statements = (routed_statement("45000", 1), routed_statement("7000", 3))
    worksheet = return_form(statements=statements)

    assert worksheet.get(BUSINESS_INCOME).value == D("78904.11")
    assert worksheet.get(COMMISSION_INCOME).value == D("7000.00")
    (summary,) = run([KARIM], statements=statements)[T1139_RETURN]
    assert summary.get(T1139_COMMISSION_INCOME_ON_RETURN).value == D("7000.00")


def test_with_no_form_the_lines_are_the_statements_line_9946() -> None:
    result = run([])

    assert result[T1139] == ()
    assert return_form([]).get(BUSINESS_INCOME).value == D("45000.00")


# --- the refusals ---------------------------------------------------------------------------------


def test_a_position_beyond_the_statements_of_the_line_is_refused() -> None:
    with pytest.raises(InputOutOfRangeError):
        run([{**KARIM, "a": (2,)}])


def test_a_statement_named_twice_is_refused() -> None:
    with pytest.raises(InputOutOfRangeError):
        run([{**KARIM, "a": (1, 1)}])


def test_a_designating_answer_above_1_is_refused_and_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        run([{**KARIM, "designates": 2}])


def test_a_cancelling_answer_above_1_is_refused_and_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        run([{**KARIM, "cancelling": 2}])
