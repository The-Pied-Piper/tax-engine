"""Unit tests for blank as a value (`tax_engine.domain.blank`) and how a capability treats one.

A blank is a value of its own: an artifact of any kind can be blank, reading its value is an
error, and a capability's `BLANK_RULES` say, per consumed slot, whether a blank there is refused
(no rule), replaced by a fallback value, or passed on to everything the capability produces.
Capabilities with one compute and different rules share a parent, as the made-up `ex/` ones here.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, ClassVar

import pytest

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.blank import BLANK, PASS_ON, Blank, BlankRule
from tax_engine.domain.capability import Capability, CapabilityResult
from tax_engine.domain.composition import Composition
from tax_engine.domain.digits import DigitsKind
from tax_engine.domain.errors import (
    BlankNotAllowedError,
    BlankValueError,
    InvalidCapabilityError,
    InvalidCompositionError,
    NegativeArtifactError,
)
from tax_engine.domain.record_list import RecordListKind
from tax_engine.domain.trace import (
    BlankFallbackLine,
    BlankPassedOnLine,
    LeftBlankLine,
    SubtractedLine,
    SumLine,
)
from tax_engine.domain.worksheet import Worksheet

D = Decimal

INCOME = ArtifactKind("ex/income", Decimal)
CHART_GAIN = ArtifactKind("ex/chart_gain", Decimal)
LIMIT = ArtifactKind("ex/limit", Decimal)
DEDUCTION = ArtifactKind("ex/deduction", Decimal)
TAXABLE = ArtifactKind("ex/taxable_income", Decimal)
OTHER = ArtifactKind("ex/other", Decimal)
NET = ArtifactKind("ex/net", Decimal)
NON_NEGATIVE = ArtifactKind("ex/count_of_things", int, non_negative=True)


class SubtractCompute(Capability):
    """The shared compute: `output` = `amount` less `less`. The parent declares no blank rules."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"amount": Decimal, "less": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}
    computed = 0

    def __init__(self, amount: Money, less: Money, output: Money) -> None:
        super().__init__(amount=amount, less=less, output=output)
        self._amount, self._less, self._output = amount, less, output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        type(self).computed += 1
        amount = self._input(inputs, self._amount).value
        less = self._input(inputs, self._less).value
        result = amount - less
        line = SubtractedLine(self._output, self._amount, amount, self._less, less, result)
        return CapabilityResult((Artifact(self._output, result),), (line,))


class SubtractStrict(SubtractCompute):
    """No slot may be blank."""


class SubtractLessZero(SubtractCompute):
    """A blank `less` is 0; a blank `amount` is refused."""

    BLANK_RULES: ClassVar[Mapping[str, BlankRule]] = {"less": D(0)}


class SubtractPassOn(SubtractCompute):
    """A blank in either slot makes the output blank."""

    BLANK_RULES: ClassVar[Mapping[str, BlankRule]] = {"amount": PASS_ON, "less": PASS_ON}


def blank(kind: ArtifactKind[Any]) -> Artifact[Any]:
    return Artifact(kind, BLANK)


# --- the blank value --------------------------------------------------------------------------


def test_a_blank_artifact_is_blank_and_has_no_value() -> None:
    artifact = blank(INCOME)

    assert artifact.is_blank
    assert artifact.kind == INCOME
    with pytest.raises(BlankValueError, match="income was left blank"):
        _ = artifact.value


def test_a_filled_artifact_is_not_blank() -> None:
    assert not Artifact(INCOME, D(0)).is_blank
    assert Artifact(INCOME, D("12.5")).value == D("12.5")


def test_blank_is_not_zero() -> None:
    assert blank(INCOME) != Artifact(INCOME, D(0))
    assert blank(INCOME) == blank(INCOME)
    assert hash(blank(INCOME)) == hash(blank(INCOME))


