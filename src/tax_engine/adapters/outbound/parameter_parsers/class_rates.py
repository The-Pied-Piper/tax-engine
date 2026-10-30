"""Parses `class_rates` datasets: a mapping of class numbers to their rates, rules and factors
into ClassRates."""

from __future__ import annotations

from tax_engine.adapters.outbound.parameter_parsers.fraction import FractionParser
from tax_engine.adapters.outbound.parameter_parsers.registry import parameter_parser
from tax_engine.adapters.outbound.yaml_support import YamlNode
from tax_engine.domain.errors import DomainError, InvalidClassRatesError
from tax_engine.domain.parameters.class_rates import (
    CLASS_RATES,
    ClassElection,
    ClassRate,
    ClassRates,
    HalfYearRule,
    HalfYearRuleOnSale,
    RecaptureAndTerminalLoss,
)
from tax_engine.domain.parameters.rate import Rate

_CLASS_KEYS = frozenset(
    {
        "rate",
        "half_year_rule",
        "recapture_and_terminal_loss",
        "half_year_rule_on_sale",
        "aiip_factor",
        "riip_factor",
    }
)
_OPTIONAL_CLASS_KEYS = frozenset({"elections"})
_ELECTION_KEYS = frozenset({"rate"})
# Each factor is read as a `fraction` dataset's body is: the same keys, the same parts.
_FRACTIONS = FractionParser()


@parameter_parser
class ClassRatesParser:
    """Parser for `class_rates` datasets: `classes`, keyed by each class number as a quoted
    decimal, each a `rate`, a `half_year_rule`, a `recapture_and_terminal_loss`, a
    `half_year_rule_on_sale`, an `aiip_factor` and a `riip_factor`, each factor a quoted whole
    `numerator` and `denominator` read as a `fraction` dataset's are, and optionally `elections`,
    keyed by each code as a quoted whole number above 0, each a `rate` as a quoted decimal; and
    `full_year_days`, a quoted whole number above 0, the days of a full fiscal period; and
    `longest_fiscal_period_days`, a quoted whole number, the days of the longest fiscal period."""

    kind = CLASS_RATES
    body_keys = frozenset({"classes", "full_year_days", "longest_fiscal_period_days"})

    def parse(self, document: YamlNode) -> ClassRates:
        """Build ClassRates from the dataset's `classes`, in the file's order, its
        `full_year_days` and its `longest_fiscal_period_days`."""
        classes = tuple(
            self._class(key, entry) for key, entry in document.field("classes").fields()
        )
        full_year_days = document.field("full_year_days").parse_whole_number()
        longest_fiscal_period_days = document.field(
            "longest_fiscal_period_days"
        ).parse_whole_number()
        try:
            return ClassRates(classes, full_year_days, longest_fiscal_period_days)
        except DomainError as exc:
            raise InvalidClassRatesError(f"{document.where}: {exc}") from exc

    def _class(self, key: str, entry: YamlNode) -> ClassRate:
        class_number = YamlNode(key, entry.where).parse_decimal()
        fields = entry.require_mapping(_CLASS_KEYS, optional=_OPTIONAL_CLASS_KEYS)
        rate = fields.field("rate").parse_decimal()
        half_year_rule = fields.field("half_year_rule").parse_choice(HalfYearRule)
        recapture_and_terminal_loss = fields.field("recapture_and_terminal_loss").parse_choice(
            RecaptureAndTerminalLoss
        )
        half_year_rule_on_sale = fields.field("half_year_rule_on_sale").parse_choice(
            HalfYearRuleOnSale
        )
        aiip_factor = fields.field("aiip_factor").require_mapping(_FRACTIONS.body_keys)
        riip_factor = fields.field("riip_factor").require_mapping(_FRACTIONS.body_keys)
        elections_node = fields.optional_field("elections")
        elections = (
            ()
            if elections_node is None
            else tuple(self._election(code, held) for code, held in elections_node.fields())
        )
        try:
            return ClassRate(
                class_number,
                Rate(rate),
                half_year_rule,
                recapture_and_terminal_loss,
                _FRACTIONS.parse(aiip_factor),
                _FRACTIONS.parse(riip_factor),
                half_year_rule_on_sale,
                elections,
            )
        except DomainError as exc:
            # Name the class: the value objects do not know where in the table they sit.
            raise InvalidClassRatesError(f"{entry.where}: {exc}") from exc

    def _election(self, key: str, entry: YamlNode) -> ClassElection:
        code = YamlNode(key, entry.where).parse_whole_number()
        rate = entry.require_mapping(_ELECTION_KEYS).field("rate").parse_decimal()
        try:
            return ClassElection(code, Rate(rate))
        except DomainError as exc:
            raise InvalidClassRatesError(f"{entry.where}: {exc}") from exc
