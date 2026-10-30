"""Artifacts: the named intermediate values that capabilities consume and produce.

Ordering in the engine is expressed through artifacts, never through direct
capability-to-capability dependencies (design.md §2). An `ArtifactKind[V]` names a kind of
artifact by a namespaced identifier such as `ex/taxable_income` and states the type of its
values; an `Artifact[V]` is one value of a kind, produced in one computation. Each package
declares its kinds through one `ArtifactCatalog`, which only records them; the composition root
registers each catalog explicitly with `ArtifactRegistry.register_catalog`. A `Decimal` kind, or
an `int` kind such as a count, may be declared non-negative, and then no artifact of it holds a
value below zero. A kind that carries more than its value type, such as a record-list kind
(record_list.py) or a digits kind (digits.py), is built by its own class and recorded with
`ArtifactCatalog.add`. Names come from the jurisdiction's own law or return, never from another
system's.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Generic, TypeVar

from tax_engine.domain.errors import (
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


@dataclass(frozen=True)
class ArtifactKind(Generic[V]):  # noqa: UP046  (invariant V, see above)
    """A kind of artifact, named by its identifier `<namespace>/<local id>`, and its value type.

    A `Decimal` or `int` kind with `non_negative` set never holds a value below zero. Built
    directly it is unregistered; packages declare theirs through an `ArtifactCatalog`.
    """

    identifier: str
    value_type: type[V]
    non_negative: bool = False

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
        # `bool` is a subclass of `int` but not a count, so the int check is exact.
        if self.non_negative and not (
            issubclass(self.value_type, Decimal) or self.value_type is int
        ):
            raise InvalidRegistrationError(
                f"artifact kind {self.identifier!r} cannot be non-negative: only a Decimal or "
                f"int kind can, not a {self.value_type.__name__} one"
            )

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

        Called by `Artifact`; a kind accepts every instance unless a subclass says otherwise, as
        `RecordListKind` does for a record list of other fields and `DigitsKind` for text that is
        not its digits.
        """


type Money = ArtifactKind[Decimal]
"""A money kind: its artifacts are exact `Decimal`s in the jurisdiction's currency."""


@dataclass(frozen=True)
class Artifact[T]:
    """One value of an artifact kind in one computation, checked against the kind's value type.

    A `Decimal` that is NaN or infinite is an InvalidAmountError, whatever the kind. A value below
    zero for a kind declared non-negative is a NegativeArtifactError; zero, signed or not, is
    accepted.
    """

    kind: ArtifactKind[T]
    value: T

    def __post_init__(self) -> None:
        if not isinstance(self.value, self.kind.value_type):
            raise TypeError(
                f"{self.kind.label} must be a {self.kind.value_type.__name__}, "
                f"got {type(self.value).__name__}"
            )
        if isinstance(self.value, Decimal) and not self.value.is_finite():
            raise InvalidAmountError(f"{self.kind.identifier} must be finite, got {self.value}")
        self.kind.check_value(self.value)
        if self.kind.non_negative and isinstance(self.value, Decimal | int) and self.value < 0:
            raise NegativeArtifactError(
                f"{self.kind.identifier} cannot be negative, got {self.value}",
                identifier=self.kind.identifier,
                value=self.value,
            )


class ArtifactRegistry(Registry[object]):
    """The registry of artifact kinds packages declare, by full identifier (`ex/taxable_income`).

    Register through `register_catalog`. Items are stored as `object` because `ArtifactKind` is
    invariant: an `ArtifactKind[Decimal]` is not an `ArtifactKind[object]`.
    """

    def register_catalog(self, catalog: ArtifactCatalog) -> None:
        """Register every kind `catalog` declared under its identifier.

        A kind already registered as that same object is skipped, so registering one catalog
        twice is idempotent; an identifier taken by anything else is an error, and then nothing
        from the catalog is registered.
        """
        pending = [kind for kind in catalog.kinds if self.identifier_of(kind) != kind.identifier]
        for kind in pending:
            if kind.identifier in self.identifiers():
                raise DuplicateRegistrationError(f"{kind.identifier!r} is already registered")
        for kind in pending:
            self.register(kind.identifier, kind)

    def register_kind(self, kind: ArtifactKind[Any]) -> None:
        """Register `kind` under its own identifier.

        The same kind again (equal to the one registered) is skipped and the first stays; another
        kind under that identifier is the registry's DuplicateRegistrationError.
        """
        if kind.identifier in self.identifiers() and self.kind(kind.identifier) == kind:
            return
        self.register(kind.identifier, kind)

    def kind(self, identifier: str) -> ArtifactKind[Any]:
        """The artifact kind registered as `identifier`.

        An unknown identifier is the registry's UnknownRegistrationError; an entry that is not an
        `ArtifactKind`, or a kind registered under another identifier than its own, is an
        InvalidRegistrationError naming the identifier.
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

    def declare[T](
        self, local_id: str, value_type: type[T], *, non_negative: bool = False
    ) -> ArtifactKind[T]:
        """Declare the kind `<namespace>/<local_id>` with values of `value_type` and record it.

        `non_negative` declares that its values are never below zero (a `Decimal` or `int` kind
        only). A local id this catalog already declared is an error.
        """
        kind = ArtifactKind(self._namespace.identifier(local_id), value_type, non_negative)
        self.add(kind)
        return kind

    def add(self, kind: ArtifactKind[Any]) -> None:
        """Record `kind`, built by its own class, such as a record-list kind or a digits kind.

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
