"""Unit tests for ParameterParserRegistry and `@parameter_parser`.

Parsers are keyed by their kind's plain name (`amount`, `amount_by_band`, `amount_by_count`,
`brackets`,
`claim_reduction`, `class_rates`, `conditions`, `contribution_tier`, `credit`, `factor`,
`fraction`, `rate`, `rate_table`, `rounding_only`, `surcharge_tiers`, `taper`, `threshold_rate`,
`year_amounts`), not namespaced yet.
Lookups are typed: `for_kind(kind)` for a `ParameterKind[T]` gives a `ParameterParser[T]`; the
`assert_type` checks below make `mypy .` fail if a lookup returned `Any` or another type.
Made-up kinds and parsers are registered only in registries the tests create.
"""

from __future__ import annotations

from decimal import Decimal
from typing import assert_type

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.parameter_parser import (
    ParameterParser,
    ParameterParserRegistry,
    parameter_parser,
)
from tax_engine.adapters.outbound.yaml_support import YamlNode
from tax_engine.domain.errors import (
    DuplicateRegistrationError,
    InvalidRegistrationError,
    UnknownRegistrationError,
)
from tax_engine.domain.parameters.amount import AMOUNT
from tax_engine.domain.parameters.amount_by_band import AMOUNT_BY_BAND
from tax_engine.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_engine.domain.parameters.class_rates import (
    CLASS_RATES,
)
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
)
from tax_engine.domain.parameters.credit import CREDIT
from tax_engine.domain.parameters.factor import FACTOR
from tax_engine.domain.parameters.fraction import FRACTION
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import RATE
from tax_engine.domain.parameters.rate_table import RATE_TABLE
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.parameters.surcharge_tiers import (
    SURCHARGE_TIERS,
)
from tax_engine.domain.parameters.threshold_rate import THRESHOLD_RATE
from tax_engine.domain.registry import Registry
from tax_engine.jurisdictions.ca.parameter_parsers.amount_by_count import AmountByCountParser
from tax_engine.jurisdictions.ca.parameter_parsers.claim_reduction import ClaimReductionParser
from tax_engine.jurisdictions.ca.parameter_parsers.contribution_tier import (
    ContributionTierParser,
)
from tax_engine.jurisdictions.ca.parameter_parsers.taper import TaperParser
from tax_engine.jurisdictions.ca.parameter_parsers.year_amounts import YearAmountsParser
from tax_engine.jurisdictions.ca.parameter_shapes.amount_by_count import (
    AMOUNT_BY_COUNT,
)
from tax_engine.jurisdictions.ca.parameter_shapes.claim_reduction import CLAIM_REDUCTION
from tax_engine.jurisdictions.ca.parameter_shapes.contribution_tier import (
    CONTRIBUTION_TIER,
)
from tax_engine.jurisdictions.ca.parameter_shapes.taper import TAPER
from tax_engine.jurisdictions.ca.parameter_shapes.year_amounts import (
    YEAR_AMOUNTS,
)
from tax_engine.jurisdictions.core.parameter_parsers.amount import AmountParser
from tax_engine.jurisdictions.core.parameter_parsers.amount_by_band import AmountByBandParser
from tax_engine.jurisdictions.core.parameter_parsers.brackets import BracketsParser
from tax_engine.jurisdictions.core.parameter_parsers.class_rates import ClassRatesParser
from tax_engine.jurisdictions.core.parameter_parsers.conditions import ConditionsParser
from tax_engine.jurisdictions.core.parameter_parsers.credit import CreditParser
from tax_engine.jurisdictions.core.parameter_parsers.factor import FactorParser
from tax_engine.jurisdictions.core.parameter_parsers.fraction import FractionParser
from tax_engine.jurisdictions.core.parameter_parsers.rate import RateParser
from tax_engine.jurisdictions.core.parameter_parsers.rate_table import RateTableParser
from tax_engine.jurisdictions.core.parameter_parsers.rounding_only import RoundingOnlyParser
from tax_engine.jurisdictions.core.parameter_parsers.surcharge_tiers import SurchargeTiersParser
from tax_engine.jurisdictions.core.parameter_parsers.threshold_rate import ThresholdRateParser

