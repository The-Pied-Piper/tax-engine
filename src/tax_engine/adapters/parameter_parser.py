"""Reading parameter datasets: the `ParameterParser` protocol and the registry of parsers.

A package contributes parsers in its `parameter_parsers` package; nothing registers on import: the
composition root builds a `ParameterParserRegistry` by walking each package's parsers
(`tax_engine.registrations.parameter_parsers`). Parsers are keyed by their kind's name
(`brackets`, `credit`, `rate`), which is not namespaced yet. The module is neutral on purpose: a
jurisdiction's parsers extend it without importing the outbound adapters.
"""

from __future__ import annotations

import inspect
from typing import Any, Protocol, cast, runtime_checkable

from tax_engine.adapters.yaml_support import YamlNode
from tax_engine.domain.errors import InvalidRegistrationError, UnknownRegistrationError
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.registry import Registry


class ParameterParser[T](Protocol):
    """Reads the kind-specific part of a YAML dataset file into that kind's values.

    YamlParameterSource looks the parser up by the kind requested, in a ParameterParserRegistry.
    Declare `kind` as a plain class attribute, not a property, so `@parameter_parser` can
    type-check it against `parse`.
    """

    @property
    def kind(self) -> ParameterKind[T]:
        """The parameter kind this parser reads; a dataset file declares it as `kind:`."""
        ...

    @property
    def body_keys(self) -> frozenset[str]:
        """The keys this kind adds to a dataset file, beyond the shared ones."""
        ...

    def parse(self, document: YamlNode) -> T:
        """Build this kind's values from the dataset's kind-specific keys.

        Raises YamlShapeError or a DomainError if they are malformed or invalid.
        """
        ...


@runtime_checkable
class OptionalKeysParser(Protocol):
    """A parser that also accepts keys a dataset file may leave out.

    Declare `optional_keys` as a plain class attribute beside `body_keys`; a parser without it
    accepts no optional keys. Its `parse` reads each of them with `optional_field`.
    """

    @property
    def optional_keys(self) -> frozenset[str]:
        """The keys this kind may add to a dataset file, beyond `body_keys`."""
        ...


class ParserClass[T, P](Protocol):
    """A parser class as `@parameter_parser` sees it: its kind, its `parse`, its constructor.

    Matching both `kind` and `parse` against one `T` is what lets mypy reject a parser whose
    `parse` returns another type than its kind's values; `kind` must be a class attribute.
    """

    kind: ParameterKind[T]

    def parse(self, parser: P, document: YamlNode, /) -> T:
        """The class's `parse`, unbound: called with an instance and a dataset document."""
        ...

    def __call__(self) -> P:
        """Construct the parser."""
        ...


class ParameterParserRegistry(Registry[object]):
    """Holds one parser per parameter kind; lookups by `ParameterKind[T]` give `ParameterParser[T]`.

    Its string keys are kind names (not namespaced yet); register parsers with `register_class`.
    """

    def for_kind[T](self, kind: ParameterKind[T]) -> ParameterParser[T]:
        """The parser registered for exactly `kind` (same name and value type)."""
        found = self.get(kind.name)
        if getattr(found, "kind", None) != kind:
            raise UnknownRegistrationError(
                f"no parser for parameter kind {kind.name!r} with values of {kind.value_type!r}"
            )
        # Safe: the found object's kind equals `kind`, value type included.
        return cast(ParameterParser[T], found)

    def register_class(self, cls: type) -> None:
        """Register an instance of the parser class `cls` under its kind's name.

        `cls` must declare a `ParameterKind` as its `kind` class attribute; whether its `parse`
        returns that kind's values is checked by `@parameter_parser` when mypy runs.
        """
        kind = inspect.getattr_static(cls, "kind", None)
        if not isinstance(kind, ParameterKind):
            raise InvalidRegistrationError(f"{cls.__name__} declares no parameter kind as `kind`")
        self.register(kind.name, cls())


def parameter_parser[T, P: ParameterParser[Any]](cls: ParserClass[T, P]) -> type[P]:
    """Class decorator that type-checks a parser class and registers nothing.

    A parser whose `parse` returns another type than its kind's values fails `mypy .` here
    with "Cannot infer value of type parameter". The composition root finds the decorated
    classes by walking each package's `parameter_parsers` (`parsers_in`).
    """
    return type(cls())
