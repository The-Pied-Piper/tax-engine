"""Artifacts: the named intermediate values that capabilities consume and produce.

A kind names a value type by a namespaced identifier; a package declares its kinds on an
`ArtifactCatalog`.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

from tax_engine.domain.blank import BLANK, Blank
from tax_engine.domain.errors import (
    BlankValueError,
    DuplicateRegistrationError,
    InvalidAmountError,
    InvalidRegistrationError,
    NegativeArtifactError,
)
from tax_engine.domain.registry import Namespace, Registry

# Invariant on purpose. PEP 695 syntax would infer covariance from `value_type: type[V]`, and
# mypy would then accept, say, an ArtifactKind[int] wired where an ArtifactKind[Decimal] is
# expected.
V = TypeVar("V")


@runtime_checkable
class HasFloor(Protocol):
    """A kind with a lowest value it holds, as a non-negative amount or count does.

    Matched by shape: any kind with `is_below_floor` is one. An amount or count kind always matches;
    its answer is always no unless it was declared non-negative.
    """

    def is_below_floor(self, value: Any) -> bool:
        """Whether `value`, already an instance of the value type, is below the floor."""
        ...


@runtime_checkable
class RecordField(Protocol):
    """A kind a record can hold as one of its fields: an amount, a count or a record list.

    Matching is the answer: only those kinds have the member, which is always true.
    """

    @property
    def is_record_field(self) -> bool:
        """Always true for a kind that has it: a kind without it cannot be a field."""
        ...


@runtime_checkable
class YesNo(Protocol):
    """A kind that may be a yes/no: a count, which is one when declared non-negative."""

    @property
    def is_yes_no(self) -> bool:
        """Whether this kind is a yes/no, 1 for yes and 0 for no."""
        ...


@dataclass(frozen=True)
class ArtifactKind(Generic[V]):  # noqa: UP046  (invariant V, see above)
    """A kind of artifact, named by `<namespace>/<local id>`, with its value type.

    Build one of its subclasses (kinds.py); a package declares it on an `ArtifactCatalog` with the
    subclass's `declare`. A subclass may refuse values (`check_value`) but never reads text.
    """

    identifier: str
    value_type: type[V]

    def __post_init__(self) -> None:
        namespace, _, local_id = self.identifier.partition("/")
        # One dot is allowed, for the `<form>.<export>` kind the engine derives for a form export.
        form_id, dot, export_id = local_id.partition(".")
        try:
            Namespace(namespace).identifier(form_id)
            if dot:
                Namespace(namespace).identifier(export_id)
        except InvalidRegistrationError as exc:
            raise InvalidRegistrationError(
                f"invalid artifact kind identifier {self.identifier!r}: {exc}"
            ) from None
        if not isinstance(self.value_type, type):
            raise TypeError(f"value_type must be a type, got {self.value_type!r}")

    @property
    def label(self) -> str:
        """The local part of the identifier, for traces and messages."""
        return self.identifier.partition("/")[2]

    @staticmethod
    def labels(kinds: Iterable[ArtifactKind[Any]]) -> str:
        """The distinct labels of `kinds`, sorted, quoted and comma-separated."""
        return ", ".join(repr(label) for label in sorted({kind.label for kind in kinds}))

    @property
    def is_form_export(self) -> bool:
        """Whether this is the kind `<form>.<export>` the engine derives for a form's export."""
        return "." in self.identifier

    def check_value(self, value: V) -> None:
        """Refuse `value`, already an instance of the value type, if this kind cannot hold it.

        Called by `Artifact`; accepts every instance unless a subclass says otherwise.
        """


type Money = ArtifactKind[Decimal]
"""A money kind: its artifacts are exact `Decimal`s in the jurisdiction's currency."""


