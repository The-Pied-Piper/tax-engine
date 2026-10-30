"""Parses `taper` datasets: four quoted decimals into a Taper."""

from __future__ import annotations

from tax_engine.adapters.outbound.parameter_parsers.registry import parameter_parser
from tax_engine.adapters.outbound.yaml_support import YamlNode
from tax_engine.domain.parameters.taper import TAPER, Taper


@parameter_parser
class TaperParser:
    """Parser for `taper` datasets: a `base`, `supplement`, `threshold` and `range`."""

    kind = TAPER
    body_keys = frozenset({"base", "supplement", "threshold", "range"})

    def parse(self, document: YamlNode) -> Taper:
        """Build a Taper from the dataset's four quoted decimals."""
        return Taper(
            base=document.field("base").parse_decimal(),
            supplement=document.field("supplement").parse_decimal(),
            threshold=document.field("threshold").parse_decimal(),
            range=document.field("range").parse_decimal(),
        )
