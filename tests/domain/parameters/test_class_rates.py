"""Unit tests for ClassRates: a yearly table of classes and their rates, the `class_rates` kind.

A class-rate table is one entry per class, keyed by the class number as printed: each `ClassRate`
holds its `class_number` (an exact `Decimal`, so "10.1" is a number), its `rate` (a `Rate`),
whether the half-year rule applies to it or it is exempt (`HalfYearRule`), whether recapture and a
terminal loss apply to it or it is excluded (`RecaptureAndTerminalLoss`), and its two factors, the
`aiip_factor` and the `riip_factor`, each a `Fraction` (the `fraction` kind's value, which accepts
a numerator of 0, since a form can print a factor of 0, and refuses a negative part itself), kept
as given, never reduced. Like `RateTable`, the value objects only hold and check the table:
at least one class, no class number twice (by value, so "10.1" and "10.10" are the same class),
the classes kept in the order given. `for_class` finds a class by its number, or `None` for a
class the table does not list. Values are made up.

A class may also list `elections`, a tuple of `ClassElection`: each a whole `code` above 0 and the
`rate` (a `Rate`) a row takes when the caller elects it (Guide T4036 2025, "Class 1 (4%)": 10% for
a new purpose-built residential rental, and, by election into a separate class, 6% or 10% for a
non-residential building). `election_rate(code)` gives the rate of a listed code, or `None` for a
code the class does not list (and for 0, which is no election). The codes of a class are unique;
the elections default to none, and are kept in the order given.
"""

from __future__ import annotations

import fractions
from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from typing import Any, cast

import pytest

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
from tax_engine.domain.parameters.fraction import Fraction
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import Rate

D = Decimal
F = Fraction
APPLIES = HalfYearRule.APPLIES
EXEMPT = HalfYearRule.EXEMPT
INCLUDED = RecaptureAndTerminalLoss.APPLIES
EXCLUDED = RecaptureAndTerminalLoss.EXCLUDED
ON_SALE = HalfYearRuleOnSale.APPLIES
NOT_ON_SALE = HalfYearRuleOnSale.DOES_NOT_APPLY
ZERO = F(0, 1)
ONE_HALF = F(1, 2)


def entry(
    number: str,
    rate: str = "0.20",
    half_year_rule: HalfYearRule = APPLIES,
    recapture_and_terminal_loss: RecaptureAndTerminalLoss = INCLUDED,
    aiip_factor: Fraction = ZERO,
    riip_factor: Fraction = ONE_HALF,
    half_year_rule_on_sale: HalfYearRuleOnSale = NOT_ON_SALE,
) -> ClassRate:
    return ClassRate(
        class_number=D(number),
        rate=Rate(D(rate)),
        half_year_rule=half_year_rule,
        recapture_and_terminal_loss=recapture_and_terminal_loss,
        aiip_factor=aiip_factor,
        riip_factor=riip_factor,
        half_year_rule_on_sale=half_year_rule_on_sale,
    )


def with_elections(*elections: ClassElection) -> ClassRate:
    return ClassRate(
        D("1"),
        Rate(D("0.04")),
        APPLIES,
        INCLUDED,
        ZERO,
        ONE_HALF,
        NOT_ON_SALE,
        elections,
    )


def first() -> ClassRate:
    return entry("8")


def decimal_class() -> ClassRate:
    return entry("10.1", "0.30", recapture_and_terminal_loss=EXCLUDED)


def exempt() -> ClassRate:
    return entry("12", "1", half_year_rule=EXEMPT, riip_factor=F(0, 1))


def table(*classes: ClassRate) -> ClassRates:
    return ClassRates(
        classes=classes or (first(), decimal_class(), exempt()),
        full_year_days=365,
        longest_fiscal_period_days=366,
    )


# --- the two choices ---------------------------------------------------------------------------


def test_the_half_year_rule_applies_or_is_exempt() -> None:
    assert [rule.value for rule in HalfYearRule] == ["applies", "exempt"]
    assert HalfYearRule("applies") is HalfYearRule.APPLIES
    assert HalfYearRule("exempt") is HalfYearRule.EXEMPT


def test_recapture_and_terminal_loss_apply_or_are_excluded() -> None:
    assert [choice.value for choice in RecaptureAndTerminalLoss] == ["applies", "excluded"]
    assert RecaptureAndTerminalLoss("applies") is RecaptureAndTerminalLoss.APPLIES
    assert RecaptureAndTerminalLoss("excluded") is RecaptureAndTerminalLoss.EXCLUDED


