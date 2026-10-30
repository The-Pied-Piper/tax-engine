"""The 2025 datasets of Form T2204 (Employee Overpayment of Employment Insurance Premiums) lines 1,
7, 15 and 45000, checked against Form T2204.

Form T2204 (2025) line 7: "Amount from line 3 – $2,000 = (if negative, enter "0")". The $2,000 is
claimed whole, and the amount it is taken from is not floored below zero by the dataset.

Form T2204 (2025) note (1): "If you have no self-employment earnings and your total EI insurable
earnings on your T4 slips are less than $2,000, enter "0"." The condition reads two figures, the
line 2 amount (equal to "0") and the $2,000 (more than the line 1 amount, so the insurable earnings
are less than $2,000). Both must hold; when they do the count is 0, and it is 1 otherwise.

Form T2204 (2025) line 45000 test: "If this amount is more than $1, enter it on line 45000 of your
return." The count is 1 when line 15 is more than $1 and 0 otherwise. A count is a whole number,
so nothing is rounded. The $2,000 is a dollars-and-cents figure, rounded half-up to the cent,
which changes nothing.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
T2204_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2204/t2204-25e.pdf"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

EXEMPTION_FAMILY = "ca/t2204_exemption"
MAXIMUM_FAMILY = "ca/t2204_maximum_insurable_earnings"
LINE_1_FAMILY = "ca/t2204_line_1_conditions"
LINE_15_FAMILY = "ca/t2204_line_15_conditions"

# Made up for this test and not registered: the amounts and the counts the capabilities read.
SELF_EMPLOYMENT = ArtifactKind("ex/t2204_self_employment_earnings", Decimal)
EXEMPTION = ArtifactKind("ex/t2204_exemption", Decimal)
INSURABLE = ArtifactKind("ex/t2204_insurable_earnings", Decimal)
HAS_NOTE_1 = ArtifactKind("ex/t2204_line_1_count", int)
LINE_15 = ArtifactKind("ex/t2204_line_15", Decimal)
LINE_15_IS_OVER_1 = ArtifactKind("ex/t2204_line_15_count", int)


def test_2025_the_exemption_is_2000_claimed_whole() -> None:
    data = SOURCE.get(EXEMPTION_FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("2000.00"))


def test_2025_the_exemption_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(EXEMPTION_FAMILY, 2025, CREDIT)

    assert data.rounding == CENT


def test_2025_the_exemption_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(EXEMPTION_FAMILY, 2025, CREDIT)

    assert T2204_PDF in data.sources


def test_2025_line_3_maximum_is_65700() -> None:
    data = SOURCE.get(MAXIMUM_FAMILY, 2025, AMOUNT)

    assert data.values == Amount(value=D("65700.00"))


def test_2025_line_3_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(MAXIMUM_FAMILY, 2025, AMOUNT)

    assert data.rounding == CENT


def test_2025_line_3_maximum_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(MAXIMUM_FAMILY, 2025, AMOUNT)

    assert T2204_PDF in data.sources


def test_2025_note_1_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(LINE_1_FAMILY, 2025, CONDITIONS)

    assert T2204_PDF in data.sources


def test_2025_line_45000_condition_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(LINE_15_FAMILY, 2025, CONDITIONS)

    assert T2204_PDF in data.sources


def test_2025_note_1_is_two_parts_that_must_both_hold_and_counts_0_when_they_do() -> None:
    data = SOURCE.get(LINE_1_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        0,
        (
            Condition(
                data.values.conditions[0].text,
                (
                    # Part 1: the line 2 amount is "0", so there are no self-employment earnings
                    # under the agreement.
                    ConditionPart((ConditionTest("amount", 1, "equal_to", D("0"), None),)),
                    # Part 2: the $2,000 (amount 2) is more than the insurable earnings (amount 3),
                    # so the insurable earnings are less than $2,000.
                    ConditionPart((ConditionTest("amount", 2, "more_than", None, 3),)),
                ),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 1
    assert data.values.count_positions_read == frozenset()
    assert data.values.amount_positions_read == frozenset({1, 2, 3})
    # A count, not the amount of a line: nothing is rounded.
    assert data.rounding == NO_ROUNDING


def test_2025_line_45000_condition_is_more_than_1_and_counts_1_when_it_is() -> None:
    data = SOURCE.get(LINE_15_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                data.values.conditions[0].text,
                (ConditionPart((ConditionTest("amount", 1, "more_than", D("1"), None),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 0
    assert data.values.amount_positions_read == frozenset({1})
    assert data.rounding == NO_ROUNDING


@pytest.mark.parametrize(
    ("line_2", "exemption", "insurable", "count"),
    [
        # No self-employment earnings and insurable earnings of 1800: note (1) applies, so 0.
        ("0", "2000", "1800", 0),
        # Insurable earnings of exactly 2000 are not less than $2,000: the note does not apply.
        ("0", "2000", "2000", 1),
        # Insurable earnings of 70000: the note does not apply.
        ("0", "2000", "70000", 1),
        # Self-employment earnings under the agreement: the note does not apply, whatever the
        # insurable earnings.
        ("1000", "2000", "1800", 1),
        # No insurable earnings at all: less than $2,000 and no self-employment, so 0.
        ("0", "2000", "0", 0),
    ],
)
def test_line_1_is_multiplied_by_0_when_note_1_applies_and_by_1_otherwise(
    line_2: str, exemption: str, insurable: str, count: int
) -> None:
    capability = CountByConditions(
        SOURCE.get(LINE_1_FAMILY, 2025, CONDITIONS),
        (),
        (SELF_EMPLOYMENT, EXEMPTION, INSURABLE),
        HAS_NOTE_1,
    )

    result = capability.compute(
        (
            Artifact(SELF_EMPLOYMENT, D(line_2)),
            Artifact(EXEMPTION, D(exemption)),
            Artifact(INSURABLE, D(insurable)),
        )
    ).outputs

    assert result == (Artifact(HAS_NOTE_1, count),)


@pytest.mark.parametrize(
    ("line_15", "count"),
    [
        # Exactly $1.00 is not more than $1, so line 45000 is 0.
        ("1.00", 0),
        # $1.01 is more than $1, so line 45000 is line 15.
        ("1.01", 1),
        ("0", 0),
        ("122.52", 1),
    ],
)
def test_line_45000_counts_1_when_line_15_is_more_than_1_and_0_otherwise(
    line_15: str, count: int
) -> None:
    capability = CountByConditions(
        SOURCE.get(LINE_15_FAMILY, 2025, CONDITIONS),
        (),
        (LINE_15,),
        LINE_15_IS_OVER_1,
    )

    result = capability.compute((Artifact(LINE_15, D(line_15)),)).outputs

    assert result == (Artifact(LINE_15_IS_OVER_1, count),)
