"""Unit tests for the T2017ReserveTotalForPeriod capability (`ca/t2017_reserve_total_for_period`).

Form T657 asks, for each year or period of disposition it has a chart for, for "Amount from line 6
of Form T2017 (do not include reserves from dispositions of QFFP in any year other than 2016)" and,
for QSBCS, line 12. Line 6 is "Line 1 minus line 5": for the dispositions of one year it is the
total, over those dispositions, of each one's 2024 reserve less its 2025 reserve. Its slots: one
parameter slot `conditions` (a `conditions` dataset that says which dispositions the chart takes,
reading four counts of each record in this order: 1 the years after the disposition, 2 disposed of
in Period 1 of 2024, 3 reserve reported on a T5013 slip or letter, 4 partnership year began before
June 25, 2024), two consumed list slots, `rows`
(the record lists of the dispositions) and `amounts` (the reserve change of each record, one list
for each list of rows, at the same positions), and one produced slot `total` (a kind of
`Decimal`).

It records one `ReserveRowForPeriodLine` for each disposition of each list, named by the list's
position and its own from 1, and then one `ItemsTotalLine` of the amounts of the dispositions
counted. Nothing is rounded.

The artifact kinds of the totals and the dataset family are made up; the figures are chosen and
worked by hand.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import (
    InvalidCapabilityError,
    MissingArtifactError,
    ValidationError,
)
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.capabilities.t2017_reserve_total_for_period import (
    T2017ReserveTotalForPeriod,
)
from tax_engine.jurisdictions.ca.catalog import (
    T2017_LINE_2_RESERVE_ROWS,
    T2017_LINE_3_RESERVE_ROWS,
    T2017_LINE_17_RESERVE_ROWS,
    T2017_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END,
    T2017_RESERVE_CAPITAL_GAIN,
    T2017_RESERVE_CLAIMED,
    T2017_RESERVE_NINE_YEAR,
    T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024,
    T2017_RESERVE_PERIOD_1_OF_2024,
    T2017_RESERVE_PREVIOUS_YEAR_CLAIM,
    T2017_RESERVE_PROCEEDS,
    T2017_RESERVE_REPORTED_ON_SLIP,
    T2017_RESERVE_YEARS_AFTER_DISPOSITION,
    T2017_ROW_CHANGE,
    T2017_ROW_RESERVE,
)
from tax_engine.jurisdictions.ca.trace.gains import ReserveRowForPeriodLine

D = Decimal

# Made up for this test and not registered: the total the capability produces.
TOTAL = ArtifactKind("ex/t2017_total", Decimal)

CHANGES_2 = RecordListKind("ex/t2017_line_2_reserve.t2017_row_change", fields=(T2017_ROW_CHANGE,))
CHANGES_3 = RecordListKind("ex/t2017_line_3_reserve.t2017_row_change", fields=(T2017_ROW_CHANGE,))


def condition(*parts: tuple[int, str]) -> Condition:
    """One condition whose parts all hold: each (position, figure) is a count equal to a figure."""
    return Condition(
        "taken",
        tuple(
            ConditionPart((ConditionTest("count", position, "equal_to", D(figure), None),))
            for position, figure in parts
        ),
    )


def dataset(*conditions: Condition, when_any: int = 1) -> ParameterDataset[ConditionList]:
    return ParameterDataset(
        "ex/disposed_in",
        2025,
        CONDITIONS,
        ConditionList(when_any, conditions),
        NO_ROUNDING,
        ("https://example.org/conditions",),
    )


# Chart 2019: the dispositions of 2019, 6 years after.
IN_2019 = dataset(condition((1, "6")))
# Chart 2024 Period 1 and Chart 2025 Part 1: 1 year after, Period 1 of 2024, on a T5013 slip.
PERIOD_1 = dataset(condition((1, "1"), (2, "1")))
PERIOD_1_ON_SLIP = dataset(condition((1, "1"), (2, "1"), (3, "1")))
# Guide T4037: a Period 1 reserve a partnership reports is Chart 2025 Part 1 when its fiscal period
# began before June 25, 2024 and Chart 2024 Period 1 when it began after; one not on a slip is
# Chart 2024 Period 1.
PERIOD_1_CHART_2024 = dataset(
    condition((1, "1"), (2, "1"), (3, "0")), condition((1, "1"), (2, "1"), (4, "0"))
)
PERIOD_1_CHART_2025_PART_1 = dataset(condition((1, "1"), (2, "1"), (3, "1"), (4, "1")))


def row(years: int, period_1: int = 0, slip: int = 0, before: int = 0) -> dict[Any, Any]:
    return {
        T2017_RESERVE_CAPITAL_GAIN: D("100000"),
        T2017_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END: D("0"),
        T2017_RESERVE_PROCEEDS: D("100000"),
        T2017_RESERVE_YEARS_AFTER_DISPOSITION: years,
        T2017_RESERVE_CLAIMED: D("0"),
        T2017_RESERVE_PREVIOUS_YEAR_CLAIM: D("0"),
        T2017_RESERVE_PERIOD_1_OF_2024: period_1,
        T2017_RESERVE_REPORTED_ON_SLIP: slip,
        T2017_RESERVE_PARTNERSHIP_YEAR_BEGAN_BEFORE_JUNE_25_2024: before,
        T2017_RESERVE_NINE_YEAR: 1,
    }


def rows_of(kind: RecordListKind, *records: dict[Any, Any]) -> Artifact[Any]:
    return Artifact(
        kind,
        RecordList(
            kind.fields,
            [{field: record[field] for field in kind.fields} for record in records],
        ),
    )


def changes_of(kind: RecordListKind, *amounts: str) -> Artifact[Any]:
    return Artifact(
        kind, RecordList(kind.fields, [{T2017_ROW_CHANGE: D(each)} for each in amounts])
    )


def capability(
    conditions: ParameterDataset[ConditionList] = IN_2019,
) -> T2017ReserveTotalForPeriod:
    return T2017ReserveTotalForPeriod(
        conditions,
        (T2017_LINE_2_RESERVE_ROWS, T2017_LINE_3_RESERVE_ROWS),
        (CHANGES_2, CHANGES_3),
        TOTAL,
    )


def inputs(
    rows_2: list[dict[Any, Any]],
    changes_2: list[str],
    rows_3: list[dict[Any, Any]],
    changes_3: list[str],
) -> tuple[Artifact[Any], ...]:
    return (
        rows_of(T2017_LINE_2_RESERVE_ROWS, *rows_2),
        changes_of(CHANGES_2, *changes_2),
        rows_of(T2017_LINE_3_RESERVE_ROWS, *rows_3),
        changes_of(CHANGES_3, *changes_3),
    )


def test_is_registered_as_ca_t2017_reserve_total_for_period() -> None:
    assert ca_capabilities.t2017_reserve_total_for_period is not None
    assert (
        CapabilityRegistry.shared().get("ca/t2017_reserve_total_for_period")
        is T2017ReserveTotalForPeriod
    )


def test_adds_the_change_of_the_dispositions_of_the_year_and_leaves_out_the_others() -> None:
    # Chart 2019 takes 6 years after: 2019 dispositions of 30,000 and 5,000.25; a 2020 disposition
    # (5 years after) of 7,000 is left out.
    result = capability().compute(
        inputs(
            [row(6), row(5)],
            ["30000", "7000"],
            [row(6)],
            ["5000.25"],
        )
    )

    assert result.outputs == (Artifact(TOTAL, D("35000.25")),)


def test_a_chart_that_takes_nothing_is_0() -> None:
    result = capability().compute(inputs([row(5)], ["7000"], [], []))

    assert result.outputs == (Artifact(TOTAL, D("0")),)


def test_no_dispositions_total_nothing() -> None:
    result = capability().compute(inputs([], [], [], []))

    assert result.outputs == (Artifact(TOTAL, D("0")),)
    assert result.trace == (ItemsTotalLine(output=TOTAL, items=(), total=D("0")),)


def test_a_change_below_zero_is_added_as_it_is() -> None:
    # A 2025 disposition: its 2024 reserve is 0 and its 2025 reserve 4,000, so the line is (4,000).
    in_2025 = dataset(condition((1, "0")))

    result = capability(in_2025).compute(inputs([row(0), row(0)], ["-4000", "-500"], [], []))

    assert result.outputs == (Artifact(TOTAL, D("-4500")),)


def test_period_1_takes_only_the_dispositions_answered_yes_to_period_1_of_2024() -> None:
    # 2024 dispositions (1 year after): Period 1 of 12,000 and Period 2 of 3,000.
    result = capability(PERIOD_1).compute(
        inputs([row(1, period_1=1), row(1, period_1=0)], ["12000", "3000"], [], [])
    )

    assert result.outputs == (Artifact(TOTAL, D("12000")),)


def test_the_t5013_chart_takes_only_the_reserves_reported_on_a_slip() -> None:
    result = capability(PERIOD_1_ON_SLIP).compute(
        inputs(
            [row(1, period_1=1, slip=1), row(1, period_1=1, slip=0)],
            ["12000", "3000"],
            [row(1, period_1=1, slip=1)],
            ["200"],
        )
    )

    assert result.outputs == (Artifact(TOTAL, D("12200")),)


def test_any_one_condition_takes_a_disposition() -> None:
    either = dataset(condition((1, "6")), condition((1, "5")))

    result = capability(either).compute(inputs([row(6), row(5), row(4)], ["1", "2", "4"], [], []))

    assert result.outputs == (Artifact(TOTAL, D("3")),)


def test_traces_each_disposition_then_the_total() -> None:
    result = capability().compute(inputs([row(6), row(5)], ["30000", "7000"], [row(6)], ["500"]))

    assert result.trace == (
        ReserveRowForPeriodLine(TOTAL, 1, 1, 6, 0, 0, 0, D("30000"), True),
        ReserveRowForPeriodLine(TOTAL, 1, 2, 5, 0, 0, 0, D("7000"), False),
        ReserveRowForPeriodLine(TOTAL, 2, 1, 6, 0, 0, 0, D("500"), True),
        ItemsTotalLine(TOTAL, ((1, D("30000")), (2, D("0")), (3, D("500"))), D("30500")),
    )
    assert result.trace[-1].amount == D("30500")
    assert result.trace[0].amount == D("30000")
    assert result.trace[1].amount == D("0")


def test_refuses_a_list_of_changes_with_another_number_of_records_than_its_rows() -> None:
    with pytest.raises(ValidationError, match="has 2 records but"):
        capability().compute(inputs([row(6), row(5)], ["30000"], [], []))


def test_needs_its_lists() -> None:
    with pytest.raises(MissingArtifactError):
        capability().compute(())


def test_compute_is_repeatable() -> None:
    given = inputs([row(6)], ["30000"], [row(6)], ["500"])

    assert capability().compute(given) == capability().compute(given)


def test_refuses_lists_that_are_not_paired() -> None:
    with pytest.raises(InvalidCapabilityError, match="one list of amounts for each"):
        T2017ReserveTotalForPeriod(IN_2019, (T2017_LINE_2_RESERVE_ROWS,), (), TOTAL)


def test_refuses_rows_without_the_counts() -> None:
    with pytest.raises(InvalidCapabilityError, match="lacks the field"):
        T2017ReserveTotalForPeriod(IN_2019, (T2017_LINE_17_RESERVE_ROWS,), (CHANGES_2,), TOTAL)


def test_refuses_amounts_that_are_not_one_amount() -> None:
    not_amounts = RecordListKind("ex/not_amounts", fields=(T2017_ROW_CHANGE, T2017_ROW_RESERVE))

    with pytest.raises(InvalidCapabilityError, match="exactly one amount field"):
        T2017ReserveTotalForPeriod(IN_2019, (T2017_LINE_2_RESERVE_ROWS,), (not_amounts,), TOTAL)


def test_refuses_conditions_that_read_a_count_beyond_the_fourth() -> None:
    fifth = dataset(condition((5, "1")))

    with pytest.raises(InvalidCapabilityError, match="counts 1 to 4"):
        T2017ReserveTotalForPeriod(fifth, (T2017_LINE_2_RESERVE_ROWS,), (CHANGES_2,), TOTAL)


def test_refuses_conditions_that_read_an_amount() -> None:
    amount_test = Condition(
        "taken", (ConditionPart((ConditionTest("amount", 1, "more_than", D("0"), None),)),)
    )

    with pytest.raises(InvalidCapabilityError, match="counts 1 to 4"):
        T2017ReserveTotalForPeriod(
            dataset(amount_test), (T2017_LINE_2_RESERVE_ROWS,), (CHANGES_2,), TOTAL
        )


def test_refuses_conditions_that_give_0_when_one_applies() -> None:
    with pytest.raises(InvalidCapabilityError, match="must give 1 when one applies"):
        T2017ReserveTotalForPeriod(
            dataset(condition((1, "6")), when_any=0),
            (T2017_LINE_2_RESERVE_ROWS,),
            (CHANGES_2,),
            TOTAL,
        )


def test_a_period_1_reserve_on_a_slip_is_in_one_chart_by_when_the_partnership_year_began() -> None:
    # Rows (1 year after, Period 1 of 2024): not on a slip 1,000; on a slip of a partnership year
    # that began before June 25, 2024 20,000; on a slip of a year that began after 300.
    rows = [
        row(1, period_1=1, slip=0),
        row(1, period_1=1, slip=1, before=1),
        row(1, period_1=1, slip=1, before=0),
    ]
    changes = ["1000", "20000", "300"]

    chart_2024 = capability(PERIOD_1_CHART_2024).compute(inputs(rows, changes, [], []))
    part_1 = capability(PERIOD_1_CHART_2025_PART_1).compute(inputs(rows, changes, [], []))

    assert chart_2024.outputs == (Artifact(TOTAL, D("1300")),)
    assert part_1.outputs == (Artifact(TOTAL, D("20000")),)
