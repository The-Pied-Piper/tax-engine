"""Unit tests for CapabilityBuilder: one capability built from a manifest selection.

The builder is given the selection, the capability class, the resolved datasets (parameter slot ->
dataset) and an `ArtifactRegistry`. It checks the selection fills exactly the class's slots, each
in its own section, with datasets of the slots' kinds, resolves each artifact slot's identifier (or,
for a list slot, identifiers in manifest order) to kinds through the registry, then calls the
constructor by keyword. Value types of kinds are the constructor's check. Names are made up.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from functools import cache
from typing import Any, ClassVar, assert_type

import pytest

from tax_calculator.domain.artifact import Artifact, ArtifactKind, ArtifactRegistry, Money
from tax_calculator.domain.capability import Capability, CapabilityResult
from tax_calculator.domain.capability_builder import CapabilityBuilder
from tax_calculator.domain.errors import (
    DomainError,
    InvalidCapabilityError,
    InvalidRegistrationError,
    InvalidSelectionError,
    UnknownRegistrationError,
)
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rounding import NO_ROUNDING
from tax_calculator.domain.trace import TraceLine

D = Decimal


@dataclass(frozen=True)
class Factor:
    """A made-up parameter: a multiplier."""

    value: Decimal


@dataclass(frozen=True)
class Offset:
    """Another made-up parameter, of another kind."""

    value: Decimal


FACTOR = ParameterKind("factor", Factor)
OFFSET = ParameterKind("offset", Offset)

SOURCE = ArtifactKind("ex/source", Decimal)
TARGET = ArtifactKind("ex/target", Decimal)
EXTRA = ArtifactKind("ex/extra", Decimal)
FACTOR_KIND = ArtifactKind("ex/factor", Decimal)


@dataclass(frozen=True)
class ScaledLine(TraceLine):
    """A made-up trace line: the scaled value."""

    scaled: Decimal

    @property
    def amount(self) -> Decimal:
        return self.scaled


class Scale(Capability):
    """Produces `target` = `source` × the `factor` dataset's value."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Any]]] = {"factor": FACTOR}
    CONSUMES: ClassVar[Mapping[str, type]] = {"source": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"target": Decimal}

    def __init__(self, *, source: Money, target: Money, factor: ParameterDataset[Factor]) -> None:
        super().__init__(source=source, target=target)
        self.source = source
        self.target = target
        self.factor = factor

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        value = self._input(inputs, self.source).value * self.factor.values.value
        return CapabilityResult(outputs=(Artifact(self.target, value),), trace=(ScaledLine(value),))


FACTOR_DATA = ParameterDataset(
    family="ex/factor",
    tax_year=2025,
    kind=FACTOR,
    values=Factor(D("3")),
    rounding=NO_ROUNDING,
    sources=("https://example.org/ex/factor",),
)
OFFSET_DATA = ParameterDataset(
    family="ex/offset",
    tax_year=2025,
    kind=OFFSET,
    values=Offset(D("1")),
    rounding=NO_ROUNDING,
    sources=("https://example.org/ex/offset",),
)


def selection(
    params: Mapping[str, str] | None = None,
    consumes: Mapping[str, str] | None = None,
    produces: Mapping[str, str] | None = None,
) -> CapabilitySelection:
    return CapabilitySelection(
        name="ex/scale",
        params={"factor": "ex/factor"} if params is None else params,
        consumes={"source": "ex/source"} if consumes is None else consumes,
        produces={"target": "ex/target"} if produces is None else produces,
    )


def datasets(**overrides: ParameterDataset[Any]) -> dict[str, ParameterDataset[Any]]:
    return {"factor": FACTOR_DATA, **overrides}


