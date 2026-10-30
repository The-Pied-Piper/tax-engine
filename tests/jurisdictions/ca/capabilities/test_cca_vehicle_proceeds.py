"""Unit tests for the CcaVehicleProceeds capability (`ca/cca_vehicle_proceeds`), the adjustment of
the proceeds of disposition of a Class 10.1 passenger vehicle designated for immediate expensing,
and of the zero-emission passenger vehicles sold from a Class 54 row.

Form T2125 (2025), Area A endnote 2 (the T776's Column 5 Note 2, and the T2042's and T2121's
endnote 2, say the same): "The proceeds of disposition of a zero-emission passenger vehicle
(ZEPV) that has been included in Class 54, or a passenger vehicle bought after April 18, 2021,
that has been included in Class 10.1, and whose cost is more than the prescribed amount will be
adjusted based on a factor equal to its prescribed amount as a proportion of the actual cost of
the vehicle. For dispositions after July 29, 2019, you will have to adjust the actual cost of the
vehicle for any payments or repayments of government assistance that you may have received or
repaid for the vehicle. If the passenger vehicle in Class 10.1 is not designated for immediate
expensing treatment, this special rule does not apply." Guide T4002 2025, "Class 10.1 (30%)": the
prescribed amounts are $30,000 (acquired before 2022), $34,000 (2022), $36,000 (2023), $37,000
(2024) and $38,000 (2025), each "plus the GST/HST or PST".

Guide T4036 2025, "Class 54 (30%)": "There is a limit of $61,000 (plus federal and provincial
sales taxes) on the capital cost for each zero-emission passenger vehicle in Class 54. Class 54 may
include both zero-emission passenger vehicles that do and do not exceed the prescribed threshold.
However, unlike Class 10.1, Class 54 does not establish a separate class for each vehicle whose
cost exceeds the threshold." and "If a zero-emission passenger vehicle is disposed of to a person
or partnership with whom you deal at arm's length, and its cost exceeds the prescribed amount
($55,000 for vehicles acquired after March 18, 2019, and before January 1, 2022; $59,000 for
vehicles acquired after December 31, 2021, and before January 1, 2023; or $61,000 for vehicles
acquired after December 31, 2022), the proceeds of disposition will be adjusted based on a factor
equal to the prescribed amount as a proportion of the actual cost of the vehicle." Its example:
"$30,000 × ($61,000 ÷ $65,000) = $28,154" (to the dollar; the capability rounds with its dataset).

A Class 54 row holds the list `ca/cca_sold_zepvs` of its sold vehicles, each with the year it was
acquired (0 when the rule does not apply to it), its cost, the government assistance for it, its
proceeds and the DIEP part of them. The list may be non-empty only on a Class 54 row, else the row
is refused (`InvalidRecordError`, naming the item and the vehicle: "item 2 vehicle 1"). Each
vehicle of a year is scaled on its own, with the `zepv_prescribed_amounts` dataset (a year before
its oldest row is refused) and the same rule as a Class 10.1 vehicle, the prescribed amount with
tax (the year's amount plus the rate), the actual cost (the cost less the assistance), the exact
factor and the one rounding with that dataset's rule; a vehicle of year 0 is copied as entered.
Column 5 of the row is the sum of the proceeds of its vehicles, scaled; column 6 likewise. An
amount entered in either column of a Class 54 row is refused. A Class 54 row does not use the
scalar vehicle fields of Class 10.1 (a year on it is refused as before). Each vehicle gives a
`CcaZepvProceedsLine` after the row's own `CcaVehicleProceedsLine`, which is as for a row of year 0.

Its slots: two parameter slots, `prescribed_amounts` (a `year_amounts` dataset with the amount
`prescribed_amount`) and `zepv_prescribed_amounts` (the same, for Class 54), two consumed slots,
`classes` (a record list of the Area A rows) and `sales_tax_rate` (the caller's GST or HST rate,
in percent), and one produced slot `output`, a record list kind of the Area A fields without the
four of the adjustment. Each row has the year
the vehicle was acquired (0 when the rule does not apply to the row, which the caller decides), its
actual cost and the government assistance received less repaid. A row of year 0 is copied as it
is. For a year, the class must be 10.1 and the year 2021 or later (a vehicle bought after April
18, 2021; a later year than the dataset's newest row uses that row), else the row is refused
(`InvalidRecordError`, naming the item). The prescribed amount with tax is the year's amount plus
that amount times the rate, rounded; the actual cost is the cost less the assistance; when the
actual cost is more than the prescribed amount with tax, columns 5 and 6 each become the exact
product of the column and the prescribed amount with tax over the actual cost, rounded once with
the dataset's rule; otherwise they are unchanged. It records one `CcaVehicleProceedsLine` per row
and no total.
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
    InvalidCapabilityError,
    InvalidRecordError,
    MissingArtifactError,
)
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.year_amounts import YEAR_AMOUNTS
from tax_engine.domain.record_list import Record, RecordList, RecordListKind
from tax_engine.jurisdictions.ca.capabilities.cca_vehicle_proceeds import CcaVehicleProceeds
from tax_engine.jurisdictions.ca.catalog import (
    CCA_ADDITIONS,
    CCA_AIIP_ADDITIONS,
    CCA_CLAIMED,
    CCA_CLASS_NUMBER,
    CCA_DIEP_ADDITIONS,
    CCA_DIEP_PROCEEDS,
    CCA_HALF_YEAR_RULE_DIFFERS,
    CCA_IMMEDIATE_EXPENSING,
    CCA_NO_PROPERTY_LEFT,
    CCA_PERSONAL_PART_REMAINING,
    CCA_PROCEEDS,
    CCA_RATE_ELECTION,
    CCA_RIIP_ADDITIONS,
    CCA_UCC_AT_START,
)
from tax_engine.jurisdictions.ca.trace import CcaVehicleProceedsLine, CcaZepvProceedsLine
from tests.jurisdictions.ca.capabilities.cca_vehicle_proceeds import (
    ADJUSTED,
    CENT,
    CLASSES,
    DOLLAR,
    SALES_TAX_RATE,
    SOLD,
    VEHICLE_FIELDS,
    CcaRow,
    capability,
    classes,
    prescribed_amounts,
    row,
    sales_tax_rate,
    service,
    trace_line,
    zepv,
    zepv_line,
    zepv_prescribed_amounts,
)

D = Decimal


def adjusted(
    *rows: CcaRow,
    rate: str = "13",
    dataset: ParameterDataset[Any] | None = None,
    zepv_dataset: ParameterDataset[Any] | None = None,
) -> RecordList:
    (output,) = (
        capability(dataset, zepv_dataset).compute((classes(*rows), sales_tax_rate(rate))).outputs
    )
    assert output.kind is ADJUSTED
    value = output.value
    assert isinstance(value, RecordList)
    return value


def proceeds(
    *rows: CcaRow,
    rate: str = "13",
    dataset: ParameterDataset[Any] | None = None,
    zepv_dataset: ParameterDataset[Any] | None = None,
) -> list[tuple[Decimal, Decimal]]:
    """Columns 5 and 6 of each adjusted record."""
    return [
        (record[CCA_PROCEEDS], record[CCA_DIEP_PROCEEDS])
        for record in adjusted(*rows, rate=rate, dataset=dataset, zepv_dataset=zepv_dataset).records
    ]


def only(
    year: int,
    cost: str,
    proceeds_: str,
    diep_proceeds: str = "0",
    assistance: str = "0",
) -> CcaRow:
    """A Class 10.1 row sold for `proceeds_`, `diep_proceeds` of it a DIEP's."""
    return row(
        proceeds=proceeds_,
        diep_proceeds=diep_proceeds,
        year=year,
        cost=cost,
        assistance=assistance,
    )


