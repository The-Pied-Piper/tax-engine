"""The 2025 Form T2043 Chart B datasets: the percent rounding, the row 8 table and note 9.

Form T2043, Return of Fuel Charge Proceeds to Farmers Tax Credit, 2025 edition, read from the PDF
(https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2043/t2043-25e.pdf; no .txt is
published), Chart B "Calculation of eligible farming expenses allocated to a designated province"
and note 9. The form prints no rounding rule for the percentage rows 3, 6, 7 and 8, so:

- `ca/farm_chart_b_percentage_rounding` (`rounding_only`): rows 3 and 6, a percent to twelve
  decimals of a percent (0.000000000001), half up (the form prints no rule; the owner's decision).
- `ca/farm_chart_b_row_8_rounding` (`rounding_only`): row 8, "Row 7 multiplied by 50%". Half of a
  percent with twelve decimals has at most thirteen decimals, so the product is exact: no rounding.
- `ca/farm_chart_b_row_9_rounding` and `ca/farm_chart_b_row_11_rounding` (`rounding_only`): rows 9
  and 11, dollars and cents, half up to the cent as in Chart A.
- `ca/farm_chart_b_note_9_conditions` (`conditions`): note 9 "If either the total gross income from
  row 2 or the total salaries and wages from row 5 is zero, do not multiply row 7 by 50%.": one
  condition per amount, each zero, the count 1 when either applies.
- `ca/farm_chart_b_row_8_percentage_table` (`amount_by_count`): the percentage of row 7 kept
  at row 8, 50 when note 9 does not apply (count 0) and 100 when it does (count 1).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.parameters.amount_by_count import AMOUNT_BY_COUNT, AmountByCount
from tax_calculator.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionPart,
    ConditionTest,
)
from tax_calculator.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
TWELVE_DECIMALS_OF_A_PERCENT = RoundTo(D("0.000000000001"), RoundingMode.HALF_UP)
T2043_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2043/t2043-25e.pdf"

PERCENTAGE_ROUNDING = "ca/farm_chart_b_percentage_rounding"
ROW_8_ROUNDING = "ca/farm_chart_b_row_8_rounding"
ROW_9_ROUNDING = "ca/farm_chart_b_row_9_rounding"
ROW_11_ROUNDING = "ca/farm_chart_b_row_11_rounding"
NOTE_9_CONDITIONS = "ca/farm_chart_b_note_9_conditions"
ROW_8_TABLE = "ca/farm_chart_b_row_8_percentage_table"


def test_the_percentage_rows_are_rounded_half_up_to_four_decimals_of_a_percent() -> None:
    data = SOURCE.get(PERCENTAGE_ROUNDING, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == TWELVE_DECIMALS_OF_A_PERCENT
    assert T2043_PDF in data.sources


def test_row_8_is_exact_so_it_takes_no_rounding() -> None:
    # 50% of a percent with twelve decimals has at most thirteen decimals: the product is exact.
    data = SOURCE.get(ROW_8_ROUNDING, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == NO_ROUNDING
    assert T2043_PDF in data.sources


def test_rows_9_and_11_are_rounded_half_up_to_the_cent() -> None:
    for name in (ROW_9_ROUNDING, ROW_11_ROUNDING):
        data = SOURCE.get(name, 2025, ROUNDING_ONLY)

        assert data.values == RoundingOnly(), name
        assert data.rounding == CENT, name
        assert T2043_PDF in data.sources, name


def test_note_9_has_one_condition_for_each_of_the_two_totals() -> None:
    data = SOURCE.get(NOTE_9_CONDITIONS, 2025, CONDITIONS)
    conditions = data.values.conditions

    assert len(conditions) == 2
    assert all(isinstance(condition, Condition) for condition in conditions)
    assert "gross income" in conditions[0].text
    assert "salaries" in conditions[1].text


def test_note_9_reads_the_two_totals_as_amounts_1_and_2_and_no_count() -> None:
    values = SOURCE.get(NOTE_9_CONDITIONS, 2025, CONDITIONS).values

    assert values.amount_positions_read == frozenset({1, 2})
    assert values.count_positions_read == frozenset()


def test_note_9_counts_1_when_either_total_is_zero() -> None:
    values = SOURCE.get(NOTE_9_CONDITIONS, 2025, CONDITIONS).values
    first, second = values.conditions

    assert values.count_when_any_applies == 1
    assert first.parts == (ConditionPart((ConditionTest("amount", 1, "equal_to", D("0"), None),)),)
    assert second.parts == (ConditionPart((ConditionTest("amount", 2, "equal_to", D("0"), None),)),)


def test_note_9_is_a_count_so_nothing_is_rounded() -> None:
    assert SOURCE.get(NOTE_9_CONDITIONS, 2025, CONDITIONS).rounding == NO_ROUNDING


def test_row_8_is_50_percent_when_note_9_does_not_apply_and_100_when_it_does() -> None:
    data: Any = SOURCE.get(ROW_8_TABLE, 2025, AMOUNT_BY_COUNT)

    assert data.values == AmountByCount(((0, D("50")), (1, D("100"))))
    assert T2043_PDF in data.sources


def test_row_8_table_counts_only_0_and_1() -> None:
    data: Any = SOURCE.get(ROW_8_TABLE, 2025, AMOUNT_BY_COUNT)

    assert [count for count, _ in data.values.rows] == [0, 1]
