"""CA-ON 2025 end to end: return hi, Form T777 employment expenses and T1 line 22900.

The worked return `returns/2025_return_hi.yaml` (T777 lines 4, 15 and 17 with one RC359 copy) is
checked by `test_worked_returns.py`. This module computes each example of the ticket on its own:
Form T777's own lines (`ca/t777`, run once) and its labour mobility copies
(`ca/t777_relocation`, one for each relocation), and T1 line 22900 "Other employment expenses"
(the total of T777 line 17 and the RC359 line 7 total), read by the medical supplement and by T691
Part 1 line 77.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    AMT_OFFICE_EXPENSES_ADJUSTMENT,
    MEDICAL_SUPPLEMENT_EMPLOYMENT_DEDUCTIONS,
    OTHER_EMPLOYMENT_EXPENSES,
    RC359_EXCESS_EPSP_TOTAL,
    REFUND_OR_BALANCE_OWING,
    SPECIAL_TAXES,
    T777_LINE_3,
    T777_LINE_4,
    T777_LINE_9,
    T777_LINE_11,
    T777_LINE_15,
    T777_LINE_16,
    T777_LINE_17,
    T777_RELOCATION_CARRIED_FORWARD,
    T777_RELOCATION_CARRIED_FORWARD_OUT,
    T777_RELOCATION_CLAIM,
    T777_RELOCATION_DEDUCTION,
    T777_RELOCATION_INCOME_LIMIT,
    T777_RELOCATION_LODGING,
    T777_RELOCATION_MEALS,
    T777_RELOCATION_TOTAL,
    T777_RELOCATION_TRADESPERSON_INCOME,
    T777_RELOCATION_TRANSPORTATION,
    T777_VEHICLE_EMPLOYMENT_USE,
    T777_VEHICLE_TOTAL_EXPENSES,
    T777_WORK_SPACE_CARRIED_FORWARD_OUT,
    T777_WORK_SPACE_EMPLOYMENT_INCOME,
    T777_WORK_SPACE_EMPLOYMENT_OFFSETS,
    T777_WORK_SPACE_EXPENSES,
    T777_WORK_SPACE_INCOME_LIMIT,
    T777_WORK_SPACE_TOTAL_AMOUNT,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting
from tests.jurisdictions.ca_on.end_to_end.test_return_dj import EMPLOYER_A, employer

# The Form T777 kinds the copies and the form read, named as the caller gives them (the keys of
# `t777` are the names after `ca/t777_`).
FOOD = "food_beverages_entertainment"
OFFICE = "office_supplies"
TOOLS = "tradespersons_tools"
KILOMETRES = "employment_kilometres"
TOTAL_KILOMETRES = "total_kilometres"
FUEL = "vehicle_fuel"
MAINTENANCE = "vehicle_maintenance"
INSURANCE = "vehicle_insurance"
ALLOWANCES = "vehicle_allowances"
ELECTRICITY = "work_space_electricity_heat_water_internet"
WORK_SPACE_OTHER = "work_space_other_expenses"
WORK_SPACE_USE = "work_space_employment_use_amount"


def run_hi(
    *,
    employment: str = "0",
    t777: dict[str, str] | None = None,
    relocations: tuple[dict[Any, Any], ...] = (),
    copies: tuple[dict[Any, Any], ...] = (),
) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of return HI, with the employment income, the Form T777 figures, the
    labour mobility relocations and the RC359 copies given (none given: none, as the return has
    none)."""
    artifacts = starting(
        employment,
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        t777_amounts=t777,
        t777_relocations=relocations,
        rc359_employers=copies,
    )
    return service().compute(CA_ON, 2025, *artifacts)


def t777_form(*, employment: str = "0", **amounts: str) -> Worksheet:
    """The one worksheet of Form T777 with the figures given (keyword names are the names after
    `ca/t777_`, with the `t777` figures of `run_hi`) on a return with `employment` of income."""
    run = run_hi(employment=employment, t777=dict(amounts))
    (form,) = run["ca/t777"]
    return form