def test_the_half_year_rule_on_sale_applies_or_does_not() -> None:
    assert [choice.value for choice in HalfYearRuleOnSale] == ["applies", "does_not_apply"]
    assert HalfYearRuleOnSale("applies") is HalfYearRuleOnSale.APPLIES
    assert HalfYearRuleOnSale("does_not_apply") is HalfYearRuleOnSale.DOES_NOT_APPLY


# --- one class ---------------------------------------------------------------------------------


def test_a_class_holds_its_number_rate_rules_and_factors() -> None:
    held = entry("43.1", "0.30", aiip_factor=F(3, 2), riip_factor=F(7, 3))

    assert held.class_number == D("43.1")
    assert held.rate == Rate(D("0.30"))
    assert held.half_year_rule is HalfYearRule.APPLIES
    assert held.recapture_and_terminal_loss is RecaptureAndTerminalLoss.APPLIES
    assert held.aiip_factor == F(3, 2)
    assert held.riip_factor == F(7, 3)


def test_a_class_holds_its_fields_in_order() -> None:
    assert [field.name for field in fields(ClassRate)] == [
        "class_number",
        "rate",
        "half_year_rule",
        "recapture_and_terminal_loss",
        "aiip_factor",
        "riip_factor",
        "half_year_rule_on_sale",
        "elections",
    ]


def test_a_class_without_a_half_year_rule_on_sale_is_refused() -> None:
    with pytest.raises(TypeError, match="half_year_rule_on_sale"):
        ClassRate(D("8"), Rate(D("0.20")), APPLIES, INCLUDED, F(0, 1), F(1, 2))  # type: ignore[call-arg]


def test_a_class_holds_the_half_year_rule_on_sale() -> None:
    held = entry(
        "10.1", "0.30", recapture_and_terminal_loss=EXCLUDED, half_year_rule_on_sale=ON_SALE
    )

    assert held.half_year_rule_on_sale is HalfYearRuleOnSale.APPLIES


def test_a_class_is_built_positionally_in_field_order() -> None:
    assert (
        ClassRate(D("8"), Rate(D("0.20")), APPLIES, INCLUDED, F(0, 1), F(1, 2), NOT_ON_SALE)
        == first()
    )


def test_a_class_keeps_its_number_exact() -> None:
    assert str(decimal_class().class_number) == "10.1"
    assert str(entry("43.10").class_number) == "43.10"


def test_a_class_may_have_factors_of_zero() -> None:
    held = entry("12", aiip_factor=F(0, 1), riip_factor=F(0, 1))

    assert (held.aiip_factor, held.riip_factor) == (F(0, 1), F(0, 1))


def test_a_class_may_have_factors_above_one() -> None:
    held = entry("44", "0.25", aiip_factor=F(3, 1), riip_factor=F(9, 11))

    assert (held.aiip_factor, held.riip_factor) == (F(3, 1), F(9, 11))


def test_keeps_its_factors_as_given() -> None:
    # Not reduced: 4/8 stays 4/8, and 0/3 stays 0/3, as the dataset writes them.
    held = entry("8", aiip_factor=F(0, 3), riip_factor=F(4, 8))

    assert (held.aiip_factor.numerator, held.aiip_factor.denominator) == (0, 3)
    assert (held.riip_factor.numerator, held.riip_factor.denominator) == (4, 8)
    assert type(held.aiip_factor) is Fraction
    assert type(held.riip_factor) is Fraction


def test_a_class_may_have_a_rate_of_one() -> None:
    assert exempt().rate == Rate(D("1"))


def test_equal_classes_are_equal() -> None:
    assert entry("8", "0.2") == entry("8.0", "0.20")
    assert entry("8") != entry("8", "0.30")
    assert entry("8") != entry("8", half_year_rule=EXEMPT)
    assert entry("8") != entry("8", recapture_and_terminal_loss=EXCLUDED)
    assert entry("8") != entry("8", half_year_rule_on_sale=ON_SALE)
    assert entry("8") != entry("8", aiip_factor=F(1, 2))
    assert entry("8") != entry("8", riip_factor=F(1, 1))
    assert entry("8") != entry("10")


def test_a_class_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, first()).rate = Rate(D("0.5"))


def test_a_class_is_hashable() -> None:
    assert hash(first()) == hash(first())


@pytest.mark.parametrize("value", [8, 8.0, "8", F(8, 1)])
def test_rejects_a_class_number_that_is_not_a_decimal(value: object) -> None:
    with pytest.raises(TypeError, match="class_number must be a Decimal"):
        ClassRate(value, Rate(D("0.2")), APPLIES, INCLUDED, F(0, 1), F(1, 2), NOT_ON_SALE)  # type: ignore[arg-type]


