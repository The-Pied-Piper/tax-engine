"""Unit tests for the RecapturedCca capability (`ca/recaptured_cca`), the recapture of Area A.

T776 Area A, "Column 7: UCC after additions and dispositions (column 2 plus column 3 minus
column 5)", and Note 3: "If you have a negative amount in column 7, add it to income as a
recapture under "Recaptured capital cost allowance" on line 9947. ... Recapture and terminal loss
do not apply to a Class 10.1 property unless it is a DIEP." T2125 Note 3 sends it to line 8230.

Its slots: one parameter slot `class_rates` (a `class_rates` dataset), one consumed slot `classes`
(a record list of the Area A rows) and one produced slot `output`. Each class is worked on its
own: its recapture is column 7 made positive when column 7 is negative, and 0 otherwise or for a
class the dataset marks as excluded. A class the dataset does not list, or a row whose columns 11
and 12 are above its column 3, is refused (`InvalidRecordError`). The output is the total of the
recaptures. It records one `RecapturedCcaLine` per class, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import (
    InvalidCapabilityError,
    InvalidRecordError,
    MissingArtifactError,
)
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.parameters.class_rates import CLASS_RATES, ClassRate, ClassRates
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.capabilities.recaptured_cca import RecapturedCca
from tax_engine.jurisdictions.ca.trace import CcaZeroReason, RecapturedCcaLine
from tests.jurisdictions.ca.capabilities.cca_table import (
    CENT,
    CLASS_1,
    CLASS_8,
    CLASS_10,
    CLASS_10_1,
    CLASSES,
    RECAPTURED_CCA,
    WITH_ADDITIONS,
    WITH_RECAPTURE,
    WITH_TERMINAL_LOSS,
    class_rates,
    classes,
    row,
    service,
)

D = Decimal


def capability(dataset: ParameterDataset[ClassRates] | None = None) -> RecapturedCca:
    return RecapturedCca(dataset or class_rates(), CLASSES, RECAPTURED_CCA)


def compute(*rows: dict[Any, Decimal | int]) -> Artifact[Any]:
    (output,) = capability().compute((classes(*rows),)).outputs
    return output


def total(*rows: dict[Any, Decimal | int]) -> Decimal:
    value = compute(*rows).value
    assert isinstance(value, Decimal)
    return value


def recapture(
    position: int,
    class_rate: ClassRate,
    column_7: str,
    result: str,
    zero_reason: CcaZeroReason = CcaZeroReason.NONE,
) -> RecapturedCcaLine:
    return RecapturedCcaLine(
        RECAPTURED_CCA, position, class_rate, D(column_7), zero_reason, D(result)
    )


def test_is_registered_as_ca_recaptured_cca() -> None:
    assert CapabilityRegistry.shared().get("ca/recaptured_cca") is RecapturedCca


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "recaptured_cca" in ca_capabilities.__all__
    assert ca_capabilities.recaptured_cca.RecapturedCca is RecapturedCca


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({CLASSES})
    assert capability().produces == frozenset({RECAPTURED_CCA})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(RecapturedCca)
    assert "produces" not in vars(RecapturedCca)


def test_declares_its_slots() -> None:
    assert RecapturedCca.PARAMETERS == {"class_rates": CLASS_RATES}
    assert RecapturedCca.CONSUMES == {"classes": RecordList}
    assert RecapturedCca.PRODUCES == {"output": Decimal}


def test_its_slots_are_read_only() -> None:
    for each in (RecapturedCca.PARAMETERS, RecapturedCca.CONSUMES, RecapturedCca.PRODUCES):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, each)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(RecapturedCca.PARAMETERS, Mapping[str, ParameterKind[ClassRates]])
    assert_type(RecapturedCca.CONSUMES, Mapping[str, type])
    assert_type(RecapturedCca.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = RecapturedCca(class_rates=class_rates(), classes=CLASSES, output=RECAPTURED_CCA)

    (output,) = wired.compute((classes(WITH_RECAPTURE),)).outputs
    assert output == Artifact(RECAPTURED_CCA, D("3000"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        RecapturedCca(class_rates(), CLASSES, RECAPTURED_CCA, CENT)  # type: ignore[call-arg]


def test_rejects_a_money_kind_for_its_classes() -> None:
    with pytest.raises(InvalidCapabilityError, match="RecapturedCca.*'classes'"):
        RecapturedCca(class_rates(), RECAPTURED_CCA, RECAPTURED_CCA)  # type: ignore[arg-type]


# --- computing ----------------------------------------------------------------------------------


def test_a_class_with_a_disposition_causing_recapture_gives_the_tables_figure() -> None:
    # Column 7: 5,000 - 8,000 = -3,000: a recapture of 3,000.
    assert total(WITH_RECAPTURE) == D("3000")


def test_a_class_with_additions_has_no_recapture() -> None:
    assert total(WITH_ADDITIONS) == D("0")


def test_a_class_closing_with_a_terminal_loss_has_no_recapture() -> None:
    assert total(WITH_TERMINAL_LOSS) == D("0")


def test_a_column_7_of_zero_has_no_recapture() -> None:
    value = total(row("8", "1000", proceeds="1000"))

    assert value == D("0")
    assert not value.is_signed()


def test_a_cent_below_zero_is_a_cent_of_recapture() -> None:
    assert total(row("8", "1000", proceeds="1000.01")) == D("0.01")


def test_additions_in_the_year_count_in_column_7() -> None:
    # Column 7: 1,000 + 500 - 2,000 = -500.
    assert total(row("8", "1000", "500", "2000")) == D("500")


def test_recapture_applies_whether_or_not_property_is_left() -> None:
    assert total(row("8", "1000", proceeds="1500", no_property_left=1)) == D("500")
    assert total(row("8", "1000", proceeds="1500", no_property_left=0)) == D("500")


def test_a_class_excluded_from_recapture_has_none() -> None:
    # Note 3: "Recapture and terminal loss do not apply to a Class 10.1 property unless it is a
    # DIEP."
    value = total(row("10.1", "10000", proceeds="12000"))

    assert value == D("0")
    assert not value.is_signed()


def test_the_recaptures_of_several_classes_are_added() -> None:
    assert total(WITH_RECAPTURE, WITH_ADDITIONS, row("8", "1000", proceeds="1500")) == D("3500")


def test_no_classes_give_zero() -> None:
    output = compute()

    assert output == Artifact(RECAPTURED_CCA, D("0"))
    assert not output.value.is_signed()


def test_the_claim_does_not_change_the_recapture() -> None:
    assert total(row("8", "10000", "3000", claimed="2300")) == D("0")


@pytest.mark.parametrize("number", ["13", "14"])
def test_a_class_the_dataset_does_not_list_is_refused(number: str) -> None:
    with pytest.raises(
        InvalidRecordError, match=f"^item 2: class {number} is not in the class rates"
    ):
        compute(WITH_RECAPTURE, row(number, "1000", proceeds="2000"))


def test_missing_classes_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="cca_classes"):
        capability().compute(())


def test_a_row_whose_columns_11_and_12_are_above_column_3_is_refused() -> None:
    # Columns 11 and 12 are "Cost of remaining additions from column 10".
    with pytest.raises(InvalidRecordError) as raised:
        compute(row("43.1", "0", "100", aiip_additions="60000", riip_additions="40000"))

    assert str(raised.value) == "item 1: columns 11 and 12 (100000) are above column 3 (100)"


# --- trace --------------------------------------------------------------------------------------


def test_traces_one_recapture_line_per_class_then_the_total() -> None:
    excluded = row("10.1", "10000", proceeds="12000")
    trace = (
        capability()
        .compute((classes(WITH_ADDITIONS, WITH_RECAPTURE, WITH_TERMINAL_LOSS, excluded),))
        .trace
    )

    assert trace == (
        recapture(1, CLASS_8, "13000", "0"),
        recapture(2, CLASS_10, "-3000", "3000", CcaZeroReason.COLUMN_7_NEGATIVE),
        recapture(3, CLASS_1, "5000", "0", CcaZeroReason.NO_PROPERTY_LEFT),
        recapture(4, CLASS_10_1, "-2000", "0", CcaZeroReason.COLUMN_7_NEGATIVE),
        ItemsTotalLine(
            RECAPTURED_CCA, ((1, D("0")), (2, D("3000")), (3, D("0")), (4, D("0"))), D("3000")
        ),
    )


def test_traces_no_classes_as_only_an_empty_total() -> None:
    assert capability().compute((classes(),)).trace == (ItemsTotalLine(RECAPTURED_CCA, (), D("0")),)


def test_the_last_trace_line_amount_is_the_output() -> None:
    result = capability().compute((classes(WITH_RECAPTURE, row("8", "1000", proceeds="1500")),))

    (output,) = result.outputs
    assert result.trace[-1].amount == output.value == D("3500")


# --- through TaxComputationService --------------------------------------------------------------


def test_a_computation_gives_the_total_recapture() -> None:
    worksheet = service("ca/recaptured_cca", RECAPTURED_CCA).compute(
        JurisdictionCode("CA-ON"), 2025, classes(WITH_ADDITIONS, WITH_RECAPTURE, WITH_TERMINAL_LOSS)
    )["ca-on/return"][0]

    assert worksheet.get(RECAPTURED_CCA).value == D("3000")
    assert isinstance(worksheet.producer_of(RECAPTURED_CCA), RecapturedCca)
