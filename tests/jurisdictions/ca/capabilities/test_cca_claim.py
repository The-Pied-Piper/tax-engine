"""Unit tests for the CcaClaim capability (`ca/cca_claim`), the total CCA claim of Area A.

T776 Area A, one row per class: "Column 7: UCC after additions and dispositions (column 2 plus
column 3 minus column 5)"; "Column 14: Proceeds of dispositions available to reduce additions of
AIIPs, RIIPs, and ZEVs (column 5 minus column 10 plus column 11 plus column 12). If negative,
enter "0""; "Column 15: UCC adjustment for current-year additions of AIIPs and ZEVs acquired
before 2025 (column 11 minus column 14) multiplied by the relevant factor. If negative, enter
"0" (Note 7)"; "Column 16: Proceeds of dispositions available to reduce additions of RIIPs and
ZEVs acquired after 2024 (column 14 minus column 11).If negative, enter "0""; "Column 17: UCC
adjustment for current-year additions of RIIPs and ZEVs acquired after 2024 (column 12 minus
column 16) multiplied by the relevant factor. If negative, enter "0" (Note 8)"; "Column 18:
Adjustment for current-year additions subject to the half-year rule. one half multiplied by
(column 10 minus column 11 minus column 12 minus column 5). If negative, enter "0""; "Column 19:
Base amount for CCA (column 13 plus column 15 plus column 17 minus column 18)"; "Column 21:
Available CCA for the year (column 19 multiplied by column 20, or a lower amount, plus column 9)";
"Column 23: CCA claim for the year"; "Line ii: Total CCA claim for the year *: Total of column
23". T2125 has the same columns, its column 21 the claim. Columns 4, 6, 8 and 9 (DIEPs) are taken
as 0, so column 10 is column 3 and column 13 is column 7; T776 column 22 joins with Chart B.

Its slots: one parameter slot `class_rates` (a `class_rates` dataset), one consumed slot `classes`
(a record list of the Area A rows) and one produced slot `output`. Each class is worked on its
own: its rate, factors and half-year rule come from the dataset, columns 15, 17 and 18 and the
maximum are rounded once each with the dataset's rule (every form column rounds half up to the
cent), and column 18 is 0 for a class exempt from the
half-year rule. The maximum is 0 when column 7 is negative or is positive with no property left
in the class (T4036 "Column 7": "You cannot claim CCA when the amount in column 7 is: negative
... positive and you do not have any property left in that class"). The claim is the caller's,
refused above the maximum (`InputAboveBoundError`); a class the dataset does not list is refused
(`InvalidRecordError`), as is a row whose columns 11 and 12 are above its column 3 ("Cost of
remaining additions from column 10"). The output is the total of the claims. It records one
`CcaClaimLine` per class, which names why the maximum is 0 when it is, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.jurisdictions.ca.capabilities as ca_capabilities
from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.artifact import Artifact
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import (
    InputAboveBoundError,
    InvalidCapabilityError,
    InvalidRecordError,
    MissingArtifactError,
)
from tax_calculator.domain.jurisdiction_code import JurisdictionCode
from tax_calculator.domain.parameters.class_rates import CLASS_RATES, ClassRate, ClassRates
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.capabilities.cca_claim import CcaClaim
from tax_calculator.jurisdictions.ca.catalog import CCA_CLAIMED
from tax_calculator.jurisdictions.ca.trace import CcaClaimLine, CcaZeroReason
from tests.jurisdictions.ca.capabilities.cca_table import (
    CCA_CLAIM,
    CENT,
    CLASS_1,
    CLASS_8,
    CLASS_10,
    CLASS_10_1,
    CLASS_43_1,
    CLASSES,
    WITH_ADDITIONS,
    WITH_RECAPTURE,
    WITH_TERMINAL_LOSS,
    class_rates,
    classes,
    row,
    service,
)

D = Decimal


def capability(dataset: ParameterDataset[ClassRates] | None = None) -> CcaClaim:
    return CcaClaim(dataset or class_rates(), CLASSES, CCA_CLAIM)


def compute(
    *rows: dict[Any, Decimal | int], dataset: ParameterDataset[ClassRates] | None = None
) -> Artifact[Any]:
    (output,) = capability(dataset).compute((classes(*rows),)).outputs
    return output


def total(
    *rows: dict[Any, Decimal | int], dataset: ParameterDataset[ClassRates] | None = None
) -> Decimal:
    value = compute(*rows, dataset=dataset).value
    assert isinstance(value, Decimal)
    return value


def claim_line(
    position: int,
    class_rate: ClassRate,
    columns: tuple[str, str, str, str, str, str, str],
    maximum: str,
    claim: str,
    no_property_left: int = 0,
    rounding: RoundingRule = CENT,
    zero_reason: CcaZeroReason = CcaZeroReason.NONE,
) -> CcaClaimLine:
    column_7, column_14, column_15, column_16, column_17, column_18, column_19 = columns
    return CcaClaimLine(
        output=CCA_CLAIM,
        position=position,
        class_rate=class_rate,
        no_property_left=no_property_left,
        column_7=D(column_7),
        column_14=D(column_14),
        column_15=D(column_15),
        column_16=D(column_16),
        column_17=D(column_17),
        column_18=D(column_18),
        column_19=D(column_19),
        zero_reason=zero_reason,
        maximum=D(maximum),
        rounding=rounding,
        claim=D(claim),
    )


def only_line(
    *rows: dict[Any, Decimal | int], dataset: ParameterDataset[ClassRates] | None = None
) -> CcaClaimLine:
    line, _total = capability(dataset).compute((classes(*rows),)).trace
    assert isinstance(line, CcaClaimLine)
    return line


def test_is_registered_as_ca_cca_claim() -> None:
    assert CapabilityRegistry.shared().get("ca/cca_claim") is CcaClaim


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert ca_capabilities.NAMESPACE == "ca"
    assert "cca_claim" in ca_capabilities.__all__
    assert ca_capabilities.cca_claim.CcaClaim is CcaClaim


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({CLASSES})
    assert capability().produces == frozenset({CCA_CLAIM})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(CcaClaim)
    assert "produces" not in vars(CcaClaim)


def test_declares_its_slots() -> None:
    assert CcaClaim.PARAMETERS == {"class_rates": CLASS_RATES}
    assert CcaClaim.CONSUMES == {"classes": RecordList}
    assert CcaClaim.PRODUCES == {"output": Decimal}
    assert not CcaClaim.is_list_slot("classes")


def test_its_slots_are_read_only() -> None:
    for each in (CcaClaim.PARAMETERS, CcaClaim.CONSUMES, CcaClaim.PRODUCES):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, each)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(CcaClaim.PARAMETERS, Mapping[str, ParameterKind[ClassRates]])
    assert_type(CcaClaim.CONSUMES, Mapping[str, type])
    assert_type(CcaClaim.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = CcaClaim(class_rates=class_rates(), classes=CLASSES, output=CCA_CLAIM)

    (output,) = wired.compute((classes(WITH_ADDITIONS),)).outputs
    assert output == Artifact(CCA_CLAIM, D("2300.00"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        CcaClaim(class_rates(), CLASSES, CCA_CLAIM, CENT)  # type: ignore[call-arg]


def test_rejects_a_money_kind_for_its_classes() -> None:
    with pytest.raises(InvalidCapabilityError, match="CcaClaim.*'classes'"):
        CcaClaim(class_rates(), CCA_CLAIM, CCA_CLAIM)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(CcaClaim, "__type_params__", ())
    assert not getattr(CcaClaim, "__parameters__", ())


# --- computing: the acceptance rows -------------------------------------------------------------


def test_a_class_with_additions_gives_the_tables_figures() -> None:
    # Column 7: 10,000 + 3,000 = 13,000; column 18: one half of 3,000 = 1,500; column 19:
    # 13,000 - 1,500 = 11,500; the maximum: 20% of 11,500 = 2,300.00, all claimed.
    assert only_line(WITH_ADDITIONS) == claim_line(
        1, CLASS_8, ("13000", "0", "0", "0", "0", "1500", "11500"), "2300.00", "2300"
    )
    assert total(WITH_ADDITIONS) == D("2300.00")


def test_a_class_with_a_disposition_causing_recapture_claims_nothing() -> None:
    # Column 7: 5,000 - 8,000 = -3,000, negative: no CCA can be claimed.
    assert only_line(WITH_RECAPTURE) == claim_line(
        1,
        CLASS_10,
        ("-3000", "8000", "0", "8000", "0", "0", "-3000"),
        "0",
        "0",
        zero_reason=CcaZeroReason.COLUMN_7_NEGATIVE,
    )
    assert total(WITH_RECAPTURE) == D("0")


def test_a_class_closing_with_a_terminal_loss_claims_nothing() -> None:
    # Column 7: 20,000 - 15,000 = 5,000, positive with no property left: no CCA can be claimed.
    assert only_line(WITH_TERMINAL_LOSS) == claim_line(
        1,
        CLASS_1,
        ("5000", "15000", "0", "15000", "0", "0", "5000"),
        "0",
        "0",
        no_property_left=1,
        zero_reason=CcaZeroReason.NO_PROPERTY_LEFT,
    )
    assert total(WITH_TERMINAL_LOSS) == D("0")


def test_the_three_rows_together_give_the_total_of_their_claims() -> None:
    assert total(WITH_ADDITIONS, WITH_RECAPTURE, WITH_TERMINAL_LOSS) == D("2300.00")


# --- computing: how many classes ----------------------------------------------------------------


def test_no_classes_give_zero() -> None:
    output = compute()

    assert output == Artifact(CCA_CLAIM, D("0"))
    assert type(output.value) is Decimal
    assert not output.value.is_signed()


def test_two_classes_give_the_sum_of_their_claims() -> None:
    # Class 8: 2,300 claimed; Class 43.1: 1,950 claimed of a maximum of 1,950.
    aiip = row("43.1", "5000", "1000", "400", aiip_additions="1000", claimed="1950")

    assert total(WITH_ADDITIONS, aiip) == D("4250.00")


def test_the_total_does_not_depend_on_the_order() -> None:
    aiip = row("43.1", "5000", "1000", "400", aiip_additions="1000", claimed="1950")

    assert total(aiip, WITH_ADDITIONS) == total(WITH_ADDITIONS, aiip)


def test_two_rows_of_one_class_are_worked_on_apart() -> None:
    # Each row is its own Area A row, as the caller entered it.
    assert total(WITH_ADDITIONS, WITH_ADDITIONS) == D("4600.00")


# --- computing: the claim is an election --------------------------------------------------------


def test_the_claim_may_be_less_than_the_maximum() -> None:
    # T4036: "You can claim any amount you like, from zero to the maximum allowed for the year."
    assert total(row("8", "10000", "3000", claimed="1000")) == D("1000")


def test_the_claim_may_be_zero() -> None:
    assert total(row("8", "10000", "3000")) == D("0")


def test_a_claim_of_exactly_the_maximum_is_allowed() -> None:
    assert total(row("8", "10000", "3000", claimed="2300.00")) == D("2300.00")


def test_a_claim_above_the_maximum_is_refused() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        compute(row("8", "10000", "3000", claimed="2300.01"))

    assert str(raised.value) == (
        f"item 1: {CCA_CLAIMED.identifier} 2300.01 is above the maximum 2300.00"
    )


def test_a_claim_above_the_maximum_names_its_item() -> None:
    with pytest.raises(InputAboveBoundError, match=r"^item 2: ca/cca_claimed 2400 is above"):
        compute(WITH_ADDITIONS, row("8", "10000", "3000", claimed="2400"))


def test_a_claim_on_a_class_with_a_negative_column_7_is_refused() -> None:
    with pytest.raises(
        InputAboveBoundError, match=r"^item 1: ca/cca_claimed 1 is above the maximum 0"
    ):
        compute(row("10", "5000", proceeds="8000", claimed="1"))


def test_a_claim_on_a_class_with_no_property_left_is_refused() -> None:
    with pytest.raises(
        InputAboveBoundError, match=r"^item 1: ca/cca_claimed 100 is above the maximum 0"
    ):
        compute(row("1", "20000", proceeds="15000", claimed="100", no_property_left=1))


def test_a_class_with_no_property_left_and_a_column_7_of_zero_keeps_its_rate() -> None:
    # Column 7 is 0, not positive: Note 3 gives no terminal loss, and the maximum is the rate's,
    # which is 0.
    line = only_line(row("1", "1000", proceeds="1000", no_property_left=1))

    assert line.maximum == D("0")
    assert line.claim == D("0")
    assert line.zero_reason is CcaZeroReason.NONE


@pytest.mark.parametrize("value", [2, 13])
def test_a_no_property_left_flag_above_1_is_refused_with_a_claim_of_0(value: int) -> None:
    # Column 7 is 5,000 and the claim 0: read as 1 this would be the terminal loss, not a refusal.
    with pytest.raises(
        InputAboveBoundError,
        match=rf"^item 1: ca/cca_no_property_left {value} is above a yes or no answer of 1$",
    ):
        compute(row("1", "20000", proceeds="15000", no_property_left=value))


@pytest.mark.parametrize("value", [2, 13])
def test_a_no_property_left_flag_above_1_names_its_item_at_position_2(value: int) -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=rf"^item 2: ca/cca_no_property_left {value} is above a yes or no answer of 1$",
    ):
        compute(WITH_ADDITIONS, row("1", "20000", proceeds="15000", no_property_left=value))


def test_property_left_in_a_class_with_a_positive_column_7_keeps_its_maximum() -> None:
    line = only_line(row("1", "20000", proceeds="15000", claimed="200"))

    # Column 19 is column 7, 5,000: 4% of it is 200.00.
    assert line.maximum == D("200.00")
    assert total(row("1", "20000", proceeds="15000", claimed="200")) == D("200")


# --- computing: the columns ---------------------------------------------------------------------


def test_proceeds_reduce_the_half_year_adjustment() -> None:
    # Column 18: one half of (3,000 - 1,000) = 1,000; column 19: 12,000 - 1,000 = 11,000.
    line = only_line(row("8", "10000", "3000", "1000", claimed="2200"))

    assert line == claim_line(
        1, CLASS_8, ("12000", "0", "0", "0", "0", "1000", "11000"), "2200.00", "2200"
    )


def test_proceeds_above_the_additions_give_no_half_year_adjustment() -> None:
    # Column 18: one half of (1,000 - 3,000) is negative, so 0.
    line = only_line(row("8", "10000", "1000", "3000"))

    assert line.column_18 == D("0")
    assert line.column_19 == D("8000")
    assert line.maximum == D("1600.00")


def test_a_class_exempt_from_the_half_year_rule_has_no_column_18() -> None:
    # Class 12: column 18 is 0, so 100% of 500.
    line = only_line(row("12", "0", "500", claimed="500"))

    assert line.column_18 == D("0")
    assert line.maximum == D("500.00")


def test_the_same_additions_in_a_class_the_rule_applies_to_are_halved() -> None:
    # Class 8: column 18 is one half of 500, 250; column 19 is 250, the maximum 20% of it.
    line = only_line(row("8", "0", "500"))

    assert line.column_18 == D("250")
    assert line.maximum == D("50.00")


def test_aiip_additions_take_the_classs_note_7_factor() -> None:
    # Class 43.1: column 14: 400 - 1,000 + 1,000 = 400; column 15: (1,000 - 400) x 3/2 = 900;
    # column 18: one half of (1,000 - 1,000 - 400) is negative, so 0; column 19: 5,600 + 900.
    line = only_line(row("43.1", "5000", "1000", "400", aiip_additions="1000", claimed="1950"))

    assert line == claim_line(
        1, CLASS_43_1, ("5600", "400", "900.00", "0", "0", "0", "6500.00"), "1950.00", "1950"
    )


def test_aiip_additions_in_a_class_note_7_does_not_list_take_a_factor_of_0() -> None:
    # Class 8: column 15 is 1,000 x 0; column 18 leaves out the AIIPs, so column 19 is 1,000.
    line = only_line(row("8", "0", "1000", aiip_additions="1000"))

    assert line.column_15 == D("0")
    assert line.column_18 == D("0")
    assert line.column_19 == D("1000")
    assert line.maximum == D("200.00")


def test_aiip_additions_in_class_53_take_one_half() -> None:
    # Column 15: 1,000 x 1/2 = 500; column 19: 1,500; 50% of it is 750.
    line = only_line(row("53", "0", "1000", aiip_additions="1000"))

    assert line.column_15 == D("500")
    assert line.maximum == D("750.00")


def test_riip_additions_take_the_classs_note_8_factor() -> None:
    # Class 43.1: column 17: 10,000 x 7/3 = 23,333.33 (to the cent); column 19: 33,333.33; the
    # maximum: 30% of it, 9,999.999, is 10,000.00.
    line = only_line(row("43.1", "0", "10000", riip_additions="10000", claimed="10000"))

    assert line == claim_line(
        1, CLASS_43_1, ("10000", "0", "0", "0", "23333.33", "0", "33333.33"), "10000.00", "10000"
    )


def test_riip_additions_in_a_class_note_8_does_not_list_take_one_half() -> None:
    # Class 8: column 17: 1,000 x 1/2 = 500; column 19: 1,500; 20% of it is 300.
    line = only_line(row("8", "0", "1000", riip_additions="1000"))

    assert line.column_17 == D("500")
    assert line.maximum == D("300.00")


def test_riip_additions_in_class_12_take_a_factor_of_0() -> None:
    line = only_line(row("12", "0", "1000", riip_additions="1000"))

    assert line.column_17 == D("0")
    assert line.maximum == D("1000.00")


def test_a_factor_of_9_over_11_is_rounded_once_to_the_cent() -> None:
    # Class 50: column 17: 1,000 x 9/11 = 818.1818..., 818.18; column 19: 1,818.18; the maximum:
    # 55% of it, 999.999, is 1,000.00.
    line = only_line(row("50", "0", "1000", riip_additions="1000"))

    assert line.column_17 == D("818.18")
    assert line.column_19 == D("1818.18")
    assert line.maximum == D("1000.00")


def test_column_17_is_rounded_half_up_to_the_cent() -> None:
    # Class 55: 1,000.01 x 3/2 = 1,500.015, half up 1,500.02; column 19: 2,500.03; the maximum:
    # 40% of it, 1,000.012, is 1,000.01.
    line = only_line(row("55", "0", "1000.01", riip_additions="1000.01"))

    assert line.column_17 == D("1500.02")
    assert line.column_19 == D("2500.03")
    assert line.maximum == D("1000.01")


def test_proceeds_go_to_the_aiip_additions_first_and_the_rest_to_the_riip_additions() -> None:
    # Class 43.1: column 14: 1,500 - 2,000 + 1,000 + 1,000 = 1,500; column 15: (1,000 - 1,500)
    # is negative, so 0; column 16: 1,500 - 1,000 = 500; column 17: (1,000 - 500) x 7/3 =
    # 1,166.666..., 1,166.67; column 19: 500 + 1,166.67; the maximum: 30% of 1,666.67, 500.001,
    # is 500.00.
    line = only_line(row("43.1", "0", "2000", "1500", "1000", "1000", claimed="500"))

    assert line == claim_line(
        1, CLASS_43_1, ("500", "1500", "0", "500", "1166.67", "0", "1666.67"), "500.00", "500"
    )


def test_column_18_is_rounded_half_up_to_the_cent() -> None:
    # Column 18: one half of 100.01 = 50.005, half up 50.01; column 19: 100.01 - 50.01 = 50.00;
    # the maximum: 20% of it, 10.00.
    line = only_line(row("8", "0", "100.01"))

    assert line.column_18 == D("50.01")
    assert line.column_19 == D("50.00")
    assert line.maximum == D("10.00")


def test_column_18_is_rounded_with_the_datasets_rule() -> None:
    # Floored to the cent instead: 50.00; column 19: 50.01; the maximum: 20% of it, 10.002,
    # floored to 10.00.
    dataset = class_rates(rounding=RoundTo(D("0.01"), RoundingMode.FLOOR))

    line = only_line(row("8", "0", "100.01"), dataset=dataset)

    assert line.column_18 == D("50.00")
    assert line.column_19 == D("50.01")


def test_a_decimal_class_number_finds_its_class() -> None:
    line = only_line(row("10.1", "20000", claimed="6000"))

    assert line.class_rate == CLASS_10_1
    assert line.maximum == D("6000.00")


# --- computing: rounding ------------------------------------------------------------------------


def test_the_rounding_rule_comes_from_the_dataset() -> None:
    dataset = class_rates(rounding=RoundTo(D("1"), RoundingMode.FLOOR))

    # Class 50: column 17 floors 818.18... to 818; the maximum: 55% of 1,818, 999.90, floors to
    # 999.
    line = only_line(row("50", "0", "1000", riip_additions="1000"), dataset=dataset)

    assert line.column_17 == D("818")
    assert line.maximum == D("999")
    assert line.rounding == RoundTo(D("1"), RoundingMode.FLOOR)


def test_no_rounding_keeps_a_terminating_maximum_exact() -> None:
    line = only_line(row("8", "0", "100.01"), dataset=class_rates(rounding=NO_ROUNDING))

    assert line.maximum == D("10.001")
    assert line.rounding == NO_ROUNDING


def test_a_rounded_maximum_carries_the_increments_scale() -> None:
    assert str(only_line(WITH_ADDITIONS).maximum) == "2300.00"


# --- computing: the class rates -----------------------------------------------------------------


@pytest.mark.parametrize("number", ["13", "14", "2"])
def test_a_class_the_dataset_does_not_list_is_refused(number: str) -> None:
    with pytest.raises(
        InvalidRecordError, match=f"^item 1: class {number} is not in the class rates"
    ):
        compute(row(number, "1000"))


def test_a_class_the_dataset_does_not_list_names_its_item() -> None:
    with pytest.raises(InvalidRecordError, match="^item 2: class 13 is not in the class rates"):
        compute(WITH_ADDITIONS, row("13", "1000"))


def test_a_different_years_rate_changes_the_maximum() -> None:
    other = ClassRate(
        D("8"),
        Rate(D("0.10")),
        CLASS_8.half_year_rule,
        CLASS_8.recapture_and_terminal_loss,
        CLASS_8.aiip_factor,
        CLASS_8.riip_factor,
        CLASS_8.half_year_rule_on_sale,
    )

    line = only_line(row("8", "10000", "3000"), dataset=class_rates(classes=(other,)))

    assert line.maximum == D("1150.00")


# --- computing: inputs --------------------------------------------------------------------------


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(CCA_CLAIM, D("9"))

    result = capability().compute((other, classes(WITH_ADDITIONS)))

    assert result.outputs == (Artifact(CCA_CLAIM, D("2300.00")),)


def test_missing_classes_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="cca_classes"):
        capability().compute(())


def test_has_one_output() -> None:
    assert len(capability().compute((classes(WITH_ADDITIONS, WITH_RECAPTURE),)).outputs) == 1


# --- refused rows and signed zeros -------------------------------------------------------------


def test_a_row_whose_columns_11_and_12_are_above_column_3_is_refused() -> None:
    # Columns 11 and 12 are "Cost of remaining additions from column 10": 60,000 + 40,000 of a
    # column 3 of 100 would inflate columns 15, 17 and the maximum.
    with pytest.raises(InvalidRecordError) as raised:
        compute(row("43.1", "0", "100", aiip_additions="60000", riip_additions="40000"))

    assert str(raised.value) == "item 1: columns 11 and 12 (100000) are above column 3 (100)"


def test_a_row_whose_columns_11_and_12_are_above_column_3_names_its_item() -> None:
    with pytest.raises(
        InvalidRecordError,
        match=r"^item 2: columns 11 and 12 \(1000.01\) are above column 3 \(1000\)$",
    ):
        compute(WITH_ADDITIONS, row("8", "0", "1000", aiip_additions="1000.01"))


def test_columns_11_and_12_may_together_equal_column_3() -> None:
    line = only_line(row("43.1", "0", "2000", aiip_additions="1000", riip_additions="1000"))

    assert line.column_18 == D("0")


def test_a_claim_of_minus_zero_is_traced_and_totalled_as_plain_zero() -> None:
    result = capability().compute((classes(row("8", "10000", "3000", claimed="-0")),))

    line, total_line = result.trace
    assert isinstance(line, CcaClaimLine)
    assert isinstance(total_line, ItemsTotalLine)
    assert not line.claim.is_signed()
    assert [not amount.is_signed() for _position, amount in total_line.items] == [True]
    assert not total_line.total.is_signed()
    (output,) = result.outputs
    assert not output.value.is_signed()


def test_a_claim_of_minus_zero_renders_as_zero() -> None:
    trace = capability().compute((classes(row("8", "10000", "3000", claimed="-0")),)).trace

    claim_text, total_text = EnglishTraceRenderer().render_all(trace)

    assert claim_text.endswith(", claim 0")
    assert total_text == "cca_claim: item 1 0 = 0"


# --- trace --------------------------------------------------------------------------------------


def test_traces_one_claim_line_per_class_then_the_total() -> None:
    trace = (
        capability().compute((classes(WITH_ADDITIONS, WITH_RECAPTURE, WITH_TERMINAL_LOSS),)).trace
    )

    assert trace == (
        claim_line(1, CLASS_8, ("13000", "0", "0", "0", "0", "1500", "11500"), "2300.00", "2300"),
        claim_line(
            2,
            CLASS_10,
            ("-3000", "8000", "0", "8000", "0", "0", "-3000"),
            "0",
            "0",
            zero_reason=CcaZeroReason.COLUMN_7_NEGATIVE,
        ),
        claim_line(
            3,
            CLASS_1,
            ("5000", "15000", "0", "15000", "0", "0", "5000"),
            "0",
            "0",
            no_property_left=1,
            zero_reason=CcaZeroReason.NO_PROPERTY_LEFT,
        ),
        ItemsTotalLine(CCA_CLAIM, ((1, D("2300")), (2, D("0")), (3, D("0"))), D("2300.00")),
    )


def test_traces_no_classes_as_only_an_empty_total() -> None:
    assert capability().compute((classes(),)).trace == (ItemsTotalLine(CCA_CLAIM, (), D("0")),)


def test_the_last_trace_line_amount_is_the_output() -> None:
    result = capability().compute((classes(WITH_ADDITIONS, row("8", "0", "500", claimed="50")),))

    (output,) = result.outputs
    assert result.trace[-1].amount == output.value
    assert [line.amount for line in result.trace[:-1]] == [D("2300"), D("50")]


def test_compute_is_repeatable() -> None:
    wired = capability()
    given = (classes(WITH_ADDITIONS, WITH_RECAPTURE),)

    assert wired.compute(given) == wired.compute(given)


# --- through TaxComputationService --------------------------------------------------------------


def test_a_computation_builds_the_capability_from_the_registry_and_its_dataset() -> None:
    composition = (
        service("ca/cca_claim", CCA_CLAIM)
        .compose(JurisdictionCode("CA-ON"), 2025)
        .form("ca-on/return")
        .composition
    )

    (built,) = composition.order
    assert isinstance(built, CcaClaim)
    assert built.consumes == frozenset({CLASSES})
    assert built.produces == frozenset({CCA_CLAIM})


def test_a_computation_gives_the_total_claim() -> None:
    worksheet = service("ca/cca_claim", CCA_CLAIM).compute(
        JurisdictionCode("CA-ON"), 2025, classes(WITH_ADDITIONS, WITH_RECAPTURE, WITH_TERMINAL_LOSS)
    )["ca-on/return"][0]

    assert worksheet.get(CCA_CLAIM).value == D("2300.00")
    assert isinstance(worksheet.producer_of(CCA_CLAIM), CcaClaim)
