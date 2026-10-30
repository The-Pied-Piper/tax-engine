"""The 2025 conditions under which Form T1032 line 33 follows Note 1, checked against the form.

Form T1032 E (25), Step 4 Part B, page 3: "If all of the following conditions apply, calculate line
33 according to the instructions in note 1: the amount on line 32 is less than $2,000; the receiving
spouse or common-law partner was under age 65 on December 31, 2025; the transferring spouse or
common-law partner was age 65 or older and received any of the following amounts in the year: a) ...
e) eligible veterans benefits". The count is 1 when all of them hold and 0 otherwise, so a single
condition of four parts. "Received any" is an amount above 0. The count is a whole number, so
nothing is rounded.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
FAMILY = "ca/t1032_note_1_applies_conditions"
T1032_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1032/t1032-25e.pdf"

# Made up for this test and not registered: the counts and amounts tested, and the count given.
RECEIVING_UNDER_65 = ArtifactKind("ex/t1032_receiving_spouse_under_65", int)
TRANSFERRING_65_OR_OLDER = ArtifactKind("ex/t1032_transferring_spouse_65_or_older", int)
LINE_32 = ArtifactKind("ex/t1032_line_32", Decimal)
LINE_32_LIMIT = ArtifactKind("ex/t1032_line_32_limit", Decimal)
PAYMENTS = ArtifactKind("ex/t1032_payments", Decimal)
APPLIES = ArtifactKind("ex/t1032_note_1_applies", int)


def test_2025_the_four_conditions_of_the_form_are_one_condition_of_four_parts() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert isinstance(data.values, ConditionList)
    assert data.values.count_when_none_applies == 0
    (condition,) = data.values.conditions
    assert condition.parts == (
        ConditionPart((ConditionTest("amount", 2, "more_than", None, 1),)),
        ConditionPart((ConditionTest("count", 1, "more_than", D("0"), None),)),
        ConditionPart((ConditionTest("count", 2, "more_than", D("0"), None),)),
        ConditionPart((ConditionTest("amount", 3, "more_than", D("0"), None),)),
    )
    assert data.values.count_positions_read == frozenset({1, 2})
    assert data.values.amount_positions_read == frozenset({1, 2, 3})
    assert data.rounding == NO_ROUNDING
    assert isinstance(condition, Condition)


def test_2025_the_conditions_cite_the_form_they_are_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert T1032_PDF in data.sources


def count(
    *, under_65: int, transferring_65: int, line_32: str, payments: str, limit: str = "2000.00"
) -> int:
    capability = CountByConditions(
        SOURCE.get(FAMILY, 2025, CONDITIONS),
        (RECEIVING_UNDER_65, TRANSFERRING_65_OR_OLDER),
        (LINE_32, LINE_32_LIMIT, PAYMENTS),
        APPLIES,
    )
    (output,) = capability.compute(
        (
            Artifact(RECEIVING_UNDER_65, under_65),
            Artifact(TRANSFERRING_65_OR_OLDER, transferring_65),
            Artifact(LINE_32, D(line_32)),
            Artifact(LINE_32_LIMIT, D(limit)),
            Artifact(PAYMENTS, D(payments)),
        )
    ).outputs
    value: int = output.value
    return value


def test_counts_1_when_all_four_conditions_hold() -> None:
    assert count(under_65=1, transferring_65=1, line_32="0", payments="10000") == 1


@pytest.mark.parametrize(
    ("under_65", "transferring_65", "line_32", "payments"),
    [
        # Line 32 is $2,000 or more: not "less than $2,000".
        (1, 1, "2000.00", "10000"),
        (1, 1, "5000.00", "10000"),
        # The receiving spouse was 65 or older.
        (0, 1, "0", "10000"),
        # The transferring spouse was under 65.
        (1, 0, "0", "10000"),
        # None of the amounts a) to e) was received.
        (1, 1, "0", "0"),
    ],
)
def test_counts_0_when_any_one_condition_fails(
    under_65: int, transferring_65: int, line_32: str, payments: str
) -> None:
    assert (
        count(
            under_65=under_65, transferring_65=transferring_65, line_32=line_32, payments=payments
        )
        == 0
    )


def test_a_line_32_of_one_cent_under_2000_is_less_than_2000() -> None:
    assert count(under_65=1, transferring_65=1, line_32="1999.99", payments="1") == 1
