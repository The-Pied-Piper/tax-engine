"""Unit tests for the ClosingUcc capability (`ca/closing_ucc`), the UCC at the end of the year.

T776 Area A, "Column 24: UCC at the end of the year (column 7 minus column 23)" (T2125 column
22, column 7 minus column 21), and T4036 "Column 7": "You cannot claim CCA when the amount in
column 7 is: negative ... positive and you do not have any property left in that class ... In
either case, enter "0" in column 24". Decided on the ticket: produced per class, as a record list
for next year.

Its slots: one parameter slot `class_rates` (a `class_rates` dataset), one consumed slot `classes`
(a record list of the Area A rows) and one produced slot `output`, a record list kind of exactly
the class number and the UCC at the end of the year. Each class gives one record, in the caller's
order: its class number and column 7 less its claim, or 0 when column 7 is negative or is
positive with no property left. The claim is refused above the class's maximum
(`InputAboveBoundError`), as `ca/cca_claim` refuses it; a class the dataset does not list, or a
row whose columns 11 and 12 are above its column 3, is refused (`InvalidRecordError`). It records
one `ClosingUccLine` per class, which names why column 24 is 0 when it is, and no total.
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
from tax_engine.domain.errors import (
    InputAboveBoundError,
    InvalidCapabilityError,
    InvalidRecordError,
    MissingArtifactError,
)
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.parameters.class_rates import CLASS_RATES, ClassRate, ClassRates
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.jurisdictions.ca.capabilities.closing_ucc import ClosingUcc
from tax_engine.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    CCA_UCC_AT_START,
)
from tax_engine.jurisdictions.ca.trace import CcaZeroReason, ClosingUccLine
from tests.jurisdictions.ca.capabilities.cca_table import (
    CCA_CLAIM,
    CENT,
    CLASS_1,
    CLASS_8,
    CLASS_10,
    CLASS_10_1,
    CLASS_43_1,
    CLASSES,
    CLOSING_UCC,
    WITH_ADDITIONS,
    WITH_RECAPTURE,
    WITH_TERMINAL_LOSS,
    class_rates,
    classes,
    row,
    service,
)

D = Decimal


def capability(dataset: ParameterDataset[ClassRates] | None = None) -> ClosingUcc:
    return ClosingUcc(dataset or class_rates(), CLASSES, CLOSING_UCC)


def closing(*rows: dict[Any, Decimal | int]) -> RecordList:
    (output,) = capability().compute((classes(*rows),)).outputs
    assert output.kind is CLOSING_UCC
    value = output.value
    assert isinstance(value, RecordList)
    return value


def figures(*rows: dict[Any, Decimal | int]) -> list[tuple[Decimal | int, Decimal | int]]:
    return [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in closing(*rows).records]


def ucc_line(
    position: int,
    class_rate: ClassRate,
    no_property_left: int,
    column_7: str,
    claim: str,
    result: str,
    zero_reason: CcaZeroReason = CcaZeroReason.NONE,
) -> ClosingUccLine:
    return ClosingUccLine(
        CLOSING_UCC,
        position,
        class_rate,
        no_property_left,
        D(column_7),
        zero_reason,
        D(claim),
        D(result),
    )


def test_is_registered_as_ca_closing_ucc() -> None:
    assert CapabilityRegistry.shared().get("ca/closing_ucc") is ClosingUcc


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "closing_ucc" in ca_capabilities.__all__
    assert ca_capabilities.closing_ucc.ClosingUcc is ClosingUcc


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({CLASSES})
    assert capability().produces == frozenset({CLOSING_UCC})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(ClosingUcc)
    assert "produces" not in vars(ClosingUcc)


def test_declares_its_slots() -> None:
    assert ClosingUcc.PARAMETERS == {"class_rates": CLASS_RATES}
    assert ClosingUcc.CONSUMES == {"classes": RecordList}
    assert ClosingUcc.PRODUCES == {"output": RecordList}


def test_its_slots_are_read_only() -> None:
    for each in (ClosingUcc.PARAMETERS, ClosingUcc.CONSUMES, ClosingUcc.PRODUCES):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, each)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(ClosingUcc.PARAMETERS, Mapping[str, ParameterKind[ClassRates]])
    assert_type(ClosingUcc.CONSUMES, Mapping[str, type])
    assert_type(ClosingUcc.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = ClosingUcc(class_rates=class_rates(), classes=CLASSES, output=CLOSING_UCC)

    (output,) = wired.compute((classes(WITH_ADDITIONS),)).outputs
    assert output == Artifact(
        CLOSING_UCC,
        RecordList(CLOSING_UCC.fields, [{CCA_CLASS_NUMBER: D("8"), CCA_UCC_AT_END: D("10700")}]),
    )


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        ClosingUcc(class_rates(), CLASSES, CLOSING_UCC, CENT)  # type: ignore[call-arg]


def test_rejects_a_money_kind_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="ClosingUcc.*'output'"):
        ClosingUcc(class_rates(), CLASSES, CCA_CLAIM)  # type: ignore[arg-type]


def test_an_output_list_of_other_fields_fails_when_its_artifact_is_built() -> None:
    # The record-list kind refuses a list of other fields; the capability adds no check of its own.
    other = RecordListKind("ex/other_closing_ucc", fields=(CCA_CLASS_NUMBER, CCA_UCC_AT_START))
    wired = ClosingUcc(class_rates(), CLASSES, other)

    with pytest.raises(TypeError, match="ex/other_closing_ucc must be a record list of fields"):
        wired.compute((classes(WITH_ADDITIONS),))


def test_its_output_holds_the_class_number_and_the_ucc_at_the_end_of_the_year() -> None:
    assert closing(WITH_ADDITIONS).fields == (CCA_CLASS_NUMBER, CCA_UCC_AT_END)


# --- computing: the acceptance rows -------------------------------------------------------------


def test_a_class_with_additions_gives_column_7_less_the_claim() -> None:
    # Column 7: 13,000; claimed 2,300 of a maximum of 2,300.00: column 24 is 10,700.
    assert figures(WITH_ADDITIONS) == [(D("8"), D("10700"))]


def test_a_class_with_a_disposition_causing_recapture_closes_at_zero() -> None:
    assert figures(WITH_RECAPTURE) == [(D("10"), D("0"))]


def test_a_class_closing_with_a_terminal_loss_closes_at_zero() -> None:
    assert figures(WITH_TERMINAL_LOSS) == [(D("1"), D("0"))]


def test_each_class_gives_one_record_in_the_callers_order() -> None:
    assert figures(WITH_TERMINAL_LOSS, WITH_ADDITIONS, WITH_RECAPTURE) == [
        (D("1"), D("0")),
        (D("8"), D("10700")),
        (D("10"), D("0")),
    ]


def test_no_classes_give_an_empty_list() -> None:
    held = closing()

    assert held.records == ()
    assert held.fields == CLOSING_UCC.fields


# --- computing: the claim -----------------------------------------------------------------------


def test_no_claim_leaves_column_7() -> None:
    assert figures(row("8", "10000", "3000")) == [(D("8"), D("13000"))]


def test_a_claim_below_the_maximum_is_taken_off_as_claimed() -> None:
    assert figures(row("8", "10000", "3000", claimed="1000.50")) == [(D("8"), D("11999.50"))]


def test_a_claim_above_the_maximum_is_refused() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        closing(row("8", "10000", "3000", claimed="2300.01"))

    assert str(raised.value) == "item 1: ca/cca_claimed 2300.01 is above the maximum 2300.00"


def test_a_claim_on_a_class_closing_at_zero_is_refused() -> None:
    with pytest.raises(
        InputAboveBoundError, match=r"^item 2: ca/cca_claimed 1 is above the maximum 0"
    ):
        closing(WITH_ADDITIONS, row("10", "5000", proceeds="8000", claimed="1"))


def test_the_claim_comes_off_column_7_not_column_19() -> None:
    # Class 43.1: column 7 is 5,600, column 19 6,500 and the maximum 1,950.00: 5,600 - 1,950.
    aiip = row("43.1", "5000", "1000", "400", aiip_additions="1000", claimed="1950")

    assert figures(aiip) == [(D("43.1"), D("3650"))]


def test_a_class_with_no_property_left_and_a_column_7_of_zero_closes_at_zero() -> None:
    assert figures(row("1", "1000", proceeds="1000", no_property_left=1)) == [(D("1"), D("0"))]


def test_a_class_excluded_from_recapture_still_closes_at_zero() -> None:
    # T4036 "Column 7": a negative column 7 or a positive one with no property left: "enter "0" in
    # column 24", whether or not Note 3 gives a recapture or a terminal loss.
    assert figures(row("10.1", "10000", proceeds="12000")) == [(D("10.1"), D("0"))]
    assert figures(row("10.1", "10000", proceeds="4000", no_property_left=1)) == [
        (D("10.1"), D("0"))
    ]


def test_the_class_number_is_kept_as_given() -> None:
    (record,) = closing(row("10.1", "20000", claimed="6000")).records

    assert str(record[CCA_CLASS_NUMBER]) == "10.1"
    assert record[CCA_UCC_AT_END] == D("14000")


@pytest.mark.parametrize("number", ["13", "14"])
def test_a_class_the_dataset_does_not_list_is_refused(number: str) -> None:
    with pytest.raises(
        InvalidRecordError, match=f"^item 1: class {number} is not in the class rates"
    ):
        closing(row(number, "1000"))


def test_missing_classes_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="cca_classes"):
        capability().compute(())


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(ArtifactKind("ex/other_amount", Decimal), D("9"))

    (output,) = capability().compute((other, classes(WITH_ADDITIONS))).outputs

    assert output.kind is CLOSING_UCC


# --- refused rows and signed zeros -------------------------------------------------------------


def test_a_row_whose_columns_11_and_12_are_above_column_3_is_refused() -> None:
    # Columns 11 and 12 are "Cost of remaining additions from column 10".
    with pytest.raises(InvalidRecordError) as raised:
        closing(row("43.1", "0", "100", aiip_additions="60000", riip_additions="40000"))

    assert str(raised.value) == "item 1: columns 11 and 12 (100000) are above column 3 (100)"


def test_a_claim_of_minus_zero_is_traced_and_taken_off_as_plain_zero() -> None:
    result = capability().compute((classes(row("8", "10000", "3000", claimed="-0")),))

    (line,) = result.trace
    assert isinstance(line, ClosingUccLine)
    assert line.claim == D("0")
    assert not line.claim.is_signed()
    (record,) = result.outputs[0].value.records
    assert record[CCA_UCC_AT_END] == D("13000")
    assert not record[CCA_UCC_AT_END].is_signed()


# --- trace --------------------------------------------------------------------------------------


def test_traces_one_line_per_class_and_no_total() -> None:
    aiip = row("43.1", "5000", "1000", "400", aiip_additions="1000", claimed="1950")
    trace = (
        capability()
        .compute((classes(WITH_ADDITIONS, WITH_RECAPTURE, WITH_TERMINAL_LOSS, aiip),))
        .trace
    )

    assert trace == (
        ucc_line(1, CLASS_8, 0, "13000", "2300", "10700"),
        ucc_line(2, CLASS_10, 0, "-3000", "0", "0", CcaZeroReason.COLUMN_7_NEGATIVE),
        ucc_line(3, CLASS_1, 1, "5000", "0", "0", CcaZeroReason.NO_PROPERTY_LEFT),
        ucc_line(4, CLASS_43_1, 0, "5600", "1950", "3650"),
    )


def test_traces_an_excluded_class_closing_at_zero() -> None:
    (line,) = capability().compute((classes(row("10.1", "10000", proceeds="12000")),)).trace

    assert line == ucc_line(1, CLASS_10_1, 0, "-2000", "0", "0", CcaZeroReason.COLUMN_7_NEGATIVE)


def test_traces_no_reason_for_a_class_with_no_property_left_and_a_column_7_of_zero() -> None:
    (line,) = (
        capability()
        .compute((classes(row("1", "1000", proceeds="1000", no_property_left=1)),))
        .trace
    )

    assert line == ucc_line(1, CLASS_1, 1, "0", "0", "0")


def test_traces_no_classes_as_no_lines() -> None:
    assert capability().compute((classes(),)).trace == ()


def test_each_trace_lines_amount_is_its_records_ucc_at_the_end_of_the_year() -> None:
    result = capability().compute((classes(WITH_ADDITIONS, WITH_TERMINAL_LOSS),))

    (output,) = result.outputs
    assert [line.amount for line in result.trace] == [
        record[CCA_UCC_AT_END] for record in output.value.records
    ]


# --- through TaxComputationService --------------------------------------------------------------


def test_a_computation_gives_the_closing_list() -> None:
    worksheet = service("ca/closing_ucc", CLOSING_UCC).compute(
        JurisdictionCode("CA-ON"), 2025, classes(WITH_ADDITIONS, WITH_RECAPTURE, WITH_TERMINAL_LOSS)
    )["ca-on/return"][0]

    value = worksheet.get(CLOSING_UCC).value
    assert [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in value.records] == [
        (D("8"), D("10700")),
        (D("10"), D("0")),
        (D("1"), D("0")),
    ]
    assert isinstance(worksheet.producer_of(CLOSING_UCC), ClosingUcc)


# --- a no-property-left flag above 1 -------------------------------------------------------------


@pytest.mark.parametrize("value", [2, 13])
def test_a_no_property_left_flag_above_1_is_refused(value: int) -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=rf"^item 1: ca/cca_no_property_left {value} is above a yes or no answer of 1$",
    ):
        capability().compute(
            (classes(row("1", "20000", proceeds="15000", no_property_left=value)),)
        )


@pytest.mark.parametrize("value", [2, 13])
def test_a_no_property_left_flag_above_1_names_its_item_at_position_2(value: int) -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=rf"^item 2: ca/cca_no_property_left {value} is above a yes or no answer of 1$",
    ):
        capability().compute(
            (classes(WITH_ADDITIONS, row("1", "20000", proceeds="15000", no_property_left=value)),)
        )
