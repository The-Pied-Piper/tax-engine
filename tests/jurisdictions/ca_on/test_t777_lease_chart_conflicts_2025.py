"""The 2025 datasets of the T777 leasing chart's conflicts, checked against Guide T4044.

Guide T4044 "Repayments and imputed interest": "When you lease a passenger vehicle, you may have
either a repayment owing to you, or you may have imputed interest. If this is your situation, you
cannot use the leasing chart below. Instead, contact the CRA." and "You can only consider imputed
interest as leasing costs on a passenger vehicle if all the following apply: - You made one or more
deposits for the leased passenger vehicle - All deposits are refundable - The deposits total is
more than $1,000". The conflicts dataset holds the two conditions (a passenger vehicle with a
repayment owing; a passenger vehicle with all three imputed interest conditions) and the printed
$1,000; the refused dataset refuses the count of the conflicts when it is 1.

The conditions are tested with made-up kinds, as the other conditions datasets are, and not
registered.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.errors import InputOutOfRangeError
from tax_calculator.domain.parameters.conditions import CONDITIONS
from tax_calculator.domain.parameters.rounding import NO_ROUNDING
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_calculator.jurisdictions.ca.capabilities.count_refused_by_conditions import (
    CountRefusedByConditions,
)

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
GUIDE_T4044 = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t4044/t4044-25e.txt"

CONFLICTS_FAMILY = "ca/t777_lease_chart_conflicts"
REFUSED_FAMILY = "ca/t777_lease_chart_conflict_refused"

PASSENGER = ArtifactKind("ex/passenger_vehicle", int)
REPAYMENT = ArtifactKind("ex/repayment_owing", int)
MADE = ArtifactKind("ex/deposits_made", int)
REFUNDABLE = ArtifactKind("ex/deposits_refundable", int)
TOTAL = ArtifactKind("ex/deposits_total", Decimal)
CONFLICT = ArtifactKind("ex/lease_chart_conflict", int)
CONFLICT_CHECKED = ArtifactKind("ex/lease_chart_conflict_checked", int)


def _conflict(passenger: int, repayment: int, made: int, refundable: int, total: str) -> int:
    """The count of the conflicts for the answers and total given."""
    capability = CountByConditions(
        SOURCE.get(CONFLICTS_FAMILY, 2025, CONDITIONS),
        (PASSENGER, REPAYMENT, MADE, REFUNDABLE),
        (TOTAL,),
        CONFLICT,
    )
    inputs: tuple[Artifact[Any], ...] = (
        Artifact(PASSENGER, passenger),
        Artifact(REPAYMENT, repayment),
        Artifact(MADE, made),
        Artifact(REFUNDABLE, refundable),
        Artifact(TOTAL, D(total)),
    )
    (count,) = capability.compute(inputs).outputs
    return int(count.value)


def test_2025_the_conflicts_are_two_conditions_in_the_order_of_the_guide() -> None:
    values = SOURCE.get(CONFLICTS_FAMILY, 2025, CONDITIONS).values

    assert [condition.text for condition in values.conditions] == [
        "a passenger vehicle with a repayment owing to the filer",
        "a passenger vehicle with imputed interest (deposits made, all refundable, total more "
        "than $1,000)",
    ]
    assert values.count_when_any_applies == 1
    assert values.count_when_none_applies == 0
    assert values.count_positions_read == frozenset({1, 2, 3, 4})
    assert values.amount_positions_read == frozenset({1})


def test_2025_a_repayment_owing_on_a_passenger_vehicle_is_a_conflict() -> None:
    assert _conflict(1, 1, 0, 0, "0") == 1


def test_2025_a_repayment_owing_on_another_vehicle_is_not_a_conflict() -> None:
    assert _conflict(0, 1, 0, 0, "0") == 0


def test_2025_deposits_made_all_refundable_and_more_than_the_printed_1000_are_a_conflict() -> None:
    assert _conflict(1, 0, 1, 1, "1000.01") == 1


def test_2025_a_total_of_exactly_the_printed_1000_is_not_more_than_it() -> None:
    assert _conflict(1, 0, 1, 1, "1000") == 0


@pytest.mark.parametrize(("made", "refundable"), [(0, 1), (1, 0), (0, 0)])
def test_2025_each_of_the_three_conditions_is_needed(made: int, refundable: int) -> None:
    assert _conflict(1, 0, made, refundable, "5000") == 0


def test_2025_the_imputed_interest_conditions_do_not_apply_to_another_vehicle() -> None:
    assert _conflict(0, 0, 1, 1, "5000") == 0


def test_2025_the_conflicts_are_not_rounded_and_cite_the_t4044_guide() -> None:
    data = SOURCE.get(CONFLICTS_FAMILY, 2025, CONDITIONS)

    assert data.rounding == NO_ROUNDING
    assert data.sources == (GUIDE_T4044,)


def test_2025_a_count_of_0_is_not_refused() -> None:
    capability = CountRefusedByConditions(
        SOURCE.get(REFUSED_FAMILY, 2025, CONDITIONS), CONFLICT, CONFLICT_CHECKED
    )
    (checked,) = capability.compute((Artifact(CONFLICT, 0),)).outputs
    assert checked.value == 0


def test_2025_a_count_of_1_is_refused_with_the_guide_s_contact_the_cra() -> None:
    capability = CountRefusedByConditions(
        SOURCE.get(REFUSED_FAMILY, 2025, CONDITIONS), CONFLICT, CONFLICT_CHECKED
    )
    with pytest.raises(
        InputOutOfRangeError, match=r"leasing chart cannot be used \(contact the CRA\)"
    ):
        capability.compute((Artifact(CONFLICT, 1),))
