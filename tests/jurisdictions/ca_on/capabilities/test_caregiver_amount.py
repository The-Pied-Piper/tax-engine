"""Unit tests for the OntarioCaregiverAmount capability (`ca-on/caregiver_amount`), line 58185.

Worksheet ON428 (form 5006-D), "Line 58185 - Ontario caregiver amount": "Complete one column for
each dependant." Per dependant, line 1 "Base amount" 26,562.00 less line 2 "Dependant's net
income from line 23600 of their return" is line 3 ("if negative, enter "0") (maximum $6,008 per
dependant)"; line 4 is the "Amount claimed for this dependant on line 58160 of your Form ON428, if
any"; line 5 "Allowable amount for this dependant: line 3 minus line 4 (if negative, enter "0")";
line 6 "Add the amounts from line 5 of columns 1, 2, and 3 (and others, if any). Enter this amount
on line 58185 of your Form ON428."

Its slots: two parameter slots `base` and `maximum` (`amount` datasets), three consumed slots
`dependants` (a record list whose records hold each dependant's net income and whether it is the
dependant claimed on line 58160), `eligible_dependant_amount` (the line 58160 amount) and
`eligible_dependants` (the count of eligible dependants, `ca/eligible_dependants_checked`), and one
produced slot `output`. Each dependant is worked on its own, never pooled: line 3 is the base less
that dependant's net income, at least 0 and at most the maximum, rounded once with the `maximum`
dataset's rule; line 4 is the `eligible_dependant_amount` artifact for a flagged dependant and 0
for any other; line 5 is line 3 less line 4, at least 0; and the output is the total of line 5. A
flag is refused when the flagged rows outnumber the eligible dependants. It records one
`CaregiverClaimLessClaimedLine` per dependant, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.jurisdictions.ca_on.capabilities as ca_on_capabilities
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import (
    InvalidCapabilityError,
    MissingArtifactError,
    ValidationError,
)
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
from tax_calculator.jurisdictions.ca.catalog import (
    DEPENDANT_NET_INCOME,
    ELIGIBLE_DEPENDANTS_CHECKED,
)
from tax_calculator.jurisdictions.ca_on.capabilities.caregiver_amount import OntarioCaregiverAmount
from tax_calculator.jurisdictions.ca_on.catalog import (
    CAREGIVER_AMOUNT,
    CAREGIVER_DEPENDANTS,
    CLAIMED_AS_ELIGIBLE_DEPENDANT,
    ELIGIBLE_DEPENDANT_AMOUNT,
)
from tax_calculator.jurisdictions.ca_on.trace import CaregiverClaimLessClaimedLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
Dependant = tuple[str, int]


def amount(family: str, value: str, rounding: RoundingRule = CENT) -> ParameterDataset[Amount]:
    return ParameterDataset(
        family, 2025, AMOUNT, Amount(D(value)), rounding, ("https://example.org/on428-worksheet",)
    )


def capability(
    base: ParameterDataset[Amount] | None = None,
    maximum: ParameterDataset[Amount] | None = None,
) -> OntarioCaregiverAmount:
    """By default the 2025 figures: the base 26,562.00 and the maximum 6,008, to the cent."""
    return OntarioCaregiverAmount(
        base or amount("ca-on/caregiver_base_amount", "26562.00"),
        maximum or amount("ca-on/caregiver_maximum_amount", "6008"),
        CAREGIVER_DEPENDANTS,
        ELIGIBLE_DEPENDANT_AMOUNT,
        ELIGIBLE_DEPENDANTS_CHECKED,
        CAREGIVER_AMOUNT,
    )


def dependants(*given: Dependant) -> Artifact[Any]:
    """A `ca-on/caregiver_dependants` artifact of one record per (net income, flag), in order."""
    records: list[dict[ArtifactKind[Any], object]] = [
        {DEPENDANT_NET_INCOME: D(net_income), CLAIMED_AS_ELIGIBLE_DEPENDANT: flag}
        for net_income, flag in given
    ]
    return Artifact(CAREGIVER_DEPENDANTS, RecordList(CAREGIVER_DEPENDANTS.fields, records))


def claimed_on_58160(value: str = "0") -> Artifact[Any]:
    """An `ca-on/eligible_dependant_amount` artifact: the amount claimed on line 58160."""
    return Artifact(ELIGIBLE_DEPENDANT_AMOUNT, D(value))


def eligible_dependants_checked(count: int = 1) -> Artifact[Any]:
    """A `ca/eligible_dependants_checked` artifact: how many eligible dependants are claimed."""
    return Artifact(ELIGIBLE_DEPENDANTS_CHECKED, count)


def compute(
    wired: OntarioCaregiverAmount, *given: Dependant, line_58160: str = "0", eligible: int = 1
) -> Artifact[Any]:
    (output,) = wired.compute(
        (dependants(*given), claimed_on_58160(line_58160), eligible_dependants_checked(eligible))
    ).outputs
    return output


def total(*given: Dependant, line_58160: str = "0", eligible: int = 1) -> Decimal:
    value = compute(capability(), *given, line_58160=line_58160, eligible=eligible).value
    assert isinstance(value, Decimal)
    return value


def test_is_registered_as_ca_on_caregiver_amount() -> None:
    assert CapabilityRegistry.shared().get("ca-on/caregiver_amount") is OntarioCaregiverAmount


def test_is_exported_from_the_ca_on_capabilities_package() -> None:
    assert ca_on_capabilities.NAMESPACE == "ca-on"
    assert "caregiver_amount" in ca_on_capabilities.__all__
    assert ca_on_capabilities.caregiver_amount.OntarioCaregiverAmount is OntarioCaregiverAmount


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset(
        {CAREGIVER_DEPENDANTS, ELIGIBLE_DEPENDANT_AMOUNT, ELIGIBLE_DEPENDANTS_CHECKED}
    )
    assert capability().produces == frozenset({CAREGIVER_AMOUNT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(OntarioCaregiverAmount)
    assert "produces" not in vars(OntarioCaregiverAmount)


def test_declares_its_slots() -> None:
    assert OntarioCaregiverAmount.PARAMETERS == {"base": AMOUNT, "maximum": AMOUNT}
    assert OntarioCaregiverAmount.CONSUMES == {
        "dependants": RecordList,
        "eligible_dependant_amount": Decimal,
        "eligible_dependants": int,
    }
    assert OntarioCaregiverAmount.PRODUCES == {"output": Decimal}
    assert not OntarioCaregiverAmount.is_list_slot("dependants")
    assert not OntarioCaregiverAmount.is_list_slot("eligible_dependant_amount")
    assert not OntarioCaregiverAmount.is_list_slot("eligible_dependants")


def test_its_slots_are_read_only() -> None:
    for slots in (
        OntarioCaregiverAmount.PARAMETERS,
        OntarioCaregiverAmount.CONSUMES,
        OntarioCaregiverAmount.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(OntarioCaregiverAmount.PARAMETERS, Mapping[str, ParameterKind[Amount]])
    assert_type(OntarioCaregiverAmount.CONSUMES, Mapping[str, type])
    assert_type(OntarioCaregiverAmount.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (
        OntarioCaregiverAmount.PARAMETERS,
        OntarioCaregiverAmount.CONSUMES,
        OntarioCaregiverAmount.PRODUCES,
    ):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = OntarioCaregiverAmount(
        base=amount("ca-on/caregiver_base_amount", "26562.00"),
        maximum=amount("ca-on/caregiver_maximum_amount", "6008"),
        dependants=CAREGIVER_DEPENDANTS,
        eligible_dependant_amount=ELIGIBLE_DEPENDANT_AMOUNT,
        eligible_dependants=ELIGIBLE_DEPENDANTS_CHECKED,
        output=CAREGIVER_AMOUNT,
    )

    assert compute(wired, ("25000", 0)) == Artifact(CAREGIVER_AMOUNT, D("1562.00"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        OntarioCaregiverAmount(  # type: ignore[call-arg]
            amount("ca-on/caregiver_base_amount", "26562.00"),
            amount("ca-on/caregiver_maximum_amount", "6008"),
            CAREGIVER_DEPENDANTS,
            ELIGIBLE_DEPENDANT_AMOUNT,
            ELIGIBLE_DEPENDANTS_CHECKED,
            CAREGIVER_AMOUNT,
            CENT,
        )


def test_rejects_a_money_kind_for_its_dependants() -> None:
    with pytest.raises(InvalidCapabilityError, match="OntarioCaregiverAmount.*'dependants'"):
        OntarioCaregiverAmount(
            amount("ca-on/caregiver_base_amount", "26562.00"),
            amount("ca-on/caregiver_maximum_amount", "6008"),
            CAREGIVER_AMOUNT,  # type: ignore[arg-type]
            ELIGIBLE_DEPENDANT_AMOUNT,
            ELIGIBLE_DEPENDANTS_CHECKED,
            CAREGIVER_AMOUNT,
        )


def test_rejects_a_record_list_kind_for_its_eligible_dependant_amount() -> None:
    with pytest.raises(
        InvalidCapabilityError, match="OntarioCaregiverAmount.*'eligible_dependant_amount'"
    ):
        OntarioCaregiverAmount(
            amount("ca-on/caregiver_base_amount", "26562.00"),
            amount("ca-on/caregiver_maximum_amount", "6008"),
            CAREGIVER_DEPENDANTS,
            CAREGIVER_DEPENDANTS,  # type: ignore[arg-type]
            ELIGIBLE_DEPENDANTS_CHECKED,
            CAREGIVER_AMOUNT,
        )


def test_rejects_a_money_kind_for_its_eligible_dependants() -> None:
    with pytest.raises(
        InvalidCapabilityError, match="OntarioCaregiverAmount.*'eligible_dependants'"
    ):
        OntarioCaregiverAmount(
            amount("ca-on/caregiver_base_amount", "26562.00"),
            amount("ca-on/caregiver_maximum_amount", "6008"),
            CAREGIVER_DEPENDANTS,
            ELIGIBLE_DEPENDANT_AMOUNT,
            CAREGIVER_AMOUNT,  # type: ignore[arg-type]
            CAREGIVER_AMOUNT,
        )


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(OntarioCaregiverAmount, "__type_params__", ())
    assert not getattr(OntarioCaregiverAmount, "__parameters__", ())


# --- computing: how many dependants -------------------------------------------------------------


def test_no_dependants_give_zero() -> None:
    output = compute(capability())

    assert output == Artifact(CAREGIVER_AMOUNT, D("0"))
    assert type(output.value) is Decimal
    assert not output.value.is_signed()


def test_no_dependants_give_zero_whatever_line_58160_is() -> None:
    assert compute(capability(), line_58160="10823").value == D("0")


def test_one_dependant_gives_the_per_item_figure() -> None:
    # Line 3: 26,562.00 - 25,000 = 1,562.00, under the 6,008 maximum.
    assert total(("25000", 0)) == D("1562.00")


def test_one_dependant_with_a_low_income_gives_the_maximum() -> None:
    # 26,562.00 - 5,000 = 21,562.00, at most 6,008.
    assert total(("5000", 0)) == D("6008")


def test_two_dependants_give_the_sum_of_their_own_amounts_not_the_pooled_figure() -> None:
    # 6,008 + 1,562.00 = 7,570.00; pooled, 26,562.00 - 30,000 is negative and gives 0.
    assert total(("5000", 0), ("25000", 0)) == D("7570.00")
    assert total(("5000", 0), ("25000", 0)) != total(("30000", 0))


def test_three_dependants_are_summed_one_by_one() -> None:
    # 6,008 + 1,562.00 + 6,008 (20,000 leaves 6,562.00, at most 6,008) = 13,578.00.
    assert total(("5000", 0), ("25000", 0), ("20000", 0)) == D("13578.00")


def test_a_dependant_with_no_allowable_amount_adds_nothing_to_the_others() -> None:
    assert total(("30000", 0), ("25000", 0)) == D("1562.00")


def test_the_total_does_not_depend_on_the_order() -> None:
    assert total(("25000", 0), ("5000", 0)) == total(("5000", 0), ("25000", 0))


# --- computing: the floor and the maximum -------------------------------------------------------


def test_a_net_income_of_zero_gives_the_maximum_not_the_base() -> None:
    assert total(("0", 0)) == D("6008")


def test_the_maximum_is_reached_exactly_at_a_net_income_of_20554() -> None:
    assert total(("20554", 0)) == D("6008")
    assert total(("20555", 0)) == D("6007")


def test_the_allowable_amount_is_capped_at_6008_whatever_the_base_less_the_net_income() -> None:
    assert total(("0", 0)) == D("6008")
    assert total(("1", 0)) == D("6008")
    assert total(("20553.99", 0)) == D("6008")


def test_a_net_income_at_the_base_gives_plain_zero() -> None:
    output = compute(capability(), ("26562", 0))

    assert output.value == D("0")
    assert not output.value.is_signed()


def test_a_net_income_at_the_base_with_cents_gives_plain_zero() -> None:
    output = compute(capability(), ("26562.00", 0))

    assert output.value == D("0")
    assert not output.value.is_signed()


@pytest.mark.parametrize("net_income", ["26562.01", "26563", "30000", "100000", "99999999.99"])
def test_a_net_income_above_the_base_gives_plain_zero_never_negative(net_income: str) -> None:
    value = total((net_income, 0))

    assert value == D("0")
    assert not value.is_signed()


def test_every_dependant_above_the_base_gives_plain_zero() -> None:
    value = total(("26562", 0), ("30000", 0), ("50000", 0))

    assert value == D("0")
    assert not value.is_signed()


def test_a_cent_under_the_base_gives_a_cent() -> None:
    assert total(("26561.99", 0)) == D("0.01")


def test_a_dependant_over_the_base_does_not_reduce_another_dependants_amount() -> None:
    # The floor is per dependant: 0 + 1,562.00, not 1,562.00 - 3,438.00.
    assert total(("30000", 0), ("25000", 0)) == D("1562.00")


# --- computing: the amount claimed on line 58160 (line 4) ---------------------------------------


def test_a_flagged_dependant_takes_line_58160_off_its_line_3() -> None:
    # Line 3 is 6,008; line 4 is 2,500.00; line 5 is 6,008 - 2,500.00 = 3,508.00.
    assert total(("5000", 1), line_58160="2500.00") == D("3508.00")


def test_a_flagged_dependant_whose_line_58160_amount_is_the_same_as_line_3_gives_zero() -> None:
    value = total(("25000", 1), line_58160="1562.00")

    assert value == D("0")
    assert not value.is_signed()


def test_a_flagged_dependant_whose_line_58160_amount_exceeds_line_3_gives_zero_not_negative() -> (
    None
):
    # Line 3 is 1,562.00; line 4 is 10,823; line 3 minus line 4 is negative, so line 5 is "0".
    value = total(("25000", 1), line_58160="10823")

    assert value == D("0")
    assert not value.is_signed()


def test_a_flagged_dependant_with_a_line_58160_amount_of_zero_keeps_line_3() -> None:
    assert total(("5000", 1), line_58160="0") == D("6008")


def test_an_unflagged_dependant_takes_zero_whatever_line_58160_is() -> None:
    assert total(("5000", 0), line_58160="2500.00") == D("6008")
    assert total(("25000", 0), line_58160="10823") == D("1562.00")


def test_only_the_flagged_dependant_is_reduced() -> None:
    # 6,008 - 2,500.00 for the flagged one, plus 1,562.00 for the other.
    assert total(("5000", 1), ("25000", 0), line_58160="2500.00") == D("5070.00")
    # The other way round: 6,008 for the unflagged one, plus 1,562.00 less 2,500.00 (not below 0).
    assert total(("5000", 0), ("25000", 1), line_58160="2500.00") == D("6008")


def test_a_flagged_dependants_shortfall_does_not_reduce_another_dependants_amount() -> None:
    # The floor of line 5 is per dependant: 0 + 6,008, not 6,008 + 1,562.00 - 10,823.
    assert total(("25000", 1), ("5000", 0), line_58160="10823") == D("6008")


def test_every_flagged_dependant_takes_line_58160_as_its_own_line_4() -> None:
    # With two eligible dependants the caller may flag two; each takes the amount as its line 4.
    assert total(("5000", 1), ("5000", 1), line_58160="2500.00", eligible=2) == D("7016.00")


def test_the_flag_is_read_from_each_record_not_from_the_position() -> None:
    assert total(("5000", 0), ("5000", 1), line_58160="2500.00") == D("9516.00")
    assert total(("5000", 1), ("5000", 0), line_58160="2500.00") == D("9516.00")


def test_a_flag_above_1_is_refused_naming_the_dependant_by_position() -> None:
    # A flag is 0 or 1; 2 used to be read as claimed.
    with pytest.raises(ValidationError, match=r"dependant 2.*flag is 2.*0 or 1"):
        total(("5000", 1), ("5000", 2), line_58160="2500.00")


def test_a_flag_of_7_is_refused() -> None:
    with pytest.raises(ValidationError, match=r"dependant 1.*flag is 7"):
        total(("5000", 7))


def test_flags_of_0_and_1_are_not_refused() -> None:
    assert total(("5000", 0), ("5000", 1), line_58160="2500.00") == D("9516.00")


# --- computing: flagged dependants against the eligible dependants ------------------------------


def test_one_flagged_dependant_is_not_refused_with_one_eligible_dependant() -> None:
    assert total(("5000", 1), line_58160="2500.00", eligible=1) == D("3508.00")


def test_one_flagged_of_two_dependants_is_not_refused_with_one_eligible_dependant() -> None:
    assert total(("5000", 0), ("25000", 1), line_58160="2500.00", eligible=1) == D("6008")


def test_no_flagged_dependant_is_not_refused_with_no_eligible_dependants() -> None:
    assert total(("5000", 0), ("25000", 0), eligible=0) == D("7570.00")


def test_unflagged_dependants_never_count_against_the_eligible_dependants() -> None:
    assert total(("5000", 0), ("25000", 0), ("30000", 0), eligible=0) == D("7570.00")


def test_two_flagged_dependants_are_refused_with_one_eligible_dependant_naming_dependant_2() -> (
    None
):
    with pytest.raises(ValidationError) as refused:
        total(("5000", 1), ("5000", 1), line_58160="2500.00", eligible=1)

    assert str(refused.value) == (
        "dependant 2: the amount claimed on line 58160 flag is 1 but only 1 eligible dependant(s) "
        "are claimed on line 30400; at most that many dependants may be flagged"
    )


def test_one_flagged_dependant_is_refused_with_no_eligible_dependants_naming_dependant_1() -> None:
    with pytest.raises(ValidationError, match=r"dependant 1: .* flag is 1 but only 0 eligible"):
        total(("5000", 1), eligible=0)


def test_the_running_count_refuses_the_flagged_dependant_that_tips_it_over() -> None:
    # Two may be flagged with a count of 2; the third flagged row is the one refused.
    with pytest.raises(ValidationError, match=r"dependant 3: .* flag is 1 but only 2 eligible"):
        total(("5000", 1), ("5000", 1), ("5000", 1), line_58160="2500.00", eligible=2)


def test_a_flag_above_1_is_refused_before_the_eligible_dependants_are_counted() -> None:
    with pytest.raises(ValidationError, match=r"dependant 1: .*flag is 2; it must be 0 or 1"):
        total(("5000", 2), eligible=0)


# --- computing: the datasets --------------------------------------------------------------------


def test_the_base_dataset_supplies_the_base() -> None:
    wired = capability(
        base=amount("ca-on/caregiver_base_amount", "100"), maximum=amount("ca-on/m", "30")
    )

    assert compute(wired, ("90", 0)).value == D("10")
    assert compute(wired, ("100", 0)).value == D("0")


def test_the_maximum_dataset_supplies_the_maximum() -> None:
    wired = capability(
        base=amount("ca-on/caregiver_base_amount", "100"), maximum=amount("ca-on/m", "30")
    )

    assert compute(wired, ("10", 0)).value == D("30")
    assert compute(wired, ("70", 0)).value == D("30")
    assert compute(wired, ("71", 0)).value == D("29")


def test_the_datasets_supply_the_figures_for_line_4_too() -> None:
    wired = capability(
        base=amount("ca-on/caregiver_base_amount", "100"), maximum=amount("ca-on/m", "30")
    )

    assert compute(wired, ("10", 1), line_58160="12").value == D("18")


def test_a_different_year_figure_changes_the_result() -> None:
    wired = capability(
        base=amount("ca-on/caregiver_base_amount", "27000.00"),
        maximum=amount("ca-on/caregiver_maximum_amount", "7000"),
    )

    assert compute(wired, ("25000", 0), ("5000", 0)).value == D("9000.00")


# --- computing: rounding ------------------------------------------------------------------------


def test_line_3_is_rounded_half_up_to_the_cent() -> None:
    # 26,562.00 - 26,561.995 = 0.005, rounded half-up to the cent: 0.01.
    assert total(("26561.995", 0)) == D("0.01")
    # 26,562.00 - 26,561.996 = 0.004 -> 0.00.
    assert total(("26561.996", 0)) == D("0.00")
    # 26,562.00 - 26,561.994 = 0.006 -> 0.01.
    assert total(("26561.994", 0)) == D("0.01")


def test_a_line_3_that_rounds_to_zero_is_plain_zero() -> None:
    value = total(("26561.996", 0))

    assert value == D("0")
    assert not value.is_signed()


def test_the_rounding_is_done_once_per_dependant_before_they_are_summed() -> None:
    # Per dependant: 0.005 -> 0.01, twice: 0.02. Rounding only the total of the exact amounts,
    # 0.010 -> 0.01, would be wrong.
    assert total(("26561.995", 0), ("26561.995", 0)) == D("0.02")


def test_line_5_is_taken_from_the_rounded_line_3() -> None:
    # Line 3: 0.005 -> 0.01; line 4: 0.01; line 5: 0.00. From the exact 0.005, line 5 would be
    # negative.
    assert total(("26561.995", 1), line_58160="0.01") == D("0")


def test_the_rounding_rule_comes_from_the_maximum_dataset() -> None:
    wired = capability(
        base=amount("ca-on/caregiver_base_amount", "26562.00", NO_ROUNDING),
        maximum=amount(
            "ca-on/caregiver_maximum_amount", "6008", RoundTo(D("1"), RoundingMode.FLOOR)
        ),
    )

    # 26,562.00 - 25,000.005 = 1,561.995, floored to the dollar: 1,561.
    assert compute(wired, ("25000.005", 0)).value == D("1561")


def test_the_base_datasets_rounding_rule_is_not_used() -> None:
    wired = capability(
        base=amount("ca-on/caregiver_base_amount", "26562.00", RoundTo(D("1"), RoundingMode.FLOOR)),
        maximum=amount("ca-on/caregiver_maximum_amount", "6008", NO_ROUNDING),
    )

    assert compute(wired, ("25000.005", 0)).value == D("1561.995")


def test_a_rounded_allowable_amount_carries_the_increments_scale() -> None:
    assert str(compute(capability(), ("5000", 0)).value) == "6008.00"
    assert str(compute(capability(), ("5000", 0), ("25000", 0)).value) == "7570.00"


def test_the_maximum_is_rounded_with_the_rule_too() -> None:
    wired = capability(maximum=amount("ca-on/caregiver_maximum_amount", "6008.005"))

    assert compute(wired, ("0", 0)).value == D("6008.01")


# --- computing: inputs --------------------------------------------------------------------------


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(DEPENDANT_NET_INCOME, D("9"))

    result = capability().compute(
        (other, dependants(("25000", 0)), claimed_on_58160(), eligible_dependants_checked())
    )

    assert result.outputs == (Artifact(CAREGIVER_AMOUNT, D("1562.00")),)


def test_takes_its_inputs_in_any_order() -> None:
    result = capability().compute(
        (claimed_on_58160("2500.00"), eligible_dependants_checked(), dependants(("5000", 1)))
    )

    assert result.outputs == (Artifact(CAREGIVER_AMOUNT, D("3508.00")),)


def test_missing_dependants_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="caregiver_dependants"):
        capability().compute(
            (
                claimed_on_58160(),
                eligible_dependants_checked(),
            )
        )


def test_missing_line_58160_amount_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="eligible_dependant_amount"):
        capability().compute((dependants(("25000", 0)), eligible_dependants_checked()))


def test_missing_eligible_dependants_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="eligible_dependants_checked"):
        capability().compute((dependants(("25000", 0)), claimed_on_58160()))


def test_missing_both_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError):
        capability().compute(())


def test_has_one_output() -> None:
    assert (
        len(
            capability()
            .compute(
                (dependants(("1", 0), ("2", 0)), claimed_on_58160(), eligible_dependants_checked())
            )
            .outputs
        )
        == 1
    )


# --- trace --------------------------------------------------------------------------------------


def claim(
    position: int,
    net_income: str,
    allowable: str,
    claimed: str,
    result: str,
    rounding: RoundingRule = CENT,
) -> Any:
    return CaregiverClaimLessClaimedLine(
        output=CAREGIVER_AMOUNT,
        position=position,
        base=Amount(D("26562.00")),
        net_income=D(net_income),
        maximum=Amount(D("6008")),
        allowable_before_claimed=D(allowable),
        claimed=D(claimed),
        rounding=rounding,
        result=D(result),
    )


def test_traces_one_claim_line_per_dependant_then_the_total() -> None:
    trace = (
        capability()
        .compute(
            (
                dependants(("5000", 0), ("25000", 0)),
                claimed_on_58160(),
                eligible_dependants_checked(),
            )
        )
        .trace
    )

    assert trace == (
        claim(1, "5000", "6008.00", "0", "6008.00"),
        claim(2, "25000", "1562.00", "0", "1562.00"),
        ItemsTotalLine(CAREGIVER_AMOUNT, ((1, D("6008.00")), (2, D("1562.00"))), D("7570.00")),
    )


def test_traces_the_callers_order_with_positions_from_one() -> None:
    trace = (
        capability()
        .compute(
            (
                dependants(("25000", 0), ("5000", 0), ("30000", 0)),
                claimed_on_58160(),
                eligible_dependants_checked(),
            )
        )
        .trace
    )

    assert trace == (
        claim(1, "25000", "1562.00", "0", "1562.00"),
        claim(2, "5000", "6008.00", "0", "6008.00"),
        claim(3, "30000", "0.00", "0", "0.00"),
        ItemsTotalLine(
            CAREGIVER_AMOUNT,
            ((1, D("1562.00")), (2, D("6008.00")), (3, D("0.00"))),
            D("7570.00"),
        ),
    )


def test_traces_one_dependant_as_a_claim_and_a_total() -> None:
    trace = (
        capability()
        .compute((dependants(("25000", 0)), claimed_on_58160(), eligible_dependants_checked()))
        .trace
    )

    assert trace == (
        claim(1, "25000", "1562.00", "0", "1562.00"),
        ItemsTotalLine(CAREGIVER_AMOUNT, ((1, D("1562.00")),), D("1562.00")),
    )


def test_traces_a_flagged_dependants_line_3_line_4_and_line_5() -> None:
    trace = (
        capability()
        .compute(
            (
                dependants(("5000", 1), ("25000", 0)),
                claimed_on_58160("2500.00"),
                eligible_dependants_checked(),
            )
        )
        .trace
    )

    assert trace == (
        claim(1, "5000", "6008.00", "2500.00", "3508.00"),
        claim(2, "25000", "1562.00", "0", "1562.00"),
        ItemsTotalLine(CAREGIVER_AMOUNT, ((1, D("3508.00")), (2, D("1562.00"))), D("5070.00")),
    )


def test_traces_the_unflagged_dependants_line_4_as_a_plain_zero() -> None:
    claim_line, _ = (
        capability()
        .compute(
            (dependants(("5000", 0)), claimed_on_58160("2500.00"), eligible_dependants_checked())
        )
        .trace
    )

    assert isinstance(claim_line, CaregiverClaimLessClaimedLine)
    assert claim_line.claimed == D("0")
    assert not claim_line.claimed.is_signed()
    assert claim_line.allowable_before_claimed == D("6008.00")


def test_traces_a_claimed_amount_over_line_3_as_a_plain_zero_result() -> None:
    claim_line, total_line = (
        capability()
        .compute(
            (dependants(("25000", 1)), claimed_on_58160("10823"), eligible_dependants_checked())
        )
        .trace
    )

    assert isinstance(claim_line, CaregiverClaimLessClaimedLine)
    assert claim_line.allowable_before_claimed == D("1562.00")
    assert claim_line.claimed == D("10823")
    assert claim_line.result == D("0")
    assert not claim_line.result.is_signed()
    assert isinstance(total_line, ItemsTotalLine)
    assert total_line.total == D("0")
    assert not total_line.total.is_signed()


def test_traces_a_dependant_over_the_base_as_a_plain_zero_claim() -> None:
    claim_line, total_line = (
        capability()
        .compute((dependants(("30000", 0)), claimed_on_58160(), eligible_dependants_checked()))
        .trace
    )

    assert isinstance(claim_line, CaregiverClaimLessClaimedLine)
    assert claim_line.net_income == D("30000")
    assert claim_line.allowable_before_claimed == D("0")
    assert not claim_line.allowable_before_claimed.is_signed()
    assert claim_line.result == D("0")
    assert not claim_line.result.is_signed()
    assert isinstance(total_line, ItemsTotalLine)
    assert total_line.total == D("0")
    assert not total_line.total.is_signed()


def test_traces_no_dependants_as_only_an_empty_total() -> None:
    trace = (
        capability()
        .compute((dependants(), claimed_on_58160(), eligible_dependants_checked()))
        .trace
    )

    assert trace == (ItemsTotalLine(CAREGIVER_AMOUNT, (), D("0")),)


def test_traces_the_datasets_rounding_rule_and_the_rounded_amounts() -> None:
    claim_line, total_line = (
        capability()
        .compute((dependants(("26561.995", 0)), claimed_on_58160(), eligible_dependants_checked()))
        .trace
    )

    assert claim_line == claim(1, "26561.995", "0.01", "0", "0.01")
    assert isinstance(claim_line, CaregiverClaimLessClaimedLine)
    assert claim_line.rounding == CENT
    assert total_line == ItemsTotalLine(CAREGIVER_AMOUNT, ((1, D("0.01")),), D("0.01"))


def test_traces_the_maximum_datasets_rounding_rule() -> None:
    wired = capability(
        base=amount("ca-on/caregiver_base_amount", "26562.00", NO_ROUNDING),
        maximum=amount(
            "ca-on/caregiver_maximum_amount", "6008", RoundTo(D("1"), RoundingMode.FLOOR)
        ),
    )

    (claim_line, _) = wired.compute(
        (dependants(("25000.005", 0)), claimed_on_58160(), eligible_dependants_checked())
    ).trace

    assert isinstance(claim_line, CaregiverClaimLessClaimedLine)
    assert claim_line.rounding == RoundTo(D("1"), RoundingMode.FLOOR)
    assert claim_line.allowable_before_claimed == D("1561")
    assert claim_line.result == D("1561")


def test_the_last_trace_line_amount_is_the_output() -> None:
    result = capability().compute(
        (dependants(("5000", 0), ("25000", 0)), claimed_on_58160(), eligible_dependants_checked())
    )

    (output,) = result.outputs
    assert result.trace[-1].amount == output.value
    assert [line.amount for line in result.trace[:-1]] == [D("6008.00"), D("1562.00")]


def test_the_total_is_the_sum_of_its_items() -> None:
    *_, total_line = (
        capability()
        .compute(
            (
                dependants(("5000", 1), ("25000", 0), ("1", 0)),
                claimed_on_58160("2500.00"),
                eligible_dependants_checked(),
            )
        )
        .trace
    )

    assert isinstance(total_line, ItemsTotalLine)
    assert total_line.total == sum((amount for _, amount in total_line.items), D("0"))


def test_compute_is_repeatable() -> None:
    wired = capability()
    given = (
        dependants(("5000", 1), ("25000", 0)),
        claimed_on_58160("2500.00"),
        eligible_dependants_checked(),
    )

    assert wired.compute(given) == wired.compute(given)
