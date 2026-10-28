"""English rendering of the structured trace: one readable sentence per trace line.

The domain records facts; this adapter turns them into the text a reader sees, line by line, like
the tax authority's own worksheet. Each line class's text is a renderer class registered with
`@english_renderer`, in the module named after its line class's module in `tax_calculator.domain.trace`;
this package imports every one of them, so importing it fills the shared EnglishRendererRegistry
with the core lines' renderers. A new feature module of trace lines adds its renderer module here.
A jurisdiction package renders its own lines in its `trace_english` package. Other languages get
their own package.
"""

from __future__ import annotations

from tax_calculator.adapters.inbound.trace_english import (
    arithmetic,
    choices,
    figures,
    forms,
    line_renderer,
    rate_tables,
    record_lists,
    registry,
    renderer,
)
from tax_calculator.adapters.inbound.trace_english.line_renderer import LineRenderer
from tax_calculator.adapters.inbound.trace_english.renderer import EnglishTraceRenderer

__all__ = [
    "EnglishTraceRenderer",
    "LineRenderer",
    "arithmetic",
    "choices",
    "figures",
    "forms",
    "line_renderer",
    "rate_tables",
    "record_lists",
    "registry",
    "renderer",
]
