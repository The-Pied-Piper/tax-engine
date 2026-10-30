"""Parses `rounding_only` datasets: no keys beyond the shared envelope, into a RoundingOnly."""

from __future__ import annotations

from tax_engine.adapters.outbound.parameter_parsers.registry import parameter_parser
from tax_engine.adapters.outbound.yaml_support import YamlNode
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly


@parameter_parser
class RoundingOnlyParser:
    """Parser for `rounding_only` datasets: the envelope alone, whose `rounding` is read with it."""

    kind = ROUNDING_ONLY
    body_keys: frozenset[str] = frozenset()

    def parse(self, document: YamlNode) -> RoundingOnly:
        """Build the empty RoundingOnly; the dataset adds no keys to read."""
        return RoundingOnly()
