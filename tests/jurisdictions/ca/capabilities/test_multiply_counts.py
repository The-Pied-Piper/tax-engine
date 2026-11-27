"""Unit tests for the MultiplyCounts capability (`ca/multiply_counts`), with made-up kinds.

Schedule 8 Part 2 line A: the months a filer typed in times two 0-or-1 flags from the year of
birth. Its slots: one consumed list slot `counts` (count kinds, at least one, since there is no
product of nothing), one produced slot `output`, no parameters. One `MultiplyCountsLine` records
each count in wiring order. The `counts` slot may be blank, with one rule for each kind.
"""

from __future__ import annotations

from typing import Any

import pytest

import tax_engine.jurisdictions.ca.trace_english  # noqa: F401  (registers the renderers)
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.blank import BLANK, PASS_ON
from tax_engine.domain.errors import InvalidCapabilityError
from tax_engine.domain.kinds import CountKind
from tax_engine.jurisdictions.ca.capabilities.multiply_counts import MultiplyCounts
from tax_engine.jurisdictions.ca.trace import MultiplyCountsLine
from tests.capabilities import bundled_capabilities

MONTHS = CountKind("ex/months")
FLAG_ONE = CountKind("ex/flag_one")
FLAG_TWO = CountKind("ex/flag_two")
PRODUCT = CountKind("ex/product_months")


def capability() -> MultiplyCounts:
    return MultiplyCounts((MONTHS, FLAG_ONE, FLAG_TWO), PRODUCT)


def product(*values: tuple[ArtifactKind[int], int]) -> Artifact[Any]:
    (output,) = capability().compute(tuple(Artifact(kind, v) for kind, v in values)).outputs
    return output


def test_is_registered_as_ca_multiply_counts() -> None:
    assert bundled_capabilities().get("ca/multiply_counts") is MultiplyCounts


def test_declares_its_slots() -> None:
    assert MultiplyCounts.CONSUMES == {"counts": list[int]}
    assert MultiplyCounts.PRODUCES == {"output": int}
    assert MultiplyCounts.is_list_slot("counts")
    assert "counts" in MultiplyCounts.BLANK_ALLOWED
    assert "counts" in MultiplyCounts.BLANK_PER_ITEM


@pytest.mark.parametrize(
    ("months", "one", "two", "expected"),
    [(12, 1, 1, 12), (7, 1, 1, 7), (12, 0, 1, 0), (12, 1, 0, 0), (0, 1, 1, 0)],
)
def test_the_product_is_the_months_times_the_flags(
    months: int, one: int, two: int, expected: int
) -> None:
    assert product((MONTHS, months), (FLAG_ONE, one), (FLAG_TWO, two)) == Artifact(
        PRODUCT, expected
    )


def test_one_count_is_its_own_product() -> None:
    wired = MultiplyCounts((MONTHS,), PRODUCT)

    assert wired.compute((Artifact(MONTHS, 5),)).outputs == (Artifact(PRODUCT, 5),)


def test_an_empty_list_of_kinds_is_refused() -> None:
    with pytest.raises(InvalidCapabilityError, match="at least one kind"):
        MultiplyCounts((), PRODUCT)


def test_a_blank_flag_may_take_a_fallback_for_its_kind_alone() -> None:
    result = (
        capability()
        .with_blank_rules({}, per_item={FLAG_ONE: 1, FLAG_TWO: 1})
        .run((Artifact(MONTHS, 12), Artifact(FLAG_ONE, BLANK), Artifact(FLAG_TWO, BLANK)))
    )

    assert result.outputs == (Artifact(PRODUCT, 12),)


def test_a_blank_count_may_be_passed_on() -> None:
    result = (
        capability()
        .with_blank_rules({"counts": PASS_ON})
        .run((Artifact(MONTHS, 12), Artifact(FLAG_ONE, BLANK), Artifact(FLAG_TWO, 1)))
    )

    assert result.outputs == (Artifact(PRODUCT, BLANK),)


def test_records_one_trace_line_with_each_count_and_the_product() -> None:
    result = capability().compute(
        (Artifact(MONTHS, 12), Artifact(FLAG_ONE, 0), Artifact(FLAG_TWO, 1))
    )

    assert result.trace == (
        MultiplyCountsLine(PRODUCT, ((MONTHS, 12), (FLAG_ONE, 0), (FLAG_TWO, 1)), 0),
    )
    (text,) = EnglishTraceRenderer().render_all(result.trace)
    assert "multiplied give" in text
