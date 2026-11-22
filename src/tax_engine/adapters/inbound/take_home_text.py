"""English wording of a take-home answer. Implements the `TakeHomeText` port."""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.renderer import EnglishTraceRenderer
from tax_engine.adapters.inbound.trace_english.unit_text import EnglishUnitTextRegistry
from tax_engine.application.services.take_home_models import UnitDescription
from tax_engine.domain.trace import TraceLine
from tax_engine.domain.unit import Unit
from tax_engine.domain.worksheet import Worksheet


class EnglishTakeHomeText:
    """The English text of units and of trace lines."""

    def __init__(
        self,
        renderer: EnglishTraceRenderer | None = None,
        units: EnglishUnitTextRegistry | None = None,
    ) -> None:
        self._renderer = EnglishTraceRenderer() if renderer is None else renderer
        self._units = EnglishUnitTextRegistry.shared() if units is None else units

    def unit(self, unit: Unit) -> UnitDescription:
        text = self._units.for_unit(unit)
        return UnitDescription(
            name=unit.identifier,
            placement=text.placement.value,
            singular=text.singular,
            plural=text.plural,
            spaced=text.spaced,
            as_percentage=text.as_percentage,
        )

    def sentence(self, line: TraceLine, printed: Worksheet) -> str:
        return self._renderer.render(line, printed)
