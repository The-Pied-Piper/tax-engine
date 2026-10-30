"""Unit tests for the ClosingUccAfterColumn22 capability (`ca/closing_ucc_after_column_22`), the UCC
at the end of the year of T776 Area A with each claim limited by column 22.

T776 Area A "Column 22: Non-compliant amount of CCA (see Chart B below)", "Column 23: CCA claim
for the year (column 21 minus column 22)" and "Column 24: UCC at the end of the year (column 7
minus column 23)": the most a class may claim is its maximum, column 21, less its column 22, never
below 0. It is `ClosingUcc` otherwise (see its tests): the same records and the same trace.

Its slots are those of `ClosingUcc` and one consumed slot `non_compliant` (a record list of the
class number and the column 22 amount, a class it does not list having 0). The claim is refused
above the limit (`InputAboveBoundError`, naming the item), above column 21 as `ClosingUcc` refuses
it.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import (
    InputAboveBoundError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca.capabilities.closing_ucc import ClosingUcc
from tax_engine.jurisdictions.ca.capabilities.closing_ucc_after_column_22 import (
    ClosingUccAfterColumn22,
)
from tax_engine.jurisdictions.ca.catalog import CCA_CLASS_NUMBER, CCA_UCC_AT_END
from tests.jurisdictions.ca.capabilities.cca_table import (
    CCA_CLAIM,
    CLASSES,
    CLOSING_UCC,
    NO_COLUMN_22,
    NON_COMPLIANT,
    WITH_ADDITIONS,
    WITH_RECAPTURE,
    WITH_TERMINAL_LOSS,
    class_rates,
    classes,
    non_compliant_cca,
    row,
    service,
)

D = Decimal


def capability() -> ClosingUccAfterColumn22:
    return ClosingUccAfterColumn22(class_rates(), CLASSES, NON_COMPLIANT, CLOSING_UCC)


def closing(*rows: dict[Any, Decimal | int], column_22: Artifact[Any] = NO_COLUMN_22) -> RecordList:
    (output,) = capability().compute((column_22, classes(*rows))).outputs
    assert output.kind is CLOSING_UCC
    value = output.value
    assert isinstance(value, RecordList)
    return value


def figures(
    column_22: Artifact[Any], *rows: dict[Any, Decimal | int]
) -> list[tuple[Decimal | int, Decimal | int]]:
    return [
        (record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END])
        for record in closing(*rows, column_22=column_22).records
    ]


def test_is_registered_as_ca_closing_ucc_after_column_22() -> None:
    registered = CapabilityRegistry.shared().get("ca/closing_ucc_after_column_22")

    assert registered is ClosingUccAfterColumn22


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "closing_ucc_after_column_22" in ca_capabilities.__all__
    module = ca_capabilities.closing_ucc_after_column_22
    assert module.ClosingUccAfterColumn22 is ClosingUccAfterColumn22


def test_is_a_closing_ucc() -> None:
    assert issubclass(ClosingUccAfterColumn22, ClosingUcc)


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({CLASSES, NON_COMPLIANT})
    assert capability().produces == frozenset({CLOSING_UCC})


def test_declares_its_slots() -> None:
    assert ClosingUccAfterColumn22.CONSUMES == {
        "classes": RecordList,
        "non_compliant": RecordList,
    }
    assert ClosingUccAfterColumn22.PRODUCES == {"output": RecordList}


def test_the_closing_ucc_without_the_column_22_slot_is_unchanged() -> None:
    assert ClosingUcc.CONSUMES == {"classes": RecordList}


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = ClosingUccAfterColumn22(
        class_rates=class_rates(),
        classes=CLASSES,
        non_compliant=NON_COMPLIANT,
        output=CLOSING_UCC,
    )

    (output,) = wired.compute((NO_COLUMN_22, classes(WITH_ADDITIONS))).outputs
    assert output == Artifact(
        CLOSING_UCC,
        RecordList(CLOSING_UCC.fields, [{CCA_CLASS_NUMBER: D("8"), CCA_UCC_AT_END: D("10700")}]),
    )


def test_rejects_a_money_kind_for_its_non_compliant_list() -> None:
    with pytest.raises(InvalidCapabilityError, match="ClosingUccAfterColumn22.*'non_compliant'"):
        ClosingUccAfterColumn22(class_rates(), CLASSES, CCA_CLAIM, CLOSING_UCC)  # type: ignore[arg-type]


def test_missing_non_compliant_list_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="non_compliant_cca"):
        capability().compute((classes(WITH_ADDITIONS),))


def test_missing_classes_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="cca_classes"):
        capability().compute((NO_COLUMN_22,))


# --- computing: column 22 limits the claim -------------------------------------------------------


def test_with_no_column_22_it_gives_the_records_and_trace_of_the_closing_ucc() -> None:
    rows = (WITH_ADDITIONS, WITH_RECAPTURE, WITH_TERMINAL_LOSS)
    plain = ClosingUcc(class_rates(), CLASSES, CLOSING_UCC)

    assert capability().compute((NO_COLUMN_22, classes(*rows))) == plain.compute((classes(*rows),))


def test_a_claim_above_the_maximum_is_refused_as_the_closing_ucc_refuses_it() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        closing(row("8", "10000", "3000", claimed="2300.01"))

    assert str(raised.value) == "item 1: ca/cca_claimed 2300.01 is above the maximum 2300.00"


def test_a_claim_of_the_maximum_less_column_22_is_taken_off_column_7() -> None:
    # Class 8: column 7 13,000, maximum 2,300.00 less a column 22 of 300 = 2,000: column 24 is
    # 13,000 - 2,000 = 11,000.
    column_22 = non_compliant_cca(("8", "300"))

    assert figures(column_22, row("8", "10000", "3000", claimed="2000")) == [(D("8"), D("11000"))]


def test_a_claim_above_the_maximum_less_column_22_is_refused() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        closing(
            row("8", "10000", "3000", claimed="2000.01"),
            column_22=non_compliant_cca(("8", "300")),
        )

    assert str(raised.value) == (
        "item 1: ca/cca_claimed 2000.01 is above the maximum 2000.00 (2300.00 less column 22 300)"
    )


def test_a_class_not_in_the_column_22_list_keeps_its_maximum() -> None:
    column_22 = non_compliant_cca(("1", "500"))

    assert figures(column_22, row("8", "10000", "3000", claimed="2300"), row("1", "0", "0")) == [
        (D("8"), D("10700")),
        (D("1"), D("0")),
    ]


def test_a_column_22_above_the_maximum_allows_no_claim() -> None:
    column_22 = non_compliant_cca(("8", "2400"))

    assert figures(column_22, row("8", "10000", "3000")) == [(D("8"), D("13000"))]
    with pytest.raises(InputAboveBoundError, match=r"ca/cca_claimed 1 is above the maximum 0 "):
        closing(row("8", "10000", "3000", claimed="1"), column_22=column_22)


def test_each_class_is_limited_by_its_own_column_22() -> None:
    column_22 = non_compliant_cca(("8", "300"))

    with pytest.raises(InputAboveBoundError, match=r"^item 2: "):
        closing(
            row("1", "10000", claimed="400"),
            row("8", "10000", "3000", claimed="2001"),
            column_22=column_22,
        )


# --- computing through the service ---------------------------------------------------------------


def test_a_computation_gives_the_closing_list() -> None:
    worksheet = service("ca/closing_ucc_after_column_22", CLOSING_UCC, checks_claim=True).compute(
        JurisdictionCode("CA-ON"),
        2025,
        classes(row("8", "10000", "3000", claimed="2000")),
        non_compliant_cca(("8", "300")),
    )["ca-on/return"][0]

    value = worksheet.get(CLOSING_UCC).value
    assert isinstance(value, RecordList)
    assert [r[CCA_UCC_AT_END] for r in value.records] == [D("11000")]
