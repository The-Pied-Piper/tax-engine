"""The tradesperson's tools maximum of Guide T4044 (2025) "Deduction for tools", end to end.

Each test fills Form T777 with the Guide's electrician (tools cost 2,500, tradesperson income
45,000) and changes the worksheet's figures:
- the printed $1,471 is its own dataset (`ca/t777_tradespersons_tools_threshold`);
- the maximum is the lesser of $1,000 and A minus $1,471, where A is the lesser of the tools cost
  and the income plus the grants minus the overpayments;
- "the amount, if any" is no amount below zero;
- a line 9 claim above the maximum is refused, never capped;
- the income as a tradesperson is a part of the employment income of the return, so more than it is
  refused.
"""

from __future__ import annotations

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.jurisdictions.ca.catalog import (
    T777_LINE_9,
    T777_TOOLS_FORMULA_A,
    T777_TOOLS_FORMULA_B,
    T777_TRADESPERSON_EMPLOYMENT_INCOME_CHECKED,
    T777_TRADESPERSONS_TOOLS_MAXIMUM_DEDUCTION,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting
from tests.jurisdictions.ca_on.end_to_end.test_return_hi import t777_form

SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
THRESHOLD = "ca/t777_tradespersons_tools_threshold"
T4044_TXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t4044/t4044-25e.txt"
TRADESPERSON_CERTIFIED = "tradesperson_tools_certified_on_t2200_question_12"
# The Guide's electrician: the worksheet's figures with a claim of $1,000.
ELECTRICIAN = {
    "were_a_tradesperson_in_2025": "1",
    TRADESPERSON_CERTIFIED: "1",
    "eligible_tools_cost": "2500",
    "tradesperson_employment_income": "45000",
    "tradespersons_tools": "1000",
}
# The return's employment income is the tradesperson income: it is a part of it, never more.
EMPLOYMENT = "45000"


def test_2025_threshold_is_1471_rounded_to_the_cent() -> None:
    data = SOURCE.get(THRESHOLD, 2025, CREDIT)

    assert data.values == Credit(D("1471"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert T4044_TXT in data.sources


def test_the_guides_electrician_has_a_maximum_of_1000() -> None:
    form = t777_form(employment=EMPLOYMENT, **ELECTRICIAN)

    assert form.get(T777_TOOLS_FORMULA_B).value == D("1029")
    assert form.get(T777_TRADESPERSONS_TOOLS_MAXIMUM_DEDUCTION).value == D("1000.00")


def test_a_small_tools_cost_gives_the_formula_as_the_maximum() -> None:
    # Cost 1,500: A is 1,500, A minus 1,471 is 29, the lesser of 1,000 and 29 is 29.
    form = t777_form(
        employment=EMPLOYMENT,
        **{**ELECTRICIAN, "eligible_tools_cost": "1500", "tradespersons_tools": "29"},
    )

    assert form.get(T777_TRADESPERSONS_TOOLS_MAXIMUM_DEDUCTION).value == D("29")
    assert form.get(T777_LINE_9).value == D("29")


def test_a_claim_above_the_maximum_is_refused_not_capped() -> None:
    with pytest.raises(InputAboveBoundError, match="t777_tradespersons_tools_maximum_deduction"):
        t777_form(
            employment=EMPLOYMENT,
            **{**ELECTRICIAN, "eligible_tools_cost": "1500", "tradespersons_tools": "30"},
        )


def test_income_below_the_cost_is_the_a_of_the_formula() -> None:
    # Income 2,000 plus grants 500 minus overpayments 100 is 2,400, below the cost of 2,500:
    # A is 2,400, A minus 1,471 is 929.
    form = t777_form(
        employment="2000",
        **{
            **ELECTRICIAN,
            "tradesperson_employment_income": "2000",
            "apprenticeship_grants_received": "500",
            "apprenticeship_grant_overpayments": "100",
            "tradespersons_tools": "929",
        },
    )

    assert form.get(T777_TOOLS_FORMULA_A).value == D("2400")
    assert form.get(T777_TOOLS_FORMULA_B).value == D("929")
    assert form.get(T777_LINE_9).value == D("929")


def test_a_formula_below_zero_is_no_amount() -> None:
    # Income 1,000: A is 1,000, A minus 1,471 is -471, "the amount, if any" is 0.
    form = t777_form(
        employment="1000",
        **{**ELECTRICIAN, "tradesperson_employment_income": "1000", "tradespersons_tools": "0"},
    )

    assert form.get(T777_TOOLS_FORMULA_B).value == D("0")
    assert form.get(T777_TRADESPERSONS_TOOLS_MAXIMUM_DEDUCTION).value == D("0.00")


def test_a_filer_who_was_not_a_tradesperson_has_a_maximum_of_0_and_a_claim_is_refused() -> None:
    # Guide T4044: "If you were a tradesperson in 2025, use the following formula". Answer no: the
    # Guide's electrician has a maximum of 0 instead of 1,000, so a claim of 1 is refused.
    answers = {**ELECTRICIAN, "were_a_tradesperson_in_2025": "0"}
    form = t777_form(employment=EMPLOYMENT, **{**answers, "tradespersons_tools": "0"})

    assert form.get(T777_TRADESPERSONS_TOOLS_MAXIMUM_DEDUCTION).value == D("0.00")
    with pytest.raises(InputAboveBoundError, match="t777_tradespersons_tools_maximum_deduction"):
        t777_form(employment=EMPLOYMENT, **{**answers, "tradespersons_tools": "1"})


def test_tools_the_employer_did_not_certify_on_the_t2200_leave_a_maximum_of_0() -> None:
    # Guide T4044: "Have your employer complete question 12 of Part C of the form to certify that
    # the tools being claimed were bought and provided by you".
    answers = {**ELECTRICIAN, TRADESPERSON_CERTIFIED: "0"}

    assert t777_form(employment=EMPLOYMENT, **{**answers, "tradespersons_tools": "0"}).get(
        T777_TRADESPERSONS_TOOLS_MAXIMUM_DEDUCTION
    ).value == D("0.00")
    with pytest.raises(InputAboveBoundError, match="t777_tradespersons_tools_maximum_deduction"):
        t777_form(employment=EMPLOYMENT, **answers)


def test_an_answer_above_one_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        t777_form(employment=EMPLOYMENT, **{**ELECTRICIAN, "were_a_tradesperson_in_2025": "2"})
    with pytest.raises(InputAboveBoundError):
        t777_form(employment=EMPLOYMENT, **{**ELECTRICIAN, TRADESPERSON_CERTIFIED: "2"})


def test_the_tradesperson_income_is_a_part_of_the_employment_income_of_the_return() -> None:
    # The return's employment income is 45,000: all of it as a tradesperson is accepted.
    worksheet = t777_form(employment=EMPLOYMENT, **ELECTRICIAN)

    assert worksheet.get(T777_TRADESPERSON_EMPLOYMENT_INCOME_CHECKED).value == D("45000")


def test_a_tradesperson_income_of_one_cent_above_the_employment_income_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match="t777_work_space_employment_income"):
        t777_form(
            employment=EMPLOYMENT, **{**ELECTRICIAN, "tradesperson_employment_income": "45000.01"}
        )


def test_the_other_employment_income_of_line_10400_counts_in_the_whole() -> None:
    # Line 51 of the line 16 chart reads T1 lines 10100 and 10400 as the employment income.
    artifacts = starting(
        "30000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_employment_income="15000",
        t777_amounts={**ELECTRICIAN},
    )
    (worksheet,) = service().compute(CA_ON, 2025, *artifacts)["ca/t777"]

    assert worksheet.get(T777_TRADESPERSON_EMPLOYMENT_INCOME_CHECKED).value == D("45000")
