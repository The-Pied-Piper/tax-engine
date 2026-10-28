"""Unit tests for the OntarioDisabilityTransferAmount capability, line 58480.

Its identifier is `ca-on/disability_transfer_amount`; it produces ON428 line 30 (line 58480).

Worksheet ON428 (form 5006-D), "Line 58480 - Disability amount transferred from a dependant":
"Complete this calculation for each dependant."; line 1 "Base amount 10,298.00"; "If the dependant
was under 18 years of age on December 31, 2025, complete lines 2 to 12. If the dependant was 18
years of age or older, enter "0" on line 6 and continue on line 7."; line 2 "Maximum amount
6,007.00"; line 3 "Total child care and attendant care expenses for this dependant claimed by
you or another person"; line 4 "Threshold for child and attendant care expenses 3,518.00"; line 5
"Line 3 minus line 4 (if negative, enter "0")"; line 6 "Line 2 minus line 5 (if negative, enter
"0")"; line 7 "Line 1 plus line 6 (maximum $16,305)"; line 8 "Enter the amount from line 28 of the
dependant's Form ON428."; line 9 "Line 7 plus line 8"; line 10 "Dependant's taxable income from
line 26000 of their return"; line 11 "Line 9 minus line 10 (if negative, enter "0")"; line 12
"Enter whichever is less: amount from line 7 or line 11. Allowable amount for this dependant";
"Enter the total of allowable amounts claimed for all dependants on line 58480 of your Form
ON428."

Its slots: four parameter slots `base`, `supplement`, `threshold` and `maximum` (`amount` datasets,
lines 1, 2, 4 and 7's maximum), one consumed slot `dependants` (a record list whose records hold
each dependant's figures: under 18, care expenses, line 28 of their ON428 and their taxable income)
and one produced slot `output`. Each dependant is worked on its own, never pooled: line 12 is
rounded once, with the `maximum` dataset's rule, and the output is their total. It records one
`DisabilityTransferLine` per dependant (the federal trace line, whose field names follow the
federal worksheet's numbering: `line_8` is the Ontario worksheet's line 7, `credit_amounts` its
line 8, `line_10` its line 9, `taxable_income` its line 10 and `line_12` its line 11), then an
`ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.jurisdictions.ca_on.capabilities as ca_on_capabilities
from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.artifact import Artifact, ArtifactKind
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
from tax_calculator.jurisdictions.ca.capabilities.disability_transfer_amount import (
    DisabilityTransferAmount,
)
from tax_calculator.jurisdictions.ca.catalog import (
    DEPENDANT_CARE_EXPENSES,
    DEPENDANT_NET_INCOME,
    DEPENDANT_TAXABLE_INCOME,
    DEPENDANT_UNDER_18,
)
from tax_calculator.jurisdictions.ca.trace import DisabilityTransferLine
from tax_calculator.jurisdictions.ca_on.capabilities.disability_transfer_amount import (
    OntarioDisabilityTransferAmount,
)
from tax_calculator.jurisdictions.ca_on.catalog import (
    CAREGIVER_AMOUNT,
    DEPENDANT_ON428_LINE_28,
    DISABILITY_DEPENDANTS,
    DISABILITY_TRANSFERRED_AMOUNT,
)

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
DOLLAR_FLOOR = RoundTo(D("1"), RoundingMode.FLOOR)

# One dependant's figures, as the worksheet asks for them: under 18 on December 31, 2025 (1 or 0),
# line 3 the care expenses, line 8 line 28 of their Form ON428 and line 10 their taxable income.
Figures = tuple[int, str, str, str]
AGED_20: Figures = (0, "0", "15000", "20000")
AGED_17: Figures = (1, "5000", "0", "0")


def amount(family: str, value: str, rounding: RoundingRule = CENT) -> ParameterDataset[Amount]:
    return ParameterDataset(
        family, 2025, AMOUNT, Amount(D(value)), rounding, ("https://example.org/on428-worksheet",)
    )


def capability(
    base: ParameterDataset[Amount] | None = None,
    supplement: ParameterDataset[Amount] | None = None,
    threshold: ParameterDataset[Amount] | None = None,
    maximum: ParameterDataset[Amount] | None = None,
) -> OntarioDisabilityTransferAmount:
    """By default the 2025 figures: line 1 10,298.00, line 2 6,007.00, line 4 3,518.00 and line 7's
    maximum 16,305, each to the cent."""
    return OntarioDisabilityTransferAmount(
        base or amount("ca-on/disability_transfer_base_amount", "10298.00"),
        supplement or amount("ca-on/disability_transfer_supplement_maximum", "6007.00"),
        threshold or amount("ca-on/disability_transfer_care_threshold", "3518.00"),
        maximum or amount("ca-on/disability_transfer_maximum", "16305"),
        DISABILITY_DEPENDANTS,
        DISABILITY_TRANSFERRED_AMOUNT,
    )


def dependants(*given: Figures) -> Artifact[Any]:
    """A `ca-on/disability_dependants` artifact of one record per dependant, in the order given."""
    records: list[dict[ArtifactKind[Any], object]] = [
        {
            DEPENDANT_UNDER_18: under_18,
            DEPENDANT_CARE_EXPENSES: D(care),
            DEPENDANT_ON428_LINE_28: D(line_28),
            DEPENDANT_TAXABLE_INCOME: D(taxable),
        }
        for under_18, care, line_28, taxable in given
    ]
    return Artifact(DISABILITY_DEPENDANTS, RecordList(DISABILITY_DEPENDANTS.fields, records))


def compute(wired: OntarioDisabilityTransferAmount, *given: Figures) -> Artifact[Any]:
    (output,) = wired.compute((dependants(*given),)).outputs
    return output


def total(*given: Figures) -> Decimal:
    value = compute(capability(), *given).value
    assert isinstance(value, Decimal)
    return value


def test_is_registered_as_ca_on_disability_transfer_amount() -> None:
    assert (
        CapabilityRegistry.shared().get("ca-on/disability_transfer_amount")
        is OntarioDisabilityTransferAmount
    )


def test_is_exported_from_the_ca_on_capabilities_package() -> None:
    assert ca_on_capabilities.NAMESPACE == "ca-on"
    assert "disability_transfer_amount" in ca_on_capabilities.__all__
    assert (
        ca_on_capabilities.disability_transfer_amount.OntarioDisabilityTransferAmount
        is OntarioDisabilityTransferAmount
    )


def test_is_not_the_federal_capability() -> None:
    assert CapabilityRegistry.shared().get("ca/disability_transfer_amount") is (
        DisabilityTransferAmount
    )


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({DISABILITY_DEPENDANTS})
    assert capability().produces == frozenset({DISABILITY_TRANSFERRED_AMOUNT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(OntarioDisabilityTransferAmount)
    assert "produces" not in vars(OntarioDisabilityTransferAmount)


def test_declares_its_slots() -> None:
    assert OntarioDisabilityTransferAmount.PARAMETERS == {
        "base": AMOUNT,
        "supplement": AMOUNT,
        "threshold": AMOUNT,
        "maximum": AMOUNT,
    }
    assert list(OntarioDisabilityTransferAmount.PARAMETERS) == [
        "base",
        "supplement",
        "threshold",
        "maximum",
    ]
    assert OntarioDisabilityTransferAmount.CONSUMES == {"dependants": RecordList}
    assert OntarioDisabilityTransferAmount.PRODUCES == {"output": Decimal}
    assert not OntarioDisabilityTransferAmount.is_list_slot("dependants")


def test_its_slots_are_read_only() -> None:
    for slots in (
        OntarioDisabilityTransferAmount.PARAMETERS,
        OntarioDisabilityTransferAmount.CONSUMES,
        OntarioDisabilityTransferAmount.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(OntarioDisabilityTransferAmount.PARAMETERS, Mapping[str, ParameterKind[Amount]])
    assert_type(OntarioDisabilityTransferAmount.CONSUMES, Mapping[str, type])
    assert_type(OntarioDisabilityTransferAmount.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (
        OntarioDisabilityTransferAmount.PARAMETERS,
        OntarioDisabilityTransferAmount.CONSUMES,
        OntarioDisabilityTransferAmount.PRODUCES,
    ):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = OntarioDisabilityTransferAmount(
        base=amount("ca-on/disability_transfer_base_amount", "10298.00"),
        supplement=amount("ca-on/disability_transfer_supplement_maximum", "6007.00"),
        threshold=amount("ca-on/disability_transfer_care_threshold", "3518.00"),
        maximum=amount("ca-on/disability_transfer_maximum", "16305"),
        dependants=DISABILITY_DEPENDANTS,
        output=DISABILITY_TRANSFERRED_AMOUNT,
    )

    assert compute(wired, AGED_20) == Artifact(DISABILITY_TRANSFERRED_AMOUNT, D("5298.00"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        OntarioDisabilityTransferAmount(  # type: ignore[call-arg]
            amount("ca-on/disability_transfer_base_amount", "10298.00"),
            amount("ca-on/disability_transfer_supplement_maximum", "6007.00"),
            amount("ca-on/disability_transfer_care_threshold", "3518.00"),
            amount("ca-on/disability_transfer_maximum", "16305"),
            DISABILITY_DEPENDANTS,
            DISABILITY_TRANSFERRED_AMOUNT,
            CENT,
        )


def test_rejects_a_money_kind_for_its_dependants() -> None:
    with pytest.raises(
        InvalidCapabilityError, match="OntarioDisabilityTransferAmount.*'dependants'"
    ):
        OntarioDisabilityTransferAmount(
            amount("ca-on/disability_transfer_base_amount", "10298.00"),
            amount("ca-on/disability_transfer_supplement_maximum", "6007.00"),
            amount("ca-on/disability_transfer_care_threshold", "3518.00"),
            amount("ca-on/disability_transfer_maximum", "16305"),
            CAREGIVER_AMOUNT,  # type: ignore[arg-type]
            DISABILITY_TRANSFERRED_AMOUNT,
        )


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(OntarioDisabilityTransferAmount, "__type_params__", ())
    assert not getattr(OntarioDisabilityTransferAmount, "__parameters__", ())


# --- computing: how many dependants -------------------------------------------------------------


def test_no_dependants_give_zero() -> None:
    output = compute(capability())

    assert output == Artifact(DISABILITY_TRANSFERRED_AMOUNT, D("0"))
    assert type(output.value) is Decimal
    assert not output.value.is_signed()


def test_one_dependant_gives_the_per_item_figure() -> None:
    # Aged 20 (line 6 is "0"), line 7 10,298.00; line 9 = 10,298.00 + 15,000 = 25,298.00; line 11
    # = 25,298.00 - 20,000 = 5,298.00; line 12 = lesser(10,298.00, 5,298.00) = 5,298.00.
    assert total(AGED_20) == D("5298.00")


def test_one_dependant_under_18_gives_the_per_item_figure() -> None:
    # Line 5: 5,000 - 3,518.00 = 1,482.00; line 6: 6,007.00 - 1,482.00 = 4,525.00; line 7:
    # 10,298.00 + 4,525.00 = 14,823.00 (under the 16,305 maximum); line 9 = line 7 + 0; line 11 =
    # line 9 - 0; line 12 = lesser(14,823.00, 14,823.00).
    assert total(AGED_17) == D("14823.00")


def test_two_dependants_give_the_sum_of_their_own_amounts() -> None:
    # 5,298.00 (aged 20) + 14,823.00 (aged 17).
    assert total(AGED_20, AGED_17) == D("20121.00")


def test_three_dependants_are_summed_one_by_one() -> None:
    # 5,298.00 + 14,823.00 + 10,298.00 (aged 30, line 11 = 10,298.00 + 5,000 - 0 over line 7).
    assert total(AGED_20, AGED_17, (0, "0", "5000", "0")) == D("30419.00")


def test_a_dependant_with_nothing_transferable_adds_nothing_to_the_others() -> None:
    assert total((0, "0", "0", "20000"), AGED_20) == D("5298.00")


def test_the_total_does_not_depend_on_the_order() -> None:
    assert total(AGED_17, AGED_20) == total(AGED_20, AGED_17)


# --- computing: under 18 or 18 and older (lines 1 to 7) -----------------------------------------


def test_a_dependant_aged_18_or_older_has_line_6_zero_whatever_the_care_expenses() -> None:
    # "If the dependant was 18 years of age or older, enter "0" on line 6". Line 7 is the base
    # alone.
    assert total((0, "0", "0", "0")) == D("10298.00")
    assert total((0, "5000", "0", "0")) == D("10298.00")
    assert total((0, "0.01", "0", "0")) == D("10298.00")


def test_a_dependant_under_18_with_no_care_expenses_takes_the_whole_line_2_amount() -> None:
    # Line 3 is 0: line 5 is -3,518.00, entered as "0"; line 6 is 6,007.00; line 7 is 10,298.00 +
    # 6,007.00 = 16,305.00, the maximum.
    assert total((1, "0", "0", "0")) == D("16305.00")


def test_care_expenses_at_the_threshold_leave_line_5_zero_and_the_whole_line_2_amount() -> None:
    assert total((1, "3518", "0", "0")) == D("16305.00")
    assert total((1, "3518.00", "0", "0")) == D("16305.00")


def test_care_expenses_below_the_threshold_leave_line_5_zero_and_the_whole_line_2_amount() -> None:
    assert total((1, "3000", "0", "0")) == D("16305.00")
    assert total((1, "3517.99", "0", "0")) == D("16305.00")


def test_care_expenses_a_cent_above_the_threshold_take_a_cent_off_line_6() -> None:
    # Line 5: 3,518.01 - 3,518.00 = 0.01; line 6: 6,007.00 - 0.01 = 6,006.99; line 7: 16,304.99.
    assert total((1, "3518.01", "0", "0")) == D("16304.99")


def test_care_expenses_above_the_threshold_reduce_line_6_dollar_for_dollar() -> None:
    # Line 5: 5,000 - 3,518.00 = 1,482.00; line 6: 4,525.00; line 7: 14,823.00.
    assert total((1, "5000", "0", "0")) == D("14823.00")
    # Line 5: 4,000 - 3,518.00 = 482.00; line 6: 5,525.00; line 7: 15,823.00.
    assert total((1, "4000", "0", "0")) == D("15823.00")


def test_care_expenses_of_the_threshold_plus_line_2_leave_line_6_zero() -> None:
    # Line 5: 9,525 - 3,518.00 = 6,007.00; line 6: 6,007.00 - 6,007.00 = 0; line 7: 10,298.00.
    assert total((1, "9525", "0", "0")) == D("10298.00")


def test_care_expenses_above_the_threshold_plus_line_2_leave_line_6_zero_not_negative() -> None:
    # Line 5: 10,000 - 3,518.00 = 6,482.00; line 6: 6,007.00 - 6,482.00 is negative, entered "0".
    assert total((1, "10000", "0", "0")) == D("10298.00")
    assert total((1, "9525.01", "0", "0")) == D("10298.00")
    assert total((1, "999999.99", "0", "0")) == D("10298.00")


def test_a_dependant_under_18_and_one_aged_18_or_older_each_follow_their_own_lines() -> None:
    assert total((1, "5000", "0", "0")) == D("14823.00")
    assert total((0, "5000", "0", "0")) == D("10298.00")
    assert total((1, "5000", "0", "0"), (0, "5000", "0", "0")) == D("25121.00")


# --- computing: line 7's maximum ----------------------------------------------------------------


def test_the_2025_line_2_amount_added_to_the_base_reaches_the_maximum_exactly() -> None:
    # 10,298.00 + 6,007.00 = 16,305.00: "(maximum $16,305)" is never cut by the 2025 figures.
    assert total((1, "0", "0", "0")) == D("16305.00")


def test_line_7_is_at_most_the_maximum_dataset() -> None:
    wired = capability(maximum=amount("ca-on/disability_transfer_maximum", "15000"))

    # 10,298.00 + 6,007.00 = 16,305.00, cut to 15,000.
    assert compute(wired, (1, "0", "0", "0")).value == D("15000.00")
    # 10,298.00 + 4,525.00 = 14,823.00, under the 15,000 maximum.
    assert compute(wired, (1, "5000", "0", "0")).value == D("14823.00")
    # 10,298.00 + 4,702.00 = 15,000.00: just reaches it (line 5 = 1,305.00, expenses 4,823).
    assert compute(wired, (1, "4823", "0", "0")).value == D("15000.00")
    # 10,298.00 + 4,701.99 = 14,999.99: a cent under it.
    assert compute(wired, (1, "4823.01", "0", "0")).value == D("14999.99")


def test_line_11_is_taken_from_the_capped_line_7() -> None:
    wired = capability(maximum=amount("ca-on/disability_transfer_maximum", "15000"))

    # Line 7 is 15,000; line 9 = 15,000 + 100 = 15,100; line 11 = 15,100 - 0; lesser(15,000,
    # 15,100) = 15,000, not the uncapped 16,305.
    assert compute(wired, (1, "0", "100", "0")).value == D("15000.00")


# --- computing: lines 8 to 12 -------------------------------------------------------------------


def test_line_11_is_line_7_plus_line_8_less_the_taxable_income() -> None:
    # Line 11 = 10,298.00 + 15,000 - 20,000 = 5,298.00, under line 7.
    assert total((0, "0", "15000", "20000")) == D("5298.00")
    # 10,298.00 + 15,000 - 25,000 = 298.00.
    assert total((0, "0", "15000", "25000")) == D("298.00")
    # 10,298.00 + 1,000 - 5,000 = 6,298.00.
    assert total((0, "0", "1000", "5000")) == D("6298.00")


def test_line_12_is_line_11_when_that_is_less_than_line_7() -> None:
    assert total((0, "0", "15000", "20000")) == D("5298.00")


def test_line_12_is_line_7_when_that_is_less_than_line_11() -> None:
    # Line 11 = 10,298.00 + 15,000 - 0 = 25,298.00, over line 7.
    assert total((0, "0", "15000", "0")) == D("10298.00")


def test_line_12_is_line_7_when_line_7_equals_line_11() -> None:
    # No line 28 amount and no taxable income: line 11 = 10,298.00 = line 7.
    assert total((0, "0", "0", "0")) == D("10298.00")
    # Line 9 = line 7 + 5,000; taxable income 5,000.
    assert total((0, "0", "5000", "5000")) == D("10298.00")


def test_line_11_a_cent_under_line_7_is_the_amount() -> None:
    assert total((0, "0", "0", "0.01")) == D("10297.99")


def test_line_11_is_zero_when_the_taxable_income_exceeds_line_9() -> None:
    # Line 9 = 10,298.00 + 0; line 11 = 10,298.00 - 20,000 is negative, entered "0".
    assert total((0, "0", "0", "20000")) == D("0")


def test_a_taxable_income_equal_to_line_9_leaves_plain_zero() -> None:
    output = compute(capability(), (0, "0", "0", "10298"))

    assert output.value == D("0")
    assert not output.value.is_signed()


def test_a_taxable_income_a_cent_over_line_9_leaves_plain_zero_never_negative() -> None:
    value = total((0, "0", "0", "10298.01"))

    assert value == D("0")
    assert not value.is_signed()


@pytest.mark.parametrize("taxable", ["10298.01", "10299", "20000", "100000", "99999999.99"])
def test_a_taxable_income_above_line_9_gives_plain_zero_never_negative(taxable: str) -> None:
    value = total((0, "0", "0", taxable))

    assert value == D("0")
    assert not value.is_signed()


def test_every_dependant_with_nothing_transferable_gives_plain_zero() -> None:
    value = total((0, "0", "0", "20000"), (1, "0", "0", "90000"))

    assert value == D("0")
    assert not value.is_signed()


def test_the_floor_is_per_dependant_so_a_dependant_over_the_limit_does_not_reduce_another() -> None:
    # 0 + 5,298.00, not 5,298.00 - 9,702.00.
    assert total((0, "0", "0", "20000"), AGED_20) == D("5298.00")


def test_the_line_8_amount_of_a_dependant_under_18_adds_to_line_7_with_its_line_2_amount() -> None:
    # Line 7 = 14,823.00; line 9 = 14,823.00 + 1,000; line 11 = 15,823.00 - 2,000 = 13,823.00,
    # under line 7.
    assert total((1, "5000", "1000", "2000")) == D("13823.00")


def test_the_taxable_income_does_not_change_line_7() -> None:
    # Line 11 = 14,823.00 + 0 - 1,000 = 13,823.00.
    assert total((1, "5000", "0", "1000")) == D("13823.00")
    assert total((1, "5000", "0", "0")) == D("14823.00")


# --- computing: the datasets --------------------------------------------------------------------


def test_the_base_dataset_supplies_line_1() -> None:
    wired = capability(base=amount("ca-on/b", "100"), maximum=amount("ca-on/m", "1000"))

    assert compute(wired, (0, "0", "0", "0")).value == D("100")
    # Line 7 = 100 + 6,007.00 for an under 18; at most 1,000.
    assert compute(wired, (1, "0", "0", "0")).value == D("1000")


def test_the_supplement_dataset_supplies_line_2() -> None:
    wired = capability(supplement=amount("ca-on/s", "500"), maximum=amount("ca-on/m", "100000"))

    # Line 5 is 0 (no expenses); line 6 is 500; line 7 = 10,298 + 500.
    assert compute(wired, (1, "0", "0", "0")).value == D("10798")
    # Line 5 = 3,818 - 3,518.00 = 300; line 6 = 200.
    assert compute(wired, (1, "3818", "0", "0")).value == D("10498")


def test_the_threshold_dataset_supplies_line_4() -> None:
    wired = capability(threshold=amount("ca-on/t", "1000"), maximum=amount("ca-on/m", "100000"))

    # Line 5 = 2,000 - 1,000 = 1,000; line 6 = 6,007 - 1,000 = 5,007; line 7 = 15,305.
    assert compute(wired, (1, "2000", "0", "0")).value == D("15305")


def test_the_maximum_dataset_supplies_line_7s_maximum() -> None:
    wired = capability(maximum=amount("ca-on/m", "12000"))

    assert compute(wired, (0, "0", "0", "0")).value == D("10298")
    assert compute(wired, (1, "0", "0", "0")).value == D("12000")


def test_a_different_year_figure_changes_the_result() -> None:
    wired = capability(
        base=amount("ca-on/disability_transfer_base_amount", "10500.00"),
        supplement=amount("ca-on/disability_transfer_supplement_maximum", "6100.00"),
        threshold=amount("ca-on/disability_transfer_care_threshold", "3600.00"),
        maximum=amount("ca-on/disability_transfer_maximum", "16600"),
    )

    # Aged 20: line 7 = 10,500.00; line 11 = 10,500.00 + 15,000 - 20,000 = 5,500.00.
    assert compute(wired, AGED_20).value == D("5500.00")
    # Under 18: line 5 = 5,000 - 3,600.00 = 1,400.00; line 6 = 4,700.00; line 7 = 15,200.00.
    assert compute(wired, AGED_17).value == D("15200.00")


# --- computing: rounding ------------------------------------------------------------------------


def test_each_allowable_amount_is_rounded_half_up_to_the_cent() -> None:
    # Line 11 = 10,298.00 + 15,000 - 20,000.005 = 5,297.995, rounded half-up to the cent:
    # 5,298.00.
    assert total((0, "0", "15000", "20000.005")) == D("5298.00")
    # 20,000.004 leaves 5,297.996 -> 5,298.00; 20,000.006 leaves 5,297.994 -> 5,297.99.
    assert total((0, "0", "15000", "20000.004")) == D("5298.00")
    assert total((0, "0", "15000", "20000.006")) == D("5297.99")


def test_a_sub_cent_figure_of_line_7_is_rounded_once_at_line_12() -> None:
    # Line 5 = 5,000.005 - 3,518.00 = 1,482.005; line 6 = 4,524.995; line 7 = 14,822.995, rounded
    # half-up at line 12 to 14,823.00.
    assert total((1, "5000.005", "0", "0")) == D("14823.00")


def test_the_rounding_is_done_once_per_dependant_before_they_are_summed() -> None:
    # Per dependant: 5,297.995 -> 5,298.00, twice: 10,596.00. Rounding only the total of the exact
    # amounts, 10,595.99, would be wrong.
    both = total((0, "0", "15000", "20000.005"), (0, "0", "15000", "20000.005"))
    assert both == D("10596.00")


def test_the_rounding_rule_comes_from_the_maximum_dataset() -> None:
    wired = capability(
        base=amount("ca-on/disability_transfer_base_amount", "10298.00", NO_ROUNDING),
        supplement=amount("ca-on/disability_transfer_supplement_maximum", "6007.00", NO_ROUNDING),
        threshold=amount("ca-on/disability_transfer_care_threshold", "3518.00", NO_ROUNDING),
        maximum=amount("ca-on/disability_transfer_maximum", "16305", DOLLAR_FLOOR),
    )

    # Line 11 = 10,298.00 + 15,000 - 20,000.005 = 5,297.995, floored to the dollar: 5,297.
    assert compute(wired, (0, "0", "15000", "20000.005")).value == D("5297")


def test_the_other_datasets_rounding_rules_are_not_used() -> None:
    wired = capability(
        base=amount("ca-on/disability_transfer_base_amount", "10298.00", DOLLAR_FLOOR),
        supplement=amount("ca-on/disability_transfer_supplement_maximum", "6007.00", DOLLAR_FLOOR),
        threshold=amount("ca-on/disability_transfer_care_threshold", "3518.00", DOLLAR_FLOOR),
        maximum=amount("ca-on/disability_transfer_maximum", "16305", NO_ROUNDING),
    )

    assert compute(wired, (0, "0", "15000", "20000.005")).value == D("5297.995")


def test_a_rounded_allowable_amount_carries_the_increments_scale() -> None:
    assert str(compute(capability(), AGED_20).value) == "5298.00"
    assert str(compute(capability(), AGED_20, AGED_17).value) == "20121.00"


# --- computing: inputs --------------------------------------------------------------------------


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(DEPENDANT_NET_INCOME, D("9"))

    result = capability().compute((other, dependants(AGED_20)))

    assert result.outputs == (Artifact(DISABILITY_TRANSFERRED_AMOUNT, D("5298.00")),)


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
# The federal `DisabilityTransferLine` is reused, with the federal worksheet's field names (13
# lines against Ontario's 12). Field by field, what it holds for the Ontario worksheet:
#   base = line 1, supplement = line 2, threshold = line 4, maximum = line 7's maximum;
#   under_18, care_expenses = line 3, line_5 = line 5, line_6 = line 6;
#   line_7 = line 6 as entered (0 at 18 or older), line_8 = line 7 (base plus that, at most the
#   maximum), credit_amounts = line 8 (line 28 of the dependant's ON428), line_10 = line 9,
#   taxable_income = line 10, line_12 = line 11, result = line 12 (rounded).


def aged_20_line(position: int = 1, rounding: RoundingRule = CENT) -> DisabilityTransferLine:
    """Aged 20: lines 5 and 6 are worked from nothing, line 6 as entered is "0"."""
    return DisabilityTransferLine(
        output=DISABILITY_TRANSFERRED_AMOUNT,
        position=position,
        base=Amount(D("10298.00")),
        supplement=Amount(D("6007.00")),
        threshold=Amount(D("3518.00")),
        maximum=Amount(D("16305")),
        under_18=0,
        care_expenses=D("0"),
        line_5=D("0"),
        line_6=D("6007.00"),
        line_7=D("0"),
        line_8=D("10298.00"),
        credit_amounts=D("15000"),
        line_10=D("25298.00"),
        taxable_income=D("20000"),
        line_12=D("5298.00"),
        rounding=rounding,
        result=D("5298.00"),
    )


def aged_17_line(position: int = 1) -> DisabilityTransferLine:
    """Under 18, care expenses 5,000, nothing on their return."""
    return DisabilityTransferLine(
        output=DISABILITY_TRANSFERRED_AMOUNT,
        position=position,
        base=Amount(D("10298.00")),
        supplement=Amount(D("6007.00")),
        threshold=Amount(D("3518.00")),
        maximum=Amount(D("16305")),
        under_18=1,
        care_expenses=D("5000"),
        line_5=D("1482.00"),
        line_6=D("4525.00"),
        line_7=D("4525.00"),
        line_8=D("14823.00"),
        credit_amounts=D("0"),
        line_10=D("14823.00"),
        taxable_income=D("0"),
        line_12=D("14823.00"),
        rounding=CENT,
        result=D("14823.00"),
    )


def test_traces_one_line_per_dependant_then_the_total() -> None:
    trace = capability().compute((dependants(AGED_20, AGED_17),)).trace

    assert trace == (
        aged_20_line(1),
        aged_17_line(2),
        ItemsTotalLine(
            DISABILITY_TRANSFERRED_AMOUNT, ((1, D("5298.00")), (2, D("14823.00"))), D("20121.00")
        ),
    )


def test_traces_the_callers_order_with_positions_from_one() -> None:
    trace = capability().compute((dependants(AGED_17, AGED_20),)).trace

    assert trace == (
        aged_17_line(1),
        aged_20_line(2),
        ItemsTotalLine(
            DISABILITY_TRANSFERRED_AMOUNT, ((1, D("14823.00")), (2, D("5298.00"))), D("20121.00")
        ),
    )


def test_traces_one_dependant_as_a_line_and_a_total() -> None:
    trace = capability().compute((dependants(AGED_20),)).trace

    assert trace == (
        aged_20_line(1),
        ItemsTotalLine(DISABILITY_TRANSFERRED_AMOUNT, ((1, D("5298.00")),), D("5298.00")),
    )


def test_traces_no_dependants_as_only_an_empty_total() -> None:
    trace = capability().compute((dependants(),)).trace

    assert trace == (ItemsTotalLine(DISABILITY_TRANSFERRED_AMOUNT, (), D("0")),)


def test_traces_the_federal_trace_line_class_and_no_other() -> None:
    trace = capability().compute((dependants(AGED_20, AGED_17),)).trace

    assert [type(line) for line in trace] == [
        DisabilityTransferLine,
        DisabilityTransferLine,
        ItemsTotalLine,
    ]


def test_traces_each_worksheet_figure_of_a_dependant_aged_18_or_older() -> None:
    (line, _) = capability().compute((dependants((0, "5000", "15000", "20000")),)).trace

    assert isinstance(line, DisabilityTransferLine)
    assert line.under_18 == 0
    assert line.care_expenses == D("5000")
    # The line 6 entered is "0" at 18 or older, whatever lines 3 to 5 hold.
    assert line.line_7 == D("0")
    # Ontario line 7.
    assert line.line_8 == D("10298.00")
    # Ontario line 8, line 28 of the dependant's ON428.
    assert line.credit_amounts == D("15000")
    # Ontario line 9.
    assert line.line_10 == D("25298.00")
    # Ontario line 10.
    assert line.taxable_income == D("20000")
    # Ontario line 11.
    assert line.line_12 == D("5298.00")
    # Ontario line 12.
    assert line.result == D("5298.00")


def test_traces_each_worksheet_figure_of_a_dependant_under_18() -> None:
    (line, _) = capability().compute((dependants((1, "5000", "1000", "2000")),)).trace

    assert isinstance(line, DisabilityTransferLine)
    assert line.under_18 == 1
    assert line.care_expenses == D("5000")
    assert line.line_5 == D("1482.00")
    assert line.line_6 == D("4525.00")
    assert line.line_7 == D("4525.00")
    assert line.line_8 == D("14823.00")
    assert line.credit_amounts == D("1000")
    assert line.line_10 == D("15823.00")
    assert line.taxable_income == D("2000")
    assert line.line_12 == D("13823.00")
    assert line.result == D("13823.00")


def test_traces_the_datasets_figures() -> None:
    wired = capability(
        base=amount("ca-on/b", "100"),
        supplement=amount("ca-on/s", "50"),
        threshold=amount("ca-on/t", "10"),
        maximum=amount("ca-on/m", "140"),
    )

    (line, _) = wired.compute((dependants((1, "20", "0", "0")),)).trace

    assert isinstance(line, DisabilityTransferLine)
    assert line.base == Amount(D("100"))
    assert line.supplement == Amount(D("50"))
    assert line.threshold == Amount(D("10"))
    assert line.maximum == Amount(D("140"))
    # Line 5 = 20 - 10 = 10; line 6 = 50 - 10 = 40; line 7 = 100 + 40 = 140, at most 140.
    assert (line.line_5, line.line_6, line.line_7, line.line_8) == (
        D("10"),
        D("40"),
        D("40"),
        D("140"),
    )


def test_traces_line_5_and_line_6_floored_at_zero() -> None:
    (line, _) = capability().compute((dependants((1, "10000", "0", "0")),)).trace

    assert isinstance(line, DisabilityTransferLine)
    assert line.line_5 == D("6482.00")
    assert line.line_6 == D("0")
    assert not line.line_6.is_signed()
    assert line.line_7 == D("0")
    assert line.line_8 == D("10298.00")
    (below, _) = capability().compute((dependants((1, "100", "0", "0")),)).trace
    assert isinstance(below, DisabilityTransferLine)
    assert below.line_5 == D("0")
    assert not below.line_5.is_signed()


def test_traces_line_7_cut_at_the_maximum() -> None:
    wired = capability(maximum=amount("ca-on/disability_transfer_maximum", "15000"))

    (line, _) = wired.compute((dependants((1, "0", "0", "0")),)).trace

    assert isinstance(line, DisabilityTransferLine)
    assert line.line_7 == D("6007.00")
    assert line.line_8 == D("15000")
    assert line.maximum == Amount(D("15000"))


def test_traces_line_11_floored_at_zero_with_line_9_unfloored() -> None:
    (line, total_line) = capability().compute((dependants((0, "0", "0", "20000")),)).trace

    assert isinstance(line, DisabilityTransferLine)
    assert line.line_10 == D("10298.00")
    assert line.taxable_income == D("20000")
    assert line.line_12 == D("0")
    assert not line.line_12.is_signed()
    assert line.result == D("0")
    assert not line.result.is_signed()
    assert isinstance(total_line, ItemsTotalLine)
    assert total_line.total == D("0")
    assert not total_line.total.is_signed()


def test_traces_the_lesser_of_line_7_and_line_11_when_line_7_is_less() -> None:
    (line, _) = capability().compute((dependants((0, "0", "15000", "0")),)).trace

    assert isinstance(line, DisabilityTransferLine)
    assert line.line_8 == D("10298.00")
    assert line.line_12 == D("25298.00")
    assert line.result == D("10298.00")


def test_traces_the_datasets_rounding_rule_and_the_rounded_amount() -> None:
    line, total_line = capability().compute((dependants((0, "0", "15000", "20000.005")),)).trace

    assert isinstance(line, DisabilityTransferLine)
    assert line.rounding == CENT
    # Lines 7 to 11 are exact; only line 12 is rounded.
    assert line.taxable_income == D("20000.005")
    assert line.line_10 == D("25298.00")
    assert line.line_12 == D("5297.995")
    assert line.result == D("5298.00")
    assert total_line == ItemsTotalLine(
        DISABILITY_TRANSFERRED_AMOUNT, ((1, D("5298.00")),), D("5298.00")
    )


def test_traces_the_maximum_datasets_rounding_rule() -> None:
    wired = capability(
        base=amount("ca-on/disability_transfer_base_amount", "10298.00", NO_ROUNDING),
        maximum=amount("ca-on/disability_transfer_maximum", "16305", DOLLAR_FLOOR),
    )

    (line, _) = wired.compute((dependants((0, "0", "15000", "20000.005")),)).trace

    assert isinstance(line, DisabilityTransferLine)
    assert line.rounding == DOLLAR_FLOOR
    assert line.result == D("5297")


def test_the_last_trace_line_amount_is_the_output() -> None:
    result = capability().compute((dependants(AGED_20, AGED_17),))

    (output,) = result.outputs
    assert result.trace[-1].amount == output.value
    assert [line.amount for line in result.trace[:-1]] == [D("5298.00"), D("14823.00")]


def test_the_total_is_the_sum_of_its_items() -> None:
    *_, total_line = capability().compute((dependants(AGED_20, AGED_17, (0, "0", "0", "0")),)).trace

    assert isinstance(total_line, ItemsTotalLine)
    assert total_line.total == sum((amount for _, amount in total_line.items), D("0"))


def test_compute_is_repeatable() -> None:
    wired = capability()
    given = (dependants(AGED_20, AGED_17),)

    assert wired.compute(given) == wired.compute(given)


# --- trace: English -----------------------------------------------------------------------------
# The English rendering of the reused federal line prints no worksheet line numbers: it names the
# steps ("care expenses ... less threshold ...", "supplement ... less ...", "base ... + ..., at
# most ...", "... + credit amounts ... less taxable income ...", "the lesser of ... and ..."), so
# the federal field names do not show wrongly for the Ontario worksheet. The Ontario figure it
# calls "credit amounts" is line 28 of the dependant's ON428, the total of their Ontario credit
# amounts, which the word describes.


def english(*given: Figures) -> tuple[str, ...]:
    return EnglishTraceRenderer().render_all(capability().compute((dependants(*given),)).trace)


def test_renders_a_dependant_aged_18_or_older_in_english() -> None:
    assert english(AGED_20) == (
        "disability_transferred_amount: dependant 1: 18 or older: base 10298 + 0, at most 16305 = "
        "10298; 10298 + credit amounts 15000 less taxable income 20000 = 5298; "
        "the lesser of 10298 and 5298 = 5298 (half-up to 0.01)",
        "disability_transferred_amount: item 1 5298 = 5298",
    )


def test_renders_a_dependant_under_18_in_english() -> None:
    assert english(AGED_17) == (
        "disability_transferred_amount: dependant 1: under 18: care expenses 5000 less threshold "
        "3518 = 1482; supplement 6007 less 1482 = 4525; base 10298 + 4525, at most 16305 = 14823; "
        "14823 + credit amounts 0 less taxable income 0 = 14823; "
        "the lesser of 14823 and 14823 = 14823 (half-up to 0.01)",
        "disability_transferred_amount: item 1 14823 = 14823",
    )


def test_renders_two_dependants_and_their_total_in_english() -> None:
    lines = english(AGED_20, AGED_17)

    assert len(lines) == 3
    assert lines[0].startswith("disability_transferred_amount: dependant 1: 18 or older: ")
    assert lines[1].startswith("disability_transferred_amount: dependant 2: under 18: ")
    assert lines[2] == "disability_transferred_amount: item 1 5298 + item 2 14823 = 20121"


def test_renders_no_dependants_in_english() -> None:
    assert english() == ("disability_transferred_amount: no items = 0",)


def test_the_english_rendering_has_no_federal_line_numbers() -> None:
    for sentence in english(AGED_20, AGED_17):
        assert "line" not in sentence
