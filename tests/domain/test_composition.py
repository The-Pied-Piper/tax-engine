"""Unit tests for the Composition: wired capabilities, checked and ordered (design.md §5).

A composition is built from capabilities and the kinds a computation takes and returns. It
rejects bad wiring when built, derives a deterministic execution order from the capabilities'
contracts, and computes by applying each capability, in that order, to a fresh worksheet.
Generic tests use made-up kinds and the small summing capabilities below (`Link`, `Join`, ...),
each declaring its artifact slots.
"""

from __future__ import annotations

import decimal
from dataclasses import dataclass
from decimal import Decimal
from functools import cache
from itertools import permutations
from typing import Any, assert_type, cast

import pytest

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.at_most import AtMost
from tax_calculator.domain.capabilities.progressive_tax import ProgressiveTax
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capability import Capability, CapabilityRegistry, CapabilityResult
from tax_calculator.domain.composition import Composition
from tax_calculator.domain.errors import (
    CapabilityContractError,
    DomainError,
    DuplicateArtifactError,
    InputAboveBoundError,
    InvalidCapabilityError,
    InvalidCompositionError,
    NegativeArtifactError,
)
from tax_calculator.domain.parameters.brackets import BRACKETS, Bracket, BracketSchedule
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import NO_ROUNDING
from tax_calculator.domain.trace import BracketColumnLine, RoundedTotalLine, TraceLine
from tax_calculator.domain.worksheet import Worksheet

D = Decimal
A = ArtifactKind("ex/a", Decimal)
B = ArtifactKind("ex/b", Decimal)
C = ArtifactKind("ex/c", Decimal)
E = ArtifactKind("ex/e", Decimal)
F = ArtifactKind("ex/f", Decimal)
ZERO = D(0)


@dataclass(frozen=True)
class TaggedLine(TraceLine):
    """A made-up trace line: a capability's tag and the total it produced."""

    tag: str
    total: Decimal

    @property
    def amount(self) -> Decimal:
        return self.total


class Summing(Capability):
    """Produces each kind it produces as the sum of what it consumes + `add`; declares no slots.

    Its one trace line is labelled `tag`, so tests can see the order capabilities ran in. Each
    subclass declares its artifact slots and passes their kinds to `super().__init__`.
    """

    def __init__(
        self,
        *,
        add: Decimal = ZERO,
        tag: str = "link",
        **slots: ArtifactKind[Any] | tuple[ArtifactKind[Any], ...],
    ) -> None:
        super().__init__(**slots)
        self._add = add
        self.tag = tag

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        total = sum((self._input(inputs, kind).value for kind in self.consumes), ZERO) + self._add
        outputs = tuple(Artifact(kind, total) for kind in self.produces)
        return CapabilityResult(outputs=outputs, trace=(TaggedLine(self.tag, total),))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.tag})"


class Link(Summing):
    """Consumes `source` and produces `target` = `source` + `add`."""

    CONSUMES = {"source": Decimal}
    PRODUCES = {"target": Decimal}

    def __init__(
        self,
        source: Money,
        target: Money,
        add: Decimal = ZERO,
        tag: str = "link",
    ) -> None:
        super().__init__(source=source, target=target, add=add, tag=tag)


class IntLink(Summing):
    """Consumes a `Decimal` `source` and produces an `int` `target`.

    Its class is named `Link`, so a tie with a `Link` falls through to the kinds they produce.
    """

    CONSUMES = {"source": Decimal}
    PRODUCES = {"target": int}

    def __init__(
        self,
        source: Money,
        target: ArtifactKind[int],
        add: Decimal = ZERO,
        tag: str = "link",
    ) -> None:
        super().__init__(source=source, target=target, add=add, tag=tag)


IntLink.__name__ = "Link"


class Join(Summing):
    """Consumes `first` and `second` and produces `target` = `first` + `second` + `add`."""

    CONSUMES = {"first": Decimal, "second": Decimal}
    PRODUCES = {"target": Decimal}

    def __init__(
        self,
        first: Money,
        second: Money,
        target: Money,
        add: Decimal = ZERO,
        tag: str = "join",
    ) -> None:
        super().__init__(first=first, second=second, target=target, add=add, tag=tag)


class Sink(Summing):
    """Consumes `source` and produces nothing: it can be built, but no composition accepts it."""

    CONSUMES = {"source": Decimal}

    def __init__(self, source: Money, tag: str = "sink") -> None:
        super().__init__(source=source, tag=tag)


class Constant(Summing):
    """Consumes nothing and produces `target` = `add`: it has no incoming edges."""

    PRODUCES = {"target": Decimal}

    def __init__(self, target: Money, add: Decimal = ZERO, tag: str = "constant") -> None:
        super().__init__(target=target, add=add, tag=tag)


class LeftJoin(Join):
    """A `Join` whose class name sorts before `RightJoin`'s."""


class RightJoin(Join):
    """A `Join` whose class name sorts after `LeftJoin`'s."""


class Left(Link):
    """A `Link` whose class name sorts before `Right`'s."""


class Right(Link):
    """A `Link` whose class name sorts after `Left`'s."""


