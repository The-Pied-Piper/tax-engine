"""The apprentice mechanic tools maximum of Guide T4044 (2025) "Deduction for tools for an eligible
apprentice mechanic", end to end.

Each test fills Form T777 with the Guide's Example 1 (tools cost 4,500; job income 18,000, grant
1,000; tradesperson's tools claim 1,000; carry forward 2,000) and changes the worksheet's figures:
- the maximum is (A minus B) plus C, where B is the lesser of A and the greater of $1,000 plus the
  Canada employment amount and 5% of the income;
- a first-time apprentice mechanic adds the cost of the tools bought in the last three months of
  2024 to A, and only a first-time one;
- a line 10 claim above the maximum is refused, never capped;
- the claim cannot be more than the net income of the return;
- the income as an apprentice mechanic is a part of the employment income of the return, so more
  than it is refused.
"""

from __future__ import annotations

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    T777_APPRENTICE_MECHANIC_EMPLOYMENT_INCOME_CHECKED,
    T777_APPRENTICE_MECHANIC_TOOLS_CARRIED_FORWARD_OUT,
    T777_APPRENTICE_MECHANIC_TOOLS_MAXIMUM_ALLOWED,
    T777_APPRENTICE_MECHANIC_TOOLS_MAXIMUM_DEDUCTION,
    T777_APPRENTICE_MECHANIC_TOOLS_NET_INCOME_LIMIT,
    T777_APPRENTICE_TOOLS_FORMULA_A,
    T777_APPRENTICE_TOOLS_FORMULA_B,
    T777_LINE_10,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting
from tests.jurisdictions.ca_on.end_to_end.test_return_hi import run_hi, t777_form

SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
BASE = "ca/t777_apprentice_mechanic_tools_base"
RATE_DATASET = "ca/t777_apprentice_mechanic_tools_rate"
T4044_TXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t4044/t4044-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
REGISTERED = "registered_in_a_mechanic_designation_program"
EMPLOYED = "employed_as_an_apprentice_mechanic"
CERTIFIED = "apprentice_mechanic_tools_certified_on_t2200_question_13"
# The Guide's Example 1: tradesperson's tools claim 1,000 (maximum 1,000 on the cost and income).
EXAMPLE_1 = {
    "were_a_tradesperson_in_2025": "1",
    "tradesperson_tools_certified_on_t2200_question_12": "1",
    REGISTERED: "1",
    EMPLOYED: "1",
    CERTIFIED: "1",
    "eligible_tools_cost": "4500",
    "tradesperson_employment_income": "18000",
    "apprenticeship_grants_received": "1000",
    "tradespersons_tools": "1000",
    "apprentice_mechanic_employment_income": "18000",
    "apprentice_mechanic_tools_carry_forward": "2000",
    "apprentice_mechanic_tools": "4029",
}
EMPLOYMENT = "30000"
# The net income tests give the return less employment income than Example 1's 18,000, so both
# incomes are 2,000, a part of it (5% of them is below the 2,471, so the maximum is the same).
SMALL_INCOMES = {
    "tradesperson_employment_income": "2000",
    "apprentice_mechanic_employment_income": "2000",
}


def form(**changes: str) -> Worksheet:
    """The T777 worksheet of Example 1 with the figures `changes`, on a return with 30,000 of
    employment income."""
    return t777_form(employment=EMPLOYMENT, **{**EXAMPLE_1, **changes})


def test_2025_base_is_1000_and_rate_is_5_percent_rounded_to_the_cent() -> None:
    base = SOURCE.get(BASE, 2025, CREDIT)
    rate = SOURCE.get(RATE_DATASET, 2025, RATE)

    assert base.values == Credit(D("1000"))
    assert rate.values == Rate(D("0.05"))
    assert base.rounding == CENT
    assert rate.rounding == CENT
    assert T4044_TXT in base.sources
    assert T4044_TXT in rate.sources


def test_example_1_has_a_maximum_of_4029() -> None:
    # A 4,500; B is the lesser of 4,500 and the greater of 1,000 + 1,471 = 2,471 and 5% of
    # (18,000 + 1,000 - 1,000) = 900, so 2,471; (4,500 - 2,471) + 2,000 = 4,029.
    worksheet = form()

    assert worksheet.get(T777_APPRENTICE_TOOLS_FORMULA_A).value == D("4500")
    assert worksheet.get(T777_APPRENTICE_TOOLS_FORMULA_B).value == D("2471.00")
    assert worksheet.get(T777_APPRENTICE_MECHANIC_TOOLS_MAXIMUM_DEDUCTION).value == D("4029.00")
    assert worksheet.get(T777_LINE_10).value == D("4029")