def test_is_registered_as_ca_cca_vehicle_proceeds() -> None:
    assert CapabilityRegistry.shared().get("ca/cca_vehicle_proceeds") is CcaVehicleProceeds


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "cca_vehicle_proceeds" in ca_capabilities.__all__
    assert ca_capabilities.cca_vehicle_proceeds.CcaVehicleProceeds is CcaVehicleProceeds


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({CLASSES, SALES_TAX_RATE})
    assert capability().produces == frozenset({ADJUSTED})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(CcaVehicleProceeds)
    assert "produces" not in vars(CcaVehicleProceeds)


def test_declares_its_slots() -> None:
    assert CcaVehicleProceeds.PARAMETERS == {
        "prescribed_amounts": YEAR_AMOUNTS,
        "zepv_prescribed_amounts": YEAR_AMOUNTS,
    }
    assert list(CcaVehicleProceeds.PARAMETERS) == ["prescribed_amounts", "zepv_prescribed_amounts"]
    assert CcaVehicleProceeds.CONSUMES == {"classes": RecordList, "sales_tax_rate": Decimal}
    assert list(CcaVehicleProceeds.CONSUMES) == ["classes", "sales_tax_rate"]
    assert CcaVehicleProceeds.PRODUCES == {"output": RecordList}


def test_its_slots_are_read_only() -> None:
    for each in (
        CcaVehicleProceeds.PARAMETERS,
        CcaVehicleProceeds.CONSUMES,
        CcaVehicleProceeds.PRODUCES,
    ):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, each)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(CcaVehicleProceeds.PARAMETERS, Mapping[str, ParameterKind[Any]])
    assert_type(CcaVehicleProceeds.CONSUMES, Mapping[str, type])
    assert_type(CcaVehicleProceeds.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = CcaVehicleProceeds(
        prescribed_amounts=prescribed_amounts(),
        zepv_prescribed_amounts=zepv_prescribed_amounts(),
        classes=CLASSES,
        sales_tax_rate=SALES_TAX_RATE,
        output=ADJUSTED,
    )

    (output,) = wired.compute((classes(SOLD), sales_tax_rate())).outputs
    assert output.kind is ADJUSTED
    assert [(r[CCA_PROCEEDS], r[CCA_DIEP_PROCEEDS]) for r in output.value.records] == [
        (D("30400.00"), D("30400.00"))
    ]


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        CcaVehicleProceeds(  # type: ignore[call-arg]
            prescribed_amounts(), zepv_prescribed_amounts(), CLASSES, SALES_TAX_RATE, ADJUSTED, CENT
        )


def test_rejects_a_money_kind_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="CcaVehicleProceeds.*'output'"):
        CcaVehicleProceeds(
            prescribed_amounts(),
            zepv_prescribed_amounts(),
            CLASSES,
            SALES_TAX_RATE,
            ArtifactKind("ex/other_amount", Decimal),  # type: ignore[arg-type]
        )


def test_needs_the_zepv_prescribed_amounts() -> None:
    with pytest.raises(TypeError):
        CcaVehicleProceeds(  # type: ignore[call-arg]
            prescribed_amounts=prescribed_amounts(),
            classes=CLASSES,
            sales_tax_rate=SALES_TAX_RATE,
            output=ADJUSTED,
        )


def test_its_output_holds_the_area_a_fields_without_the_four_of_the_adjustment() -> None:
    assert adjusted(SOLD).fields == ADJUSTED.fields
    assert ADJUSTED.fields == tuple(f for f in CLASSES.fields if f not in VEHICLE_FIELDS)
    assert len(ADJUSTED.fields) == 14


# --- computing: a row the rule does not apply to -----------------------------------------------


def test_a_row_of_year_0_is_unchanged() -> None:
    # "If the passenger vehicle in Class 10.1 is not designated for immediate expensing treatment,
    # this special rule does not apply": the caller marks such a row with the year 0, whatever its
    # cost.
    unchanged = row("10.1", proceeds="40000", diep_proceeds="40000", year=0, cost="0")

    assert proceeds(unchanged) == [(D("40000"), D("40000"))]


@pytest.mark.parametrize(
    ("cost", "assistance"),
    [("56500", "0"), ("0", "100"), ("0", "-100"), ("56500", "100"), ("0.01", "0")],
)
def test_a_row_of_year_0_with_a_cost_or_assistance_is_refused(cost: str, assistance: str) -> None:
    # The cost and the assistance are only read for a vehicle year; entered with the year 0 they
    # would be silently dropped.
    with pytest.raises(InvalidRecordError, match=r"^item 2: .*cost or government assistance"):
        adjusted(SOLD, row("10.1", proceeds="40000", year=0, cost=cost, assistance=assistance))


