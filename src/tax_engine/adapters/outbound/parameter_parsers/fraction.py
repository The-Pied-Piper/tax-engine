"""Parses `fraction` datasets: a quoted whole `numerator` and `denominator` into a Fraction,
which checks the numerator is zero or more and the denominator positive."""

from __future__ import annotations

from tax_engine.adapters.outbound.parameter_parsers.registry import parameter_parser
from tax_engine.adapters.outbound.yaml_support import YamlNode
from tax_engine.domain.parameters.fraction import FRACTION, Fraction


@parameter_parser
class FractionParser:
    """Parser for `fraction` datasets: a `numerator` and a `denominator`."""

    kind = FRACTION
    body_keys = frozenset({"numerator", "denominator"})

    def parse(self, document: YamlNode) -> Fraction:
        """Build a Fraction from the dataset's `numerator` and `denominator` (quoted digits)."""
        return Fraction(
            numerator=document.field("numerator").parse_whole_number(),
            denominator=document.field("denominator").parse_whole_number(),
        )
