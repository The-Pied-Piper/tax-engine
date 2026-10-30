"""Unit tests for the ApprenticeshipWagesTotal capability (`ca/apprenticeship_wages_total`).

Form T2038(IND) 2025, Part B, Table 1 "Calculation of total Apprenticeship job creation tax credit":
one row for each apprentice, column 3 "The lesser of eligible salary and wages** payable in the year
or $20,000." The credit is 10% of the total of column 3; that multiplication is not this capability.

Its slots: one parameter slot `maximum` (an `amount` dataset, 20,000), one consumed slot
`apprentices` (a record list whose records hold each apprentice's eligible salary and wages) and
one produced slot `output`. Each apprentice is worked on its own, never pooled: the amount is the
lesser of that apprentice's salary and wages and the `maximum`, rounded once with the `maximum`
dataset's rule, and the output is the total of those amounts, 0 for an empty list. It records one
`ApprenticeWagesLine` per apprentice, then an `ItemsTotalLine`.
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
from tax_engine.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.capabilities.apprenticeship_wages_total import (
    ApprenticeshipWagesTotal,
)
from tax_engine.jurisdictions.ca.catalog import (
    ITC_APPRENTICE_SALARY_AND_WAGES,
    ITC_APPRENTICES,
    ITC_APPRENTICESHIP_WAGES_TOTAL,
)
from tax_engine.jurisdictions.ca.trace import ApprenticeWagesLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


def amount(family: str, value: str, rounding: RoundingRule = CENT) -> ParameterDataset[Amount]:
    return ParameterDataset(
        family, 2025, AMOUNT, Amount(D(value)), rounding, ("https://example.org/t2038",)
    )


def capability(maximum: ParameterDataset[Amount] | None = None) -> ApprenticeshipWagesTotal:
    """By default the 2025 figure: the maximum 20,000, to the cent."""
    return ApprenticeshipWagesTotal(
        maximum or amount("ca/itc_apprentice_wages_maximum", "20000"),
        ITC_APPRENTICES,
        ITC_APPRENTICESHIP_WAGES_TOTAL,
    )


def apprentices(*salaries: str) -> Artifact[Any]:
    """An `ca/itc_apprentices` artifact of one record per salary and wages, in the order given."""
    records = [{ITC_APPRENTICE_SALARY_AND_WAGES: D(salary)} for salary in salaries]
    return Artifact(ITC_APPRENTICES, RecordList(ITC_APPRENTICES.fields, records))


def compute(wired: ApprenticeshipWagesTotal, *salaries: str) -> Artifact[Any]:
    (output,) = wired.compute((apprentices(*salaries),)).outputs
    return output


def total(*salaries: str) -> Decimal:
    value = compute(capability(), *salaries).value
    assert isinstance(value, Decimal)
    return value


def test_is_registered_as_ca_apprenticeship_wages_total() -> None:
    assert CapabilityRegistry.shared().get("ca/apprenticeship_wages_total") is (
        ApprenticeshipWagesTotal
    )


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert ca_capabilities.NAMESPACE == "ca"
    assert "apprenticeship_wages_total" in ca_capabilities.__all__
    assert (
        ca_capabilities.apprenticeship_wages_total.ApprenticeshipWagesTotal
        is ApprenticeshipWagesTotal
    )


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({ITC_APPRENTICES})
    assert capability().produces == frozenset({ITC_APPRENTICESHIP_WAGES_TOTAL})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(ApprenticeshipWagesTotal)
    assert "produces" not in vars(ApprenticeshipWagesTotal)


def test_declares_its_slots() -> None:
    assert ApprenticeshipWagesTotal.PARAMETERS == {"maximum": AMOUNT}
    assert ApprenticeshipWagesTotal.CONSUMES == {"apprentices": RecordList}
    assert ApprenticeshipWagesTotal.PRODUCES == {"output": Decimal}
    assert not ApprenticeshipWagesTotal.is_list_slot("apprentices")


def test_its_slots_are_read_only() -> None:
    for slots in (
        ApprenticeshipWagesTotal.PARAMETERS,
        ApprenticeshipWagesTotal.CONSUMES,
        ApprenticeshipWagesTotal.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(ApprenticeshipWagesTotal.PARAMETERS, Mapping[str, ParameterKind[Amount]])
    assert_type(ApprenticeshipWagesTotal.CONSUMES, Mapping[str, type])
    assert_type(ApprenticeshipWagesTotal.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (
        ApprenticeshipWagesTotal.PARAMETERS,
        ApprenticeshipWagesTotal.CONSUMES,
        ApprenticeshipWagesTotal.PRODUCES,
    ):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = ApprenticeshipWagesTotal(
        maximum=amount("ca/itc_apprentice_wages_maximum", "20000"),
        apprentices=ITC_APPRENTICES,
        output=ITC_APPRENTICESHIP_WAGES_TOTAL,
    )

    assert compute(wired, "25000") == Artifact(ITC_APPRENTICESHIP_WAGES_TOTAL, D("20000.00"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        ApprenticeshipWagesTotal(  # type: ignore[call-arg]
            amount("ca/itc_apprentice_wages_maximum", "20000"),
            ITC_APPRENTICES,
            ITC_APPRENTICESHIP_WAGES_TOTAL,
            CENT,
        )


def test_rejects_a_money_kind_for_its_apprentices() -> None:
    with pytest.raises(InvalidCapabilityError, match="ApprenticeshipWagesTotal.*'apprentices'"):
        ApprenticeshipWagesTotal(
            amount("ca/itc_apprentice_wages_maximum", "20000"),
            ITC_APPRENTICESHIP_WAGES_TOTAL,  # type: ignore[arg-type]
            ITC_APPRENTICESHIP_WAGES_TOTAL,
        )


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(ApprenticeshipWagesTotal, "__type_params__", ())
    assert not getattr(ApprenticeshipWagesTotal, "__parameters__", ())


# --- computing: how many apprentices ------------------------------------------------------------


def test_no_apprentices_give_zero() -> None:
    output = compute(capability())

    assert output == Artifact(ITC_APPRENTICESHIP_WAGES_TOTAL, D("0"))
    assert type(output.value) is Decimal
    assert not output.value.is_signed()


def test_one_apprentice_under_the_maximum_gives_the_salary_and_wages() -> None:
    # Column 3: the lesser of 15,000 and 20,000 is 15,000.
    assert total("15000") == D("15000.00")


def test_one_apprentice_over_the_maximum_gives_the_maximum() -> None:
    # Column 3: the lesser of 25,000 and 20,000 is 20,000.
    assert total("25000") == D("20000.00")


def test_an_apprentice_at_the_maximum_gives_the_maximum() -> None:
    assert total("20000") == D("20000.00")
    assert total("20000.01") == D("20000.00")


def test_an_apprentice_with_no_salary_and_wages_gives_plain_zero() -> None:
    output = compute(capability(), "0")

    assert output.value == D("0")
    assert not output.value.is_signed()


def test_two_apprentices_give_the_sum_of_their_own_amounts_not_the_pooled_figure() -> None:
    # 20,000 + 15,000 = 35,000; pooled, the 40,000 of salary and wages would be capped at 20,000.
    assert total("25000", "15000") == D("35000.00")
    assert total("25000", "15000") != D("20000.00")


def test_three_apprentices_are_summed_one_by_one() -> None:
    # 20,000 + 20,000 + 5,000 = 45,000.
    assert total("25000", "25000", "5000") == D("45000.00")


def test_the_total_does_not_depend_on_the_order() -> None:
    assert total("25000", "5000") == total("5000", "25000")


def test_an_apprentice_with_no_salary_and_wages_adds_nothing_to_the_others() -> None:
    assert total("0", "15000") == D("15000.00")


# --- computing: the datasets --------------------------------------------------------------------


def test_the_maximum_dataset_supplies_the_maximum() -> None:
    wired = capability(maximum=amount("ca/itc_apprentice_wages_maximum", "1000"))

    assert compute(wired, "5000").value == D("1000.00")
    assert compute(wired, "500").value == D("500.00")


def test_a_different_year_figure_changes_the_result() -> None:
    wired = capability(maximum=amount("ca/itc_apprentice_wages_maximum", "21000"))

    assert compute(wired, "25000", "5000").value == D("26000.00")


# --- computing: rounding ------------------------------------------------------------------------


def test_each_amount_is_rounded_half_up_to_the_cent_before_they_are_summed() -> None:
    # Per apprentice: 10,000.005 -> 10,000.01, twice: 20,000.02. Rounding only the exact total,
    # 20,000.01, would be wrong.
    assert total("10000.005", "10000.005") == D("20000.02")


def test_a_single_salary_and_wages_is_rounded_half_up() -> None:
    assert total("15000.005") == D("15000.01")
    assert total("15000.004") == D("15000.00")


def test_the_rounding_rule_comes_from_the_maximum_dataset() -> None:
    wired = capability(
        maximum=amount(
            "ca/itc_apprentice_wages_maximum", "20000", RoundTo(D("1"), RoundingMode.FLOOR)
        )
    )

    # 15,000.5, floored to the dollar: 15,000.
    assert compute(wired, "15000.5").value == D("15000")


def test_the_maximum_is_rounded_with_the_rule_too() -> None:
    wired = capability(maximum=amount("ca/itc_apprentice_wages_maximum", "20000.005"))

    assert compute(wired, "25000").value == D("20000.01")


def test_a_rounded_amount_carries_the_increments_scale() -> None:
    assert str(compute(capability(), "15000").value) == "15000.00"
    assert str(compute(capability(), "25000").value) == "20000.00"


def test_rounding_without_a_rule_keeps_every_figure() -> None:
    wired = capability(maximum=amount("ca/itc_apprentice_wages_maximum", "20000", NO_ROUNDING))

    assert compute(wired, "15000.005").value == D("15000.005")


# --- computing: inputs --------------------------------------------------------------------------


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(ITC_APPRENTICE_SALARY_AND_WAGES, D("9"))

    result = capability().compute((other, apprentices("15000")))

    assert result.outputs == (Artifact(ITC_APPRENTICESHIP_WAGES_TOTAL, D("15000.00")),)


def test_missing_apprentices_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="itc_apprentices"):
        capability().compute(())


def test_has_one_output() -> None:
    assert len(capability().compute((apprentices("1", "2"),)).outputs) == 1


# --- trace --------------------------------------------------------------------------------------


def claim(
    position: int,
    salary: str,
    result: str,
    rounding: RoundingRule = CENT,
) -> ApprenticeWagesLine:
    return ApprenticeWagesLine(
        output=ITC_APPRENTICESHIP_WAGES_TOTAL,
        position=position,
        salary_and_wages=D(salary),
        maximum=Amount(D("20000")),
        rounding=rounding,
        result=D(result),
    )


def test_traces_one_line_per_apprentice_then_the_total() -> None:
    trace = capability().compute((apprentices("25000", "15000"),)).trace

    assert trace == (
        claim(1, "25000", "20000.00"),
        claim(2, "15000", "15000.00"),
        ItemsTotalLine(
            ITC_APPRENTICESHIP_WAGES_TOTAL,
            ((1, D("20000.00")), (2, D("15000.00"))),
            D("35000.00"),
        ),
    )


def test_traces_the_callers_order_with_positions_from_one() -> None:
    trace = capability().compute((apprentices("15000", "25000", "0"),)).trace

    assert trace == (
        claim(1, "15000", "15000.00"),
        claim(2, "25000", "20000.00"),
        claim(3, "0", "0.00"),
        ItemsTotalLine(
            ITC_APPRENTICESHIP_WAGES_TOTAL,
            ((1, D("15000.00")), (2, D("20000.00")), (3, D("0.00"))),
            D("35000.00"),
        ),
    )


def test_traces_one_apprentice_as_a_line_and_a_total() -> None:
    trace = capability().compute((apprentices("25000"),)).trace

    assert trace == (
        claim(1, "25000", "20000.00"),
        ItemsTotalLine(ITC_APPRENTICESHIP_WAGES_TOTAL, ((1, D("20000.00")),), D("20000.00")),
    )


def test_traces_no_apprentices_as_only_an_empty_total() -> None:
    trace = capability().compute((apprentices(),)).trace

    assert trace == (ItemsTotalLine(ITC_APPRENTICESHIP_WAGES_TOTAL, (), D("0")),)


def test_traces_the_maximum_datasets_amount_and_rounding_rule() -> None:
    wired = capability(
        maximum=amount(
            "ca/itc_apprentice_wages_maximum", "20000", RoundTo(D("1"), RoundingMode.FLOOR)
        )
    )

    (line, _) = wired.compute((apprentices("15000.5"),)).trace

    assert isinstance(line, ApprenticeWagesLine)
    assert line.maximum == Amount(D("20000"))
    assert line.rounding == RoundTo(D("1"), RoundingMode.FLOOR)
    assert line.salary_and_wages == D("15000.5")
    assert line.result == D("15000")


def test_the_last_trace_line_amount_is_the_output() -> None:
    result = capability().compute((apprentices("25000", "15000"),))

    (output,) = result.outputs
    assert result.trace[-1].amount == output.value
    assert [line.amount for line in result.trace[:-1]] == [D("20000.00"), D("15000.00")]


def test_the_total_is_the_sum_of_its_items() -> None:
    *_, total_line = capability().compute((apprentices("25000", "15000", "1"),)).trace

    assert isinstance(total_line, ItemsTotalLine)
    assert total_line.total == sum((amount for _, amount in total_line.items), D("0"))


def test_compute_is_repeatable() -> None:
    wired = capability()
    given = (apprentices("25000", "15000"),)

    assert wired.compute(given) == wired.compute(given)
