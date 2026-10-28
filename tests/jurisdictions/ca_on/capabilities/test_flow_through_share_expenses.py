"""Unit tests for the FlowThroughShareExpenses capability (`ca-on/flow_through_share_expenses`).

Form T1221 takes one line per corporation or slip, "Enter the amount of qualifying expenses.",
and line 4 "Add lines 1 to 3." The capability consumes the record list of those slips and
produces their total: it adds the one field of every record exactly, with no rounding (it has no
dataset), is zero for an empty list, and records one `RecordTotalLine` naming each item by its
position from 1.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType

import pytest

import tax_calculator.jurisdictions.ca_on
import tax_calculator.jurisdictions.ca_on.capabilities
import tax_calculator.registrations
from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import RecordTotalLine
from tax_calculator.jurisdictions.ca_on.capabilities.flow_through_share_expenses import (
    FlowThroughShareExpenses,
)
from tax_calculator.jurisdictions.ca_on.catalog import (
    FLOW_THROUGH_SHARE_EXPENSES,
    FLOW_THROUGH_SHARE_SLIP_EXPENSES,
    FLOW_THROUGH_SHARE_SLIPS,
)

D = Decimal


def capability() -> FlowThroughShareExpenses:
    return FlowThroughShareExpenses(
        slips=FLOW_THROUGH_SHARE_SLIPS, output=FLOW_THROUGH_SHARE_EXPENSES
    )


def slips(*expenses: str) -> Artifact[RecordList]:
    """An `ca-on/flow_through_share_slips` artifact of one record per amount, in order."""
    records = [{FLOW_THROUGH_SHARE_SLIP_EXPENSES: D(amount)} for amount in expenses]
    return Artifact(FLOW_THROUGH_SHARE_SLIPS, RecordList(FLOW_THROUGH_SHARE_SLIPS.fields, records))


def total_of(*expenses: str) -> Decimal:
    result = capability().compute((slips(*expenses),))
    (artifact,) = result.outputs
    assert artifact.kind == FLOW_THROUGH_SHARE_EXPENSES
    value = artifact.value
    assert isinstance(value, Decimal)
    return value


def test_is_registered_as_ca_on_flow_through_share_expenses() -> None:
    assert (
        tax_calculator.registrations.CORE_PACKAGES
    )  # importing registrations imports the packages
    registered = CapabilityRegistry.shared().get("ca-on/flow_through_share_expenses")

    assert registered is FlowThroughShareExpenses


def test_its_package_declares_the_ca_on_namespace_and_exports_the_module() -> None:
    package = tax_calculator.jurisdictions.ca_on.capabilities

    assert package.NAMESPACE == tax_calculator.jurisdictions.ca_on.NAMESPACE == "ca-on"
    assert "flow_through_share_expenses" in package.__all__
    assert package.flow_through_share_expenses.FlowThroughShareExpenses is FlowThroughShareExpenses


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({FLOW_THROUGH_SHARE_SLIPS})
    assert capability().produces == frozenset({FLOW_THROUGH_SHARE_EXPENSES})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(FlowThroughShareExpenses)
    assert "produces" not in vars(FlowThroughShareExpenses)


def test_declares_its_slots() -> None:
    assert FlowThroughShareExpenses.PARAMETERS == {}
    assert FlowThroughShareExpenses.CONSUMES == {"slips": RecordList}
    assert FlowThroughShareExpenses.PRODUCES == {"output": Decimal}
    assert not FlowThroughShareExpenses.is_list_slot("slips")


def test_its_slots_are_read_only() -> None:
    for slots in (
        FlowThroughShareExpenses.PARAMETERS,
        FlowThroughShareExpenses.CONSUMES,
        FlowThroughShareExpenses.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)
        assert isinstance(slots, Mapping)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        FlowThroughShareExpenses(  # type: ignore[call-arg]
            FLOW_THROUGH_SHARE_SLIPS, FLOW_THROUGH_SHARE_EXPENSES, object()
        )


def test_rejects_a_money_kind_for_its_slips() -> None:
    other = ArtifactKind("ex/not_a_list", Decimal)

    with pytest.raises(InvalidCapabilityError, match="FlowThroughShareExpenses.*'slips'"):
        FlowThroughShareExpenses(slips=other, output=FLOW_THROUGH_SHARE_EXPENSES)  # type: ignore[arg-type]


def test_rejects_a_record_list_kind_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="FlowThroughShareExpenses.*'output'"):
        FlowThroughShareExpenses(slips=FLOW_THROUGH_SHARE_SLIPS, output=FLOW_THROUGH_SHARE_SLIPS)  # type: ignore[arg-type]


# --- computing --------------------------------------------------------------------------------


def test_an_empty_list_totals_zero() -> None:
    assert total_of() == D("0")


def test_one_slip_is_its_own_total() -> None:
    assert total_of("6000") == D("6000")


def test_two_slips_add_up_to_line_4() -> None:
    # The ticket's worked figures: expenses of 6,000 and 4,000 from two corporations.
    assert total_of("6000", "4000") == D("10000")


def test_three_slips_add_up() -> None:
    assert total_of("6000", "4000", "2500.75") == D("12500.75")


def test_a_zero_slip_adds_nothing() -> None:
    assert total_of("0", "4000") == D("4000")


def test_equal_slips_are_each_counted() -> None:
    assert total_of("6000", "6000") == D("12000")


def test_the_total_is_exact_and_never_rounded_to_the_cent() -> None:
    # 0.001 + 0.002 = 0.003 and 1000.005 + 0.001 = 1000.006: a sum has no dataset, so no rounding.
    assert total_of("0.001", "0.002") == D("0.003")
    assert str(total_of("1000.005", "0.001")) == "1000.006"


def test_the_total_is_exact_beyond_a_binary_float() -> None:
    assert total_of("0.1", "0.2") == D("0.3")


def test_the_total_does_not_depend_on_the_order_of_the_slips() -> None:
    assert total_of("4000", "6000") == total_of("6000", "4000")


def test_produces_one_artifact_of_the_output_kind() -> None:
    result = capability().compute((slips("6000", "4000"),))

    assert result.outputs == (Artifact(FLOW_THROUGH_SHARE_EXPENSES, D("10000")),)


def test_records_one_trace_line_naming_each_amount_in_order() -> None:
    result = capability().compute((slips("6000", "4000"),))

    assert result.trace == (
        RecordTotalLine(
            FLOW_THROUGH_SHARE_EXPENSES,
            FLOW_THROUGH_SHARE_SLIP_EXPENSES,
            (D("6000"), D("4000")),
            D("10000"),
        ),
    )


def test_records_one_trace_line_for_an_empty_list() -> None:
    result = capability().compute((slips(),))

    assert result.trace == (
        RecordTotalLine(FLOW_THROUGH_SHARE_EXPENSES, FLOW_THROUGH_SHARE_SLIP_EXPENSES, (), D("0")),
    )


def test_records_one_trace_line_whatever_the_number_of_slips() -> None:
    for amounts in ((), ("1",), ("1", "2"), ("1", "2", "3", "4")):
        assert len(capability().compute((slips(*amounts),)).trace) == 1


def test_the_trace_keeps_the_callers_order_not_the_sorted_one() -> None:
    result = capability().compute((slips("4000", "6000"),))

    (line,) = result.trace
    assert isinstance(line, RecordTotalLine)
    assert line.amounts == (D("4000"), D("6000"))


def test_its_trace_reads_item_by_item_in_english() -> None:
    result = capability().compute((slips("6000", "4000"),))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "flow_through_share_expenses: item 1 flow_through_share_slip_expenses 6000 "
        "+ item 2 flow_through_share_slip_expenses 4000 = 10000",
    )


def test_its_trace_for_an_empty_list_says_no_items() -> None:
    result = capability().compute((slips(),))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "flow_through_share_expenses: no items = 0",
    )


def test_needs_its_slips() -> None:
    with pytest.raises(MissingArtifactError, match="FlowThroughShareExpenses"):
        capability().compute(())


def test_does_not_consume_anything_else() -> None:
    other = Artifact(ArtifactKind("ex/other", Decimal), D("1"))

    result = capability().compute((other, slips("6000")))

    assert result.outputs == (Artifact(FLOW_THROUGH_SHARE_EXPENSES, D("6000")),)
