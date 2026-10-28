"""The 2025 rule for Schedule 6 line 46 of Step 4, checked against CRA's Schedule 6.

2025 Schedule 6 (form 5000-S6), Step 4 "Advanced Canada workers benefit (ACWB)": "If you have an
eligible spouse who is claiming the basic CWB for you, but you are claiming your CWB disability
supplement, enter "0" on line 46 and continue on line 47." The dataset `ca/acwb_line_46_spouse_rule`
copies that sentence as one condition in four parts, all of which must hold: an eligible spouse
(line 38101, count 1), the filer not claiming the basic CWB (line 38102 no, count 2), that spouse
claiming the basic CWB for the filer (the caller's yes or no, count 3) and the filer claiming the
CWB disability supplement (line 38103, count 4). The count is 0
when it applies and 1 otherwise, so line 46 is 0 or line 44 plus line 45. The count of a rule is not
an amount of a line, so it does not round.
"""

from __future__ import annotations

from decimal import Decimal

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.parameters.conditions import CONDITIONS, ConditionPart, ConditionTest
from tax_calculator.domain.parameters.rounding import NO_ROUNDING

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
LINE_46 = "ca/acwb_line_46_spouse_rule"
SCHEDULE_6_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s6/5000-s6-25e.txt"


def test_the_rule_is_one_condition_of_four_counts_the_second_0_and_the_others_1() -> None:
    values = SOURCE.get(LINE_46, 2025, CONDITIONS).values
    (condition,) = values.conditions

    assert condition.parts == tuple(
        ConditionPart((ConditionTest("count", position, "equal_to", D(than), None),))
        for position, than in ((1, "1"), (2, "0"), (3, "1"), (4, "1"))
    )
    assert 'enter "0" on line 46 and continue on line 47' in condition.text


def test_the_count_is_0_when_the_rule_applies_and_reads_four_counts_and_no_amount() -> None:
    values = SOURCE.get(LINE_46, 2025, CONDITIONS).values

    assert values.count_when_any_applies == 0
    assert values.count_when_none_applies == 1
    assert values.count_positions_read == frozenset({1, 2, 3, 4})
    assert values.amount_positions_read == frozenset()


def test_the_rule_is_a_count_so_nothing_is_rounded() -> None:
    data = SOURCE.get(LINE_46, 2025, CONDITIONS)

    assert data.rounding == NO_ROUNDING
    assert SCHEDULE_6_TEXT in data.sources
