"""Parses `brackets` datasets: a list of {from, rate} entries, each with an optional printed
`tax_at_start`, and an optional `tax_at_start_rounding` rule and `up_to`, into a BracketSchedule."""

from __future__ import annotations

from tax_engine.adapters.outbound.parameter_parser import parameter_parser
from tax_engine.adapters.outbound.yaml_support import YamlNode
from tax_engine.domain.parameters.brackets import BRACKETS, Bracket, BracketSchedule
from tax_engine.domain.parameters.rounding import NO_ROUNDING

_BRACKET_KEYS = frozenset({"from", "rate"})
_BRACKET_OPTIONAL_KEYS = frozenset({"tax_at_start"})


@parameter_parser
class BracketsParser:
    """Parser for `brackets` datasets: a list of thresholds and rates.

    Each bracket may carry its printed tax at its start; an optional rule rounds the computed tax at
    each start. An optional `up_to` is the last amount the schedule covers; the first bracket's
    `from` is where its range starts.
    """

    kind = BRACKETS
    body_keys = frozenset({"brackets"})
    optional_keys = frozenset({"tax_at_start_rounding", "up_to"})

    def parse(self, document: YamlNode) -> BracketSchedule:
        """Build a BracketSchedule from the dataset's `brackets` list and its optional
        `tax_at_start_rounding` rule and its optional `up_to`.

        The rule is read in the same form as `rounding`; a missing rule is NO_ROUNDING, and a
        printed `tax_at_start` is always used as given.
        """
        rounding = document.optional_field("tax_at_start_rounding")
        up_to = document.optional_field("up_to")
        return BracketSchedule(
            tuple(self._bracket(entry) for entry in document.field("brackets").items()),
            NO_ROUNDING if rounding is None else rounding.parse_rounding_rule(),
            None if up_to is None else up_to.parse_decimal(),
        )

    @staticmethod
    def _bracket(entry: YamlNode) -> Bracket:
        """One `{from, rate}` entry, with an optional printed `tax_at_start` string."""
        fields = entry.require_mapping(_BRACKET_KEYS, optional=_BRACKET_OPTIONAL_KEYS)
        printed = fields.optional_field("tax_at_start")
        return Bracket(
            lower=fields.field("from").parse_decimal(),
            rate=fields.field("rate").parse_decimal(),
            tax_at_start=None if printed is None else printed.parse_decimal(),
        )
