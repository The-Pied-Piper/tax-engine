"""The 2025 entry conditions of Form T657 Charts 2016 to 2023 Part 2, checked against the form.

Form T657 (2025), Chart 2016 Part 1: "If you are reporting a reserve in 2025 from the disposition
of QFFP in 2016 and amount C above is less than the amounts on line 21 of Step 1, line 19 of Step
2, and amount G above, and you want to claim the additional deduction, complete Part 2 of Chart
2016 on the next page." Form T657 (2025), Charts 2017 to 2023 Part 1: "... and amount E above is
equal to or less than the amounts on line 21 of Step 1, line 19 of Step 2, and amount K above
(Charts 2017 to 2020) or amount M above (Charts 2021 to 2023) ... complete Part 2 of Chart Y on the
next page." Each dataset `ca/t657_chart_Y_part_2_conditions` lists, in that order, the conditions
under which Part 2 is not completed: the filer does not want the additional deduction (a 0/1
count), and Part 1 amount E (Chart 2016: amount C) is more than line 21, more than line 19 or more
than Part 1's total (Chart 2016: amount G; Charts 2017 to 2020: amount K; Charts 2021 to 2023:
amount M), amounts read in that order. The count is 0 when any applies and 1 when none does, and is
not rounded.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.rounding import NO_ROUNDING

SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
T657_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t657/t657-25e.pdf"
YEARS = (2021, 2022, 2023)
# Charts 2016 to 2020: the amount read as Part 1's amount C (2016) or E (2017 to 2020), and the
# total read as Part 1's amount G (2016) or K (2017 to 2020).
EARLY_YEARS = (2016, 2017, 2018, 2019, 2020)
ALL_YEARS = (*EARLY_YEARS, *YEARS)


def conditions_dataset(year: int) -> Any:
    return SOURCE.get(f"ca/t657_chart_{year}_part_2_conditions", 2025, CONDITIONS)


def expected_conditions(amount: str, total: str) -> ConditionList:
    """The four conditions, with `amount` (Part 1's E or C) and `total` (Part 1's M, K or G)."""
    return ConditionList(
        0,
        (
            Condition(
                "You do not want to claim the additional deduction",
                (ConditionPart((ConditionTest("count", 1, "equal_to", Decimal(0), None),)),),
            ),
            Condition(
                f"Amount {amount} in Part 1 is more than your annual gains limit for 2025 from "
                "line 21 in Step 1",
                (ConditionPart((ConditionTest("amount", 1, "more_than", None, 2),)),),
            ),
            Condition(
                f"Amount {amount} in Part 1 is more than your cumulative gains limit for 2025 from "
                "line 19 in Step 2",
                (ConditionPart((ConditionTest("amount", 1, "more_than", None, 3),)),),
            ),
            Condition(
                f"Amount {amount} in Part 1 is more than the total amount of capital gains "
                "included "
                "in your 2025 income that is eligible for the capital gains deduction from amount "
                f"{total} in Part 1",
                (ConditionPart((ConditionTest("amount", 1, "more_than", None, 4),)),),
            ),
        ),
    )


@pytest.mark.parametrize("year", YEARS)
def test_2025_part_2_is_skipped_when_any_of_four_conditions_applies(year: int) -> None:
    data = conditions_dataset(year)

    assert data.values == expected_conditions("E", "M")


@pytest.mark.parametrize("year", (2017, 2018, 2019, 2020))
def test_2025_part_2_of_charts_2017_to_2020_is_skipped_on_amount_e_and_amount_k(year: int) -> None:
    # Chart 2017 Part 2 is completed when "amount E in Part 1 is equal to or less than ... line 21,
    # line 19 and amount K above"; the conditions compare Part 1 amount E with those three.
    data = conditions_dataset(year)

    assert data.values == expected_conditions("E", "K")


def test_2025_part_2_of_chart_2016_is_skipped_on_amount_c_and_amount_g() -> None:
    # Chart 2016 Part 2 is completed when "amount C in Part 1 is equal to or less than" line 21,
    # line 19 and "amount G in Part 1 for 2016": the conditions compare Part 1 amount C with those.
    data = conditions_dataset(2016)

    assert data.values == expected_conditions("C", "G")


@pytest.mark.parametrize("year", ALL_YEARS)
def test_2025_the_conditions_are_a_count_so_nothing_is_rounded_and_cite_the_pdf(year: int) -> None:
    data = conditions_dataset(year)

    assert data.rounding == NO_ROUNDING
    assert data.sources == (T657_PDF,)