class Apple(Link):
    """A `Link` whose class name sorts before `Zebra`'s."""


class Zebra(Link):
    """A `Link` whose class name sorts after `Apple`'s."""


def kinds(*members: ArtifactKind[Any]) -> frozenset[ArtifactKind[Any]]:
    return frozenset(members)


# --- construction and build-time checks ---------------------------------------------------------


def test_a_well_wired_composition_builds() -> None:
    first, second = Link(A, B), Link(B, C)

    composition = Composition([first, second], inputs=kinds(A), outputs=kinds(C))

    assert composition.order == (first, second)


def test_accepts_any_iterable_of_capabilities() -> None:
    first, second = Link(A, B), Link(B, C)

    composition = Composition(iter([second, first]), inputs=kinds(A), outputs=kinds(C))

    assert composition.order == (first, second)


def test_wires_by_kind_equality_not_identity() -> None:
    first = Link(A, ArtifactKind("ex/b", Decimal))
    second = Link(ArtifactKind("ex/b", Decimal), C)

    composition = Composition([second, first], inputs=kinds(A), outputs=kinds(C))

    assert composition.order == (first, second)


def test_rejects_a_consumed_kind_nothing_produces() -> None:
    with pytest.raises(InvalidCompositionError, match="no producer for 'b'"):
        Composition([Join(A, B, C)], inputs=kinds(A), outputs=kinds(C))


def test_rejects_a_consumed_kind_produced_only_with_another_value_type() -> None:
    b_as_int = ArtifactKind("ex/b", int)
    producer = IntLink(A, b_as_int)
    consumer = Link(B, C)

    with pytest.raises(InvalidCompositionError, match="no producer for 'b'") as raised:
        Composition([producer, consumer], inputs=kinds(A), outputs=kinds(b_as_int, C))

    message = str(raised.value)
    assert "int" in message
    assert "Decimal" in message


def test_rejects_a_cycle_and_names_its_kinds() -> None:
    to_b = Join(A, C, B)
    to_c = Link(B, C)
    to_e = Link(B, E)

    with pytest.raises(InvalidCompositionError, match="cycle") as raised:
        Composition([to_b, to_c, to_e], inputs=kinds(A), outputs=kinds(E))

    message = str(raised.value)
    assert "cycle involving" in message
    assert "'b'" in message
    assert "'c'" in message
    assert "'e'" not in message  # strictly downstream of the cycle


def test_a_capability_that_consumes_what_it_produces_cannot_be_built() -> None:
    # The self-cycle never reaches the composition: the capability itself refuses the wiring.
    with pytest.raises(InvalidCapabilityError, match="Join"):
        Join(A, B, B)


def test_rejects_a_cycle_of_two_capabilities() -> None:
    to_b, to_c = Join(A, C, B), Link(B, C)

    with pytest.raises(InvalidCompositionError, match="cycle involving 'b', 'c'"):
        Composition([to_b, to_c], inputs=kinds(A), outputs=kinds(C))


def test_rejects_an_orphan_output() -> None:
    with pytest.raises(InvalidCompositionError, match="orphan") as raised:
        Composition([Link(A, B), Link(A, C)], inputs=kinds(A), outputs=kinds(B))

    assert "'c'" in str(raised.value)


def test_rejects_a_declared_output_nothing_produces() -> None:
    with pytest.raises(InvalidCompositionError, match="output 'c'"):
        Composition([Link(A, B)], inputs=kinds(A), outputs=kinds(B, C))


def test_rejects_two_capabilities_producing_one_kind() -> None:
    with pytest.raises(InvalidCompositionError, match="more than one") as raised:
        Composition(
            [Link(A, B, tag="one"), Link(A, B, tag="two")],
            inputs=kinds(A),
            outputs=kinds(B),
        )

    assert "'b'" in str(raised.value)


def test_rejects_a_declared_input_a_capability_also_produces() -> None:
    with pytest.raises(InvalidCompositionError, match="input 'b'") as raised:
        Composition([Link(A, B)], inputs=kinds(A, B), outputs=kinds(B))

    assert "produce" in str(raised.value)


def test_rejects_a_declared_input_nothing_consumes() -> None:
    with pytest.raises(InvalidCompositionError, match="input 'c' is consumed by nothing"):
        Composition([Link(A, B)], inputs=kinds(A, C), outputs=kinds(B))


def test_accepts_an_input_nothing_consumes_when_it_is_also_a_declared_output() -> None:
    link = Link(A, B)

    composition = Composition([link], inputs=kinds(A, C), outputs=kinds(B, C))

    assert composition.order == (link,)


def test_accepts_an_input_a_capability_consumes_when_it_is_also_a_declared_output() -> None:
    link = Link(A, B)

    composition = Composition([link], inputs=kinds(A), outputs=kinds(A, B))

    assert composition.order == (link,)


