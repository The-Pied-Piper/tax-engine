"""Jurisdiction manifest: which capabilities run for a jurisdiction, and from which tax year.

A flat set of forms plus the declarations of the artifacts a computation starts from.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from tax_engine.domain.artifact import (
    Artifact,
    ArtifactKind,
    ArtifactRegistry,
    RecordField,
    YesNo,
)
from tax_engine.domain.blank import BlankRule
from tax_engine.domain.errors import (
    InvalidManifestError,
    InvalidRegistrationError,
)
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import RecordListKind
from tax_engine.domain.registry import Namespace


@dataclass(frozen=True, slots=True)
class CapabilitySelection:
    """One capability chosen by a manifest, with its slots filled by identifier.

    `params` maps parameter slots to families; `consumes` and `produces` map artifact slots to
    identifiers (a consumed slot may map to a list, kept as a tuple). `blank` maps a consumed slot,
    or one artifact in a `BLANK_PER_ITEM` list, to a `BlankRule`; `blank_fields` maps a record-list
    slot to a `BlankRule` per field. A slot not named refuses a blank. `title` and `reference` are
    the printed wording and line label of the one figure the selection produces; `None` for none,
    and a selection producing several figures may not have either. `unit` names the unit of that
    figure (`None` for none), under the same one-figure rule.
    """

    name: str
    params: Mapping[str, str]
    consumes: Mapping[str, str | tuple[str, ...]]
    produces: Mapping[str, str]
    blank: Mapping[str, BlankRule] = dataclasses.field(default_factory=dict)
    blank_fields: Mapping[str, Mapping[str, BlankRule]] = dataclasses.field(default_factory=dict)
    title: str | None = None
    reference: str | None = None
    unit: str | None = None

    def __post_init__(self) -> None:
        for key, given in (
            ("title", self.title),
            ("reference", self.reference),
            ("unit", self.unit),
        ):
            if given is not None and len(self.produces) != 1:
                raise InvalidManifestError(
                    f"{self.name}: a {key} belongs to the one figure a selection produces, "
                    f"but it produces {len(self.produces)}"
                )
        for name in ("params", "produces", "blank"):
            object.__setattr__(self, name, MappingProxyType(dict(getattr(self, name))))
        object.__setattr__(
            self,
            "blank_fields",
            MappingProxyType(
                {slot: MappingProxyType(dict(rules)) for slot, rules in self.blank_fields.items()}
            ),
        )
        # A list of identifiers becomes a tuple, so the selection stays frozen and hashable.
        consumes = {
            slot: named if isinstance(named, str) else tuple(named)
            for slot, named in self.consumes.items()
        }
        object.__setattr__(self, "consumes", MappingProxyType(consumes))

    def __hash__(self) -> int:
        """Hash by value, like the frozen dataclass it is; the read-only mappings are unhashable."""
        bindings = (self.params, self.consumes, self.produces, self.blank)
        fields = frozenset(
            (slot, frozenset(rules.items())) for slot, rules in self.blank_fields.items()
        )
        return hash((self.name, *(frozenset(mapping.items()) for mapping in bindings), fields))


@dataclass(frozen=True, slots=True)
class InputDeclaration:
    """How a manifest declares one input, or one field of a form's instances list.

    A required input takes no `default` or `basis`; an optional one declares both. `default` is the
    artifact read when the request leaves the line out (a blank artifact is a declared blank, `None`
    is no default); `basis` is the form's printed sentence justifying it, which nothing checks.
    `title` and `reference` are the figure's printed title and line label (`None` for none); `unit`
    names its unit, as a manifest writes it.
    """

    name: str
    required: bool
    default: Artifact[Any] | None = None
    basis: str | None = None
    title: str | None = None
    reference: str | None = None
    unit: str | None = None

    def __post_init__(self) -> None:
        Form.check_identifier("input", self.name)
        if self.required:
            for key, value in (("default", self.default), ("basis", self.basis)):
                if value is not None:
                    raise InvalidManifestError(
                        f"input {self.name!r}: a required input takes no {key}"
                    )
            return
        if self.default is None:
            raise InvalidManifestError(f"input {self.name!r}: an optional input needs a default")
        if not self.basis:
            raise InvalidManifestError(f"input {self.name!r}: an optional input needs a basis")

    def default_artifact(self, kind: ArtifactKind[Any]) -> Artifact[Any] | None:
        """The artifact of `kind` that a request leaving this input out is read as.

        `None` for a required input, which has no default. Otherwise the declared default, which
        must be an artifact of `kind`, else an InvalidManifestError naming the input.
        """
        if self.default is None:
            return None
        found = self.default.kind
        if found != kind:
            raise InvalidManifestError(
                f"input {self.name!r}: default is an artifact of {found.identifier!r}, "
                f"not of the kind {kind.identifier!r}"
            )
        return self.default


@dataclass(frozen=True, slots=True)
class Form:
    """A named group of selections run once per instance, with the artifacts it exports.

    `instances` is the record-list kind the caller supplies (`None` for one instance and no
    `fields`); `exports` are readable by every form as `<name>.<local id>`; `supplies` maps neutral
    identifiers to own exports. See docs/forms.md for the other keys.
    """

    name: str
    instances: str | None
    exports: tuple[str, ...]
    capabilities: tuple[CapabilitySelection, ...]
    required: bool
    max_instances: int | None = None
    min_instances: int | None = None
    exclusive_group: str | None = None
    required_when: str | None = None
    basis: str | None = None
    fields: tuple[InputDeclaration, ...] = ()
    title: str | None = None
    # Not hashed: a read-only mapping is unhashable, and equal forms still hash alike.
    supplies: Mapping[str, str] = dataclasses.field(default_factory=dict, hash=False)

    def derived_kinds(self, kinds: ArtifactRegistry) -> tuple[RecordListKind, ...]:
        """The kind `<form>.<export>` of each of this form's exports a record can hold, then those
        it supplies.

        Each is a record list of the export's one field, in export order, then one per neutral
        identifier in `supplies`. An export that is not an amount, a count or a record list has
        none, and supplying one is an InvalidManifestError.
        """
        namespace, _, form_id = self.name.partition("/")
        own = tuple(
            RecordListKind(f"{namespace}/{form_id}.{export.label}", fields=(export,))
            for export in (kinds.kind(identifier) for identifier in self.exports)
            if isinstance(export, RecordField)
        )
        return own + tuple(
            self._supplied(neutral, kinds.kind(export)) for neutral, export in self.supplies.items()
        )

    def _supplied(self, neutral: str, export: ArtifactKind[Any]) -> RecordListKind:
        if not isinstance(export, RecordField):
            raise InvalidManifestError(
                f"form {self.name!r}: supplies {neutral!r}: {export.identifier!r} is not an "
                "amount, a count or a record list"
            )
        return RecordListKind(neutral, fields=(export,))

    def __post_init__(self) -> None:
        object.__setattr__(self, "exports", tuple(self.exports))
        object.__setattr__(self, "supplies", MappingProxyType(dict(self.supplies)))
        object.__setattr__(self, "capabilities", tuple(self.capabilities))
        object.__setattr__(self, "fields", tuple(self.fields))
        self.check_identifier("name", self.name)
        if self.instances is not None:
            self.check_identifier("instances", self.instances)
        if not self.exports:
            raise InvalidManifestError(
                f"form {self.name!r}: exports must name at least one artifact"
            )
        self.check_exports("exports", self.exports)
        try:
            self.check_limits(self.max_instances, self.min_instances, self.instances is not None)
        except InvalidManifestError as exc:
            raise InvalidManifestError(f"form {self.name!r}: {exc}") from None
        if self.exclusive_group is not None:
            try:
                self.check_identifier("exclusive_group", self.exclusive_group)
            except InvalidManifestError as exc:
                raise InvalidManifestError(f"form {self.name!r}: {exc}") from None
        self._check_requirement()
        self._check_fields()
        self._check_supplies()

    def _check_supplies(self) -> None:
        for neutral, export in self.supplies.items():
            form_id, dot, label = neutral.partition(".")
            if not dot:
                raise InvalidManifestError(
                    f"form {self.name!r}: supplies {neutral!r} must be "
                    "<namespace>/<snake_case>.<label>"
                )
            self.check_identifier("supplies", form_id)
            self.check_identifier("supplies", f"{form_id.partition('/')[0]}/{label}")
            if export not in self.exports:
                raise InvalidManifestError(
                    f"form {self.name!r}: supplies {neutral!r}: {export!r} is not one of its "
                    "exports"
                )

    def _check_requirement(self) -> None:
        if self.required:
            for key, value in (("required_when", self.required_when), ("basis", self.basis)):
                if value is not None:
                    raise InvalidManifestError(
                        f"form {self.name!r}: a required form takes no {key}"
                    )
            return
        if self.required_when is None:
            raise InvalidManifestError(
                f"form {self.name!r}: an optional form needs a required_when"
            )
        if not self.basis:
            raise InvalidManifestError(f"form {self.name!r}: an optional form needs a basis")
        self.check_identifier("required_when", self.required_when)
        if self.required_when in self.exports:
            raise InvalidManifestError(
                f"form {self.name!r}: required_when {self.required_when!r} is one of its own "
                "exports"
            )

    def _check_fields(self) -> None:
        if self.fields and self.instances is None:
            raise InvalidManifestError(
                f"form {self.name!r}: fields belong to a form with instances"
            )
        names = [declared.name for declared in self.fields]
        for name in names:
            if names.count(name) > 1:
                raise InvalidManifestError(f"form {self.name!r}: field {name!r} is declared twice")

    @staticmethod
    def check_limits(
        max_instances: object, min_instances: object, has_instances_list: bool
    ) -> None:
        """Refuse limits no instance count could satisfy; the message does not name the form.

        Each limit must be an integer: `max_instances` at least 1, `min_instances` at least 0 and
        not above the maximum. A form without an instances list has one instance, so a
        `min_instances` above 1 can never hold.
        """
        for field, value, least in (
            ("max_instances", max_instances, 1),
            ("min_instances", min_instances, 0),
        ):
            if value is None:
                continue
            if not isinstance(value, int) or isinstance(value, bool):
                raise InvalidManifestError(
                    f"{field} must be an integer, got {type(value).__name__}"
                )
            if value < least:
                raise InvalidManifestError(f"{field} must be at least {least}, got {value}")
        if (
            isinstance(min_instances, int)
            and isinstance(max_instances, int)
            and min_instances > max_instances
        ):
            raise InvalidManifestError(
                f"min_instances {min_instances} is above max_instances {max_instances}"
            )
        if isinstance(min_instances, int) and min_instances > 1 and not has_instances_list:
            raise InvalidManifestError(
                f"min_instances {min_instances} can never hold: "
                "a form without an instances list has one instance"
            )

    @staticmethod
    def check_exports(field: str, exports: Iterable[str]) -> None:
        """Refuse an identifier that is malformed or repeats a local id, naming `field`."""
        local_ids: set[str] = set()
        for export in exports:
            Form.check_identifier(field, export)
            local_id = export.partition("/")[2]
            if local_id in local_ids:
                raise InvalidManifestError(
                    f"{field}: local id {local_id!r} is listed more than once"
                )
            local_ids.add(local_id)

    @staticmethod
    def check_identifier(field: str, identifier: str) -> None:
        """Refuse an identifier that is not `<namespace>/<snake_case>`, naming `field`."""
        namespace, _, local_id = identifier.partition("/")
        try:
            Namespace(namespace).identifier(local_id)
        except InvalidRegistrationError as exc:
            raise InvalidManifestError(f"{field} {identifier!r}: {exc}") from None


@dataclass(frozen=True, slots=True)
class Manifest:
    """One structural version of a jurisdiction's composition.

    `forms` is a tuple of at least one form with distinct names; `inputs` declare the starting
    artifacts once each, among them each form's instances kind. A manifest is checked against
    `artifacts` (the application's kinds) when built, so one that exists is correct. `kinds` adds
    the `<form>.<export>` kinds and the neutral kinds the forms supply. An unresolvable default or
    `required_when` that is not a yes/no is an InvalidManifestError; an unknown identifier is an
    UnknownRegistrationError.
    """

    jurisdiction: JurisdictionCode
    version: int
    valid_from_tax_year: int
    inputs: Mapping[str, InputDeclaration]
    forms: tuple[Form, ...]
    artifacts: ArtifactRegistry = dataclasses.field(compare=False)
    kinds: ArtifactRegistry = dataclasses.field(init=False, compare=False)
    defaults: tuple[Artifact[Any], ...] = dataclasses.field(init=False, compare=False)
    field_defaults: Mapping[str, tuple[Artifact[Any], ...]] = dataclasses.field(
        init=False, compare=False
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "inputs", MappingProxyType(dict(self.inputs)))
        object.__setattr__(self, "forms", tuple(self.forms))
        if not self.forms:
            raise InvalidManifestError("forms must name at least one form")
        names = [found.name for found in self.forms]
        for name in names:
            if names.count(name) > 1:
                raise InvalidManifestError(f"form {name!r} is listed more than once")
        if not self.inputs:
            raise InvalidManifestError("inputs must name at least one artifact")
        for name, declaration in self.inputs.items():
            if declaration.name != name:
                raise InvalidManifestError(f"input {name!r} is declared as {declaration.name!r}")
        self._check_predicates()
        derived = [kind for form in self.forms for kind in form.derived_kinds(self.artifacts)]
        self._check_derived(derived)
        kinds = self.artifacts.extended(derived)
        object.__setattr__(self, "kinds", kinds)
        self._check_artifacts(kinds)
        found = (
            declaration.default_artifact(kinds.kind(name))
            for name, declaration in self.inputs.items()
        )
        object.__setattr__(
            self, "defaults", tuple(artifact for artifact in found if artifact is not None)
        )
        object.__setattr__(
            self,
            "field_defaults",
            MappingProxyType({form.name: self._field_defaults(form, kinds) for form in self.forms}),
        )

    def __hash__(self) -> int:
        """Hash by value, like the frozen dataclass it is; the read-only mapping is unhashable."""
        return hash(
            (
                self.jurisdiction,
                self.version,
                self.valid_from_tax_year,
                frozenset(self.inputs.items()),
                self.forms,
            )
        )

    @staticmethod
    def _check_derived(derived: list[RecordListKind]) -> None:
        """Refuse an identifier two forms derive, as an export or as a supplied figure."""
        identifiers = [kind.identifier for kind in derived]
        for identifier in identifiers:
            if identifiers.count(identifier) > 1:
                raise InvalidManifestError(
                    f"{identifier!r} is derived by more than one form: a form's export is "
                    "also supplied, or two forms supply it"
                )

    def _check_artifacts(self, kinds: ArtifactRegistry) -> None:
        """Refuse what only the artifact kinds can say, naming the input or form."""
        for name in self.inputs:
            kinds.kind(name)
        for form in self.forms:
            if form.instances is not None:
                self._check_fields(form, kinds.kind(form.instances))
            if form.required_when is not None:
                kind = kinds.kind(form.required_when)
                if not (isinstance(kind, YesNo) and kind.is_yes_no):
                    raise InvalidManifestError(
                        f"form {form.name!r}: required_when {form.required_when!r} is not a "
                        "yes/no: it must be a count, 1 for yes and 0 for no"
                    )

    @staticmethod
    def _field_defaults(form: Form, kinds: ArtifactRegistry) -> tuple[Artifact[Any], ...]:
        """The artifact each optional field of `form`'s records is read as when a record leaves
        it blank, in the form's order.
        """
        if form.instances is None:
            return ()
        instances = kinds.kind(form.instances)
        if not isinstance(instances, RecordListKind):
            return ()
        by_name = {kind.identifier: kind for kind in instances.fields}
        found = (
            declaration.default_artifact(by_name[declaration.name]) for declaration in form.fields
        )
        return tuple(artifact for artifact in found if artifact is not None)

    @staticmethod
    def _check_fields(form: Form, instances: ArtifactKind[Any]) -> None:
        if not isinstance(instances, RecordListKind):
            return  # the composition refuses instances that are not a record list
        kinds = {kind.identifier: kind for kind in instances.fields}
        declared = {declaration.name: declaration for declaration in form.fields}
        for name in sorted(kinds.keys() - declared.keys()):
            raise InvalidManifestError(
                f"form {form.name!r}: field {name!r} of {instances.identifier!r} is not declared "
                "in the manifest"
            )
        for name in sorted(declared.keys() - kinds.keys()):
            raise InvalidManifestError(
                f"form {form.name!r}: field {name!r} is not a field of {instances.identifier!r}"
            )

    def _check_predicates(self) -> None:
        """Refuse a `required_when` that names nothing the manifest has or an optional input."""
        required = {name for name, declaration in self.inputs.items() if declaration.required}
        produced = {
            identifier
            for form in self.forms
            for selection in form.capabilities
            for identifier in selection.produces.values()
        }
        for form in self.forms:
            predicate = form.required_when
            if predicate is None or predicate in required | produced:
                continue
            if predicate in self.inputs:
                raise InvalidManifestError(
                    f"form {form.name!r}: required_when {predicate!r} is an optional input, "
                    "and the filer always answers a yes/no"
                )
            raise InvalidManifestError(
                f"form {form.name!r}: required_when {predicate!r} is not a required input "
                "or produced by a selection"
            )
