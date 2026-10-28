"""Unit tests for the LoggingTaxCredit capability (`ca/logging_tax_credit`), T1 line 133 by item.

5000-G, "Federal logging tax credit": "To calculate your credit for each province where you
operated, use the lower of the following amounts for each province you had a logging operation
in: 66.6667% of the logging tax that you paid to that province for the year; 6.6667% of your net
logging income in that province for the year. Add up the amounts for all provinces for the year,
up to 6.6667% of your taxable income from line 26000 of your return, ..."

This capability is the per-province half: for each province in the consumed record list, the
lesser of `tax_rate` times the logging tax paid and `income_rate` times the net logging income,
each rounded with its dataset's rule, then the total of those amounts. The cap of line 133 is not
here: it is wired from artifacts in the manifest.

Its slots: two parameter slots `tax_rate` and `income_rate` (`rate` datasets), one consumed slot
`provinces` (a record list whose records hold each province's logging tax paid and net logging
income) and one produced slot `output`. Each province is worked on its own, never pooled: its
amount is rounded once for each side, the lesser is taken, and the output is the sum. It records one
`LoggingTaxCreditLine` per province, by position from 1, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.jurisdictions.ca.capabilities as ca_capabilities
from tax_calculator.domain.artifact import Artifact
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.capabilities.logging_tax_credit import LoggingTaxCredit
from tax_calculator.jurisdictions.ca.catalog import (
    LOGGING_OPERATIONS,
    LOGGING_TAX_PAID,
    NET_LOGGING_INCOME,
    PROVINCES_LOGGING_TAX_CREDIT,
)
from tax_calculator.jurisdictions.ca.trace import LoggingTaxCreditLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
TAX_RATE = "0.666667"
INCOME_RATE = "0.066667"


def rate(family: str, value: str, rounding: RoundingRule = CENT) -> ParameterDataset[Rate]:
    return ParameterDataset(
        family, 2025, RATE, Rate(D(value)), rounding, ("https://example.org/5000-g",)
    )


def capability(
    tax_rate: ParameterDataset[Rate] | None = None,
    income_rate: ParameterDataset[Rate] | None = None,
) -> LoggingTaxCredit:
    """By default the 2025 rates, 66.6667% of the tax paid and 6.6667% of the net income, to the
    cent."""
    return LoggingTaxCredit(
        tax_rate or rate("ca/logging_tax_rate", TAX_RATE),
        income_rate or rate("ca/logging_income_rate", INCOME_RATE),
        LOGGING_OPERATIONS,
        PROVINCES_LOGGING_TAX_CREDIT,
    )


def provinces(*pairs: tuple[str, str]) -> Artifact[Any]:
    """A `ca/logging_operations` artifact of one record per (tax paid, net logging income) pair, in
    the order given."""
    records = [
        {LOGGING_TAX_PAID: D(tax_paid), NET_LOGGING_INCOME: D(net_income)}
        for tax_paid, net_income in pairs
    ]
    return Artifact(LOGGING_OPERATIONS, RecordList(LOGGING_OPERATIONS.fields, records))


def compute(wired: LoggingTaxCredit, *pairs: tuple[str, str]) -> Artifact[Any]:
    (output,) = wired.compute((provinces(*pairs),)).outputs
    return output


def total(*pairs: tuple[str, str]) -> Decimal:
    value = compute(capability(), *pairs).value
    assert isinstance(value, Decimal)
    return value


def test_is_registered_as_ca_logging_tax_credit() -> None:
    assert CapabilityRegistry.shared().get("ca/logging_tax_credit") is LoggingTaxCredit


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert ca_capabilities.NAMESPACE == "ca"
    assert "logging_tax_credit" in ca_capabilities.__all__
    assert ca_capabilities.logging_tax_credit.LoggingTaxCredit is LoggingTaxCredit


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({LOGGING_OPERATIONS})
    assert capability().produces == frozenset({PROVINCES_LOGGING_TAX_CREDIT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(LoggingTaxCredit)
    assert "produces" not in vars(LoggingTaxCredit)


def test_declares_its_slots() -> None:
    assert LoggingTaxCredit.PARAMETERS == {"tax_rate": RATE, "income_rate": RATE}
    assert LoggingTaxCredit.CONSUMES == {"provinces": RecordList}
    assert LoggingTaxCredit.PRODUCES == {"output": Decimal}
    assert not LoggingTaxCredit.is_list_slot("provinces")


def test_its_slots_are_read_only() -> None:
    for slots in (
        LoggingTaxCredit.PARAMETERS,
        LoggingTaxCredit.CONSUMES,
        LoggingTaxCredit.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(LoggingTaxCredit.PARAMETERS, Mapping[str, ParameterKind[Rate]])
    assert_type(LoggingTaxCredit.CONSUMES, Mapping[str, type])
    assert_type(LoggingTaxCredit.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (
        LoggingTaxCredit.PARAMETERS,
        LoggingTaxCredit.CONSUMES,
        LoggingTaxCredit.PRODUCES,
    ):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = LoggingTaxCredit(
        tax_rate=rate("ca/logging_tax_rate", TAX_RATE),
        income_rate=rate("ca/logging_income_rate", INCOME_RATE),
        provinces=LOGGING_OPERATIONS,
        output=PROVINCES_LOGGING_TAX_CREDIT,
    )

    assert compute(wired, ("300", "6000")) == Artifact(PROVINCES_LOGGING_TAX_CREDIT, D("200.00"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        LoggingTaxCredit(  # type: ignore[call-arg]
            rate("ca/logging_tax_rate", TAX_RATE),
            rate("ca/logging_income_rate", INCOME_RATE),
            LOGGING_OPERATIONS,
            PROVINCES_LOGGING_TAX_CREDIT,
            CENT,
        )


def test_rejects_a_money_kind_for_its_provinces() -> None:
    with pytest.raises(InvalidCapabilityError, match="LoggingTaxCredit.*'provinces'"):
        LoggingTaxCredit(
            rate("ca/logging_tax_rate", TAX_RATE),
            rate("ca/logging_income_rate", INCOME_RATE),
            PROVINCES_LOGGING_TAX_CREDIT,  # type: ignore[arg-type]
            PROVINCES_LOGGING_TAX_CREDIT,
        )


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(LoggingTaxCredit, "__type_params__", ())
    assert not getattr(LoggingTaxCredit, "__parameters__", ())


# --- computing: how many provinces ----------------------------------------------------------------


def test_no_logging_provinces_give_zero() -> None:
    output = compute(capability())

    assert output == Artifact(PROVINCES_LOGGING_TAX_CREDIT, D("0"))
    assert type(output.value) is Decimal
    assert not output.value.is_signed()


def test_one_province_gives_the_lesser_of_its_two_amounts() -> None:
    # Acceptance: tax paid 300 gives 300 x 66.6667% = 200.00; net logging income 6,000 gives
    # 6,000 x 6.6667% = 400.00; the lesser is 200.00.
    assert total(("300", "6000")) == D("200.00")


def test_a_province_whose_net_income_side_is_lower_gives_that_side() -> None:
    # Tax paid 900 gives 600.00; net logging income 3,000 gives 200.00; the lesser is 200.00.
    assert total(("900", "3000")) == D("200.00")


def test_a_province_whose_net_income_is_zero_gives_zero() -> None:
    output = compute(capability(), ("300", "0"))

    assert output.value == D("0")
    assert not output.value.is_signed()


def test_a_province_with_no_logging_tax_paid_gives_zero() -> None:
    output = compute(capability(), ("0", "6000"))

    assert output.value == D("0")
    assert not output.value.is_signed()


def test_two_provinces_give_the_sum_of_their_own_lesser_amounts() -> None:
    # Province 1: min(200.00, 400.00) = 200.00. Province 2: min(600.00, 200.00) = 200.00.
    assert total(("300", "6000"), ("900", "3000")) == D("400.00")


def test_provinces_are_never_pooled() -> None:
    # Pooled, 300 + 900 tax gives 800.00 and 6,000 + 3,000 income gives 600.00 (lesser 600.00).
    # Each province on its own gives 200.00 + 200.00 = 400.00.
    assert total(("300", "6000"), ("900", "3000")) != D("600.00")
    assert total(("300", "6000"), ("900", "3000")) == D("400.00")


def test_a_province_with_the_lesser_tax_side_gives_that_side() -> None:
    # Tax paid 300 gives 200.00; net logging income 100,000 gives 6,666.70; the lesser is 200.00.
    assert total(("300", "100000")) == D("200.00")


def test_three_provinces_are_summed_one_by_one() -> None:
    assert total(("300", "6000"), ("900", "3000"), ("150", "1500")) == D("200.00") * 2 + D("100.00")


def test_the_total_does_not_depend_on_the_order() -> None:
    assert total(("300", "6000"), ("900", "3000")) == total(("900", "3000"), ("300", "6000"))


# --- computing: the rates -------------------------------------------------------------------------


def test_the_tax_rate_dataset_supplies_the_tax_side() -> None:
    wired = capability(tax_rate=rate("ca/logging_tax_rate", "0.5"))

    # Tax 300 at 0.5 gives 150.00; net 6,000 at 6.6667% gives 400.00; the lesser is 150.00.
    assert compute(wired, ("300", "6000")).value == D("150.00")


def test_the_income_rate_dataset_supplies_the_income_side() -> None:
    wired = capability(income_rate=rate("ca/logging_income_rate", "0.02"))

    # Tax 300 gives 200.00; net 6,000 at 2% gives 120.00; the lesser is 120.00.
    assert compute(wired, ("300", "6000")).value == D("120.00")


def test_a_different_year_rate_changes_the_result() -> None:
    wired = capability(tax_rate=rate("ca/logging_tax_rate", "0.5"))

    assert compute(wired, ("1000", "1000000")).value == D("500.00")


# --- computing: rounding --------------------------------------------------------------------------


def test_each_side_is_rounded_half_up_to_the_cent_before_the_lesser_is_taken() -> None:
    # 0.5 x 0.01 = 0.005 rounds half-up to 0.01; the income side 0.5 x 1 = 0.5 is above it.
    wired = capability(
        tax_rate=rate("ca/logging_tax_rate", "0.5"),
        income_rate=rate("ca/logging_income_rate", "0.5"),
    )

    assert compute(wired, ("0.01", "1")).value == D("0.01")


def test_the_tax_side_rounding_rule_comes_from_the_tax_rate_dataset() -> None:
    wired = capability(
        tax_rate=rate("ca/logging_tax_rate", "0.5", RoundTo(D("1"), RoundingMode.FLOOR)),
        income_rate=rate("ca/logging_income_rate", INCOME_RATE, NO_ROUNDING),
    )

    # 0.5 x 301 = 150.5, floored to the dollar: 150.
    assert compute(wired, ("301", "6000")).value == D("150")


def test_the_income_side_rounding_rule_comes_from_the_income_rate_dataset() -> None:
    wired = capability(
        tax_rate=rate("ca/logging_tax_rate", TAX_RATE, NO_ROUNDING),
        income_rate=rate("ca/logging_income_rate", "0.5", RoundTo(D("1"), RoundingMode.FLOOR)),
    )

    # Tax 900 gives 600.0003 unrounded; net 1,001 at 0.5 gives 500.5, floored to 500.
    assert compute(wired, ("900", "1001")).value == D("500")


def test_the_rounding_is_done_once_per_province_before_they_are_summed() -> None:
    # Each province: 0.5 x 0.01 = 0.005 -> 0.01, twice: 0.02. Rounding the exact total 0.01 once
    # would give 0.01.
    wired = capability(
        tax_rate=rate("ca/logging_tax_rate", "0.5"),
        income_rate=rate("ca/logging_income_rate", "0.5"),
    )

    assert compute(wired, ("0.01", "1"), ("0.01", "1")).value == D("0.02")


def test_a_rounded_amount_carries_the_increments_scale() -> None:
    assert str(compute(capability(), ("300", "6000")).value) == "200.00"


# --- computing: inputs ----------------------------------------------------------------------------


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(LOGGING_TAX_PAID, D("9"))

    result = capability().compute((other, provinces(("300", "6000"))))

    assert result.outputs == (Artifact(PROVINCES_LOGGING_TAX_CREDIT, D("200.00")),)


def test_missing_provinces_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="logging_operations"):
        capability().compute(())


def test_has_one_output() -> None:
    assert len(capability().compute((provinces(("1", "2")),)).outputs) == 1


# --- trace ----------------------------------------------------------------------------------------


def province_line(
    position: int,
    tax_paid: str,
    net_income: str,
    tax_share: str,
    income_share: str,
    result: str,
    tax_rounding: RoundingRule = CENT,
    income_rounding: RoundingRule = CENT,
) -> Any:
    """The line of one province: `tax_share` and `income_share` are the two sides, each rounded
    with its dataset's rule, and `result` the lesser of them."""
    return LoggingTaxCreditLine(
        output=PROVINCES_LOGGING_TAX_CREDIT,
        position=position,
        tax_paid=D(tax_paid),
        tax_rate=Rate(D(TAX_RATE)),
        tax_share=D(tax_share),
        net_logging_income=D(net_income),
        income_rate=Rate(D(INCOME_RATE)),
        income_share=D(income_share),
        tax_rounding=tax_rounding,
        income_rounding=income_rounding,
        result=D(result),
    )


