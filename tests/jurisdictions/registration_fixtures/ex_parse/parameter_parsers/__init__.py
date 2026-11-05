"""Made-up parsers."""

from decimal import Decimal

from tax_engine.adapters.outbound.parameter_parser import parameter_parser
from tax_engine.adapters.outbound.yaml_support import YamlNode
from tax_engine.domain.parameters.kind import ParameterKind

IN_INIT = ParameterKind("in_init", Decimal)


@parameter_parser
class InInitParser:
    kind = IN_INIT
    body_keys = frozenset({"rate"})

    def parse(self, document: YamlNode) -> Decimal:
        return document.field("rate").parse_decimal()
