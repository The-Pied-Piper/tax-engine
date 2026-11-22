"""Outbound port: how a take-home answer is worded and how its units are written."""

from __future__ import annotations

from typing import Protocol

from tax_engine.domain.take_home import UnitDescription
from tax_engine.domain.trace import TraceLine
from tax_engine.domain.unit import Unit
from tax_engine.domain.worksheet import Worksheet


class TakeHomeText(Protocol):
    def unit(self, unit: Unit) -> UnitDescription:
        """How a figure is written with `unit`."""
        ...

    def sentence(self, line: TraceLine, printed: Worksheet) -> str:
        """The sentence that says what `line` did, naming the figures as `printed` shows them."""
        ...
