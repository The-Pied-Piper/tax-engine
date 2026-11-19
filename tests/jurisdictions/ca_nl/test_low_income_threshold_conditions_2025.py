"""The 2025 conditions of NL428 line 100's count, checked against CRA's NL428 text.

Form NL428 (5001-C, 2025), line 100: "Line 100: If you claimed an amount on line 96 or line 97,
enter $40,460; if not, enter $23,928." The dataset `ca-nl/low_income_threshold_conditions` copies
the two conditions in the form's wording, an amount on line 96 (amount 1) and an amount on line 97
(amount 2), each more than 0. The count is 1 when either applies and 0 when neither does. It is a
count, so nothing is rounded.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tests.jurisdictions.ca_nl.support import newfoundland_packages, newfoundland_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(newfoundland_packages().roots(), newfoundland_parameter_parsers())
FAMILY = "ca-nl/low_income_threshold_conditions"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-c/5001-c-25e.txt"


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
