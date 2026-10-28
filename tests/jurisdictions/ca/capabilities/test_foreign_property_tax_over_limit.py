"""Unit tests for ForeignPropertyTaxOverLimit, the T2209 page 1 note on income from property.

Form T2209, page 1 note: "If you paid tax on income from property sourced outside of Canada (other
than real or immovable property), your non-business foreign tax credit for that income cannot be
more than 15% of your net income from that property. However, you may be able to deduct the part of
the foreign taxes you paid over 15% on line 23200 of your return."

Its slots: one parameter slot, `limit_rate` (a `rate` dataset: the printed 15%, rounded with its
rule); one consumed slot, `countries` (a record list of each country's tax paid and income, and the
parts of them on income from property); one produced slot, `output` (Decimal): the sum over the
countries of the property tax paid less the limit, each not below zero. The dataset family is made
up.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.jurisdictions.ca.capabilities as ca_capabilities
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, ValidationError
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.capabilities.foreign_property_tax_over_limit import (
    ForeignPropertyTaxOverLimit,
)
from tax_calculator.jurisdictions.ca.catalog import (
    FOREIGN_BUSINESS_TAX_PAID,
    FOREIGN_BUSINESS_UNUSED_TAX_CREDITS,
    FOREIGN_NON_BUSINESS_TAX_PAID,
    FOREIGN_PROPERTY_TAX_PAID,
    FOREIGN_SURTAX_OUTSIDE_CANADA,
    FOREIGN_TAX_COUNTRIES,
    NET_FOREIGN_BUSINESS_INCOME,
    NET_FOREIGN_NON_BUSINESS_INCOME,
    NET_FOREIGN_PROPERTY_INCOME,
)
from tax_calculator.jurisdictions.ca.trace import ForeignPropertyTaxLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
OUTPUT = ArtifactKind("ex/over_limit", Decimal, non_negative=True)


def limit_rate(value: str = "0.15") -> ParameterDataset[Rate]:
    return ParameterDataset(
        "ex/property_limit", 2025, RATE, Rate(D(value)), CENT, ("https://example.org/t2209",)
    )


def capability() -> ForeignPropertyTaxOverLimit:
    return ForeignPropertyTaxOverLimit(limit_rate(), FOREIGN_TAX_COUNTRIES, OUTPUT)


def countries(*rows: tuple[str, str, str, str]) -> Artifact[RecordList]:
    """One record per (tax paid, income, property tax paid, property income)."""
    return Artifact(
        FOREIGN_TAX_COUNTRIES,
        RecordList(
            FOREIGN_TAX_COUNTRIES.fields,
            [
                {
                    FOREIGN_NON_BUSINESS_TAX_PAID: D(tax),
                    NET_FOREIGN_NON_BUSINESS_INCOME: D(income),
                    FOREIGN_BUSINESS_TAX_PAID: D(0),
                    FOREIGN_BUSINESS_UNUSED_TAX_CREDITS: D(0),
                    NET_FOREIGN_BUSINESS_INCOME: D(0),
                    FOREIGN_SURTAX_OUTSIDE_CANADA: D(0),
                    FOREIGN_PROPERTY_TAX_PAID: D(property_tax),
                    NET_FOREIGN_PROPERTY_INCOME: D(property_income),
                }
                for tax, income, property_tax, property_income in rows
            ],
        ),
    )


def total(*rows: tuple[str, str, str, str]) -> Decimal:
    (output,) = capability().compute((countries(*rows),)).outputs
    assert isinstance(output.value, Decimal)
    return output.value


# --- contract and wiring ------------------------------------------------------------------------


def test_declares_its_slots() -> None:
    assert ForeignPropertyTaxOverLimit.PARAMETERS == {"limit_rate": RATE}
    assert ForeignPropertyTaxOverLimit.CONSUMES == {"countries": type(countries().value)}
    assert ForeignPropertyTaxOverLimit.PRODUCES == {"output": Decimal}


def test_its_slots_are_read_only() -> None:
    for each in (
        ForeignPropertyTaxOverLimit.PARAMETERS,
        ForeignPropertyTaxOverLimit.CONSUMES,
        ForeignPropertyTaxOverLimit.PRODUCES,
    ):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, each)["extra"] = Decimal


def test_is_registered_as_ca_foreign_property_tax_over_limit() -> None:
    registered = CapabilityRegistry.shared().get("ca/foreign_property_tax_over_limit")

    assert registered is ForeignPropertyTaxOverLimit


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert ca_capabilities.NAMESPACE == "ca"
    assert "foreign_property_tax_over_limit" in ca_capabilities.__all__
    assert (
        ca_capabilities.foreign_property_tax_over_limit.ForeignPropertyTaxOverLimit
        is ForeignPropertyTaxOverLimit
    )


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({FOREIGN_TAX_COUNTRIES})
    assert capability().produces == frozenset({OUTPUT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(ForeignPropertyTaxOverLimit)
    assert "produces" not in vars(ForeignPropertyTaxOverLimit)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(ForeignPropertyTaxOverLimit.PARAMETERS, Mapping[str, ParameterKind[Any]])
    assert_type(ForeignPropertyTaxOverLimit.CONSUMES, Mapping[str, type])
    assert_type(ForeignPropertyTaxOverLimit.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = ForeignPropertyTaxOverLimit(
        limit_rate=limit_rate(), countries=FOREIGN_TAX_COUNTRIES, output=OUTPUT
    )

    (output,) = wired.compute((countries(("6000", "20000", "6000", "20000")),)).outputs
    assert output == Artifact(OUTPUT, D("3000.00"))


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        amount = ParameterDataset(
            "ex/some_amount", 2025, AMOUNT, Amount(D("5")), CENT, ("https://example.org/a",)
        )
        ForeignPropertyTaxOverLimit(
            amount,  # type: ignore[arg-type]
            FOREIGN_TAX_COUNTRIES,
            OUTPUT,
        )

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(ForeignPropertyTaxOverLimit, "__type_params__", ())
    assert not getattr(ForeignPropertyTaxOverLimit, "__parameters__", ())


def test_rejects_a_money_kind_for_its_countries() -> None:
    with pytest.raises(InvalidCapabilityError, match="ForeignPropertyTaxOverLimit.*'countries'"):
        ForeignPropertyTaxOverLimit(limit_rate(), OUTPUT, OUTPUT)  # type: ignore[arg-type]


# --- the amount over the limit ------------------------------------------------------------------


def test_the_ticket_example_has_3000_over_the_limit() -> None:
    # $20,000 of dividends, $6,000 withheld: 15% is 3,000, so 3,000 is over.
    assert total(("6000", "20000", "6000", "20000")) == D("3000.00")


def test_tax_at_or_under_15_percent_has_nothing_over() -> None:
    assert total(("3000", "20000", "3000", "20000")) == D("0")
    assert total(("2000", "20000", "2000", "20000")) == D("0")


def test_tax_on_other_income_is_not_limited() -> None:
    assert total(("6000", "20000", "0", "0")) == D("0")


def test_the_limit_is_rounded_with_the_datasets_rule() -> None:
    # 15% of 1.10 is 0.165, 0.17 half up; 1.00 less 0.17.
    assert total(("1", "1.10", "1", "1.10")) == D("0.83")


def test_each_country_is_worked_on_its_own() -> None:
    # 300 on 1,000 is 150 over; 100 on 1,000 is under: the under country does not offset.
    assert total(("300", "1000", "300", "1000"), ("100", "1000", "100", "1000")) == D("150.00")


def test_no_countries_give_zero() -> None:
    assert total() == D("0")


# --- trace --------------------------------------------------------------------------------------


def test_traces_the_excess_of_each_country_then_the_total() -> None:
    result = capability().compute(
        (countries(("300", "1000", "300", "1000"), ("100", "1000", "100", "1000")),)
    )

    assert result.trace == (
        ForeignPropertyTaxLine(
            OUTPUT, 1, D("300"), D("1000"), D("0.15"), CENT, D("150.00"), D("150.00")
        ),
        ForeignPropertyTaxLine(
            OUTPUT, 2, D("100"), D("1000"), D("0.15"), CENT, D("150.00"), D("0")
        ),
        ItemsTotalLine(OUTPUT, ((1, D("150.00")), (2, D("0"))), D("150.00")),
    )


def test_the_last_trace_line_amount_is_the_output() -> None:
    result = capability().compute((countries(("300", "1000", "300", "1000")),))

    assert result.trace[-1].amount == D("150.00")


# --- refusals -----------------------------------------------------------------------------------


def test_refuses_property_tax_above_the_tax_paid() -> None:
    with pytest.raises(ValidationError, match="country 2.*foreign_property_tax_paid"):
        total(("10", "100", "0", "0"), ("10", "100", "11", "50"))


def test_refuses_property_income_above_the_net_foreign_income() -> None:
    with pytest.raises(ValidationError, match="country 1.*net_foreign_property_income"):
        total(("10", "100", "5", "101"))
