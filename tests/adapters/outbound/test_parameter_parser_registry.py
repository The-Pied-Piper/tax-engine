"""Unit tests for ParameterParserRegistry and `@parameter_parser`.

Parsers are keyed by their kind's plain name (`amount`, `amount_by_count`, `brackets`,
`claim_reduction`, `class_rates`, `conditions`, `contribution_tier`, `credit`, `factor`,
`fraction`, `rate`, `rate_table`, `rounding_only`, `surcharge_tiers`, `taper`, `threshold_rate`,
`year_amounts`), not namespaced yet.
Lookups are typed: `for_kind(kind)` for a `ParameterKind[T]` gives a `ParameterParser[T]`; the
`assert_type` checks below make `mypy .` fail if a lookup returned `Any` or another type.
Made-up kinds and parsers are never registered in the shared registry: the decorator test
points `ParameterParserRegistry.shared` at a fresh registry with monkeypatch.
"""

from __future__ import annotations

from decimal import Decimal
from typing import assert_type

import pytest

import tax_calculator.registrations  # noqa: F401  (fills the capability and parser registries)
from tax_calculator.adapters.outbound.parameter_parsers import ParameterParser
from tax_calculator.adapters.outbound.parameter_parsers.amount import AmountParser
from tax_calculator.adapters.outbound.parameter_parsers.amount_by_count import AmountByCountParser
from tax_calculator.adapters.outbound.parameter_parsers.brackets import BracketsParser
from tax_calculator.adapters.outbound.parameter_parsers.claim_reduction import ClaimReductionParser
from tax_calculator.adapters.outbound.parameter_parsers.class_rates import ClassRatesParser
from tax_calculator.adapters.outbound.parameter_parsers.conditions import ConditionsParser
from tax_calculator.adapters.outbound.parameter_parsers.contribution_tier import (
    ContributionTierParser,
)
from tax_calculator.adapters.outbound.parameter_parsers.credit import CreditParser
from tax_calculator.adapters.outbound.parameter_parsers.factor import FactorParser
from tax_calculator.adapters.outbound.parameter_parsers.fraction import FractionParser
from tax_calculator.adapters.outbound.parameter_parsers.rate import RateParser
from tax_calculator.adapters.outbound.parameter_parsers.rate_table import RateTableParser
from tax_calculator.adapters.outbound.parameter_parsers.registry import (
    ParameterParserRegistry,
    parameter_parser,
)
from tax_calculator.adapters.outbound.parameter_parsers.rounding_only import RoundingOnlyParser
from tax_calculator.adapters.outbound.parameter_parsers.surcharge_tiers import SurchargeTiersParser
from tax_calculator.adapters.outbound.parameter_parsers.taper import TaperParser
from tax_calculator.adapters.outbound.parameter_parsers.threshold_rate import ThresholdRateParser
from tax_calculator.adapters.outbound.parameter_parsers.year_amounts import YearAmountsParser
from tax_calculator.adapters.outbound.yaml_support import YamlNode
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import DuplicateRegistrationError, UnknownRegistrationError
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.amount_by_count import AMOUNT_BY_COUNT, AmountByCount
from tax_calculator.domain.parameters.brackets import BRACKETS, Bracket, BracketSchedule
from tax_calculator.domain.parameters.claim_reduction import CLAIM_REDUCTION
from tax_calculator.domain.parameters.class_rates import (
    CLASS_RATES,
    ClassElection,
    ClassRate,
    ClassRates,
    HalfYearRule,
    HalfYearRuleOnSale,
    RecaptureAndTerminalLoss,
)
from tax_calculator.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_calculator.domain.parameters.contribution_tier import CONTRIBUTION_TIER, ContributionTier
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.factor import FACTOR, Factor
from tax_calculator.domain.parameters.fraction import FRACTION, Fraction
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rate_table import RATE_TABLE, RateTable, RateTableRow
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.domain.parameters.surcharge_tiers import (
    SURCHARGE_TIERS,
    SurchargeTier,
    SurchargeTiers,
)
from tax_calculator.domain.parameters.taper import TAPER, Taper
from tax_calculator.domain.parameters.threshold_rate import THRESHOLD_RATE, ThresholdRate
from tax_calculator.domain.parameters.year_amounts import YEAR_AMOUNTS, YearAmounts, YearAmountsRow
from tax_calculator.domain.registry import Registry

