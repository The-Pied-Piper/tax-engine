"""Unit tests for the DisabilityTransferAmount capability (`ca/disability_transfer_amount`), T1
line 100 (line 31800).

Federal Worksheet (form 5000-D1), "Line 31800 - Disability amount transferred from a dependant":
"Complete the following calculation fore ach dependant who is eligible for the disability tax
credit in 2025." Line 1 "Base amount 10,138.00"; "If the dependant was under 18 years of age on
December 31, 2025, complete lines 2 to 13. If the dependant was 18 years of age or older, complete
lines 7 to 13."; line 2 "Maximum supplement 5,914.00"; line 3 "Total of child care and attendant
care expenses for your dependant that you or another person claimed"; line 4 "Threshold for child
care and attendant care expenses 3,464.00"; line 5 "Line 3 minus line 4 (if negative, enter "0")";
line 6 "Line 2 minus line 5 (if negative, enter "0")"; line 7 "If the dependant was under 18 years
of age on December 31, 2025, enter the amount from line 6. If the dependant was 18 years of age or
older, enter "0"."; line 8 "Line 1 plus line 7 (maximum $16,052)"; line 9 "amount from line 98 of
your dependant's return"; line 10 "Line 8 plus line 9"; line 11 "Dependant's taxable income from
line 26000 of their return"; line 12 "Line 10 minus line 11 (if negative, enter "0")"; line 13
"Enter whichever is less: amount from line 8 or line 12. Allowable amount for this dependant";
"Enter the total of allowable amounts claimed for all dependants who qualify for the disability tax
credit on line 31800 of your return."

Its slots: four parameter slots `base`, `supplement`, `threshold` and `maximum` (`amount` datasets,
lines 1, 2, 4 and 8), one consumed slot `dependants` (a record list whose records hold each
dependant's figures: under 18, care expenses, the credit amounts of their return and their taxable
income) and one produced slot `output`. Each dependant is worked on its own, never pooled: line
13 is rounded once, with the `maximum` dataset's rule, and the output is their total. It records
one `DisabilityTransferLine` per dependant, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.capabilities.disability_transfer_amount import (
    DisabilityTransferAmount,
)
from tax_engine.jurisdictions.ca.catalog import (
    CAREGIVER_AMOUNT,
    DEPENDANT_CARE_EXPENSES,
    DEPENDANT_CREDIT_AMOUNTS,
    DEPENDANT_NET_INCOME,
    DEPENDANT_TAXABLE_INCOME,
    DEPENDANT_UNDER_18,
    DISABILITY_DEPENDANTS,
    DISABILITY_TRANSFERRED_AMOUNT,
)
from tax_engine.jurisdictions.ca.trace import DisabilityTransferLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
DOLLAR_FLOOR = RoundTo(D("1"), RoundingMode.FLOOR)

# One dependant's figures, as the worksheet asks for them: under 18 on December 31, 2025 (1 or 0),
# line 3 the care expenses, line 9 line 98 of their return and line 11 their taxable income.
Figures = tuple[int, str, str, str]
AGED_20: Figures = (0, "0", "16129", "20000")
AGED_17: Figures = (1, "5000", "0", "0")


def amount(family: str, value: str, rounding: RoundingRule = CENT) -> ParameterDataset[Amount]:
    return ParameterDataset(
        family, 2025, AMOUNT, Amount(D(value)), rounding, ("https://example.org/d1",)
    )


def capability(
    base: ParameterDataset[Amount] | None = None,
    supplement: ParameterDataset[Amount] | None = None,
    threshold: ParameterDataset[Amount] | None = None,
    maximum: ParameterDataset[Amount] | None = None,
) -> DisabilityTransferAmount:
    """By default the 2025 figures: line 1 10,138.00, line 2 5,914.00, line 4 3,464.00 and line 8's
    maximum 16,052, each to the cent."""
    return DisabilityTransferAmount(
        base or amount("ca/disability_transfer_base_amount", "10138.00"),
        supplement or amount("ca/disability_transfer_supplement_maximum", "5914.00"),
        threshold or amount("ca/disability_transfer_care_threshold", "3464.00"),
        maximum or amount("ca/disability_transfer_maximum", "16052"),
        DISABILITY_DEPENDANTS,
        DISABILITY_TRANSFERRED_AMOUNT,
    )


def dependants(*given: Figures) -> Artifact[Any]:
    """A `ca/disability_dependants` artifact of one record per dependant, in the order given."""
    records: list[dict[ArtifactKind[Any], object]] = [
        {
            DEPENDANT_UNDER_18: under_18,
            DEPENDANT_CARE_EXPENSES: D(care),
            DEPENDANT_CREDIT_AMOUNTS: D(credits),
            DEPENDANT_TAXABLE_INCOME: D(taxable),
        }
        for under_18, care, credits, taxable in given
    ]
    return Artifact(DISABILITY_DEPENDANTS, RecordList(DISABILITY_DEPENDANTS.fields, records))


def compute(wired: DisabilityTransferAmount, *given: Figures) -> Artifact[Any]:
    (output,) = wired.compute((dependants(*given),)).outputs
    return output


def total(*given: Figures) -> Decimal:
    value = compute(capability(), *given).value
    assert isinstance(value, Decimal)
    return value


def test_is_registered_as_ca_disability_transfer_amount() -> None:
    assert (
        CapabilityRegistry.shared().get("ca/disability_transfer_amount") is DisabilityTransferAmount
    )


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert ca_capabilities.NAMESPACE == "ca"
    assert "disability_transfer_amount" in ca_capabilities.__all__
    assert (
        ca_capabilities.disability_transfer_amount.DisabilityTransferAmount
        is DisabilityTransferAmount
    )


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({DISABILITY_DEPENDANTS})
    assert capability().produces == frozenset({DISABILITY_TRANSFERRED_AMOUNT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(DisabilityTransferAmount)
    assert "produces" not in vars(DisabilityTransferAmount)


def test_declares_its_slots() -> None:
    assert DisabilityTransferAmount.PARAMETERS == {
        "base": AMOUNT,
        "supplement": AMOUNT,
        "threshold": AMOUNT,
        "maximum": AMOUNT,
    }
    assert list(DisabilityTransferAmount.PARAMETERS) == [
        "base",
        "supplement",
        "threshold",
        "maximum",
    ]
    assert DisabilityTransferAmount.CONSUMES == {"dependants": RecordList}
    assert DisabilityTransferAmount.PRODUCES == {"output": Decimal}
    assert not DisabilityTransferAmount.is_list_slot("dependants")


def test_its_slots_are_read_only() -> None:
    for slots in (
        DisabilityTransferAmount.PARAMETERS,
        DisabilityTransferAmount.CONSUMES,
        DisabilityTransferAmount.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(DisabilityTransferAmount.PARAMETERS, Mapping[str, ParameterKind[Amount]])
    assert_type(DisabilityTransferAmount.CONSUMES, Mapping[str, type])
    assert_type(DisabilityTransferAmount.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (
        DisabilityTransferAmount.PARAMETERS,
        DisabilityTransferAmount.CONSUMES,
        DisabilityTransferAmount.PRODUCES,
    ):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = DisabilityTransferAmount(
        base=amount("ca/disability_transfer_base_amount", "10138.00"),
        supplement=amount("ca/disability_transfer_supplement_maximum", "5914.00"),
        threshold=amount("ca/disability_transfer_care_threshold", "3464.00"),
        maximum=amount("ca/disability_transfer_maximum", "16052"),
        dependants=DISABILITY_DEPENDANTS,
        output=DISABILITY_TRANSFERRED_AMOUNT,
    )

    assert compute(wired, AGED_20) == Artifact(DISABILITY_TRANSFERRED_AMOUNT, D("6267.00"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        DisabilityTransferAmount(  # type: ignore[call-arg]
            amount("ca/disability_transfer_base_amount", "10138.00"),
            amount("ca/disability_transfer_supplement_maximum", "5914.00"),
            amount("ca/disability_transfer_care_threshold", "3464.00"),
            amount("ca/disability_transfer_maximum", "16052"),
            DISABILITY_DEPENDANTS,
            DISABILITY_TRANSFERRED_AMOUNT,
            CENT,
        )


def test_rejects_a_money_kind_for_its_dependants() -> None:
    with pytest.raises(InvalidCapabilityError, match="DisabilityTransferAmount.*'dependants'"):
        DisabilityTransferAmount(
            amount("ca/disability_transfer_base_amount", "10138.00"),
            amount("ca/disability_transfer_supplement_maximum", "5914.00"),
            amount("ca/disability_transfer_care_threshold", "3464.00"),
            amount("ca/disability_transfer_maximum", "16052"),
            CAREGIVER_AMOUNT,  # type: ignore[arg-type]
            DISABILITY_TRANSFERRED_AMOUNT,
        )


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(DisabilityTransferAmount, "__type_params__", ())
    assert not getattr(DisabilityTransferAmount, "__parameters__", ())


# --- computing: how many dependants -------------------------------------------------------------


def test_no_dependants_give_zero() -> None:
    output = compute(capability())

    assert output == Artifact(DISABILITY_TRANSFERRED_AMOUNT, D("0"))
    assert type(output.value) is Decimal
    assert not output.value.is_signed()


def test_one_dependant_gives_the_per_item_figure() -> None:
    # The ticket's worked example: aged 20 (line 7 is "0"), line 8 10,138.00; line 10 = 10,138.00
    # + 16,129 = 26,267.00; line 12 = 26,267.00 - 20,000 = 6,267.00; line 13 = lesser(10,138.00,
    # 6,267.00) = 6,267.00.
    assert total(AGED_20) == D("6267.00")


def test_one_dependant_under_18_gives_the_per_item_figure() -> None:
    # Line 5: 5,000 - 3,464.00 = 1,536.00; line 6: 5,914.00 - 1,536.00 = 4,378.00; line 7 =
    # line 6; line 8: 10,138.00 + 4,378.00 = 14,516.00 (under the 16,052 maximum); line 10 =
    # line 8 + 0; line 12 = line 10 - 0; line 13 = lesser(14,516.00, 14,516.00).
    assert total(AGED_17) == D("14516.00")


def test_two_dependants_give_the_sum_of_their_own_amounts() -> None:
    # 6,267.00 (aged 20) + 14,516.00 (aged 17).
    assert total(AGED_20, AGED_17) == D("20783.00")


def test_three_dependants_are_summed_one_by_one() -> None:
    # 6,267.00 + 14,516.00 + 10,138.00 (aged 30, line 12 = 10,138.00 + 5,000 - 0 over line 8).
    assert total(AGED_20, AGED_17, (0, "0", "5000", "0")) == D("30921.00")


def test_a_dependant_with_nothing_transferable_adds_nothing_to_the_others() -> None:
    assert total((0, "0", "0", "20000"), AGED_20) == D("6267.00")


def test_the_total_does_not_depend_on_the_order() -> None:
    assert total(AGED_17, AGED_20) == total(AGED_20, AGED_17)


# --- computing: under 18 or 18 and older (lines 1 to 8) -----------------------------------------


def test_a_dependant_aged_18_or_older_has_line_7_zero_whatever_the_care_expenses() -> None:
    # "If the dependant was 18 years of age or older, enter "0"." Line 8 is the base alone.
    assert total((0, "0", "0", "0")) == D("10138.00")
    assert total((0, "5000", "0", "0")) == D("10138.00")
    assert total((0, "0.01", "0", "0")) == D("10138.00")


def test_a_dependant_under_18_with_no_care_expenses_takes_the_whole_supplement() -> None:
    # Line 3 is 0: line 5 is -3,464.00, entered as "0"; line 6 is 5,914.00; line 8 is 10,138.00 +
    # 5,914.00 = 16,052.00, the maximum.
    assert total((1, "0", "0", "0")) == D("16052.00")


def test_care_expenses_at_the_threshold_leave_line_5_zero_and_the_whole_supplement() -> None:
    assert total((1, "3464", "0", "0")) == D("16052.00")
    assert total((1, "3464.00", "0", "0")) == D("16052.00")


def test_care_expenses_below_the_threshold_leave_line_5_zero_and_the_whole_supplement() -> None:
    assert total((1, "3000", "0", "0")) == D("16052.00")
    assert total((1, "3463.99", "0", "0")) == D("16052.00")


def test_care_expenses_a_cent_above_the_threshold_take_a_cent_off_the_supplement() -> None:
    # Line 5: 3,464.01 - 3,464.00 = 0.01; line 6: 5,914.00 - 0.01 = 5,913.99; line 8: 16,051.99.
    assert total((1, "3464.01", "0", "0")) == D("16051.99")


def test_care_expenses_above_the_threshold_reduce_the_supplement_dollar_for_dollar() -> None:
    # Line 5: 5,000 - 3,464.00 = 1,536.00; line 6: 4,378.00; line 8: 14,516.00.
    assert total((1, "5000", "0", "0")) == D("14516.00")
    # Line 5: 4,000 - 3,464.00 = 536.00; line 6: 5,378.00; line 8: 15,516.00.
    assert total((1, "4000", "0", "0")) == D("15516.00")


def test_care_expenses_of_the_threshold_plus_the_supplement_leave_line_6_zero() -> None:
    # Line 5: 9,378 - 3,464.00 = 5,914.00; line 6: 5,914.00 - 5,914.00 = 0; line 8: 10,138.00.
    assert total((1, "9378", "0", "0")) == D("10138.00")


def test_care_expenses_above_the_threshold_plus_the_supplement_leave_line_6_zero_not_negative() -> (
    None
):
    # Line 5: 10,000 - 3,464.00 = 6,536.00; line 6: 5,914.00 - 6,536.00 is negative, entered "0".
    assert total((1, "10000", "0", "0")) == D("10138.00")
    assert total((1, "9378.01", "0", "0")) == D("10138.00")
    assert total((1, "999999.99", "0", "0")) == D("10138.00")


def test_a_dependant_under_18_and_one_aged_18_or_older_each_follow_their_own_lines() -> None:
    assert total((1, "5000", "0", "0")) == D("14516.00")
    assert total((0, "5000", "0", "0")) == D("10138.00")
    assert total((1, "5000", "0", "0"), (0, "5000", "0", "0")) == D("24654.00")


# --- computing: line 8's maximum ----------------------------------------------------------------


def test_the_2025_supplement_added_to_the_base_reaches_the_maximum_exactly() -> None:
    # 10,138.00 + 5,914.00 = 16,052.00: "(maximum $16,052)" is never cut by the 2025 figures.
    assert total((1, "0", "0", "0")) == D("16052.00")


def test_line_8_is_at_most_the_maximum_dataset() -> None:
    wired = capability(maximum=amount("ca/disability_transfer_maximum", "15000"))

    # 10,138.00 + 5,914.00 = 16,052.00, cut to 15,000.
    assert compute(wired, (1, "0", "0", "0")).value == D("15000.00")
    # 10,138.00 + 4,378.00 = 14,516.00, under the 15,000 maximum.
    assert compute(wired, (1, "5000", "0", "0")).value == D("14516.00")
    # 10,138.00 + 4,862.00 = 15,000.00: just reaches it.
    assert compute(wired, (1, "4516", "0", "0")).value == D("15000.00")
    # 10,138.00 + 4,861.99 = 14,999.99: a cent under it.
    assert compute(wired, (1, "4516.01", "0", "0")).value == D("14999.99")


def test_line_12_is_taken_from_the_capped_line_8() -> None:
    wired = capability(maximum=amount("ca/disability_transfer_maximum", "15000"))

    # Line 8 is 15,000; line 10 = 15,000 + 100 = 15,100; line 12 = 15,100 - 0; lesser(15,000,
    # 15,100) = 15,000, not the uncapped 16,052.
    assert compute(wired, (1, "0", "100", "0")).value == D("15000.00")


# --- computing: lines 9 to 13 -------------------------------------------------------------------


def test_line_12_is_line_8_plus_the_credit_amounts_less_the_taxable_income() -> None:
    # Line 12 = 10,138.00 + 16,129 - 20,000 = 6,267.00, under line 8.
    assert total((0, "0", "16129", "20000")) == D("6267.00")
    # 10,138.00 + 16,129 - 25,000 = 1,267.00.
    assert total((0, "0", "16129", "25000")) == D("1267.00")
    # 10,138.00 + 1,000 - 5,000 = 6,138.00.
    assert total((0, "0", "1000", "5000")) == D("6138.00")


def test_line_13_is_line_12_when_that_is_less_than_line_8() -> None:
    assert total((0, "0", "16129", "20000")) == D("6267.00")


def test_line_13_is_line_8_when_that_is_less_than_line_12() -> None:
    # Line 12 = 10,138.00 + 16,129 - 0 = 26,267.00, over line 8.
    assert total((0, "0", "16129", "0")) == D("10138.00")


def test_line_13_is_line_8_when_line_8_equals_line_12() -> None:
    # No credit amounts and no taxable income: line 12 = 10,138.00 = line 8.
    assert total((0, "0", "0", "0")) == D("10138.00")
    # Line 10 = line 8 + 5,000; taxable income 5,000.
    assert total((0, "0", "5000", "5000")) == D("10138.00")


def test_line_12_a_cent_under_line_8_is_the_amount() -> None:
    assert total((0, "0", "0", "0.01")) == D("10137.99")


def test_line_12_is_zero_when_the_taxable_income_exceeds_line_10() -> None:
    # Line 10 = 10,138.00 + 0; line 12 = 10,138.00 - 20,000 is negative, entered "0".
    assert total((0, "0", "0", "20000")) == D("0")


def test_a_taxable_income_equal_to_line_10_leaves_plain_zero() -> None:
    output = compute(capability(), (0, "0", "0", "10138"))

    assert output.value == D("0")
    assert not output.value.is_signed()


def test_a_taxable_income_a_cent_over_line_10_leaves_plain_zero_never_negative() -> None:
    value = total((0, "0", "0", "10138.01"))

    assert value == D("0")
    assert not value.is_signed()


@pytest.mark.parametrize("taxable", ["10138.01", "10139", "20000", "100000", "99999999.99"])
def test_a_taxable_income_above_line_10_gives_plain_zero_never_negative(taxable: str) -> None:
    value = total((0, "0", "0", taxable))

    assert value == D("0")
    assert not value.is_signed()


def test_every_dependant_with_nothing_transferable_gives_plain_zero() -> None:
    value = total((0, "0", "0", "20000"), (1, "0", "0", "90000"))

    assert value == D("0")
    assert not value.is_signed()


def test_the_floor_is_per_dependant_so_a_dependant_over_the_limit_does_not_reduce_another() -> None:
    # 0 + 6,267.00, not 6,267.00 - 9,862.00.
    assert total((0, "0", "0", "20000"), AGED_20) == D("6267.00")


def test_the_credit_amounts_of_a_dependant_under_18_add_to_line_8_with_its_supplement() -> None:
    # Line 8 = 14,516.00; line 10 = 14,516.00 + 1,000; line 12 = 15,516.00 - 2,000 = 13,516.00,
    # under line 8.
    assert total((1, "5000", "1000", "2000")) == D("13516.00")


def test_the_taxable_income_does_not_change_line_8() -> None:
    # Line 12 = 14,516.00 + 0 - 1,000 = 13,516.00.
    assert total((1, "5000", "0", "1000")) == D("13516.00")
    assert total((1, "5000", "0", "0")) == D("14516.00")


# --- computing: the datasets --------------------------------------------------------------------


def test_the_base_dataset_supplies_line_1() -> None:
    wired = capability(base=amount("ca/b", "100"), maximum=amount("ca/m", "1000"))

    assert compute(wired, (0, "0", "0", "0")).value == D("100")
    # Line 8 = 100 + 5,914.00 for an under 18; at most 1,000.
    assert compute(wired, (1, "0", "0", "0")).value == D("1000")


def test_the_supplement_dataset_supplies_line_2() -> None:
    wired = capability(supplement=amount("ca/s", "500"), maximum=amount("ca/m", "100000"))

    # Line 5 is 0 (no expenses); line 6 is 500; line 8 = 10,138 + 500.
    assert compute(wired, (1, "0", "0", "0")).value == D("10638")
    # Line 5 = 3,764 - 3,464.00 = 300; line 6 = 200.
    assert compute(wired, (1, "3764", "0", "0")).value == D("10338")


def test_the_threshold_dataset_supplies_line_4() -> None:
    wired = capability(threshold=amount("ca/t", "1000"), maximum=amount("ca/m", "100000"))

    # Line 5 = 2,000 - 1,000 = 1,000; line 6 = 5,914 - 1,000 = 4,914; line 8 = 15,052.
    assert compute(wired, (1, "2000", "0", "0")).value == D("15052")


def test_the_maximum_dataset_supplies_line_8s_maximum() -> None:
    wired = capability(maximum=amount("ca/m", "12000"))

    assert compute(wired, (0, "0", "0", "0")).value == D("10138")
    assert compute(wired, (1, "0", "0", "0")).value == D("12000")


def test_a_different_year_figure_changes_the_result() -> None:
    wired = capability(
        base=amount("ca/disability_transfer_base_amount", "10500.00"),
        supplement=amount("ca/disability_transfer_supplement_maximum", "6000.00"),
        threshold=amount("ca/disability_transfer_care_threshold", "3500.00"),
        maximum=amount("ca/disability_transfer_maximum", "16500"),
    )

    # Aged 20: line 8 = 10,500.00; line 12 = 10,500.00 + 16,129 - 20,000 = 6,629.00.
    assert compute(wired, AGED_20).value == D("6629.00")
    # Under 18: line 5 = 5,000 - 3,500.00 = 1,500.00; line 6 = 4,500.00; line 8 = 15,000.00.
    assert compute(wired, AGED_17).value == D("15000.00")


# --- computing: rounding ------------------------------------------------------------------------


def test_each_allowable_amount_is_rounded_half_up_to_the_cent() -> None:
    # Line 12 = 10,138.00 + 16,129 - 20,000.005 = 6,266.995, rounded half-up to the cent:
    # 6,267.00.
    assert total((0, "0", "16129", "20000.005")) == D("6267.00")
    # 20,000.004 leaves 6,266.996 -> 6,267.00; 20,000.006 leaves 6,266.994 -> 6,266.99.
    assert total((0, "0", "16129", "20000.004")) == D("6267.00")
    assert total((0, "0", "16129", "20000.006")) == D("6266.99")


def test_a_sub_cent_figure_of_line_8_is_rounded_once_at_line_13() -> None:
    # Line 5 = 5,000.005 - 3,464.00 = 1,536.005; line 6 = 4,377.995; line 8 = 14,515.995, rounded
    # half-up at line 13 to 14,516.00.
    assert total((1, "5000.005", "0", "0")) == D("14516.00")


def test_the_rounding_is_done_once_per_dependant_before_they_are_summed() -> None:
    # Per dependant: 6,266.995 -> 6,267.00, twice: 12,534.00. Rounding only the total of the exact
    # amounts, 12,533.99, would be wrong.
    both = total((0, "0", "16129", "20000.005"), (0, "0", "16129", "20000.005"))
    assert both == D("12534.00")


def test_the_rounding_rule_comes_from_the_maximum_dataset() -> None:
    wired = capability(
        base=amount("ca/disability_transfer_base_amount", "10138.00", NO_ROUNDING),
        supplement=amount("ca/disability_transfer_supplement_maximum", "5914.00", NO_ROUNDING),
        threshold=amount("ca/disability_transfer_care_threshold", "3464.00", NO_ROUNDING),
        maximum=amount("ca/disability_transfer_maximum", "16052", DOLLAR_FLOOR),
    )

    # Line 12 = 10,138.00 + 16,129 - 20,000.005 = 6,266.995, floored to the dollar: 6,266.
    assert compute(wired, (0, "0", "16129", "20000.005")).value == D("6266")


def test_the_other_datasets_rounding_rules_are_not_used() -> None:
    wired = capability(
        base=amount("ca/disability_transfer_base_amount", "10138.00", DOLLAR_FLOOR),
        supplement=amount("ca/disability_transfer_supplement_maximum", "5914.00", DOLLAR_FLOOR),
        threshold=amount("ca/disability_transfer_care_threshold", "3464.00", DOLLAR_FLOOR),
        maximum=amount("ca/disability_transfer_maximum", "16052", NO_ROUNDING),
    )

    assert compute(wired, (0, "0", "16129", "20000.005")).value == D("6266.995")


def test_a_rounded_allowable_amount_carries_the_increments_scale() -> None:
    assert str(compute(capability(), AGED_20).value) == "6267.00"
    assert str(compute(capability(), AGED_20, AGED_17).value) == "20783.00"


# --- computing: inputs --------------------------------------------------------------------------


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(DEPENDANT_NET_INCOME, D("9"))

    result = capability().compute((other, dependants(AGED_20)))

    assert result.outputs == (Artifact(DISABILITY_TRANSFERRED_AMOUNT, D("6267.00")),)


def test_missing_dependants_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="disability_dependants"):
        capability().compute(())


def test_has_one_output() -> None:
    assert len(capability().compute((dependants(AGED_20, AGED_17),)).outputs) == 1


def test_the_output_is_a_decimal_of_the_output_kind() -> None:
    (output,) = capability().compute((dependants(AGED_20),)).outputs

    assert output.kind is DISABILITY_TRANSFERRED_AMOUNT
    assert type(output.value) is Decimal


# --- trace --------------------------------------------------------------------------------------


def aged_20_line(position: int = 1, rounding: RoundingRule = CENT) -> DisabilityTransferLine:
    """Aged 20: lines 5 and 6 are worked from nothing, line 7 is "0"."""
    return DisabilityTransferLine(
        output=DISABILITY_TRANSFERRED_AMOUNT,
        position=position,
        base=Amount(D("10138.00")),
        supplement=Amount(D("5914.00")),
        threshold=Amount(D("3464.00")),
        maximum=Amount(D("16052")),
        under_18=0,
        care_expenses=D("0"),
        line_5=D("0"),
        line_6=D("5914.00"),
        line_7=D("0"),
        line_8=D("10138.00"),
        credit_amounts=D("16129"),
        line_10=D("26267.00"),
        taxable_income=D("20000"),
        line_12=D("6267.00"),
        rounding=rounding,
        result=D("6267.00"),
    )


def aged_17_line(position: int = 1) -> DisabilityTransferLine:
    """Under 18, care expenses 5,000, nothing on their return."""
    return DisabilityTransferLine(
        output=DISABILITY_TRANSFERRED_AMOUNT,
        position=position,
        base=Amount(D("10138.00")),
        supplement=Amount(D("5914.00")),
        threshold=Amount(D("3464.00")),
        maximum=Amount(D("16052")),
        under_18=1,
        care_expenses=D("5000"),
        line_5=D("1536.00"),
        line_6=D("4378.00"),
        line_7=D("4378.00"),
        line_8=D("14516.00"),
        credit_amounts=D("0"),
        line_10=D("14516.00"),
        taxable_income=D("0"),
        line_12=D("14516.00"),
        rounding=CENT,
        result=D("14516.00"),
    )


def test_traces_one_line_per_dependant_then_the_total() -> None:
    trace = capability().compute((dependants(AGED_20, AGED_17),)).trace

    assert trace == (
        aged_20_line(1),
        aged_17_line(2),
        ItemsTotalLine(
            DISABILITY_TRANSFERRED_AMOUNT, ((1, D("6267.00")), (2, D("14516.00"))), D("20783.00")
        ),
    )


def test_traces_the_callers_order_with_positions_from_one() -> None:
    trace = capability().compute((dependants(AGED_17, AGED_20),)).trace

    assert trace == (
        aged_17_line(1),
        aged_20_line(2),
        ItemsTotalLine(
            DISABILITY_TRANSFERRED_AMOUNT, ((1, D("14516.00")), (2, D("6267.00"))), D("20783.00")
        ),
    )


def test_traces_one_dependant_as_a_line_and_a_total() -> None:
    trace = capability().compute((dependants(AGED_20),)).trace

    assert trace == (
        aged_20_line(1),
        ItemsTotalLine(DISABILITY_TRANSFERRED_AMOUNT, ((1, D("6267.00")),), D("6267.00")),
    )


def test_traces_no_dependants_as_only_an_empty_total() -> None:
    trace = capability().compute((dependants(),)).trace

    assert trace == (ItemsTotalLine(DISABILITY_TRANSFERRED_AMOUNT, (), D("0")),)


def test_traces_each_worksheet_figure_of_a_dependant_aged_18_or_older() -> None:
    (line, _) = capability().compute((dependants((0, "5000", "16129", "20000")),)).trace

    assert isinstance(line, DisabilityTransferLine)
    assert line.under_18 == 0
    assert line.care_expenses == D("5000")
    # Line 7 is "0" at 18 or older, whatever lines 3 to 6 hold.
    assert line.line_7 == D("0")
    assert line.line_8 == D("10138.00")
    assert line.credit_amounts == D("16129")
    assert line.line_10 == D("26267.00")
    assert line.taxable_income == D("20000")
    assert line.line_12 == D("6267.00")
    assert line.result == D("6267.00")


def test_traces_each_worksheet_figure_of_a_dependant_under_18() -> None:
    (line, _) = capability().compute((dependants((1, "5000", "1000", "2000")),)).trace

    assert isinstance(line, DisabilityTransferLine)
    assert line.under_18 == 1
    assert line.care_expenses == D("5000")
    assert line.line_5 == D("1536.00")
    assert line.line_6 == D("4378.00")
    assert line.line_7 == D("4378.00")
    assert line.line_8 == D("14516.00")
    assert line.credit_amounts == D("1000")
    assert line.line_10 == D("15516.00")
    assert line.taxable_income == D("2000")
    assert line.line_12 == D("13516.00")
    assert line.result == D("13516.00")


def test_traces_the_datasets_figures() -> None:
    wired = capability(
        base=amount("ca/b", "100"),
        supplement=amount("ca/s", "50"),
        threshold=amount("ca/t", "10"),
        maximum=amount("ca/m", "140"),
    )

    (line, _) = wired.compute((dependants((1, "20", "0", "0")),)).trace

    assert isinstance(line, DisabilityTransferLine)
    assert line.base == Amount(D("100"))
    assert line.supplement == Amount(D("50"))
    assert line.threshold == Amount(D("10"))
    assert line.maximum == Amount(D("140"))
    # Line 5 = 20 - 10 = 10; line 6 = 50 - 10 = 40; line 8 = 100 + 40 = 140, at most 140.
    assert (line.line_5, line.line_6, line.line_7, line.line_8) == (
        D("10"),
        D("40"),
        D("40"),
        D("140"),
    )


def test_traces_line_5_and_line_6_floored_at_zero() -> None:
    (line, _) = capability().compute((dependants((1, "10000", "0", "0")),)).trace

    assert isinstance(line, DisabilityTransferLine)
    assert line.line_5 == D("6536.00")
    assert line.line_6 == D("0")
    assert not line.line_6.is_signed()
    assert line.line_7 == D("0")
    assert line.line_8 == D("10138.00")
    (below, _) = capability().compute((dependants((1, "100", "0", "0")),)).trace
    assert isinstance(below, DisabilityTransferLine)
    assert below.line_5 == D("0")
    assert not below.line_5.is_signed()


def test_traces_line_8_cut_at_the_maximum() -> None:
    wired = capability(maximum=amount("ca/disability_transfer_maximum", "15000"))

    (line, _) = wired.compute((dependants((1, "0", "0", "0")),)).trace

    assert isinstance(line, DisabilityTransferLine)
    assert line.line_7 == D("5914.00")
    assert line.line_8 == D("15000")
    assert line.maximum == Amount(D("15000"))


def test_traces_line_12_floored_at_zero_with_line_10_unfloored() -> None:
    (line, total_line) = capability().compute((dependants((0, "0", "0", "20000")),)).trace

    assert isinstance(line, DisabilityTransferLine)
    assert line.line_10 == D("10138.00")
    assert line.taxable_income == D("20000")
    assert line.line_12 == D("0")
    assert not line.line_12.is_signed()
    assert line.result == D("0")
    assert not line.result.is_signed()
    assert isinstance(total_line, ItemsTotalLine)
    assert total_line.total == D("0")
    assert not total_line.total.is_signed()


def test_traces_the_lesser_of_line_8_and_line_12_when_line_8_is_less() -> None:
    (line, _) = capability().compute((dependants((0, "0", "16129", "0")),)).trace

    assert isinstance(line, DisabilityTransferLine)
    assert line.line_8 == D("10138.00")
    assert line.line_12 == D("26267.00")
    assert line.result == D("10138.00")


def test_traces_the_datasets_rounding_rule_and_the_rounded_amount() -> None:
    line, total_line = capability().compute((dependants((0, "0", "16129", "20000.005")),)).trace

    assert isinstance(line, DisabilityTransferLine)
    assert line.rounding == CENT
    # Lines 8 to 12 are exact; only line 13 is rounded.
    assert line.taxable_income == D("20000.005")
    assert line.line_10 == D("26267.00")
    assert line.line_12 == D("6266.995")
    assert line.result == D("6267.00")
    assert total_line == ItemsTotalLine(
        DISABILITY_TRANSFERRED_AMOUNT, ((1, D("6267.00")),), D("6267.00")
    )


def test_traces_the_maximum_datasets_rounding_rule() -> None:
    wired = capability(
        base=amount("ca/disability_transfer_base_amount", "10138.00", NO_ROUNDING),
        maximum=amount("ca/disability_transfer_maximum", "16052", DOLLAR_FLOOR),
    )

    (line, _) = wired.compute((dependants((0, "0", "16129", "20000.005")),)).trace

    assert isinstance(line, DisabilityTransferLine)
    assert line.rounding == DOLLAR_FLOOR
    assert line.result == D("6266")


def test_the_last_trace_line_amount_is_the_output() -> None:
    result = capability().compute((dependants(AGED_20, AGED_17),))

    (output,) = result.outputs
    assert result.trace[-1].amount == output.value
    assert [line.amount for line in result.trace[:-1]] == [D("6267.00"), D("14516.00")]


def test_the_total_is_the_sum_of_its_items() -> None:
    *_, total_line = capability().compute((dependants(AGED_20, AGED_17, (0, "0", "0", "0")),)).trace

    assert isinstance(total_line, ItemsTotalLine)
    assert total_line.total == sum((amount for _, amount in total_line.items), D("0"))


def test_compute_is_repeatable() -> None:
    wired = capability()
    given = (dependants(AGED_20, AGED_17),)

    assert wired.compute(given) == wired.compute(given)
