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
    UnknownRegistrationError,
)
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import RecordListKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.unit import Unit


@dataclass(frozen=True, slots=True)
class CapabilitySelection:
    """One capability chosen by a manifest, with its slots filled by identifier.

    `params` maps parameter slots to families; `consumes` and `produces` map artifact slots to
    identifiers (a consumed slot may map to a list, kept as a tuple). `blank` maps a consumed slot,
    or one artifact in a `BLANK_PER_ITEM` list, to a `BlankRule`; `blank_fields` maps a record-list
    slot to a `BlankRule` per field. A slot not named refuses a blank. `optional` maps each consumed
    slot that may go without a producer to the identifier of the registered amount, count or record
    list kind the read is a list of: a record list read through one that no form supplies is a
    list of that kind and a blank, which the slot's blank rule decides (default none: every slot is
    required). The manifest checks the kind, as only it has the registry.
    `title` and `reference` are the printed wording and line label of the one figure the selection
    produces (a step the form does not print may carry plain words as its title, and no reference);
    `None` for none, and a selection producing several figures may not have either. `unit`
    names the unit of that figure (`None` for none), under the same one-figure rule.
    """

    name: str
    params: Mapping[str, str]
    consumes: Mapping[str, str | tuple[str, ...]]
    produces: Mapping[str, str]
    blank: Mapping[str, BlankRule] = dataclasses.field(default_factory=dict)
    blank_fields: Mapping[str, Mapping[str, BlankRule]] = dataclasses.field(default_factory=dict)
    optional: Mapping[str, str] = dataclasses.field(default_factory=dict)
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
        for name in ("params", "produces", "blank", "optional"):
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
        self._check_optional()

    def _check_optional(self) -> None:
        """Refuse an `optional` entry that is not a consumed slot holding one form-export figure."""
        for slot in self.optional:
            if slot not in self.consumes:
                raise InvalidManifestError(
                    f"{self.name}: optional slot {slot!r} is not a consumed slot of the selection"
                )
            named = self.consumes[slot]
            if not isinstance(named, str):
                raise InvalidManifestError(
                    f"{self.name}: optional slot {slot!r} takes a list, not one identifier"
                )
            if "." not in named:
                raise InvalidManifestError(
                    f"{self.name}: optional slot {slot!r} reads {named!r}, which is not a form's "
                    "figure of the form <form>.<label>"
                )

    def __hash__(self) -> int:
        """Hash by value, like the frozen dataclass it is; the read-only mappings are unhashable."""
        bindings = (self.params, self.consumes, self.produces, self.blank, self.optional)
        fields = frozenset(
            (slot, frozenset(rules.items())) for slot, rules in self.blank_fields.items()
        )
        return hash(
            (
                self.name,
                *(frozenset(mapping.items()) for mapping in bindings),
                fields,
            )
        )


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
    identifiers to own exports. `inputs` are the starting artifacts the form owns: it alone reads
    them, and every other form reads its export instead. See docs/forms.md for the other keys.
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
    inputs: tuple[InputDeclaration, ...] = ()
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

    @property
    def optionally_read(self) -> frozenset[str]:
        """The identifiers this form reads only through slots marked optional: a list-valued read
        of the same identifier, or an unmarked slot, makes it a required read."""
        required: set[str] = set()
        optional: set[str] = set()
        for selection in self.capabilities:
            for slot, named in selection.consumes.items():
                identifiers = (named,) if isinstance(named, str) else named
                (optional if slot in selection.optional else required).update(identifiers)
        return frozenset(optional - required)

    @property
    def unruled_optional(self) -> tuple[tuple[str, str], ...]:
        """The optional slots with no blank rule, each as (slot, identifier), in selection order."""
        return tuple(
            (slot, str(selection.consumes[slot]))
            for selection in self.capabilities
            for slot in selection.optional
            if slot not in selection.blank
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

    `forms` is a tuple of at least one form with distinct names; the first is the default form.
    Each form holds the inputs it owns (`Form.inputs`). A manifest is checked against
    `artifacts` (the application's kinds) when built, so one that exists is correct. `kinds` adds
    the `<form>.<export>` kinds and the neutral kinds the forms supply. An unresolvable default or
    `required_when` that is not a yes/no is an InvalidManifestError; an unknown identifier is an
    UnknownRegistrationError. `units_by_name` holds each unit its declarations name, by the full
    identifier they write, already looked up in the unit registry; the loader builds it and refuses
    an unknown identifier.
    """

    jurisdiction: JurisdictionCode
    version: int
    valid_from_tax_year: int
    forms: tuple[Form, ...]
    artifacts: ArtifactRegistry = dataclasses.field(compare=False)
    units_by_name: Mapping[str, Unit] = dataclasses.field(default_factory=dict, compare=False)
    kinds: ArtifactRegistry = dataclasses.field(init=False, compare=False)
    field_defaults: Mapping[str, tuple[Artifact[Any], ...]] = dataclasses.field(
        init=False, compare=False
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "forms", tuple(self.forms))
        object.__setattr__(self, "units_by_name", MappingProxyType(dict(self.units_by_name)))
        if not self.forms:
            raise InvalidManifestError("forms must name at least one form")
        names = [found.name for found in self.forms]
        for name in names:
            if names.count(name) > 1:
                raise InvalidManifestError(f"form {name!r} is listed more than once")
        self._check_predicates()
        derived = [kind for form in self.forms for kind in form.derived_kinds(self.artifacts)]
        derived += self._stand_ins(derived)
        self._check_derived(derived)
        kinds = self.artifacts.extended(derived)
        object.__setattr__(self, "kinds", kinds)
        self._check_artifacts(kinds)
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
                self.forms,
            )
        )

    def _stand_ins(self, derived: list[RecordListKind]) -> list[RecordListKind]:
        """The record list of each figure that a form reads through an optional slot and no form
        supplies, so that its blank can be read: a list of one field, the registered kind that the
        slot's declaration names.

        A declared kind that is not a registered amount, count or record list cannot be listed. A
        figure a form does supply ignores the declaration, unless the supplier's field is another
        kind than the declared one.
        """
        made: dict[str, RecordListKind] = {}
        supplied = {kind.identifier: kind for kind in derived}
        known = self.artifacts.identifiers()
        for form in self.forms:
            for selection in form.capabilities:
                for slot, declared in selection.optional.items():
                    named = str(selection.consumes[slot])
                    field = self._declared_kind(form, named, declared)
                    if named in supplied:
                        self._check_supplier(form, supplied[named], field)
                    elif named not in made and named not in known:
                        made[named] = RecordListKind(named, fields=(field,))
        return list(made.values())

    def _declared_kind(self, form: Form, named: str, declared: str) -> ArtifactKind[Any]:
        """The registered amount, count or record list `declared` names, for the optional read of
        `named`."""
        try:
            field = self.artifacts.kind(declared)
        except UnknownRegistrationError:
            raise InvalidManifestError(
                f"form {form.name!r}: {named!r} is read through an optional slot that declares "
                f"{declared!r}, which is not a registered kind"
            ) from None
        if not isinstance(field, RecordField):
            raise InvalidManifestError(
                f"form {form.name!r}: {named!r} is read through an optional slot that declares "
                f"{declared!r}, which is not an amount, a count or a record list"
            )
        return field

    @staticmethod
    def _check_supplier(form: Form, supplier: RecordListKind, declared: ArtifactKind[Any]) -> None:
        """Refuse a supplied figure whose field is not a kind of the shape the optional read
        declares: the same kind class, value type and sign rule. The identifier may differ, as a
        form may supply its own namespaced figure for a neutral list."""
        (found,) = supplier.fields
        shape = (type(found), found.value_type, getattr(found, "non_negative", None))
        wanted = (type(declared), declared.value_type, getattr(declared, "non_negative", None))
        if shape != wanted:
            raise InvalidManifestError(
                f"form {form.name!r}: {supplier.identifier!r} is read through an optional slot "
                f"that declares {declared.identifier!r}, but the form that supplies it lists "
                f"{found.identifier!r}, a different kind"
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
        for form in self.forms:
            for declaration in form.inputs:
                declaration.default_artifact(kinds.kind(declaration.name))
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
        declarations = {d.name: d for form in self.forms for d in form.inputs}
        required = {name for name, declaration in declarations.items() if declaration.required}
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
            if predicate in declarations:
                raise InvalidManifestError(
                    f"form {form.name!r}: required_when {predicate!r} is an optional input, "
                    "and the filer always answers a yes/no"
                )
            raise InvalidManifestError(
                f"form {form.name!r}: required_when {predicate!r} is not a required input "
                "or produced by a selection"
            )
