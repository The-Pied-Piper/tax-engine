"""Unit tests for the CcaClaimAfterColumn22 capability (`ca/cca_claim_after_column_22`), the total
CCA claim of T776 Area A with each claim limited by column 22.

T776 Area A "Column 22: Non-compliant amount of CCA (see Chart B below)" and "Column 23: CCA claim
for the year (column 21 minus column 22)": the most a class may claim is its maximum, column 21,
less its column 22, never below 0. It is `CcaClaim` otherwise (see its tests): the same total and
the same trace.

Its slots are those of `CcaClaim` and one consumed slot `non_compliant` (a record list of the class
number and the column 22 amount, a class it does not list having 0). The claim is refused above the
limit (`InputAboveBoundError`, naming the item), above column 21 as `CcaClaim` refuses it.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_calculator.jurisdictions.ca.capabilities as ca_capabilities
from tax_calculator.domain.artifact import Artifact
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import (
    InputAboveBoundError,
    InvalidCapabilityError,
    InvalidRecordError,
    MissingArtifactError,
)
from tax_calculator.domain.jurisdiction_code import JurisdictionCode
from tax_calculator.domain.record_list import RecordList
from tax_calculator.jurisdictions.ca.capabilities.cca_claim import CcaClaim
from tax_calculator.jurisdictions.ca.capabilities.cca_claim_after_column_22 import (
    CcaClaimAfterColumn22,
)
from tax_calculator.jurisdictions.ca.catalog import CCA_CLAIMED
from tax_calculator.jurisdictions.ca.trace import CcaClaimLine
from tests.jurisdictions.ca.capabilities.cca_table import (
    CCA_CLAIM,
    CLASSES,
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


def capability() -> CcaClaimAfterColumn22:
    return CcaClaimAfterColumn22(class_rates(), CLASSES, NON_COMPLIANT, CCA_CLAIM)


def compute(
    *rows: dict[Any, Decimal | int], column_22: Artifact[Any] = NO_COLUMN_22
) -> Artifact[Any]:
    (output,) = capability().compute((column_22, classes(*rows))).outputs
    return output


def total(*rows: dict[Any, Decimal | int], column_22: Artifact[Any] = NO_COLUMN_22) -> Decimal:
    value = compute(*rows, column_22=column_22).value
    assert isinstance(value, Decimal)
    return value


def test_is_registered_as_ca_cca_claim_after_column_22() -> None:
    registered = CapabilityRegistry.shared().get("ca/cca_claim_after_column_22")

    assert registered is CcaClaimAfterColumn22


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "cca_claim_after_column_22" in ca_capabilities.__all__
    module = ca_capabilities.cca_claim_after_column_22
    assert module.CcaClaimAfterColumn22 is CcaClaimAfterColumn22


def test_is_a_cca_claim() -> None:
    assert issubclass(CcaClaimAfterColumn22, CcaClaim)


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({CLASSES, NON_COMPLIANT})
    assert capability().produces == frozenset({CCA_CLAIM})


def test_declares_its_slots() -> None:
    assert CcaClaimAfterColumn22.CONSUMES == {"classes": RecordList, "non_compliant": RecordList}
    assert CcaClaimAfterColumn22.PRODUCES == {"output": Decimal}
    assert not CcaClaimAfterColumn22.is_list_slot("non_compliant")


def test_the_claim_without_the_column_22_slot_is_unchanged() -> None:
    assert CcaClaim.CONSUMES == {"classes": RecordList}


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = CcaClaimAfterColumn22(
        class_rates=class_rates(), classes=CLASSES, non_compliant=NON_COMPLIANT, output=CCA_CLAIM
    )

    (output,) = wired.compute((NO_COLUMN_22, classes(WITH_ADDITIONS))).outputs
    assert output == Artifact(CCA_CLAIM, D("2300.00"))


def test_rejects_a_money_kind_for_its_non_compliant_list() -> None:
    with pytest.raises(InvalidCapabilityError, match="CcaClaimAfterColumn22.*'non_compliant'"):
        CcaClaimAfterColumn22(class_rates(), CLASSES, CCA_CLAIM, CCA_CLAIM)  # type: ignore[arg-type]


def test_missing_non_compliant_list_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="non_compliant_cca"):
        capability().compute((classes(WITH_ADDITIONS),))


def test_missing_classes_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="cca_classes"):
        capability().compute((NO_COLUMN_22,))


# --- computing: column 22 limits the claim -------------------------------------------------------
# WITH_ADDITIONS is Class 8 with a maximum of 2,300.00.


def test_with_no_column_22_it_gives_the_total_and_trace_of_the_cca_claim() -> None:
    given = (NO_COLUMN_22, classes(WITH_ADDITIONS, WITH_RECAPTURE, WITH_TERMINAL_LOSS))
    plain = CcaClaim(class_rates(), CLASSES, CCA_CLAIM)

    assert capability().compute(given) == plain.compute((classes(*given[1].value.records),))


def test_a_claim_of_the_maximum_less_column_22_is_allowed() -> None:
    column_22 = non_compliant_cca(("8", "300.50"))

    assert total(row("8", "10000", "3000", claimed="1999.50"), column_22=column_22) == D("1999.50")


def test_a_claim_above_the_maximum_less_column_22_is_refused() -> None:
    column_22 = non_compliant_cca(("8", "300.50"))

    with pytest.raises(InputAboveBoundError) as raised:
        compute(row("8", "10000", "3000", claimed="1999.51"), column_22=column_22)

    assert str(raised.value) == (
        f"item 1: {CCA_CLAIMED.identifier} 1999.51 is above the maximum 1999.50 "
        "(2300.00 less column 22 300.50)"
    )


def test_a_claim_above_the_maximum_is_refused_as_the_cca_claim_refuses_it() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        compute(row("8", "10000", "3000", claimed="2300.01"))

    assert str(raised.value) == "item 1: ca/cca_claimed 2300.01 is above the maximum 2300.00"


def test_the_refusal_message_names_column_22_when_it_is_not_zero() -> None:
    with pytest.raises(InputAboveBoundError, match=r"^item 1: .*less column 22 1\)$"):
        compute(row("8", "10000", "3000", claimed="2300"), column_22=non_compliant_cca(("8", "1")))


def test_the_refusal_message_does_not_name_column_22_when_it_is_zero() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        compute(
            row("8", "10000", "3000", claimed="2300.01"),
            row("1", "0", "0"),
            column_22=non_compliant_cca(("1", "9")),
        )

    assert "column 22" not in str(raised.value)


def test_a_class_not_in_the_column_22_list_has_a_column_22_of_zero() -> None:
    column_22 = non_compliant_cca(("1", "500"))

    assert total(
        row("8", "10000", "3000", claimed="2300"), row("1", "0", "0"), column_22=column_22
    ) == D("2300.00")


def test_a_column_22_of_zero_leaves_the_limit_at_the_maximum() -> None:
    column_22 = non_compliant_cca(("8", "0"))

    assert total(row("8", "10000", "3000", claimed="2300"), column_22=column_22) == D("2300.00")


def test_a_column_22_above_the_maximum_limits_the_claim_to_zero() -> None:
    column_22 = non_compliant_cca(("8", "2300.01"))

    assert total(row("8", "10000", "3000", claimed="0"), column_22=column_22) == D("0")
    with pytest.raises(InputAboveBoundError, match=r"ca/cca_claimed 0.01 is above the maximum 0 "):
        compute(row("8", "10000", "3000", claimed="0.01"), column_22=column_22)


def test_each_class_is_limited_by_its_own_column_22() -> None:
    # Class 8: 2,300.00 - 300 = 2,000; Class 1: 4% of 10,000 = 400.00 - 100 = 300.
    column_22 = non_compliant_cca(("8", "300"), ("1", "100"))

    assert total(
        row("8", "10000", "3000", claimed="2000"),
        row("1", "10000", claimed="300"),
        column_22=column_22,
    ) == D("2300.00")
    with pytest.raises(InputAboveBoundError, match=r"^item 2: ca/cca_claimed 301 is above"):
        compute(
            row("8", "10000", "3000", claimed="2000"),
            row("1", "10000", claimed="301"),
            column_22=column_22,
        )


def test_column_22_of_a_class_applies_to_each_row_of_that_class() -> None:
    column_22 = non_compliant_cca(("8", "300"))

    with pytest.raises(InputAboveBoundError, match=r"^item 2: "):
        compute(
            row("8", "10000", "3000", claimed="2000"),
            row("8", "10000", "3000", claimed="2001"),
            column_22=column_22,
        )


def test_a_decimal_class_number_in_the_column_22_list_finds_its_class() -> None:
    # Class 10.1: 30% of 1,000 = 300.00 - 10 = 290.
    column_22 = non_compliant_cca(("10.1", "10"))

    assert total(row("10.1", "1000", claimed="290"), column_22=column_22) == D("290")
    with pytest.raises(InputAboveBoundError, match=r"ca/cca_claimed 291 is above"):
        compute(row("10.1", "1000", claimed="291"), column_22=column_22)


def test_column_22_does_not_change_the_maximum_in_the_trace() -> None:
    # Column 21 is the maximum; the trace line holds it as without a column 22.
    column_22 = non_compliant_cca(("8", "300"))

    line, _total = (
        capability().compute((column_22, classes(row("8", "10000", "3000", claimed="2000")))).trace
    )

    assert isinstance(line, CcaClaimLine)
    assert line.maximum == D("2300.00")
    assert line.claim == D("2000")


def test_a_row_with_a_zero_maximum_and_a_column_22_still_refuses_any_claim() -> None:
    with pytest.raises(InputAboveBoundError, match=r"ca/cca_claimed 1 is above the maximum 0"):
        compute(
            row("10", "5000", proceeds="8000", claimed="1"),
            column_22=non_compliant_cca(("10", "5")),
        )


# --- computing through the service ---------------------------------------------------------------


def test_a_computation_builds_the_capability_from_the_registry_and_its_dataset() -> None:
    composition = (
        service("ca/cca_claim_after_column_22", CCA_CLAIM, checks_claim=True)
        .compose(JurisdictionCode("CA-ON"), 2025)
        .form("ca-on/return")
        .composition
    )

    (built,) = composition.order
    assert isinstance(built, CcaClaimAfterColumn22)
    assert built.consumes == frozenset({CLASSES, NON_COMPLIANT})


def test_a_computation_gives_the_total_claim() -> None:
    worksheet = service("ca/cca_claim_after_column_22", CCA_CLAIM, checks_claim=True).compute(
        JurisdictionCode("CA-ON"),
        2025,
        classes(WITH_ADDITIONS, WITH_RECAPTURE, WITH_TERMINAL_LOSS),
        NO_COLUMN_22,
    )["ca-on/return"][0]

    assert worksheet.get(CCA_CLAIM).value == D("2300.00")


def test_a_computation_refuses_a_claim_above_the_maximum_less_column_22() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=r"^ca-on/return, instance 1: item 1: ca/cca_claimed 2300 is above",
    ):
        service("ca/cca_claim_after_column_22", CCA_CLAIM, checks_claim=True).compute(
            JurisdictionCode("CA-ON"),
            2025,
            classes(WITH_ADDITIONS),
            non_compliant_cca(("8", "0.01")),
        )


# --- a Chart B class with no Area A row -----------------------------------------------------------
# Form T776 Chart B "*** For each class, add the amounts from column 7 of Chart B and enter each
# total in column 22 of Area A, in the respective row.": a class of Chart B with no row of Area A
# has no row to enter its total in, so it is refused (`InvalidRecordError`, naming its class), not
# dropped. Area A here is Class 8 alone (`WITH_ADDITIONS`).


def test_a_column_22_class_with_no_area_a_row_is_refused_naming_its_class() -> None:
    with pytest.raises(InvalidRecordError, match=r"^Chart B class 5 has no row in Area A$"):
        capability().compute((non_compliant_cca(("5", "100")), classes(WITH_ADDITIONS)))


def test_a_column_22_class_with_no_area_a_row_is_refused_even_at_0() -> None:
    with pytest.raises(InvalidRecordError, match=r"^Chart B class 5 has no row in Area A$"):
        capability().compute((non_compliant_cca(("5", "0")), classes(WITH_ADDITIONS)))


def test_a_column_22_class_with_an_area_a_row_is_not_refused() -> None:
    # Class 8 with column 22 of 300.50 may claim 2,300 less 300.50: 1,999.50 is allowed.
    claim = row("8", "10000", "3000", claimed="1999.50")

    (output,) = capability().compute((non_compliant_cca(("8", "300.50")), classes(claim))).outputs

    assert output == Artifact(CCA_CLAIM, D("1999.50"))


def test_no_column_22_list_means_no_class_is_checked_against_area_a() -> None:
    plain = CcaClaim(class_rates(), CLASSES, CCA_CLAIM)

    assert plain.compute((classes(WITH_ADDITIONS),)).outputs == (Artifact(CCA_CLAIM, D("2300.00")),)
