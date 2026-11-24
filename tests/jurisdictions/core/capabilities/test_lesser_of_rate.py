"""Unit tests for the LesserOfRate capability (`core/lesser_of_rate`).

Each amount comes with the rate a further dollar adds to it; the output is the rate of the least
amount, and of equal least amounts the smallest of their rates.
"""

from __future__ import annotations

from decimal import Decimal
from types import MappingProxyType
from typing import Any, cast

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.trace import LesserOfRateLine
from tax_engine.jurisdictions.core.capabilities.lesser_of_rate import LesserOfRate
from tests.capabilities import bundled_capabilities

D = Decimal
FIRST = AmountKind("ex/first")
SECOND = AmountKind("ex/second")
FIRST_RATE = AmountKind("ex/first_rate")
SECOND_RATE = AmountKind("ex/second_rate")
OUT = AmountKind("ex/out")


def compute(first: str, second: str) -> Any:
    wired = LesserOfRate((FIRST, SECOND), (FIRST_RATE, SECOND_RATE), OUT)
    return wired.compute(
        (
            Artifact(FIRST, D(first)),
            Artifact(SECOND, D(second)),
            Artifact(FIRST_RATE, D("1")),
            Artifact(SECOND_RATE, D("0.0164")),
        )
    )


def test_is_registered_as_ca_lesser_of_rate() -> None:
    assert bundled_capabilities().get("core/lesser_of_rate") is LesserOfRate


def test_declares_its_slots() -> None:
    assert LesserOfRate.CONSUMES == {"amounts": list[Decimal], "rates": list[Decimal]}
    assert LesserOfRate.PRODUCES == {"output": Decimal}


@pytest.mark.parametrize(
    ("first", "second", "rate"),
    [("10", "20", "1"), ("30", "20", "0.0164"), ("20", "20", "0.0164")],
)
def test_is_the_rate_of_the_least_amount_and_the_smallest_rate_on_a_tie(
    first: str, second: str, rate: str
) -> None:
    result = compute(first, second)

    assert result.outputs == (Artifact(OUT, D(rate)),)
    (line,) = result.trace
    assert isinstance(line, LesserOfRateLine)
    assert line.amount == D(rate)


def test_refuses_amounts_and_rates_that_do_not_pair() -> None:
    with pytest.raises(InvalidCapabilityError, match="LesserOfRate"):
        LesserOfRate((FIRST, SECOND), (FIRST_RATE,), OUT)
    with pytest.raises(InvalidCapabilityError, match="LesserOfRate"):
        LesserOfRate((), (), OUT)


# --- the contract -----------------------------------------------------------------------------


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(LesserOfRate)
    assert "produces" not in vars(LesserOfRate)


def test_its_slots_are_read_only() -> None:
    for slots in (LesserOfRate.CONSUMES, LesserOfRate.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_cannot_be_changed() -> None:
    for slots in (LesserOfRate.CONSUMES, LesserOfRate.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = LesserOfRate(amounts=(FIRST, SECOND), rates=(FIRST_RATE, SECOND_RATE), output=OUT)

    assert isinstance(wired, LesserOfRate)


def test_rejects_one_kind_as_both_an_amount_and_the_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="LesserOfRate"):
        LesserOfRate((FIRST, SECOND), (FIRST_RATE, SECOND_RATE), FIRST)


def test_rejects_a_single_kind_for_its_amounts() -> None:
    with pytest.raises(InvalidCapabilityError, match="LesserOfRate"):
        LesserOfRate(FIRST, (FIRST_RATE,), OUT)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = CountKind("ex/count")
    # The ignore fails under mypy (warn_unused_ignores) if wiring a kind of another value type is
    # ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="LesserOfRate"):
        LesserOfRate((count,), (FIRST_RATE,), OUT)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(LesserOfRate, "__type_params__", ())
    assert not getattr(LesserOfRate, "__parameters__", ())


def test_a_missing_amount_is_a_missing_artifact() -> None:
    wired = LesserOfRate((FIRST, SECOND), (FIRST_RATE, SECOND_RATE), OUT)

    with pytest.raises(MissingArtifactError):
        wired.compute(())
