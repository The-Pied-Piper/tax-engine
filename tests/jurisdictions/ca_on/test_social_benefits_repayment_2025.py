"""The 2025 social benefits repayment chart's entry conditions, base and rate, checked against CRA's
Federal Worksheet.

2025 Federal Worksheet (form 5000-D1), "Line 23500 - Social benefits repayment": "Complete the
chart below if one or both of the following applies:" followed by the two conditions "You entered
an amount on line 11900 of your return and the amount on line 23400 is more than $82,125" and
"You entered an amount on line 11300 or line 14600 of your return and the amount on line 23400 is
more than $93,454"; "Line 16: OAS benefits base amount 93,343.00"; "Line 18: Amount from line 17
multiplied by 15% ="; and T1 (form 5006-R) "Line 55 and line 23500: If not, enter "0" on line
23500." The dataset `ca/social_benefits_repayment_conditions` copies the two conditions in the
form's order and wording, with the count 1 when either applies: each is the amount entered (more
than 0) joined by "and" to the amount on line 23400 over the printed figure, and the amounts are
read in the order line 11900, line 23400, line 11300, line 14600 (line 23400 is read by both and
listed once). The count is not the amount of a line, so it is not rounded. The OAS benefits base
amount of line 16 is an amount claimed whole (the `credit` kind, as the Ontario basic reduction is)
and the 15% of line 18 a rate (the `rate` kind); line 16 and line 18 are dollars-and-cents boxes,
so each is rounded half-up to the cent, the owner's decision, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
CONDITIONS_FAMILY = "ca/social_benefits_repayment_conditions"
BASE_FAMILY = "ca/oas_benefits_base_amount"
RATE_FAMILY = "ca/social_benefits_repayment_rate"
D1_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-d1/5000-d1-25e.txt"

# Made up for this test and not registered: the four amounts the conditions read in their order,
# the count, the adjusted net income of line 15 and line 18 (15% of line 17).
LINE_11900 = ArtifactKind("ex/line_11900", Decimal)
LINE_23400 = ArtifactKind("ex/line_23400", Decimal)
LINE_11300 = ArtifactKind("ex/line_11300", Decimal)
LINE_14600 = ArtifactKind("ex/line_14600", Decimal)
APPLIES = ArtifactKind("ex/chart_applies", int)
LINE_17 = ArtifactKind("ex/line_17", Decimal)
LINE_18 = ArtifactKind("ex/line_18", Decimal)
BASE = ArtifactKind("ex/oas_base", Decimal)

AMOUNTS = (LINE_11900, LINE_23400, LINE_11300, LINE_14600)


def conditions_dataset() -> Any:
    return SOURCE.get(CONDITIONS_FAMILY, 2025, CONDITIONS)


def test_2025_the_chart_applies_on_either_of_two_conditions_in_the_forms_wording() -> None:
    data = conditions_dataset()

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "You entered an amount on line 11900 of your return and the amount on line 23400 "
                "is more than $82,125",
                (
                    ConditionPart((ConditionTest("amount", 1, "more_than", D(0), None),)),
                    ConditionPart((ConditionTest("amount", 2, "more_than", D(82125), None),)),
                ),
            ),
            Condition(
                "You entered an amount on line 11300 or line 14600 of your return and the amount "
                "on line 23400 is more than $93,454",
                (
                    ConditionPart(
                        (
                            ConditionTest("amount", 3, "more_than", D(0), None),
                            ConditionTest("amount", 4, "more_than", D(0), None),
                        )
                    ),
                    ConditionPart((ConditionTest("amount", 2, "more_than", D(93454), None),)),
                ),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 0
    # A count, not the amount of a line: nothing is rounded.
    assert data.rounding == NO_ROUNDING


def test_2025_the_conditions_read_four_amounts_and_no_counts() -> None:
    values = conditions_dataset().values

    assert values.count_positions_read == frozenset()
    assert values.amount_positions_read == frozenset({1, 2, 3, 4})


def test_2025_oas_benefits_base_amount_is_93343() -> None:
    data = SOURCE.get(BASE_FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("93343.00"))
    # Line 16, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_social_benefits_repayment_rate_is_15_percent() -> None:
    data = SOURCE.get(RATE_FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.15"))
    # Line 18, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_datasets_cite_only_the_federal_worksheet_text() -> None:
    assert conditions_dataset().sources == (D1_TEXT,)
    assert SOURCE.get(BASE_FAMILY, 2025, CREDIT).sources == (D1_TEXT,)
    assert SOURCE.get(RATE_FAMILY, 2025, RATE).sources == (D1_TEXT,)


# --- the datasets run through their capabilities ------------------------------------------------


def chart_count(
    line_11900: str = "0", line_23400: str = "0", line_11300: str = "0", line_14600: str = "0"
) -> int:
    capability = CountByConditions(conditions_dataset(), (), AMOUNTS, APPLIES)
    inputs = (
        Artifact(LINE_11900, D(line_11900)),
        Artifact(LINE_23400, D(line_23400)),
        Artifact(LINE_11300, D(line_11300)),
        Artifact(LINE_14600, D(line_14600)),
    )

    (output,) = capability.compute(inputs).outputs

    assert isinstance(output.value, int)
    return output.value


@pytest.mark.parametrize(
    ("line_11900", "line_23400", "line_11300", "line_14600", "applies"),
    [
        # Condition 1: an amount on line 11900 and line 23400 over $82,125, strictly.
        ("5000", "82125.01", "0", "0", 1),
        ("5000", "82125.00", "0", "0", 0),
        ("0.01", "100000", "0", "0", 1),
        # Condition 2: an amount on line 11300 or line 14600 and line 23400 over $93,454.
        ("0", "93454.01", "9000", "0", 1),
        ("0", "93454.00", "9000", "0", 0),
        ("0", "93454.01", "0", "3000", 1),
        ("0", "93454.00", "0", "3000", 0),
        ("0", "100000", "9000", "3000", 1),
        # The worked example and the acceptance cases: OAS 9,000 with line 23400 of 100,000.00 and
        # of 93,400.00, and OAS 3,000 with 150,000.
        ("0", "100000.00", "9000", "0", 1),
        ("0", "93400.00", "9000", "0", 0),
        ("0", "150000.00", "3000", "0", 1),
        # Between the two figures, only the line 11900 condition can hold.
        ("0", "90000", "9000", "0", 0),
        ("5000", "90000", "9000", "0", 1),
        # Nothing entered, or too little income: the chart does not apply.
        ("0", "1000000", "0", "0", 0),
        ("5000", "50000", "9000", "3000", 0),
        # A negative line 23400 is not over either figure.
        ("5000", "-1000", "9000", "0", 0),
    ],
)
def test_the_chart_applies_when_one_of_its_two_conditions_holds(
    line_11900: str, line_23400: str, line_11300: str, line_14600: str, applies: int
) -> None:
    assert chart_count(line_11900, line_23400, line_11300, line_14600) == applies


def test_the_oas_benefits_base_amount_is_claimed_whole() -> None:
    capability = CreditAmount(SOURCE.get(BASE_FAMILY, 2025, CREDIT), BASE)

    result = capability.compute(())

    assert result.outputs == (Artifact(BASE, D("93343.00")),)


@pytest.mark.parametrize(
    ("line_17", "line_18"),
    [
        # The worked example: 100,000.00 - 93,343.00 = 6,657.00, and 15% is 998.55.
        ("6657.00", "998.55"),
        # 93,400.00 - 93,343.00 = 57.00, and 15% is 8.55.
        ("57.00", "8.55"),
        ("0", "0"),
        # A product past the cent rounds half-up: 0.10 x 15% = 0.015 is 0.02, 0.30 x 15% = 0.045
        # is 0.05.
        ("0.10", "0.02"),
        ("0.30", "0.05"),
    ],
)
def test_15_percent_of_line_17_is_line_18(line_17: str, line_18: str) -> None:
    capability = ApplyRate(SOURCE.get(RATE_FAMILY, 2025, RATE), LINE_17, LINE_18)

    result = capability.compute((Artifact(LINE_17, D(line_17)),))

    assert result.outputs == (Artifact(LINE_18, D(line_18)),)
