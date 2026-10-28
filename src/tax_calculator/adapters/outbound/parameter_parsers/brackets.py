"""Parses `brackets` datasets: a list of {from, rate} and a `tax_at_start_rounding` rule into a
BracketSchedule."""

from __future__ import annotations

from tax_calculator.adapters.outbound.parameter_parsers.registry import parameter_parser
from tax_calculator.adapters.outbound.yaml_support import YamlNode
from tax_calculator.domain.parameters.brackets import BRACKETS, Bracket, BracketSchedule

_BRACKET_KEYS = frozenset({"from", "rate"})


@parameter_parser
class BracketsParser:
    """Parser for `brackets` datasets: a list of thresholds and rates, and the rule that rounds
    the tax at each bracket's start."""

    kind = BRACKETS
    body_keys = frozenset({"brackets", "tax_at_start_rounding"})

    def parse(self, document: YamlNode) -> BracketSchedule:
        """Build a BracketSchedule from the dataset's `brackets` list of entries and its
        `tax_at_start_rounding` rule, read in the same form as `rounding` but apart from it."""
        return BracketSchedule(
            tuple(self._bracket(entry) for entry in document.field("brackets").items()),
            document.field("tax_at_start_rounding").parse_rounding_rule(),
        )

    @staticmethod
    def _bracket(entry: YamlNode) -> Bracket:
        fields = entry.require_mapping(_BRACKET_KEYS)
        return Bracket(
            lower=fields.field("from").parse_decimal(),
            rate=fields.field("rate").parse_decimal(),
        )
