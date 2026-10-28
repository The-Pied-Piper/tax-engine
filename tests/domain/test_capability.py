"""Unit tests for the Capability base: its slots and how it reads its inputs (design.md §3).

A capability class declares three read-only slot mappings: `PARAMETERS` (slot -> parameter kind),
`CONSUMES` and `PRODUCES` (slot -> artifact value type). Subclasses may assign plain dicts; the
base exposes every mapping as a `MappingProxyType`, empty when nothing is declared. When a subclass
is defined, the base checks that every slot name is snake_case, unique across the three mappings,
and a keyword parameter of the constructor; otherwise it raises `InvalidCapabilityError` naming
the class and the slot.

A capability is built by passing its artifact slot kinds, by name, to `Capability.__init__`, which
derives `consumes` and `produces` from them; subclasses do not define those. Construction checks
every `CONSUMES` / `PRODUCES` slot is given, no other name is, each kind's value type is exactly the
slot's, and no kind fills two slots; otherwise it raises `InvalidCapabilityError` naming the class
and the slot. Names and values are made up.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from decimal import Decimal
from functools import cache
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult
from tax_calculator.domain.errors import (
    CapabilityContractError,
    DomainError,
    DuplicateArtifactError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rounding import NO_ROUNDING

D = Decimal
IN = ArtifactKind("ex/in", Decimal)
OTHER = ArtifactKind("ex/other", Decimal)
OUT = ArtifactKind("ex/out", Decimal)
FACTOR = ParameterKind("factor", Decimal)
OFFSET = ParameterKind("offset", Decimal)


class Bare(Capability):
    """Declares no slots and defines nothing but `compute`."""

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        return CapabilityResult(outputs=(), trace=())


class Reader(Capability):
    """Consumes `first` and `second`, produces `output`; `read` returns what `_input` finds."""

    CONSUMES = {"first": Decimal, "second": Decimal}
    PRODUCES = {"output": Decimal}

    def __init__(self, first: Money = IN, second: Money = OTHER, output: Money = OUT) -> None:
        super().__init__(first=first, second=second, output=output)

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        return CapabilityResult(outputs=(Artifact(OUT, self._input(inputs, IN).value),), trace=())

    def read[V](self, inputs: tuple[Artifact[Any], ...], kind: ArtifactKind[V]) -> Artifact[V]:
        return self._input(inputs, kind)


class Scale(Capability):
    """Produces `target` = `source` × `factor` + `offset`; declares every kind of slot."""

    PARAMETERS = {"factor": FACTOR, "offset": OFFSET}
    CONSUMES = {"source": Decimal}
    PRODUCES = {"target": Decimal}

    def __init__(
        self,
        source: Money,
        target: Money,
        factor: ParameterDataset[Decimal],
        *,
        offset: ParameterDataset[Decimal],
    ) -> None:
        super().__init__(source=source, target=target)
        self._source, self._target = source, target
        self._factor, self._offset = factor, offset

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        value = self._input(inputs, self._source).value * self._factor.values + self._offset.values
        return CapabilityResult(outputs=(Artifact(self._target, value),), trace=())


class Split(Capability):
    """Consumes `source` and produces it twice, as `low` and `high`."""

    CONSUMES = {"source": Decimal}
    PRODUCES = {"low": Decimal, "high": Decimal}

    def __init__(self, source: Money, low: Money, high: Money) -> None:
        super().__init__(source=source, low=low, high=high)

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        return CapabilityResult(outputs=(), trace=())


class Cents(Decimal):
    """A made-up Decimal subtype: not the slot's type, so not accepted for a Decimal slot."""


def dataset(kind: ParameterKind[Decimal], value: int) -> ParameterDataset[Decimal]:
    return ParameterDataset(f"ex/{kind.name}", 2025, kind, D(value), NO_ROUNDING, ("src",))


def scale(source: object = IN, target: object = OUT) -> Scale:
    """A Scale wired with `source` and `target`, unchecked by mypy so tests can give bad kinds."""
    return Scale(
        cast(Any, source), cast(Any, target), dataset(FACTOR, 2), offset=dataset(OFFSET, 1)
    )


# --- reading inputs -------------------------------------------------------------------------


def test_input_finds_the_artifact_of_the_kind() -> None:
    inputs = (Artifact(OTHER, D(2)), Artifact(IN, D(1)))

    found = Reader().read(inputs, IN)

    assert_type(found, Artifact[Decimal])
    assert found == Artifact(IN, D(1))