def relocation(
    *,
    carried: str = "0",
    transportation: str = "0",
    meals: str = "0",
    lodging: str = "0",
    income: str = "0",
    claim: str = "0",
) -> dict[Any, Any]:
    """One record of `ca/t777_relocations`: the Form T777 line 33 to 36 expenses, the employment
    income of line 38 and the amount claimed of line 39."""
    return {
        T777_RELOCATION_CARRIED_FORWARD: D(carried),
        T777_RELOCATION_TRANSPORTATION: D(transportation),
        T777_RELOCATION_MEALS: D(meals),
        T777_RELOCATION_LODGING: D(lodging),
        T777_RELOCATION_TRADESPERSON_INCOME: D(income),
        T777_RELOCATION_CLAIM: D(claim),
    }


# --- Form T777 page 1 and the return's line 22900 -----------------------------------------------


def test_food_of_400_is_line_4_of_200_and_office_supplies_of_300_give_line_17_of_500() -> None:
    # Acceptance: food 400 (line 4 = 200.00) and office supplies 300, nothing else: line 15 =
    # 500.00, line 17 = 500.00 and line 22900 = 500.00.
    run = run_hi(t777={FOOD: "400", OFFICE: "300"})

    (form,) = run["ca/t777"]
    assert form.get(T777_LINE_4).value == D("200.00")
    assert form.get(T777_LINE_15).value == D("500.00")
    assert form.get(T777_LINE_17).value == D("500.00")
    (return_form,) = run["ca-on/return"]
    assert return_form.get(OTHER_EMPLOYMENT_EXPENSES).value == D("500.00")


def test_the_vehicle_chart_of_8000_of_10000_kilometres_gives_line_29_5000_and_line_3_3500() -> None:
    # Acceptance: 8,000 of 10,000 kilometres, fuel 3,000, maintenance 1,000 and insurance 1,000:
    # line 29 = 5,000.00 and line 30 = 4,000.00; with 500 of allowances (line 31), line 32 and
    # line 3 = 3,500.00.
    form = t777_form(
        **{
            KILOMETRES: "8000",
            TOTAL_KILOMETRES: "10000",
            FUEL: "3000",
            MAINTENANCE: "1000",
            INSURANCE: "1000",
            ALLOWANCES: "500",
        }
    )

    assert form.get(T777_VEHICLE_TOTAL_EXPENSES).value == D("5000.00")
    assert form.get(T777_VEHICLE_EMPLOYMENT_USE).value == D("4000.00")
    assert form.get(T777_LINE_3).value == D("3500.00")
    assert form.get(T777_LINE_15).value == D("3500.00")


def test_vehicle_allowances_equal_to_line_30_give_line_3_of_0() -> None:
    # Line 30 = 4,000.00 (8,000 of 10,000 kilometres, expenses of 5,000); line 31 of 4,000 is
    # allowed: line 32 and line 3 = 0.00.
    form = t777_form(
        **{
            KILOMETRES: "8000",
            TOTAL_KILOMETRES: "10000",
            FUEL: "3000",
            MAINTENANCE: "1000",
            INSURANCE: "1000",
            ALLOWANCES: "4000",
        }
    )

    assert form.get(T777_LINE_3).value == D("0.00")


def test_vehicle_allowances_above_line_30_are_refused_naming_the_input() -> None:
    # A 500 allowance with no vehicle expenses (line 30 = 0) would give line 32 of -500.00; the
    # filer's line 31 is refused, naming it, not the derived line 3.
    with pytest.raises(InputAboveBoundError, match="ca/t777_vehicle_allowances"):
        t777_form(**{ALLOWANCES: "500"})

    with pytest.raises(InputAboveBoundError, match="ca/t777_vehicle_allowances"):
        t777_form(
            **{
                KILOMETRES: "8000",
                TOTAL_KILOMETRES: "10000",
                FUEL: "3000",
                MAINTENANCE: "1000",
                INSURANCE: "1000",
                ALLOWANCES: "4000.01",
            }
        )