def test_a_row_of_year_0_of_another_class_is_unchanged() -> None:
    assert proceeds(row("8", additions="5000", proceeds="3000.55")) == [(D("3000.55"), D("0"))]


# --- computing: the cost against the prescribed amount -----------------------------------------


def test_a_cost_under_the_prescribed_amount_with_tax_is_unchanged() -> None:
    # 2025: 38,000 + 13% = 38,000 + 4,940 = 42,940.
    assert proceeds(only(2025, "30000", "20000", "20000")) == [(D("20000"), D("20000"))]


def test_a_cost_at_the_prescribed_amount_with_tax_is_unchanged() -> None:
    # "whose cost is more than the prescribed amount": a cost of exactly 42,940 is not more.
    assert proceeds(only(2025, "42940.00", "40000", "40000")) == [(D("40000"), D("40000"))]


def test_a_cost_a_cent_over_the_prescribed_amount_with_tax_is_adjusted() -> None:
    # 40,000 x 42,940 / 42,940.01 = 39,999.99068..., 39,999.99.
    assert proceeds(only(2025, "42940.01", "40000")) == [(D("39999.99"), D("0"))]


def test_a_cost_over_the_prescribed_amount_scales_the_proceeds_by_the_proportion() -> None:
    # Return CZ's vehicle: 42,940 / 56,500 = 0.76, so 40,000 becomes 30,400.00.
    assert proceeds(only(2025, "56500.00", "40000", "40000")) == [(D("30400.00"), D("30400.00"))]


def test_the_proceeds_come_out_to_the_cent() -> None:
    (record,) = adjusted(only(2025, "56500.00", "40000", "40000")).records

    assert str(record[CCA_PROCEEDS]) == "30400.00"
    assert str(record[CCA_DIEP_PROCEEDS]) == "30400.00"


# --- computing: government assistance ----------------------------------------------------------


def test_assistance_received_reduces_the_actual_cost() -> None:
    # 56,500 - 13,560 = 42,940: not more than the prescribed amount with tax, so unchanged though
    # the cost alone is.
    assert proceeds(only(2025, "56500", "40000", "40000", assistance="13560")) == [
        (D("40000"), D("40000"))
    ]


def test_assistance_received_still_leaves_a_cost_over_the_prescribed_amount() -> None:
    # 56,500 - 6,500 = 50,000; 40,000 x 42,940 / 50,000 = 34,352.00.
    assert proceeds(only(2025, "56500", "40000", assistance="6500")) == [(D("34352.00"), D("0"))]


def test_assistance_repaid_increases_the_actual_cost() -> None:
    # A repayment is negative: 42,940 - (-7,060) = 50,000, over the prescribed amount with tax
    # though the cost alone is at it; 40,000 x 42,940 / 50,000 = 34,352.00.
    assert proceeds(only(2025, "42940", "40000", assistance="-7060")) == [(D("34352.00"), D("0"))]


@pytest.mark.parametrize(("cost", "assistance"), [("10000", "10000"), ("10000", "12000")])
def test_an_actual_cost_of_zero_or_less_is_unchanged(cost: str, assistance: str) -> None:
    # The actual cost is 0 or -2,000: not more than the prescribed amount; no division by it.
    assert proceeds(only(2025, cost, "40000", "40000", assistance=assistance)) == [
        (D("40000"), D("40000"))
    ]


def test_a_cost_of_zero_with_a_year_is_unchanged() -> None:
    assert proceeds(only(2025, "0", "40000", "40000")) == [(D("40000"), D("40000"))]


# --- computing: the sales tax rate -------------------------------------------------------------


def test_a_rate_of_0_gives_the_prescribed_amount_without_tax() -> None:
    # 38,000 only: a cost of 40,000 is over it, 40,000 x 38,000 / 40,000 = 38,000.00 ...
    assert proceeds(only(2025, "40000", "40000", "40000"), rate="0") == [
        (D("38000.00"), D("38000.00"))
    ]
    # ... and the same cost at 13% (42,940) is under it.
    assert proceeds(only(2025, "40000", "40000", "40000"), rate="13") == [(D("40000"), D("40000"))]


def test_a_rate_of_0_scales_by_the_prescribed_amount_alone() -> None:
    # 40,000 x 38,000 / 50,000 = 30,400.00.
    assert proceeds(only(2025, "50000", "40000"), rate="0") == [(D("30400.00"), D("0"))]


def test_a_rate_of_13_adds_the_hst_to_the_prescribed_amount() -> None:
    # 38,000 + 13% = 42,940: 40,000 x 42,940 / 50,000 = 34,352.00.
    assert proceeds(only(2025, "50000", "40000"), rate="13") == [(D("34352.00"), D("0"))]


def test_a_rate_of_5_adds_the_gst_to_the_prescribed_amount() -> None:
    # "Use the GST rate of 5": 38,000 + 1,900 = 39,900; 40,000 x 39,900 / 50,000 = 31,920.00.
    assert proceeds(only(2025, "50000", "40000"), rate="5") == [(D("31920.00"), D("0"))]


def test_the_tax_on_the_prescribed_amount_is_rounded_with_the_dataset_rule() -> None:
    # 37,000 x 0.0865 / 100 = 32.005, half-up 32.01: 37,032.01; 40,000 x 37,032.01 / 50,000 =
    # 29,625.608, 29,625.61, and 10,000 x 37,032.01 / 50,000 = 7,406.402, 7,406.40.
    assert proceeds(only(2024, "50000", "40000", "10000"), rate="0.0865") == [
        (D("29625.61"), D("7406.40"))
    ]


# --- computing: the year the vehicle was acquired ---------------------------------------------