def test_traces_one_line_per_province_then_the_total() -> None:
    trace = capability().compute((provinces(("300", "6000"), ("900", "3000")),)).trace

    assert trace == (
        province_line(1, "300", "6000", "200.00", "400.00", "200.00"),
        province_line(2, "900", "3000", "600.00", "200.00", "200.00"),
        ItemsTotalLine(
            PROVINCES_LOGGING_TAX_CREDIT,
            ((1, D("200.00")), (2, D("200.00"))),
            D("400.00"),
        ),
    )


def test_traces_the_callers_order_with_positions_from_one() -> None:
    trace = capability().compute((provinces(("900", "3000"), ("300", "6000")),)).trace

    lines = [line for line in trace if isinstance(line, LoggingTaxCreditLine)]
    assert [line.position for line in lines] == [1, 2]
    assert isinstance(trace[0], LoggingTaxCreditLine)
    assert trace[0].tax_paid == D("900")


def test_traces_no_provinces_as_only_an_empty_total() -> None:
    trace = capability().compute((provinces(),)).trace

    assert trace == (ItemsTotalLine(PROVINCES_LOGGING_TAX_CREDIT, (), D("0")),)


def test_traces_the_datasets_rounding_rules() -> None:
    wired = capability(
        tax_rate=rate("ca/logging_tax_rate", "0.5", RoundTo(D("1"), RoundingMode.FLOOR)),
        income_rate=rate("ca/logging_income_rate", INCOME_RATE, NO_ROUNDING),
    )

    (line, _) = wired.compute((provinces(("301", "6000")),)).trace

    assert isinstance(line, LoggingTaxCreditLine)
    assert line.tax_rounding == RoundTo(D("1"), RoundingMode.FLOOR)
    assert line.income_rounding == NO_ROUNDING
    assert line.result == D("150")


def test_the_last_trace_line_amount_is_the_output() -> None:
    result = capability().compute((provinces(("300", "6000"), ("900", "3000")),))

    (output,) = result.outputs
    assert result.trace[-1].amount == output.value
    assert [line.amount for line in result.trace[:-1]] == [D("200.00"), D("200.00")]


def test_the_total_is_the_sum_of_its_items() -> None:
    *_, total_line = capability().compute((provinces(("300", "6000"), ("900", "3000")),)).trace

    assert isinstance(total_line, ItemsTotalLine)
    assert total_line.total == sum((amount for _, amount in total_line.items), D("0"))


def test_compute_is_repeatable() -> None:
    wired = capability()
    given = (provinces(("300", "6000"), ("900", "3000")),)

    assert wired.compute(given) == wired.compute(given)