def registry(replacing: Mapping[str, object] | None = None) -> ArtifactRegistry:
    """A private registry of every made-up kind of this module.

    `replacing` registers its items under their identifiers instead of this module's kinds.
    """
    registered: dict[str, object] = {
        kind.identifier: kind
        for kind in (SOURCE, TARGET, EXTRA, FACTOR_KIND, PART_A, PART_B, PART_C, TOTAL)
    }
    registered.update(replacing or {})
    artifacts = ArtifactRegistry()
    for identifier, item in registered.items():
        artifacts.register(identifier, item)
    return artifacts


def build(
    chosen: CapabilitySelection,
    given_datasets: Mapping[str, ParameterDataset[Any]] | None = None,
    artifacts: ArtifactRegistry | None = None,
) -> Capability:
    return CapabilityBuilder().build(
        chosen,
        Scale,
        datasets() if given_datasets is None else given_datasets,
        registry() if artifacts is None else artifacts,
    )


def assert_names(excinfo: pytest.ExceptionInfo[InvalidSelectionError], slot: str) -> None:
    message = str(excinfo.value)
    assert "ex/scale (produces " in message, message
    assert repr(slot) in message, message


def test_builds_an_instance_of_the_class_wired_with_the_registered_kinds() -> None:
    built = CapabilityBuilder().build(selection(), Scale, datasets(), artifacts=registry())

    assert_type(built, Capability)
    assert isinstance(built, Scale)
    assert built.source is SOURCE
    assert built.target is TARGET
    assert built.consumes == frozenset({SOURCE})
    assert built.produces == frozenset({TARGET})
    assert built.factor is FACTOR_DATA


def test_resolves_kinds_through_the_registry_it_is_given() -> None:
    own_source = ArtifactKind("ex/source", Decimal)  # equal to SOURCE, but another object
    own_target = ArtifactKind("ex/target", Decimal)
    artifacts = registry(replacing={"ex/source": own_source, "ex/target": own_target})

    built = build(selection(), artifacts=artifacts)

    assert isinstance(built, Scale)
    assert built.source is own_source
    assert built.target is own_target
    assert "ex/source" not in ArtifactRegistry.shared().identifiers()


@pytest.mark.parametrize(
    ("consumes", "produces"),
    [
        pytest.param({"source": "ex/nowhere"}, {"target": "ex/target"}, id="consumed"),
        pytest.param({"source": "ex/source"}, {"target": "ex/nowhere"}, id="produced"),
    ],
)
def test_an_unknown_identifier_is_the_registrys_unknown_registration(
    consumes: dict[str, str], produces: dict[str, str]
) -> None:
    with pytest.raises(UnknownRegistrationError, match=re.escape("'ex/nowhere'")):
        build(selection(consumes=consumes, produces=produces))


def test_an_identifier_registered_as_something_other_than_a_kind_is_an_invalid_registration() -> (
    None
):
    artifacts = registry(replacing={"ex/stray": object()})

    with pytest.raises(InvalidRegistrationError, match="'ex/stray'.*not as an artifact kind"):
        build(selection(consumes={"source": "ex/stray"}), artifacts=artifacts)


def test_the_built_capability_computes_with_its_dataset() -> None:
    built = build(selection())

    result = built.compute((Artifact(SOURCE, D("5")),))

    assert result.outputs == (Artifact(TARGET, D("15")),)


def test_invalid_selection_error_is_a_domain_error() -> None:
    assert issubclass(InvalidSelectionError, DomainError)


def test_rejects_a_params_key_that_is_not_a_parameter_slot() -> None:
    with pytest.raises(InvalidSelectionError) as excinfo:
        build(selection(params={"factor": "ex/factor", "bonus": "ex/bonus"}))

    assert_names(excinfo, "bonus")


def test_rejects_an_artifact_slot_given_as_a_parameter() -> None:
    with pytest.raises(InvalidSelectionError) as excinfo:
        build(selection(params={"factor": "ex/factor", "source": "ex/source"}))

    assert_names(excinfo, "source")