@pytest.mark.parametrize(
    ("year", "prescribed", "scaled"),
    [
        (2025, "42940", "21470.00"),
        (2024, "41810", "20905.00"),
        (2023, "40680", "20340.00"),
        (2022, "38420", "19210.00"),
        (2021, "33900", "16950.00"),
        (2026, "42940", "21470.00"),
        (2030, "42940", "21470.00"),
    ],
)
def test_each_year_uses_the_prescribed_amount_printed_for_it(
    year: int, prescribed: str, scaled: str
) -> None:
    # At 13% HST, a cost of 100,000 and proceeds of 50,000, the factor is the prescribed amount
    # with tax over 100,000: 2025 38,000 + 4,940, 2024 37,000 + 4,810, 2023 36,000 + 4,680, 2022
    # 34,000 + 4,420 and 2021 30,000 + 3,900 (the open-ended "before 2022" row); a later year than
    # the dataset's newest row (2026, 2030) uses the 2025 row.
    row_ = only(year, "100000", "50000.00")

    assert proceeds(row_) == [(D(scaled), D("0"))]
    (line,) = capability().compute((classes(row_), sales_tax_rate())).trace
    assert isinstance(line, CcaVehicleProceedsLine)
    assert line.prescribed_amount == D(prescribed)


def test_a_vehicle_acquired_before_2021_is_refused() -> None:
    # A DIEP is property acquired after April 18, 2021: nothing is printed for 2020.
    with pytest.raises(InvalidRecordError, match=r"^item 1: .*2020"):
        adjusted(only(2020, "56500", "40000"))


def test_a_year_before_2021_is_refused_even_when_the_cost_is_under_the_amount() -> None:
    with pytest.raises(InvalidRecordError, match=r"^item 1: .*2020"):
        adjusted(only(2020, "0", "40000"))


def test_2021_is_allowed() -> None:
    assert proceeds(only(2021, "100000", "30000")) == [(D("10170.00"), D("0"))]


@pytest.mark.parametrize("number", ["8", "10", "54", "12"])
def test_a_class_other_than_10_1_with_a_year_is_refused(number: str) -> None:
    # Class 54 (zero-emission cars) has the same rule in the form text, but its vehicles are in the
    # row's list of sold vehicles, not in the year of the row: refused, not adjusted.
    with pytest.raises(InvalidRecordError, match=r"^item 2: .*10\.1"):
        adjusted(SOLD, row(number, proceeds="40000", year=2025, cost="56500"))


def test_a_class_other_than_10_1_without_a_year_is_unchanged() -> None:
    assert proceeds(row("10", proceeds="40000")) == [(D("40000"), D("0"))]


# --- computing: the DIEP part ------------------------------------------------------------------


def test_the_diep_proceeds_are_scaled_by_the_same_factor() -> None:
    # 20,000 x 0.76 = 15,200.00 of the 40,000 x 0.76 = 30,400.00.
    assert proceeds(only(2025, "56500", "40000", "20000")) == [(D("30400.00"), D("15200.00"))]


def test_no_diep_proceeds_stay_zero() -> None:
    assert proceeds(only(2025, "56500", "40000")) == [(D("30400.00"), D("0"))]


def test_the_diep_proceeds_stay_at_most_the_proceeds() -> None:
    # Column 6 is part of column 5: 99.99 of 100.00, 50.00 and 50.00 (49.995 and 50.00 half-up).
    ((column_5, column_6),) = proceeds(only(2025, "85880", "100.00", "99.99"))

    assert (column_5, column_6) == (D("50.00"), D("50.00"))
    assert column_6 <= column_5


@pytest.mark.parametrize("diep", ["0", "0.01", "33333.33", "39999.99", "40000"])
def test_the_scaled_diep_proceeds_never_exceed_the_scaled_proceeds(diep: str) -> None:
    ((column_5, column_6),) = proceeds(only(2025, "60000", "40000", diep))

    assert column_6 <= column_5


# --- computing: rounding -----------------------------------------------------------------------


def test_rounds_half_up_to_the_cent() -> None:
    # 100.01 x 42,940 / 85,880 = 50.005, half-up 50.01; 25.01 of it a DIEP's, 12.505, 12.51.
    assert proceeds(only(2025, "85880", "100.01", "25.01")) == [(D("50.01"), D("12.51"))]


def test_rounds_once_the_exact_product_over_the_cost() -> None:
    # 10,000 x 42,940 / 60,000 = 7,156.666..., 7,156.67 (rounding the factor, 0.7156..., first to
    # 0.7157 would give 7,157.00); 3,333.33 x 42,940 / 60,000 = 2,385.5497..., 2,385.55.
    assert proceeds(only(2025, "60000", "10000", "3333.33")) == [(D("7156.67"), D("2385.55"))]


def test_rounds_with_the_datasets_rule_not_a_fixed_one() -> None:
    # Half-even at the cent: 50.005 is 50.00 and 12.505 is 12.50.
    dataset = prescribed_amounts(RoundTo(D("0.01"), RoundingMode.HALF_EVEN))

    assert proceeds(only(2025, "85880", "100.01", "25.01"), dataset=dataset) == [
        (D("50.00"), D("12.50"))
    ]


def test_rounds_to_the_datasets_increment() -> None:
    # To the dollar, half-up: 50.005 is 50.
    dataset = prescribed_amounts(RoundTo(D("1"), RoundingMode.HALF_UP))

    assert proceeds(only(2025, "85880", "100.01"), dataset=dataset) == [(D("50"), D("0"))]


def test_the_prescribed_amount_is_the_datasets_row_not_a_fixed_figure() -> None:
    dataset = prescribed_amounts(rows=((2025, "20000"), (None, "10000")))

    # 20,000 + 13% = 22,600; 40,000 x 22,600 / 56,500 = 16,000.00.
    assert proceeds(only(2025, "56500", "40000"), dataset=dataset) == [(D("16000.00"), D("0"))]


# --- computing: the record ---------------------------------------------------------------------


def test_the_output_record_lacks_the_vehicle_fields_and_keeps_all_the_others() -> None:
    full = row(
        "10.1",
        ucc_at_start="1000",
        additions="42940",
        proceeds="40000",
        diep_proceeds="20000",
        year=2025,
        cost="56500",
        assistance="0",
        diep_additions="42940",
        immediate_expensing="500",
        claimed="900.50",
        no_property_left=1,
        personal_part_remaining="75.25",
        half_year_rule_differs=1,
        rate_election=2,
        aiip_additions="11",
        riip_additions="12",
    )

    (record,) = adjusted(full).records

    assert record == {
        CCA_CLASS_NUMBER: D("10.1"),
        CCA_UCC_AT_START: D("1000"),
        CCA_ADDITIONS: D("42940"),
        CCA_DIEP_ADDITIONS: D("42940"),
        CCA_PROCEEDS: D("30400.00"),
        CCA_DIEP_PROCEEDS: D("15200.00"),
        CCA_IMMEDIATE_EXPENSING: D("500"),
        CCA_AIIP_ADDITIONS: D("11"),
        CCA_RIIP_ADDITIONS: D("12"),
        CCA_CLAIMED: D("900.50"),
        CCA_NO_PROPERTY_LEFT: 1,
        CCA_PERSONAL_PART_REMAINING: D("75.25"),
        CCA_HALF_YEAR_RULE_DIFFERS: 1,
        CCA_RATE_ELECTION: 2,
    }
    for field in VEHICLE_FIELDS:
        assert field not in record


