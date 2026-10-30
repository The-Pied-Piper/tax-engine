"""The 2025 datasets of Form T2203 Part 2 lines 5, 8 and 10, checked against Form T2203.

Form T2203 (2025) Part 2 line 5: "If you have to pay tax on split income, enter the amount from line
22 of your Form T1206. If not, enter "0"." The condition "you have to pay tax on split income" is a
count of 1 when the federal tax on split income is more than 0 and 0 otherwise, and the count
chooses the amount of line 22 of Form T1206. The count is a whole number, so nothing is rounded.

Form T2203 (2025) Part 2 line 8: "Line 6 multiplied by the percentage from line 7". The product is a
dollars-and-cents line, so it rounds half-up to the cent, the owner's decision, as the form states
no rounding rule.

Form T2203 (2025) Part 2 line 9: "Federal surtax rate" "48%", and line 10: "Line 8 multiplied by the
percentage from line 9". The 48% is a rate of 0.48. The product is a dollars-and-cents line, so it
rounds half-up to the cent, the owner's decision, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.jurisdictions.ca.capabilities.apply_percentage import ApplyPercentage
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
T2203_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2203/t2203-25e.pdf"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

CONDITIONS_FAMILY = "ca/t2203_tax_on_split_income_conditions"
ROUNDING_FAMILY = "ca/t2203_line_8_rounding"
RATE_FAMILY = "ca/t2203_federal_surtax_rate"

# Made up for this test and not registered: the amounts, the percentage and the products.
SPLIT_INCOME_TAX = ArtifactKind("ex/federal_tax_on_split_income", Decimal)
HAS_SPLIT_INCOME_TAX = ArtifactKind("ex/t2203_has_tax_on_split_income", int)
LINE_6 = ArtifactKind("ex/t2203_line_6", Decimal)
PERCENTAGE = ArtifactKind("ex/amt_t2203_column_5_percentage", Decimal)
LINE_8 = ArtifactKind("ex/t2203_line_8", Decimal)
LINE_8_BASE = ArtifactKind("ex/t2203_line_8_base", Decimal)
LINE_10 = ArtifactKind("ex/t2203_line_10", Decimal)


def test_2025_you_have_to_pay_tax_on_split_income_is_the_one_condition() -> None:
    data = SOURCE.get(CONDITIONS_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "you have to pay tax on split income",
                (ConditionPart((ConditionTest("amount", 1, "more_than", D("0"), None),)),),
            ),
        ),
    )
    # The count is 1 when the condition applies and 0 when it does not.
    assert data.values.count_when_none_applies == 0
    assert data.values.count_positions_read == frozenset()
    assert data.values.amount_positions_read == frozenset({1})
    # A count, not the amount of a line: nothing is rounded.
    assert data.rounding == NO_ROUNDING


def test_2025_the_split_income_condition_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(CONDITIONS_FAMILY, 2025, CONDITIONS)

    assert T2203_PDF in data.sources


@pytest.mark.parametrize(
    ("split_income_tax", "count"),
    [
        # Tax on split income is payable, so line 5 is line 22 of Form T1206.
        ("1524.37", 1),
        ("0.01", 1),
        # No tax on split income: line 5 is "0".
        ("0", 0),
    ],
)
def test_counts_1_when_there_is_tax_on_split_income_and_0_otherwise(
    split_income_tax: str, count: int
) -> None:
    capability = CountByConditions(
        SOURCE.get(CONDITIONS_FAMILY, 2025, CONDITIONS),
        (),
        (SPLIT_INCOME_TAX,),
        HAS_SPLIT_INCOME_TAX,
    )

    result = capability.compute((Artifact(SPLIT_INCOME_TAX, D(split_income_tax)),)).outputs

    assert result == (Artifact(HAS_SPLIT_INCOME_TAX, count),)


def test_2025_line_8_rounding_is_half_up_to_the_cent() -> None:
    data = SOURCE.get(ROUNDING_FAMILY, 2025, ROUNDING_ONLY)

    assert data.rounding == CENT


def test_2025_line_8_rounding_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(ROUNDING_FAMILY, 2025, ROUNDING_ONLY)

    assert T2203_PDF in data.sources


@pytest.mark.parametrize(
    ("line_6", "percentage", "result"),
    [
        # 3461.29 x 25 / 100 = 865.3225, rounded half-up to 865.32 (the worked return CX, line 8).
        ("3461.29", "25", "865.32"),
        # 2806.31 x 50 / 100 = 1403.155, a tie, rounded half-up to 1403.16.
        ("2806.31", "50", "1403.16"),
        # Not a figure allocated outside Canada: the percentage is "0", so line 8 is 0.00.
        ("3461.29", "0", "0.00"),
    ],
)
def test_line_8_applies_the_percentage_as_printed_and_rounds_once(
    line_6: str, percentage: str, result: str
) -> None:
    capability = ApplyPercentage(
        SOURCE.get(ROUNDING_FAMILY, 2025, ROUNDING_ONLY), LINE_6, PERCENTAGE, LINE_8
    )

    result_outputs = capability.compute(
        (Artifact(LINE_6, D(line_6)), Artifact(PERCENTAGE, D(percentage)))
    ).outputs

    assert result_outputs == (Artifact(LINE_8, D(result)),)


def test_2025_the_federal_surtax_rate_is_48_percent() -> None:
    data = SOURCE.get(RATE_FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.48"))
    # Part 2 line 10, a dollars-and-cents line: half-up to the cent.
    assert data.rounding == CENT


def test_2025_the_federal_surtax_rate_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(RATE_FAMILY, 2025, RATE)

    assert T2203_PDF in data.sources


@pytest.mark.parametrize(
    ("line_8", "result"),
    [
        # 865.32 x 0.48 = 415.3536, rounded half-up to 415.35 (the worked return CX, line 10).
        ("865.32", "415.35"),
        # 1.04 x 0.48 = 0.4992, rounded half-up to 0.50.
        ("1.04", "0.50"),
        # 100 x 0.48 = 48.00.
        ("100", "48.00"),
    ],
)
def test_line_10_applies_the_rate_and_rounds_once(line_8: str, result: str) -> None:
    capability = ApplyRate(SOURCE.get(RATE_FAMILY, 2025, RATE), LINE_8_BASE, LINE_10)

    result_outputs = capability.compute((Artifact(LINE_8_BASE, D(line_8)),)).outputs

    assert result_outputs == (Artifact(LINE_10, D(result)),)
