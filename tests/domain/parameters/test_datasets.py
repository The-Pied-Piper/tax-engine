"""Unit tests for ParameterDataset: one family's values of one kind for one tax year."""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.errors import InvalidParameterDataError
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding import NO_ROUNDING


def test_holds_values_of_its_kind() -> None:
    credit = Credit(amount=Decimal(1))

    dataset = ParameterDataset("ex/credit", 2025, CREDIT, credit, NO_ROUNDING, ("src",))

    assert dataset.values is credit


def test_rejects_values_of_another_type() -> None:
    with pytest.raises(TypeError, match="credit dataset values must be a Credit, got Decimal"):
        # The wrong value type is deliberate: it exercises the run-time check mypy would block.
        ParameterDataset(  # type: ignore[misc]
            "ex/credit",
            2025,
            CREDIT,
            Decimal(1),
            NO_ROUNDING,
            ("src",),
        )


def test_works_for_any_kind() -> None:
    rate = ParameterKind("flat_rate", Decimal)

    dataset = ParameterDataset("ex/rate", 2025, rate, Decimal("0.2"), NO_ROUNDING, ("src",))

    assert dataset.values == Decimal("0.2")


def test_a_blank_title_is_refused() -> None:
    with pytest.raises(InvalidParameterDataError):
        ParameterDataset(
            "ex/credit", 2025, CREDIT, Credit(Decimal("1")), NO_ROUNDING, ("https://x.org",), " "
        )


def test_the_title_is_optional() -> None:
    dataset = ParameterDataset("ex/credit", 2025, CREDIT, Credit(Decimal("1")), NO_ROUNDING, ("s",))

    assert dataset.title is None
