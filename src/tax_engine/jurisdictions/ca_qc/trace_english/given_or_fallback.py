"""English text for the trace lines of `tax_engine.jurisdictions.ca_qc.trace.given_or_fallback`: one
renderer class per line class, each registered with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.names import EnglishNames
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.jurisdictions.ca_qc.trace.given_or_fallback import GivenOrFallbackLine


@english_renderer
class GivenOrFallbackRenderer:
    """English text for GivenOrFallbackLine."""

    line_class = GivenOrFallbackLine

    def render(self, line: GivenOrFallbackLine, names: EnglishNames) -> str:
        """The English sentence for `line`."""
        if line.given_was_blank:
            return (
                f"{names.of(line.given)} was left blank, so "
                f"{names.figure(line.fallback, line.result)} is used"
            )
        return f"{names.figure(line.given, line.result)}, as given"