def test_computing_returns_an_input_that_is_also_an_output_unchanged() -> None:
    link, entered = Link(A, B), Artifact(C, D("7.25"))

    worksheet = Composition([link], inputs=kinds(A, C), outputs=kinds(B, C)).compute(
        Artifact(A, D(5)), entered
    )

    assert worksheet.get(C) == entered
    assert worksheet.producer_of(C) is None
    assert worksheet.get(B) == Artifact(B, D(5))
    assert worksheet.trace == (TaggedLine("link", D(5)),)


def test_still_rejects_an_input_nothing_consumes_when_only_another_kind_is_the_output() -> None:
    with pytest.raises(InvalidCompositionError, match="input 'c' is consumed by nothing"):
        Composition([Link(A, B)], inputs=kinds(A, C), outputs=kinds(B, E))


def test_still_rejects_an_input_a_capability_produces_even_when_it_is_a_declared_output() -> None:
    with pytest.raises(InvalidCompositionError, match="input 'b' is also produced by Link"):
        Composition([Link(A, B)], inputs=kinds(A, B), outputs=kinds(B))


def test_accepts_a_capability_that_consumes_nothing_while_its_output_is_consumed() -> None:
    constant, join = Constant(B, D(5), "b"), Join(A, B, C)

    composition = Composition([join, constant], inputs=kinds(A), outputs=kinds(C))

    assert composition.order == (constant, join)


def test_a_capability_that_consumes_nothing_may_produce_a_declared_output() -> None:
    constant, link = Constant(B, D(5), "b"), Link(A, C)

    composition = Composition([link, constant], inputs=kinds(A), outputs=kinds(B, C))

    assert set(composition.order) == {constant, link}


def test_a_capability_that_consumes_nothing_is_an_orphan_if_nothing_consumes_its_output() -> None:
    with pytest.raises(InvalidCompositionError, match="orphan output 'b': produced by Constant"):
        Composition([Link(A, C), Constant(B)], inputs=kinds(A), outputs=kinds(C))


def test_a_composition_of_only_capabilities_that_consume_nothing_takes_no_inputs() -> None:
    constant = Constant(B, D(5), "b")
    composition = Composition([constant], inputs=kinds(), outputs=kinds(B))

    worksheet = composition.compute()

    assert worksheet.get(B) == Artifact(B, D(5))
    assert worksheet.producer_of(B) is constant


def test_compute_runs_a_capability_that_consumes_nothing_before_its_consumer() -> None:
    constant, join = Constant(B, D(5), "b"), Join(A, B, C, D(1), "c")
    composition = Composition([join, constant], inputs=kinds(A), outputs=kinds(C))

    worksheet = composition.compute(Artifact(A, D(2)))

    assert worksheet.get(C) == Artifact(C, D(8))
    assert worksheet.trace == (TaggedLine("b", D(5)), TaggedLine("c", D(8)))


def test_rejects_a_capability_that_produces_nothing() -> None:
    with pytest.raises(InvalidCompositionError, match="Sink produces nothing"):
        Composition([Link(A, B), Sink(A)], inputs=kinds(A), outputs=kinds(B))


def test_naming_duplicate_producers_does_not_depend_on_the_order_given() -> None:
    left, right = Left(A, B), Right(A, B)
    messages = set()

    for given in ([left, right], [right, left]):
        with pytest.raises(InvalidCompositionError, match="more than one") as raised:
            Composition(given, inputs=kinds(A), outputs=kinds(B))
        messages.add(str(raised.value))

    assert len(messages) == 1


def test_naming_an_unsatisfied_consume_does_not_depend_on_the_order_given() -> None:
    needs_e, needs_f = LeftJoin(A, E, B), RightJoin(A, F, C)
    messages = set()

    for given in ([needs_e, needs_f], [needs_f, needs_e]):
        with pytest.raises(InvalidCompositionError, match="no producer") as raised:
            Composition(given, inputs=kinds(A), outputs=kinds(B, C))
        messages.add(str(raised.value))

    assert len(messages) == 1


def test_invalid_composition_is_a_domain_error() -> None:
    assert issubclass(InvalidCompositionError, DomainError)


# --- derived order -------------------------------------------------------------------------------


def test_order_is_derived_from_contracts_whatever_order_capabilities_are_given_in() -> None:
    chain: tuple[Capability, ...] = (
        Link(A, B, tag="1"),
        Link(B, C, tag="2"),
        Link(C, E, tag="3"),
        Link(E, F, tag="4"),
    )

    for given in permutations(chain):
        composition = Composition(given, inputs=kinds(A), outputs=kinds(F))

        assert composition.order == chain


def test_order_of_a_diamond_is_the_same_for_every_input_order() -> None:
    left, right, join = Left(A, B), Right(A, C), Join(B, C, E)

    for given in permutations((left, right, join)):
        composition = Composition(given, inputs=kinds(A), outputs=kinds(E))

        assert composition.order == (left, right, join)


def test_ties_are_broken_by_class_name_when_unregistered() -> None:
    apple, zebra = Apple(A, C), Zebra(A, B)

    for given in ([apple, zebra], [zebra, apple]):
        composition = Composition(given, inputs=kinds(A), outputs=kinds(B, C))

        assert composition.order == (apple, zebra)


