"""Builds one capability from a manifest selection (design.md §4).

The selection fills slots by identifier. The builder resolves artifact kinds from the registry it
is given; datasets are resolved by the caller. It checks the selection fills exactly the slots the
capability class declares, each in its own section, and that each resolved dataset is the family
the selection names and of the slot's kind; a list slot takes a list of distinct identifiers and
is resolved to their kinds in the same order. Then it calls the constructor by keyword.
Value types of kinds are the constructor's check; the builder re-raises the constructor's
rejection naming the selection, and never calls ports.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.domain.blank import PASS_ON, BlankRule
from tax_engine.domain.capability import Capability
from tax_engine.domain.errors import InvalidCapabilityError, InvalidSelectionError
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.domain.parameters.datasets import ParameterDataset

_SECTIONS = (("params", "PARAMETERS"), ("consumes", "CONSUMES"), ("produces", "PRODUCES"))
_SLOT_NOUNS = {
    "PARAMETERS": "parameter slot",
    "CONSUMES": "consumed slot",
    "PRODUCES": "produced slot",
}


class CapabilityBuilder:
    """Builds a capability of a class from a selection, its resolved datasets and a registry."""

    def build(
        self,
        selection: CapabilitySelection,
        cls: type[Capability],
        datasets: Mapping[str, ParameterDataset[Any]],
        artifacts: ArtifactRegistry,
    ) -> Capability:
        """A `cls` built from the resolved `datasets`, keyed by slot, and kinds from `artifacts`.

        A list slot is resolved to a tuple of kinds, one per identifier in the order named.
        Raises InvalidSelectionError naming the selection and slot if the selection does not fill
        exactly `cls`'s slots, fills a list slot with other than a list of distinct identifiers or
        another slot with a list, or a resolved dataset is missing, extra, or not what the
        selection names; the constructor's InvalidCapabilityError (a kind of the wrong value type,
        or one kind filling two slots) is re-raised as InvalidSelectionError naming the selection,
        chained to it. Lookup errors from `artifacts.kind` propagate unchanged.
        """
        who = self._describe(selection)
        self._check_sections(selection, cls, who)
        arguments = {
            **self._parameter_arguments(selection, cls, datasets, who),
            **self._artifact_arguments(selection, cls, artifacts, who),
        }
        # `type[Capability]` cannot describe a subclass's constructor, so it is called through
        # `Callable[..., Capability]`: a deliberate, documented loosening at the manifest
        # boundary. Slot names were checked against `__init__` when the class was defined,
        # dataset kinds by `_parameter_arguments`, and kinds' value types are checked by
        # `Capability.__init__`.
        constructor: Callable[..., Capability] = cls
        try:
            return constructor(**arguments).with_blank_rules(self._blank_rules(selection, cls, who))
        except InvalidCapabilityError as error:
            raise InvalidSelectionError(f"{who}: {error}") from error

    @classmethod
    def _blank_rules(
        cls, selection: CapabilitySelection, capability: type[Capability], who: str
    ) -> dict[str, BlankRule]:
        """What a blank does in each slot the selection names: `pass_on`, else the fallback text
        read as the slot's own value type (a `Decimal`, or an `int` for a count slot).
        """
        rules: dict[str, BlankRule] = {}
        for slot, text in selection.blank.items():
            if text == "pass_on":
                rules[slot] = PASS_ON
                continue
            if slot not in capability.CONSUMES:
                raise InvalidSelectionError(
                    f"{who}: {slot!r} is given under blank but is not a consumed slot of "
                    f"{capability.__name__}"
                )
            value_type = capability.slot_value_type(slot)
            try:
                rules[slot] = value_type(text)
            except (ValueError, ArithmeticError):
                raise InvalidSelectionError(
                    f"{who}: blank rule for slot {slot!r} must be pass_on or a "
                    f"{value_type.__name__}, got {text!r}"
                ) from None
        return rules

    def _parameter_arguments(
        self,
        selection: CapabilitySelection,
        cls: type[Capability],
        datasets: Mapping[str, ParameterDataset[Any]],
        who: str,
    ) -> dict[str, ParameterDataset[Any]]:
        """Each parameter slot's dataset, checked to be the family and kind the slot takes."""
        self._check_no_extra(datasets, cls.PARAMETERS, "dataset", "a parameter slot", cls, who)
        arguments: dict[str, ParameterDataset[Any]] = {}
        for slot, kind in cls.PARAMETERS.items():
            if slot not in datasets:
                raise InvalidSelectionError(
                    f"{who}: parameter slot {slot!r} has no resolved dataset"
                )
            dataset, family = datasets[slot], selection.params[slot]
            if dataset.family != family:
                raise InvalidSelectionError(
                    f"{who}: parameter slot {slot!r} names family {family!r}, "
                    f"but was resolved to {dataset.family!r}"
                )
            if dataset.kind != kind:
                raise InvalidSelectionError(
                    f"{who}: parameter slot {slot!r} takes a dataset of kind {kind.name!r}, "
                    f"got {dataset.family!r} of kind {dataset.kind.name!r}"
                )
            arguments[slot] = dataset
        return arguments

    def _artifact_arguments(
        self,
        selection: CapabilitySelection,
        cls: type[Capability],
        artifacts: ArtifactRegistry,
        who: str,
    ) -> dict[str, ArtifactKind[Any] | tuple[ArtifactKind[Any], ...]]:
        """Each slot's kind, or a list slot's kinds in the order named, from `artifacts`."""
        named = {**selection.consumes, **selection.produces}
        arguments: dict[str, ArtifactKind[Any] | tuple[ArtifactKind[Any], ...]] = {}
        for slot in {**cls.CONSUMES, **cls.PRODUCES}:
            if cls.is_list_slot(slot):
                arguments[slot] = self._listed_kinds(slot, named[slot], artifacts, who)
            else:
                arguments[slot] = self._single_kind(slot, named[slot], artifacts, who)
        return arguments

    @staticmethod
    def _single_kind(
        slot: str, named: str | tuple[str, ...], artifacts: ArtifactRegistry, who: str
    ) -> ArtifactKind[Any]:
        """The kind registered as the one identifier named for a single slot."""
        if not isinstance(named, str):
            raise InvalidSelectionError(
                f"{who}: artifact slot {slot!r} takes one identifier, but is given a list {named!r}"
            )
        return artifacts.kind(named)

    @staticmethod
    def _listed_kinds(
        slot: str, named: str | tuple[str, ...], artifacts: ArtifactRegistry, who: str
    ) -> tuple[ArtifactKind[Any], ...]:
        """The kinds registered as the distinct identifiers named for a list slot, in that order."""
        if isinstance(named, str):
            raise InvalidSelectionError(
                f"{who}: list slot {slot!r} takes a list of identifiers, but is given {named!r}"
            )
        for position, identifier in enumerate(named):
            if identifier in named[:position]:
                raise InvalidSelectionError(
                    f"{who}: list slot {slot!r} lists {identifier!r} more than once"
                )
        return tuple(artifacts.kind(identifier) for identifier in named)

    @staticmethod
    def _describe(selection: CapabilitySelection) -> str:
        """The selection's name and produced identifiers, which tell repeated names apart."""
        produced = ", ".join(sorted(selection.produces.values())) or "nothing"
        return f"{selection.name} (produces {produced})"

    @staticmethod
    def _check_sections(selection: CapabilitySelection, cls: type[Capability], who: str) -> None:
        """Every key in each section names a slot of that section, and every slot is filled."""
        declared: dict[str, Mapping[str, object]] = {
            mapping: getattr(cls, mapping) for _section, mapping in _SECTIONS
        }
        for section, mapping in _SECTIONS:
            for slot in getattr(selection, section):
                if slot in declared[mapping]:
                    continue
                other = next((m for m, slots in declared.items() if slot in slots), None)
                what = "not a slot" if other is None else f"a {_SLOT_NOUNS[other]}"
                raise InvalidSelectionError(
                    f"{who}: {slot!r} is given under {section} but is {what} of {cls.__name__}"
                )
        for section, mapping in _SECTIONS:
            for slot in declared[mapping]:
                if slot not in getattr(selection, section):
                    raise InvalidSelectionError(
                        f"{who}: {_SLOT_NOUNS[mapping]} {slot!r} of {cls.__name__} "
                        f"is not filled under {section}"
                    )

    @staticmethod
    def _check_no_extra(
        resolved: Mapping[str, object],
        slots: Mapping[str, object],
        noun: str,
        slot_noun: str,
        cls: type[Capability],
        who: str,
    ) -> None:
        """Nothing was resolved for a key that is not one of `slots`."""
        for key in resolved:
            if key not in slots:
                raise InvalidSelectionError(
                    f"{who}: a {noun} was resolved for {key!r}, which is not {slot_noun} "
                    f"of {cls.__name__}"
                )
