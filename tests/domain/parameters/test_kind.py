"""Unit tests for ParameterKind: names a kind of parameter and the type it produces."""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_calculator.domain.parameters.claim_reduction import CLAIM_REDUCTION, ClaimReduction
from tax_calculator.domain.parameters.class_rates import CLASS_RATES, ClassRates
from tax_calculator.domain.parameters.conditions import CONDITIONS, ConditionList
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rate_table import RATE_TABLE, RateTable
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.domain.parameters.threshold_rate import THRESHOLD_RATE, ThresholdRate
from tax_calculator.domain.parameters.year_amounts import YEAR_AMOUNTS, YearAmounts


def test_built_in_kinds() -> None:
    assert AMOUNT == ParameterKind("amount", Amount)
    assert BRACKETS == ParameterKind("brackets", BracketSchedule)
    assert CLAIM_REDUCTION == ParameterKind("claim_reduction", ClaimReduction)
    assert CLASS_RATES == ParameterKind("class_rates", ClassRates)
    assert CONDITIONS == ParameterKind("conditions", ConditionList)
    assert CREDIT == ParameterKind("credit", Credit)
    assert RATE == ParameterKind("rate", Rate)
    assert RATE_TABLE == ParameterKind("rate_table", RateTable)
    assert ROUNDING_ONLY == ParameterKind("rounding_only", RoundingOnly)
    assert THRESHOLD_RATE == ParameterKind("threshold_rate", ThresholdRate)
    assert YEAR_AMOUNTS == ParameterKind("year_amounts", YearAmounts)


@pytest.mark.parametrize("name", ["", "Brackets", "flat-rate", "2x", "_x"])
def test_rejects_names_that_are_not_snake_case(name: str) -> None:
    with pytest.raises(ValueError, match="parameter kind name"):
        ParameterKind(name, Decimal)


def test_value_type_must_be_a_type() -> None:
    with pytest.raises(TypeError, match="value_type must be a type"):
        ParameterKind("x", "Decimal")  # type: ignore[arg-type]


def test_kind_is_invariant_in_its_value_type() -> None:
    # Covariance would let mypy widen T and accept a parser whose values do not match its kind.
    (value_type,) = vars(ParameterKind)["__parameters__"]
    assert not (
        value_type.__covariant__
        or value_type.__contravariant__
        or getattr(value_type, "__infer_variance__", False)
    )