def test_a_claim_of_one_cent_above_the_maximum_is_refused() -> None:
    with pytest.raises(
        InputAboveBoundError, match="t777_apprentice_mechanic_tools_maximum_deduction"
    ):
        form(apprentice_mechanic_tools="4029.01")


def test_five_percent_of_a_large_income_is_the_greater_of_the_two() -> None:
    # Income 100,000 plus the grant 1,000 minus the tools claim 1,000 is 100,000; 5% is 5,000, more
    # than 2,471, so B is the lesser of 4,500 and 5,000: 4,500; the maximum is 0 + 2,000.
    worksheet = t777_form(
        employment="100000",
        **{
            **EXAMPLE_1,
            "apprentice_mechanic_employment_income": "100000",
            "apprentice_mechanic_tools": "2000",
        },
    )

    assert worksheet.get(T777_APPRENTICE_TOOLS_FORMULA_B).value == D("4500")
    assert worksheet.get(T777_APPRENTICE_MECHANIC_TOOLS_MAXIMUM_DEDUCTION).value == D("2000")


def test_the_tools_bought_late_in_2024_count_only_for_a_first_time_apprentice() -> None:
    late = {"apprentice_tools_cost_last_three_months_of_2024": "500"}

    without = form(**late)
    with_first = form(first_employed_as_apprentice_mechanic_in_2025="1", **late)

    assert without.get(T777_APPRENTICE_TOOLS_FORMULA_A).value == D("4500")
    assert with_first.get(T777_APPRENTICE_TOOLS_FORMULA_A).value == D("5000")
    # A 5,000, B 2,471, C 2,000: 2,529 + 2,000.
    assert with_first.get(T777_APPRENTICE_MECHANIC_TOOLS_MAXIMUM_DEDUCTION).value == D("4529.00")


def test_a_first_time_answer_above_one_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        form(first_employed_as_apprentice_mechanic_in_2025="2")


def test_a_claim_above_the_net_income_of_the_return_is_refused() -> None:
    # Employment income of 1,000 and the claim of 4,029 would leave a net income below zero: the
    # claim cannot create a non-capital loss.
    with pytest.raises(InputAboveBoundError, match="t777_apprentice_mechanic_tools_net_income"):
        t777_form(
            employment="1000",
            **{
                **EXAMPLE_1,
                "tradesperson_employment_income": "1000",
                "apprentice_mechanic_employment_income": "1000",
                "tradespersons_tools": "0",
            },
        )


def test_a_claim_below_the_net_income_of_the_return_is_accepted() -> None:
    # Employment income of 10,000 leaves a net income above zero after the claim of 4,029 and the
    # 1,000 of line 9.
    worksheet = t777_form(employment="10000", **{**EXAMPLE_1, **SMALL_INCOMES})

    assert worksheet.get(T777_LINE_10).value == D("4029")


def test_a_claim_at_the_net_income_limit_is_accepted_and_just_below_it_is_refused() -> None:
    # Employment 5,045 less its CPP deduction leaves, after the line 9 claim of 1,000, a limit of
    # 4,029 or more; at 5,044 the limit is 4,028.56, below the claim of 4,029.
    assert t777_form(employment="5045", **{**EXAMPLE_1, **SMALL_INCOMES}).get(
        T777_LINE_10
    ).value == D("4029")
    with pytest.raises(InputAboveBoundError, match="t777_apprentice_mechanic_tools_net_income"):
        t777_form(employment="5044", **{**EXAMPLE_1, **SMALL_INCOMES})


def return_form(*, employment: str = EMPLOYMENT, **changes: str) -> Worksheet:
    """The return's worksheet of Example 1 with the figures `changes`."""
    run = run_hi(employment=employment, t777={**EXAMPLE_1, **changes})
    (worksheet,) = run["ca-on/return"]
    return worksheet


def test_claiming_the_whole_maximum_leaves_nothing_to_carry_forward() -> None:
    # Example 1 claims the maximum of 4,029.
    worksheet = return_form()

    assert worksheet.get(T777_APPRENTICE_MECHANIC_TOOLS_MAXIMUM_ALLOWED).value == D("4029.00")
    assert worksheet.get(T777_APPRENTICE_MECHANIC_TOOLS_CARRIED_FORWARD_OUT).value == D("0.00")


def test_the_unused_part_of_the_maximum_is_carried_forward() -> None:
    # "If you do not want to claim the maximum deduction, you can carry forward the unused amount":
    # a claim of 1,500 of the maximum 4,029 leaves 2,529.
    worksheet = return_form(apprentice_mechanic_tools="1500")

    assert worksheet.get(T777_APPRENTICE_MECHANIC_TOOLS_CARRIED_FORWARD_OUT).value == D("2529.00")