def test_an_unchanged_row_keeps_every_field_but_the_vehicle_ones() -> None:
    unchanged = row("8", ucc_at_start="10000", additions="5000", claimed="2200", year=0)

    (record,) = adjusted(unchanged).records

    assert {field: record[field] for field in ADJUSTED.fields} == {
        field: unchanged[field] for field in ADJUSTED.fields
    }


def test_each_row_gives_one_record_in_the_callers_order() -> None:
    assert proceeds(
        row("8", proceeds="1000"),
        SOLD,
        only(2024, "100000", "50000"),
    ) == [
        (D("1000"), D("0")),
        (D("30400.00"), D("30400.00")),
        (D("20905.00"), D("0")),
    ]
    assert [r[CCA_CLASS_NUMBER] for r in adjusted(row("8"), SOLD).records] == [D("8"), D("10.1")]


def test_no_classes_give_an_empty_list() -> None:
    held = adjusted()

    assert held.records == ()
    assert held.fields == ADJUSTED.fields


def test_the_error_names_the_item_by_position_from_1() -> None:
    with pytest.raises(InvalidRecordError, match=r"^item 3: "):
        adjusted(SOLD, row("8"), row("8", proceeds="1", year=2025, cost="1"))


def test_missing_classes_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="business_cca_classes"):
        capability().compute((sales_tax_rate(),))


def test_a_missing_sales_tax_rate_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="business_vehicle_sales_tax_rate"):
        capability().compute((classes(SOLD),))


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(ArtifactKind("ex/other_amount", Decimal), D("9"))

    (output,) = capability().compute((other, classes(SOLD), sales_tax_rate())).outputs

    assert output.kind is ADJUSTED


def test_does_not_change_its_input() -> None:
    held = classes(SOLD)
    before = [dict(record.items()) for record in held.value.records]

    capability().compute((held, sales_tax_rate()))

    assert [dict(record.items()) for record in held.value.records] == before


# --- trace -------------------------------------------------------------------------------------


def test_traces_one_line_per_row_and_no_total() -> None:
    trace = (
        capability()
        .compute(
            (
                classes(
                    row("8", proceeds="1000"),
                    SOLD,
                    only(2025, "30000", "20000", "10000"),
                    only(2024, "100000", "50000", "25000", assistance="0"),
                ),
                sales_tax_rate(),
            )
        )
        .trace
    )

    assert trace == (
        trace_line(1, False, "0", "0", "1000", "1000"),
        trace_line(2, True, "42940", "56500", "40000", "30400", "40000", "30400"),
        trace_line(3, False, "42940", "30000", "20000", "20000", "10000", "10000"),
        trace_line(4, True, "41810", "100000", "50000", "20905", "25000", "10452.5"),
    )


def test_a_row_of_year_0_is_traced_as_not_adjusted_with_no_amounts() -> None:
    (line,) = capability().compute((classes(row("8", proceeds="1000")), sales_tax_rate())).trace

    assert line == trace_line(1, False, "0", "0", "1000", "1000")


def test_a_cost_not_over_the_amount_is_traced_with_both_amounts_and_not_adjusted() -> None:
    (line,) = (
        capability()
        .compute((classes(only(2025, "42940", "40000", "40000")), sales_tax_rate()))
        .trace
    )

    assert line == trace_line(1, False, "42940", "42940", "40000", "40000", "40000", "40000")


def test_traces_the_cost_less_the_assistance() -> None:
    (line,) = (
        capability()
        .compute((classes(only(2025, "56500", "40000", assistance="6500")), sales_tax_rate()))
        .trace
    )

    assert line == trace_line(1, True, "42940", "50000", "40000", "34352")


def test_traces_the_prescribed_amount_with_the_rounded_tax() -> None:
    (line,) = (
        capability()
        .compute((classes(only(2024, "50000", "40000")), sales_tax_rate("0.0865")))
        .trace
    )

    assert line == trace_line(1, True, "37032.01", "50000", "40000", "29625.61")


def test_traces_no_classes_as_no_lines() -> None:
    assert capability().compute((classes(), sales_tax_rate())).trace == ()


def test_each_trace_lines_amount_is_its_records_adjusted_proceeds() -> None:
    result = capability().compute((classes(SOLD, row("8", proceeds="7")), sales_tax_rate()))

    (output,) = result.outputs
    assert [line.amount for line in result.trace] == [
        record[CCA_PROCEEDS] for record in output.value.records
    ]


# --- through TaxComputationService -------------------------------------------------------------


def test_a_computation_gives_the_adjusted_list() -> None:
    worksheet = service().compute(
        JurisdictionCode("CA-ON"), 2025, classes(SOLD, row("8", proceeds="500")), sales_tax_rate()
    )["ca-on/return"][0]

    value = worksheet.get(ADJUSTED).value
    assert isinstance(value, RecordList)
    records: tuple[Record, ...] = value.records
    assert [(r[CCA_CLASS_NUMBER], r[CCA_PROCEEDS], r[CCA_DIEP_PROCEEDS]) for r in records] == [
        (D("10.1"), D("30400.00"), D("30400.00")),
        (D("8"), D("500"), D("0")),
    ]
    assert isinstance(worksheet.producer_of(ADJUSTED), CcaVehicleProceeds)


def test_the_list_kind_the_computation_gives_is_a_record_list_kind() -> None:
    assert isinstance(ADJUSTED, RecordListKind)


