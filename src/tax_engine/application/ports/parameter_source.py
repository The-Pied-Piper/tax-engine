"""Outbound port: where parameter datasets come from.

One method serves every kind of parameter: the caller passes the kind it needs
and gets back a dataset typed for it. New kinds never change this port.
"""

from __future__ import annotations

from typing import Protocol

from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind


class ParameterSource(Protocol):
    def get[T](self, family: str, tax_year: int, kind: ParameterKind[T]) -> ParameterDataset[T]:
        """The dataset of `kind` for `family` in `tax_year`.

        Raise NotFoundError if that year has no dataset (no carry-forward), and
        InvalidParameterDataError if the dataset cannot be read or is another kind.
        """
        ...