def test_input_matches_by_kind_equality_not_identity() -> None:
    inputs = (Artifact(ArtifactKind("ex/in", Decimal), D(1)),)

    assert Reader().read(inputs, IN) == Artifact(IN, D(1))


def test_input_rejects_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="Reader needs 'in'"):
        Reader().read((Artifact(OTHER, D(2)),), IN)


def test_input_rejects_two_artifacts_of_one_kind() -> None:
    with pytest.raises(DuplicateArtifactError, match="Reader got 2 values for 'in'"):
        Reader().read((Artifact(IN, D(1)), Artifact(IN, D(2))), IN)


def test_input_refuses_a_kind_the_capability_does_not_consume() -> None:
    with pytest.raises(CapabilityContractError, match="Reader does not consume 'out'"):
        Reader().read((Artifact(OUT, D(1)),), OUT)


def test_compute_returns_artifacts() -> None:
    result = Reader().compute((Artifact(IN, D(3)), Artifact(OTHER, D(4))))

    assert result.outputs == (Artifact(OUT, D(3)),)


# --- declared slots -------------------------------------------------------------------------


def test_the_base_declares_no_slots() -> None:
    for slots in (Capability.PARAMETERS, Capability.CONSUMES, Capability.PRODUCES):
        assert isinstance(slots, MappingProxyType)
        assert slots == {}


def test_a_capability_declaring_nothing_has_empty_slots() -> None:
    assert Bare.PARAMETERS == {}
    assert Bare.CONSUMES == {}
    assert Bare.PRODUCES == {}


def test_slot_mappings_are_typed() -> None:
    assert_type(Capability.PARAMETERS, Mapping[str, ParameterKind[Any]])
    assert_type(Capability.CONSUMES, Mapping[str, type])
    assert_type(Capability.PRODUCES, Mapping[str, type])


def test_declared_slots_are_exposed() -> None:
    assert Scale.PARAMETERS == {"factor": FACTOR, "offset": OFFSET}
    assert Scale.CONSUMES == {"source": Decimal}
    assert Scale.PRODUCES == {"target": Decimal}