def test_rejects_a_parameter_slot_the_selection_does_not_fill() -> None:
    with pytest.raises(InvalidSelectionError) as excinfo:
        build(selection(params={}), given_datasets={})

    assert_names(excinfo, "factor")


def test_rejects_a_dataset_of_another_kind_than_the_slots() -> None:
    with pytest.raises(InvalidSelectionError) as excinfo:
        build(selection(), given_datasets=datasets(factor=OFFSET_DATA))

    assert_names(excinfo, "factor")
    assert "offset" in str(excinfo.value)


def test_rejects_a_consumes_key_that_is_not_a_consumed_slot() -> None:
    with pytest.raises(InvalidSelectionError) as excinfo:
        build(selection(consumes={"source": "ex/source", "extra": "ex/extra"}))

    assert_names(excinfo, "extra")


def test_rejects_a_produces_key_that_is_not_a_produced_slot() -> None:
    with pytest.raises(InvalidSelectionError) as excinfo:
        build(selection(produces={"target": "ex/target", "extra": "ex/extra"}))

    assert_names(excinfo, "extra")


def test_rejects_a_produced_slot_given_under_consumes() -> None:
    with pytest.raises(InvalidSelectionError) as excinfo:
        build(selection(consumes={"source": "ex/source", "target": "ex/target"}, produces={}))

    assert_names(excinfo, "target")


def test_rejects_a_consumed_slot_given_under_produces() -> None:
    with pytest.raises(InvalidSelectionError) as excinfo:
        build(selection(consumes={}, produces={"source": "ex/source", "target": "ex/target"}))

    assert_names(excinfo, "source")


def test_rejects_a_parameter_slot_given_as_an_artifact_slot() -> None:
    with pytest.raises(InvalidSelectionError) as excinfo:
        build(selection(consumes={"source": "ex/source", "factor": "ex/factor"}))

    assert_names(excinfo, "factor")


@pytest.mark.parametrize(
    ("consumes", "produces", "slot"),
    [
        pytest.param({}, {"target": "ex/target"}, "source", id="consumed-slot-missing"),
        pytest.param({"source": "ex/source"}, {}, "target", id="produced-slot-missing"),
    ],
)
def test_rejects_an_artifact_slot_the_selection_does_not_fill(
    consumes: dict[str, str], produces: dict[str, str], slot: str
) -> None:
    with pytest.raises(InvalidSelectionError) as excinfo:
        build(selection(consumes=consumes, produces=produces))

    assert_names(excinfo, slot)


def test_rejects_a_parameter_slot_without_a_resolved_dataset() -> None:
    with pytest.raises(InvalidSelectionError) as excinfo:
        build(selection(), given_datasets={})

    assert_names(excinfo, "factor")


def assert_names_the_constructors_rejection(
    excinfo: pytest.ExceptionInfo[InvalidSelectionError], prefix: str, class_name: str
) -> InvalidCapabilityError:
    """The rejection names the selection, carries the constructor's message and chains it."""
    error = excinfo.value
    cause = error.__cause__
    assert isinstance(cause, InvalidCapabilityError), repr(cause)
    message = str(error)
    assert message.startswith(prefix), message
    assert str(cause) in message, message
    assert class_name in message, message
    return cause


def test_a_kind_of_the_wrong_value_type_is_rejected_naming_the_selection() -> None:
    wrong = ArtifactKind("ex/target", int)

    with pytest.raises(InvalidSelectionError) as excinfo:
        build(selection(), artifacts=registry(replacing={"ex/target": wrong}))

    cause = assert_names_the_constructors_rejection(
        excinfo, "ex/scale (produces ex/target)", "Scale"
    )
    assert_names(excinfo, "target")
    assert "'target'" in str(cause)


def test_the_constructor_called_directly_still_raises_invalid_capability() -> None:
    wrong: Any = ArtifactKind("ex/target", int)  # past mypy, to reach the runtime check

    with pytest.raises(InvalidCapabilityError, match=re.escape("Scale: artifact slot 'target'")):
        Scale(source=SOURCE, target=wrong, factor=FACTOR_DATA)


