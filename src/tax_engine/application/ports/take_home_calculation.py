"""Inbound port: the take-home pay of a salary."""

from __future__ import annotations

from typing import Protocol

from tax_engine.application.models.take_home import TakeHomeResult
from tax_engine.application.models.take_home_request import TakeHomeRequest


class TakeHomeCalculation(Protocol):
    def compute(self, request: TakeHomeRequest) -> TakeHomeResult:
        """The take-home answer for `request`.

        Raises NotFoundError when the jurisdiction declares no take-home figures for the tax year,
        and InvalidManifestError when a declared figure cannot be read as declared.
        """
        ...