@pytest.mark.parametrize("number", ["Infinity", "-Infinity", "NaN"])
def test_rejects_a_class_number_that_is_not_finite(number: str) -> None:
    with pytest.raises(InvalidClassRatesError, match="class_number must be finite"):
        entry(number)


@pytest.mark.parametrize("number", ["0", "-1", "-10.1"])
def test_rejects_a_class_number_that_is_not_positive(number: str) -> None:
    with pytest.raises(InvalidClassRatesError, match="class_number must be positive"):
        entry(number)


@pytest.mark.parametrize("rate", [D("0.2"), 0.2, "0.2"])
def test_rejects_a_rate_that_is_not_a_rate(rate: object) -> None:
    with pytest.raises(TypeError, match="rate must be a Rate"):
        ClassRate(D("8"), rate, APPLIES, INCLUDED, F(0, 1), F(1, 2), NOT_ON_SALE)  # type: ignore[arg-type]


@pytest.mark.parametrize("rule", ["applies", True, RecaptureAndTerminalLoss.APPLIES])
def test_rejects_a_half_year_rule_that_is_not_one(rule: object) -> None:
    with pytest.raises(TypeError, match="half_year_rule must be a HalfYearRule"):
        ClassRate(D("8"), Rate(D("0.2")), rule, INCLUDED, F(0, 1), F(1, 2), NOT_ON_SALE)  # type: ignore[arg-type]


@pytest.mark.parametrize("choice", ["applies", False, HalfYearRule.APPLIES])
def test_rejects_a_recapture_and_terminal_loss_choice_that_is_not_one(choice: object) -> None:
    with pytest.raises(
        TypeError, match="recapture_and_terminal_loss must be a RecaptureAndTerminalLoss"
    ):
        ClassRate(D("8"), Rate(D("0.2")), APPLIES, choice, F(0, 1), F(1, 2), NOT_ON_SALE)  # type: ignore[arg-type]


@pytest.mark.parametrize("choice", ["applies", True, HalfYearRule.APPLIES, None])
def test_rejects_a_half_year_rule_on_sale_that_is_not_one(choice: object) -> None:
    with pytest.raises(TypeError, match="half_year_rule_on_sale must be a HalfYearRuleOnSale"):
        entry("8", half_year_rule_on_sale=choice)  # type: ignore[arg-type]


@pytest.mark.parametrize("factor", ["aiip_factor", "riip_factor"])
@pytest.mark.parametrize(
    ("value", "type_name"),
    [
        (0, "int"),
        (1, "int"),
        (True, "bool"),
        (D("0.5"), "Decimal"),
        (0.5, "float"),
        ("1/2", "str"),
        # The standard library's fraction is not the `fraction` kind's value.
        (fractions.Fraction(1, 2), "Fraction"),
        ((1, 2), "tuple"),
    ],
)
def test_rejects_a_factor_that_is_not_a_fraction(
    factor: str, value: object, type_name: str
) -> None:
    parts: dict[str, object] = {
        "aiip_factor": F(0, 1),
        "riip_factor": F(1, 2),
        "half_year_rule_on_sale": NOT_ON_SALE,
    }
    parts[factor] = value

    with pytest.raises(TypeError, match=f"{factor} must be a Fraction, got {type_name}"):
        ClassRate(D("8"), Rate(D("0.2")), APPLIES, INCLUDED, **parts)  # type: ignore[arg-type]


# --- elections ---------------------------------------------------------------------------------


def test_an_election_holds_its_code_and_rate_in_order() -> None:
    held = ClassElection(2, Rate(D("0.06")))

    assert [field.name for field in fields(ClassElection)] == ["code", "rate"]
    assert (held.code, held.rate) == (2, Rate(D("0.06")))
    assert held == ClassElection(2, Rate(D("0.06")))
    assert held != ClassElection(3, Rate(D("0.06")))
    assert held != ClassElection(2, Rate(D("0.10")))
    assert hash(held) == hash(ClassElection(2, Rate(D("0.06"))))
    with pytest.raises(FrozenInstanceError):
        cast(Any, held).code = 3


@pytest.mark.parametrize("code", [0, -1])
def test_rejects_an_election_code_that_is_not_above_zero(code: int) -> None:
    with pytest.raises(InvalidClassRatesError, match="code must be above 0"):
        ClassElection(code, Rate(D("0.10")))


@pytest.mark.parametrize("code", [1.0, "1", D("1"), True, None])
def test_rejects_an_election_code_that_is_not_a_whole_number(code: object) -> None:
    with pytest.raises(TypeError, match="code must be an int"):
        ClassElection(code, Rate(D("0.10")))  # type: ignore[arg-type]