def test_a_class_without_parameter_slots_builds_from_an_empty_params() -> None:
    class Copy(Capability):
        CONSUMES: ClassVar[Mapping[str, type]] = {"source": Decimal}
        PRODUCES: ClassVar[Mapping[str, type]] = {"target": Decimal}

        def __init__(self, source: Money, target: Money) -> None:
            super().__init__(source=source, target=target)

        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            raise NotImplementedError

    chosen = CapabilitySelection(
        name="ex/copy",
        params={},
        consumes={"source": "ex/source"},
        produces={"target": "ex/target"},
    )

    built = CapabilityBuilder().build(chosen, Copy, {}, registry())

    assert isinstance(built, Copy)
    assert built.produces == frozenset({TARGET})


class Grant(Capability):
    """Produces `target` = the `factor` dataset's value; consumes nothing."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Any]]] = {"factor": FACTOR}
    PRODUCES: ClassVar[Mapping[str, type]] = {"target": Decimal}

    def __init__(self, *, factor: ParameterDataset[Factor], target: Money) -> None:
        super().__init__(target=target)
        self.factor, self.target = factor, target

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        return CapabilityResult(
            outputs=(Artifact(self.target, self.factor.values.value),), trace=()
        )


def grant(consumes: Mapping[str, str] | None = None) -> CapabilitySelection:
    return CapabilitySelection(
        name="ex/grant",
        params={"factor": "ex/factor"},
        consumes={} if consumes is None else consumes,
        produces={"target": "ex/target"},
    )


def test_a_class_without_consumed_slots_builds_from_an_empty_consumes() -> None:
    built = CapabilityBuilder().build(grant(), Grant, datasets(), registry())

    assert isinstance(built, Grant)
    assert built.consumes == frozenset()
    assert built.produces == frozenset({TARGET})
    assert built.compute(()).outputs == (Artifact(TARGET, D("3")),)


def test_rejects_a_consumes_key_for_a_class_without_consumed_slots() -> None:
    with pytest.raises(InvalidSelectionError, match="'source' is given under consumes") as raised:
        CapabilityBuilder().build(grant({"source": "ex/source"}), Grant, datasets(), registry())

    assert "ex/grant (produces ex/target)" in str(raised.value)


def test_identifies_the_selection_by_name_and_produced_identifiers() -> None:
    with pytest.raises(InvalidSelectionError, match=re.escape("ex/scale (produces ex/target)")):
        build(selection(params={}), given_datasets={})


def test_rejects_a_dataset_of_another_family_than_the_selection_names() -> None:
    other = ParameterDataset(
        family="ex/other_factor",
        tax_year=2025,
        kind=FACTOR,
        values=Factor(D("2")),
        rounding=NO_ROUNDING,
        sources=("https://example.org/ex/other_factor",),
    )

    with pytest.raises(InvalidSelectionError) as excinfo:
        build(selection(), given_datasets=datasets(factor=other))

    assert_names(excinfo, "factor")
    assert "ex/other_factor" in str(excinfo.value)


def test_rejects_a_resolved_dataset_for_a_key_that_is_not_a_parameter_slot() -> None:
    with pytest.raises(InvalidSelectionError) as excinfo:
        build(selection(), given_datasets=datasets(bonus=FACTOR_DATA))

    assert_names(excinfo, "bonus")


# --- list slots: a consumed slot filled with a list of identifiers ------------------------------
#
# The list-slot classes are defined inside cached factories, so a class definition the base
# rejects fails the tests that use it rather than the collection of this whole module.

PART_A = ArtifactKind("ex/part_a", Decimal)
PART_B = ArtifactKind("ex/part_b", Decimal)
PART_C = ArtifactKind("ex/part_c", Decimal)
TOTAL = ArtifactKind("ex/total", Decimal)


@cache
def total_class() -> Any:
    class Total(Capability):
        """Produces `total` = the sum of its `parts`; keeps the parts in the order it was given."""

        CONSUMES = {"parts": list[Decimal]}
        PRODUCES = {"total": Decimal}

        def __init__(self, *, parts: tuple[Money, ...], total: Money) -> None:
            super().__init__(parts=parts, total=total)
            self.parts, self.total = parts, total

        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            value = sum((self._input(inputs, kind).value for kind in self.parts), D(0))
            return CapabilityResult(outputs=(Artifact(self.total, value),), trace=())

    return Total


@cache
def adjusted_class() -> Any:
    class Adjusted(Capability):
        """Consumes a single `base` and a list of `parts`; produces `total`."""

        CONSUMES = {"base": Decimal, "parts": list[Decimal]}
        PRODUCES = {"total": Decimal}

        def __init__(self, *, base: Money, parts: tuple[Money, ...], total: Money) -> None:
            super().__init__(base=base, parts=parts, total=total)
            self.base, self.parts = base, parts

        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            raise NotImplementedError

    return Adjusted


def listing(consumes: Mapping[str, Any], name: str = "ex/total_up") -> CapabilitySelection:
    return CapabilitySelection(
        name=name, params={}, consumes=consumes, produces={"total": "ex/total"}
    )


def build_list(
    cls: type[Capability], consumes: Mapping[str, Any], artifacts: ArtifactRegistry | None = None
) -> Any:
    return CapabilityBuilder().build(
        listing(consumes), cls, {}, registry() if artifacts is None else artifacts
    )


def assert_names_listing(excinfo: pytest.ExceptionInfo[InvalidSelectionError], slot: str) -> None:
    message = str(excinfo.value)
    assert "ex/total_up (produces ex/total)" in message, message
    assert repr(slot) in message, message


def test_builds_a_list_slot_with_the_kinds_in_manifest_order() -> None:
    total = total_class()

    built = build_list(total, {"parts": ("ex/part_c", "ex/part_a", "ex/part_b")})

    assert isinstance(built, total)
    assert built.parts == (PART_C, PART_A, PART_B)
    assert built.consumes == frozenset({PART_A, PART_B, PART_C})
    assert built.produces == frozenset({TOTAL})


def test_a_list_slots_kinds_are_the_registered_objects() -> None:
    own_a = ArtifactKind("ex/part_a", Decimal)  # equal to PART_A, but another object
    own_b = ArtifactKind("ex/part_b", Decimal)
    artifacts = registry(replacing={"ex/part_a": own_a, "ex/part_b": own_b})

    built = build_list(total_class(), {"parts": ("ex/part_b", "ex/part_a")}, artifacts)

    assert type(built.parts) is tuple
    assert len(built.parts) == 2
    assert built.parts[0] is own_b
    assert built.parts[1] is own_a


def test_the_built_list_capability_computes_from_every_part() -> None:
    built = build_list(total_class(), {"parts": ("ex/part_a", "ex/part_b", "ex/part_c")})

    inputs = (Artifact(PART_A, D("1")), Artifact(PART_B, D("2")), Artifact(PART_C, D("4")))

    assert built.compute(inputs).outputs == (Artifact(TOTAL, D("7")),)


def test_builds_a_list_slot_filled_with_no_identifiers() -> None:
    built = build_list(total_class(), {"parts": ()})

    assert built.parts == ()
    assert built.consumes == frozenset()


def test_builds_single_and_list_slots_together() -> None:
    adjusted = adjusted_class()

    built = build_list(adjusted, {"base": "ex/source", "parts": ("ex/part_a", "ex/part_b")})

    assert built.base is SOURCE
    assert built.parts == (PART_A, PART_B)
    assert built.consumes == frozenset({SOURCE, PART_A, PART_B})


def test_an_unknown_identifier_in_a_list_is_the_registrys_unknown_registration() -> None:
    with pytest.raises(UnknownRegistrationError, match=re.escape("'ex/nowhere'")):
        build_list(total_class(), {"parts": ("ex/part_a", "ex/nowhere", "ex/part_b")})


def test_an_identifier_in_a_list_registered_as_something_other_than_a_kind_is_invalid() -> None:
    artifacts = registry(replacing={"ex/stray": object()})

    with pytest.raises(InvalidRegistrationError, match="'ex/stray'.*not as an artifact kind"):
        build_list(total_class(), {"parts": ("ex/part_a", "ex/stray")}, artifacts)


def test_rejects_a_single_identifier_for_a_list_slot() -> None:
    total = total_class()

    with pytest.raises(InvalidSelectionError) as excinfo:
        build_list(total, {"parts": "ex/part_a"})

    assert_names_listing(excinfo, "parts")
    assert "list" in str(excinfo.value)


def test_rejects_a_list_of_identifiers_for_a_single_slot() -> None:
    adjusted = adjusted_class()

    with pytest.raises(InvalidSelectionError) as excinfo:
        build_list(adjusted, {"base": ("ex/source",), "parts": ("ex/part_a",)})

    assert_names_listing(excinfo, "base")
    assert "list" in str(excinfo.value)


def test_rejects_a_list_for_a_slot_of_a_class_without_list_slots() -> None:
    chosen = CapabilitySelection(
        name="ex/scale",
        params={"factor": "ex/factor"},
        consumes={"source": ("ex/source",)},
        produces={"target": "ex/target"},
    )

    with pytest.raises(InvalidSelectionError) as excinfo:
        build(chosen)

    assert_names(excinfo, "source")


def test_rejects_an_identifier_listed_twice() -> None:
    total = total_class()

    with pytest.raises(InvalidSelectionError) as excinfo:
        build_list(total, {"parts": ("ex/part_a", "ex/part_b", "ex/part_a")})

    assert_names_listing(excinfo, "parts")
    assert "ex/part_a" in str(excinfo.value)


def test_a_listed_kind_of_the_wrong_value_type_is_rejected_naming_the_selection() -> None:
    total = total_class()
    wrong = ArtifactKind("ex/part_b", int)

    with pytest.raises(InvalidSelectionError) as excinfo:
        build_list(
            total,
            {"parts": ("ex/part_a", "ex/part_b")},
            registry(replacing={"ex/part_b": wrong}),
        )

    assert_names_the_constructors_rejection(excinfo, "ex/total_up (produces ex/total)", "Total")
    assert_names_listing(excinfo, "parts")
    assert "'ex/part_b'" in str(excinfo.value)


def test_a_listed_kind_that_is_also_the_produced_kind_is_rejected_naming_the_selection() -> None:
    with pytest.raises(InvalidSelectionError) as excinfo:
        build_list(total_class(), {"parts": ("ex/part_a", "ex/total")})

    assert_names_the_constructors_rejection(excinfo, "ex/total_up (produces ex/total)", "Total")
    message = str(excinfo.value)
    assert "'parts'" in message, message
    assert "'total'" in message, message


def test_a_constructor_rejection_names_which_of_two_selections_of_one_class_failed() -> None:
    total = total_class()
    good = CapabilitySelection(
        name="ex/total_up",
        params={},
        consumes={"parts": ("ex/part_a",)},
        produces={"total": "ex/total"},
    )
    bad = CapabilitySelection(
        name="ex/total_up",
        params={},
        consumes={"parts": ("ex/part_b", "ex/source")},
        produces={"total": "ex/source"},
    )

    CapabilityBuilder().build(good, total, {}, registry())
    with pytest.raises(InvalidSelectionError) as excinfo:
        CapabilityBuilder().build(bad, total, {}, registry())

    assert_names_the_constructors_rejection(excinfo, "ex/total_up (produces ex/source)", "Total")
