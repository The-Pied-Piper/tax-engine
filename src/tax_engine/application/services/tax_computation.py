"""Tax computation: a jurisdiction's manifest for a tax year built into a set of forms, run.

The service does I/O only. Each composed `FormSet` is cached per jurisdiction and tax year; sharing
it is safe because `FormSet.compute` never writes to the forms.
"""

from __future__ import annotations

from threading import Lock
from typing import Any

from tax_engine.application.ports.jurisdiction_source import JurisdictionSource
from tax_engine.application.ports.parameter_source import ParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactRegistry
from tax_engine.domain.capability import Capability, CapabilityRegistry
from tax_engine.domain.capability_builder import CapabilityBuilder
from tax_engine.domain.form import FormComposition, FormSet
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.worksheet import Worksheet


class TaxComputationService:
    """Builds and runs the set of forms (a `FormSet`) a manifest describes for a tax year."""

    def __init__(
        self,
        jurisdictions: JurisdictionSource,
        parameters: ParameterSource,
        capabilities: CapabilityRegistry,
    ) -> None:
        """Resolve manifests, datasets and capability classes through these."""
        self._jurisdictions = jurisdictions
        self._parameters = parameters
        self._capabilities = capabilities
        self._builder = CapabilityBuilder()
        self._composed: dict[tuple[JurisdictionCode, int], FormSet] = {}
        self._lock = Lock()

    def compose(self, code: JurisdictionCode, tax_year: int) -> FormSet:
        """The forms of the manifest that applies to `tax_year` in `code`, wired.

        The same `FormSet` is returned on every call for the same `code` and `tax_year`. A lock is
        held for a whole compose, so concurrent callers of a cold key wait.
        """
        with self._lock:
            key = (code, tax_year)
            if key not in self._composed:
                self._composed[key] = self._compose(code, tax_year)
            return self._composed[key]

    def _compose(self, code: JurisdictionCode, tax_year: int) -> FormSet:
        jurisdiction = self._jurisdictions.get_jurisdiction(code)
        manifest = jurisdiction.manifest_for(tax_year)
        kinds = manifest.kinds
        inputs = frozenset(kinds.kind(identifier) for identifier in manifest.inputs)
        return FormSet(
            [
                FormComposition(
                    form,
                    [
                        self._capability(selection, tax_year, kinds)
                        for selection in form.capabilities
                    ],
                    kinds=kinds,
                    starting=inputs,
                    defaults=manifest.defaults,
                    field_defaults=manifest.field_defaults[form.name],
                    declared=manifest.inputs.values(),
                    units=manifest.units_by_name,
                )
                for form in manifest.forms
            ],
            inputs=inputs,
            defaults=manifest.defaults,
        )

    def compute(
        self, code: JurisdictionCode, tax_year: int, *artifacts: Artifact[Any]
    ) -> dict[str, tuple[Worksheet, ...]]:
        """The worksheets of every form, by form name, from `artifacts`.

        `artifacts` are one of each declared input kind, among them each form's instances. An
        optional input left out, or given blank where its default is a value, is read as its
        manifest default; a required one left out is refused, naming it. Each form has one worksheet
        per instance, in instance order.
        """
        return self.compose(code, tax_year).compute(*artifacts)

    def _capability(
        self, selection: CapabilitySelection, tax_year: int, kinds: ArtifactRegistry
    ) -> Capability:
        cls = self._capabilities.get(selection.name)
        # Only slots the class declares are fetched; the builder reports any other key.
        datasets: dict[str, ParameterDataset[Any]] = {
            slot: self._parameters.get(family, tax_year, cls.PARAMETERS[slot])
            for slot, family in selection.params.items()
            if slot in cls.PARAMETERS
        }
        return self._builder.build(selection, cls, datasets, kinds)