D = Decimal

FLAT_RATE = ParameterKind("flat_rate", Decimal)


class FlatRateParser:
    """A made-up kind's parser, registered only in registries the tests create."""

    kind = FLAT_RATE
    body_keys = frozenset({"rate"})

    def parse(self, document: YamlNode) -> Decimal:
        return document.field("rate").parse_decimal()


class OtherFlatRateParser(FlatRateParser):
    """A second parser for the same made-up kind."""


@pytest.fixture
def fresh(monkeypatch: pytest.MonkeyPatch) -> ParameterParserRegistry:
    """A fresh registry that `@parameter_parser` registers into for the duration of one test."""
    registry = ParameterParserRegistry()
    monkeypatch.setattr(ParameterParserRegistry, "shared", classmethod(lambda cls: registry))
    return registry


# --- typed registration and lookup ------------------------------------------------------------


def test_parameter_parser_registry_is_a_registry() -> None:
    assert issubclass(ParameterParserRegistry, Registry)


def test_register_class_returns_the_class_unchanged() -> None:
    registered = ParameterParserRegistry().register_class(FlatRateParser)

    assert_type(registered, type[FlatRateParser])

    assert registered is FlatRateParser


def test_for_kind_returns_the_parser_registered_for_the_kind() -> None:
    registry = ParameterParserRegistry()
    registry.register_class(BracketsParser)
    registry.register_class(CreditParser)

    found = registry.for_kind(BRACKETS)

    assert_type(found, ParameterParser[BracketSchedule])
    assert isinstance(found, BracketsParser)
    assert found.kind is BRACKETS


