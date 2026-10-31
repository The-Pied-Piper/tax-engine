"""The capability contract (design.md §3).

A capability is pure mechanism. Its class declares, in code, named slots: parameter slots
(`PARAMETERS`, slot -> parameter kind) and artifact slots (`CONSUMES` / `PRODUCES`, slot -> value
type), each a keyword parameter of its constructor; a manifest fills them. A consumed slot may
take a list of kinds of one value type (declared as `list[Decimal]`), so a capability's number of
inputs can be left to the manifest. An instance consumes and produces the artifact kinds it was
built with, and the worksheet holds it to that. The vocabulary is consume / produce only: there
is no "modify". Any artifact can be blank (blank.py), so a class declares in `BLANK_ALLOWED` which
of its consumed slots may ever be blank; the manifest says what a blank does in each of those
(`with_blank_rules`), and the base applies it before `compute` runs, so `compute` never sees a
blank.
"""

from __future__ import annotations

import inspect
import re
from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from decimal import Decimal
from types import MappingProxyType
from typing import Any, ClassVar, Self, cast, get_args, get_origin

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.blank import BLANK, BlankRule, PassOn
from tax_engine.domain.errors import (
    BlankNotAllowedError,
    CapabilityContractError,
    DomainError,
    DuplicateArtifactError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.registry import Namespace, Registry
from tax_engine.domain.trace import BlankFallbackLine, BlankPassedOnLine, TraceLine


@dataclass(frozen=True)
class CapabilityResult:
    """What a capability computed: one artifact per kind it produces, and how."""

    outputs: tuple[Artifact[Any], ...]
    trace: tuple[TraceLine, ...]


_SLOT_NAME = re.compile(r"[a-z][a-z0-9]*(_[a-z0-9]+)*")
_SLOT_MAPPINGS = ("PARAMETERS", "CONSUMES", "PRODUCES")
_KEYWORD_CAPABLE = frozenset(
    {inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY}
)


class Capability(ABC):
    """A mechanism, built from named slots, that computes what it produces from what it consumes.

    Subclasses may assign plain dicts to the slot mappings; each is exposed read-only, and every
    slot is checked against the constructor when the subclass is defined. The constructor must be
    written in the class body (a dataclass-generated `__init__` is not there yet when the check
    runs), and each slot must be a named keyword parameter of it: `**kwargs` does not count. The
    constructor passes its artifact slots, by name, to `super().__init__`, which checks them and
    derives `consumes` and `produces`; parameter datasets stay on the subclass.
    """

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Any]]] = MappingProxyType({})
    """Parameter slots: slot name -> the kind of dataset the constructor takes under that name."""

    CONSUMES: ClassVar[Mapping[str, type]] = MappingProxyType({})
    """Consumed artifact slots: slot name -> the value type of the artifact kind it takes, or
    `list[<value type>]` for a list slot, which takes a tuple of kinds of that value type (a type
    to the type checker, a `GenericAlias` at runtime). The value type is concrete: `Any`,
    `list[Any]` and a bare `list` are rejected, since no kind could fill them."""

    PRODUCES: ClassVar[Mapping[str, type]] = MappingProxyType({})
    """Produced artifact slots: slot name -> the value type of the artifact kind it takes."""

    BLANK_ALLOWED: ClassVar[frozenset[str]] = frozenset()
    """The consumed slots that may be blank. The manifest gives each of them a rule
    (`with_blank_rules`): the fallback value taken in its place, or pass the blank on to
    everything produced. A consumed slot not listed here, or listed without a rule, refuses a
    blank. A subclass inherits its parent's slots unless it declares its own.
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Freeze the slot mappings `cls` declares and check every slot it has against `__init__`.

        Raises InvalidCapabilityError naming the class and the slot.
        """
        super().__init_subclass__(**kwargs)
        for mapping in _SLOT_MAPPINGS:
            if mapping in vars(cls):
                declared = getattr(cls, mapping)
                if not isinstance(declared, Mapping):
                    raise InvalidCapabilityError(
                        f"{cls.__name__}: {mapping} must be a mapping of slot names, "
                        f"got {type(declared).__name__}"
                    )
                setattr(cls, mapping, MappingProxyType(dict(declared)))
        if "BLANK_ALLOWED" in vars(cls):
            cls.BLANK_ALLOWED = frozenset(cls.BLANK_ALLOWED)
        cls._check_slots()

    @classmethod
    def _check_slots(cls) -> None:
        name = cls.__name__
        declared_in: dict[str, str] = {}
        for mapping in _SLOT_MAPPINGS:
            for slot, filler in getattr(cls, mapping).items():
                cls._check_slot(mapping, slot, filler)
                if slot in declared_in:
                    raise InvalidCapabilityError(
                        f"{name}: slot {slot!r} is declared in both {declared_in[slot]} "
                        f"and {mapping}"
                    )
                declared_in[slot] = mapping
        cls._check_blank_allowed()
        # `__init__`'s own signature, not the class's, so a custom `__new__` cannot hide it; its
        # first parameter (`self`) is skipped, so `self` can never fill a slot.
        _self, *parameters = inspect.signature(cls.__init__).parameters.values()
        keywords = {p.name for p in parameters if p.kind in _KEYWORD_CAPABLE}
        for slot, mapping in declared_in.items():
            if slot not in keywords:
                raise InvalidCapabilityError(
                    f"{name}: {mapping} slot {slot!r} is not a keyword parameter of {name}.__init__"
                )

    @classmethod
    def _check_blank_allowed(cls) -> None:
        """Refuse a `BLANK_ALLOWED` entry that is not the name of a consumed slot."""
        for slot in cls.BLANK_ALLOWED:
            if slot not in cls.CONSUMES:
                raise InvalidCapabilityError(
                    f"{cls.__name__}: BLANK_ALLOWED slot {slot!r} is not a consumed slot"
                )

    @classmethod
    def _check_slot(cls, mapping: str, slot: object, filler: object) -> None:
        name = cls.__name__
        if not isinstance(slot, str):
            raise InvalidCapabilityError(
                f"{name}: {mapping} slot {slot!r} must be a string, got {type(slot).__name__}"
            )
        if not _SLOT_NAME.fullmatch(slot):
            raise InvalidCapabilityError(f"{name}: {mapping} slot {slot!r} must be snake_case")
        if mapping == "PARAMETERS":
            if not isinstance(filler, ParameterKind):
                raise InvalidCapabilityError(
                    f"{name}: PARAMETERS slot {slot!r} must map to a ParameterKind, got {filler!r}"
                )
        elif mapping == "CONSUMES" and (filler is list or get_origin(filler) is list):
            # A bare `list` names no element type, and no kind has value type `Any`.
            if cls._element_type(filler) is None:
                raise InvalidCapabilityError(
                    f"{name}: CONSUMES slot {slot!r} must be a list of one concrete type, "
                    f"got {filler!r}"
                )
        elif not isinstance(filler, type) or filler is list or filler is Any:
            # Kinds are matched by their value type's identity, so a slot of `Any` could never be
            # filled; `Any` counts as a type at runtime.
            is_list = filler is list or get_origin(filler) is list
            hint = " (only a consumed slot may take a list)" if is_list else ""
            raise InvalidCapabilityError(
                f"{name}: {mapping} slot {slot!r} must be a type, got {filler!r}{hint}"
            )

    @staticmethod
    def _element_type(declared: object) -> type | None:
        """The value type of each kind in a list slot declared as `list[<type>]`, else None.

        None for `list[Any]` too: no kind has value type `Any`.
        """
        if get_origin(declared) is not list:
            return None
        arguments = get_args(declared)
        if len(arguments) != 1 or not isinstance(arguments[0], type) or arguments[0] is Any:
            return None
        element: type = arguments[0]
        return element

    @classmethod
    def slot_value_type(cls, slot: str) -> type:
        """The value type of the kinds a consumed `slot` takes (the element type of a list slot)."""
        declared = cls.CONSUMES[slot]
        return cls._element_type(declared) or declared

    @classmethod
    def is_list_slot(cls, slot: str) -> bool:
        """Whether `slot` is a consumed slot taking a list of kinds rather than one kind."""
        return slot in cls.CONSUMES and cls._element_type(cls.CONSUMES[slot]) is not None

    def __init__(self, **slots: ArtifactKind[Any] | tuple[ArtifactKind[Any], ...]) -> None:
        """Wire the artifact slots declared in `CONSUMES` / `PRODUCES` with the kinds given by name.

        A list slot takes a tuple of kinds (possibly empty); every other slot takes one kind.
        Raises InvalidCapabilityError naming the class and the slot if one is missing, unknown,
        not filled as declared with kinds of exactly its value type, or filled with a kind
        another slot, or another place in the same list, has.
        """
        name = type(self).__name__
        declared = {**self.CONSUMES, **self.PRODUCES}
        for slot in slots:
            if slot not in declared:
                hint = " (it is a parameter slot)" if slot in self.PARAMETERS else ""
                raise InvalidCapabilityError(f"{name}: {slot!r} is not an artifact slot{hint}")
        filled_by: dict[ArtifactKind[Any], str] = {}
        wired: dict[str, tuple[ArtifactKind[Any], ...]] = {}
        for slot, value_type in declared.items():
            if slot not in slots:
                raise InvalidCapabilityError(f"{name}: artifact slot {slot!r} is not given")
            wired[slot] = self._slot_kinds(slot, value_type, slots[slot])
            for kind in wired[slot]:
                if kind in filled_by:
                    raise InvalidCapabilityError(
                        f"{name}: artifact slots {filled_by[kind]!r} and {slot!r} are both given "
                        f"{kind.identifier!r}"
                    )
                filled_by[kind] = slot
        self._wired_kinds = wired
        self._blank_rules: Mapping[str, BlankRule] = MappingProxyType({})
        self._slot_of = {kind: slot for slot in self.CONSUMES for kind in wired[slot]}
        self._consumes = frozenset(kind for slot in self.CONSUMES for kind in wired[slot])
        self._produces = frozenset(kind for slot in self.PRODUCES for kind in wired[slot])

    def with_blank_rules(self, rules: Mapping[str, BlankRule]) -> Self:
        """Give this capability what a blank does in each consumed slot named in `rules`, and
        return it: the fallback value taken in its place, or `PASS_ON`. A slot without a rule
        refuses a blank.

        Raises InvalidCapabilityError naming the class and the slot if rules were already given,
        a slot is not in `BLANK_ALLOWED`, or a fallback is not a finite `Decimal` or `int` of
        exactly the slot's value type or is not valid for a kind wired to the slot, such as a
        negative one for a non-negative kind.
        """
        name = type(self).__name__
        if self._blank_rules:
            raise InvalidCapabilityError(f"{name}: blank rules are already given")
        for slot, rule in rules.items():
            if slot not in self.BLANK_ALLOWED:
                raise InvalidCapabilityError(f"{name}: slot {slot!r} may not be blank")
            if isinstance(rule, PassOn):
                continue
            value_type = self.slot_value_type(slot)
            if type(rule) is not value_type or (isinstance(rule, Decimal) and not rule.is_finite()):
                raise InvalidCapabilityError(
                    f"{name}: blank rule for slot {slot!r} must be PASS_ON or a finite "
                    f"{value_type.__name__}, got {rule!r}"
                )
            for kind in self._wired_kinds[slot]:
                try:
                    Artifact(kind, rule)
                except DomainError as error:
                    raise InvalidCapabilityError(
                        f"{name}: the blank fallback {rule} for slot {slot!r} is not valid for "
                        f"{kind.identifier!r}: {error}"
                    ) from error
        self._blank_rules = MappingProxyType(dict(rules))
        return self

    def _slot_kinds(
        self, slot: str, declared: type, given: object
    ) -> tuple[ArtifactKind[Any], ...]:
        """The kinds `given` for `slot`, declared as `declared`: a tuple of distinct kinds for a
        list slot, else one kind. Each kind must have exactly the slot's value type.
        """
        name = type(self).__name__
        element_type = self._element_type(declared)
        if element_type is None:
            if isinstance(given, tuple):
                raise InvalidCapabilityError(
                    f"{name}: artifact slot {slot!r} takes one ArtifactKind, not a tuple: {given!r}"
                )
            return (self._checked_kind(slot, declared, given),)
        if not isinstance(given, tuple):
            raise InvalidCapabilityError(
                f"{name}: list slot {slot!r} takes a tuple of ArtifactKinds of "
                f"{element_type.__name__}, got {given!r}"
            )
        kinds = tuple(self._checked_kind(slot, element_type, element) for element in given)
        for position, kind in enumerate(kinds):
            if kind in kinds[:position]:
                raise InvalidCapabilityError(
                    f"{name}: list slot {slot!r} lists {kind.identifier!r} more than once"
                )
        return kinds

    def _checked_kind(self, slot: str, value_type: type, given: object) -> ArtifactKind[Any]:
        """`given`, which must be an ArtifactKind of exactly `value_type`, for `slot`."""
        name = type(self).__name__
        if not isinstance(given, ArtifactKind):
            raise InvalidCapabilityError(
                f"{name}: artifact slot {slot!r} must be given ArtifactKinds, got {given!r}"
            )
        if given.value_type is not value_type:
            raise InvalidCapabilityError(
                f"{name}: artifact slot {slot!r} takes a kind of {value_type.__name__}, "
                f"got {given.identifier!r} of {given.value_type.__name__}"
            )
        return given

    @property
    def consumes(self) -> frozenset[ArtifactKind[Any]]:
        """The artifact kinds this capability was built to consume."""
        return self._wired("_consumes")

    @property
    def produces(self) -> frozenset[ArtifactKind[Any]]:
        """The artifact kinds this capability was built to produce."""
        return self._wired("_produces")

    def _wired(self, attribute: str) -> frozenset[ArtifactKind[Any]]:
        """The kinds stored under `attribute` by `Capability.__init__`, which must have run."""
        try:
            kinds: frozenset[ArtifactKind[Any]] = getattr(self, attribute)
        except AttributeError:
            raise InvalidCapabilityError(
                f"{type(self).__name__}: __init__ must pass its artifact slots to super().__init__"
            ) from None
        return kinds

    @abstractmethod
    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        """Compute this capability's output artifacts from the artifacts of the kinds it consumes.

        Only `run` calls this in a real computation, with no blank among `inputs`.
        """

    def run(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        """Apply the blank rules to `inputs`, then compute; only `Worksheet.apply` calls this.

        A blank input in a slot with a fallback is replaced by an artifact of the fallback, and the
        trace says so first. A blank in a slot with no rule is a BlankNotAllowedError naming the
        line and the slot; that refusal comes before anything else. Otherwise a blank in a
        `PASS_ON` slot gives a blank artifact for every produced kind, with a trace line each and
        `compute` not called; with no blank left, `compute` runs as usual, and a blank among its
        outputs is a CapabilityContractError, since only a `PASS_ON` rule makes an output blank.
        """
        name = type(self).__name__
        kept: list[Artifact[Any]] = []
        fallbacks: list[BlankFallbackLine] = []
        passed_on: list[ArtifactKind[Any]] = []
        for artifact in sorted(inputs, key=lambda each: each.kind.identifier):
            if not artifact.is_blank:
                kept.append(artifact)
                continue
            slot = self._slot_of[artifact.kind]
            rule = self._blank_rules.get(slot)
            if rule is None:
                raise BlankNotAllowedError(
                    f"{name}: {artifact.kind.label!r} was left blank, and {slot!r} may not be blank"
                )
            if isinstance(rule, PassOn):
                passed_on.append(artifact.kind)
            else:
                kept.append(Artifact(artifact.kind, rule))
                fallbacks.append(BlankFallbackLine(artifact.kind, rule))
        if passed_on:
            because = tuple(sorted(passed_on, key=lambda kind: kind.identifier))
            produced = sorted(self.produces, key=lambda kind: kind.identifier)
            return CapabilityResult(
                outputs=tuple(Artifact(kind, BLANK) for kind in produced),
                trace=(
                    *fallbacks,
                    *(BlankPassedOnLine(kind, because) for kind in produced),
                ),
            )
        result = self.compute(tuple(kept))
        # A non-Artifact output is the worksheet's TypeError to raise, not this check's.
        blank = [
            artifact.kind
            for artifact in result.outputs
            if isinstance(artifact, Artifact) and artifact.is_blank
        ]
        if blank:
            raise CapabilityContractError(
                f"{name} returned {ArtifactKind.labels(blank)} blank from compute; "
                "only a PASS_ON rule makes an output blank"
            )
        return CapabilityResult(outputs=result.outputs, trace=(*fallbacks, *result.trace))

    def _input[V](self, inputs: tuple[Artifact[Any], ...], kind: ArtifactKind[V]) -> Artifact[V]:
        """The one artifact of `kind` in `inputs`; `kind` must be one this consumes."""
        name = type(self).__name__
        if kind not in self.consumes:
            raise CapabilityContractError(f"{name} does not consume {kind.label!r}")
        found = [artifact for artifact in inputs if artifact.kind == kind]
        if not found:
            raise MissingArtifactError(f"{name} needs {kind.label!r}")
        if len(found) > 1:
            raise DuplicateArtifactError(f"{name} got {len(found)} values for {kind.label!r}")
        # Safe: the artifact's kind equals `kind`, and an Artifact is checked against its kind.
        return cast(Artifact[V], found[0])


class CapabilityRegistry(Registry[type[Capability]]):
    """The capability classes packages contribute, by full identifier (`core/progressive_tax`).

    Register through `register_class` or `@capability`; the inherited `register` takes the key
    as given and skips namespace validation.
    """

    def register_class[C: Capability](self, local_id: str, cls: type[C]) -> type[C]:
        """Register `cls` under `local_id` in its package's namespace and return it unchanged."""
        self.register(Namespace.of(cls).identifier(local_id), cls)
        return cls


def capability[C: Capability](*, identifier: str) -> Callable[[type[C]], type[C]]:
    """Class decorator registering a capability in the shared CapabilityRegistry under `identifier`.

    `identifier` is the local id; the namespace comes from the package declaring `NAMESPACE`.
    """
    return lambda cls: CapabilityRegistry.shared().register_class(identifier, cls)
