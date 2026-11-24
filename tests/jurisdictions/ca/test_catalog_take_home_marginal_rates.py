"""Registered and money kinds of the federal catalog family `take_home_marginal_rates`."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.jurisdictions.ca.catalog import (
    MARGINAL_BASIC_FEDERAL_TAX,
    MARGINAL_CONTRIBUTION_RATE,
    MARGINAL_CPP_BASE_RATE,
    MARGINAL_CPP_FIRST_ADDITIONAL_RATE,
    MARGINAL_CPP_LINE_4,
    MARGINAL_CPP_LINE_7_DIFFERENCE,
    MARGINAL_CPP_SECOND_ADDITIONAL_RATE,
    MARGINAL_CREDIT_CONTRIBUTION_RATE,
    MARGINAL_EI_LINE_1,
    MARGINAL_EI_LINE_7,
    MARGINAL_EI_LINE_7_RATE,
    MARGINAL_EI_LINE_10,
    MARGINAL_EI_PREMIUM_RATE,
    MARGINAL_EI_RATE,
    MARGINAL_FEDERAL_BPA_CREDIT_RATE,
    MARGINAL_FEDERAL_BPA_REDUCTION_RATE,
    MARGINAL_FEDERAL_BRACKET_COLUMN_RATE,
    MARGINAL_FEDERAL_BRACKET_RATE,
    MARGINAL_FEDERAL_CONTRIBUTION_CREDIT_RATE,
    MARGINAL_FEDERAL_CREDIT_RATE,
    MARGINAL_FEDERAL_GATE,
    MARGINAL_FEDERAL_RATE,
    MARGINAL_FEDERAL_RATE_AFTER_CREDITS,
    MARGINAL_FEDERAL_RATE_BEFORE_CREDITS,
    MARGINAL_NET_INCOME,
    MARGINAL_NET_INCOME_RATE,
    MARGINAL_NET_INCOME_RATE_BEFORE_CPP2,
    MARGINAL_PHASE_DOWN_NET_INCOME_RATE,
    MARGINAL_SALARY,
    MARGINAL_SALARY_GATE,
)
from tests.kinds import non_negative

# Each kind is a plain figure of the marginal rate form: a salary, a net income, a printed rate or
# a rate per further dollar of salary (a fraction, 0.2 for 20%), none of them signed.
KINDS = (
    MARGINAL_SALARY,
    MARGINAL_NET_INCOME,
    MARGINAL_FEDERAL_BRACKET_COLUMN_RATE,
    MARGINAL_BASIC_FEDERAL_TAX,
    MARGINAL_FEDERAL_GATE,
    MARGINAL_CPP_BASE_RATE,
    MARGINAL_CPP_FIRST_ADDITIONAL_RATE,
    MARGINAL_CPP_SECOND_ADDITIONAL_RATE,
    MARGINAL_CPP_LINE_7_DIFFERENCE,
    MARGINAL_CPP_LINE_4,
    MARGINAL_EI_LINE_1,
    MARGINAL_EI_LINE_7,
    MARGINAL_EI_LINE_10,
    MARGINAL_EI_PREMIUM_RATE,
    MARGINAL_EI_LINE_7_RATE,
    MARGINAL_EI_RATE,
    MARGINAL_SALARY_GATE,
    MARGINAL_NET_INCOME_RATE_BEFORE_CPP2,
    MARGINAL_NET_INCOME_RATE,
    MARGINAL_CREDIT_CONTRIBUTION_RATE,
    MARGINAL_FEDERAL_CREDIT_RATE,
    MARGINAL_FEDERAL_CONTRIBUTION_CREDIT_RATE,
    MARGINAL_FEDERAL_BRACKET_RATE,
    MARGINAL_PHASE_DOWN_NET_INCOME_RATE,
    MARGINAL_FEDERAL_BPA_REDUCTION_RATE,
    MARGINAL_FEDERAL_BPA_CREDIT_RATE,
    MARGINAL_FEDERAL_RATE_BEFORE_CREDITS,
    MARGINAL_FEDERAL_RATE_AFTER_CREDITS,
    MARGINAL_FEDERAL_RATE,
    MARGINAL_CONTRIBUTION_RATE,
)


def test_the_marginal_rate_kinds_are_registered_non_negative_money(
    registry: ArtifactRegistry,
) -> None:
    for kind in KINDS:
        assert kind.identifier.startswith("ca/marginal_"), kind.identifier
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is True, kind.identifier
        assert registry.get(kind.identifier) is kind


def test_the_marginal_rate_kinds_are_the_whole_family() -> None:
    assert len({kind.identifier for kind in KINDS}) == 30
