"""The ParameterParser protocol: how one parameter kind's part of a YAML dataset is read."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from tax_calculator.adapters.outbound.yaml_support import YamlNode
from tax_calculator.domain.parameters.kind import ParameterKind


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