@dataclass(frozen=True, init=False)
class Artifact[T]:
    """One value of an artifact kind in one computation, checked against the kind's value type.

    A NaN or infinite `Decimal` is an InvalidAmountError; a value below zero for a non-negative kind
    is a NegativeArtifactError (zero is accepted). `BLANK` is accepted for any kind: the kind's
    checks are skipped and reading `value` is a BlankValueError.
    """

    kind: ArtifactKind[T]
    _content: T | Blank

    def __init__(self, kind: ArtifactKind[T], value: T | Blank) -> None:
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "_content", value)
        if value is BLANK:
            return
        if not isinstance(value, kind.value_type):
            raise TypeError(
                f"{kind.label} must be a {kind.value_type.__name__}, got {type(value).__name__}"
            )
        if isinstance(value, Decimal) and not value.is_finite():
            raise InvalidAmountError(f"{kind.identifier} must be finite, got {value}")
        kind.check_value(value)
        if isinstance(kind, HasFloor) and kind.is_below_floor(value):
            raise NegativeArtifactError(
                f"{kind.identifier} cannot be negative, got {value}",
                identifier=kind.identifier,
                value=value if isinstance(value, Decimal | int) else None,
            )

    @property
    def is_blank(self) -> bool:
        """Whether the filer left this line blank, which is not the same as zero."""
        return self._content is BLANK

    @property
    def value(self) -> T:
        """The value; a BlankValueError naming the kind if the artifact is blank."""
        if self._content is BLANK:
            raise BlankValueError(f"{self.kind.label} was left blank, so it has no value")
        return self._content


class ArtifactRegistry(Registry[object]):
    """The registry of artifact kinds packages declare, by full identifier (`ex/taxable_income`).

    Register through `register_catalog`. Items are stored as `object` because `ArtifactKind` is
    invariant: an `ArtifactKind[Decimal]` is not an `ArtifactKind[object]`.
    """

    def register_catalog(self, catalog: ArtifactCatalog) -> None:
        """Register every kind `catalog` declared under its identifier.

        Registering the same kind object again is skipped, so a catalog registers idempotently. An
        identifier taken by another object is an error, and then nothing from the catalog is
        registered.
        """
        pending = [kind for kind in catalog.kinds if self.identifier_of(kind) != kind.identifier]
        for kind in pending:
            if kind.identifier in self.identifiers():
                raise DuplicateRegistrationError(f"{kind.identifier!r} is already registered")
        for kind in pending:
            self.register(kind.identifier, kind)

    def extended(self, kinds: Iterable[ArtifactKind[Any]]) -> ArtifactRegistry:
        """A new registry of every kind of this one and `kinds`, which this one is not changed by.

        A kind equal to one already registered is skipped and the first stays; another kind under
        that identifier is the registry's DuplicateRegistrationError.
        """
        extended = ArtifactRegistry()
        for identifier in sorted(self.identifiers()):
            extended.register(identifier, self.get(identifier))
        for kind in kinds:
            if kind.identifier in extended.identifiers() and extended.kind(kind.identifier) == kind:
                continue
            extended.register(kind.identifier, kind)
        return extended

    def kind(self, identifier: str) -> ArtifactKind[Any]:
        """The artifact kind registered as `identifier`.

        Raises UnknownRegistrationError for an unknown identifier and InvalidRegistrationError if
        the entry is not an `ArtifactKind` or is registered under another identifier than its own.
        """
        item = self.get(identifier)
        if not isinstance(item, ArtifactKind):
            raise InvalidRegistrationError(
                f"{identifier!r} is registered as {item!r}, not as an artifact kind"
            )
        if item.identifier != identifier:
            raise InvalidRegistrationError(
                f"{identifier!r} is registered as the kind {item.identifier!r}, not as itself"
            )
        return item


class ArtifactCatalog:
    """One package's artifact kinds: builds each kind in the package's namespace and records it.

    Each package creates one, e.g. `ArtifactCatalog(Namespace("ca"))`. Declaring registers
    nothing; `ArtifactRegistry.register_catalog` does.
    """

    def __init__(self, namespace: Namespace) -> None:
        self._namespace = namespace
        self._kinds: dict[str, ArtifactKind[Any]] = {}

    @property
    def namespace(self) -> Namespace:
        """The namespace every kind of this catalog is declared in."""
        return self._namespace

    @property
    def kinds(self) -> tuple[ArtifactKind[Any], ...]:
        """Every kind declared so far, in declaration order."""
        return tuple(self._kinds.values())

    def add(self, kind: ArtifactKind[Any]) -> None:
        """Record `kind`, which its own class's `declare` builds and passes here.

        A kind outside this catalog's namespace is an InvalidRegistrationError; a local id this
        catalog already declared is an error.
        """
        namespace = kind.identifier.partition("/")[0]
        if namespace != self._namespace.name:
            raise InvalidRegistrationError(
                f"{kind.identifier!r} is not in this catalog's namespace {self._namespace.name!r}"
            )
        if kind.identifier in self._kinds:
            raise DuplicateRegistrationError(
                f"{kind.identifier!r} is already declared in this catalog"
            )
        self._kinds[kind.identifier] = kind
