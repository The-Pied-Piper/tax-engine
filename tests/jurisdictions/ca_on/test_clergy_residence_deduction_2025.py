"""The 2025 figures of the clergy residence deduction, checked against Form T1223 Part C.

T1 2025 (form 5006-R) line 51 and line 23100 "Clergy residence deduction (complete Form T1223)"
and Form T1223 (2025) Part C, line 2 "Amount from line 1 multiplied by 1/3", line 4 "Line 3
multiplied by $1,000 (maximum $10,000)" and the maximum of $10,000 on the same line. The one-third
is not a finite decimal, so it is a `fraction`; the $1,000 per month and the $10,000 maximum are
dollars-and-cents `amount`s, taken as printed. Line 2 and line 4 are dollars-and-cents boxes, so
the fraction and the per-month amount round half-up to the cent, the owner's decision, as the form
states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_fraction import ApplyFraction
from tax_engine.domain.capabilities.capped_amount import CappedAmount
from tax_engine.domain.capabilities.per_unit_amount import PerUnitAmount
from tax_engine.domain.errors import InvalidCapabilityError
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.fraction import FRACTION, Fraction
from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
ONE_THIRD = "ca/clergy_residence_fraction"
PER_MONTH = "ca/clergy_residence_per_month"
MONTHS_MAXIMUM = "ca/clergy_residence_months_maximum"
PART_B_CONDITIONS = "ca/clergy_residence_part_b_conditions"
T1223_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1223/t1223-25e.pdf"

# Made up for this test and not registered: the income, the months and the amounts they give.
INCOME = ArtifactKind("ex/qualifying_income", Decimal)
LINE_2 = ArtifactKind("ex/line_2", Decimal)
MONTHS = ArtifactKind("ex/months", int)
MONTHS_AMOUNT = ArtifactKind("ex/months_amount", Decimal)
LINE_4 = ArtifactKind("ex/line_4", Decimal)

# Made up for the Part C (B) count: the figures of lines 3, 6 and 7 and the line 1 income that the
# count must not read, and the count the conditions give.
PART_B_MONTHS = ArtifactKind("ex/part_b_months", int)
PART_B_COST = ArtifactKind("ex/part_b_accommodation_cost", Decimal)
PART_B_CLAIMS = ArtifactKind("ex/part_b_other_accommodation_claims", Decimal)
PART_B_INCOME = ArtifactKind("ex/part_b_qualifying_income", Decimal)
PART_B_COMPLETED = ArtifactKind("ex/part_b_completed", int)


def test_2025_the_one_third_fraction_is_one_over_three() -> None:
    data = SOURCE.get(ONE_THIRD, 2025, FRACTION)

    # Line 2 "Amount from line 1 multiplied by 1/3".
    assert data.values == Fraction(1, 3)
    # Line 2, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_the_per_month_amount_is_1000() -> None:
    data = SOURCE.get(PER_MONTH, 2025, AMOUNT)

    # Line 4 "Line 3 multiplied by $1,000".
    assert data.values == Amount(D("1000"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_the_months_maximum_is_10000() -> None:
    data = SOURCE.get(MONTHS_MAXIMUM, 2025, AMOUNT)

    # Line 4 "(maximum $10,000)".
    assert data.values == Amount(D("10000"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_the_datasets_cite_only_the_t1223_form() -> None:
    assert SOURCE.get(ONE_THIRD, 2025, FRACTION).sources == (T1223_PDF,)
    assert SOURCE.get(PER_MONTH, 2025, AMOUNT).sources == (T1223_PDF,)
    assert SOURCE.get(MONTHS_MAXIMUM, 2025, AMOUNT).sources == (T1223_PDF,)


@pytest.mark.parametrize(
    ("income", "line_2"),
    [
        # Line 1 45000 (the worked example): 45000 / 3 = 15000.
        ("45000", "15000.00"),
        # Line 1 8000: 8000 / 3 = 2666.666..., rounded half-up to the cent.
        ("8000", "2666.67"),
        ("30000", "10000.00"),
        ("0", "0"),
    ],
)
def test_line_2_is_one_third_of_the_income_from_qualifying_employment(
    income: str, line_2: str
) -> None:
    capability = ApplyFraction(SOURCE.get(ONE_THIRD, 2025, FRACTION), INCOME, LINE_2)

    result = capability.compute((Artifact(INCOME, D(income)),))

    assert result.outputs == (Artifact(LINE_2, D(line_2)),)


@pytest.mark.parametrize(
    ("months", "amount"),
    [(12, "12000"), (3, "3000"), (1, "1000"), (0, "0")],
)
def test_line_4_is_1000_for_each_month_of_qualifying_employment(months: int, amount: str) -> None:
    capability = PerUnitAmount(SOURCE.get(PER_MONTH, 2025, AMOUNT), MONTHS, MONTHS_AMOUNT)

    result = capability.compute((Artifact(MONTHS, months),))

    assert result.outputs == (Artifact(MONTHS_AMOUNT, D(amount)),)


@pytest.mark.parametrize(
    ("base", "capped"),
    [
        # Twelve months is 12000, capped at 10000 (line 4 of the worked example).
        ("12000", "10000.00"),
        ("10000", "10000.00"),
        ("9000", "9000"),
        ("0", "0"),
    ],
)
def test_line_4_is_capped_at_the_maximum(base: str, capped: str) -> None:
    capability = CappedAmount(SOURCE.get(MONTHS_MAXIMUM, 2025, AMOUNT), MONTHS_AMOUNT, LINE_4)

    result = capability.compute((Artifact(MONTHS_AMOUNT, D(base)),))

    assert result.outputs == (Artifact(LINE_4, D(capped)),)


def test_2025_part_b_completed_is_a_conditions_dataset_citing_t1223_with_no_rounding() -> None:
    data = SOURCE.get(PART_B_CONDITIONS, 2025, CONDITIONS)

    assert data.sources == (T1223_PDF,)
    # A count, not a dollars-and-cents box: nothing is rounded.
    assert data.rounding == NO_ROUNDING
    # Any one of the conditions makes (B) completed, a count of 1; none, a count of 0.
    assert data.values.count_when_any_applies == 1
    assert data.values.count_when_none_applies == 0


def test_2025_part_b_completed_has_the_three_figures_of_part_c_b_in_form_order() -> None:
    data = SOURCE.get(PART_B_CONDITIONS, 2025, CONDITIONS)

    # Line 3 "Number of months in qualifying employment", line 6 "Actual rent and eligible utilities
    # paid ..." and line 7 "All amounts claimed by you, or any person, for the accommodation". Line
    # 1 is not a condition: a filer who claims (A) alone still has line 1.
    assert data.values == ConditionList(
        1,
        (
            Condition(
                data.values.conditions[0].text,
                (ConditionPart((ConditionTest("count", 1, "more_than", D("0"), None),)),),
            ),
            Condition(
                data.values.conditions[1].text,
                (ConditionPart((ConditionTest("amount", 1, "more_than", D("0"), None),)),),
            ),
            Condition(
                data.values.conditions[2].text,
                (ConditionPart((ConditionTest("amount", 2, "more_than", D("0"), None),)),),
            ),
        ),
    )
    assert data.values.count_positions_read == frozenset({1})
    assert data.values.amount_positions_read == frozenset({1, 2})


def test_part_b_completed_refuses_line_1_listed_as_an_amount_the_count_never_reads() -> None:
    # The conditions read the months, the cost and the other claims only, so listing the line 1
    # income among the amounts is refused: the count does not depend on it.
    with pytest.raises(InvalidCapabilityError):
        CountByConditions(
            SOURCE.get(PART_B_CONDITIONS, 2025, CONDITIONS),
            (PART_B_MONTHS,),
            (PART_B_COST, PART_B_CLAIMS, PART_B_INCOME),
            PART_B_COMPLETED,
        )


@pytest.mark.parametrize(
    ("months", "cost", "claims", "count"),
    [
        # Nothing entered in (B): (A) alone, so the count is 0.
        (0, "0", "0", 0),
        # Line 3 more than 0 (the months alone).
        (6, "0", "0", 1),
        # Line 6 more than 0 (the rent or fair rental value alone).
        (0, "12000", "0", 1),
        # Line 7 more than 0 (the other claims alone).
        (0, "0", "5000", 1),
        # All three entered.
        (12, "14000", "5000", 1),
    ],
)
def test_part_b_completed_counts_1_when_any_of_months_cost_or_claims_is_more_than_0(
    months: int, cost: str, claims: str, count: int
) -> None:
    capability = CountByConditions(
        SOURCE.get(PART_B_CONDITIONS, 2025, CONDITIONS),
        (PART_B_MONTHS,),
        (PART_B_COST, PART_B_CLAIMS),
        PART_B_COMPLETED,
    )

    result = capability.compute(
        (
            Artifact(PART_B_MONTHS, months),
            Artifact(PART_B_COST, D(cost)),
            Artifact(PART_B_CLAIMS, D(claims)),
        )
    ).outputs

    assert result == (Artifact(PART_B_COMPLETED, count),)


def test_part_b_completed_is_0_when_only_line_1_is_present_because_line_1_is_not_read() -> None:
    # Line 1 of 15000 with no (B) figures: the count reads months, cost and claims only, so 0.
    capability = CountByConditions(
        SOURCE.get(PART_B_CONDITIONS, 2025, CONDITIONS),
        (PART_B_MONTHS,),
        (PART_B_COST, PART_B_CLAIMS),
        PART_B_COMPLETED,
    )

    result = capability.compute(
        (
            Artifact(PART_B_MONTHS, 0),
            Artifact(PART_B_COST, D("0")),
            Artifact(PART_B_CLAIMS, D("0")),
        )
    ).outputs

    assert result == (Artifact(PART_B_COMPLETED, 0),)
