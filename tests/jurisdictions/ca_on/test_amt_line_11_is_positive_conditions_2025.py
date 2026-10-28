"""The 2025 condition of Form T691 Part 5 line 11, checked against Form T691.

Form T691 (2025) Part 5 line 11: "Line 7 minus line 10 (if negative, enter "0")", then "If line 11
is "0", you are not subject to alternative minimum tax." and "If line 11 is positive, complete parts
6 and 7." The condition "line 11 is positive" is a count of 1 when line 11 is more than 0 and 0
otherwise, and it chooses the T1 line 41700 figure. The count is a whole number, so nothing is
rounded. The line 11 amount is the one `ca/amt_alternative_minimum_tax_payable`.
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
FAMILY = "ca/amt_line_11_is_positive_conditions"
T691_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t691/t691-25e.pdf"

# Made up for this test and not registered: the amount tested, and the count it gives.
LINE_11 = ArtifactKind("ex/amt_line_11", Decimal)
IS_POSITIVE = ArtifactKind("ex/line_11_is_positive", int)


def test_2025_line_11_is_positive_is_the_one_condition() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "line 11 is positive",
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


def test_2025_the_condition_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert T691_PDF in data.sources


@pytest.mark.parametrize(
    ("line_11", "count"),
    [
        # A positive line 11: the condition applies, so the count is 1 and Part 6 is completed.
        ("1558.95", 1),
        ("10960.02", 1),
        ("0.01", 1),
        # Line 11 is 0 (not subject to alternative minimum tax): the count is 0.
        ("0", 0),
        # A negative figure is not positive: the count is 0.
        ("-283.65", 0),
    ],
)
def test_counts_1_when_line_11_is_positive_and_0_otherwise(line_11: str, count: int) -> None:
    capability = CountByConditions(
        SOURCE.get(FAMILY, 2025, CONDITIONS), (), (LINE_11,), IS_POSITIVE
    )

    result = capability.compute((Artifact(LINE_11, D(line_11)),)).outputs

    assert result == (Artifact(IS_POSITIVE, count),)