def test_blank_is_one_value_distinct_from_every_typed_value() -> None:
    assert BLANK is Blank.BLANK
    others: tuple[object, ...] = (0, "", (), None, False)
    assert all(BLANK != other for other in others)


def test_any_kind_accepts_blank() -> None:
    kinds: tuple[ArtifactKind[Any], ...] = (
        INCOME,
        NON_NEGATIVE,
        ArtifactKind("ex/yes_or_no", bool),
        ArtifactKind("ex/note", str),
        DigitsKind("ex/sin", digits=9),
        RecordListKind("ex/people", fields=(INCOME,)),
    )
    assert all(blank(kind).is_blank for kind in kinds)


def test_a_wrong_typed_value_is_still_refused() -> None:
    with pytest.raises(TypeError, match="income must be a Decimal"):
        Artifact(ArtifactKind[Any]("ex/income", Decimal), "12")


def test_a_negative_value_is_still_refused_for_a_non_negative_kind() -> None:
    with pytest.raises(NegativeArtifactError):
        Artifact(NON_NEGATIVE, -1)


# --- declaring blank rules --------------------------------------------------------------------


def test_blank_rules_are_read_only_and_inherited() -> None:
    assert SubtractCompute.BLANK_RULES == {}
    assert SubtractStrict.BLANK_RULES == {}
    assert SubtractLessZero.BLANK_RULES == {"less": D(0)}
    assert isinstance(SubtractLessZero.BLANK_RULES, MappingProxyType)

    class Child(SubtractLessZero):
        pass

    assert Child.BLANK_RULES == {"less": D(0)}


def test_a_rule_for_a_slot_that_is_not_consumed_is_refused() -> None:
    with pytest.raises(InvalidCapabilityError, match="BLANK_RULES slot 'output'"):

        class Bad(SubtractCompute):
            BLANK_RULES: ClassVar[Mapping[str, BlankRule]] = {"output": PASS_ON}


@pytest.mark.parametrize("fallback", [1, D("NaN"), D("Infinity"), True])
def test_a_fallback_of_the_wrong_type_or_not_finite_is_refused(fallback: BlankRule) -> None:
    with pytest.raises(InvalidCapabilityError, match="BLANK_RULES slot 'less'"):

        class Bad(SubtractCompute):
            BLANK_RULES: ClassVar[Mapping[str, BlankRule]] = {"less": fallback}


def test_a_count_slot_takes_an_int_fallback() -> None:
    class Count(Capability):
        CONSUMES: ClassVar[Mapping[str, type]] = {"count": int}
        PRODUCES: ClassVar[Mapping[str, type]] = {"output": int}
        BLANK_RULES: ClassVar[Mapping[str, BlankRule]] = {"count": 0}

        def __init__(self, count: ArtifactKind[int], output: ArtifactKind[int]) -> None:
            super().__init__(count=count, output=output)

        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            raise NotImplementedError

    assert Count.BLANK_RULES == {"count": 0}


def test_a_fallback_for_a_list_slot_is_the_type_of_its_kinds() -> None:
    class Total(Capability):
        CONSUMES: ClassVar[Mapping[str, type]] = {"parts": list[Decimal]}
        PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}
        BLANK_RULES: ClassVar[Mapping[str, BlankRule]] = {"parts": D(0)}

        def __init__(self, parts: tuple[Money, ...], output: Money) -> None:
            super().__init__(parts=parts, output=output)

        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            parts = tuple(artifact for artifact in inputs)
            total = sum((a.value for a in parts), D(0))
            return CapabilityResult((Artifact(NET, total),), (SumLine(NET, (), total),))

    result = Total((INCOME, OTHER), NET).run((blank(INCOME), Artifact(OTHER, D(5))))

    assert result.outputs == (Artifact(NET, D(5)),)
    assert result.trace[0] == BlankFallbackLine(INCOME, D(0))


# --- what a capability does with a blank ------------------------------------------------------


