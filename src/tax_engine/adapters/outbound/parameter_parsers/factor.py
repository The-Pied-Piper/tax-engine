"""Parses `factor` datasets: one quoted decimal `value` into a Factor."""

from __future__ import annotations

from tax_engine.adapters.outbound.parameter_parsers.registry import parameter_parser
from tax_engine.adapters.outbound.yaml_support import YamlNode
from tax_engine.domain.parameters.factor import FACTOR, Factor


@parameter_parser
class FactorParser:
    """Parser for `factor` datasets: a single `value`."""

    kind = FACTOR
    body_keys = frozenset({"value"})

    def parse(self, document: YamlNode) -> Factor:
        """Build a Factor from the dataset's `value` (a quoted decimal)."""
        return Factor(document.field("value").parse_decimal())