# --- Class 54: the sold zero-emission passenger vehicles of a row ---------------------------------
#
# Guide T4036 2025, "Class 54 (30%)", with the sales tax rate 0 unless a test says otherwise: the
# prescribed amount for a vehicle acquired in 2023 or later is $61,000, in 2022 $59,000, from 2019
# to 2021 $55,000. Car A, acquired in 2024 for 65,000 and sold for 30,000, is over the limit: the
# factor is 61,000 / 65,000. Car B, acquired in 2022 for 50,000 and sold for 20,000, is under the
# limit of 59,000 and unchanged.

CAR_A = zepv(2024, "65000", "30000")
CAR_B = zepv(2022, "50000", "20000")


def class_54(*vehicles: CcaRow, **fields: Any) -> CcaRow:
    """A Class 54 row selling `vehicles`; `fields` are the other arguments of `row`."""
    return row("54", sold=vehicles, **fields)


def totals(
    *vehicles: CcaRow,
    rate: str = "0",
    dataset: ParameterDataset[Any] | None = None,
    zepv_dataset: ParameterDataset[Any] | None = None,
    **fields: Any,
) -> tuple[Decimal, Decimal]:
    """Columns 5 and 6 of the one Class 54 row selling `vehicles`, after the adjustment."""
    (found,) = proceeds(
        class_54(*vehicles, **fields), rate=rate, dataset=dataset, zepv_dataset=zepv_dataset
    )
    return found


def test_the_two_cars_are_scaled_one_by_one_and_summed_into_column_5() -> None:
    # Car A: 30,000 x 61,000 / 65,000 = 28,153.846..., 28,153.85 to the cent; car B: unchanged
    # 20,000; column 5 is 28,153.85 + 20,000 = 48,153.85.
    assert totals(CAR_A, CAR_B) == (D("48153.85"), D("0"))


def test_the_guides_example_is_28154_when_the_dataset_rounds_to_the_dollar() -> None:
    # The guide's "$30,000 × ($61,000 ÷ $65,000) = $28,154" is to the dollar; the capability
    # rounds with the dataset's rule, so a dataset of whole dollars gives the guide's figures,
    # 28,154 + 20,000 = 48,154.
    dataset = zepv_prescribed_amounts(DOLLAR)

    assert totals(CAR_A, zepv_dataset=dataset) == (D("28154"), D("0"))
    assert totals(CAR_A, CAR_B, zepv_dataset=dataset) == (D("48154"), D("0"))


def test_a_cost_over_the_limit_alone_is_scaled_to_the_cent() -> None:
    assert totals(CAR_A) == (D("28153.85"), D("0"))


def test_a_vehicle_of_year_0_is_copied_as_entered() -> None:
    # Year 0: the rule does not apply to the vehicle (not sold at arm's length, say).
    assert totals(zepv(0, "0", "30000", "10000")) == (D("30000"), D("10000"))
    assert totals(zepv(0, "0", "30000"), CAR_A) == (D("58153.85"), D("0"))


def test_a_vehicle_of_year_0_with_a_cost_or_assistance_is_refused() -> None:
    with pytest.raises(InvalidRecordError, match=r"^item 1 vehicle 1: .*cost or government"):
        totals(zepv(0, "65000", "30000", "10000"))


def test_a_vehicle_at_the_limit_is_unchanged() -> None:
    # "whose cost is more than the prescribed amount": 61,000 is not more than 61,000.
    assert totals(zepv(2024, "61000", "1000000")) == (D("1000000"), D("0"))


def test_a_vehicle_a_cent_over_the_limit_is_scaled() -> None:
    # 1,000,000 x 61,000 / 61,000.01 = 999,999.836..., 999,999.84.
    assert totals(zepv(2024, "61000.01", "1000000")) == (D("999999.84"), D("0"))


def test_the_limit_is_the_prescribed_amount_plus_the_sales_tax_rate() -> None:
    # At 13%: 61,000 + 7,930 = 68,930 for 2024 and 59,000 + 7,670 = 66,670 for 2022, so cars A and
    # B are both under their limits; 68,930.00 is the limit, a cent more is over it.
    assert totals(CAR_A, CAR_B, rate="13") == (D("50000"), D("0"))
    assert totals(zepv(2024, "68930", "1000000"), rate="13") == (D("1000000"), D("0"))
    assert totals(zepv(2024, "68930.01", "1000000"), rate="13") == (D("999999.85"), D("0"))
    # 30,000 x 68,930 / 80,000 = 25,848.75.
    assert totals(zepv(2024, "80000", "30000"), rate="13") == (D("25848.75"), D("0"))


def test_the_sales_tax_on_the_prescribed_amount_is_rounded_with_the_zepv_datasets_rule() -> None:
    # 61,000 x 0.0865% = 52.765, 52.77 half-up: 61,052.77; 40,000 x 61,052.77 / 70,000 = 34,887.30.
    result = capability().compute(
        (classes(class_54(zepv(2024, "70000", "40000"))), sales_tax_rate("0.0865"))
    )

    assert result.trace[1:] == (zepv_line(1, 1, True, "61052.77", "70000", "40000", "34887.30"),)


@pytest.mark.parametrize(
    ("year", "scaled"),
    [
        (2030, "30500.00"),
        (2025, "30500.00"),
        (2023, "30500.00"),
        (2022, "29500.00"),
        (2021, "27500.00"),
        (2020, "27500.00"),
        (2019, "27500.00"),
    ],
)
def test_each_year_uses_the_prescribed_amount_printed_for_it_in_class_54(
    year: int, scaled: str
) -> None:
    # At a cost of 100,000 and proceeds of 50,000: 2023 and later 61,000, 2022 59,000, 2019 to
    # 2021 55,000 (the oldest row); a later year than the newest row uses the newest.
    assert totals(zepv(year, "100000", "50000")) == (D(scaled), D("0"))


def test_a_vehicle_acquired_before_2019_is_refused() -> None:
    # Class 54 is for vehicles "acquired after March 18, 2019": nothing is printed for 2018.
    with pytest.raises(InvalidRecordError, match=r"^item 2 vehicle 2: .*2018"):
        adjusted(row("8"), class_54(CAR_A, zepv(2018, "65000", "30000")))


def test_a_vehicle_year_before_2019_is_refused_even_when_the_cost_is_under_the_amount() -> None:
    with pytest.raises(InvalidRecordError, match=r"^item 1 vehicle 1: .*2018"):
        adjusted(class_54(zepv(2018, "0", "30000")))


