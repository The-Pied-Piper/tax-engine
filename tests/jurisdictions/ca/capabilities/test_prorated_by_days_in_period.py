"""Unit tests for the ProratedByDaysInPeriod capability (`ca/prorated_by_days_in_period`), an amount
times a count of days over a count of days of a period, made-up kinds.

Form T2043, Chart A amount 7 "Total number of days in the fiscal period that fall within the 2024
calendar year divided by the total number of days in the fiscal period (if the fiscal period starts
and ends in 2025, enter "0")" and amount 8 "Amount 6 multiplied by amount 7.". Amount 7 is an exact
fraction, so it is not an artifact: the capability forms amount x days / period days as one exact
fraction and rounds it once, which is the T2043 amount 8.

Its slots: one parameter slot, `rounding` (a `rounding_only` dataset); three consumed slots, the
`Decimal` `amount`, the int `days` (the days in 2024) and the int `period_days` (the days of the
fiscal period); and one produced `Decimal` slot `output`. The output is
`rounding.apply(amount x days / period_days)`. Days of 0 give 0 (the form's "enter 0"). Days above
`period_days` are refused (`InputAboveBoundError`, "<kind> 366 is above the maximum 365"), as the
T2042 fiscal period days are. It records one `ProratedByDaysInPeriodLine` (in
`tax_engine.jurisdictions.ca.trace`) with the output, the amount's kind and value, the days'
kind and
value, the period days' kind and value and the result, in that order.

Worked values, each an exact fraction rounded half-up to the cent: 36500 x 184 / 365 = 18400
exactly; 18250 x 184 / 365 = 9200 exactly; 20000 x 184 / 365 = 3680000 / 365 = 10082.1917...,
so 10082.19; 36500 x 0 / 365 = 0.
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from decimal import Decimal
from types import MappingProxyType
from typing import assert_type, cast

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import (
    InputAboveBoundError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.jurisdictions.ca.capabilities.prorated_by_days_in_period import (
    ProratedByDaysInPeriod,
)
from tax_engine.jurisdictions.ca.trace import ProratedByDaysInPeriodLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
DOLLAR = RoundTo(D("1"), RoundingMode.HALF_UP)

LIMIT = ArtifactKind("ex/limit", Decimal)
DAYS = ArtifactKind("ex/days", int)
PERIOD_DAYS = ArtifactKind("ex/period_days", int)
PRORATED = ArtifactKind("ex/limit_prorated", Decimal)


def rounding(rule: RoundingRule = CENT) -> ParameterDataset[RoundingOnly]:
    """By default half-up to the cent."""
    return ParameterDataset(
        "ex/limit_rounding",
        2025,
        ROUNDING_ONLY,
        RoundingOnly(),
        rule,
        ("https://example.org/rounding",),
    )


def capability(rule: RoundingRule = CENT) -> ProratedByDaysInPeriod:
    return ProratedByDaysInPeriod(rounding(rule), LIMIT, DAYS, PERIOD_DAYS, PRORATED)


def inputs(
    amount: str, days: int, period_days: int = 365
) -> tuple[Artifact[Decimal] | Artifact[int], ...]:
    return (
        Artifact(LIMIT, D(amount)),
        Artifact(DAYS, days),
        Artifact(PERIOD_DAYS, period_days),
    )


def prorated(amount: str, days: int, period_days: int = 365, rule: RoundingRule = CENT) -> Decimal:
    (output,) = capability(rule).compute(inputs(amount, days, period_days)).outputs
    assert isinstance(output.value, Decimal)
    return output.value


def test_is_registered_as_ca_prorated_by_days_in_period() -> None:
    registered = CapabilityRegistry.shared().get("ca/prorated_by_days_in_period")

    assert registered is ProratedByDaysInPeriod


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "prorated_by_days_in_period" in ca_capabilities.__all__
    assert (
        ca_capabilities.prorated_by_days_in_period.ProratedByDaysInPeriod is ProratedByDaysInPeriod
    )


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({LIMIT, DAYS, PERIOD_DAYS})
    assert capability().produces == frozenset({PRORATED})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(ProratedByDaysInPeriod)
    assert "produces" not in vars(ProratedByDaysInPeriod)


def test_declares_its_slots() -> None:
    assert ProratedByDaysInPeriod.PARAMETERS == {"rounding": ROUNDING_ONLY}
    assert ProratedByDaysInPeriod.CONSUMES == {
        "amount": Decimal,
        "days": int,
        "period_days": int,
    }
    assert ProratedByDaysInPeriod.PRODUCES == {"output": Decimal}


def test_its_slots_are_read_only() -> None:
    for each in (
        ProratedByDaysInPeriod.PARAMETERS,
        ProratedByDaysInPeriod.CONSUMES,
        ProratedByDaysInPeriod.PRODUCES,
    ):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast("MutableMapping[str, object]", each)["extra"] = int


def test_its_consumed_and_produced_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(ProratedByDaysInPeriod.CONSUMES, Mapping[str, type])
    assert_type(ProratedByDaysInPeriod.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = ProratedByDaysInPeriod(
        rounding=rounding(),
        amount=LIMIT,
        days=DAYS,
        period_days=PERIOD_DAYS,
        output=PRORATED,
    )

    (output,) = wired.compute(inputs("36500", 184)).outputs
    assert output == Artifact(PRORATED, D("18400.00"))


def test_rejects_an_int_kind_for_the_amount() -> None:
    int_kind = cast("Money", ArtifactKind("ex/count", int))

    with pytest.raises(InvalidCapabilityError, match="ProratedByDaysInPeriod.*'amount'"):
        ProratedByDaysInPeriod(rounding(), int_kind, DAYS, PERIOD_DAYS, PRORATED)


def test_rejects_a_money_kind_for_the_days() -> None:
    money_kind = cast("ArtifactKind[int]", ArtifactKind("ex/money", Decimal))

    with pytest.raises(InvalidCapabilityError, match="ProratedByDaysInPeriod.*'days'"):
        ProratedByDaysInPeriod(rounding(), LIMIT, money_kind, PERIOD_DAYS, PRORATED)


def test_rejects_a_money_kind_for_the_period_days() -> None:
    money_kind = cast("ArtifactKind[int]", ArtifactKind("ex/money", Decimal))

    with pytest.raises(InvalidCapabilityError, match="ProratedByDaysInPeriod.*'period_days'"):
        ProratedByDaysInPeriod(rounding(), LIMIT, DAYS, money_kind, PRORATED)


def test_rejects_one_kind_as_both_amount_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="ProratedByDaysInPeriod") as raised:
        ProratedByDaysInPeriod(rounding(), LIMIT, DAYS, PERIOD_DAYS, LIMIT)

    assert "'amount'" in str(raised.value)
    assert "'output'" in str(raised.value)


@pytest.mark.parametrize(
    ("amount", "days", "expected"),
    [
        # Ontario's amount 6 of 36,500 for 184 days of 2024 in a 365-day period: exact.
        ("36500", 184, "18400.00"),
        # Manitoba's amount 6 of 18,250, the same split.
        ("18250", 184, "9200.00"),
        # 20,000 x 184 / 365 = 10082.1917..., rounded once to the cent.
        ("20000", 184, "10082.19"),
        # A period that starts and ends in 2025: no day in 2024, so 0 (the form's "enter 0").
        ("36500", 0, "0.00"),
        # Every day of the period in 2024: the whole amount.
        ("36500", 365, "36500.00"),
        # An amount of 0 stays 0.
        ("0", 184, "0.00"),
    ],
)
def test_multiplies_by_the_days_over_the_period_days_and_rounds_once(
    amount: str, days: int, expected: str
) -> None:
    assert prorated(amount, days) == D(expected)


def test_the_dataset_decides_the_rounding() -> None:
    assert prorated("20000", 184, rule=DOLLAR) == D("10082")


def test_under_no_rounding_a_product_that_is_exact_stays_exact() -> None:
    assert prorated("36500", 184, rule=NO_ROUNDING) == D("18400")


def test_days_in_a_longer_period_are_prorated_by_that_period() -> None:
    # A 183-day period with 183 days in 2024 is not prorated: the whole amount.
    assert prorated("36500", 183, period_days=183) == D("36500.00")


def test_the_output_is_a_decimal_of_the_produced_kind() -> None:
    (output,) = capability().compute(inputs("36500", 184)).outputs

    assert output.kind == PRORATED
    assert type(output.value) is Decimal


def test_days_above_the_period_days_are_refused_naming_the_kind_and_the_maximum() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        prorated("36500", 366)

    assert str(raised.value) == "ex/days 366 is above the maximum 365"


def test_days_above_a_shorter_period_are_refused() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        prorated("36500", 200, period_days=180)

    assert str(raised.value) == "ex/days 200 is above the maximum 180"


@pytest.mark.parametrize("missing", [0, 1, 2])
def test_a_missing_consumed_artifact_is_a_missing_artifact(missing: int) -> None:
    given = tuple(a for i, a in enumerate(inputs("36500", 184)) if i != missing)

    with pytest.raises(MissingArtifactError):
        capability().compute(given)


def test_traces_one_prorated_by_days_in_period_line() -> None:
    result = capability().compute(inputs("36500", 184))

    assert result.trace == (
        ProratedByDaysInPeriodLine(
            PRORATED, LIMIT, D("36500"), DAYS, 184, PERIOD_DAYS, 365, D("18400.00")
        ),
    )


def test_the_line_carries_the_period_days_of_the_fiscal_period() -> None:
    result = capability().compute(inputs("18250", 184, period_days=366))

    assert result.trace == (
        ProratedByDaysInPeriodLine(
            PRORATED, LIMIT, D("18250"), DAYS, 184, PERIOD_DAYS, 366, D("9174.86")
        ),
    )
