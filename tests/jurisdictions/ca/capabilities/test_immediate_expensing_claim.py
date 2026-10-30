"""Unit tests for the ImmediateExpensingClaim capability (`ca/immediate_expensing_claim`), line i of
T776 Area A.

T776 Area A "Line i: Total immediate expensing claim for the year: Total of column 9", with Note 5:
"The immediate expensing applies to DIEPs included in column 8. The total immediate expensing
amount for the tax year (total of column 9) is limited to the lesser of: - the immediate expensing
limit ... - the UCC of DIEPs in column 8 - the amount of income, if any, earned from the source of
income that is a property (before any CCA deductions) in which the relevant DIEP is used for the
tax year". Guide T4036 "Column 9 - Immediate expensing amount for DIEPs": "The total immediate
expensing amount must be equal to or less than the least of the following amounts".

Its slots: one parameter slot `class_rates` (a `class_rates` dataset), three consumed slots
`classes` (a record list of the Area A rows with columns 4, 6 and 9), `immediate_expensing_limit`
and `income_before_cca` (money), and one produced slot `output`. Each class is worked as `CcaTable`
works it (column 8 is column 4 less column 6, at most column 7 and at least 0); the output is the
total of column 9, 0 for no classes. A total above the limit, the total of column 8 or the income
(a loss counting as 0) is refused (`InputAboveBoundError`, naming the one that binds). It records
one `ImmediateExpensingLine` per class, then an `ItemsTotalLine`.

Worked rows, Class 8 (see test_cca_table_diep.py): A has column 8 4,000 and column 9 3,000; a Class
12 row with column 3 2,000, column 4 2,000 and column 9 1,500 has column 8 2,000. B has column 8
5,000 and column 9 5,000. Totals: A 3,000; A and the Class 12 row 4,500 of 6,000.
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
    InputAboveBoundError,
    InvalidCapabilityError,
    InvalidRecordError,
    MissingArtifactError,
)
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.parameters.class_rates import CLASS_RATES, ClassRates
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.capabilities.immediate_expensing_claim import (
    ImmediateExpensingClaim,
)
from tax_engine.jurisdictions.ca.trace import ImmediateExpensingLine
from tests.jurisdictions.ca.capabilities.cca_table import (
    CENT,
    CLASS_8,
    CLASS_12,
    CLASSES,
    class_rates,
    classes,
    row,
    service,
)
from tests.jurisdictions.ca.capabilities.cca_table_diep import (
    DIEP_CLASSES,
    IMMEDIATE_EXPENSING,
    INCOME,
    LIMIT,
    diep_classes,
    diep_row,
    money,
)

D = Decimal

# Column 8 4,000, column 9 3,000, claim 3,400 (maximum 400.00 plus column 9).
A_ROW = diep_row(
    "8", "1000", "5000", diep_additions="4000", immediate_expensing="3000", claimed="3400"
)
# Column 8 5,000, column 9 5,000, claim 5,200 (maximum 200.00 plus column 9).
B_ROW = diep_row(
    "8", "1000", "5000", diep_additions="5000", immediate_expensing="5000", claimed="5200"
)
# Class 12 (100%, no half-year rule): column 8 2,000, column 9 1,500, claim 2,000.
TWELVE_ROW = diep_row(
    "12", "0", "2000", diep_additions="2000", immediate_expensing="1500", claimed="2000"
)
MILLIONS = "1500000"


def capability(dataset: ParameterDataset[ClassRates] | None = None) -> ImmediateExpensingClaim:
    return ImmediateExpensingClaim(
        dataset or class_rates(), DIEP_CLASSES, LIMIT, INCOME, IMMEDIATE_EXPENSING
    )


def inputs(
    *rows: dict[Any, Decimal | int], limit: str = MILLIONS, income: str = "100000"
) -> tuple[Artifact[Any], ...]:
    return (diep_classes(*rows), money(LIMIT, limit), money(INCOME, income))


def total(*rows: dict[Any, Decimal | int], limit: str = MILLIONS, income: str = "100000") -> Any:
    (output,) = capability().compute(inputs(*rows, limit=limit, income=income)).outputs
    return output.value


def line(
    position: int,
    class_rate: Any,
    column_4: str,
    column_6: str,
    column_7: str,
    column_8: str,
    column_9: str,
) -> ImmediateExpensingLine:
    return ImmediateExpensingLine(
        IMMEDIATE_EXPENSING,
        position,
        class_rate,
        D(column_4),
        D(column_6),
        D(column_7),
        D(column_8),
        D(column_9),
    )


def test_is_registered_as_ca_immediate_expensing_claim() -> None:
    assert (
        CapabilityRegistry.shared().get("ca/immediate_expensing_claim") is ImmediateExpensingClaim
    )


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "immediate_expensing_claim" in ca_capabilities.__all__
    assert (
        ca_capabilities.immediate_expensing_claim.ImmediateExpensingClaim is ImmediateExpensingClaim
    )


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({DIEP_CLASSES, LIMIT, INCOME})
    assert capability().produces == frozenset({IMMEDIATE_EXPENSING})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(ImmediateExpensingClaim)
    assert "produces" not in vars(ImmediateExpensingClaim)


def test_declares_its_slots() -> None:
    assert ImmediateExpensingClaim.PARAMETERS == {"class_rates": CLASS_RATES}
    assert ImmediateExpensingClaim.CONSUMES == {
        "classes": RecordList,
        "immediate_expensing_limit": Decimal,
        "income_before_cca": Decimal,
    }
    assert ImmediateExpensingClaim.PRODUCES == {"output": Decimal}


def test_its_slots_are_read_only() -> None:
    for each in (
        ImmediateExpensingClaim.PARAMETERS,
        ImmediateExpensingClaim.CONSUMES,
        ImmediateExpensingClaim.PRODUCES,
    ):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, each)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(ImmediateExpensingClaim.PARAMETERS, Mapping[str, ParameterKind[ClassRates]])
    assert_type(ImmediateExpensingClaim.CONSUMES, Mapping[str, type])
    assert_type(ImmediateExpensingClaim.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = ImmediateExpensingClaim(
        class_rates=class_rates(),
        classes=DIEP_CLASSES,
        immediate_expensing_limit=LIMIT,
        income_before_cca=INCOME,
        output=IMMEDIATE_EXPENSING,
    )

    (output,) = wired.compute(inputs(A_ROW)).outputs
    assert output == Artifact(IMMEDIATE_EXPENSING, D("3000"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        ImmediateExpensingClaim(  # type: ignore[call-arg]
            class_rates(), DIEP_CLASSES, LIMIT, INCOME, IMMEDIATE_EXPENSING, CENT
        )


def test_rejects_a_money_kind_for_its_classes() -> None:
    money_kind = cast(Any, IMMEDIATE_EXPENSING)

    with pytest.raises(InvalidCapabilityError, match="ImmediateExpensingClaim.*'classes'"):
        ImmediateExpensingClaim(class_rates(), money_kind, LIMIT, INCOME, IMMEDIATE_EXPENSING)


def test_rejects_a_record_list_kind_for_its_limit() -> None:
    list_kind = cast(Any, DIEP_CLASSES)

    with pytest.raises(
        InvalidCapabilityError, match="ImmediateExpensingClaim.*'immediate_expensing_limit'"
    ):
        ImmediateExpensingClaim(class_rates(), DIEP_CLASSES, list_kind, INCOME, IMMEDIATE_EXPENSING)


# --- computing ----------------------------------------------------------------------------------


def test_a_class_with_a_diep_gives_the_total_of_column_9() -> None:
    assert total(A_ROW) == D("3000")


def test_the_total_of_column_9_of_several_classes_is_added() -> None:
    assert total(A_ROW, TWELVE_ROW) == D("4500")


def test_a_class_with_no_column_9_adds_nothing() -> None:
    assert total(A_ROW, diep_row("8", "10000", "3000", claimed="2300")) == D("3000")


def test_no_classes_give_zero() -> None:
    (output,) = capability().compute(inputs()).outputs

    assert output == Artifact(IMMEDIATE_EXPENSING, D("0"))
    assert not output.value.is_signed()


def test_a_list_kind_without_the_diep_fields_gives_zero() -> None:
    plain = ImmediateExpensingClaim(class_rates(), CLASSES, LIMIT, INCOME, IMMEDIATE_EXPENSING)
    claimed = row("8", "10000", "3000", claimed="2300")

    (output,) = plain.compute(
        (classes(claimed), money(LIMIT, MILLIONS), money(INCOME, "100000"))
    ).outputs

    assert output == Artifact(IMMEDIATE_EXPENSING, D("0"))


def test_the_claim_does_not_change_the_total() -> None:
    assert total(A_ROW) == total(
        diep_row("8", "1000", "5000", diep_additions="4000", immediate_expensing="3000")
    )


# --- the limit, the total of column 8 and the income -----------------------------------------


def test_a_total_equal_to_the_limit_is_allowed() -> None:
    assert total(A_ROW, limit="3000") == D("3000")


def test_a_total_above_the_limit_is_refused_naming_the_limit() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=r"^total of column 9 \(3000\) is above the immediate expensing limit \(2999.99\)",
    ):
        total(A_ROW, limit="2999.99")


def test_a_limit_of_zero_allows_no_immediate_expensing() -> None:
    # An associated EPOP with no agreement gives a limit of 0.
    assert total(diep_row("8", "10000", "3000", claimed="2300"), limit="0") == D("0")
    with pytest.raises(InputAboveBoundError, match=r"immediate expensing limit \(0\)"):
        total(A_ROW, limit="0")


def test_a_total_equal_to_the_income_is_allowed() -> None:
    assert total(A_ROW, income="3000") == D("3000")


def test_a_total_above_the_income_is_refused_naming_the_income() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=r"^total of column 9 \(3000\) is above the income before CCA \(2999.99\)",
    ):
        total(A_ROW, income="2999.99")


def test_an_income_of_zero_allows_no_immediate_expensing() -> None:
    assert total(diep_row("8", "10000", "3000", claimed="2300"), income="0") == D("0")
    assert total(income="0") == D("0")
    with pytest.raises(InputAboveBoundError, match=r"income before CCA \(0\)"):
        total(A_ROW, income="0")


def test_a_loss_allows_no_immediate_expensing() -> None:
    # "the amount of income, if any": a loss is no income.
    with pytest.raises(InputAboveBoundError, match="income before CCA"):
        total(A_ROW, income="-100")
    assert total(diep_row("8", "10000", "3000", claimed="2300"), income="-100") == D("0")


def test_the_limit_binds_when_it_is_below_the_income() -> None:
    with pytest.raises(InputAboveBoundError, match="immediate expensing limit"):
        total(A_ROW, TWELVE_ROW, limit="4000", income="4499")


def test_the_income_binds_when_it_is_below_the_limit() -> None:
    with pytest.raises(InputAboveBoundError, match="income before CCA"):
        total(A_ROW, TWELVE_ROW, limit="4499", income="4000")


def test_the_limit_is_for_the_total_over_all_the_classes() -> None:
    # 3,000 + 1,500 = 4,500: each class is below 4,000 but the total is above it.
    assert total(A_ROW, limit="4500") == D("3000")
    with pytest.raises(InputAboveBoundError, match=r"\(4500\) is above the immediate"):
        total(A_ROW, TWELVE_ROW, limit="4499.99")


def test_a_total_of_all_of_column_8_is_allowed() -> None:
    # Row B: column 8 5,000, column 9 5,000: the UCC of DIEPs (total of column 8) is the least.
    assert total(B_ROW, limit=MILLIONS, income="100000") == D("5000")


def test_column_9_above_column_8_is_refused_by_the_table_before_the_total() -> None:
    # Note 5's "UCC of DIEPs in column 8" is kept class by class: column 8 is 4,000.
    above = diep_row("8", "1000", "5000", diep_additions="4000", immediate_expensing="4001")

    with pytest.raises(InvalidRecordError) as raised:
        total(above)

    assert str(raised.value) == "item 1: column 9 (4001) is above column 8 (4000)"


def test_a_column_8_cut_by_column_7_limits_column_9() -> None:
    # Column 7 3,000 (column 5 2,000), column 4 5,000: column 8 3,000.
    cut = diep_row(
        "8", "0", "5000", "2000", diep_additions="5000", immediate_expensing="3000", claimed="3000"
    )

    assert total(cut) == D("3000")


def test_a_class_the_dataset_does_not_list_is_refused() -> None:
    with pytest.raises(InvalidRecordError, match="^item 2: class 13 is not in the class rates"):
        total(A_ROW, diep_row("13", "1000", "2000", diep_additions="1000"))


def test_missing_inputs_are_missing_artifacts() -> None:
    present = inputs(A_ROW)

    with pytest.raises(MissingArtifactError, match="cca_diep_classes"):
        capability().compute(present[1:])
    with pytest.raises(MissingArtifactError, match="immediate_expensing_limit"):
        capability().compute((present[0], present[2]))
    with pytest.raises(MissingArtifactError, match="income_before_cca"):
        capability().compute(present[:2])


# --- trace --------------------------------------------------------------------------------------


def test_traces_one_line_per_class_then_the_total() -> None:
    assert capability().compute(inputs(A_ROW, TWELVE_ROW)).trace == (
        line(1, CLASS_8, "4000", "0", "6000", "4000", "3000"),
        line(2, CLASS_12, "2000", "0", "2000", "2000", "1500"),
        ItemsTotalLine(IMMEDIATE_EXPENSING, ((1, D("3000")), (2, D("1500"))), D("4500")),
    )


def test_traces_a_column_8_cut_by_column_6_and_column_7() -> None:
    # Column 6 1,500 above column 4 1,000: column 8 0. Column 7 3,000 below column 4 5,000:
    # column 8 3,000.
    over = diep_row(
        "8", "2000", "1000", "1500", diep_additions="1000", diep_proceeds="1500", claimed="300"
    )
    cut = diep_row(
        "8", "0", "5000", "2000", diep_additions="5000", immediate_expensing="3000", claimed="3000"
    )

    assert capability().compute(inputs(over, cut)).trace[:2] == (
        line(1, CLASS_8, "1000", "1500", "1500", "0", "0"),
        line(2, CLASS_8, "5000", "0", "3000", "3000", "3000"),
    )


def test_traces_no_classes_as_only_an_empty_total() -> None:
    assert capability().compute(inputs()).trace == (
        ItemsTotalLine(IMMEDIATE_EXPENSING, (), D("0")),
    )


def test_the_last_trace_line_amount_is_the_output() -> None:
    result = capability().compute(inputs(A_ROW, TWELVE_ROW))

    (output,) = result.outputs
    assert result.trace[-1].amount == output.value == D("4500")


def test_a_line_amount_is_column_9() -> None:
    assert line(1, CLASS_8, "4000", "0", "6000", "4000", "3000").amount == D("3000")


# --- through TaxComputationService --------------------------------------------------------------


def test_a_computation_gives_the_total_immediate_expensing() -> None:
    worksheet = service(
        "ca/immediate_expensing_claim",
        IMMEDIATE_EXPENSING,
        classes_kind=DIEP_CLASSES,
        extra={"immediate_expensing_limit": LIMIT, "income_before_cca": INCOME},
    ).compute(
        JurisdictionCode("CA-ON"),
        2025,
        diep_classes(A_ROW, TWELVE_ROW),
        money(LIMIT, MILLIONS),
        money(INCOME, "100000"),
    )["ca-on/return"][0]

    assert worksheet.get(IMMEDIATE_EXPENSING).value == D("4500")
    assert isinstance(worksheet.producer_of(IMMEDIATE_EXPENSING), ImmediateExpensingClaim)