FLAT_RATE = ParameterKind("flat_rate", Decimal)


class FlatRateParser:
    """A made-up kind's parser, registered only in registries the tests create."""

    kind = FLAT_RATE
    body_keys = frozenset({"rate"})

    def parse(self, document: YamlNode) -> Decimal:
        return document.field("rate").parse_decimal()


class OtherFlatRateParser(FlatRateParser):
    """A second parser for the same made-up kind."""


# --- typed registration and lookup ------------------------------------------------------------


def test_parameter_parser_registry_is_a_registry() -> None:
    assert issubclass(ParameterParserRegistry, Registry)


def test_register_class_registers_an_instance_under_its_kind() -> None:
    registry = ParameterParserRegistry()
    registry.register_class(FlatRateParser)

    found = registry.for_kind(FLAT_RATE)

    assert_type(found, ParameterParser[Decimal])
    assert isinstance(found, FlatRateParser)


def test_registering_the_same_class_again_changes_nothing() -> None:
    registry = ParameterParserRegistry()
    registry.register_class(FlatRateParser)
    first = registry.for_kind(FLAT_RATE)

    registry.register_class(FlatRateParser)

    assert registry.for_kind(FLAT_RATE) is first


def test_register_class_refuses_a_class_without_a_kind() -> None:
    with pytest.raises(InvalidRegistrationError, match="declares no parameter kind"):
        ParameterParserRegistry().register_class(Decimal)


def test_for_kind_returns_the_parser_registered_for_the_kind() -> None:
    registry = ParameterParserRegistry()
    registry.register_class(BracketsParser)
    registry.register_class(CreditParser)

    found = registry.for_kind(BRACKETS)

    assert_type(found, ParameterParser[BracketSchedule])
    assert isinstance(found, BracketsParser)
    assert found.kind is BRACKETS


def test_parsers_are_keyed_by_their_kind_name() -> None:
    registry = ParameterParserRegistry()
    registry.register_class(FlatRateParser)

    assert isinstance(registry.get("flat_rate"), FlatRateParser)  # the inherited lookup


def test_registering_another_class_for_a_kind_fails() -> None:
    registry = ParameterParserRegistry()
    registry.register_class(FlatRateParser)
    first = registry.for_kind(FLAT_RATE)

    with pytest.raises(DuplicateRegistrationError, match="'flat_rate'"):
        registry.register_class(OtherFlatRateParser)

    assert registry.for_kind(FLAT_RATE) is first  # never silently overridden


def test_getting_a_kind_without_a_parser_fails() -> None:
    registry = ParameterParserRegistry()
    registry.register_class(BracketsParser)

    with pytest.raises(UnknownRegistrationError, match="'flat_rate'"):
        registry.for_kind(FLAT_RATE)


def test_a_kind_with_a_registered_name_but_another_value_type_is_unknown() -> None:
    registry = ParameterParserRegistry()
    registry.register_class(BracketsParser)
    impostor = ParameterKind("brackets", Decimal)

    with pytest.raises(UnknownRegistrationError, match="'brackets'"):
        registry.for_kind(impostor)


def test_a_non_parser_stored_under_a_kind_name_is_unknown() -> None:
    # The inherited string-keyed `register` bypasses `register_class`; `for_kind` must not
    # trust what it finds there.
    registry = ParameterParserRegistry()
    registry.register("brackets", 42)

    with pytest.raises(UnknownRegistrationError, match="'brackets'"):
        registry.for_kind(BRACKETS)


# --- the decorator ----------------------------------------------------------------------------


def test_decorator_returns_the_class_unchanged_and_registers_nothing() -> None:
    decorated = parameter_parser(FlatRateParser)

    assert_type(decorated, type[FlatRateParser])

    assert decorated is FlatRateParser
    with pytest.raises(UnknownRegistrationError):
        ParameterParserRegistry().for_kind(FLAT_RATE)


