"""The 2025 condition of Form T691 Part 3 line 4, checked against Form T691.

Form T691 (2025) Part 3 line 4: "If you have an amount on line 3, enter that amount. If not, and you
are a non-resident or deemed resident, enter the amount from line 2. Otherwise, enter "0"." The
condition "you have an amount on line 3" is a count of 1 when line 3 is not 0 and 0 otherwise; a
negative line 3 is an amount, as the form prints no floor on line 3. The count is a whole number, so
nothing is rounded. The line 3 amount is the one `ca/amt_federal_surtax_multiple_jurisdictions`.
"""

from __future__ import annotations

from decimal import Decimal

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
from tax_calculator.domain.parameters.rounding import NO_ROUNDING
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
FAMILY = "ca/amt_line_3_has_amount_conditions"
T691_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t691/t691-25e.pdf"

# Made up for this test and not registered: the amount tested, and the count it gives.
LINE_3 = ArtifactKind("ex/amt_line_3", Decimal)
HAS_AMOUNT = ArtifactKind("ex/line_3_has_amount", int)


def test_2025_you_have_an_amount_on_line_3_is_the_one_condition() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "you have an amount on line 3",
                (ConditionPart((ConditionTest("amount", 1, "not_equal_to", D("0"), None),)),),
            ),
        ),
    )
    # The count is 1 when the condition applies and 0 when it does not.
    assert data.values.count_when_none_applies == 0
    assert data.values.count_positions_read == frozenset()
    assert data.values.amount_positions_read == frozenset({1})
    # A count, not the amount of a line: nothing is rounded.
    assert data.rounding == NO_ROUNDING


def test_2025_the_condition_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert T691_PDF in data.sources


@pytest.mark.parametrize(
    ("line_3", "count"),
    [
        # An amount on line 3: the condition applies, so the count is 1.
        ("2806.31", 1),
        ("1403.16", 1),
        # A negative line 3 is still an amount (no floor is printed on the form): count 1.
        ("-283.65", 1),
        # Line 3 is 0.00 (no multiple jurisdictions, or a percentage of "0"): count 0.
        ("0", 0),
    ],
)
def test_counts_1_when_line_3_has_an_amount_and_0_otherwise(line_3: str, count: int) -> None:
    capability = CountByConditions(SOURCE.get(FAMILY, 2025, CONDITIONS), (), (LINE_3,), HAS_AMOUNT)

    result = capability.compute((Artifact(LINE_3, D(line_3)),)).outputs

    assert result == (Artifact(HAS_AMOUNT, count),)