@pytest.mark.parametrize("rate", [D("0.10"), 0.1, "0.10", None])
def test_rejects_an_election_rate_that_is_not_a_rate(rate: object) -> None:
    with pytest.raises(TypeError, match="rate must be a Rate"):
        ClassElection(1, rate)  # type: ignore[arg-type]


def test_a_class_has_no_elections_by_default() -> None:
    assert first().elections == ()
    assert first().election_rate(1) is None


def test_a_class_holds_its_elections_in_the_order_given() -> None:
    purpose_built = ClassElection(1, Rate(D("0.10")))
    other = ClassElection(2, Rate(D("0.06")))

    assert with_elections(other, purpose_built).elections == (other, purpose_built)
    assert with_elections(purpose_built, other).elections == (purpose_built, other)
    assert with_elections(purpose_built) != with_elections()
    assert with_elections(purpose_built, other) != with_elections(other, purpose_built)


def test_a_class_gives_the_rate_of_a_listed_election() -> None:
    held = with_elections(
        ClassElection(1, Rate(D("0.10"))),
        ClassElection(2, Rate(D("0.06"))),
        ClassElection(3, Rate(D("0.10"))),
    )

    assert held.election_rate(1) == Rate(D("0.10"))
    assert held.election_rate(2) == Rate(D("0.06"))
    assert held.election_rate(3) == Rate(D("0.10"))


def test_a_class_gives_no_rate_for_a_code_it_does_not_list() -> None:
    held = with_elections(ClassElection(1, Rate(D("0.10"))))

    assert held.election_rate(2) is None
    assert held.election_rate(0) is None
    assert first().election_rate(1) is None


def test_a_class_is_built_positionally_with_elections_last() -> None:
    purpose_built = ClassElection(1, Rate(D("0.10")))

    assert ClassRate(
        D("1"), Rate(D("0.04")), APPLIES, INCLUDED, ZERO, ONE_HALF, NOT_ON_SALE, (purpose_built,)
    ) == with_elections(purpose_built)


def test_rejects_an_election_code_listed_twice() -> None:
    with pytest.raises(InvalidClassRatesError, match="election 1 is listed more than once"):
        with_elections(ClassElection(1, Rate(D("0.10"))), ClassElection(1, Rate(D("0.06"))))


@pytest.mark.parametrize("elections", [[ClassElection(1, Rate(D("0.10")))], "elections", None])
def test_rejects_elections_that_are_not_a_tuple(elections: object) -> None:
    with pytest.raises(TypeError, match="elections must be a tuple"):
        ClassRate(
            D("1"),
            Rate(D("0.04")),
            APPLIES,
            INCLUDED,
            ZERO,
            ONE_HALF,
            NOT_ON_SALE,
            elections,  # type: ignore[arg-type]
        )


def test_rejects_an_election_that_is_not_an_election() -> None:
    with pytest.raises(TypeError, match="elections must hold ClassElection"):
        with_elections((1, Rate(D("0.10"))))  # type: ignore[arg-type]


# --- the table ---------------------------------------------------------------------------------


def test_holds_its_classes_in_the_order_given() -> None:
    assert table().classes == (first(), decimal_class(), exempt())
    assert table(exempt(), first()).classes == (exempt(), first())


def test_holds_its_classes_and_the_days_in_a_full_year() -> None:
    assert [field.name for field in fields(ClassRates)] == [
        "classes",
        "full_year_days",
        "longest_fiscal_period_days",
    ]


def test_is_built_positionally() -> None:
    assert ClassRates((first(), decimal_class(), exempt()), 365, 366) == table()


def test_a_single_class_is_enough() -> None:
    assert table(first()).classes == (first(),)


def test_equal_tables_are_equal() -> None:
    assert table(first()) == table(entry("8.0", "0.2"))
    assert table(first()) != table(entry("8", "0.3"))
    assert table(first(), exempt()) != table(exempt(), first())


def test_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, table()).classes = (first(),)


def test_is_hashable() -> None:
    assert hash(table()) == hash(table())


def test_rejects_no_classes() -> None:
    with pytest.raises(InvalidClassRatesError, match="at least one class"):
        ClassRates((), 365, 366)


def test_rejects_a_class_listed_twice() -> None:
    with pytest.raises(InvalidClassRatesError, match="class 8 is listed more than once"):
        table(first(), exempt(), entry("8", "0.30"))


def test_rejects_a_class_listed_twice_with_another_spelling_of_its_number() -> None:
    with pytest.raises(InvalidClassRatesError, match="listed more than once"):
        table(decimal_class(), entry("10.10"))


