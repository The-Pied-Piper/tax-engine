"""Unit tests for the OntarioCappedRecordTotal capability (`ca-on/capped_record_total`).

Form ON428 line 23 and line 58330 "Adoption expenses", with T2203 note (5): "If you were a resident
of Ontario, you can claim up to $15,551 of eligible expenses for each child in the year the
adoption is finalized or recognized under Ontario law." Each child's eligible expenses (a field of
each record in the consumed record list, the same list the federal line 31300 reads) are capped at
the `cap` dataset's amount, and the capped amounts are added up. The cap is the filer's share of the
expenses, so a split between two adoptive parents is already in each record.

Its slots: one parameter slot `cap` (an `amount` dataset), one consumed slot `records` (a record
list whose kind has exactly one field, an amount) and one produced slot `output`. Each child is
worked on its own, never pooled with the others: the child's amount is capped at the `cap`
dataset's amount and rounded once with the `cap` dataset's rule. It records one
`CappedRecordLine` per child, by position from 1, then an `ItemsTotalLine`; with no children the
output is 0 and the only trace line is the total. A record list of more than one field, or whose
one field is not an amount, is refused when the capability is built.
A missing records artifact is refused when it is computed.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.jurisdictions.ca_on.capabilities as ca_on_capabilities
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
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.catalog import (
    ADOPTION_CHILD_EXPENSES,
    ADOPTION_EXPENSE_CHILDREN,
)
from tax_calculator.jurisdictions.ca_on.capabilities.capped_record_total import (
    OntarioCappedRecordTotal,
)
from tax_calculator.jurisdictions.ca_on.catalog import ADOPTION_CREDIT
from tax_calculator.jurisdictions.ca_on.trace import CappedRecordLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
WHOLE_DOLLAR_DOWN = RoundTo(D("1"), RoundingMode.FLOOR)
COUNT = ArtifactKind("ex/child_count", int)
TWO_AMOUNTS = RecordListKind("ex/two_amounts", fields=(ADOPTION_CHILD_EXPENSES, COUNT))
COUNT_ONLY = RecordListKind("ex/child_counts", fields=(COUNT,))
UNRELATED = ArtifactKind("ex/unrelated", Decimal)


def amount(family: str, value: str, rounding: RoundingRule = CENT) -> ParameterDataset[Amount]:
    return ParameterDataset(
        family, 2025, AMOUNT, Amount(D(value)), rounding, ("https://example.org/on428-worksheet",)
    )


def capability(cap: ParameterDataset[Amount] | None = None) -> OntarioCappedRecordTotal:
    """By default the 2025 figure: the cap of 15,551 on each child, to the cent."""
    return OntarioCappedRecordTotal(
        cap or amount("ca-on/adoption_expenses_maximum", "15551"),
        ADOPTION_EXPENSE_CHILDREN,
        ADOPTION_CREDIT,
    )


def children(*expenses: str) -> Artifact[Any]:
    """An `ca/adoption_expense_children` artifact of one record per expense, in order."""
    records: list[dict[ArtifactKind[Any], object]] = [
        {ADOPTION_CHILD_EXPENSES: D(expense)} for expense in expenses
    ]
    return Artifact(
        ADOPTION_EXPENSE_CHILDREN, RecordList(ADOPTION_EXPENSE_CHILDREN.fields, records)
    )


def compute(wired: OntarioCappedRecordTotal, *expenses: str) -> Artifact[Any]:
    (output,) = wired.compute((children(*expenses),)).outputs
    return output


def total(*expenses: str, cap: ParameterDataset[Amount] | None = None) -> Decimal:
    value = compute(capability(cap), *expenses).value
    assert isinstance(value, Decimal)
    return value


def test_is_registered_as_ca_on_capped_record_total() -> None:
    assert CapabilityRegistry.shared().get("ca-on/capped_record_total") is OntarioCappedRecordTotal


def test_is_exported_from_the_ca_on_capabilities_package() -> None:
    assert ca_on_capabilities.NAMESPACE == "ca-on"
    assert "capped_record_total" in ca_on_capabilities.__all__
    assert (
        ca_on_capabilities.capped_record_total.OntarioCappedRecordTotal is OntarioCappedRecordTotal
    )


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({ADOPTION_EXPENSE_CHILDREN})
    assert capability().produces == frozenset({ADOPTION_CREDIT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(OntarioCappedRecordTotal)
    assert "produces" not in vars(OntarioCappedRecordTotal)


def test_declares_its_slots() -> None:
    assert OntarioCappedRecordTotal.PARAMETERS == {"cap": AMOUNT}
    assert OntarioCappedRecordTotal.CONSUMES == {"records": RecordList}
    assert OntarioCappedRecordTotal.PRODUCES == {"output": Decimal}
    assert not OntarioCappedRecordTotal.is_list_slot("records")


def test_its_slots_are_read_only() -> None:
    for slots in (
        OntarioCappedRecordTotal.PARAMETERS,
        OntarioCappedRecordTotal.CONSUMES,
        OntarioCappedRecordTotal.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(OntarioCappedRecordTotal.PARAMETERS, Mapping[str, ParameterKind[Amount]])
    assert_type(OntarioCappedRecordTotal.CONSUMES, Mapping[str, type])
    assert_type(OntarioCappedRecordTotal.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (
        OntarioCappedRecordTotal.PARAMETERS,
        OntarioCappedRecordTotal.CONSUMES,
        OntarioCappedRecordTotal.PRODUCES,
    ):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = OntarioCappedRecordTotal(
        cap=amount("ca-on/adoption_expenses_maximum", "15551"),
        records=ADOPTION_EXPENSE_CHILDREN,
        output=ADOPTION_CREDIT,
    )

    assert compute(wired, "20000") == Artifact(ADOPTION_CREDIT, D("15551"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        OntarioCappedRecordTotal(  # type: ignore[call-arg]
            amount("ca-on/adoption_expenses_maximum", "15551"),
            ADOPTION_EXPENSE_CHILDREN,
            ADOPTION_CREDIT,
            CENT,
        )


def test_rejects_an_amount_kind_for_its_records() -> None:
    with pytest.raises(InvalidCapabilityError, match="OntarioCappedRecordTotal.*'records'"):
        OntarioCappedRecordTotal(
            amount("ca-on/adoption_expenses_maximum", "15551"),
            ADOPTION_CHILD_EXPENSES,  # type: ignore[arg-type]
            ADOPTION_CREDIT,
        )


def test_rejects_a_list_kind_of_more_than_one_field() -> None:
    with pytest.raises(InvalidCapabilityError, match="OntarioCappedRecordTotal.*'records'"):
        OntarioCappedRecordTotal(
            amount("ca-on/adoption_expenses_maximum", "15551"), TWO_AMOUNTS, ADOPTION_CREDIT
        )


def test_rejects_a_list_kind_whose_one_field_is_a_count() -> None:
    with pytest.raises(InvalidCapabilityError, match="OntarioCappedRecordTotal.*'records'"):
        OntarioCappedRecordTotal(
            amount("ca-on/adoption_expenses_maximum", "15551"), COUNT_ONLY, ADOPTION_CREDIT
        )


def test_no_children_give_zero() -> None:
    assert total() == 0


def test_no_children_give_zero_as_an_output_of_the_output_kind() -> None:
    assert compute(capability()) == Artifact(ADOPTION_CREDIT, D("0"))


def test_a_child_under_the_maximum_is_its_own_expenses() -> None:
    assert total("8000") == D("8000")


def test_a_child_with_expenses_at_the_maximum_is_the_maximum() -> None:
    assert total("15551") == D("15551")


def test_a_child_over_the_maximum_is_capped_at_15551() -> None:
    assert total("20000") == D("15551")


def test_two_children_give_the_sum_of_their_own_capped_amounts_not_the_pooled_figure() -> None:
    # 10,000 + 15,551 (the second child's 20,000 capped), not 15,551 for both pooled.
    assert total("10000", "20000") == D("25551")


def test_three_children_are_summed_one_by_one() -> None:
    assert total("8000", "20000", "30000") == D("39102")


def test_the_total_does_not_depend_on_the_order() -> None:
    assert total("20000", "8000") == total("8000", "20000") == D("23551")


def test_a_child_with_no_expenses_adds_nothing_to_the_others() -> None:
    assert total("0", "20000") == D("15551")


def test_exact_cents_are_added_exactly() -> None:
    assert total("8000.25", "20000.75") == D("23551.25")


def test_produces_one_artifact_of_the_output_kind() -> None:
    (output,) = capability().compute((children("8000"),)).outputs

    assert output.kind is ADOPTION_CREDIT


def test_a_child_over_the_maximum_is_capped_at_the_cap_datasets_amount() -> None:
    wired = capability(amount("ca-on/adoption_expenses_maximum", "9000"))

    assert compute(wired, "20000") == Artifact(ADOPTION_CREDIT, D("9000"))


def test_a_child_is_rounded_half_up_to_the_cent() -> None:
    assert total("8000.005") == D("8000.01")


def test_a_capped_child_gives_the_cap_exactly() -> None:
    assert total("20000.005") == D("15551")


def test_the_rounding_rule_comes_from_the_cap_dataset() -> None:
    assert total(
        "8000.99", cap=amount("ca-on/adoption_expenses_maximum", "15551", WHOLE_DOLLAR_DOWN)
    ) == (D("8000"))


def test_no_rounding_keeps_a_child_to_its_exact_expenses() -> None:
    assert total(
        "8000.005", cap=amount("ca-on/adoption_expenses_maximum", "15551", NO_ROUNDING)
    ) == (D("8000.005"))


def test_the_rounding_is_done_once_per_child_before_they_are_summed() -> None:
    assert total("8000.005", "8000.005") == D("16000.02")


def test_the_cap_is_rounded_with_the_rule_too() -> None:
    assert total("20000", cap=amount("ca-on/adoption_expenses_maximum", "15551.005")) == D(
        "15551.01"
    )


def test_ignores_artifacts_it_does_not_consume() -> None:
    unrelated = Artifact(UNRELATED, D("1"))

    (output,) = capability().compute((unrelated, children("8000"))).outputs

    assert output == Artifact(ADOPTION_CREDIT, D("8000"))


def test_takes_its_inputs_in_any_order() -> None:
    (output,) = capability().compute((Artifact(UNRELATED, D("1")), children("8000"))).outputs

    assert output == Artifact(ADOPTION_CREDIT, D("8000"))


def test_missing_children_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError):
        capability().compute(())


def test_traces_one_line_per_child_then_the_items_total() -> None:
    result = capability().compute((children("8000", "20000"),))

    assert len(result.trace) == 3
    assert isinstance(result.trace[0], CappedRecordLine)
    assert isinstance(result.trace[1], CappedRecordLine)
    assert isinstance(result.trace[2], ItemsTotalLine)


def test_traces_each_child_by_its_position_from_one() -> None:
    result = capability().compute((children("8000", "20000"),))

    assert result.trace[0] == CappedRecordLine(
        ADOPTION_CREDIT,
        1,
        D("8000"),
        Amount(D("15551")),
        CENT,
        D("8000"),
    )
    assert result.trace[1] == CappedRecordLine(
        ADOPTION_CREDIT,
        2,
        D("20000"),
        Amount(D("15551")),
        CENT,
        D("15551"),
    )


def test_the_items_total_names_each_capped_amount_by_position_and_the_total() -> None:
    result = capability().compute((children("8000", "20000"),))

    assert result.trace[-1] == ItemsTotalLine(
        ADOPTION_CREDIT, ((1, D("8000")), (2, D("15551"))), D("23551")
    )


def test_the_trace_is_in_the_callers_order() -> None:
    result = capability().compute((children("20000", "8000"),))

    first, second = result.trace[:2]
    assert isinstance(first, CappedRecordLine)
    assert isinstance(second, CappedRecordLine)
    assert [first.expenditure, second.expenditure] == [D("20000"), D("8000")]
    assert [first.position, second.position] == [1, 2]


def test_the_trace_records_the_cap_dataset_and_its_rule() -> None:
    result = capability().compute((children("20000"),))

    (line, _total) = result.trace
    assert isinstance(line, CappedRecordLine)
    assert line.cap == Amount(D("15551"))
    assert line.rounding == CENT


def test_the_last_trace_line_total_is_the_output() -> None:
    result = capability().compute((children("8000", "20000"),))
    (output,) = result.outputs

    assert result.trace[-1] == ItemsTotalLine(
        ADOPTION_CREDIT, ((1, D("8000")), (2, D("15551"))), output.value
    )


def test_traces_no_children_as_only_the_items_total() -> None:
    result = capability().compute((children(),))

    assert result.trace == (ItemsTotalLine(ADOPTION_CREDIT, (), D("0")),)


def test_compute_is_repeatable() -> None:
    wired = capability()

    assert wired.compute((children("20000"),)) == wired.compute((children("20000"),))
