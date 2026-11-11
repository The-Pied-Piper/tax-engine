"""English rendering of the structured trace: one readable sentence per trace line.

A new module of core trace lines adds its renderer module here; a jurisdiction renders its own lines
in its `trace_english` package.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english import (
    arithmetic,
    blank,
    choices,
    figures,
    forms,
    line_renderer,
    names,
    rate_tables,
    record_lists,
    registry,
    renderer,
)
from tax_engine.adapters.inbound.trace_english.line_renderer import LineRenderer
from tax_engine.adapters.inbound.trace_english.names import EnglishNames, FigureNames, Labelled
from tax_engine.adapters.inbound.trace_english.renderer import EnglishTraceRenderer

__all__ = [
    "EnglishNames",
    "EnglishTraceRenderer",
    "FigureNames",
    "Labelled",
    "LineRenderer",
    "arithmetic",
    "blank",
    "choices",
    "figures",
    "forms",
    "line_renderer",
    "names",
    "rate_tables",
    "record_lists",
    "registry",
    "renderer",
]
