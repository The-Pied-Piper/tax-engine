"""Building a `FormComposition` in a test from kind objects, as the tests write them.

The application builds one from the manifest's `Form` and its kinds. A test that has only kinds
declares the `Form` that names them and registers them, so the composition resolves the same names.
"""

from collections.abc import Iterable
from typing import Any

from tax_engine.domain.artifact import Artifact, ArtifactKind, ArtifactRegistry
from tax_engine.domain.capability import Capability
from tax_engine.domain.form import FormComposition
from tax_engine.domain.manifest import Form
from tax_engine.domain.record_list import RecordListKind


def _declared(
    name: str,
    exports: Iterable[ArtifactKind[Any]],
    instances: ArtifactKind[Any] | None = None,
    **limits: Any,
) -> tuple[Form, ArtifactRegistry]:
    """The `Form` that names `exports` and `instances`, and a registry holding those kinds."""
    listed = tuple(exports)
    form = Form(
        name=name,
        instances=None if instances is None else instances.identifier,
        exports=tuple(kind.identifier for kind in listed),
        capabilities=(),
        required=True,
        **limits,
    )
    kinds = ArtifactRegistry()
    for kind in (*listed, *(() if instances is None else (instances,))):
        if kind.identifier not in kinds.identifiers():
            kinds.register(kind.identifier, kind)
    return form, kinds


def derived(name: str, exports: Iterable[ArtifactKind[Any]]) -> tuple[RecordListKind, ...]:
    """The kinds `<form>.<export>` the form `name` derives from `exports`."""
    form, kinds = _declared(name, exports)
    return form.derived_kinds(kinds)


def composition(
    name: str,
    capabilities: Iterable[Capability],
    *,
    exports: Iterable[ArtifactKind[Any]],
    instances: ArtifactKind[Any] | None = None,
    starting: frozenset[ArtifactKind[Any]] = frozenset(),
    max_instances: int | None = None,
    min_instances: int | None = None,
    exclusive_group: str | None = None,
    defaults: Iterable[Artifact[Any]] = (),
    field_defaults: Iterable[Artifact[Any]] = (),
) -> FormComposition:
    """The `FormComposition` of the form `name` whose exports and instances are the given kinds."""
    form, kinds = _declared(
        name,
        exports,
        instances,
        max_instances=max_instances,
        min_instances=min_instances,
        exclusive_group=exclusive_group,
    )
    return FormComposition(
        form,
        capabilities,
        kinds=kinds,
        starting=starting,
        defaults=defaults,
        field_defaults=field_defaults,
    )