@pytest.mark.parametrize("number", ["8", "10", "10.1", "12", "55"])
def test_sold_vehicles_on_a_row_of_another_class_are_refused(number: str) -> None:
    # Only a Class 54 row may hold the list, Class 10.1's included.
    with pytest.raises(InvalidRecordError, match=r"^item 2 vehicle 1: .*54"):
        adjusted(SOLD, row(number, sold=(CAR_A,)))


def test_a_vehicle_of_year_0_on_a_row_of_another_class_is_refused_too() -> None:
    with pytest.raises(InvalidRecordError, match=r"^item 1 vehicle 1: .*54"):
        adjusted(row("8", sold=(zepv(0, "0", "100"),)))


def test_a_row_of_another_class_without_sold_vehicles_is_unchanged() -> None:
    assert proceeds(row("8", proceeds="1000", diep_proceeds="10")) == [(D("1000"), D("10"))]


def test_the_error_names_the_item_and_the_vehicle_by_position_from_1() -> None:
    with pytest.raises(InvalidRecordError, match=r"^item 3 vehicle 2: "):
        adjusted(SOLD, row("8"), class_54(CAR_A, zepv(2018, "1", "1")), class_54(CAR_B, CAR_B))


def test_a_year_on_a_class_54_row_is_still_refused_as_a_class_10_1_vehicle() -> None:
    with pytest.raises(
        InvalidRecordError,
        match=r"^item 1: a vehicle year is given but the class is 54, not 10\.1$",
    ):
        adjusted(row("54", proceeds="40000", year=2025, cost="56500"))


@pytest.mark.parametrize("fields", [{"proceeds": "1000"}, {"diep_proceeds": "500"}])
def test_an_amount_entered_in_column_5_or_6_of_a_class_54_row_is_refused(
    fields: dict[str, Any],
) -> None:
    with pytest.raises(
        InvalidRecordError,
        match=r"^item 1: .*column 5 or 6 of a Class 54 row; a Class 54 sale price must be listed "
        r"as a vehicle$",
    ):
        totals(CAR_A, **fields)


def test_an_amount_entered_on_a_class_54_row_without_sold_vehicles_is_refused() -> None:
    with pytest.raises(InvalidRecordError, match=r"^item 1: .*must be listed as a vehicle$"):
        totals(proceeds="5000", diep_proceeds="100")


def test_the_error_for_an_amount_on_a_class_54_row_names_the_item() -> None:
    with pytest.raises(InvalidRecordError, match=r"^item 2: "):
        adjusted(row("8"), class_54(proceeds="1"))


def test_a_class_54_row_without_sold_vehicles_has_no_proceeds() -> None:
    assert totals() == (D("0"), D("0"))


def test_the_diep_part_of_a_vehicle_is_scaled_by_its_factor() -> None:
    # 15,000 x 61,000 / 65,000 = 14,076.92.
    assert totals(zepv(2024, "65000", "30000", "15000")) == (D("28153.85"), D("14076.92"))


def test_the_diep_part_of_every_vehicle_is_summed_into_column_6() -> None:
    # Car B is under its limit: its DIEP part stays 20,000.
    assert totals(zepv(2024, "65000", "30000", "15000"), zepv(2022, "50000", "20000", "20000")) == (
        D("48153.85"),
        D("34076.92"),
    )


def test_assistance_received_reduces_the_actual_cost_of_a_vehicle() -> None:
    # 70,000 - 5,000 = 65,000, car A's.
    assert totals(zepv(2024, "70000", "30000", assistance="5000")) == (D("28153.85"), D("0"))
    # 70,000 - 9,000 = 61,000, at the limit.
    assert totals(zepv(2024, "70000", "30000", assistance="9000")) == (D("30000"), D("0"))


def test_assistance_repaid_increases_the_actual_cost_of_a_vehicle() -> None:
    # 55,000 - (-10,000) = 65,000, car A's.
    assert totals(zepv(2024, "55000", "30000", assistance="-10000")) == (D("28153.85"), D("0"))


def test_an_actual_cost_of_zero_or_less_leaves_a_vehicle_unchanged() -> None:
    assert totals(zepv(2024, "0", "30000")) == (D("30000"), D("0"))
    assert totals(zepv(2024, "10000", "30000", assistance="12000")) == (D("30000"), D("0"))


def test_each_vehicle_is_rounded_on_its_own_and_the_roundings_are_summed() -> None:
    # Two vehicles of 100.01 over a factor of 0.5 are 50.005 each, 50.01 half-up; the column is
    # 100.02, not the 100.01 of rounding the sum 200.02 x 0.5.
    car = zepv(2024, "122000", "100.01")

    assert totals(car, car) == (D("100.02"), D("0"))


def test_rounds_with_the_zepv_datasets_rule_not_the_class_10_1_datasets() -> None:
    # The Class 54 dataset rounds half-even at the cent (50.005 is 50.00); the Class 10.1 dataset
    # keeps its half-up (50.005 is 50.01). At 13%: 61,000 + 7,930 = 68,930 and 137,860 x 0.5 =
    # 68,930, so the factor of the car is 0.5.
    zepv_dataset = zepv_prescribed_amounts(RoundTo(D("0.01"), RoundingMode.HALF_EVEN))
    car = zepv(2024, "137860", "100.01")

    assert proceeds(
        class_54(car), only(2025, "85880", "100.01"), rate="13", zepv_dataset=zepv_dataset
    ) == [(D("50.00"), D("0")), (D("50.01"), D("0"))]


def test_rounds_to_the_zepv_datasets_increment() -> None:
    zepv_dataset = zepv_prescribed_amounts(DOLLAR)

    assert totals(zepv(2024, "122000", "100.01"), zepv_dataset=zepv_dataset) == (D("50"), D("0"))


def test_the_prescribed_amounts_are_the_zepv_datasets_rows_not_fixed_figures() -> None:
    dataset = zepv_prescribed_amounts(rows=((2023, "20000"), (2019, "10000")))

    # 30,000 x 20,000 / 40,000 = 15,000; 30,000 x 10,000 / 40,000 = 7,500.
    assert totals(zepv(2024, "40000", "30000"), zepv_dataset=dataset) == (D("15000.00"), D("0"))
    assert totals(zepv(2019, "40000", "30000"), zepv_dataset=dataset) == (D("7500.00"), D("0"))