def test_for_kind_is_typed_by_the_kind() -> None:
    registry = ParameterParserRegistry()
    registry.register_class(BracketsParser)
    registry.register_class(CreditParser)
    registry.register_class(RateParser)
    registry.register_class(AmountParser)
    registry.register_class(ContributionTierParser)
    registry.register_class(SurchargeTiersParser)
    registry.register_class(TaperParser)
    registry.register_class(ThresholdRateParser)
    registry.register_class(YearAmountsParser)
    registry.register_class(FactorParser)
    registry.register_class(FractionParser)
    registry.register_class(RateTableParser)
    registry.register_class(RoundingOnlyParser)
    registry.register_class(ClassRatesParser)
    registry.register_class(ConditionsParser)
    registry.register_class(AmountByCountParser)
    registry.register_class(FlatRateParser)

    schedule = registry.for_kind(BRACKETS).parse(
        YamlNode.root(
            {"brackets": [{"from": "0", "rate": "0.1"}], "tax_at_start_rounding": "none"}, "dataset"
        )
    )
    credit = registry.for_kind(CREDIT).parse(YamlNode.root({"amount": "100"}, "dataset"))
    rate = registry.for_kind(RATE).parse(YamlNode.root({"rate": "0.5"}, "dataset"))
    amount = registry.for_kind(AMOUNT).parse(YamlNode.root({"amount": "250"}, "dataset"))
    tier = registry.for_kind(CONTRIBUTION_TIER).parse(
        YamlNode.root(
            {"rate": "0.05", "lower": "3000", "upper": "50000", "maximum": "2350"}, "dataset"
        )
    )
    surcharge_tiers = registry.for_kind(SURCHARGE_TIERS).parse(
        YamlNode.root({"tiers": [{"threshold": "100", "rate": "0.2"}]}, "dataset")
    )
    taper = registry.for_kind(TAPER).parse(
        YamlNode.root(
            {"base": "1000", "supplement": "500", "threshold": "20000", "range": "10000"},
            "dataset",
        )
    )
    threshold_rate = registry.for_kind(THRESHOLD_RATE).parse(
        YamlNode.root({"threshold": "52886", "rate": "0.0505"}, "dataset")
    )
    year_amounts = registry.for_kind(YEAR_AMOUNTS).parse(
        YamlNode.root(
            {
                "rows": [
                    {"from_year": 2024, "amounts": {"interest_limit": "350"}},
                    {"amounts": {"interest_limit": "300"}},
                ]
            },
            "dataset",
        )
    )
    factor = registry.for_kind(FACTOR).parse(YamlNode.root({"value": "2"}, "dataset"))
    fraction = registry.for_kind(FRACTION).parse(
        YamlNode.root({"numerator": "2", "denominator": "3"}, "dataset")
    )
    rate_table = registry.for_kind(RATE_TABLE).parse(
        YamlNode.root(
            {
                "rate_at_zero": "0.75",
                "rows": [
                    {"more_than": "0", "not_more_than": "100", "rate": "0.75"},
                    {"more_than": "100", "rate": "0"},
                ],
            },
            "dataset",
        )
    )
    rounding_only = registry.for_kind(ROUNDING_ONLY).parse(YamlNode.root({}, "dataset"))
    class_rates = registry.for_kind(CLASS_RATES).parse(
        YamlNode.root(
            {
                "full_year_days": "365",
                "longest_fiscal_period_days": "366",
                "classes": {
                    "10.1": {
                        "rate": "0.30",
                        "half_year_rule": "applies",
                        "recapture_and_terminal_loss": "excluded",
                        "half_year_rule_on_sale": "applies",
                        "elections": {"1": {"rate": "0.10"}},
                        "aiip_factor": {"numerator": "0", "denominator": "1"},
                        "riip_factor": {"numerator": "1", "denominator": "2"},
                    }
                },
            },
            "dataset",
        )
    )
    conditions = registry.for_kind(CONDITIONS).parse(
        YamlNode.root(
            {
                "count_when_any_applies": "0",
                "conditions": [
                    {
                        "text": "You were bankrupt at any time in 2025",
                        "parts": [
                            {
                                "tests": [
                                    {
                                        "reads": "count",
                                        "position": "1",
                                        "relation": "equal_to",
                                        "than": "1",
                                    }
                                ]
                            }
                        ],
                    }
                ],
            },
            "dataset",
        )
    )
    amount_by_count = registry.for_kind(AMOUNT_BY_COUNT).parse(
        YamlNode.root({"amounts": {"1": "100", "2": "200.50"}}, "dataset")
    )
    flat_rate = registry.for_kind(FLAT_RATE).parse(YamlNode.root({"rate": "0.2"}, "dataset"))

    assert_type(schedule, BracketSchedule)
    assert_type(credit, Credit)
    assert_type(rate, Rate)
    assert_type(amount, Amount)
    assert_type(tier, ContributionTier)
    assert_type(surcharge_tiers, SurchargeTiers)
    assert_type(taper, Taper)
    assert_type(threshold_rate, ThresholdRate)
    assert_type(year_amounts, YearAmounts)
    assert_type(factor, Factor)
    assert_type(fraction, Fraction)
    assert_type(rate_table, RateTable)
    assert_type(rounding_only, RoundingOnly)
    assert_type(class_rates, ClassRates)
    assert_type(conditions, ConditionList)
    assert_type(amount_by_count, AmountByCount)
    assert_type(flat_rate, Decimal)

    assert schedule == BracketSchedule((Bracket(D("0"), D("0.1")),))
    assert credit == Credit(amount=D("100"))
    assert rate == Rate(D("0.5"))
    assert amount == Amount(D("250"))
    assert tier == ContributionTier(Rate(D("0.05")), D("3000"), D("50000"), D("2350"))
    assert surcharge_tiers == SurchargeTiers((SurchargeTier(D("100"), Rate(D("0.2"))),))
    assert taper == Taper(D("1000"), D("500"), D("20000"), D("10000"))
    assert threshold_rate == ThresholdRate(Rate(D("0.0505")), D("52886"))
    assert year_amounts == YearAmounts(
        (
            YearAmountsRow(2024, {"interest_limit": D("350")}),
            YearAmountsRow(None, {"interest_limit": D("300")}),
        )
    )
    assert factor == Factor(D("2"))
    assert fraction == Fraction(2, 3)
    assert rate_table == RateTable(
        Rate(D("0.75")),
        (
            RateTableRow(D("0"), D("100"), Rate(D("0.75"))),
            RateTableRow(D("100"), None, Rate(D("0"))),
        ),
    )
    assert rounding_only == RoundingOnly()
    assert class_rates == ClassRates(
        (
            ClassRate(
                D("10.1"),
                Rate(D("0.30")),
                HalfYearRule.APPLIES,
                RecaptureAndTerminalLoss.EXCLUDED,
                Fraction(0, 1),
                Fraction(1, 2),
                half_year_rule_on_sale=HalfYearRuleOnSale.APPLIES,
                elections=(ClassElection(1, Rate(Decimal("0.10"))),),
            ),
        ),
        full_year_days=365,
        longest_fiscal_period_days=366,
    )
    assert conditions == ConditionList(
        0,
        (
            Condition(
                "You were bankrupt at any time in 2025",
                (ConditionPart((ConditionTest("count", 1, "equal_to", D("1"), None),)),),
            ),
        ),
    )
    assert amount_by_count == AmountByCount(((1, D("100")), (2, D("200.50"))))
    assert flat_rate == D("0.2")


