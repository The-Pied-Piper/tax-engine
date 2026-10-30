"""Parses `rate` datasets: one quoted decimal into a Rate, which checks it is from 0 to 1."""

from __future__ import annotations

from tax_engine.adapters.outbound.parameter_parsers.registry import parameter_parser
from tax_engine.adapters.outbound.yaml_support import YamlNode
from tax_engine.domain.parameters.rate import RATE, Rate


@parameter_parser
class RateParser:
    """Parser for `rate` datasets: a single `rate`."""

    kind = RATE
    body_keys = frozenset({"rate"})

    def parse(self, document: YamlNode) -> Rate:
        """Build a Rate from the dataset's `rate` (a quoted decimal)."""
        return Rate(document.field("rate").parse_decimal())