def test_ties_are_broken_by_registered_identifier(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = CapabilityRegistry()
    registry.register("ex/first", Zebra)
    registry.register("ex/second", Apple)
    monkeypatch.setattr(CapabilityRegistry, "shared", classmethod(lambda cls: registry))
    apple, zebra = Apple(A, C), Zebra(A, B)

    for given in ([apple, zebra], [zebra, apple]):
        composition = Composition(given, inputs=kinds(A), outputs=kinds(B, C))

        assert composition.order == (zebra, apple)


def test_ties_between_instances_of_one_class_are_broken_by_what_they_produce() -> None:
    to_c, to_b = Link(A, C), Link(A, B)

    for given in ([to_c, to_b], [to_b, to_c]):
        composition = Composition(given, inputs=kinds(A), outputs=kinds(B, C))

        assert composition.order == (to_b, to_c)


def test_ties_between_kinds_sharing_an_identifier_are_broken_by_value_type() -> None:
    b_as_int = ArtifactKind("ex/b", int)
    to_decimal, to_int = Link(A, B), IntLink(A, b_as_int)

    for given in ([to_decimal, to_int], [to_int, to_decimal]):
        composition = Composition(given, inputs=kinds(A), outputs=kinds(B, b_as_int))

        assert composition.order == (to_decimal, to_int)


def test_order_is_a_read_only_tuple() -> None:
    composition = Composition([Link(A, B)], inputs=kinds(A), outputs=kinds(B))

    assert_type(composition.order, tuple[Capability, ...])
    assert isinstance(composition.order, tuple)
    with pytest.raises(AttributeError):
        cast(Any, composition).order = ()


# --- compute -------------------------------------------------------------------------------------


def chain_composition() -> tuple[Composition, Link, Link]:
    first, second = Link(A, B, D(1), "first"), Link(B, C, D(10), "second")
    return Composition([second, first], inputs=kinds(A), outputs=kinds(C)), first, second


def test_compute_runs_the_capabilities_in_order_and_returns_the_worksheet() -> None:
    composition, first, second = chain_composition()

    worksheet = composition.compute(Artifact(A, D(2)))

    assert_type(worksheet, Worksheet)
    assert worksheet.get(C) == Artifact(C, D(13))
    assert worksheet.get(A) == Artifact(A, D(2))
    assert worksheet.producer_of(A) is None
    assert worksheet.producer_of(B) is first
    assert worksheet.producer_of(C) is second
    assert worksheet.trace == (TaggedLine("first", D(3)), TaggedLine("second", D(13)))


def test_compute_follows_a_diamond() -> None:
    left, right = Left(A, B, D(1), "left"), Right(A, C, D(2), "right")
    join = Join(B, C, E, tag="join")
    composition = Composition([join, right, left], inputs=kinds(A), outputs=kinds(E))

    worksheet = composition.compute(Artifact(A, D(5)))

    assert worksheet.get(E) == Artifact(E, D(13))
    assert worksheet.trace == (
        TaggedLine("left", D(6)),
        TaggedLine("right", D(7)),
        TaggedLine("join", D(13)),
    )


def test_each_compute_gets_a_fresh_worksheet() -> None:
    composition, _, _ = chain_composition()

    once = composition.compute(Artifact(A, D(2)))
    again = composition.compute(Artifact(A, D(5)))

    assert once is not again
    assert once.get(C) == Artifact(C, D(13))
    assert again.get(C) == Artifact(C, D(16))
    assert len(once.trace) == 2


def test_compute_takes_several_inputs() -> None:
    composition = Composition([Join(A, B, C)], inputs=kinds(A, B), outputs=kinds(C))

    worksheet = composition.compute(Artifact(B, D(4)), Artifact(A, D(3)))

    assert worksheet.get(C) == Artifact(C, D(7))


def test_compute_rejects_a_missing_input() -> None:
    composition = Composition([Join(A, B, C)], inputs=kinds(A, B), outputs=kinds(C))

    with pytest.raises(InvalidCompositionError, match="'b'"):
        composition.compute(Artifact(A, D(3)))


def test_compute_rejects_an_extra_starting_artifact() -> None:
    composition, _, _ = chain_composition()

    with pytest.raises(InvalidCompositionError, match="'e'"):
        composition.compute(Artifact(A, D(2)), Artifact(E, D(1)))


def test_compute_names_several_extra_starting_artifacts_grammatically() -> None:
    composition, _, _ = chain_composition()

    with pytest.raises(InvalidCompositionError, match="'c', 'e' are not inputs"):
        composition.compute(Artifact(A, D(2)), Artifact(E, D(1)), Artifact(C, D(1)))


def test_compute_names_the_value_type_of_a_starting_artifact_of_the_wrong_type() -> None:
    composition, _, _ = chain_composition()

    with pytest.raises(InvalidCompositionError, match="'a'") as raised:
        composition.compute(Artifact(ArtifactKind("ex/a", int), 2))

    message = str(raised.value)
    assert "int" in message
    assert "Decimal" in message


def test_sort_key_orders_by_identifier_then_value_type_name() -> None:
    as_int = ArtifactKind("ex/a", int)

    unordered: list[ArtifactKind[Any]] = [B, as_int, A]

    ordered = sorted(unordered, key=Composition.sort_key)

    assert ordered == [A, as_int, B]
    assert Composition.sort_key(as_int) == ("ex/a", "int")


def test_labels_are_distinct_sorted_and_quoted() -> None:
    assert ArtifactKind.labels([B, A, B]) == f"{A.label!r}, {B.label!r}"
    assert ArtifactKind.labels([]) == ""


def test_check_starting_kinds_accepts_exactly_the_inputs() -> None:
    Composition.check_starting_kinds(iter([B, A]), kinds(A, B))


def test_check_starting_kinds_names_one_extra_kind() -> None:
    with pytest.raises(InvalidCompositionError) as raised:
        Composition.check_starting_kinds([A, E], kinds(A))

    assert str(raised.value) == f"{E.label!r} is not an input of this composition"


def test_check_starting_kinds_names_several_extra_kinds() -> None:
    with pytest.raises(InvalidCompositionError) as raised:
        Composition.check_starting_kinds([A, E, C], kinds(A))

    assert str(raised.value) == (f"{C.label!r}, {E.label!r} are not inputs of this composition")


def test_check_starting_kinds_names_missing_inputs_grammatically() -> None:
    with pytest.raises(InvalidCompositionError) as one:
        Composition.check_starting_kinds([A], kinds(A, B))
    with pytest.raises(InvalidCompositionError) as several:
        Composition.check_starting_kinds([], kinds(A, B))

    assert str(one.value) == f"missing input {B.label!r}"
    assert str(several.value) == f"missing inputs {A.label!r}, {B.label!r}"


def test_check_starting_kinds_reports_extra_before_missing() -> None:
    with pytest.raises(InvalidCompositionError, match="is not an input"):
        Composition.check_starting_kinds([E], kinds(A))


def test_value_type_hints_name_the_type_the_input_takes() -> None:
    as_int = ArtifactKind("ex/a", int)

    hints = Composition.value_type_hints([as_int, E], kinds(A))

    assert hints == f"; {as_int.label!r} was given as int but the input takes Decimal"


def test_value_type_hints_are_empty_without_a_shared_identifier() -> None:
    assert Composition.value_type_hints([E], kinds(A)) == ""


def test_compute_rejects_a_starting_artifact_the_composition_produces() -> None:
    composition, _, _ = chain_composition()

    with pytest.raises(InvalidCompositionError, match="'b'"):
        composition.compute(Artifact(A, D(2)), Artifact(B, D(1)))


def test_compute_rejects_two_values_for_one_input() -> None:
    composition, _, _ = chain_composition()

    with pytest.raises(DuplicateArtifactError, match="'a'"):
        composition.compute(Artifact(A, D(2)), Artifact(A, D(3)))


# --- non-negative kinds ------------------------------------------------------------------------

NON_NEGATIVE_A = ArtifactKind("ex/g", Decimal, non_negative=True)
NON_NEGATIVE_B = ArtifactKind("ex/h", Decimal, non_negative=True)


def test_compute_rejects_a_negative_input_for_a_non_negative_kind_naming_the_kind() -> None:
    composition = Composition(
        [Link(NON_NEGATIVE_A, C)], inputs=kinds(NON_NEGATIVE_A), outputs=kinds(C)
    )

    with pytest.raises(NegativeArtifactError, match=r"ex/g.*-1"):
        composition.compute(Artifact(NON_NEGATIVE_A, D("-1")))


def test_a_negative_input_is_a_negative_artifact_error_not_a_contract_error() -> None:
    composition = Composition(
        [Link(NON_NEGATIVE_A, C)], inputs=kinds(NON_NEGATIVE_A), outputs=kinds(C)
    )

    with pytest.raises(NegativeArtifactError) as raised:
        composition.compute(Artifact(NON_NEGATIVE_A, D("-1")))

    assert type(raised.value) is NegativeArtifactError


def negative_output_composition() -> Composition:
    """`ex/a` + -5 into the non-negative `ex/h`: negative for any `ex/a` below 5."""
    return Composition(
        [Link(A, NON_NEGATIVE_B, D("-5"))], inputs=kinds(A), outputs=kinds(NON_NEGATIVE_B)
    )


def test_compute_rejects_a_capability_producing_a_negative_value_for_a_non_negative_kind() -> None:
    with pytest.raises(CapabilityContractError):
        negative_output_composition().compute(Artifact(A, D(1)))


def test_a_produced_negative_names_the_capability_the_kind_and_the_value() -> None:
    with pytest.raises(CapabilityContractError) as raised:
        negative_output_composition().compute(Artifact(A, D(1)))

    assert str(raised.value) == "Link produced ex/h -4, which cannot be negative"


def test_a_produced_negative_gives_the_value_as_it_was_produced() -> None:
    with pytest.raises(CapabilityContractError) as raised:
        negative_output_composition().compute(Artifact(A, D("1.00")))

    assert str(raised.value) == "Link produced ex/h -4.00, which cannot be negative"


def test_a_produced_negative_names_the_capability_that_produced_it() -> None:
    composition = Composition(
        [Apple(A, B), Zebra(B, NON_NEGATIVE_B, D("-5"))],
        inputs=kinds(A),
        outputs=kinds(NON_NEGATIVE_B),
    )

    with pytest.raises(CapabilityContractError) as raised:
        composition.compute(Artifact(A, D(1)))

    assert str(raised.value) == "Zebra produced ex/h -4, which cannot be negative"


def test_a_produced_negative_is_chained_from_the_negative_artifact_error() -> None:
    with pytest.raises(CapabilityContractError) as raised:
        negative_output_composition().compute(Artifact(A, D(1)))

    assert isinstance(raised.value.__cause__, NegativeArtifactError)
    assert "ex/h" in str(raised.value.__cause__)


def test_a_produced_negative_is_not_a_negative_artifact_error() -> None:
    with pytest.raises(CapabilityContractError) as raised:
        negative_output_composition().compute(Artifact(A, D(1)))

    assert not isinstance(raised.value, NegativeArtifactError)


def test_a_produced_negative_returns_no_worksheet() -> None:
    worksheet: Worksheet | None = None

    with pytest.raises(CapabilityContractError):
        worksheet = negative_output_composition().compute(Artifact(A, D(1)))

    assert worksheet is None


def test_a_contract_error_and_a_negative_artifact_error_are_distinct_types() -> None:
    assert not issubclass(CapabilityContractError, NegativeArtifactError)
    assert not issubclass(NegativeArtifactError, CapabilityContractError)


def test_an_input_above_its_bound_is_not_wrapped_as_a_contract_error() -> None:
    composition = Composition([AtMost(A, B, C)], inputs=kinds(A, B), outputs=kinds(C))

    with pytest.raises(InputAboveBoundError) as raised:
        composition.compute(Artifact(A, D(3)), Artifact(B, D(2)))

    assert type(raised.value) is InputAboveBoundError


def test_compute_accepts_zero_for_a_non_negative_kind() -> None:
    composition = Composition(
        [Link(NON_NEGATIVE_A, NON_NEGATIVE_B, D("-5"))],
        inputs=kinds(NON_NEGATIVE_A),
        outputs=kinds(NON_NEGATIVE_B),
    )

    worksheet = composition.compute(Artifact(NON_NEGATIVE_A, D(5)))

    assert worksheet.get(NON_NEGATIVE_B).value == ZERO


def test_compute_lets_an_unconstrained_kind_go_negative() -> None:
    composition = Composition([Link(A, B, D("-5"))], inputs=kinds(A), outputs=kinds(B))

    worksheet = composition.compute(Artifact(A, D(1)))

    assert worksheet.get(B) == Artifact(B, D(-4))


# --- end to end, with made-up data ---------------------------------------------------------------

TAXABLE_BASE = ArtifactKind("ex/taxable_base", Decimal)
BASIC_TAX = ArtifactKind("ex/basic_tax", Decimal)
TAX_AFTER_CREDIT = ArtifactKind("ex/tax_after_credit", Decimal)
CREDIT_AMOUNTS = ArtifactKind("ex/credit_amounts", Decimal)
CREDIT = ArtifactKind("ex/credit", Decimal)

SOURCES = ("https://example.org/2025",)
SCHEDULE = ParameterDataset(
    "ex/brackets",
    2025,
    BRACKETS,
    BracketSchedule(
        (
            Bracket(D(0), D("0.10")),
            Bracket(D(100), D("0.20")),
            Bracket(D(300), D("0.30")),
        )
    ),
    NO_ROUNDING,
    SOURCES,
)
CREDIT_RATE = ParameterDataset("ex/credit_rate", 2025, RATE, Rate(D("0.15")), NO_ROUNDING, SOURCES)


def test_end_to_end_three_real_capabilities_given_in_the_wrong_order() -> None:
    tax = ProgressiveTax(TAXABLE_BASE, BASIC_TAX, SCHEDULE)
    credit = ApplyRate(CREDIT_RATE, CREDIT_AMOUNTS, CREDIT)  # 15% of 400 = 60
    less = SubtractNotBelowZero(BASIC_TAX, CREDIT, TAX_AFTER_CREDIT)
    composition = Composition(
        [less, credit, tax],
        inputs=kinds(TAXABLE_BASE, CREDIT_AMOUNTS),
        outputs=kinds(TAX_AFTER_CREDIT),
    )

    worksheet = composition.compute(
        Artifact(TAXABLE_BASE, D(500)), Artifact(CREDIT_AMOUNTS, D(400))
    )

    # 30% of (500 - 300) + 50.00 = 110; less a credit of 15% of 400 = 60.
    assert composition.order[-1] is less
    assert set(composition.order) == {tax, credit, less}
    assert worksheet.get(BASIC_TAX) == Artifact(BASIC_TAX, D(110))
    assert worksheet.get(CREDIT) == Artifact(CREDIT, D(60))
    assert worksheet.get(TAX_AFTER_CREDIT) == Artifact(TAX_AFTER_CREDIT, D(50))
    assert worksheet.producer_of(TAX_AFTER_CREDIT) is less
    assert worksheet.trace[-1].amount == D(50)
    (total,) = [line for line in worksheet.trace if isinstance(line, RoundedTotalLine)]
    assert total.amount == D(110)
    (column,) = [line for line in worksheet.trace if isinstance(line, BracketColumnLine)]
    assert column == BracketColumnLine(D(300), D("0.30"), D(200), D("50.00"), D(110))


# --- list slots: one edge per listed kind ---------------------------------------------------------
#
# The list-slot class is defined inside a cached factory, so a class definition the base rejects
# fails the tests that use it rather than the collection of this whole module.


@cache
def total_class() -> Any:
    class Total(Summing):
        """Consumes a list of `parts` and produces `target` = their sum + `add`."""

        CONSUMES = {"parts": list[Decimal]}
        PRODUCES = {"target": Decimal}

        def __init__(
            self,
            parts: tuple[Money, ...],
            target: Money,
            add: Decimal = ZERO,
            tag: str = "total",
        ) -> None:
            super().__init__(parts=parts, target=target, add=add, tag=tag)

    return Total


def test_a_list_slot_runs_after_every_producer_of_its_parts() -> None:
    to_b, to_c, to_e = Link(A, B, D(1), "b"), Link(A, C, D(2), "c"), Link(A, E, D(3), "e")
    total = total_class()((E, B, C), F)

    for given in permutations((total, to_b, to_c, to_e)):
        composition = Composition(given, inputs=kinds(A), outputs=kinds(F))

        assert composition.order == (to_b, to_c, to_e, total)


def test_a_list_slot_after_a_chain_runs_after_its_last_link() -> None:
    to_b, to_c = Link(A, B, tag="b"), Link(B, C, tag="c")
    total = total_class()((A, C), E)

    for given in permutations((total, to_c, to_b)):
        composition = Composition(given, inputs=kinds(A), outputs=kinds(E))

        assert composition.order == (to_b, to_c, total)


def test_compute_sums_every_listed_part() -> None:
    to_b, to_c, to_e = Link(A, B, D(1), "b"), Link(A, C, D(2), "c"), Link(A, E, D(3), "e")
    total = total_class()((E, B, C), F)
    composition = Composition([total, to_e, to_c, to_b], inputs=kinds(A), outputs=kinds(F))

    worksheet = composition.compute(Artifact(A, D(1)))

    # (1 + 1) + (1 + 2) + (1 + 3) = 9
    assert worksheet.get(F) == Artifact(F, D(9))
    assert worksheet.producer_of(F) is total
    assert worksheet.trace[-1] == TaggedLine("total", D(9))


def test_a_listed_part_may_be_an_input() -> None:
    to_b = Link(A, B, D(1), "b")
    total = total_class()((A, B), C)
    composition = Composition([total, to_b], inputs=kinds(A), outputs=kinds(C))

    worksheet = composition.compute(Artifact(A, D(2)))

    assert composition.order == (to_b, total)
    assert worksheet.get(C) == Artifact(C, D(5))


def test_a_list_slot_with_no_parts_runs_and_produces_zero() -> None:
    to_b = Link(A, B, tag="b")
    empty = total_class()((), C)
    composition = Composition([empty, to_b], inputs=kinds(A), outputs=kinds(B, C))

    worksheet = composition.compute(Artifact(A, D(2)))

    assert worksheet.get(C) == Artifact(C, ZERO)


def test_rejects_a_listed_kind_nothing_produces() -> None:
    total = total_class()((B, E), F)

    with pytest.raises(InvalidCompositionError, match="no producer for 'e', consumed by Total"):
        Composition([Link(A, B), total], inputs=kinds(A), outputs=kinds(F))


def test_rejects_a_cycle_through_a_listed_kind() -> None:
    total = total_class()((A, C), B)

    with pytest.raises(InvalidCompositionError, match="cycle involving 'b', 'c'"):
        Composition([total, Link(B, C)], inputs=kinds(A), outputs=kinds(C))


def test_a_listed_kind_counts_as_consumed() -> None:
    # Neither an unused input nor an orphan output: each listed kind is consumed.
    to_b = Link(A, B, tag="b")
    total = total_class()((A, B, C), E)

    composition = Composition([to_b, total], inputs=kinds(A, C), outputs=kinds(E))

    assert composition.order == (to_b, total)


def test_ties_between_list_slot_capabilities_are_broken_by_what_they_produce() -> None:
    to_b, to_c = Link(A, B, tag="b"), Link(A, C, tag="c")
    total = total_class()
    to_f, to_e = total((B, C), F, tag="f"), total((C, B), E, tag="e")

    for given in permutations((to_f, to_c, to_e, to_b)):
        composition = Composition(given, inputs=kinds(A), outputs=kinds(E, F))

        assert composition.order == (to_b, to_c, to_e, to_f)


# --- the Inexact trap -------------------------------------------------------------------------
#
# `compute` runs every capability under a decimal context that traps `decimal.Inexact` (the trap
# sits in `Worksheet.apply`, which `compute` calls for each capability): arithmetic that would lose
# digits raises instead of being silently rounded to 28 significant digits. The error is a
# `CapabilityContractError` naming the capability, chained from the `decimal.Inexact`.

FIFTEEN_DIGITS = D("123456789012345")
EIGHTEEN_DIGITS = D("123456789012345678")


class Multiply(Capability):
    """Consumes `source` and produces `target` = `source` × `factor`, which can need many digits."""

    CONSUMES = {"source": Decimal}
    PRODUCES = {"target": Decimal}

    def __init__(self, source: Money, target: Money, factor: Decimal) -> None:
        super().__init__(source=source, target=target)
        self._source, self._target, self._factor = source, target, factor

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        total = self._input(inputs, self._source).value * self._factor
        return CapabilityResult(
            outputs=(Artifact(self._target, total),), trace=(TaggedLine("multiply", total),)
        )


def inexact_composition() -> Composition:
    """`ex/a` × a 18-digit factor: 15 × 18 digits is more than the context's 28."""
    return Composition([Multiply(A, B, EIGHTEEN_DIGITS)], inputs=kinds(A), outputs=kinds(B))


def test_compute_fails_loudly_when_a_capability_needs_more_digits_than_the_context_holds() -> None:
    with pytest.raises(CapabilityContractError):
        inexact_composition().compute(Artifact(A, FIFTEEN_DIGITS))


def test_an_inexact_result_names_the_capability_and_says_it_was_inexact() -> None:
    with pytest.raises(CapabilityContractError, match=r"^Multiply .*inexact"):
        inexact_composition().compute(Artifact(A, FIFTEEN_DIGITS))


def test_an_inexact_result_names_the_capability_that_did_it_not_an_earlier_one() -> None:
    composition = Composition(
        [Apple(A, B), Multiply(B, C, EIGHTEEN_DIGITS)], inputs=kinds(A), outputs=kinds(C)
    )

    with pytest.raises(CapabilityContractError, match=r"^Multiply .*inexact"):
        composition.compute(Artifact(A, FIFTEEN_DIGITS))


def test_an_inexact_result_is_chained_from_decimal_inexact() -> None:
    with pytest.raises(CapabilityContractError) as raised:
        inexact_composition().compute(Artifact(A, FIFTEEN_DIGITS))

    assert isinstance(raised.value.__cause__, decimal.Inexact)


def test_an_inexact_result_is_a_domain_error_not_a_bare_decimal_inexact() -> None:
    with pytest.raises(CapabilityContractError) as raised:
        inexact_composition().compute(Artifact(A, FIFTEEN_DIGITS))

    assert isinstance(raised.value, DomainError)
    assert not isinstance(raised.value, decimal.Inexact)


def test_an_inexact_result_returns_no_worksheet() -> None:
    worksheet: Worksheet | None = None

    with pytest.raises(CapabilityContractError):
        worksheet = inexact_composition().compute(Artifact(A, FIFTEEN_DIGITS))

    assert worksheet is None


def test_a_product_of_exactly_28_digits_is_exact() -> None:
    composition = Composition(
        [Multiply(A, B, D("99999999999999"))], inputs=kinds(A), outputs=kinds(B)
    )

    worksheet = composition.compute(Artifact(A, D("99999999999999")))

    assert worksheet.get(B) == Artifact(B, D("9999999999999800000000000001"))


def test_a_short_exact_product_is_unaffected() -> None:
    worksheet = Composition([Multiply(A, B, D("0.25"))], inputs=kinds(A), outputs=kinds(B)).compute(
        Artifact(A, D("10.5"))
    )

    assert worksheet.get(B) == Artifact(B, D("2.625"))


def test_compute_leaves_the_callers_decimal_context_untrapped() -> None:
    with pytest.raises(CapabilityContractError):
        inexact_composition().compute(Artifact(A, FIFTEEN_DIGITS))

    assert not decimal.getcontext().traps[decimal.Inexact]
    assert decimal.getcontext().prec == 28
    assert D(1) / D(3) == D("0.3333333333333333333333333333")


def test_a_rounding_rule_still_rounds_inside_compute() -> None:
    from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

    class RoundedLink(Link):
        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            total = RoundTo(D("0.01"), RoundingMode.HALF_UP).apply(self._input(inputs, A).value)
            return CapabilityResult(
                outputs=(Artifact(B, total),), trace=(TaggedLine("rounded", total),)
            )

    composition = Composition([RoundedLink(A, B)], inputs=kinds(A), outputs=kinds(B))

    worksheet = composition.compute(Artifact(A, D("0.1234567890123456789012345678901234")))

    assert worksheet.get(B) == Artifact(B, D("0.12"))


def test_the_trap_covers_a_capability_late_in_the_order() -> None:
    composition = Composition(
        [Link(A, B), Link(B, C), Multiply(C, E, EIGHTEEN_DIGITS)],
        inputs=kinds(A),
        outputs=kinds(E),
    )

    with pytest.raises(CapabilityContractError, match=r"^Multiply .*inexact"):
        composition.compute(Artifact(A, FIFTEEN_DIGITS))
