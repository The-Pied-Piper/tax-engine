"""The 2025 conditions of the Ontario tax reduction, checked against CRA's ON428 and T1.

2025 ON428 (form 5006-C), Ontario tax reduction: "Enter "0" on line 80 if any of the following
applies to you:" followed by the six conditions "You were not a resident of Canada at the beginning
of the year", "You were not a resident of Ontario on December 31, 2025", "There is an amount on line
72", "You were bankrupt at any time in 2025", "Your return is filed for you by a trustee in
bankruptcy" and "You are choosing not to claim an Ontario tax reduction", and "If none of the above
applies to you, complete lines 74 to 80 to calculate your Ontario tax reduction." The dataset
`ca-on/tax_reduction_conditions` copies them in the form's order and wording, with the count 0 when
any applies (so 1 when none does). Five are yes or no counts the caller gives, 1 = the condition
applies, listed in the form's order; "There is an amount on line 72" reads line 72's amount, not
equal to 0.

ON428 also says "If you had a spouse or common-law partner on December 31, 2025, only the
individual with the higher net income can claim the amounts on lines 75 and 76." The dataset
`ca-on/tax_reduction_spouse_rule` copies that sentence as one condition with the count 1 when it
applies. It applies when there was no spouse or common-law partner on December 31 (the caller's
count, from the T1's "Marital status on December 31, 2025" Box 1 Married and Box 2 Living
common-law), when the net income (line 23600) is more than the spouse's, or when the two are equal
and the caller says this return claims (the form names no claimant at a tie, so that yes or no is
the caller's); in and/or parts, (no spouse, or more than, or equal) and (no spouse, or more than,
or claims at a tie). The T1 gives the spouse's net income as a caller figure: "Net income from line
23600 of their return to claim certain credits (or the amount that it would be if they filed a
return, even if the amount is "0")".

The count of a list is not an amount of a line, so neither dataset rounds.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.rounding import NO_ROUNDING
from tax_calculator.domain.trace import ConditionsCountLine
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
LINE_80 = "ca-on/tax_reduction_conditions"
SPOUSE_RULE = "ca-on/tax_reduction_spouse_rule"
ON428_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt"

# Made up for this test and not registered: the five counts of line 80 in the form's order, line
# 72, the gate, the rule's two counts, the two net incomes and the rule's count.
NOT_RESIDENT_CANADA = ArtifactKind("ex/not_resident_of_canada", int)
NOT_RESIDENT_ONTARIO = ArtifactKind("ex/not_resident_of_ontario", int)
BANKRUPT = ArtifactKind("ex/bankrupt", int)
TRUSTEE = ArtifactKind("ex/filed_by_trustee", int)
NOT_CLAIMING = ArtifactKind("ex/not_claiming", int)
LINE_72 = ArtifactKind("ex/line_72", Decimal)
GATE = ArtifactKind("ex/gate", int)
SPOUSE = ArtifactKind("ex/spouse_on_december_31", int)
CLAIMS_AT_TIE = ArtifactKind("ex/claims_at_tie", int)
NET_INCOME = ArtifactKind("ex/net_income", Decimal)
SPOUSE_INCOME = ArtifactKind("ex/spouse_net_income", Decimal)
CLAIMABLE = ArtifactKind("ex/claimable", int)

FIVE_COUNTS = (NOT_RESIDENT_CANADA, NOT_RESIDENT_ONTARIO, BANKRUPT, TRUSTEE, NOT_CLAIMING)


def a_count_applies(text: str, position: int) -> Condition:
    return Condition(
        text, (ConditionPart((ConditionTest("count", position, "equal_to", D(1), None),)),)
    )


def line_80_dataset() -> ParameterDataset[ConditionList]:
    return SOURCE.get(LINE_80, 2025, CONDITIONS)


def spouse_rule_dataset() -> ParameterDataset[ConditionList]:
    return SOURCE.get(SPOUSE_RULE, 2025, CONDITIONS)


def test_2025_line_80_is_0_when_any_of_the_six_conditions_applies() -> None:
    data = line_80_dataset()

    assert data.values == ConditionList(
        0,
        (
            a_count_applies("You were not a resident of Canada at the beginning of the year", 1),
            a_count_applies("You were not a resident of Ontario on December 31, 2025", 2),
            Condition(
                "There is an amount on line 72",
                (ConditionPart((ConditionTest("amount", 1, "not_equal_to", D(0), None),)),),
            ),
            a_count_applies("You were bankrupt at any time in 2025", 3),
            a_count_applies("Your return is filed for you by a trustee in bankruptcy", 4),
            a_count_applies("You are choosing not to claim an Ontario tax reduction", 5),
        ),
    )
    assert data.values.count_when_none_applies == 1
    # A count, not the amount of a line: nothing is rounded.
    assert data.rounding == NO_ROUNDING


def test_2025_the_spouse_rule_is_no_spouse_or_the_higher_net_income_or_a_claim_at_a_tie() -> None:
    data = spouse_rule_dataset()

    no_spouse = ConditionTest("count", 1, "equal_to", D(0), None)
    higher = ConditionTest("amount", 1, "more_than", None, 2)
    equal = ConditionTest("amount", 1, "equal_to", None, 2)
    claims = ConditionTest("count", 2, "equal_to", D(1), None)
    assert data.values == ConditionList(
        1,
        (
            Condition(
                "If you had a spouse or common-law partner on December 31, 2025, only the "
                "individual with the higher net income can claim the amounts on lines 75 and 76.",
                (
                    ConditionPart((no_spouse, higher, equal)),
                    ConditionPart((no_spouse, higher, claims)),
                ),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 0
    assert data.rounding == NO_ROUNDING


def test_2025_the_conditions_cite_only_the_on428_text() -> None:
    assert line_80_dataset().sources == (ON428_TEXT,)
    assert spouse_rule_dataset().sources == (ON428_TEXT,)


def test_2025_the_line_80_conditions_read_five_counts_and_line_72() -> None:
    values = line_80_dataset().values

    assert values.count_positions_read == frozenset({1, 2, 3, 4, 5})
    assert values.amount_positions_read == frozenset({1})


def test_2025_the_spouse_rule_reads_two_counts_and_two_amounts() -> None:
    values = spouse_rule_dataset().values

    assert values.count_positions_read == frozenset({1, 2})
    assert values.amount_positions_read == frozenset({1, 2})


# --- the datasets run through the capability ----------------------------------------------------


def line_80_gate(
    line_72: str = "0", flags: tuple[int, int, int, int, int] = (0, 0, 0, 0, 0)
) -> int:
    capability = CountByConditions(line_80_dataset(), FIVE_COUNTS, (LINE_72,), GATE)
    inputs: list[Artifact[Any]] = [
        Artifact(kind, flag) for kind, flag in zip(FIVE_COUNTS, flags, strict=True)
    ]
    inputs.append(Artifact(LINE_72, D(line_72)))

    (output,) = capability.compute(tuple(inputs)).outputs

    assert isinstance(output.value, int)
    return output.value


def test_no_condition_applying_gives_1() -> None:
    assert line_80_gate() == 1


@pytest.mark.parametrize(
    "flags",
    [
        (1, 0, 0, 0, 0),
        (0, 1, 0, 0, 0),
        (0, 0, 1, 0, 0),
        (0, 0, 0, 1, 0),
        (0, 0, 0, 0, 1),
        (1, 1, 1, 1, 1),
    ],
)
def test_any_one_of_the_five_counts_gives_0(flags: tuple[int, int, int, int, int]) -> None:
    # Bankrupt at any time in 2025 is the third printed condition and the third count.
    assert line_80_gate(flags=flags) == 0


@pytest.mark.parametrize("line_72", ["120.00", "0.01", "520.00"])
def test_an_amount_on_line_72_gives_0(line_72: str) -> None:
    assert line_80_gate(line_72=line_72) == 0


def test_line_72_of_0_is_no_amount() -> None:
    assert line_80_gate(line_72="0.00") == 1


def test_the_trace_names_the_conditions_that_apply_by_position() -> None:
    capability = CountByConditions(line_80_dataset(), FIVE_COUNTS, (LINE_72,), GATE)
    inputs: list[Artifact[Any]] = [
        Artifact(kind, flag) for kind, flag in zip(FIVE_COUNTS, (0, 0, 1, 0, 0), strict=True)
    ]
    inputs.append(Artifact(LINE_72, D("120.00")))

    result = capability.compute(tuple(inputs))

    # "There is an amount on line 72" is the third condition printed and "You were bankrupt at any
    # time in 2025" the fourth.
    assert result.trace[-1] == ConditionsCountLine(GATE, (3, 4), 0)


def spouse_rule(
    net_income: str,
    spouse_net_income: str,
    spouse: int = 1,
    claims_at_tie: int = 0,
) -> int:
    capability = CountByConditions(
        spouse_rule_dataset(), (SPOUSE, CLAIMS_AT_TIE), (NET_INCOME, SPOUSE_INCOME), CLAIMABLE
    )
    inputs = (
        Artifact(SPOUSE, spouse),
        Artifact(CLAIMS_AT_TIE, claims_at_tie),
        Artifact(NET_INCOME, D(net_income)),
        Artifact(SPOUSE_INCOME, D(spouse_net_income)),
    )

    (output,) = capability.compute(inputs).outputs

    assert isinstance(output.value, int)
    return output.value


@pytest.mark.parametrize(
    ("net_income", "spouse_net_income", "spouse", "claims_at_tie", "claimable"),
    [
        # A spouse or common-law partner and the higher net income: lines 75 and 76 are claimed.
        ("48000", "30000", 1, 0, 1),
        ("30000.01", "30000.00", 1, 0, 1),
        # A spouse and the lower net income: they are not.
        ("30000", "48000", 1, 0, 0),
        ("30000.00", "30000.01", 1, 1, 0),
        # No spouse or common-law partner on December 31: the rule does not apply, whatever the
        # spouse's net income entered.
        ("30000", "48000", 0, 0, 1),
        ("30000", "0", 0, 0, 1),
        # Equal net incomes: the form names no claimant, so the caller's yes or no decides.
        ("30000", "30000", 1, 1, 1),
        ("30000", "30000", 1, 0, 0),
        ("0", "0", 1, 1, 1),
        ("0", "0", 1, 0, 0),
        # The caller's claim at a tie changes nothing when the incomes differ, nor with no spouse.
        ("48000", "30000", 1, 1, 1),
        ("30000", "48000", 1, 1, 0),
        ("30000", "30000", 0, 0, 1),
    ],
)
def test_only_the_spouse_with_the_higher_net_income_claims_lines_75_and_76(
    net_income: str, spouse_net_income: str, spouse: int, claims_at_tie: int, claimable: int
) -> None:
    assert spouse_rule(net_income, spouse_net_income, spouse, claims_at_tie) == claimable
