"""Unit tests for RoundingOnly: the `rounding_only` kind's values, which are empty.

A `rounding_only` dataset carries nothing but the shared envelope, so its one meaningful figure is
its `rounding` rule: for a capability that computes from artifacts alone and rounds its result by
a dataset's rule. Every `RoundingOnly` is equal to every other; there is nothing to refuse.
"""

from __future__ import annotations

from dataclasses import fields, is_dataclass

import pytest

from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly


def test_holds_nothing() -> None:
    assert is_dataclass(RoundingOnly)
    assert fields(RoundingOnly) == ()


def test_every_value_is_equal() -> None:
    assert RoundingOnly() == RoundingOnly()


def test_is_hashable() -> None:
    assert hash(RoundingOnly()) == hash(RoundingOnly())


def test_is_frozen() -> None:
    with pytest.raises(AttributeError):
        RoundingOnly().rate = 1  # type: ignore[attr-defined]


def test_takes_no_values() -> None:
    with pytest.raises(TypeError):
        RoundingOnly("0.01")  # type: ignore[call-arg]


def test_rounding_only_kind() -> None:
    assert ROUNDING_ONLY == ParameterKind("rounding_only", RoundingOnly)
    assert ROUNDING_ONLY.name == "rounding_only"
    assert ROUNDING_ONLY.value_type is RoundingOnly
