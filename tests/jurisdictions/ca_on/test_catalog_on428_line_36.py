"""The kinds the ON428 (2025) line 36 steps produce, registered in the Ontario catalog.

Form text (CRA 5006-PC, section "Line 58689"): "the maximum Ontario claim for attendant care
expenses is $17,627 ($35,253 in the year of death)". Every money kind is a non-negative amount; the
checked year-of-death answer is a non-negative count. The four inputs are pinned by
`test_take_home_on428_line_36_inputs_categories.py`.
"""

from __future__ import annotations

import pytest

from tax_engine.domain.kinds import AmountKind, CountKind
from tests.kinds import bundled_kinds, non_negative

AMOUNTS = [
    "ca-on/on428_attendant_care_at_ordinary_maximum_line_36",
    "ca-on/on428_attendant_care_at_death_maximum_line_36",
    "ca-on/on428_attendant_care_allowed_line_36",
    "ca-on/on428_adapted_van_allowed_line_36",
    "ca-on/on428_patient_move_allowed_line_36",
    "ca-on/on428_attendant_care_excess_line_36",
    "ca-on/on428_adapted_van_excess_line_36",
    "ca-on/on428_patient_move_excess_line_36",
    "ca-on/on428_medical_expenses_excess_line_36",
    "ca-on/on428_medical_expenses_allowed_line_36",
]


@pytest.mark.parametrize("identifier", AMOUNTS)
def test_each_step_amount_is_a_registered_non_negative_amount(identifier: str) -> None:
    kind = bundled_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)


def test_the_checked_year_of_death_answer_is_a_registered_non_negative_count() -> None:
    kind = bundled_kinds().kind("ca-on/on428_year_of_death_checked_line_36")

    assert isinstance(kind, CountKind)
    assert non_negative(kind)
