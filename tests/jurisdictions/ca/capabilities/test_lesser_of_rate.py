"""Unit tests for the LesserOfRate capability (`ca/lesser_of_rate`).

Each amount comes with the rate a further dollar adds to it; the output is the rate of the least
amount, and of equal least amounts the smallest of their rates.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InvalidCapabilityError
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca.capabilities.lesser_of_rate import LesserOfRate
from tax_engine.jurisdictions.ca.trace.marginal_rate import LesserOfRateLine
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
    assert bundled_capabilities().get("ca/lesser_of_rate") is LesserOfRate


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
