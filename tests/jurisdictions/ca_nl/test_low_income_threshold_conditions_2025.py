"""The 2025 conditions of NL428 line 100's count, checked against CRA's NL428 text.

Form NL428 (5001-C, 2025), line 100: "Line 100: If you claimed an amount on line 96 or line 97,
enter $40,460; if not, enter $23,928." The dataset `ca-nl/low_income_threshold_conditions` copies
the two conditions in the form's wording, an amount on line 96 (amount 1) and an amount on line 97
(amount 2), each more than 0. The count is 1 when either applies and 0 when neither does. It is a
count, so nothing is rounded.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tests.jurisdictions.ca_nl.support import newfoundland_packages, newfoundland_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(newfoundland_packages().roots(), newfoundland_parameter_parsers())
FAMILY = "ca-nl/low_income_threshold_conditions"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-c/5001-c-25e.txt"

# Made up for this test and not registered: the amounts on lines 96 and 97 and the count they give.
LINE_96 = AmountKind("ex/nl428_line_96")
LINE_97 = AmountKind("ex/nl428_line_97")
LINE_100_COUNT = CountKind("ex/nl428_line_100_count")


def test_2025_conditions_are_an_amount_on_line_96_or_on_line_97_and_count_1_when_one_applies() -> (
    None
):
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "You claimed an amount on line 96",
                (ConditionPart((ConditionTest("amount", 1, "more_than", D(0), None),)),),
            ),
            Condition(
                "You claimed an amount on line 97",
                (ConditionPart((ConditionTest("amount", 2, "more_than", D(0), None),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 0


def test_2025_conditions_cite_the_form_and_do_not_round() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.sources == (CRA_FORM_TEXT,)
    assert data.rounding == NO_ROUNDING


def test_2025_conditions_read_two_amounts_and_no_count() -> None:
    values = SOURCE.get(FAMILY, 2025, CONDITIONS).values

    assert values.amount_positions_read == frozenset({1, 2})
    assert values.count_positions_read == frozenset()


@pytest.mark.parametrize(
    ("line_96", "line_97", "count"),
    [
        # Neither line has an amount, so neither condition applies and the count is 0.
        ("0", "0", 0),
        ("0.00", "0.00", 0),
        # An amount on line 96 or on line 97 (or both) makes a condition apply, so the count is 1.
        ("557", "0", 1),
        ("0", "557", 1),
        ("557", "557", 1),
    ],
)
def test_line_100_count_is_1_when_an_amount_is_on_line_96_or_97_and_0_otherwise(
    line_96: str, line_97: str, count: int
) -> None:
    capability = CountByConditions(
        SOURCE.get(FAMILY, 2025, CONDITIONS),
        (),
        (LINE_96, LINE_97),
        LINE_100_COUNT,
    )

    result = capability.compute(
        (Artifact(LINE_96, D(line_96)), Artifact(LINE_97, D(line_97)))
    ).outputs

    assert result == (Artifact(LINE_100_COUNT, count),)
