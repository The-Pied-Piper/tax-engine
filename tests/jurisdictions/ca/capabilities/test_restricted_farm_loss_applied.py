"""Unit tests for the restricted farm loss applied to a disposition list, Guide T4037 p.34.

Identifier `ca/restricted_farm_loss_applied`, one capability over each of the four lists that hold
farmland dispositions: the real estate list, the qualified farm or fishing property list, its
mortgage foreclosures list and the other mortgage foreclosures list. The output is the sum over the
rows of the property taxes (the Guide's line C) and the interest (line D) added to the cost base:
the amount the filer has applied, which reduces the restricted farm loss balance (Guide T4037 p.34
"Also, you have to reduce your RFL balance by these amounts."). The part of the loss typed on a row
is not read here: the total is checked against the unapplied balance by `core/at_most`.

The records are built with the helpers of `tests/jurisdictions/ca/capabilities/disposition_rows.py`
(`real_estate`, `qffp`). The capability has no parameter dataset, so this module has no
`ForeignTaxCountriesTotalCases`-style shared base: its figures are two fields, not one. It records
one `FarmLossAppliedLine` per row, by position from 1, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from decimal import Decimal
from types import MappingProxyType
from typing import Any, cast

import pytest

import tax_engine.jurisdictions.ca.capabilities as canada
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.capabilities.restricted_farm_loss_applied import (
    RestrictedFarmLossApplied,
)
from tax_engine.jurisdictions.ca.catalog import (
    QFFP_DISPOSITIONS,
    QFFP_FORECLOSURE_DISPOSITIONS,
    QFFP_FORECLOSURE_RESTRICTED_FARM_LOSS_APPLIED,
    QFFP_RESTRICTED_FARM_LOSS_APPLIED,
    REAL_ESTATE_DISPOSITIONS,
    REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED,
)
from tax_engine.jurisdictions.ca.trace import FarmLossAppliedLine
from tests.jurisdictions.ca.capabilities.disposition_rows import (
    FarmLossRow,
    QffpRow,
    qffp,
    real_estate,
)

D = Decimal

# Guide T4037 p.34 example: farmland sold for 200,000, ACB 160,000, 10,000 of property taxes and
# interest in the restricted farm loss, of which 5,000 property taxes (line C) and 5,000 interest
# (line D) are applied to the cost base.
FARMLAND: FarmLossRow = ("200000", "160000", "0", 0, "10000", "5000", "5000")
# The same sale on the qualified farm or fishing property list, without its depreciable answer.
FARMLAND_QFFP: QffpRow = ("200000", "160000", "0", "10000", "5000", "5000")
# A real estate row with a restricted farm loss applied to nothing: lines C and D are 0.
NOTHING_APPLIED: FarmLossRow = ("500.00", "400.00", "0", 0, "10000", "0", "0")


def wired() -> RestrictedFarmLossApplied:
    return RestrictedFarmLossApplied(
        REAL_ESTATE_DISPOSITIONS, REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED
    )


def compute(*rows: FarmLossRow) -> Any:
    return wired().compute((real_estate(*rows),))


def total(*rows: FarmLossRow) -> Decimal:
    (output,) = compute(*rows).outputs
    assert output.kind is REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED
    value: Decimal = output.value
    return value


def lines(*rows: FarmLossRow) -> tuple[Any, ...]:
    return tuple(compute(*rows).trace)


# --- registration and slots -----------------------------------------------------------------


def test_is_exported_from_the_canada_capabilities_package() -> None:
    assert canada.NAMESPACE == "ca"
    assert "restricted_farm_loss_applied" in canada.__all__
    module = canada.restricted_farm_loss_applied
    assert module.__dict__["RestrictedFarmLossApplied"] is RestrictedFarmLossApplied


def test_is_registered_under_its_identifier() -> None:
    assert CapabilityRegistry.shared().get("ca/restricted_farm_loss_applied") is (
        RestrictedFarmLossApplied
    )


def test_declares_its_contract() -> None:
    assert wired().consumes == frozenset({REAL_ESTATE_DISPOSITIONS})
    assert wired().produces == frozenset({REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(RestrictedFarmLossApplied)
    assert "produces" not in vars(RestrictedFarmLossApplied)


def test_declares_its_slots() -> None:
    assert RestrictedFarmLossApplied.PARAMETERS == {}
    assert RestrictedFarmLossApplied.CONSUMES == {"dispositions": RecordList}
    assert RestrictedFarmLossApplied.PRODUCES == {"output": Decimal}
    assert not RestrictedFarmLossApplied.is_list_slot("dispositions")


def test_its_slots_are_read_only() -> None:
    for slots in (
        RestrictedFarmLossApplied.PARAMETERS,
        RestrictedFarmLossApplied.CONSUMES,
        RestrictedFarmLossApplied.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    built = RestrictedFarmLossApplied(
        dispositions=REAL_ESTATE_DISPOSITIONS, output=REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED
    )

    (output,) = built.compute((real_estate(FARMLAND),)).outputs

    assert output == Artifact(REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED, D("10000"))


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        RestrictedFarmLossApplied(  # type: ignore[call-arg]
            REAL_ESTATE_DISPOSITIONS, REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED, object()
        )


def test_refuses_a_money_kind_for_its_record_list() -> None:
    with pytest.raises(InvalidCapabilityError, match="RestrictedFarmLossApplied") as raised:
        RestrictedFarmLossApplied(
            ArtifactKind("ex/not_a_list", Decimal),  # type: ignore[arg-type]
            REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED,
        )

    assert "'dispositions'" in str(raised.value)


def test_refuses_a_count_kind_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="RestrictedFarmLossApplied") as raised:
        RestrictedFarmLossApplied(REAL_ESTATE_DISPOSITIONS, ArtifactKind("ex/a_count", int))  # type: ignore[arg-type]

    assert "'output'" in str(raised.value)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(RestrictedFarmLossApplied, "__type_params__", ())
    assert not getattr(RestrictedFarmLossApplied, "__parameters__", ())


# --- computing ------------------------------------------------------------------------------


def test_applies_the_property_taxes_and_the_interest_of_the_guide_example() -> None:
    # Guide T4037 p.34: line C 5,000 plus line D 5,000.
    assert total(FARMLAND) == D("10000")


def test_adds_the_rows_applied_amounts() -> None:
    other: FarmLossRow = ("300000", "250000", "0", 0, "2000", "1000", "500")

    assert total(FARMLAND, other) == D("11500")


def test_the_part_of_the_loss_typed_on_a_row_is_not_what_is_applied() -> None:
    # A part of 10,000 with lines C and D of 0 applies nothing.
    assert total(NOTHING_APPLIED) == D("0")


def test_only_lines_c_and_d_are_summed_and_not_the_proceeds_or_the_cost_base() -> None:
    row: FarmLossRow = ("900000", "1", "7", 1, "2500", "2500", "0")

    assert total(row) == D("2500")


def test_a_row_with_no_farm_loss_applied_adds_nothing() -> None:
    assert total(("500.00", "400.00", "100.00", 0, "0", "0", "0")) == D("0")


def test_an_empty_list_totals_zero() -> None:
    assert total() == D("0")


def test_keeps_the_cents_and_never_rounds() -> None:
    rows = (
        ("500", "400", "0", 0, "100.10", "100.10", "50.05"),
        ("500", "400", "0", 0, "100.10", "0.015", "0"),
    )

    assert total(*rows) == D("150.165")


def test_needs_its_record_list() -> None:
    with pytest.raises(MissingArtifactError):
        wired().compute(())


def test_has_one_output() -> None:
    result = wired().compute((real_estate(),))

    assert result.outputs == (Artifact(REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED, D("0")),)


def test_compute_is_repeatable() -> None:
    inputs = (real_estate(FARMLAND, NOTHING_APPLIED),)

    assert wired().compute(inputs) == wired().compute(inputs)


def test_reads_the_qualified_farm_or_fishing_property_lists_the_same_way() -> None:
    sales = RestrictedFarmLossApplied(QFFP_DISPOSITIONS, QFFP_RESTRICTED_FARM_LOSS_APPLIED)
    foreclosures = RestrictedFarmLossApplied(
        QFFP_FORECLOSURE_DISPOSITIONS, QFFP_FORECLOSURE_RESTRICTED_FARM_LOSS_APPLIED
    )

    (sold,) = sales.compute((qffp(FARMLAND_QFFP),)).outputs
    foreclosed = qffp(FARMLAND_QFFP)
    (repossessed,) = foreclosures.compute(
        (Artifact(QFFP_FORECLOSURE_DISPOSITIONS, foreclosed.value),)
    ).outputs

    assert sold == Artifact(QFFP_RESTRICTED_FARM_LOSS_APPLIED, D("10000"))
    assert repossessed == Artifact(QFFP_FORECLOSURE_RESTRICTED_FARM_LOSS_APPLIED, D("10000"))


# --- trace ----------------------------------------------------------------------------------


def line(position: int, taxes: str, interest: str) -> FarmLossAppliedLine:
    return FarmLossAppliedLine(
        output=REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED,
        position=position,
        property_taxes=D(taxes),
        interest=D(interest),
        result=D(taxes) + D(interest),
    )


def test_records_only_an_empty_total_for_no_rows() -> None:
    assert lines() == (
        ItemsTotalLine(output=REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED, items=(), total=D("0")),
    )


def test_records_one_line_per_row_by_position_then_the_total() -> None:
    assert lines(FARMLAND, NOTHING_APPLIED, FARMLAND) == (
        line(1, "5000", "5000"),
        line(2, "0", "0"),
        line(3, "5000", "5000"),
        ItemsTotalLine(
            output=REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED,
            items=((1, D("10000")), (2, D("0")), (3, D("10000"))),
            total=D("20000"),
        ),
    )


def test_records_a_farm_loss_applied_line_for_each_row_and_ends_with_the_total() -> None:
    trace = lines(FARMLAND, NOTHING_APPLIED)

    assert [type(entry) for entry in trace] == [
        FarmLossAppliedLine,
        FarmLossAppliedLine,
        ItemsTotalLine,
    ]


def test_the_last_trace_line_amount_is_the_output() -> None:
    trace = lines(FARMLAND, FARMLAND)

    assert trace[-1].amount == total(FARMLAND, FARMLAND)