def test_registering_a_second_parser_for_one_kind_fails() -> None:
    registry = ParameterParserRegistry()
    registry.register_class(FlatRateParser)

    with pytest.raises(DuplicateRegistrationError, match="'flat_rate'"):
        registry.register_class(OtherFlatRateParser)


# --- the registry built at wiring -------------------------------------------------------------


def test_every_call_builds_its_own_registry() -> None:
    assert tax_engine.registrations.parameter_parsers() is not (
        tax_engine.registrations.parameter_parsers()
    )


@pytest.mark.parametrize(
    ("kind", "parser_class"),
    [
        (AMOUNT, AmountParser),
        (AMOUNT_BY_BAND, AmountByBandParser),
        (AMOUNT_BY_COUNT, AmountByCountParser),
        (BRACKETS, BracketsParser),
        (CLAIM_REDUCTION, ClaimReductionParser),
        (CLASS_RATES, ClassRatesParser),
        (CONDITIONS, ConditionsParser),
        (CONTRIBUTION_TIER, ContributionTierParser),
        (CREDIT, CreditParser),
        (FACTOR, FactorParser),
        (FRACTION, FractionParser),
        (RATE, RateParser),
        (RATE_TABLE, RateTableParser),
        (ROUNDING_ONLY, RoundingOnlyParser),
        (SURCHARGE_TIERS, SurchargeTiersParser),
        (TAPER, TaperParser),
        (THRESHOLD_RATE, ThresholdRateParser),
        (YEAR_AMOUNTS, YearAmountsParser),
    ],
)
def test_built_in_parsers_are_registered_by_the_walk(
    kind: ParameterKind[object], parser_class: type[object]
) -> None:
    parser = tax_engine.registrations.parameter_parsers().for_kind(kind)

    assert isinstance(parser, parser_class)
    assert parser.kind is kind


@pytest.mark.parametrize(
    ("parser_class", "body_keys"),
    [
        (AmountParser, frozenset({"amount"})),
        (AmountByBandParser, frozenset({"rows"})),
        (AmountByCountParser, frozenset({"amounts"})),
        (BracketsParser, frozenset({"brackets", "tax_at_start_rounding"})),
        (ClassRatesParser, frozenset({"classes", "full_year_days", "longest_fiscal_period_days"})),
        (ConditionsParser, frozenset({"count_when_any_applies", "conditions"})),
        (ContributionTierParser, frozenset({"rate", "lower", "upper", "maximum"})),
        (CreditParser, frozenset({"amount"})),
        (FactorParser, frozenset({"value"})),
        (FractionParser, frozenset({"numerator", "denominator"})),
        (RateParser, frozenset({"rate"})),
        (RateTableParser, frozenset({"rate_at_zero", "rows"})),
        (RoundingOnlyParser, frozenset()),
        (SurchargeTiersParser, frozenset({"tiers"})),
        (TaperParser, frozenset({"base", "supplement", "threshold", "range"})),
        (ThresholdRateParser, frozenset({"threshold", "rate"})),
        (YearAmountsParser, frozenset({"rows"})),
    ],
)
def test_built_in_parsers_read_their_body_keys(
    parser_class: type[object], body_keys: frozenset[str]
) -> None:
    assert getattr(parser_class(), "body_keys") == body_keys  # noqa: B009


def test_the_walk_finds_exactly_the_built_in_parsers() -> None:
    assert tax_engine.registrations.parameter_parsers().identifiers() == {
        "amount",
        "amount_by_band",
        "amount_by_count",
        "brackets",
        "claim_reduction",
        "class_rates",
        "conditions",
        "contribution_tier",
        "credit",
        "factor",
        "fraction",
        "rate",
        "rate_table",
        "rounding_only",
        "surcharge_tiers",
        "taper",
        "threshold_rate",
        "year_amounts",
    }
