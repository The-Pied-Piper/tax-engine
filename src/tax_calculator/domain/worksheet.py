"""The worksheet: one filled-in copy of a form.

A form (`tax_calculator.domain.form`) is the blank: which lines it has and how they connect. A worksheet is
the figures one run of it produced, so a form with several instances has one worksheet each.
It starts with the computation's starting artifacts and records each capability's
output artifacts as the capability is applied, holding it to its contract (design.md §3).
It never decides what runs next; ordering belongs to the composition (§5).
"""

from __future__ import annotations

import decimal
from collections.abc import Iterable
from typing import Any, cast

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import Capability
from tax_calculator.domain.errors import CapabilityContractError, DuplicateArtifactError, MissingArtifactError
from tax_calculator.domain.trace import TraceLine


class Worksheet:
    """One filled-in copy of a form: its artifacts by kind, who produced each, and the trace."""

    def __init__(self, *artifacts: Artifact[Any]) -> None:
        self._check_artifacts(artifacts)
        self._artifacts: dict[ArtifactKind[Any], Artifact[Any]] = {}
        self._producers: dict[ArtifactKind[Any], Capability] = {}
        self._trace: list[TraceLine] = []
        for artifact in artifacts:
            if artifact.kind in self._artifacts:
                raise DuplicateArtifactError(f"two starting values for {artifact.kind.label!r}")
            self._artifacts[artifact.kind] = artifact

    @property
    def trace(self) -> tuple[TraceLine, ...]:
        """Every applied capability's trace lines, in the order they were applied."""
        return tuple(self._trace)

    def get[V](self, kind: ArtifactKind[V]) -> Artifact[V]:
        """The artifact recorded for `kind`."""
        if kind not in self._artifacts:
            raise MissingArtifactError(f"no value for {kind.label!r}")
        return cast(Artifact[V], self._artifacts[kind])  # each artifact is keyed by its own kind

    def producer_of(self, kind: ArtifactKind[Any]) -> Capability | None:
        """The capability that produced the artifact of `kind`; `None` for a starting artifact."""
        if kind not in self._artifacts:
            raise MissingArtifactError(f"no value for {kind.label!r}")
        return self._producers.get(kind)

    def apply(self, capability: Capability) -> None:
        """Compute `capability` from this worksheet and record its output artifacts.

        Nothing is recorded unless the capability keeps its contract, including exact arithmetic:
        the capability runs under a `decimal` context that traps `Inexact`.
        """
        name = type(capability).__name__
        missing = {k for k in capability.consumes if k not in self._artifacts}
        if missing:
            raise MissingArtifactError(f"{name} needs {ArtifactKind.labels(missing)}")
        inputs = tuple(self._artifacts[k] for k in capability.consumes)
        # Exact arithmetic only: a result that would lose digits raises. Rounding goes through
        # a dataset's `RoundingRule`, which is the one place allowed to be inexact.
        with decimal.localcontext() as context:
            context.traps[decimal.Inexact] = True
            try:
                result = capability.compute(inputs)
            except decimal.Inexact as error:
                raise CapabilityContractError(
                    f"{name} produced an inexact result: {error}"
                ) from error
        self._check_artifacts(result.outputs)
        produced = [artifact.kind for artifact in result.outputs]
        if frozenset(produced) != capability.produces:
            raise CapabilityContractError(
                f"{name} declares {ArtifactKind.labels(capability.produces)} "
                f"but produced {ArtifactKind.labels(set(produced))}"
            )
        repeated = {k for k in produced if produced.count(k) > 1}
        if repeated:
            raise DuplicateArtifactError(
                f"{name} produced {ArtifactKind.labels(repeated)} more than once"
            )
        recorded = capability.produces & self._artifacts.keys()
        if recorded:
            raise DuplicateArtifactError(
                f"{name} produced {ArtifactKind.labels(recorded)}, already recorded"
            )
        for artifact in result.outputs:
            self._artifacts[artifact.kind] = artifact
            self._producers[artifact.kind] = capability
        self._trace.extend(result.trace)

    @staticmethod
    def _check_artifacts(artifacts: Iterable[object]) -> None:
        for artifact in artifacts:
            if not isinstance(artifact, Artifact):
                raise TypeError(f"a value must be an Artifact, got {type(artifact).__name__}")