def test_a_class_10_1_row_still_uses_the_class_10_1_dataset() -> None:
    # Swapping the Class 54 dataset changes only Class 54 rows.
    zepv_dataset = zepv_prescribed_amounts(rows=((2019, "1000"),))

    assert proceeds(SOLD, zepv_dataset=zepv_dataset) == [(D("30400.00"), D("30400.00"))]


def test_a_class_54_row_and_a_class_10_1_row_in_one_list() -> None:
    # The Class 10.1 vehicle at 0%: 40,000 x 38,000 / 56,500 = 26,902.65.
    assert proceeds(SOLD, class_54(CAR_A, CAR_B), row("8", proceeds="5"), rate="0") == [
        (D("26902.65"), D("26902.65")),
        (D("48153.85"), D("0")),
        (D("5"), D("0")),
    ]


def test_the_class_54_output_record_has_the_summed_proceeds_and_keeps_the_other_fields() -> None:
    full = class_54(
        CAR_A,
        CAR_B,
        ucc_at_start="100000",
        additions="5000",
        claimed="15000.00",
        no_property_left=1,
        personal_part_remaining="75.25",
        half_year_rule_differs=1,
        rate_election=2,
    )

    (record,) = adjusted(full, rate="0").records

    assert record == {
        CCA_CLASS_NUMBER: D("54"),
        CCA_UCC_AT_START: D("100000"),
        CCA_ADDITIONS: D("5000"),
        CCA_DIEP_ADDITIONS: D("0"),
        CCA_PROCEEDS: D("48153.85"),
        CCA_DIEP_PROCEEDS: D("0"),
        CCA_IMMEDIATE_EXPENSING: D("0"),
        CCA_AIIP_ADDITIONS: D("0"),
        CCA_RIIP_ADDITIONS: D("0"),
        CCA_CLAIMED: D("15000.00"),
        CCA_NO_PROPERTY_LEFT: 1,
        CCA_PERSONAL_PART_REMAINING: D("75.25"),
        CCA_HALF_YEAR_RULE_DIFFERS: 1,
        CCA_RATE_ELECTION: 2,
    }
    for field in VEHICLE_FIELDS:
        assert field not in record


def test_sold_vehicles_do_not_change_the_input() -> None:
    held = classes(class_54(CAR_A, CAR_B))
    before = [dict(record.items()) for record in held.value.records]

    capability().compute((held, sales_tax_rate("0")))

    assert [dict(record.items()) for record in held.value.records] == before


# --- Class 54: trace ---------------------------------------------------------------------------


def test_traces_each_vehicle_after_the_line_of_its_row_and_no_total() -> None:
    # Per row, the row's own line first (a Class 54 row is not adjusted as a whole: its entered
    # proceeds, no amounts), then one line for each of its vehicles, by position from 1.
    trace = (
        capability()
        .compute(
            (
                classes(
                    row("8", proceeds="1000"),
                    class_54(CAR_A, CAR_B, zepv(0, "0", "10000", "4000")),
                    row("8", proceeds="5"),
                ),
                sales_tax_rate("0"),
            )
        )
        .trace
    )

    assert trace == (
        trace_line(1, False, "0", "0", "1000", "1000"),
        trace_line(2, False, "0", "0", "0", "0"),
        zepv_line(2, 1, True, "61000", "65000", "30000", "28153.85"),
        zepv_line(2, 2, False, "59000", "50000", "20000", "20000"),
        zepv_line(2, 3, False, "0", "0", "10000", "10000", "4000", "4000"),
        trace_line(3, False, "0", "0", "5", "5"),
    )


def test_a_vehicle_over_the_limit_is_traced_with_its_diep_part() -> None:
    result = capability().compute(
        (classes(class_54(zepv(2024, "65000", "30000", "15000"))), sales_tax_rate("0"))
    )

    assert result.trace[1:] == (
        zepv_line(1, 1, True, "61000", "65000", "30000", "28153.85", "15000", "14076.92"),
    )


def test_the_traced_actual_cost_is_the_cost_less_the_assistance() -> None:
    result = capability().compute(
        (
            classes(class_54(zepv(2024, "70000", "30000", assistance="5000"))),
            sales_tax_rate("0"),
        )
    )

    assert result.trace[1:] == (zepv_line(1, 1, True, "61000", "65000", "30000", "28153.85"),)


def test_a_class_54_row_without_sold_vehicles_is_traced_as_its_row_alone() -> None:
    assert capability().compute((classes(class_54()), sales_tax_rate())).trace == (
        trace_line(1, False, "0", "0", "0", "0"),
    )


def test_each_vehicle_lines_amount_is_its_adjusted_proceeds() -> None:
    trace = capability().compute((classes(class_54(CAR_A, CAR_B)), sales_tax_rate("0"))).trace

    lines = [line for line in trace if isinstance(line, CcaZepvProceedsLine)]
    assert [line.amount for line in lines] == [D("28153.85"), D("20000")]


def test_the_vehicle_lines_add_up_to_the_records_column_5() -> None:
    result = capability().compute((classes(class_54(CAR_A, CAR_B)), sales_tax_rate("0")))

    (output,) = result.outputs
    (record,) = output.value.records
    vehicles = [line for line in result.trace if isinstance(line, CcaZepvProceedsLine)]
    assert record[CCA_PROCEEDS] == sum((line.amount for line in vehicles), D(0))


# --- Class 54: through TaxComputationService -----------------------------------------------------


def test_a_computation_gives_the_summed_class_54_proceeds() -> None:
    worksheet = service().compute(
        JurisdictionCode("CA-ON"), 2025, classes(class_54(CAR_A, CAR_B)), sales_tax_rate("0")
    )["ca-on/return"][0]

    value = worksheet.get(ADJUSTED).value
    assert isinstance(value, RecordList)
    assert [
        (r[CCA_CLASS_NUMBER], r[CCA_PROCEEDS], r[CCA_DIEP_PROCEEDS]) for r in value.records
    ] == [
        (D("54"), D("48153.85"), D("0")),
    ]
    assert isinstance(worksheet.producer_of(ADJUSTED), CcaVehicleProceeds)
