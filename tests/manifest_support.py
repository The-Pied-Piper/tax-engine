"""Test support: manifest inputs declared the way the manifest declares them."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import tax_engine.jurisdictions.ca_qc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import RecordListKind
from tax_engine.domain.manifest import InputDeclaration, Manifest
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units


def input_named(manifest: Manifest, name: str) -> InputDeclaration:
    """The declaration of the input `name`, found on the one form of `manifest` that holds it."""
    (found,) = (d for form in manifest.forms for d in form.inputs if d.name == name)
    return found


def real_manifest(code: str, tax_year: int = 2025) -> Manifest:
    """The registered engine's manifest for `code` and `tax_year`, as the application loads it."""
    source = YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units())
    return source.get_jurisdiction(JurisdictionCode(code)).manifest_for(tax_year)


def inputs_of(manifest: Manifest) -> dict[str, InputDeclaration]:
    """Every input of `manifest` by name: each form's own, side by side, for a test that asks what
    the manifest declares as a whole."""
    return {d.name: d for form in manifest.forms for d in form.inputs}


def required_fields(kind: RecordListKind) -> tuple[InputDeclaration, ...]:
    """A required declaration for each field of `kind`, in the kind's order."""
    return tuple(InputDeclaration(name=field.identifier, required=True) for field in kind.fields)


def required_inputs(names: Iterable[str]) -> tuple[InputDeclaration, ...]:
    """A required declaration for each of `names`, by identifier, for the `inputs` of a form."""
    return tuple(InputDeclaration(name=name, required=True) for name in sorted(names))


# Quebec's own part that declares the salary (line 10100) input.
QC_T1_LINE_10100_INPUT = (
    Path(tax_engine.jurisdictions.ca_qc.__file__).parent
    / "manifests"
    / "2025"
    / "t1_employment_income_line_10100_inputs.yaml"
)