def test_claiming_nothing_carries_the_whole_maximum_forward() -> None:
    worksheet = return_form(apprentice_mechanic_tools="0")

    assert worksheet.get(T777_APPRENTICE_MECHANIC_TOOLS_CARRIED_FORWARD_OUT).value == D("4029.00")


def test_a_maximum_held_down_by_the_net_income_leaves_nothing_unused_by_a_full_claim() -> None:
    # Example 1: "your maximum deduction in 2025 is $4,029 [...] since it is less than your net
    # income". With a net income below 4,029 the maximum is the net income, so claiming all of it
    # leaves nothing to carry forward.
    # Employment of 5,044 gives a limit of 4,028.56, claimed in full.
    claim = D("4028.56")
    worksheet = return_form(
        employment="5044", apprentice_mechanic_tools=str(claim), **SMALL_INCOMES
    )

    assert worksheet.get(T777_APPRENTICE_MECHANIC_TOOLS_NET_INCOME_LIMIT).value == claim
    assert worksheet.get(T777_APPRENTICE_MECHANIC_TOOLS_MAXIMUM_ALLOWED).value == claim
    assert worksheet.get(T777_APPRENTICE_MECHANIC_TOOLS_CARRIED_FORWARD_OUT).value == D("0.00")


@pytest.mark.parametrize("condition", [REGISTERED, EMPLOYED, CERTIFIED])
def test_a_condition_answered_no_leaves_only_the_carry_forward_of_2024(condition: str) -> None:
    # Guide T4044: "You are an eligible apprentice mechanic if you meet all of the following
    # conditions" and the employer's certification. (A minus B) of 2,029 goes; C of 2,000 stays,
    # as the unused amount can be deducted "even if you are no longer employed as an eligible
    # apprentice mechanic".
    worksheet = form(**{condition: "0", "apprentice_mechanic_tools": "2000"})

    assert worksheet.get(T777_APPRENTICE_MECHANIC_TOOLS_MAXIMUM_DEDUCTION).value == D("2000.00")


def test_a_filer_who_is_not_an_apprentice_mechanic_cannot_claim_above_the_carry_forward() -> None:
    answers = {EMPLOYED: "0", "apprentice_mechanic_tools": "2000.01"}
    with pytest.raises(
        InputAboveBoundError, match="t777_apprentice_mechanic_tools_maximum_deduction"
    ):
        form(**answers)
    assert form(**{EMPLOYED: "0", "apprentice_mechanic_tools": "2000"}).get(
        T777_LINE_10
    ).value == D("2000")


def test_a_tradesperson_who_is_not_an_apprentice_mechanic_carries_nothing_forward() -> None:
    # The electrician of Return LJ answers no to the apprentice mechanic conditions: the 29 of
    # (A minus B) is not carried forward.
    worksheet = return_form(
        **{
            REGISTERED: "0",
            EMPLOYED: "0",
            CERTIFIED: "0",
            "apprentice_mechanic_tools_carry_forward": "0",
            "apprentice_mechanic_tools": "0",
        }
    )

    assert worksheet.get(T777_APPRENTICE_MECHANIC_TOOLS_CARRIED_FORWARD_OUT).value == D("0.00")


def test_a_condition_answer_above_one_is_refused() -> None:
    for condition in (REGISTERED, EMPLOYED, CERTIFIED):
        with pytest.raises(InputAboveBoundError):
            form(**{condition: "2"})


def test_the_apprentice_income_is_a_part_of_the_employment_income_of_the_return() -> None:
    # The return's employment income is 30,000: all of it as an apprentice mechanic is accepted.
    worksheet = form(apprentice_mechanic_employment_income=EMPLOYMENT)

    assert worksheet.get(T777_APPRENTICE_MECHANIC_EMPLOYMENT_INCOME_CHECKED).value == D("30000")


def test_an_apprentice_income_of_one_cent_above_the_employment_income_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match="t777_work_space_employment_income"):
        form(apprentice_mechanic_employment_income="30000.01")


def test_the_other_employment_income_of_line_10400_counts_in_the_whole() -> None:
    # Line 51 of the line 16 chart reads T1 lines 10100 and 10400 as the employment income.
    artifacts = starting(
        "18000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_employment_income="12000",
        t777_amounts={**EXAMPLE_1, "apprentice_mechanic_employment_income": "30000"},
    )
    (worksheet,) = service().compute(CA_ON, 2025, *artifacts)["ca/t777"]

    assert worksheet.get(T777_APPRENTICE_MECHANIC_EMPLOYMENT_INCOME_CHECKED).value == D("30000")
