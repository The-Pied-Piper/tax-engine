"""The composition: wired capabilities, checked and ordered (design.md §5).

A composition is built once from capabilities and the artifact kinds a computation takes and
returns. An input that is also a declared output is carried onto the worksheet as entered, with
no producer. It rejects bad wiring when built, derives the execution order from the capabilities'
contracts, and computes by applying each capability, in that order, to a fresh worksheet.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import Capability, CapabilityRegistry
from tax_calculator.domain.errors import (
    CapabilityContractError,
    InvalidCompositionError,
    NegativeArtifactError,
)
from tax_calculator.domain.worksheet import Worksheet


class Composition:
    """Capabilities wired through artifact kinds into one computation from `inputs` to `outputs`.

    Construction fails with `InvalidCompositionError` if the wiring breaks a rule of design.md §5.
    """

    def __init__(
        self,
        capabilities: Iterable[Capability],
        *,
        inputs: frozenset[ArtifactKind[Any]],
        outputs: frozenset[ArtifactKind[Any]],
    ) -> None:
        # Sorted once by the tie-break key, so every check and the order are deterministic.
        self._capabilities = tuple(sorted(capabilities, key=self._tie_break_key))
        self._inputs = inputs
        self._outputs = outputs
        self._check_each_produces_something()
        self._producers = self._index_producers()
        self._check_inputs()
        self._check_consumes_are_satisfied()
        self._check_outputs()
        self._order = self._derive_order()

    @property
    def order(self) -> tuple[Capability, ...]:
        """The capabilities in the order they run, derived from their contracts."""
        return self._order

    def compute(self, *artifacts: Artifact[Any]) -> Worksheet:
        """Apply every capability, in `order`, to a fresh worksheet of the starting `artifacts`.

        The starting artifacts must be exactly one of each declared input kind. A capability that
        produces a value below zero for a kind declared non-negative breaks its contract: its
        `NegativeArtifactError` is raised as the `CapabilityContractError` naming it.
        """
        worksheet = Worksheet(*artifacts)
        self.check_starting_kinds((artifact.kind for artifact in artifacts), self._inputs)
        for capability in self._order:
            try:
                worksheet.apply(capability)
            except NegativeArtifactError as error:
                name = type(capability).__name__
                produced = (
                    f"{error.identifier} {error.value}, which cannot be negative"
                    if error.identifier is not None
                    else f"a value that cannot be negative: {error}"
                )
                raise CapabilityContractError(f"{name} produced {produced}") from error
        return worksheet

    def _check_each_produces_something(self) -> None:
        empty = [capability for capability in self._capabilities if not capability.produces]
        if empty:
            raise InvalidCompositionError(f"{type(empty[0]).__name__} produces nothing")

    def _index_producers(self) -> dict[ArtifactKind[Any], Capability]:
        producers: dict[ArtifactKind[Any], Capability] = {}
        for capability in self._capabilities:
            for kind in sorted(capability.produces, key=Composition.sort_key):
                if kind in producers:
                    raise InvalidCompositionError(
                        f"more than one capability produces {kind.label!r}: "
                        f"{type(producers[kind]).__name__} and {type(capability).__name__}"
                    )
                producers[kind] = capability
        return producers

    def _check_inputs(self) -> None:
        produced = self._inputs & self._producers.keys()
        if produced:
            kind = min(produced, key=Composition.sort_key)
            raise InvalidCompositionError(
                f"input {kind.label!r} is also produced by {type(self._producers[kind]).__name__}"
            )
        # An input that is also a declared output is used: it is carried onto the return as entered.
        unused = self._inputs - self._consumed() - self._outputs
        if unused:
            kind = min(unused, key=Composition.sort_key)
            raise InvalidCompositionError(f"input {kind.label!r} is consumed by nothing")

    def _check_consumes_are_satisfied(self) -> None:
        available = self._inputs | self._producers.keys()
        for capability in self._capabilities:
            unsatisfied = capability.consumes - available
            if unsatisfied:
                kind = min(unsatisfied, key=Composition.sort_key)
                message = f"no producer for {kind.label!r}, consumed by {type(capability).__name__}"
                others = self._same_identifier(kind, available)
                if others:
                    message += (
                        f" as {kind.value_type.__name__}; {kind.identifier!r} is available "
                        f"only as {others}"
                    )
                raise InvalidCompositionError(message)

    def _check_outputs(self) -> None:
        unproduced = self._outputs - self._producers.keys() - self._inputs
        if unproduced:
            kind = min(unproduced, key=Composition.sort_key)
            raise InvalidCompositionError(f"declared output {kind.label!r} is produced by nothing")
        orphans = self._producers.keys() - self._consumed() - self._outputs
        if orphans:
            kind = min(orphans, key=Composition.sort_key)
            raise InvalidCompositionError(
                f"orphan output {kind.label!r}: produced by "
                f"{type(self._producers[kind]).__name__}, consumed by nothing and not declared "
                "an output"
            )

    @staticmethod
    def check_starting_kinds(
        given: Iterable[ArtifactKind[Any]], inputs: frozenset[ArtifactKind[Any]]
    ) -> None:
        """Refuse a `given` that has a kind beyond `inputs` or lacks one of them."""
        kinds = frozenset(given)
        extra = kinds - inputs
        if extra:
            verb = "is not an input" if len(extra) == 1 else "are not inputs"
            raise InvalidCompositionError(
                f"{ArtifactKind.labels(extra)} {verb} of this composition"
                f"{Composition.value_type_hints(extra, inputs)}"
            )
        missing = inputs - kinds
        if missing:
            noun = "input" if len(missing) == 1 else "inputs"
            raise InvalidCompositionError(f"missing {noun} {ArtifactKind.labels(missing)}")

    @staticmethod
    def value_type_hints(
        extra: Iterable[ArtifactKind[Any]], inputs: Iterable[ArtifactKind[Any]]
    ) -> str:
        """A hint for each extra kind that has an input's identifier but another value type."""
        hints = ""
        for kind in sorted(extra, key=Composition.sort_key):
            expected = Composition._same_identifier(kind, inputs)
            if expected:
                hints += (
                    f"; {kind.label!r} was given as {kind.value_type.__name__} but the input "
                    f"takes {expected}"
                )
        return hints

    def _derive_order(self) -> tuple[Capability, ...]:
        # `pending` stays in tie-break-key order, so the first ready capability is the one to run.
        pending = list(self._capabilities)
        done: set[ArtifactKind[Any]] = set(self._inputs)
        order: list[Capability] = []
        while pending:
            chosen = next((c for c in pending if c.consumes <= done), None)
            if chosen is None:
                raise InvalidCompositionError(
                    f"cycle involving {ArtifactKind.labels(self._cycle_kinds(pending))}"
                )
            pending.remove(chosen)
            order.append(chosen)
            done |= chosen.produces
        return tuple(order)

    def _consumed(self) -> set[ArtifactKind[Any]]:
        return {kind for capability in self._capabilities for kind in capability.consumes}

    @staticmethod
    def _same_identifier(kind: ArtifactKind[Any], among: Iterable[ArtifactKind[Any]]) -> str:
        """The value types, comma-separated, of the kinds in `among` with `kind`'s identifier."""
        return ", ".join(
            sorted(
                other.value_type.__name__ for other in among if other.identifier == kind.identifier
            )
        )

    def _cycle_kinds(self, stuck: list[Capability]) -> set[ArtifactKind[Any]]:
        """The kinds wired between the capabilities on a cycle, among those that could not run."""
        remaining = list(stuck)
        while True:
            sinks = [
                capability
                for capability in remaining
                if not any(capability.produces & other.consumes for other in remaining)
            ]
            if not sinks:
                break
            remaining = [capability for capability in remaining if capability not in sinks]
        consumed = {kind for capability in remaining for kind in capability.consumes}
        return {kind for capability in remaining for kind in capability.produces & consumed}

    @classmethod
    def _tie_break_key(cls, capability: Capability) -> tuple[str, tuple[tuple[str, str], ...]]:
        """Its registered identifier, else its class name; then the kinds it produces."""
        capability_class = type(capability)
        identifier = CapabilityRegistry.shared().identifier_of(capability_class)
        produced = tuple(sorted(cls.sort_key(kind) for kind in capability.produces))
        return (identifier if identifier is not None else capability_class.__name__, produced)

    @staticmethod
    def sort_key(kind: ArtifactKind[Any]) -> tuple[str, str]:
        """Its identifier, then its value type's name."""
        return (kind.identifier, kind.value_type.__name__)
