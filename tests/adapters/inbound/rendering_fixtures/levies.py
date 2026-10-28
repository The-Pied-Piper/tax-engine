"""A made-up trace line and its English renderer, registered beside it; no core module lists it."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_calculator.adapters.inbound.trace_english.registry import english_renderer
from tax_calculator.domain.artifact import ArtifactKind
from tax_calculator.domain.trace import TraceLine


@dataclass(frozen=True)
class ExLevyLine(TraceLine):
    """A made-up fact: a levy of `figure` on `output`."""

    output: ArtifactKind[Decimal]
    figure: Decimal

    @property
    def amount(self) -> Decimal:
        return self.figure


@english_renderer
class ExLevyRenderer:
    """The made-up line's English text."""

    line_class = ExLevyLine

    def render(self, line: ExLevyLine) -> str:
        return f"{line.output.label}: levy of {line.figure}"