@pytest.mark.parametrize("classes", [[first()], "classes", None])
def test_rejects_classes_that_are_not_a_tuple(classes: object) -> None:
    with pytest.raises(TypeError, match="classes must be a tuple"):
        ClassRates(classes, 365, 366)  # type: ignore[arg-type]


def test_rejects_a_class_that_is_not_a_class_rate() -> None:
    with pytest.raises(TypeError, match=r"classes\[1\] must be a ClassRate, got Rate"):
        ClassRates((first(), Rate(D("0.2"))), 365, 366)  # type: ignore[arg-type]


# --- the days in a full year -------------------------------------------------------------------
# Guide T4002 "You were asking?": "Since your fiscal period is less than 365 days, you have to
# prorate your CCA claim. ... base your CCA claim on the number of days in your fiscal period
# compared to 365 days." The 365 is the dataset's `full_year_days`.


def test_a_table_holds_the_days_in_a_full_year() -> None:
    assert table().full_year_days == 365
    assert ClassRates((first(),), 366, 366).full_year_days == 366


def test_a_table_without_the_days_in_a_full_year_is_refused() -> None:
    with pytest.raises(TypeError, match="full_year_days"):
        ClassRates((first(),))  # type: ignore[call-arg]


def test_tables_with_different_days_in_a_full_year_differ() -> None:
    assert table(first()) != ClassRates((first(),), 366, 366)
    assert hash(table(first())) == hash(ClassRates((first(),), 365, 366))


@pytest.mark.parametrize("days", [0, -1, -365])
def test_rejects_days_in_a_full_year_that_are_not_positive(days: int) -> None:
    with pytest.raises(
        InvalidClassRatesError, match=rf"full_year_days must be positive, got {days}"
    ):
        ClassRates((first(),), days, 366)


@pytest.mark.parametrize("days", [365.0, "365", D("365"), True, None])
def test_rejects_days_in_a_full_year_that_are_not_an_int(days: object) -> None:
    with pytest.raises(TypeError, match="full_year_days must be an int"):
        ClassRates((first(),), days, 366)  # type: ignore[arg-type]


# --- the days in the longest fiscal period ------------------------------------------------------
# Guide T4002 2025: "A fiscal period cannot be longer than 12 months." The longest 12 months have
# 366 days, the dataset's `longest_fiscal_period_days`, never below the days in a full year.


def test_a_table_holds_the_days_in_the_longest_fiscal_period() -> None:
    assert table().longest_fiscal_period_days == 366


def test_a_longest_fiscal_period_equal_to_a_full_year_is_allowed() -> None:
    assert ClassRates((first(),), 365, 365).longest_fiscal_period_days == 365


@pytest.mark.parametrize("days", [364, 0, -1])
def test_rejects_a_longest_fiscal_period_below_a_full_year(days: int) -> None:
    with pytest.raises(
        InvalidClassRatesError,
        match=rf"longest_fiscal_period_days must be at least full_year_days 365, got {days}",
    ):
        ClassRates((first(),), 365, days)


@pytest.mark.parametrize("days", [366.0, "366", D("366"), True, None])
def test_rejects_a_longest_fiscal_period_that_is_not_an_int(days: object) -> None:
    with pytest.raises(TypeError, match="longest_fiscal_period_days must be an int"):
        ClassRates((first(),), 365, days)  # type: ignore[arg-type]


def test_tables_with_different_longest_fiscal_periods_differ() -> None:
    assert ClassRates((first(),), 365, 366) != ClassRates((first(),), 365, 367)


# --- finding a class ---------------------------------------------------------------------------


def test_finds_a_class_by_its_number() -> None:
    assert table().for_class(D("8")) == first()
    assert table().for_class(D("12")) == exempt()


def test_finds_a_class_numbered_with_a_decimal_point() -> None:
    assert table().for_class(D("10.1")) == decimal_class()


def test_finds_a_class_by_the_value_of_its_number() -> None:
    assert table().for_class(D("8.0")) == first()
    assert table().for_class(D("10.10")) == decimal_class()


@pytest.mark.parametrize("number", ["13", "14", "10", "1", "10.2"])
def test_a_class_the_table_does_not_list_is_none(number: str) -> None:
    assert table().for_class(D(number)) is None


# --- the kind ----------------------------------------------------------------------------------


def test_class_rates_kind() -> None:
    assert CLASS_RATES == ParameterKind("class_rates", ClassRates)
    assert CLASS_RATES.name == "class_rates"
    assert CLASS_RATES.value_type is ClassRates


def test_invalid_class_rates_is_a_domain_error() -> None:
    assert issubclass(InvalidClassRatesError, DomainError)
