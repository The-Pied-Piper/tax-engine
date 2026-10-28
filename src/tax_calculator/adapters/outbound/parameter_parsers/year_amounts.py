"""Parses `year_amounts` datasets: rows of named amounts by year into a YearAmounts."""

from __future__ import annotations

from tax_calculator.adapters.outbound.parameter_parsers.registry import parameter_parser
from tax_calculator.adapters.outbound.yaml_support import YamlNode
from tax_calculator.domain.errors import DomainError, InvalidYearAmountsError
from tax_calculator.domain.parameters.year_amounts import YEAR_AMOUNTS, YearAmounts, YearAmountsRow

_ROW_KEYS = frozenset({"amounts"})
_OPTIONAL_ROW_KEYS = frozenset({"from_year"})


@parameter_parser
class YearAmountsParser:
    """Parser for `year_amounts` datasets: a list of `rows`, newest first, each with `amounts`
    (names to quoted decimals) and, on every row but the last, a `from_year` integer."""

    kind = YEAR_AMOUNTS
    body_keys = frozenset({"rows"})

    def parse(self, document: YamlNode) -> YearAmounts:
        """Build a YearAmounts from the dataset's `rows`."""
        return YearAmounts(tuple(self._row(entry) for entry in document.field("rows").items()))

    @staticmethod
    def _row(entry: YamlNode) -> YearAmountsRow:
        fields = entry.require_mapping(_ROW_KEYS, optional=_OPTIONAL_ROW_KEYS)
        year_node = fields.optional_field("from_year")
        from_year = None if year_node is None else year_node.require_integer()
        amounts = {name: node.parse_decimal() for name, node in fields.field("amounts").fields()}
        try:
            return YearAmountsRow(from_year, amounts)
        except DomainError as exc:
            # Name the row: the value objects do not know where in the list they sit.
            raise InvalidYearAmountsError(f"{entry.where}: {exc}") from exc
