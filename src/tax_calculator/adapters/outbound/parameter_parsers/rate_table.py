"""Parses `rate_table` datasets: a rate at zero and a list of rows into a RateTable."""

from __future__ import annotations

from tax_calculator.adapters.outbound.parameter_parsers.registry import parameter_parser
from tax_calculator.adapters.outbound.yaml_support import YamlNode
from tax_calculator.domain.errors import DomainError, InvalidRateTableError
from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.parameters.rate_table import RATE_TABLE, RateTable, RateTableRow

_ROW_KEYS = frozenset({"more_than", "rate"})
_OPTIONAL_ROW_KEYS = frozenset({"not_more_than"})


@parameter_parser
class RateTableParser:
    """Parser for `rate_table` datasets: a `rate_at_zero` and a list of rows, each a `more_than`,
    a `rate` and, on every row but the last, a `not_more_than`."""

    kind = RATE_TABLE
    body_keys = frozenset({"rate_at_zero", "rows"})

    def parse(self, document: YamlNode) -> RateTable:
        """Build a RateTable from the dataset's `rate_at_zero` and its `rows`, quoted decimals."""
        rate_at_zero = Rate(document.field("rate_at_zero").parse_decimal())
        rows = tuple(self._row(entry) for entry in document.field("rows").items())
        return RateTable(rate_at_zero=rate_at_zero, rows=rows)

    @staticmethod
    def _row(entry: YamlNode) -> RateTableRow:
        fields = entry.require_mapping(_ROW_KEYS, optional=_OPTIONAL_ROW_KEYS)
        more_than = fields.field("more_than").parse_decimal()
        not_more_than_node = fields.optional_field("not_more_than")
        not_more_than = None if not_more_than_node is None else not_more_than_node.parse_decimal()
        rate = fields.field("rate").parse_decimal()
        try:
            return RateTableRow(more_than=more_than, not_more_than=not_more_than, rate=Rate(rate))
        except DomainError as exc:
            # Name the row: the value objects do not know where in the list they sit.
            raise InvalidRateTableError(f"{entry.where}: {exc}") from exc