def test_a_slot_with_no_rule_refuses_a_blank_naming_the_line_and_slot() -> None:
    with pytest.raises(BlankNotAllowedError, match="'chart_gain' was left blank.*'amount'"):
        SubtractStrict(CHART_GAIN, LIMIT, NET).run((blank(CHART_GAIN), Artifact(LIMIT, D(1))))


def test_a_slot_with_a_fallback_takes_it_and_says_so() -> None:
    SubtractCompute.computed = 0
    result = SubtractLessZero(INCOME, DEDUCTION, TAXABLE).run(
        (Artifact(INCOME, D(500)), blank(DEDUCTION))
    )

    assert result.outputs == (Artifact(TAXABLE, D(500)),)
    assert result.trace == (
        BlankFallbackLine(DEDUCTION, D(0)),
        SubtractedLine(TAXABLE, INCOME, D(500), DEDUCTION, D(0), D(500)),
    )


def test_a_blank_in_a_slot_without_a_fallback_is_refused_by_a_sibling_that_has_one() -> None:
    with pytest.raises(BlankNotAllowedError, match="'income' was left blank.*'amount'"):
        SubtractLessZero(INCOME, DEDUCTION, TAXABLE).run((blank(INCOME), Artifact(DEDUCTION, D(1))))


def test_pass_on_makes_every_output_blank_and_does_not_compute() -> None:
    SubtractCompute.computed = 0
    result = SubtractPassOn(CHART_GAIN, LIMIT, DEDUCTION).run(
        (blank(CHART_GAIN), Artifact(LIMIT, D(1)))
    )

    assert result.outputs == (blank(DEDUCTION),)
    assert result.trace == (BlankPassedOnLine(DEDUCTION, (CHART_GAIN,)),)
    assert SubtractCompute.computed == 0


def test_a_refusal_comes_before_a_pass_on() -> None:
    class Mixed(SubtractCompute):
        BLANK_RULES: ClassVar[Mapping[str, BlankRule]] = {"amount": PASS_ON}

    with pytest.raises(BlankNotAllowedError, match="'less'"):
        Mixed(INCOME, LIMIT, NET).run((blank(INCOME), blank(LIMIT)))


def test_with_no_blank_the_rules_change_nothing() -> None:
    inputs = (Artifact(INCOME, D(9)), Artifact(DEDUCTION, D(4)))
    results = [
        cls(INCOME, DEDUCTION, TAXABLE).run(inputs)
        for cls in (SubtractStrict, SubtractLessZero, SubtractPassOn)
    ]

    assert all(result == results[0] for result in results)
    assert results[0].outputs == (Artifact(TAXABLE, D(5)),)


def test_one_parent_gives_different_results_on_the_same_blank() -> None:
    inputs = (Artifact(INCOME, D(500)), blank(DEDUCTION))

    refused = pytest.raises(BlankNotAllowedError)
    with refused:
        SubtractStrict(INCOME, DEDUCTION, TAXABLE).run(inputs)
    assert SubtractLessZero(INCOME, DEDUCTION, TAXABLE).run(inputs).outputs == (
        Artifact(TAXABLE, D(500)),
    )
    assert SubtractPassOn(INCOME, DEDUCTION, TAXABLE).run(inputs).outputs == (blank(TAXABLE),)
    assert all(
        "compute" not in vars(cls) for cls in (SubtractStrict, SubtractLessZero, SubtractPassOn)
    )


# --- through a worksheet and a composition ----------------------------------------------------


def test_a_blank_starting_artifact_is_traced_as_left_blank() -> None:
    worksheet = Worksheet(blank(CHART_GAIN), Artifact(INCOME, D(1)))

    assert worksheet.trace == (LeftBlankLine(CHART_GAIN),)
    assert worksheet.get(CHART_GAIN).is_blank


