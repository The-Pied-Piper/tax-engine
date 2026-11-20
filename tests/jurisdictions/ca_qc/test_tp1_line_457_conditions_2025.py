"""The 2025 condition of TP-1 line 457's count, checked against the printed guide.

Revenu Quebec TP-1.G-V (2025-12), guide, line 457: "If the total of your net business income, your
employment income subject to the QPIP and your insurable earnings as a person responsible for a
family-type resource or an intermediate resource is less than $2,000, carry the amount from line 97
to line 457." No condition kind reads "less than", so the dataset
`ca-qc/tp1_line_457_conditions` copies the test as its two complements, "equal to $2,000" and "more
than $2,000". The count is 0 when either applies and 1 when neither does, so exactly $2,000 gives 0,
and so does $2,000.01, and $1,999.99 gives 1.

The count is a whole number, not a dollars-and-cents box, so nothing is rounded.
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
from tests.jurisdictions.ca_qc.support import quebec_packages, quebec_parameter_parsers

D = Decimal
# Quebec is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers())
FAMILY = "ca-qc/tp1_line_457_conditions"
SOURCE_FORM = "Revenu Quebec TP-1.G-V (2025-12), guide, line 457"

# Made up for this test and not registered: the total of the three amounts and the count it gives.
TOTAL = AmountKind("ex/line_457_total")
COUNT = CountKind("ex/line_457_count")


def test_2025_line_457_conditions_are_the_two_complements_of_less_than_2000() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        0,
        (
            Condition(
                "The total is equal to $2,000",
                (ConditionPart((ConditionTest("amount", 1, "equal_to", D("2000"), None),)),),
            ),
            Condition(
                "The total is more than $2,000",
                (ConditionPart((ConditionTest("amount", 1, "more_than", D("2000"), None),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 1


def test_2025_line_457_conditions_read_one_amount_and_no_count() -> None:
    values = SOURCE.get(FAMILY, 2025, CONDITIONS).values

    assert values.amount_positions_read == frozenset({1})
    assert values.count_positions_read == frozenset()


def test_2025_line_457_conditions_cite_the_form() -> None:
    assert SOURCE.get(FAMILY, 2025, CONDITIONS).sources == (SOURCE_FORM,)


def test_2025_line_457_conditions_do_not_round() -> None:
    # A count, not the amount of a line: nothing is rounded.
    assert SOURCE.get(FAMILY, 2025, CONDITIONS).rounding == NO_ROUNDING


@pytest.mark.parametrize(
    ("total", "count"),
    [
        ("0", 1),
        ("1000", 1),
        ("1999.99", 1),
        ("1999.999", 1),
        # Exactly $2,000 is not "less than $2,000", and nothing above it is either.
        ("2000", 0),
        ("2000.00", 0),
        ("2000.01", 0),
        ("70000", 0),
    ],
)
def test_2025_line_457_conditions_count_by_the_total(total: str, count: int) -> None:
    capability = CountByConditions(SOURCE.get(FAMILY, 2025, CONDITIONS), (), (TOTAL,), COUNT)

    result = capability.compute((Artifact(TOTAL, D(total)),)).outputs

    assert result == (Artifact(COUNT, count),)
