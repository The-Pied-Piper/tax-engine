"""The 2025 Form T2043 box 67062 presence datasets: where a statement is present, and its count.

Form T2043, Return of Fuel Charge Proceeds to Farmers Tax Credit, 2025 edition, read from the PDF
(https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2043/t2043-25e.pdf; no .txt is
published). Box 67062: "Tick this box if you have multiple farming businesses with one or more
permanent establishments in multiple provinces or territories." A statement of Form T2042 is present
in a place when it has a permanent establishment there, which the datasets read:

- `ca/farm_present_in_province_conditions` (`conditions`): the statement is present in one
  designated province when its Chart A designated province is that province and no Chart B is in
  use (count 1 is 1), or when its Chart B has a row 1 or row 4 amount for that province (amount 1 or
  amount 2 is more than 0). Each of the three ways is a condition, and any of them counts 1.
- `ca/farm_present_outside_eight_conditions` (`conditions`): the statement is present outside the
  eight designated provinces when its designated province is code 0 and no Chart B is in use: both
  counts are 0.
- `ca/farm_statement_counted` (`amount`): "1", the statement counted once for each place it is
  present in. Its product with a count of 1 is 1, so it is exact.
"""

from __future__ import annotations

from decimal import Decimal

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionPart,
    ConditionTest,
)
from tax_calculator.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
T2043_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2043/t2043-25e.pdf"
IN_PROVINCE = "ca/farm_present_in_province_conditions"
OUTSIDE_EIGHT = "ca/farm_present_outside_eight_conditions"
STATEMENT_COUNTED = "ca/farm_statement_counted"


def test_a_statement_is_present_in_a_province_in_three_ways_each_a_condition() -> None:
    values = SOURCE.get(IN_PROVINCE, 2025, CONDITIONS).values
    conditions = values.conditions

    assert len(conditions) == 3
    assert all(isinstance(condition, Condition) for condition in conditions)
    assert all(condition.text for condition in conditions)


def test_the_province_conditions_count_1_when_any_applies_reading_count_1_and_amounts_1_2() -> None:
    values = SOURCE.get(IN_PROVINCE, 2025, CONDITIONS).values
    first, second, third = values.conditions

    assert values.count_when_any_applies == 1
    assert values.count_positions_read == frozenset({1})
    assert values.amount_positions_read == frozenset({1, 2})
    assert first.parts == (ConditionPart((ConditionTest("count", 1, "equal_to", D("1"), None),)),)
    assert second.parts == (
        ConditionPart((ConditionTest("amount", 1, "more_than", D("0"), None),)),
    )
    assert third.parts == (ConditionPart((ConditionTest("amount", 2, "more_than", D("0"), None),)),)


def test_the_province_conditions_are_a_count_so_nothing_is_rounded() -> None:
    assert SOURCE.get(IN_PROVINCE, 2025, CONDITIONS).rounding == NO_ROUNDING
    assert T2043_PDF in SOURCE.get(IN_PROVINCE, 2025, CONDITIONS).sources


def test_outside_eight_is_two_conditions_code_0_without_chart_b_or_the_filers_yes() -> None:
    values = SOURCE.get(OUTSIDE_EIGHT, 2025, CONDITIONS).values
    first, second = values.conditions

    assert values.count_when_any_applies == 1
    assert first.parts == (
        ConditionPart((ConditionTest("count", 1, "equal_to", D("0"), None),)),
        ConditionPart((ConditionTest("count", 2, "equal_to", D("0"), None),)),
    )
    assert second.parts == (ConditionPart((ConditionTest("count", 3, "equal_to", D("1"), None),)),)


def test_outside_eight_reads_the_three_counts_and_no_amount() -> None:
    values = SOURCE.get(OUTSIDE_EIGHT, 2025, CONDITIONS).values

    assert values.count_positions_read == frozenset({1, 2, 3})
    assert values.amount_positions_read == frozenset()
    assert SOURCE.get(OUTSIDE_EIGHT, 2025, CONDITIONS).rounding == NO_ROUNDING


def test_the_statement_counted_is_the_amount_1_to_the_cent() -> None:
    data = SOURCE.get(STATEMENT_COUNTED, 2025, AMOUNT)

    assert data.values == Amount(D("1"))
    assert data.rounding == CENT
    assert T2043_PDF in data.sources
