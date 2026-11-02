"""The artifact kinds of the bundled packages, built once per test process for tests to hand on.

The application builds its kinds once at wiring (`tax_engine.registrations.artifact_kinds`); a
test that needs them takes this one registry so the catalogs are not registered over and over.
A test that registers its own kinds builds a private `ArtifactRegistry` instead.
"""

from collections.abc import Iterable
from decimal import Decimal
from functools import cache
from typing import Any

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.registrations import JURISDICTIONS, artifact_kinds


@cache
def bundled_kinds() -> ArtifactRegistry:
    """The kinds of every bundled package; never register into it."""
    return artifact_kinds()


@cache
def ca_on_kinds() -> ArtifactRegistry:
    """The kinds of the bundled packages and the `<form>.<export>` kinds the 2025 Ontario
    manifest derives: what its manifest names. Never register into it.
    """
    source = YamlJurisdictionSource(JURISDICTIONS.roots(), bundled_kinds())
    return source.get_jurisdiction(JurisdictionCode("CA-ON")).manifest_for(2025).kinds


class AutoKinds(ArtifactRegistry):
    """A registry that declares a kind the first time it is asked for, for tests of a manifest's
    own rules that name made-up artifacts: an amount, or a non-negative count if the identifier
    is in `counts`. A kind registered beforehand is used as it is.
    """

    def __init__(self, counts: Iterable[str] = ()) -> None:
        super().__init__()
        self._counts = frozenset(counts)

    def kind(self, identifier: str) -> ArtifactKind[Any]:
        if identifier not in self.identifiers():
            if identifier in self._counts:
                self.register(identifier, ArtifactKind(identifier, int, non_negative=True))
            else:
                self.register(identifier, ArtifactKind(identifier, Decimal))
        return super().kind(identifier)

    def extended(self, kinds: Iterable[ArtifactKind[Any]]) -> ArtifactRegistry:
        extended = AutoKinds(self._counts)
        for identifier in self.identifiers():
            extended.register(identifier, self.get(identifier))
        for kind in kinds:
            extended.register(kind.identifier, kind)
        return extended