def test_tradespersons_tools_claim_of_1000_on_line_9_is_the_maximum_of_the_guide() -> None:
    # Guide T4044 "Deduction for tools": tools cost 2,500 and tradesperson income 45,000 give a
    # maximum deduction of 1,000, so a claim of 1,000 on line 9 is line 9.
    form = t777_form(
        employment="45000",
        **{
            "were_a_tradesperson_in_2025": "1",
            "tradesperson_tools_certified_on_t2200_question_12": "1",
            TOOLS: "1000",
            "eligible_tools_cost": "2500",
            "tradesperson_employment_income": "45000",
        },
    )

    assert form.get(T777_LINE_9).value == D("1000")
    assert form.get(T777_LINE_15).value == D("1000")


def test_tradespersons_tools_claim_of_1500_on_line_9_is_refused_not_capped() -> None:
    # The same worksheet: a claim of 1,500 is above the maximum deduction of 1,000.
    with pytest.raises(InputAboveBoundError, match="t777_tradespersons_tools_maximum_deduction"):
        t777_form(
            employment="45000",
            **{
                "were_a_tradesperson_in_2025": "1",
                "tradesperson_tools_certified_on_t2200_question_12": "1",
                TOOLS: "1500",
                "eligible_tools_cost": "2500",
                "tradesperson_employment_income": "45000",
            },
        )


def test_the_return_s_line_22900_is_the_t777_line_17_plus_the_rc359_line_7_total() -> None:
    # Acceptance: an RC359 line 7 total of 6,000.00 and T777 line 17 of 500.00: line 22900 is
    # 6,500.00, and the medical supplement's employment deductions (line 45200) and T691 line 77
    # read it: line 69 less line 76 (0 on this return) is 6,500.00.
    run = run_hi(t777={FOOD: "400", OFFICE: "300"}, copies=(employer(*EMPLOYER_A),))

    (return_form,) = run["ca-on/return"]
    assert return_form.get(RC359_EXCESS_EPSP_TOTAL).value == D("6000.00")
    assert return_form.get(OTHER_EMPLOYMENT_EXPENSES).value == D("6500.00")
    assert return_form.get(MEDICAL_SUPPLEMENT_EMPLOYMENT_DEDUCTIONS).value == D("6500.00")
    assert return_form.get(AMT_OFFICE_EXPENSES_ADJUSTMENT).value == D("6500.00")


def test_no_t777_and_no_rc359_give_line_22900_of_0_and_nothing_else_changes() -> None:
    # Acceptance: no T777 and no RC359: line 22900 = 0, and the form's lines are 0.
    run = run_hi()

    (return_form,) = run["ca-on/return"]
    assert return_form.get(OTHER_EMPLOYMENT_EXPENSES).value == D("0")
    assert return_form.get(RC359_EXCESS_EPSP_TOTAL).value == D("0")
    assert return_form.get(SPECIAL_TAXES).value == D("0")
    assert return_form.get(REFUND_OR_BALANCE_OWING).value == D("0")
    (form,) = run["ca/t777"]
    assert form.get(T777_LINE_17).value == D("0")


# --- Form T777 line 11, the labour mobility deduction ------------------------------------------


def test_one_relocation_of_4000_gives_lines_38_to_41_of_3000_3000_1000_3000() -> None:
    # Acceptance: one relocation with line 37 of 4,000 and tradesperson income of 6,000: line 38 =
    # 3,000.00, line 39 = 3,000.00, line 40 = 1,000.00 and line 41 = 3,000.00.
    run = run_hi(
        relocations=(relocation(lodging="4000", income="6000", claim="4000"),),
    )

    (copy,) = run["ca/t777_relocation"]
    assert copy.get(T777_RELOCATION_TOTAL).value == D("4000.00")
    assert copy.get(T777_RELOCATION_INCOME_LIMIT).value == D("3000.00")
    assert copy.get(T777_RELOCATION_DEDUCTION).value == D("3000.00")
    assert copy.get(T777_RELOCATION_CARRIED_FORWARD_OUT).value == D("1000.00")
    (form,) = run["ca/t777"]
    assert form.get(T777_LINE_11).value == D("3000.00")


