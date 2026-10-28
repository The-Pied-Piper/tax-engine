"""Unit tests for the CaregiverAmount capability (`ca/caregiver_amount`), T1 line 30450.

Schedule 5, "Line 30450 - Canada caregiver amount for other infirm dependants age 18 or older":
"Complete the chart below for each dependant who meets the conditions above." Per dependant, line
1 "Base amount 28,798.00" less line 2 "Infirm dependant's net income from line 23600 of their
return" is line 3 ("if negative, enter "0") (maximum $8,601)"; "Enter on line 30450 of your return
the total of allowable amounts claimed for all dependants."

Its slots: two parameter slots `base` and `maximum` (`amount` datasets), one consumed slot
`dependants` (a record list whose records hold each dependant's net income) and one produced slot
`output`. Each dependant is worked on its own, never pooled: the allowable amount is the base less
that dependant's net income, at least 0 and at most the maximum, rounded once with the `maximum`
dataset's rule, and the output is their total. It records one
`CaregiverClaimLine` per dependant, then an `ItemsTotalLine`.
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
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.capabilities.caregiver_amount import CaregiverAmount
from tax_calculator.jurisdictions.ca.catalog import (
    CAREGIVER_AMOUNT,
    DEPENDANT_NET_INCOME,
    INFIRM_DEPENDANTS,
)
from tax_calculator.jurisdictions.ca.trace import CaregiverClaimLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


def amount(family: str, value: str, rounding: RoundingRule = CENT) -> ParameterDataset[Amount]:
    return ParameterDataset(
        family, 2025, AMOUNT, Amount(D(value)), rounding, ("https://example.org/s5",)
    )


def capability(
    base: ParameterDataset[Amount] | None = None,
    maximum: ParameterDataset[Amount] | None = None,
) -> CaregiverAmount:
    """By default the 2025 figures: the base 28,798.00 and the maximum 8,601, to the cent."""
    return CaregiverAmount(
        base or amount("ca/caregiver_base_amount", "28798.00"),
        maximum or amount("ca/caregiver_maximum_amount", "8601"),
        INFIRM_DEPENDANTS,
        CAREGIVER_AMOUNT,
    )


def dependants(*net_incomes: str) -> Artifact[Any]:
    """An `ca/infirm_dependants` artifact of one record per net income, in the order given."""
    records = [{DEPENDANT_NET_INCOME: D(net_income)} for net_income in net_incomes]
    return Artifact(INFIRM_DEPENDANTS, RecordList(INFIRM_DEPENDANTS.fields, records))


def compute(wired: CaregiverAmount, *net_incomes: str) -> Artifact[Any]:
    (output,) = wired.compute((dependants(*net_incomes),)).outputs
    return output


def total(*net_incomes: str) -> Decimal:
    value = compute(capability(), *net_incomes).value
    assert isinstance(value, Decimal)
    return value


def test_is_registered_as_ca_caregiver_amount() -> None:
    assert CapabilityRegistry.shared().get("ca/caregiver_amount") is CaregiverAmount


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert ca_capabilities.NAMESPACE == "ca"
    assert "caregiver_amount" in ca_capabilities.__all__
    assert ca_capabilities.caregiver_amount.CaregiverAmount is CaregiverAmount


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({INFIRM_DEPENDANTS})
    assert capability().produces == frozenset({CAREGIVER_AMOUNT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(CaregiverAmount)
    assert "produces" not in vars(CaregiverAmount)


def test_declares_its_slots() -> None:
    assert CaregiverAmount.PARAMETERS == {"base": AMOUNT, "maximum": AMOUNT}
    assert CaregiverAmount.CONSUMES == {"dependants": RecordList}
    assert CaregiverAmount.PRODUCES == {"output": Decimal}
    assert not CaregiverAmount.is_list_slot("dependants")


def test_its_slots_are_read_only() -> None:
    for slots in (CaregiverAmount.PARAMETERS, CaregiverAmount.CONSUMES, CaregiverAmount.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(CaregiverAmount.PARAMETERS, Mapping[str, ParameterKind[Amount]])
    assert_type(CaregiverAmount.CONSUMES, Mapping[str, type])
    assert_type(CaregiverAmount.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (CaregiverAmount.PARAMETERS, CaregiverAmount.CONSUMES, CaregiverAmount.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = CaregiverAmount(
        base=amount("ca/caregiver_base_amount", "28798.00"),
        maximum=amount("ca/caregiver_maximum_amount", "8601"),
        dependants=INFIRM_DEPENDANTS,
        output=CAREGIVER_AMOUNT,
    )

    assert compute(wired, "25000") == Artifact(CAREGIVER_AMOUNT, D("3798.00"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        CaregiverAmount(  # type: ignore[call-arg]
            amount("ca/caregiver_base_amount", "28798.00"),
            amount("ca/caregiver_maximum_amount", "8601"),
            INFIRM_DEPENDANTS,
            CAREGIVER_AMOUNT,
            CENT,
        )


def test_rejects_a_money_kind_for_its_dependants() -> None:
    with pytest.raises(InvalidCapabilityError, match="CaregiverAmount.*'dependants'"):
        CaregiverAmount(
            amount("ca/caregiver_base_amount", "28798.00"),
            amount("ca/caregiver_maximum_amount", "8601"),
            CAREGIVER_AMOUNT,  # type: ignore[arg-type]
            CAREGIVER_AMOUNT,
        )


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(CaregiverAmount, "__type_params__", ())
    assert not getattr(CaregiverAmount, "__parameters__", ())


# --- computing: how many dependants -------------------------------------------------------------


def test_no_dependants_give_zero() -> None:
    output = compute(capability())

    assert output == Artifact(CAREGIVER_AMOUNT, D("0"))
    assert type(output.value) is Decimal
    assert not output.value.is_signed()


def test_one_dependant_gives_the_per_item_figure() -> None:
    # Line 3: 28,798.00 - 25,000 = 3,798.00, under the 8,601 maximum.
    assert total("25000") == D("3798.00")


def test_one_dependant_with_a_low_income_gives_the_maximum() -> None:
    # 28,798.00 - 5,000 = 23,798.00, at most 8,601.
    assert total("5000") == D("8601")


def test_two_dependants_give_the_sum_of_their_own_amounts_not_the_pooled_figure() -> None:
    # 8,601 + 3,798.00 = 12,399.00; pooled, 28,798.00 - 30,000 is negative and gives 0.
    assert total("5000", "25000") == D("12399.00")
    assert total("5000", "25000") != total("30000")


def test_three_dependants_are_summed_one_by_one() -> None:
    # 8,601 + 3,798.00 + 8,601 (20,000 leaves 8,798.00, at most 8,601) = 21,000.00.
    assert total("5000", "25000", "20000") == D("21000.00")


def test_a_dependant_with_no_allowable_amount_adds_nothing_to_the_others() -> None:
    assert total("30000", "25000") == D("3798.00")


def test_the_total_does_not_depend_on_the_order() -> None:
    assert total("25000", "5000") == total("5000", "25000")


# --- computing: the floor and the maximum -------------------------------------------------------


def test_a_net_income_of_zero_gives_the_maximum_not_the_base() -> None:
    assert total("0") == D("8601")


def test_the_maximum_is_reached_exactly_at_a_net_income_of_20197() -> None:
    assert total("20197") == D("8601")
    assert total("20198") == D("8600")


def test_a_net_income_at_the_base_gives_plain_zero() -> None:
    output = compute(capability(), "28798")

    assert output.value == D("0")
    assert not output.value.is_signed()


def test_a_net_income_at_the_base_with_cents_gives_plain_zero() -> None:
    output = compute(capability(), "28798.00")

    assert output.value == D("0")
    assert not output.value.is_signed()


@pytest.mark.parametrize("net_income", ["28798.01", "28799", "30000", "100000", "99999999.99"])
def test_a_net_income_above_the_base_gives_plain_zero_never_negative(net_income: str) -> None:
    value = total(net_income)

    assert value == D("0")
    assert not value.is_signed()


def test_every_dependant_above_the_base_gives_plain_zero() -> None:
    value = total("28798", "30000", "50000")

    assert value == D("0")
    assert not value.is_signed()


def test_a_cent_under_the_base_gives_a_cent() -> None:
    assert total("28797.99") == D("0.01")


def test_a_dependant_over_the_base_does_not_reduce_another_dependants_amount() -> None:
    # The floor is per dependant: 0 + 3,798.00, not 3,798.00 - 1,202.00.
    assert total("30000", "25000") == D("3798.00")


# --- computing: the datasets --------------------------------------------------------------------


def test_the_base_dataset_supplies_the_base() -> None:
    wired = capability(base=amount("ca/caregiver_base_amount", "100"), maximum=amount("ca/m", "30"))

    assert compute(wired, "90").value == D("10")
    assert compute(wired, "100").value == D("0")


def test_the_maximum_dataset_supplies_the_maximum() -> None:
    wired = capability(base=amount("ca/caregiver_base_amount", "100"), maximum=amount("ca/m", "30"))

    assert compute(wired, "10").value == D("30")
    assert compute(wired, "70").value == D("30")
    assert compute(wired, "71").value == D("29")


def test_a_different_year_figure_changes_the_result() -> None:
    wired = capability(
        base=amount("ca/caregiver_base_amount", "29000.00"),
        maximum=amount("ca/caregiver_maximum_amount", "9000"),
    )

    assert compute(wired, "25000", "5000").value == D("13000.00")


# --- computing: rounding ------------------------------------------------------------------------


def test_each_allowable_amount_is_rounded_half_up_to_the_cent() -> None:
    # 28,798.00 - 25,000.005 = 3,797.995, rounded half-up to the cent: 3,798.00.
    assert total("25000.005") == D("3798.00")
    # 28,798.00 - 25,000.004 = 3,797.996 -> 3,798.00; 28,798.00 - 25,000.006 = 3,797.994 ->
    # 3,797.99.
    assert total("25000.004") == D("3798.00")
    assert total("25000.006") == D("3797.99")


def test_the_rounding_is_done_once_per_dependant_before_they_are_summed() -> None:
    # Per dependant: 3,797.995 -> 3,798.00, twice: 7,596.00. Rounding only the total of the exact
    # amounts, 7,595.99, would be wrong.
    assert total("25000.005", "25000.005") == D("7596.00")


def test_the_rounding_rule_comes_from_the_maximum_dataset() -> None:
    wired = capability(
        base=amount("ca/caregiver_base_amount", "28798.00", NO_ROUNDING),
        maximum=amount("ca/caregiver_maximum_amount", "8601", RoundTo(D("1"), RoundingMode.FLOOR)),
    )

    # 28,798.00 - 25,000.005 = 3,797.995, floored to the dollar: 3,797.
    assert compute(wired, "25000.005").value == D("3797")


def test_the_base_datasets_rounding_rule_is_not_used() -> None:
    wired = capability(
        base=amount("ca/caregiver_base_amount", "28798.00", RoundTo(D("1"), RoundingMode.FLOOR)),
        maximum=amount("ca/caregiver_maximum_amount", "8601", NO_ROUNDING),
    )

    assert compute(wired, "25000.005").value == D("3797.995")


def test_a_rounded_allowable_amount_carries_the_increments_scale() -> None:
    assert str(compute(capability(), "5000").value) == "8601.00"
    assert str(compute(capability(), "5000", "25000").value) == "12399.00"


def test_the_maximum_is_rounded_with_the_rule_too() -> None:
    wired = capability(maximum=amount("ca/caregiver_maximum_amount", "8601.005"))

    assert compute(wired, "0").value == D("8601.01")


# --- computing: inputs --------------------------------------------------------------------------


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(DEPENDANT_NET_INCOME, D("9"))

    result = capability().compute((other, dependants("25000")))

    assert result.outputs == (Artifact(CAREGIVER_AMOUNT, D("3798.00")),)


def test_missing_dependants_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="infirm_dependants"):
        capability().compute(())


def test_has_one_output() -> None:
    assert len(capability().compute((dependants("1", "2"),)).outputs) == 1


# --- trace --------------------------------------------------------------------------------------


def claim(position: int, net_income: str, result: str, rounding: RoundingRule = CENT) -> Any:
    return CaregiverClaimLine(
        output=CAREGIVER_AMOUNT,
        position=position,
        base=Amount(D("28798.00")),
        net_income=D(net_income),
        maximum=Amount(D("8601")),
        rounding=rounding,
        result=D(result),
    )


def test_traces_one_claim_line_per_dependant_then_the_total() -> None:
    trace = capability().compute((dependants("5000", "25000"),)).trace

    assert trace == (
        claim(1, "5000", "8601.00"),
        claim(2, "25000", "3798.00"),
        ItemsTotalLine(CAREGIVER_AMOUNT, ((1, D("8601.00")), (2, D("3798.00"))), D("12399.00")),
    )


def test_traces_the_callers_order_with_positions_from_one() -> None:
    trace = capability().compute((dependants("25000", "5000", "30000"),)).trace

    assert trace == (
        claim(1, "25000", "3798.00"),
        claim(2, "5000", "8601.00"),
        claim(3, "30000", "0.00"),
        ItemsTotalLine(
            CAREGIVER_AMOUNT,
            ((1, D("3798.00")), (2, D("8601.00")), (3, D("0.00"))),
            D("12399.00"),
        ),
    )


def test_traces_one_dependant_as_a_claim_and_a_total() -> None:
    trace = capability().compute((dependants("25000"),)).trace

    assert trace == (
        claim(1, "25000", "3798.00"),
        ItemsTotalLine(CAREGIVER_AMOUNT, ((1, D("3798.00")),), D("3798.00")),
    )


def test_traces_a_dependant_over_the_base_as_a_plain_zero_claim() -> None:
    claim_line, total_line = capability().compute((dependants("30000"),)).trace

    assert isinstance(claim_line, CaregiverClaimLine)
    assert claim_line.net_income == D("30000")
    assert claim_line.result == D("0")
    assert not claim_line.result.is_signed()
    assert isinstance(total_line, ItemsTotalLine)
    assert total_line.total == D("0")
    assert not total_line.total.is_signed()


def test_traces_no_dependants_as_only_an_empty_total() -> None:
    trace = capability().compute((dependants(),)).trace

    assert trace == (ItemsTotalLine(CAREGIVER_AMOUNT, (), D("0")),)


def test_traces_the_datasets_rounding_rule_and_the_rounded_amounts() -> None:
    claim_line, total_line = capability().compute((dependants("25000.005"),)).trace

    assert claim_line == claim(1, "25000.005", "3798.00")
    assert isinstance(claim_line, CaregiverClaimLine)
    assert claim_line.rounding == CENT
    assert total_line == ItemsTotalLine(CAREGIVER_AMOUNT, ((1, D("3798.00")),), D("3798.00"))


def test_traces_the_maximum_datasets_rounding_rule() -> None:
    wired = capability(
        base=amount("ca/caregiver_base_amount", "28798.00", NO_ROUNDING),
        maximum=amount("ca/caregiver_maximum_amount", "8601", RoundTo(D("1"), RoundingMode.FLOOR)),
    )

    (claim_line, _) = wired.compute((dependants("25000.005"),)).trace

    assert isinstance(claim_line, CaregiverClaimLine)
    assert claim_line.rounding == RoundTo(D("1"), RoundingMode.FLOOR)
    assert claim_line.result == D("3797")


def test_the_last_trace_line_amount_is_the_output() -> None:
    result = capability().compute((dependants("5000", "25000"),))

    (output,) = result.outputs
    assert result.trace[-1].amount == output.value
    assert [line.amount for line in result.trace[:-1]] == [D("8601.00"), D("3798.00")]


def test_the_total_is_the_sum_of_its_items() -> None:
    *_, total_line = capability().compute((dependants("5000", "25000", "1"),)).trace

    assert isinstance(total_line, ItemsTotalLine)
    assert total_line.total == sum((amount for _, amount in total_line.items), D("0"))


def test_compute_is_repeatable() -> None:
    wired = capability()
    given = (dependants("5000", "25000"),)

    assert wired.compute(given) == wired.compute(given)