def test_an_upstream_blank_is_passed_on_taken_as_zero_or_refused_by_the_consumer() -> None:
    upstream = SubtractPassOn(CHART_GAIN, LIMIT, DEDUCTION)
    start = (blank(CHART_GAIN), Artifact(LIMIT, D(1)), Artifact(INCOME, D(500)))

    def worksheet_with(consumer: Capability) -> Worksheet:
        worksheet = Worksheet(*start)
        worksheet.apply(upstream)
        worksheet.apply(consumer)
        return worksheet

    passed = worksheet_with(SubtractPassOn(INCOME, DEDUCTION, TAXABLE))
    assert passed.get(TAXABLE).is_blank

    fell_back = worksheet_with(SubtractLessZero(INCOME, DEDUCTION, TAXABLE))
    assert fell_back.get(TAXABLE).value == D(500)

    with pytest.raises(BlankNotAllowedError, match="'deduction' was left blank"):
        worksheet_with(SubtractStrict(INCOME, DEDUCTION, TAXABLE))


def test_a_skipped_chart_leaves_the_deduction_blank_and_the_tax_base_unchanged() -> None:
    """Chart skipped (blank gain), so the deduction is blank, not 0; income less a blank
    deduction, which that line takes as 0, is the unchanged $50,000.
    """
    capabilities = [
        SubtractPassOn(CHART_GAIN, LIMIT, DEDUCTION),
        SubtractLessZero(INCOME, DEDUCTION, TAXABLE),
    ]
    composition = Composition(
        capabilities,
        inputs=frozenset({CHART_GAIN, LIMIT, INCOME}),
        outputs=frozenset({DEDUCTION, TAXABLE}),
        blank_inputs=frozenset({CHART_GAIN}),
    )

    worksheet = composition.compute(
        blank(CHART_GAIN), Artifact(LIMIT, D(100000)), Artifact(INCOME, D(50000))
    )

    assert worksheet.get(DEDUCTION).is_blank
    assert worksheet.get(TAXABLE).value == D(50000)
    assert worksheet.trace == (
        LeftBlankLine(CHART_GAIN),
        BlankPassedOnLine(DEDUCTION, (CHART_GAIN,)),
        BlankFallbackLine(DEDUCTION, D(0)),
        SubtractedLine(TAXABLE, INCOME, D(50000), DEDUCTION, D(0), D(50000)),
    )


def composition(*blank_inputs: ArtifactKind[Any]) -> Composition:
    return Composition(
        [SubtractLessZero(INCOME, DEDUCTION, TAXABLE)],
        inputs=frozenset({INCOME, DEDUCTION}),
        outputs=frozenset({TAXABLE}),
        blank_inputs=frozenset(blank_inputs),
    )


def test_the_composition_accepts_a_blank_input_it_declares() -> None:
    worksheet = composition(DEDUCTION).compute(Artifact(INCOME, D(7)), blank(DEDUCTION))

    assert worksheet.get(TAXABLE).value == D(7)


def test_the_composition_refuses_a_blank_input_it_does_not_declare() -> None:
    with pytest.raises(BlankNotAllowedError, match="'deduction' may not be left blank"):
        composition().compute(Artifact(INCOME, D(7)), blank(DEDUCTION))
    with pytest.raises(BlankNotAllowedError, match="'income' may not be left blank"):
        composition(DEDUCTION).compute(blank(INCOME), Artifact(DEDUCTION, D(1)))


def test_a_declared_blank_input_must_be_an_input() -> None:
    with pytest.raises(InvalidCompositionError, match="blank input 'limit' is not an input"):
        composition(LIMIT)


def test_a_composition_declares_no_blank_input_by_default() -> None:
    plain = Composition(
        [SubtractStrict(INCOME, DEDUCTION, TAXABLE)],
        inputs=frozenset({INCOME, DEDUCTION}),
        outputs=frozenset({TAXABLE}),
    )

    with pytest.raises(BlankNotAllowedError):
        plain.compute(Artifact(INCOME, D(7)), blank(DEDUCTION))
