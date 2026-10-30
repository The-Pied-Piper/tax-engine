"""The 2025 Form T2043 box 67062 conditions: a pair of places, with more than one statement.

Form T2043, Return of Fuel Charge Proceeds to Farmers Tax Credit, 2025 edition, read from the PDF
(https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2043/t2043-25e.pdf; no .txt is
published). Box 67062: "Tick this box if you have multiple farming businesses with one or more
permanent establishments in multiple provinces or territories." The box is 1 when there is more
than one farm statement and two places each have a statement present in them.

`ca/fuel_charge_multiple_provinces_box_conditions` (`conditions`) has one condition for each pair
of the nine places, in the form's order (ON, MB, SK, AB, NS, PE, NL, NB, then outside eight): 36
pairs. Each condition has three parts, all of which must hold: the statement count (count 1) is more
than 1, and the total of the first place and the total of the second place (amounts 1 to 9, in that
order) are each more than 0. The count is 1 when any pair applies, and it is a count, so nothing is
rounded.
"""

from __future__ import annotations

from decimal import Decimal
from itertools import combinations

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.rounding import NO_ROUNDING

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
BOX_CONDITIONS = "ca/fuel_charge_multiple_provinces_box_conditions"
PLACES = ("on", "mb", "sk", "ab", "ns", "pe", "nl", "nb", "outside_eight")


def test_the_box_has_one_condition_for_each_of_the_36_pairs_of_places() -> None:
    conditions = SOURCE.get(BOX_CONDITIONS, 2025, CONDITIONS).values.conditions

    assert len(conditions) == 36
    assert all(isinstance(condition, Condition) for condition in conditions)
    assert all(condition.text for condition in conditions)


def test_the_pairs_are_the_nine_places_taken_two_at_a_time_in_the_form_order() -> None:
    # Amount positions 1 to 9 are the places in the order of PLACES; each condition reads the
    # pair (i, j) with i before j, and the pairs come in the order of the combinations.
    conditions = SOURCE.get(BOX_CONDITIONS, 2025, CONDITIONS).values.conditions
    expected = [
        (
            ConditionPart((ConditionTest("count", 1, "more_than", D("1"), None),)),
            ConditionPart((ConditionTest("amount", first, "more_than", D("0"), None),)),
            ConditionPart((ConditionTest("amount", second, "more_than", D("0"), None),)),
        )
        for first, second in combinations(range(1, len(PLACES) + 1), 2)
    ]

    assert [condition.parts for condition in conditions] == expected


def test_the_first_pair_is_ontario_and_manitoba_and_the_last_is_the_two_last_places() -> None:
    conditions = SOURCE.get(BOX_CONDITIONS, 2025, CONDITIONS).values.conditions

    assert conditions[0].parts[1].tests[0].position == 1  # Ontario
    assert conditions[0].parts[2].tests[0].position == 2  # Manitoba
    assert conditions[-1].parts[1].tests[0].position == 8  # New Brunswick
    assert conditions[-1].parts[2].tests[0].position == 9  # outside eight


def test_the_box_counts_1_when_any_pair_applies_and_reads_the_count_then_the_nine_amounts() -> None:
    values = SOURCE.get(BOX_CONDITIONS, 2025, CONDITIONS).values

    assert values.count_when_any_applies == 1
    assert values.count_positions_read == frozenset({1})
    assert values.amount_positions_read == frozenset(range(1, 10))


def test_the_box_is_a_count_so_nothing_is_rounded() -> None:
    assert SOURCE.get(BOX_CONDITIONS, 2025, CONDITIONS).rounding == NO_ROUNDING