def test_two_relocations_of_1500_and_2500_give_line_41_of_the_4000_maximum() -> None:
    # Two relocations of 1,500 and 2,500 (each with income of 6,000 and the whole amount claimed):
    # line 41 = 4,000.00, the maximum; the copies give 1,500.00 and 2,500.00 on line 39.
    run = run_hi(
        relocations=(
            relocation(lodging="1500", income="6000", claim="1500"),
            relocation(lodging="2500", income="6000", claim="2500"),
        ),
    )

    first, second = run["ca/t777_relocation"]
    assert first.get(T777_RELOCATION_DEDUCTION).value == D("1500.00")
    assert second.get(T777_RELOCATION_DEDUCTION).value == D("2500.00")
    (form,) = run["ca/t777"]
    assert form.get(T777_LINE_11).value == D("4000.00")


def test_two_relocations_of_3000_and_2500_are_refused_above_the_4000_maximum() -> None:
    # Line 41 "Total labour mobility deduction for the year (maximum $4,000)": the line 39
    # amounts of 3,000.00 and 2,500.00 total 5,500.00, which is refused, not lowered to 4,000.00.
    with pytest.raises(InputAboveBoundError) as raised:
        run_hi(
            relocations=(
                relocation(lodging="3000", income="6000", claim="3000"),
                relocation(lodging="2500", income="6000", claim="2500"),
            ),
        )

    assert (
        "ca/t777_relocation_deduction_total 5500.00 is above ca/t777_line_11_maximum 4000"
        in str(raised.value)
    )


def test_a_relocation_with_carried_forward_expenses_adds_them_on_line_37() -> None:
    # Line 33 "carried forward from the previous year from the same eligible temporary relocation"
    # is added on line 37 "Add lines 33 to 36", with the transportation and meals of line 34 and 35.
    run = run_hi(
        relocations=(
            relocation(
                carried="500", transportation="200", meals="100", lodging="1200", income="6000"
            ),
        ),
    )

    (copy,) = run["ca/t777_relocation"]
    assert copy.get(T777_RELOCATION_TOTAL).value == D("2000.00")


# --- Form T777 line 16, the work-space-in-the-home expenses -------------------------------------


def test_work_space_of_14400_with_50000_income_gives_line_54_of_417_60() -> None:
    # Acceptance: line 47 = 14,400 (2,400 and 12,000), line 48 = 417.60, line 49 = 0, employment
    # income of 50,000 and line 15 = 0: line 53 = 50,000.00, line 54 = 417.60 and line 55 = 0.00.
    run = run_hi(
        employment="50000",
        t777={ELECTRICITY: "2400", WORK_SPACE_OTHER: "12000", WORK_SPACE_USE: "417.60"},
    )

    (form,) = run["ca/t777"]
    assert form.get(T777_WORK_SPACE_EXPENSES).value == D("14400.00")
    assert form.get(T777_WORK_SPACE_TOTAL_AMOUNT).value == D("417.60")
    assert form.get(T777_WORK_SPACE_EMPLOYMENT_INCOME).value == D("50000.00")
    assert form.get(T777_WORK_SPACE_EMPLOYMENT_OFFSETS).value == D("0.00")
    assert form.get(T777_WORK_SPACE_INCOME_LIMIT).value == D("50000.00")
    assert form.get(T777_LINE_16).value == D("417.60")
    assert form.get(T777_WORK_SPACE_CARRIED_FORWARD_OUT).value == D("0.00")


def test_work_space_with_1000_income_and_line_15_of_600_gives_line_55_17_60() -> None:
    # Acceptance: employment income of 1,000 and line 15 = 600: line 53 = 400.00, line 54 = 400.00
    # and line 55 = 17.60 (the 417.60 less the 400.00 claimed).
    run = run_hi(
        employment="1000",
        t777={
            OFFICE: "600",
            ELECTRICITY: "2400",
            WORK_SPACE_OTHER: "12000",
            WORK_SPACE_USE: "417.60",
        },
    )

    (form,) = run["ca/t777"]
    assert form.get(T777_LINE_15).value == D("600.00")
    assert form.get(T777_WORK_SPACE_INCOME_LIMIT).value == D("400.00")
    assert form.get(T777_LINE_16).value == D("400.00")
    assert form.get(T777_WORK_SPACE_CARRIED_FORWARD_OUT).value == D("17.60")