def test_declared_slots_are_read_only() -> None:
    for slots in (Scale.PARAMETERS, Scale.CONSUMES, Scale.PRODUCES):
        assert isinstance(slots, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_a_capability_is_built_from_its_slot_names_as_keywords() -> None:
    arguments: dict[str, Any] = {
        "source": IN,
        "target": OUT,
        "factor": dataset(FACTOR, 2),
        "offset": dataset(OFFSET, 1),
    }

    scale = Scale(**arguments)

    assert set(arguments) == set(Scale.PARAMETERS) | set(Scale.CONSUMES) | set(Scale.PRODUCES)
    assert scale.compute((Artifact(IN, D(3)),)).outputs == (Artifact(OUT, D(7)),)


def test_a_subclass_inherits_its_parents_slots() -> None:
    class Child(Scale):
        pass

    assert Child.PARAMETERS == Scale.PARAMETERS
    assert Child.CONSUMES == Scale.CONSUMES
    assert Child.PRODUCES == Scale.PRODUCES
    child = Child(IN, OUT, dataset(FACTOR, 2), offset=dataset(OFFSET, 1))
    assert child.consumes == frozenset({IN})
    assert child.produces == frozenset({OUT})


# --- slots are checked when a class is defined ----------------------------------------------


def test_rejects_a_parameter_slot_the_constructor_does_not_take() -> None:
    with pytest.raises(InvalidCapabilityError, match="Typo.*'facter'"):

        class Typo(Bare):
            PARAMETERS = {"facter": FACTOR}

            def __init__(self, factor: ParameterDataset[Decimal]) -> None:
                self.factor = factor


def test_rejects_a_consumed_slot_the_constructor_does_not_take() -> None:
    with pytest.raises(InvalidCapabilityError, match="Typo.*'base'"):

        class Typo(Bare):
            CONSUMES = {"base": Decimal}

            def __init__(self, source: Money) -> None:
                self.source = source


def test_rejects_a_produced_slot_the_constructor_does_not_take() -> None:
    with pytest.raises(InvalidCapabilityError, match="Typo.*'output'"):

        class Typo(Bare):
            PRODUCES = {"output": Decimal}


def test_rejects_a_slot_that_is_a_positional_only_parameter() -> None:
    with pytest.raises(InvalidCapabilityError, match="Positional.*'source'"):

        class Positional(Bare):
            CONSUMES = {"source": Decimal}

            def __init__(self, source: Money, /) -> None:
                self.source = source


def test_rejects_an_inherited_slot_a_new_constructor_drops() -> None:
    with pytest.raises(InvalidCapabilityError, match="Narrower.*'offset'"):

        class Narrower(Scale):
            def __init__(
                self, source: Money, target: Money, factor: ParameterDataset[Decimal]
            ) -> None:
                super().__init__(source, target, factor, offset=factor)


def test_accepts_keyword_only_slots() -> None:
    class KeywordOnly(Bare):
        CONSUMES = {"source": Decimal}

        def __init__(self, *, source: Money) -> None:
            super().__init__(source=source)

    assert KeywordOnly.CONSUMES == {"source": Decimal}
    assert KeywordOnly(source=IN).consumes == frozenset({IN})


def _takes_upper(self: Capability, *, Source: Money) -> None:
    pass


def _takes_double_underscore(self: Capability, *, two__parts: Money) -> None:
    pass


def _takes_trailing_underscore(self: Capability, *, trailing_: Money) -> None:
    pass


def _takes_leading_underscore(self: Capability, *, _hidden: Money) -> None:
    pass


@pytest.mark.parametrize(
    ("slot", "init"),
    [
        ("Source", _takes_upper),
        ("two__parts", _takes_double_underscore),
        ("trailing_", _takes_trailing_underscore),
        ("_hidden", _takes_leading_underscore),
    ],
)
def test_rejects_a_slot_name_that_is_not_snake_case(slot: str, init: Callable[..., None]) -> None:
    # The constructor does take the slot, so only its name is wrong.
    with pytest.raises(InvalidCapabilityError, match=f"Odd.*{slot!r}.*snake_case"):
        type("Odd", (Bare,), {"CONSUMES": {slot: Decimal}, "__init__": init})


def test_a_constructor_beside_a_custom_new_is_still_checked() -> None:
    class WithNew(Bare):
        CONSUMES = {"base": Decimal}

        def __new__(cls, *args: object, **kwargs: object) -> WithNew:
            return super().__new__(cls)

        def __init__(self, base: Money) -> None:
            super().__init__(base=base)
            self.base = base

    assert WithNew.CONSUMES == {"base": Decimal}
    assert WithNew(IN).base == IN
    assert WithNew(IN).consumes == frozenset({IN})


def test_rejects_self_as_a_slot() -> None:
    with pytest.raises(InvalidCapabilityError, match="Selfish.*'self'"):

        class Selfish(Bare):
            CONSUMES = {"self": Decimal}

            def __init__(self, source: Money) -> None:
                self.source = source


def test_rejects_slots_a_constructor_takes_only_through_var_keywords() -> None:
    with pytest.raises(InvalidCapabilityError, match="Loose.*'source'"):

        class Loose(Bare):
            CONSUMES = {"source": Decimal}

            def __init__(self, **slots: Money) -> None:
                self.slots = slots


@pytest.mark.parametrize(
    ("mapping", "slots", "message"),
    [
        ("CONSUMES", {7: Decimal}, "Bad.*CONSUMES slot 7.*must be a string"),
        ("PARAMETERS", {"factor": Decimal}, "Bad.*PARAMETERS slot 'factor'.*ParameterKind"),
        ("CONSUMES", {"source": IN}, "Bad.*CONSUMES slot 'source'.*must be a type"),
        ("PRODUCES", {"target": "Decimal"}, "Bad.*PRODUCES slot 'target'.*must be a type"),
        ("PRODUCES", [("target", Decimal)], "Bad.*PRODUCES must be a mapping"),
    ],
)
def test_rejects_malformed_slot_declarations(mapping: str, slots: object, message: str) -> None:
    def init(self: Capability, factor: object, source: object, target: object) -> None:
        pass

    with pytest.raises(InvalidCapabilityError, match=message):
        type("Bad", (Bare,), {mapping: slots, "__init__": init})


@pytest.mark.parametrize(
    ("first", "second"),
    [("PARAMETERS", "CONSUMES"), ("PARAMETERS", "PRODUCES"), ("CONSUMES", "PRODUCES")],
)
def test_rejects_a_slot_name_used_in_two_mappings(first: str, second: str) -> None:
    slots: dict[str, Mapping[str, Any]] = {
        "PARAMETERS": {"value": FACTOR},
        "CONSUMES": {"value": Decimal},
        "PRODUCES": {"value": Decimal},
    }

    def init(self: Capability, value: object) -> None:
        pass

    namespace = {first: slots[first], second: slots[second], "__init__": init}
    with pytest.raises(InvalidCapabilityError, match="Twice.*'value'"):
        type("Twice", (Bare,), namespace)


# --- consumes and produces come from the artifact slots it is built with ------------------------


def test_consumes_and_produces_are_the_kinds_given_to_its_slots() -> None:
    reader = Reader()

    assert_type(reader.consumes, frozenset[ArtifactKind[Any]])
    assert_type(reader.produces, frozenset[ArtifactKind[Any]])
    assert reader.consumes == frozenset({IN, OTHER})
    assert reader.produces == frozenset({OUT})
    assert isinstance(reader.consumes, frozenset)
    assert isinstance(reader.produces, frozenset)


def test_consumes_and_produces_follow_the_wiring() -> None:
    wired = scale(OTHER, IN)

    assert wired.consumes == frozenset({OTHER})
    assert wired.produces == frozenset({IN})


def test_a_subclass_defines_neither_consumes_nor_produces() -> None:
    for cls in (Bare, Reader, Scale, Split):
        assert "consumes" not in vars(cls)
        assert "produces" not in vars(cls)


def test_only_compute_is_abstract() -> None:
    assert Capability.__abstractmethods__ == frozenset({"compute"})


def test_a_capability_without_slots_consumes_and_produces_nothing() -> None:
    bare = Bare()

    assert bare.consumes == frozenset()
    assert bare.produces == frozenset()


def test_a_capability_may_produce_nothing() -> None:
    class Drain(Capability):
        CONSUMES = {"source": Decimal}

        def __init__(self, source: Money) -> None:
            super().__init__(source=source)

        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            return CapabilityResult(outputs=(), trace=())

    drain = Drain(IN)

    assert drain.consumes == frozenset({IN})
    assert drain.produces == frozenset()


def test_a_capability_may_consume_nothing() -> None:
    class Grant(Capability):
        PARAMETERS = {"factor": FACTOR}
        PRODUCES = {"target": Decimal}

        def __init__(self, factor: ParameterDataset[Decimal], target: Money) -> None:
            super().__init__(target=target)
            self._factor, self._target = factor, target

        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            return CapabilityResult(
                outputs=(Artifact(self._target, self._factor.values),), trace=()
            )

    grant = Grant(dataset(FACTOR, 7), OUT)

    assert Grant.CONSUMES == {}
    assert grant.consumes == frozenset()
    assert grant.produces == frozenset({OUT})
    assert grant.compute(()).outputs == (Artifact(OUT, D(7)),)


def test_mypy_rejects_a_slot_filler_that_is_not_an_artifact_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # The base takes `**slots: ArtifactKind[Any]`; the ignore fails under mypy
        # (warn_unused_ignores) if a bare identifier is ever accepted.
        Bare(stray="ex/in")  # type: ignore[arg-type]

    assert callable(wire)


def test_a_capability_that_skips_the_base_constructor_fails_clearly() -> None:
    class Skipper(Capability):
        CONSUMES = {"source": Decimal}

        def __init__(self, source: Money) -> None:
            self.source = source

        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            return CapabilityResult(outputs=(), trace=())

    skipper = Skipper(IN)
    message = "Skipper: __init__ must pass its artifact slots to super().__init__"
    with pytest.raises(InvalidCapabilityError, match=re.escape(message)):
        _ = skipper.consumes
    with pytest.raises(InvalidCapabilityError, match=re.escape(message)):
        _ = skipper.produces


# --- artifact slots are checked when a capability is built ----------------------------------


def test_rejects_a_consumed_slot_not_given() -> None:
    class Forgetful(Capability):
        CONSUMES = {"source": Decimal}
        PRODUCES = {"target": Decimal}

        def __init__(self, source: Money, target: Money) -> None:
            super().__init__(target=target)

        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            return CapabilityResult(outputs=(), trace=())

    with pytest.raises(InvalidCapabilityError, match="Forgetful.*'source'"):
        Forgetful(IN, OUT)


def test_rejects_a_produced_slot_not_given() -> None:
    class Forgetful(Capability):
        CONSUMES = {"source": Decimal}
        PRODUCES = {"target": Decimal}

        def __init__(self, source: Money, target: Money) -> None:
            super().__init__(source=source)

        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            return CapabilityResult(outputs=(), trace=())

    with pytest.raises(InvalidCapabilityError, match="Forgetful.*'target'"):
        Forgetful(IN, OUT)


def test_rejects_a_name_that_is_not_an_artifact_slot() -> None:
    with pytest.raises(InvalidCapabilityError, match="Bare.*'stray'") as raised:
        Bare(stray=IN)

    assert "parameter slot" not in str(raised.value)


def test_rejects_a_parameter_slot_given_as_an_artifact_slot() -> None:
    class Confused(Scale):
        def __init__(
            self,
            source: Money,
            target: Money,
            factor: ParameterDataset[Decimal],
            *,
            offset: ParameterDataset[Decimal],
        ) -> None:
            Capability.__init__(self, source=source, target=target, factor=OTHER)

    with pytest.raises(
        InvalidCapabilityError, match=r"Confused.*'factor'.*\(it is a parameter slot\)"
    ):
        Confused(IN, OUT, dataset(FACTOR, 2), offset=dataset(OFFSET, 1))


@pytest.mark.parametrize("filler", ["ex/in", D(1), Decimal, None])
def test_rejects_a_slot_filled_with_something_other_than_an_artifact_kind(filler: object) -> None:
    with pytest.raises(InvalidCapabilityError, match="Scale.*'source'"):
        scale(source=filler)


def test_rejects_a_kind_of_another_value_type() -> None:
    with pytest.raises(InvalidCapabilityError, match="Scale.*'target'") as raised:
        scale(target=ArtifactKind("ex/count", int))

    message = str(raised.value)
    assert "int" in message
    assert "Decimal" in message


def test_rejects_a_kind_of_a_value_subtype() -> None:
    # Exact match, like the rest of the engine: a Cents kind is not a Decimal kind.
    with pytest.raises(InvalidCapabilityError, match="Scale.*'source'") as raised:
        scale(source=ArtifactKind("ex/cents", Cents))

    assert "Cents" in str(raised.value)


def test_rejects_consuming_the_kind_it_produces() -> None:
    with pytest.raises(InvalidCapabilityError, match="Scale") as raised:
        scale(source=IN, target=IN)

    message = str(raised.value)
    assert "'source'" in message
    assert "'target'" in message


def test_rejects_consuming_a_kind_equal_to_the_one_it_produces() -> None:
    with pytest.raises(InvalidCapabilityError, match="Scale"):
        scale(source=IN, target=ArtifactKind("ex/in", Decimal))


def test_rejects_producing_one_kind_twice() -> None:
    with pytest.raises(InvalidCapabilityError, match="Split") as raised:
        Split(IN, OUT, OUT)

    message = str(raised.value)
    assert "'low'" in message
    assert "'high'" in message


def test_rejects_consuming_one_kind_twice() -> None:
    with pytest.raises(InvalidCapabilityError, match="Reader") as raised:
        Reader(first=IN, second=IN)

    message = str(raised.value)
    assert "'first'" in message
    assert "'second'" in message


def test_rejects_an_int_kind_for_a_decimal_slot_even_when_it_shares_an_identifier() -> None:
    # Only the value type is checked against the slot, so this fails on the type, not as a reuse.
    with pytest.raises(InvalidCapabilityError, match="Scale.*'target'") as raised:
        scale(source=IN, target=ArtifactKind("ex/in", int))

    assert "int" in str(raised.value)


def test_kinds_sharing_an_identifier_but_not_a_value_type_may_fill_two_slots() -> None:
    # Distinct kinds, so not a reuse; the artifact registry prevents this for real catalogs.
    class Count(Capability):
        CONSUMES = {"source": Decimal}
        PRODUCES = {"count": int}

        def __init__(self, source: Money, count: ArtifactKind[int]) -> None:
            super().__init__(source=source, count=count)

        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            return CapabilityResult(outputs=(), trace=())

    as_decimal, as_int = ArtifactKind("ex/x", Decimal), ArtifactKind("ex/x", int)
    count = Count(as_decimal, as_int)

    assert count.consumes == frozenset({as_decimal})
    assert count.produces == frozenset({as_int})


def test_invalid_capability_is_a_domain_error() -> None:
    assert issubclass(InvalidCapabilityError, DomainError)


# --- list slots: a consumed slot that takes a list of kinds of one value type ------------------
#
# The list-slot classes are defined inside cached factories, so a class definition the base
# rejects fails the tests that use it rather than the collection of this whole module.

PART_A = ArtifactKind("ex/part_a", Decimal)
PART_B = ArtifactKind("ex/part_b", Decimal)
PART_C = ArtifactKind("ex/part_c", Decimal)


@cache
def total_class() -> Any:
    class Total(Capability):
        """Produces `total` = the sum of its `parts`, each read with `_input`, in their order."""

        CONSUMES = {"parts": list[Decimal]}
        PRODUCES = {"total": Decimal}

        def __init__(self, parts: tuple[Money, ...], total: Money) -> None:
            super().__init__(parts=parts, total=total)
            self.parts, self.total = parts, total

        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            value = sum((self._input(inputs, kind).value for kind in self.parts), D(0))
            return CapabilityResult(outputs=(Artifact(self.total, value),), trace=())

        def read[V](self, inputs: tuple[Artifact[Any], ...], kind: ArtifactKind[V]) -> Artifact[V]:
            return self._input(inputs, kind)

    return Total


@cache
def adjusted_class() -> Any:
    class Adjusted(Capability):
        """Consumes a single `base` and a list of `parts`; produces `total`."""

        CONSUMES = {"base": Decimal, "parts": list[Decimal]}
        PRODUCES = {"total": Decimal}

        def __init__(self, base: Money, parts: tuple[Money, ...], total: Money) -> None:
            super().__init__(base=base, parts=parts, total=total)

        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            return CapabilityResult(outputs=(), trace=())

    return Adjusted


def test_a_list_slot_is_declared_in_consumes_with_a_list_value_type() -> None:
    total = total_class()

    assert total.CONSUMES == {"parts": list[Decimal]}
    assert total.PRODUCES == {"total": Decimal}
    assert isinstance(total.CONSUMES, MappingProxyType)


def test_single_and_list_consumed_slots_may_be_declared_together() -> None:
    adjusted = adjusted_class()

    assert adjusted.CONSUMES == {"base": Decimal, "parts": list[Decimal]}


def test_rejects_a_list_slot_the_constructor_does_not_take() -> None:
    with pytest.raises(InvalidCapabilityError, match="Typo.*'parts' is not a keyword parameter"):

        class Typo(Bare):
            CONSUMES = {"parts": list[Decimal]}

            def __init__(self, part: tuple[Money, ...]) -> None:
                self.part = part


@pytest.mark.parametrize(
    "declared",
    [
        pytest.param(list[Any], id="list-of-any"),
        pytest.param(list, id="bare-list"),
    ],
)
def test_rejects_a_list_slot_no_kind_can_fill(declared: object) -> None:
    def init(self: Capability, parts: object) -> None:
        pass

    with pytest.raises(InvalidCapabilityError, match="Bad.*CONSUMES slot 'parts'"):
        type("Bad", (Bare,), {"CONSUMES": {"parts": declared}, "__init__": init})


@pytest.mark.parametrize(
    "declared",
    [pytest.param(list[Decimal], id="list-of-decimal"), pytest.param(list, id="bare-list")],
)
def test_rejects_a_list_slot_in_produces(declared: object) -> None:
    def init(self: Capability, totals: object) -> None:
        pass

    with pytest.raises(InvalidCapabilityError, match="Bad.*PRODUCES slot 'totals'"):
        type("Bad", (Bare,), {"PRODUCES": {"totals": declared}, "__init__": init})


@pytest.mark.parametrize("mapping", ["CONSUMES", "PRODUCES"])
def test_rejects_a_single_slot_of_any_which_no_kind_can_fill(mapping: str) -> None:
    def init(self: Capability, amount: object) -> None:
        pass

    with pytest.raises(InvalidCapabilityError, match=f"Bad.*{mapping} slot 'amount'"):
        type("Bad", (Bare,), {mapping: {"amount": Any}, "__init__": init})


def test_a_list_slot_is_given_a_tuple_of_kinds_and_consumes_every_one() -> None:
    total = total_class()((PART_A, PART_B, PART_C), OUT)

    assert total.consumes == frozenset({PART_A, PART_B, PART_C})
    assert total.produces == frozenset({OUT})


def test_consumes_holds_the_single_slots_kind_and_every_listed_kind() -> None:
    adjusted = adjusted_class()(IN, (PART_A, PART_B), OUT)

    assert adjusted.consumes == frozenset({IN, PART_A, PART_B})
    assert adjusted.produces == frozenset({OUT})


def test_a_list_slot_may_be_given_no_kinds() -> None:
    total = total_class()((), OUT)

    assert total.consumes == frozenset()
    assert total.compute(()).outputs == (Artifact(OUT, D(0)),)


def test_a_list_slot_may_be_given_one_kind() -> None:
    total = total_class()((PART_A,), OUT)

    assert total.consumes == frozenset({PART_A})


def test_input_reads_each_listed_part() -> None:
    total = total_class()((PART_A, PART_B, PART_C), OUT)
    inputs = (Artifact(PART_C, D(3)), Artifact(PART_A, D(1)), Artifact(PART_B, D(2)))

    assert total.read(inputs, PART_A) == Artifact(PART_A, D(1))
    assert total.read(inputs, PART_B) == Artifact(PART_B, D(2))
    assert total.read(inputs, PART_C) == Artifact(PART_C, D(3))
    assert total.compute(inputs).outputs == (Artifact(OUT, D(6)),)


def test_input_refuses_a_kind_not_listed() -> None:
    total = total_class()((PART_A, PART_B), OUT)

    with pytest.raises(CapabilityContractError, match="Total does not consume 'part_c'"):
        total.read((Artifact(PART_C, D(1)),), PART_C)


@pytest.mark.parametrize(
    "filler",
    [
        pytest.param([PART_A, PART_B], id="list"),
        pytest.param(PART_A, id="single-kind"),
        pytest.param("ex/part_a", id="identifier"),
        pytest.param(None, id="none"),
    ],
)
def test_rejects_a_list_slot_given_something_other_than_a_tuple(filler: object) -> None:
    total = total_class()

    with pytest.raises(InvalidCapabilityError, match="Total.*'parts'"):
        total(filler, OUT)


@pytest.mark.parametrize("element", ["ex/part_b", D(1), None])
def test_rejects_a_listed_element_that_is_not_an_artifact_kind(element: object) -> None:
    total = total_class()

    with pytest.raises(InvalidCapabilityError, match="Total.*'parts'"):
        total((PART_A, element), OUT)


def test_rejects_a_listed_kind_of_another_value_type() -> None:
    total = total_class()

    with pytest.raises(InvalidCapabilityError, match="Total.*'parts'") as raised:
        total((PART_A, ArtifactKind("ex/count", int)), OUT)

    message = str(raised.value)
    assert "'ex/count'" in message
    assert "int" in message
    assert "Decimal" in message


def test_rejects_a_listed_kind_of_a_value_subtype() -> None:
    total = total_class()

    with pytest.raises(InvalidCapabilityError, match="Total.*'parts'") as raised:
        total((PART_A, ArtifactKind("ex/cents", Cents)), OUT)

    assert "Cents" in str(raised.value)


def test_rejects_a_kind_listed_twice() -> None:
    total = total_class()

    with pytest.raises(InvalidCapabilityError, match="Total.*'parts'") as raised:
        total((PART_A, PART_B, PART_A), OUT)

    assert "'ex/part_a'" in str(raised.value)


def test_rejects_a_listed_kind_equal_to_the_one_it_produces() -> None:
    total = total_class()

    with pytest.raises(InvalidCapabilityError, match="Total") as raised:
        total((PART_A, OUT), OUT)

    message = str(raised.value)
    assert "'parts'" in message
    assert "'total'" in message


def test_rejects_a_listed_kind_that_also_fills_a_single_slot() -> None:
    adjusted = adjusted_class()

    with pytest.raises(InvalidCapabilityError, match="Adjusted") as raised:
        adjusted(PART_A, (PART_B, PART_A), OUT)

    message = str(raised.value)
    assert "'base'" in message
    assert "'parts'" in message


def test_rejects_a_single_slot_given_a_tuple_of_kinds() -> None:
    adjusted = adjusted_class()

    with pytest.raises(InvalidCapabilityError, match="Adjusted.*'base'"):
        adjusted((IN,), (PART_A,), OUT)
