from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.parameter_parser import parameter_parser
from tax_engine.adapters.yaml_support import YamlNode
from tax_engine.domain.parameters.kind import ParameterKind

FLAT = ParameterKind("flat", Decimal)


@parameter_parser
class FlatParser:
    kind = FLAT
    body_keys = frozenset({"rate"})

    def parse(self, document: YamlNode) -> Decimal:
        return document.field("rate").parse_decimal()


class NotAParser:
    """Declares no kind, so the walk leaves it out."""
