"""Unit tests for the CountByConditions capability (`ca/count_by_conditions`).

A count from comparisons: 1 or 0, so `core/times_count` can switch a line on or off. Its slots:
one parameter slot `conditions` (a `conditions` dataset: the form's list of conditions, in the
form's order and wording, and which count a list gives when any condition applies), two consumed
list slots, `counts` (kinds of `int`, the yes/no caller counts, 1 = the condition applies) and
`amounts` (kinds of `Decimal`), and one produced slot `output` (a kind of `int`).

Each test of the dataset names the figure it reads by `position` (from 1) in the list of counts or
of amounts, and a comparison names the amount it is compared with by `against`, a position in the
list of amounts. Each kind is listed once, however many tests read it. The constructor refuses a
position beyond its list and a listed kind that no test reads (`InvalidCapabilityError`).

Every test is evaluated, so the trace records every figure read: one `ConditionLine` for each
condition, then one `ConditionsCountLine`. The output is `count_when_any_applies` when at least
one condition applies and the other one of 0 and 1 when none does; nothing is rounded.

The artifact kinds and the dataset family are made up; the figures are the ones of Form ON428
(2025) line 80 and the rule for lines 75 and 76, and of the Federal Worksheet's chart for line
23500. The wiring comes later.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.times_count import TimesCount
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.composition import Composition
from tax_engine.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.trace import ConditionLine, ConditionsCountLine
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions

D = Decimal

# --- made-up kinds -----------------------------------------------------------------------------

NOT_RESIDENT_CANADA = ArtifactKind("ex/not_resident_of_canada", int)
NOT_RESIDENT_ONTARIO = ArtifactKind("ex/not_resident_of_ontario", int)
BANKRUPT = ArtifactKind("ex/bankrupt", int)
TRUSTEE_FILED = ArtifactKind("ex/filed_by_trustee", int)
NOT_CLAIMING = ArtifactKind("ex/not_claiming_reduction", int)
LINE_72 = ArtifactKind("ex/amount_on_line_72", Decimal)
FILER_INCOME = ArtifactKind("ex/filer_net_income", Decimal)
SPOUSE_INCOME = ArtifactKind("ex/spouse_net_income", Decimal)
LINE_11900 = ArtifactKind("ex/amount_on_line_11900", Decimal)
LINE_11300 = ArtifactKind("ex/amount_on_line_11300", Decimal)
LINE_14600 = ArtifactKind("ex/amount_on_line_14600", Decimal)
NET_INCOME = ArtifactKind("ex/net_income_line_23400", Decimal)
GATE = ArtifactKind("ex/gate", int)
HIGHER_INCOME = ArtifactKind("ex/higher_income_claims", int)
CHART = ArtifactKind("ex/chart_applies", int)
REDUCTION_BEFORE_GATE = ArtifactKind("ex/reduction_before_gate", Decimal)
REDUCTION = ArtifactKind("ex/reduction", Decimal)

FIVE_COUNTS = (NOT_RESIDENT_CANADA, NOT_RESIDENT_ONTARIO, BANKRUPT, TRUSTEE_FILED, NOT_CLAIMING)

# --- made-up datasets, copied from the forms' text ----------------------------------------------


def a_condition(text: str, *tests: ConditionTest) -> Condition:
    return Condition(text, (ConditionPart(tests),))


def a_count_applies(text: str, position: int) -> Condition:
    return a_condition(text, ConditionTest("count", position, "equal_to", D(1), None))


def dataset(
    values: ConditionList, family: str = "ex/conditions"
) -> ParameterDataset[ConditionList]:
    return ParameterDataset(
        family, 2025, CONDITIONS, values, NO_ROUNDING, ("https://example.org/conditions",)
    )


# Form ON428 2025, line 80: "Enter "0" on line 80 if any of the following applies to you:".
LINE_80_CONDITIONS = (
    a_count_applies("You were not a resident of Canada at the beginning of the year", 1),
    a_count_applies("You were not a resident of Ontario on December 31, 2025", 2),
    a_condition(
        "There is an amount on line 72", ConditionTest("amount", 1, "not_equal_to", D(0), None)
    ),
    a_count_applies("You were bankrupt at any time in 2025", 3),
    a_count_applies("Your return is filed for you by a trustee in bankruptcy", 4),
    a_count_applies("You are choosing not to claim an Ontario tax reduction", 5),
)

# The counts are listed in the form's order, so the list of counts skips line 72, an amount; line
# 72 is position 1 of the amounts.
LINE_80 = dataset(ConditionList(0, LINE_80_CONDITIONS), "ex/line_80_conditions")

# "only the individual with the higher net income can claim the amounts on lines 75 and 76".
HIGHER_NET_INCOME = dataset(
    ConditionList(
        1,
        (
            a_condition(
                "Only the individual with the higher net income can claim the amounts on lines 75 "
                "and 76",
                ConditionTest("amount", 1, "more_than", None, 2),
            ),
        ),
    ),
    "ex/higher_net_income",
)

# Federal Worksheet 2025, chart for line 23500 (docs/cra-forms-2025/5000-d1-25e.txt): "Complete the
# chart below if one or both of the following applies:". Each condition joins tests with "and"
# (the parts) and "or" (the tests of a part).
CHART_CONDITIONS = dataset(
    ConditionList(
        1,
        (
            Condition(
                "You entered an amount on line 11900 of your return and the amount on line 23400 "
                "is more than $82,125",
                (
                    ConditionPart((ConditionTest("amount", 1, "not_equal_to", D(0), None),)),
                    ConditionPart((ConditionTest("amount", 4, "more_than", D(82125), None),)),
                ),
            ),
            Condition(
                "You entered an amount on line 11300 or line 14600 of your return and the amount "
                "on line 23400 is more than $93,454",
                (
                    ConditionPart(
                        (
                            ConditionTest("amount", 2, "not_equal_to", D(0), None),
                            ConditionTest("amount", 3, "not_equal_to", D(0), None),
                        )
                    ),
                    ConditionPart((ConditionTest("amount", 4, "more_than", D(93454), None),)),
                ),
            ),
        ),
    ),
    "ex/chart_conditions",
)


def line_80() -> CountByConditions:
    return CountByConditions(LINE_80, FIVE_COUNTS, (LINE_72,), GATE)


def higher_income() -> CountByConditions:
    return CountByConditions(HIGHER_NET_INCOME, (), (FILER_INCOME, SPOUSE_INCOME), HIGHER_INCOME)


def chart() -> CountByConditions:
    # Both conditions read line 23400, listed once.
    return CountByConditions(
        CHART_CONDITIONS, (), (LINE_11900, LINE_11300, LINE_14600, NET_INCOME), CHART
    )


def line_80_inputs(
    line_72: str = "0.00", flags: tuple[int, int, int, int, int] = (0, 0, 0, 0, 0)
) -> tuple[Artifact[Any], ...]:
    return (
        *(Artifact(kind, flag) for kind, flag in zip(FIVE_COUNTS, flags, strict=True)),
        Artifact(LINE_72, D(line_72)),
    )


def line_80_count(
    line_72: str = "0.00", flags: tuple[int, int, int, int, int] = (0, 0, 0, 0, 0)
) -> int:
    (output,) = line_80().compute(line_80_inputs(line_72, flags)).outputs
    assert output.kind == GATE
    return cast(int, output.value)


def incomes(filer: str, spouse: str) -> tuple[Artifact[Any], ...]:
    return (Artifact(FILER_INCOME, D(filer)), Artifact(SPOUSE_INCOME, D(spouse)))


def higher_income_count(filer: str, spouse: str) -> int:
    (output,) = higher_income().compute(incomes(filer, spouse)).outputs
    return cast(int, output.value)


def entered(flag: int) -> Decimal:
    """An amount entered on a line (1500.00) for 1, none (0) for 0."""
    return D("1500.00") if flag else D(0)


def chart_inputs(flags: tuple[int, int, int], net_income: str) -> tuple[Artifact[Any], ...]:
    return (
        Artifact(LINE_11900, entered(flags[0])),
        Artifact(LINE_11300, entered(flags[1])),
        Artifact(LINE_14600, entered(flags[2])),
        Artifact(NET_INCOME, D(net_income)),
    )


def chart_count(flags: tuple[int, int, int], net_income: str) -> int:
    (output,) = chart().compute(chart_inputs(flags, net_income)).outputs
    return cast(int, output.value)


# --- the capability's shape ---------------------------------------------------------------------


def test_is_registered_as_ca_count_by_conditions() -> None:
    assert CapabilityRegistry.shared().get("ca/count_by_conditions") is CountByConditions


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "count_by_conditions" in ca_capabilities.__all__
    assert ca_capabilities.count_by_conditions.CountByConditions is CountByConditions


def test_its_package_declares_the_ca_namespace() -> None:
    assert ca_capabilities.NAMESPACE == "ca"
    assert ca_capabilities.__all__[0] == "NAMESPACE"


def test_declares_its_contract() -> None:
    assert line_80().consumes == frozenset({*FIVE_COUNTS, LINE_72})
    assert line_80().produces == frozenset({GATE})
    assert higher_income().consumes == frozenset({FILER_INCOME, SPOUSE_INCOME})
    assert chart().consumes == frozenset({LINE_11900, LINE_11300, LINE_14600, NET_INCOME})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(CountByConditions)
    assert "produces" not in vars(CountByConditions)


def test_declares_its_slots() -> None:
    assert CountByConditions.PARAMETERS == {"conditions": CONDITIONS}
    assert CountByConditions.PARAMETERS["conditions"] is CONDITIONS
    assert CountByConditions.CONSUMES == {"counts": list[int], "amounts": list[Decimal]}
    assert CountByConditions.PRODUCES == {"output": int}
    assert CountByConditions.is_list_slot("counts")
    assert CountByConditions.is_list_slot("amounts")
    assert not CountByConditions.is_list_slot("output")


def test_its_slots_are_read_only() -> None:
    slots = (CountByConditions.PARAMETERS, CountByConditions.CONSUMES, CountByConditions.PRODUCES)
    for mapping in slots:
        assert isinstance(mapping, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(CountByConditions.PARAMETERS, Mapping[str, ParameterKind[ConditionList]])
    assert_type(CountByConditions.CONSUMES, Mapping[str, type])
    assert_type(CountByConditions.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    slots = (CountByConditions.PARAMETERS, CountByConditions.CONSUMES, CountByConditions.PRODUCES)
    for mapping in slots:
        with pytest.raises(TypeError):
            cast(Any, mapping)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = CountByConditions(
        conditions=LINE_80, counts=FIVE_COUNTS, amounts=(LINE_72,), output=GATE
    )

    assert wired.compute(line_80_inputs()).outputs == (Artifact(GATE, 1),)


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        CountByConditions(LINE_80, FIVE_COUNTS, (LINE_72,), GATE, NO_ROUNDING)  # type: ignore[call-arg]


def test_refuses_a_position_beyond_the_list_of_counts() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountByConditions.*'counts'.*position 5"):
        CountByConditions(LINE_80, FIVE_COUNTS[:4], (LINE_72,), GATE)


def test_refuses_a_count_that_no_test_reads() -> None:
    extra = ArtifactKind("ex/extra_flag", int)

    with pytest.raises(InvalidCapabilityError, match="CountByConditions.*'counts'.*extra_flag"):
        CountByConditions(LINE_80, (*FIVE_COUNTS, extra), (LINE_72,), GATE)


def test_refuses_a_position_beyond_the_list_of_amounts() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountByConditions.*'amounts'.*position 2"):
        CountByConditions(HIGHER_NET_INCOME, (), (FILER_INCOME,), HIGHER_INCOME)


def test_refuses_an_empty_list_when_the_dataset_reads_a_position() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountByConditions.*'amounts'.*position 1"):
        CountByConditions(LINE_80, FIVE_COUNTS, (), GATE)


def test_refuses_an_amount_that_no_test_reads() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountByConditions.*'amounts'.*filer_net_in"):
        CountByConditions(LINE_80, FIVE_COUNTS, (LINE_72, FILER_INCOME), GATE)


def test_refuses_a_count_in_the_middle_that_no_test_reads() -> None:
    # Position 4 of the chart's amounts is read; with only three amounts, position 4 is beyond.
    with pytest.raises(InvalidCapabilityError, match="CountByConditions.*'amounts'.*position 4"):
        CountByConditions(CHART_CONDITIONS, (), (LINE_11900, LINE_11300, LINE_14600), CHART)


def test_an_against_position_counts_as_read() -> None:
    CountByConditions(HIGHER_NET_INCOME, (), (FILER_INCOME, SPOUSE_INCOME), HIGHER_INCOME)

    with pytest.raises(InvalidCapabilityError, match="'amounts'"):
        CountByConditions(HIGHER_NET_INCOME, (), (FILER_INCOME, SPOUSE_INCOME, LINE_72), CHART)


def test_a_kind_read_by_several_tests_is_listed_once() -> None:
    wired = chart()

    assert wired.consumes == frozenset({LINE_11900, LINE_11300, LINE_14600, NET_INCOME})


def test_refuses_a_kind_in_both_counts_and_amounts() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountByConditions"):
        CountByConditions(LINE_80, (*FIVE_COUNTS[:4], LINE_72), (LINE_72,), GATE)  # type: ignore[arg-type]


def test_refuses_the_output_as_one_of_the_counts() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountByConditions") as raised:
        CountByConditions(LINE_80, (*FIVE_COUNTS[:4], GATE), (LINE_72,), GATE)

    message = str(raised.value)
    assert "'counts'" in message
    assert "'output'" in message


def test_refuses_a_count_listed_twice() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountByConditions.*'counts'"):
        CountByConditions(LINE_80, (*FIVE_COUNTS[:4], BANKRUPT), (LINE_72,), GATE)


def test_refuses_an_amount_kind_as_a_count() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountByConditions.*'counts'"):
        CountByConditions(LINE_80, (*FIVE_COUNTS[:4], LINE_72), (FILER_INCOME,), GATE)  # type: ignore[arg-type]


def test_refuses_a_count_kind_as_an_amount() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountByConditions.*'amounts'"):
        CountByConditions(LINE_80, FIVE_COUNTS, (BANKRUPT,), GATE)  # type: ignore[arg-type]


def test_refuses_a_money_kind_as_the_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountByConditions.*'output'"):
        CountByConditions(LINE_80, FIVE_COUNTS, (LINE_72,), REDUCTION)  # type: ignore[arg-type]


def test_refuses_a_rate_kind_as_the_output() -> None:
    other = ArtifactKind("ex/a_rate", Rate)

    with pytest.raises(InvalidCapabilityError, match="CountByConditions.*'output'"):
        CountByConditions(LINE_80, FIVE_COUNTS, (LINE_72,), other)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A rate dataset is not a ParameterDataset[ConditionList]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.5")), NO_ROUNDING, ("https://example.org/r",)
        )
        CountByConditions(rate, FIVE_COUNTS, (LINE_72,), GATE)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(CountByConditions, "__type_params__", ())
    assert not getattr(CountByConditions, "__parameters__", ())


# --- line 80's gate -----------------------------------------------------------------------------


def test_line_80_with_no_amount_on_line_72_and_no_condition_gives_1() -> None:
    assert line_80_count("0.00") == 1


def test_line_80_with_120_on_line_72_gives_0() -> None:
    assert line_80_count("120.00") == 0


def test_line_80_with_a_cent_on_line_72_gives_0() -> None:
    assert line_80_count("0.01") == 0


@pytest.mark.parametrize("position", range(5))
def test_line_80_with_any_one_of_the_five_conditions_gives_0(position: int) -> None:
    flags = tuple(1 if index == position else 0 for index in range(5))

    assert line_80_count("0.00", cast(Any, flags)) == 0


def test_line_80_with_every_condition_gives_0() -> None:
    assert line_80_count("120.00", (1, 1, 1, 1, 1)) == 0


def test_the_output_is_an_int_artifact_of_the_produced_kind() -> None:
    (output,) = line_80().compute(line_80_inputs()).outputs

    assert output == Artifact(GATE, 1)
    assert type(output.value) is int


def test_the_zero_output_is_an_int_too() -> None:
    (output,) = line_80().compute(line_80_inputs("120.00")).outputs

    assert output == Artifact(GATE, 0)
    assert type(output.value) is int


def test_the_scale_of_line_72_does_not_matter() -> None:
    assert line_80_count("0") == 1
    assert line_80_count("0.000") == 1


def test_a_negative_amount_on_line_72_is_an_amount() -> None:
    # "There is an amount on line 72" is a test for not 0, not for more than 0.
    assert line_80_count("-5") == 0


def test_a_count_other_than_1_does_not_apply() -> None:
    assert line_80_count("0.00", (0, 0, 2, 0, 0)) == 1


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = line_80().compute((Artifact(other, D("9")), *line_80_inputs()))

    assert result.outputs == (Artifact(GATE, 1),)


def test_a_missing_count_is_a_missing_artifact() -> None:
    inputs = line_80_inputs()[1:]

    with pytest.raises(MissingArtifactError, match="not_resident_of_canada"):
        line_80().compute(inputs)


def test_a_missing_amount_is_a_missing_artifact() -> None:
    inputs = line_80_inputs()[:-1]

    with pytest.raises(MissingArtifactError, match="amount_on_line_72"):
        line_80().compute(inputs)


# --- lines 75 and 76: the higher net income -----------------------------------------------------


def test_the_higher_net_income_gives_1() -> None:
    assert higher_income_count("48000", "30000") == 1


def test_the_lower_net_income_gives_0() -> None:
    assert higher_income_count("30000", "48000") == 0


def test_a_tie_gives_0_because_more_than_refuses_it() -> None:
    # `more_than` does not hold for equal incomes.
    assert higher_income_count("40000", "40000") == 0


def test_a_cent_more_is_higher() -> None:
    assert higher_income_count("40000.01", "40000.00") == 1
    assert higher_income_count("40000.00", "40000.01") == 0


def test_the_first_amount_listed_is_the_one_tested_against_the_second() -> None:
    swapped = CountByConditions(HIGHER_NET_INCOME, (), (SPOUSE_INCOME, FILER_INCOME), HIGHER_INCOME)

    (output,) = swapped.compute(incomes("48000", "30000")).outputs

    assert output == Artifact(HIGHER_INCOME, 0)


def test_the_amounts_are_compared_exactly() -> None:
    assert (
        higher_income_count("12345678901234567890123456789.01", "12345678901234567890123456789")
        == 1
    )


# --- line 23500's chart: and/or within a condition ----------------------------------------------


def test_the_chart_applies_when_11900_is_entered_and_line_23400_is_above_82125() -> None:
    assert chart_count((1, 0, 0), "82125.01") == 1


def test_the_chart_does_not_apply_at_exactly_82125_with_only_11900() -> None:
    assert chart_count((1, 0, 0), "82125") == 0


def test_the_chart_applies_when_14600_alone_is_entered_and_line_23400_is_above_93454() -> None:
    assert chart_count((0, 0, 1), "93454.01") == 1


def test_the_chart_applies_when_11300_alone_is_entered_and_line_23400_is_above_93454() -> None:
    assert chart_count((0, 1, 0), "93454.01") == 1


def test_the_chart_does_not_apply_for_11300_at_exactly_93454() -> None:
    assert chart_count((0, 1, 0), "93454") == 0


def test_the_chart_does_not_apply_for_11300_between_the_two_figures() -> None:
    # 90,000 is above 82,125 but 11900 is not entered; and below 93,454.
    assert chart_count((0, 1, 0), "90000") == 0


def test_the_chart_applies_when_both_conditions_do() -> None:
    assert chart_count((1, 1, 1), "100000") == 1


def test_the_chart_does_not_apply_when_nothing_is_entered() -> None:
    assert chart_count((0, 0, 0), "1000000") == 0


def test_the_chart_does_not_apply_when_the_income_is_low() -> None:
    assert chart_count((1, 1, 1), "50000") == 0


def test_a_chart_that_applies_gives_the_other_count_than_line_80() -> None:
    # count_when_any_applies is 1 here, 0 on line 80.
    assert chart_count((1, 0, 0), "90000") == 1
    assert chart_count((0, 0, 0), "90000") == 0


# --- the count when no condition applies is the other one ---------------------------------------


def test_a_list_counting_0_when_any_applies_counts_1_when_none_does() -> None:
    assert LINE_80.values.count_when_any_applies == 0
    assert line_80_count() == 1


def test_a_list_counting_1_when_any_applies_counts_0_when_none_does() -> None:
    assert HIGHER_NET_INCOME.values.count_when_any_applies == 1
    assert higher_income_count("1", "2") == 0


# --- trace --------------------------------------------------------------------------------------


def test_traces_one_line_for_each_condition_then_a_count_line() -> None:
    trace = line_80().compute(line_80_inputs("120.00", (0, 0, 1, 0, 0))).trace

    assert trace == (
        ConditionLine(
            GATE,
            1,
            "You were not a resident of Canada at the beginning of the year",
            ((NOT_RESIDENT_CANADA, 0),),
            False,
        ),
        ConditionLine(
            GATE,
            2,
            "You were not a resident of Ontario on December 31, 2025",
            ((NOT_RESIDENT_ONTARIO, 0),),
            False,
        ),
        ConditionLine(GATE, 3, "There is an amount on line 72", ((LINE_72, D("120.00")),), True),
        ConditionLine(GATE, 4, "You were bankrupt at any time in 2025", ((BANKRUPT, 1),), True),
        ConditionLine(
            GATE,
            5,
            "Your return is filed for you by a trustee in bankruptcy",
            ((TRUSTEE_FILED, 0),),
            False,
        ),
        ConditionLine(
            GATE,
            6,
            "You are choosing not to claim an Ontario tax reduction",
            ((NOT_CLAIMING, 0),),
            False,
        ),
        ConditionsCountLine(GATE, (3, 4), 0),
    )


def test_traces_the_count_line_with_no_position_when_nothing_applies() -> None:
    trace = line_80().compute(line_80_inputs()).trace

    assert trace[-1] == ConditionsCountLine(GATE, (), 1)
    assert [line.applies for line in trace[:-1] if isinstance(line, ConditionLine)] == [False] * 6


def test_traces_the_positions_from_1_in_the_forms_order() -> None:
    trace = line_80().compute(line_80_inputs("0.00", (1, 0, 0, 0, 1))).trace

    assert trace[-1] == ConditionsCountLine(GATE, (1, 6), 0)


def test_traces_both_amounts_of_a_test_against_an_amount_in_order() -> None:
    trace = higher_income().compute(incomes("48000", "30000")).trace

    assert trace == (
        ConditionLine(
            HIGHER_INCOME,
            1,
            "Only the individual with the higher net income can claim the amounts on lines 75 "
            "and 76",
            ((FILER_INCOME, D("48000")), (SPOUSE_INCOME, D("30000"))),
            True,
        ),
        ConditionsCountLine(HIGHER_INCOME, (1,), 1),
    )


def test_traces_every_figure_read_even_when_an_earlier_part_has_decided_the_condition() -> None:
    # 11900 is not entered, so the first condition is decided, but its amount is still recorded.
    trace = chart().compute(chart_inputs((0, 0, 0), "100000")).trace

    first, second, total = trace
    assert isinstance(first, ConditionLine)
    assert first.reads == ((LINE_11900, D(0)), (NET_INCOME, D("100000")))
    assert first.applies is False
    assert isinstance(second, ConditionLine)
    assert second.reads == (
        (LINE_11300, D(0)),
        (LINE_14600, D(0)),
        (NET_INCOME, D("100000")),
    )
    assert second.applies is False
    assert total == ConditionsCountLine(CHART, (), 0)


def test_traces_every_test_of_an_or_even_when_the_first_holds() -> None:
    trace = chart().compute(chart_inputs((0, 1, 1), "100000")).trace

    second = trace[1]
    assert isinstance(second, ConditionLine)
    assert second.reads == (
        (LINE_11300, D("1500.00")),
        (LINE_14600, D("1500.00")),
        (NET_INCOME, D("100000")),
    )
    assert second.applies is True


def test_a_chart_trace_names_the_conditions_that_applied() -> None:
    trace = chart().compute(chart_inputs((0, 0, 1), "93454.01")).trace

    assert trace[-1] == ConditionsCountLine(CHART, (2,), 1)


def test_trace_count_line_is_the_output() -> None:
    result = line_80().compute(line_80_inputs("120.00"))

    (output,) = result.outputs
    count_line = result.trace[-1]
    assert isinstance(count_line, ConditionsCountLine)
    assert count_line.count == output.value
    assert count_line.amount == D(output.value)


def test_trace_amounts_are_1_for_a_condition_that_applies_and_0_for_one_that_does_not() -> None:
    trace = line_80().compute(line_80_inputs("120.00")).trace

    assert [line.amount for line in trace[:-1]] == [D(0), D(0), D(1), D(0), D(0), D(0)]


def test_trace_texts_are_the_dataset_text_only() -> None:
    trace = line_80().compute(line_80_inputs()).trace

    for line, condition in zip(trace, LINE_80_CONDITIONS, strict=False):
        assert isinstance(line, ConditionLine)
        assert line.text == condition.text
        assert [f.name for f in fields(line) if isinstance(getattr(line, f.name), str)] == ["text"]


# --- English ------------------------------------------------------------------------------------


def test_renders_the_line_80_gate_in_english() -> None:
    trace = line_80().compute(line_80_inputs("120.00", (0, 0, 1, 0, 0))).trace

    assert EnglishTraceRenderer().render_all(trace) == (
        'gate: condition 1 "You were not a resident of Canada at the beginning of the year": '
        "not_resident_of_canada 0, does not apply",
        'gate: condition 2 "You were not a resident of Ontario on December 31, 2025": '
        "not_resident_of_ontario 0, does not apply",
        'gate: condition 3 "There is an amount on line 72": amount_on_line_72 120, applies',
        'gate: condition 4 "You were bankrupt at any time in 2025": bankrupt 1, applies',
        'gate: condition 5 "Your return is filed for you by a trustee in bankruptcy": '
        "filed_by_trustee 0, does not apply",
        'gate: condition 6 "You are choosing not to claim an Ontario tax reduction": '
        "not_claiming_reduction 0, does not apply",
        "gate: conditions 3, 4 apply, so 0",
    )


def test_renders_the_higher_net_income_rule_in_english() -> None:
    trace = higher_income().compute(incomes("48000", "30000")).trace

    assert EnglishTraceRenderer().render_all(trace) == (
        'higher_income_claims: condition 1 "Only the individual with the higher net income can '
        'claim the amounts on lines 75 and 76": filer_net_income 48000, spouse_net_income 30000, '
        "applies",
        "higher_income_claims: condition 1 applies, so 1",
    )


# --- with core/times_count: line 80 switched off or on ------------------------------------------
#
# Line 80 is multiplied by the gate once: 1 keeps the figure, 0 makes it 0.


def gated_line_80() -> Composition:
    return Composition(
        (
            TimesCount(REDUCTION_BEFORE_GATE, GATE, REDUCTION),  # listed out of order on purpose
            line_80(),
        ),
        inputs=frozenset({*FIVE_COUNTS, LINE_72, REDUCTION_BEFORE_GATE}),
        outputs=frozenset({REDUCTION}),
    )


def gated(line_72: str, flags: tuple[int, int, int, int, int]) -> Decimal:
    worksheet = gated_line_80().compute(
        *line_80_inputs(line_72, flags), Artifact(REDUCTION_BEFORE_GATE, D("1234.56"))
    )
    return worksheet.get(REDUCTION).value


def test_the_gate_runs_before_the_times_count() -> None:
    order = gated_line_80().order

    assert [type(step) for step in order] == [CountByConditions, TimesCount]


def test_line_80_keeps_its_value_when_no_condition_applies() -> None:
    assert gated("0.00", (0, 0, 0, 0, 0)) == D("1234.56")


def test_line_80_is_0_when_line_72_has_an_amount() -> None:
    assert gated("120.00", (0, 0, 0, 0, 0)) == D(0)


def test_line_80_is_0_when_the_filer_was_bankrupt() -> None:
    assert gated("0.00", (0, 0, 1, 0, 0)) == D(0)
