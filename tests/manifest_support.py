"""Test support: manifest inputs declared the way the manifest declares them."""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.manifest import Form, InputDeclaration, Manifest
from tax_engine.domain.record_list import RecordListKind


def required_fields(kind: RecordListKind) -> tuple[InputDeclaration, ...]:
    """A required declaration for each field of `kind`, in the kind's order."""
    return tuple(InputDeclaration(name=field.identifier, required=True) for field in kind.fields)


def required_inputs(names: Iterable[str]) -> dict[str, InputDeclaration]:
    """A required declaration for each of `names`, by identifier."""
    return {name: InputDeclaration(name=name, required=True) for name in sorted(names)}


DECLARED = ArtifactKind("ex/declared", Decimal)


def declared_manifest() -> Manifest:
    """A manifest that declares one required input and one required form, for form sets built
    in tests that are not about the manifest."""
    return Manifest(
        jurisdiction=JurisdictionCode("EX-ON"),
        version=1,
        valid_from_tax_year=2025,
        inputs=required_inputs([DECLARED.identifier]),
        forms=(
            Form(
                required=True,
                name="ex-on/declared",
                instances=None,
                exports=(DECLARED.identifier,),
                capabilities=(),
            ),
        ),
    )


def declared_artifacts() -> ArtifactRegistry:
    """The registry in which `declared_manifest` resolves."""
    found = ArtifactRegistry()
    found.register(DECLARED.identifier, DECLARED)
    return found
