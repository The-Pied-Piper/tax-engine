"""Rounding only: the values of a dataset that carries nothing but its rounding rule.

For a capability that computes from artifacts alone and rounds its result once: its dataset is the
shared envelope, and the `rounding` rule is the one figure it states. The values are empty, so
every `RoundingOnly` is equal to every other and nothing is refused.
"""

from __future__ import annotations

from dataclasses import dataclass

from tax_engine.domain.parameters.kind import ParameterKind


@dataclass(frozen=True)
class RoundingOnly:
    """No values: the dataset's `rounding` rule is all it carries."""


ROUNDING_ONLY: ParameterKind[RoundingOnly] = ParameterKind("rounding_only", RoundingOnly)