def test_parsers_are_keyed_by_their_kind_name() -> None:
    registry = ParameterParserRegistry()
    registry.register_class(FlatRateParser)

    assert isinstance(registry.get("flat_rate"), FlatRateParser)  # the inherited lookup


def test_registering_two_parsers_for_one_kind_fails() -> None:
    registry = ParameterParserRegistry()
    registry.register_class(FlatRateParser)
    first = registry.for_kind(FLAT_RATE)

    with pytest.raises(DuplicateRegistrationError, match="'flat_rate'"):
        registry.register_class(FlatRateParser)

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


# --- the shared registry ----------------------------------------------------------------------


def test_shared_returns_the_same_instance_every_time() -> None:
    assert ParameterParserRegistry.shared() is ParameterParserRegistry.shared()
    assert isinstance(ParameterParserRegistry.shared(), ParameterParserRegistry)


def test_a_directly_constructed_registry_is_separate_and_empty() -> None:
    registry = ParameterParserRegistry()

    assert registry is not ParameterParserRegistry.shared()
    with pytest.raises(UnknownRegistrationError):
        registry.for_kind(BRACKETS)


def test_shared_parser_registry_is_not_the_shared_capability_registry() -> None:
    assert id(ParameterParserRegistry.shared()) != id(CapabilityRegistry.shared())


# --- the decorator ----------------------------------------------------------------------------


def test_decorator_registers_an_instance_under_its_kind(fresh: ParameterParserRegistry) -> None:
    parameter_parser(FlatRateParser)

    found = fresh.for_kind(FLAT_RATE)

    assert_type(found, ParameterParser[Decimal])
    assert isinstance(found, FlatRateParser)


def test_decorator_returns_the_class_unchanged(fresh: ParameterParserRegistry) -> None:
    decorated = parameter_parser(FlatRateParser)

    assert_type(decorated, type[FlatRateParser])

    assert decorated is FlatRateParser


def test_decorating_a_second_parser_for_one_kind_fails(fresh: ParameterParserRegistry) -> None:
    parameter_parser(FlatRateParser)

    with pytest.raises(DuplicateRegistrationError, match="'flat_rate'"):
        parameter_parser(OtherFlatRateParser)


@pytest.mark.parametrize(
    ("kind", "parser_class"),
    [
        (AMOUNT, AmountParser),
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
def test_built_in_parsers_are_registered_in_the_shared_registry(
    kind: ParameterKind[object], parser_class: type[object]
) -> None:
    parser = ParameterParserRegistry.shared().for_kind(kind)

    assert isinstance(parser, parser_class)
    assert parser.kind is kind


@pytest.mark.parametrize(
    ("parser_class", "body_keys"),
    [
        (AmountParser, frozenset({"amount"})),
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


def test_the_shared_registry_holds_exactly_the_built_in_parsers() -> None:
    assert ParameterParserRegistry.shared().identifiers() == {
        "amount",
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
