"""Reads jurisdictions from YAML manifest files. Implements JurisdictionSource.

The source takes a mapping of namespace -> jurisdiction package directory. A jurisdiction's
namespace is its code lower-cased (`EX-ON` -> `ex-on`). Each `*.yaml` / `*.yml` file directly in
`<roots[ex-on]>/manifests/` is one whole manifest, and each subfolder there is one manifest too,
merged from its parts: every `*.yaml` / `*.yml` file inside it (recursively), read in sorted path
order. A part may carry any of the six manifest keys or a `form:` key; the scalar keys
(`jurisdiction`, `version`, `valid_from_tax_year`) must each be in exactly one part, and the lists
(`inputs`, `outputs`, `capabilities`) are concatenated in part order, an identifier listed in two
parts of `inputs` or of `outputs` being rejected. The merged mapping then goes through the same
parse as a whole file. A manifest naming another jurisdiction is rejected.
A manifest is a flat set of forms. A part with a `form:` key (`name`, and `exports` with an optional
`instances`, all identifiers `<namespace>/<snake_case>`) gives all its `capabilities` to that
form; without `instances` the form has one instance. A part without one joins the default
form, named `<namespace>/return` and otherwise an ordinary form: its exports are the
manifest's `outputs`. A form may span parts that carry the same `form.name`, in part order:
exactly one of them declares `exports` (with its `instances`), and a second that does is rejected.
A form without `instances` has a default list of one instance, and limits apply to its count.
That part may also declare `max_instances` (an integer of at least 1), `min_instances` (an integer
of at least 0, not above `max_instances`) and `exclusive_group` (an identifier): the most and the
fewest instances the form may have, and a group of forms of which at most one may have instances.
Any of these keys in a part that does not declare `exports`, or repeated by a second part, is
rejected.
A part with a `form:` key takes no `inputs` or `outputs`: inputs are derived, exports are declared
in the `form:` block. The default form's name is reserved for the parts without a `form:` key; a
`form:` part naming it is rejected, naming the part. The default form's `outputs` are its exports,
so two with one local id (`ex/x` and `ca/x`, both `<ns>/return.x`) are rejected as "outputs".
A single manifest file is not a part and takes no `form:` key: all of it is the default form.
Each selection names a capability and fills its slots: `params` (slot -> family, optional),
`consumes` (slot -> artifact identifier, or a list of them kept in order as a tuple, optional)
`blank` (consumed slot, or one artifact identifier in a list slot -> what a blank in it does: the
text of a fallback value, `pass_on`, or `compute`, which leaves it to the class; optional, a slot
not named refuses a blank) and
`produces` (slot -> artifact identifier, required, at least one). Slot names, and whether a
slot takes one identifier or a list, are not checked against capability classes here.
The top-level `outputs` list the default form's exports: a required, non-empty list of non-empty
strings without duplicates (an identifier in both `inputs` and `outputs` is an input carried onto
the return as entered).
Every input says whether it is required: `inputs` is a required, non-empty list of mappings with
`name` and `required` (`true` or `false`, nothing implicit; a bare identifier is rejected). An
optional input also declares `default` and `basis`: `default` is written as the value the request
is read as when it leaves the line out (`null` for blank, a quoted figure such as `"0"`, `[]`, or
`""`), and must be present even when `null`; `basis` is the printed sentence of the form that
justifies it, which the loader keeps but does not check. A required input takes neither.
A `form:` block that declares `exports` also declares `required` (`true` or `false`) and, for an
optional form, `required_when` (the identifier of the yes/no artifact that says when the form is
needed: a required input or an artifact a selection produces, never one of its own exports) and
`basis` (the printed "Complete this form if" sentence); a required form takes neither. A form with
`instances` lists `fields`, one mapping per field of the instances kind, declared like inputs
(`name`, `required`, and for an optional one `default` and `basis`); a form without `instances` has
none. Which fields the instances kind has, that defaults suit their kinds and that a predicate is a
yes/no count are checked when the manifest is loaded (the `Manifest` is built with the kinds), and
an artifact the kinds do not have is an InvalidManifestError naming the file.
Any of these keys in a part that does not declare `exports` is rejected. The default form is
always required.
The default form has no `form:` block, so its title is the manifest's own optional `title` line,
beside `jurisdiction`, `version` and `valid_from_tax_year`; like those scalar keys it may be in only
one part.
Titles are for the reader of a trace: the `form:` block that declares `exports` may carry a
`title` (the form's printed name), and a selection may carry a `title` (the printed wording of
the one figure it produces; a selection producing several figures is rejected). A selection may
also carry a `reference`, what the form prints beside the figure it produces, as free text. All
are non-empty text, optional, and never used to look anything up: the identifier stays the unique
name.
Parsing is strict because a manifest must stay selection plus slot bindings
(design.md §4): unknown keys, duplicate keys and wrongly typed values are
rejected with the offending file (for a folder, the offending part) named, never coerced or
ignored.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, NamedTuple

import yaml

from tax_engine.adapters.outbound.yaml_support import YamlNode, YamlShapeError
from tax_engine.adapters.text import read_default, read_number
from tax_engine.domain.artifact import Artifact, ArtifactKind, ArtifactRegistry
from tax_engine.domain.blank import COMPUTE, PASS_ON, BlankRule
from tax_engine.domain.errors import (
    DomainError,
    InvalidJurisdictionCodeError,
    InvalidManifestError,
    InvalidRegistrationError,
    InvalidTextError,
    NotFoundError,
    UnknownRegistrationError,
)
from tax_engine.domain.jurisdiction import Jurisdiction
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import RecordListKind
from tax_engine.domain.manifest import (
    CapabilitySelection,
    Form,
    InputDeclaration,
    Manifest,
)
from tax_engine.domain.registry import Namespace

_MANIFEST_KEYS = frozenset(
    {"jurisdiction", "version", "valid_from_tax_year", "inputs", "outputs", "capabilities"}
)
_OPTIONAL_MANIFEST_KEYS = frozenset({"title"})
_PART_KEYS = _MANIFEST_KEYS | _OPTIONAL_MANIFEST_KEYS | {"form"}
_FORM_KEYS = frozenset({"name"})
_OPTIONAL_FORM_KEYS = frozenset(
    {
        "instances",
        "exports",
        "max_instances",
        "min_instances",
        "exclusive_group",
        "required",
        "required_when",
        "basis",
        "fields",
        "title",
    }
)
_OPTIONAL_INPUT_KEYS = frozenset({"default", "basis"})
_DEFAULT_FORM = "return"
_CAPABILITY_KEYS = frozenset({"name", "produces"})
_OPTIONAL_CAPABILITY_KEYS = frozenset({"params", "consumes", "blank", "title", "reference"})
_SCALAR_KEYS = ("jurisdiction", "version", "valid_from_tax_year", "title")
_IDENTIFIER_LISTS = ("inputs", "outputs")
_PATTERNS = ("*.yaml", "*.yml")


class _Declaration(NamedTuple):
    """What the one part of a form that declares its instances and exports declares."""

    instances: str | None
    exports: tuple[str, ...]
    max_instances: int | None
    min_instances: int | None
    exclusive_group: str | None
    required: bool
    required_when: str | None
    basis: str | None
    title: str | None
    fields: tuple[InputDeclaration, ...]

    def form(self, name: str, selections: tuple[CapabilitySelection, ...]) -> Form:
        """The form `name` with this declaration and `selections`, which checks the declaration."""
        return Form(
            name=name,
            instances=self.instances,
            exports=self.exports,
            capabilities=selections,
            max_instances=self.max_instances,
            min_instances=self.min_instances,
            exclusive_group=self.exclusive_group,
            required=self.required,
            required_when=self.required_when,
            basis=self.basis,
            title=self.title,
            fields=self.fields,
        )


class YamlJurisdictionSource:
    """Jurisdictions read from the `manifests/` directory of each jurisdiction package."""

    def __init__(self, roots: Mapping[Namespace, Path], kinds: ArtifactRegistry) -> None:
        """Read manifests under each namespace's package directory in `roots`.

        Each manifest is built with `kinds`, which reads and checks what it declares.
        """
        self._roots = dict(roots)
        self._kinds = kinds

    def get_jurisdiction(self, code: JurisdictionCode) -> Jurisdiction:
        """The jurisdiction with every manifest in its package; see JurisdictionSource."""
        manifests = tuple(self._load_all(code))
        if not manifests:
            raise NotFoundError(f"no manifests for jurisdiction {code} in {self._manifests(code)}")
        return Jurisdiction(code=code, manifests=manifests)

    def _load_all(self, code: JurisdictionCode) -> list[Manifest]:
        manifests = self._manifests(code)
        if not manifests.parent.is_dir():
            raise InvalidManifestError(f"package directory not found: {manifests.parent}")
        if not manifests.is_dir():
            return []
        paths = sorted(
            p
            for p in manifests.iterdir()
            if (p.is_dir() and self._parts(p))
            or (p.is_file() and any(p.match(pattern) for pattern in _PATTERNS))
        )
        return [self._load_for(code, path) for path in paths]

    def _manifests(self, code: JurisdictionCode) -> Path:
        namespace = code.namespace
        if namespace not in self._roots:
            raise NotFoundError(
                f"no jurisdiction {code}: no jurisdiction package declares namespace "
                f"{namespace.name!r}"
            )
        return self._roots[namespace] / "manifests"

    def _load_for(self, code: JurisdictionCode, path: Path) -> Manifest:
        manifest = self.load(path)
        if manifest.jurisdiction != code:
            raise InvalidManifestError(
                f"{path}: manifest is for {manifest.jurisdiction}, but its package is {code}'s"
            )
        return manifest

    def load(self, path: Path) -> Manifest:
        """The manifest in the file `path`, or merged from the parts in the folder `path`."""
        if path.is_dir():
            return self._load_folder(path)
        try:
            document = YamlNode.load(path, "manifest")
        except (OSError, yaml.YAMLError) as exc:
            raise InvalidManifestError(f"{path}: {exc}") from exc
        try:
            return self._manifest(document)
        except (
            InvalidManifestError,
            YamlShapeError,
            UnknownRegistrationError,
            InvalidRegistrationError,
        ) as exc:
            raise InvalidManifestError(f"{path}: {exc}") from exc

    @staticmethod
    def _parts(folder: Path) -> list[Path]:
        """The `*.yaml` / `*.yml` files under `folder`, in sorted path order."""
        return sorted(p for pattern in _PATTERNS for p in folder.rglob(pattern) if p.is_file())

    def _load_folder(self, folder: Path) -> Manifest:
        parts = self._parts(folder)
        merged: dict[str, object] = {}
        scalar_owners: dict[str, Path] = {}
        lists: dict[str, list[object]] = {}
        form_selections: dict[str, list[CapabilitySelection]] = {}
        declarations: dict[str, tuple[Path, _Declaration]] = {}
        identifier_owners: dict[str, dict[str, Path]] = {key: {} for key in _IDENTIFIER_LISTS}
        for part in parts:
            contents = self._part(part)
            if "form" in contents:
                self._join_form(part, contents, form_selections, declarations)
            for key, node in contents.items():
                if key in _SCALAR_KEYS:
                    if key in scalar_owners:
                        raise InvalidManifestError(
                            f"{part}: key {key!r} is already set in {scalar_owners[key]}"
                        )
                    scalar_owners[key] = part
                    merged[key] = node.value
                else:
                    self._claim_identifiers(key, node, part, identifier_owners.get(key, {}))
                    lists.setdefault(key, []).extend(item.value for item in node.items())
        if form_selections:
            lists.setdefault("capabilities", [])  # the default form may have none beside the others
        try:
            return self._manifest(
                YamlNode.root({**merged, **lists}, "manifest"),
                lambda default: tuple(
                    self._form(name, selections, declarations, default)
                    for name, selections in form_selections.items()
                ),
            )
        except (
            InvalidManifestError,
            YamlShapeError,
            UnknownRegistrationError,
            InvalidRegistrationError,
        ) as exc:
            raise InvalidManifestError(f"{folder}: {exc}") from exc

    def _join_form(
        self,
        part: Path,
        contents: dict[str, YamlNode],
        form_selections: dict[str, list[CapabilitySelection]],
        declarations: dict[str, tuple[Path, _Declaration]],
    ) -> None:
        """Give the `capabilities` of a part with a `form:` key to its form, noting its declaration.

        Takes `form` and `capabilities` out of `contents`; a second part declaring the exports of
        a form is rejected, naming the part that did.
        """
        name, declared = self._form_header(contents.pop("form"))
        if contents.keys() & set(_IDENTIFIER_LISTS):
            raise InvalidManifestError(
                f"{part}: form {name!r}: inputs are derived and exports are declared in the "
                "form: block, so the part takes no `inputs` or `outputs`"
            )
        chosen = form_selections.setdefault(name, [])
        if declared is not None:
            if name in declarations:
                raise InvalidManifestError(
                    f"{part}: form {name!r}: exports are already declared in "
                    f"{declarations[name][0]}"
                )
            declarations[name] = (part, declared)
        if "capabilities" in contents:
            chosen.extend(self._selection(entry) for entry in contents.pop("capabilities").items())

    @staticmethod
    def _form(
        name: str,
        selections: list[CapabilitySelection],
        declarations: dict[str, tuple[Path, _Declaration]],
        default: str,
    ) -> Form:
        """The form `name` of the selections of all its parts and its one declaration."""
        if name not in declarations:
            raise InvalidManifestError(f"form {name!r}: no part declares its exports")
        part, declared = declarations[name]
        if name == default:
            raise InvalidManifestError(
                f"{part}: form {name!r}: the name is reserved for the parts without a `form:` key"
            )
        return declared.form(name, tuple(selections))

    def _form_header(self, node: YamlNode) -> tuple[str, _Declaration | None]:
        """The name of a part's form and, if it declares them, its instances, exports and limits."""
        node.require_mapping(_FORM_KEYS, optional=_OPTIONAL_FORM_KEYS)
        name = node.field("name").require_non_empty_string()
        Form.check_identifier("name", name)
        instances = node.optional_field("instances")
        exports = node.optional_field("exports")
        maximum = node.optional_field("max_instances")
        minimum = node.optional_field("min_instances")
        group = node.optional_field("exclusive_group")
        required = node.optional_field("required")
        required_when = node.optional_field("required_when")
        basis = node.optional_field("basis")
        fields = node.optional_field("fields")
        title = node.optional_field("title")
        if exports is None:
            if instances is not None:
                raise InvalidManifestError(
                    f"form {name!r}: instances must be declared with exports"
                )
            for key, limit in (
                ("max_instances", maximum),
                ("min_instances", minimum),
                ("exclusive_group", group),
                ("required", required),
                ("required_when", required_when),
                ("basis", basis),
                ("fields", fields),
                ("title", title),
            ):
                if limit is not None:
                    raise InvalidManifestError(
                        f"form {name!r}: {key} belongs to the part that declares exports"
                    )
            return name, None
        if required is None:
            raise InvalidManifestError(f"form {name!r}: required must be declared true or false")
        self._identifiers(exports)
        instances_name = None if instances is None else instances.require_non_empty_string()
        declared = _Declaration(
            instances=instances_name,
            exports=tuple(item.require_string() for item in exports.items()),
            max_instances=None if maximum is None else maximum.require_integer(),
            min_instances=None if minimum is None else minimum.require_integer(),
            exclusive_group=None if group is None else group.require_non_empty_string(),
            required=required.require_boolean(),
            required_when=None
            if required_when is None
            else required_when.require_non_empty_string(),
            basis=None if basis is None else basis.require_non_empty_string(),
            title=None if title is None else self._title(title),
            fields=()
            if fields is None
            else self._declarations(
                fields,
                lambda field: self._field_kind(name, instances_name, field),
            ),
        )
        # Built to check the declaration; the form's selections are added when the parts merge.
        declared.form(name, ())
        return name, declared

    @staticmethod
    def _title(node: YamlNode) -> str:
        """The readable title `node` holds: text with something to read in it."""
        text = node.require_non_empty_string()
        if not text.strip():
            raise InvalidManifestError(f"{node.where} must not be blank")
        return text

    def _part(self, part: Path) -> dict[str, YamlNode]:
        """The keys a part carries, each checked on its own; errors name the part."""
        try:
            doc = YamlNode.load(part, "manifest").require_mapping(frozenset(), optional=_PART_KEYS)
            contents = dict(doc.fields())
            if "form" in contents:
                self._form_header(contents["form"])
            if "jurisdiction" in contents:
                self._code(contents["jurisdiction"])
            for key in ("version", "valid_from_tax_year"):
                if key in contents:
                    contents[key].require_integer()
            if "title" in contents:
                self._title(contents["title"])
            if "inputs" in contents:
                self._declarations(contents["inputs"], self._input_kind)
            if "outputs" in contents:
                self._identifiers(contents["outputs"])
            if "capabilities" in contents:
                for entry in contents["capabilities"].items():
                    self._selection(entry)
        except (OSError, yaml.YAMLError, InvalidManifestError, YamlShapeError) as exc:
            raise InvalidManifestError(f"{part}: {exc}") from exc
        return contents

    @staticmethod
    def _claim_identifiers(key: str, node: YamlNode, part: Path, owners: dict[str, Path]) -> None:
        """Record the part's identifiers under `key`, refusing one an earlier part listed."""
        if key not in _IDENTIFIER_LISTS:
            return
        for index, item in enumerate(node.items()):
            identifier = (
                item.field("name").require_string() if key == "inputs" else item.require_string()
            )
            if identifier in owners:
                raise InvalidManifestError(
                    f"{part}: {key}[{index}]: {identifier!r} is already listed in "
                    f"{owners[identifier]}"
                )
            owners[identifier] = part

    def _manifest(
        self,
        document: YamlNode,
        forms_beside: Callable[[str], tuple[Form, ...]] = lambda _: (),
    ) -> Manifest:
        """The manifest of `document`, whose selections and `outputs` are the default form's.

        `forms_beside` gives the other forms, from the name the default form takes.
        """
        doc = document.require_mapping(_MANIFEST_KEYS, optional=_OPTIONAL_MANIFEST_KEYS)
        title = doc.optional_field("title")
        code = self._code(doc.field("jurisdiction"))
        inputs = self._declarations(doc.field("inputs"), self._input_kind)
        outputs = self._identifiers(doc.field("outputs"))
        if not outputs:
            raise InvalidManifestError("outputs must name at least one artifact")
        Form.check_exports("outputs", sorted(outputs))
        default = code.namespace.identifier(_DEFAULT_FORM)
        return Manifest(
            jurisdiction=code,
            version=doc.field("version").require_integer(),
            valid_from_tax_year=doc.field("valid_from_tax_year").require_integer(),
            inputs={declaration.name: declaration for declaration in inputs},
            artifacts=self._kinds,
            forms=(
                Form(
                    name=default,
                    instances=None,
                    exports=tuple(sorted(outputs)),
                    capabilities=tuple(
                        self._selection(entry) for entry in doc.field("capabilities").items()
                    ),
                    required=True,
                    title=None if title is None else self._title(title),
                ),
                *forms_beside(default),
            ),
        )

    @staticmethod
    def _identifiers(node: YamlNode) -> frozenset[str]:
        """A list of non-empty identifiers, none repeated; an empty list is Manifest's check."""
        identifiers: set[str] = set()
        for item in node.items():
            identifier = item.require_string()
            if not identifier:
                raise YamlShapeError(f"{item.where} must not be empty")
            if identifier in identifiers:
                raise YamlShapeError(f"{item.where}: {identifier!r} is listed more than once")
            identifiers.add(identifier)
        return frozenset(identifiers)

    def _declarations(
        self, node: YamlNode, kind_of: Callable[[str], ArtifactKind[Any]]
    ) -> tuple[InputDeclaration, ...]:
        """A list of input declarations, none repeated; an empty list is Manifest's check.

        `kind_of` gives the kind a declared name stands for, which reads its default.
        """
        declarations = tuple(self._declaration(entry, kind_of) for entry in node.items())
        names: set[str] = set()
        for entry, declaration in zip(node.items(), declarations, strict=True):
            if declaration.name in names:
                raise YamlShapeError(
                    f"{entry.where}: {declaration.name!r} is listed more than once"
                )
            names.add(declaration.name)
        return declarations

    def _declaration(
        self, entry: YamlNode, kind_of: Callable[[str], ArtifactKind[Any]]
    ) -> InputDeclaration:
        """One input or field: its `name`, whether it is `required`, and for an optional one its
        `default` (written as the value, `null` for blank) and the printed `basis`."""
        fields = entry.require_mapping(
            frozenset({"name"}), optional=_OPTIONAL_INPUT_KEYS | {"required"}
        )
        name = fields.field("name").require_non_empty_string()
        required = fields.optional_field("required")
        if required is None:
            raise InvalidManifestError(f"input {name!r}: required must be declared true or false")
        default = fields.optional_field("default")
        basis = fields.optional_field("basis")
        return InputDeclaration(
            name=name,
            required=required.require_boolean(),
            default=None if default is None else self._default(name, default, kind_of(name)),
            basis=None if basis is None else basis.require_non_empty_string(),
        )

    @staticmethod
    def _default(name: str, node: YamlNode, kind: ArtifactKind[Any]) -> Artifact[Any]:
        """`null`, a quoted string or an empty list, read as an artifact of `kind`."""
        value = node.value
        declared: str | tuple[()] | None
        if value is None or isinstance(value, str):
            declared = value
        elif isinstance(value, list) and not value:
            declared = ()
        else:
            raise YamlShapeError(
                f"{node.where} must be null, a quoted string or [], got {type(value).__name__}"
            )
        try:
            return read_default(kind, declared)
        except DomainError as exc:
            raise InvalidManifestError(
                f"input {name!r}: default {declared!r} {exc} for the kind {kind.identifier!r}"
            ) from None

    def _input_kind(self, name: str) -> ArtifactKind[Any]:
        """The kind of the input `name`, an artifact the source's kinds register."""
        try:
            return self._kinds.kind(name)
        except UnknownRegistrationError as exc:
            raise InvalidManifestError(f"input {name!r}: {exc}") from None

    def _field_kind(self, form: str, instances: str | None, name: str) -> ArtifactKind[Any]:
        """The kind of the field `name` of the records of form `form`'s `instances`."""
        if instances is None:
            raise InvalidManifestError(f"form {form!r}: field {name!r} needs the form's instances")
        try:
            kind = self._kinds.kind(instances)
        except UnknownRegistrationError as exc:
            raise InvalidManifestError(f"form {form!r}: {exc}") from None
        found = (
            {field.identifier: field for field in kind.fields}
            if isinstance(kind, RecordListKind)
            else {}
        )
        if name not in found:
            raise InvalidManifestError(
                f"form {form!r}: field {name!r} is not a field of the records of {instances!r}"
            )
        return found[name]

    def _selection(self, entry: YamlNode) -> CapabilitySelection:
        fields = entry.require_mapping(_CAPABILITY_KEYS, optional=_OPTIONAL_CAPABILITY_KEYS)
        name = fields.field("name").require_string()
        consumes = self._consumed(fields.optional_field("consumes"))
        blank = fields.optional_field("blank")
        title = fields.optional_field("title")
        reference = fields.optional_field("reference")
        return CapabilitySelection(
            name=name,
            params=self._bindings(fields.optional_field("params")),
            consumes=consumes,
            produces=self._produced(fields.field("produces")),
            blank=self._blank_rules(name, blank, consumes),
            blank_fields=self._field_blank_rules(name, blank, consumes),
            title=None if title is None else self._title(title),
            reference=None if reference is None else self._title(reference),
        )

    def _blank_rules(
        self,
        who: str,
        node: YamlNode | None,
        consumes: Mapping[str, str | tuple[str, ...]],
    ) -> dict[str, BlankRule]:
        """What a blank does in each slot, or each artifact in a list slot, `node` names: `pass_on`
        and `compute` are the rules `PASS_ON` and `COMPUTE`, anything else a fallback number read
        as the value type of the kinds the slot (or the one artifact) takes.
        """
        return {
            name: self._blank_rule(who, name, value.require_non_empty_string(), consumes)
            for name, value in ([] if node is None else node.fields())
            if not value.is_mapping()
        }

    def _field_blank_rules(
        self,
        who: str,
        node: YamlNode | None,
        consumes: Mapping[str, str | tuple[str, ...]],
    ) -> dict[str, dict[str, BlankRule]]:
        """What a blank does in each record field `node` names under a slot (a mapping of field
        identifier to rule): `pass_on` and `compute` are the rules `PASS_ON` and `COMPUTE`,
        anything else a fallback number read as the value type of the field's kind.
        """
        rules: dict[str, dict[str, BlankRule]] = {}
        for slot, value in [] if node is None else node.fields():
            if not value.is_mapping():
                continue
            if slot not in consumes:
                raise InvalidManifestError(
                    f"{who}: {slot!r} is given under blank with field rules but is not a "
                    "consumed slot of the selection"
                )
            rules[slot] = {
                field: self._field_blank_rule(who, field, text)
                for field, text in value.string_mapping().items()
            }
        return rules

    def _field_blank_rule(self, who: str, field: str, text: str) -> BlankRule:
        """The rule `text` spells for the record field `field`; a fallback that is not a number of
        the field's value type is an InvalidManifestError.
        """
        keyword = self._keyword_rule(text)
        if keyword is not None:
            return keyword
        try:
            return read_number(self._kinds.kind(field).value_type, text)
        except UnknownRegistrationError as exc:
            raise InvalidManifestError(f"{who}: blank rule for field {field!r}: {exc}") from None
        except InvalidTextError as exc:
            raise InvalidManifestError(
                f"{who}: blank rule for field {field!r} must be pass_on, compute or a number, "
                f"got {text!r}, which {exc}"
            ) from None

    @staticmethod
    def _keyword_rule(text: str) -> BlankRule | None:
        """`PASS_ON` or `COMPUTE` if `text` is that keyword, else None: it is a fallback."""
        if text == "pass_on":
            return PASS_ON
        if text == "compute":
            return COMPUTE
        return None

    def _blank_rule(
        self,
        who: str,
        name: str,
        text: str,
        consumes: Mapping[str, str | tuple[str, ...]],
    ) -> BlankRule:
        """The rule `text` spells for `name`, a consumed slot or an artifact the selection
        consumes; a fallback that is not a number of that value type is an InvalidManifestError.
        """
        keyword = self._keyword_rule(text)
        if keyword is not None:
            return keyword
        label = f"slot {name!r}" if name in consumes else repr(name)
        named = consumes.get(name, name)
        identifiers = (named,) if isinstance(named, str) else named
        listed = {
            each
            for value in consumes.values()
            for each in ((value,) if isinstance(value, str) else value)
        }
        if name not in consumes and name not in listed:
            raise InvalidManifestError(
                f"{who}: {name!r} is given under blank but is neither a consumed slot "
                "nor an artifact the selection consumes"
            )
        if not identifiers:
            raise InvalidManifestError(
                f"{who}: blank rule for {label} must be pass_on or compute: it takes no kinds"
            )
        try:
            value_types = {self._kinds.kind(each).value_type for each in identifiers}
            if len(value_types) != 1:
                raise InvalidManifestError(
                    f"{who}: blank rule for {label} must be pass_on or compute: "
                    "the kinds it takes are not of one value type"
                )
            return read_number(value_types.pop(), text)
        except UnknownRegistrationError as exc:
            raise InvalidManifestError(f"{who}: blank rule for {label}: {exc}") from None
        except InvalidTextError as exc:
            raise InvalidManifestError(
                f"{who}: blank rule for {label} must be pass_on, compute or a number, "
                f"got {text!r}, which {exc}"
            ) from None

    @classmethod
    def _produced(cls, node: YamlNode) -> dict[str, str]:
        bindings = cls._bindings(node)
        if not bindings:
            raise YamlShapeError(f"{node.where} must name at least one slot")
        return bindings

    @staticmethod
    def _bindings(node: YamlNode | None) -> dict[str, str]:
        return {} if node is None else node.string_mapping()

    @classmethod
    def _consumed(cls, node: YamlNode | None) -> dict[str, str | tuple[str, ...]]:
        """Consumed slots, each bound to one identifier or to a list of them, in order."""
        if node is None:
            return {}
        return {slot: cls._identifier_or_list(value) for slot, value in node.fields()}

    @staticmethod
    def _identifier_or_list(node: YamlNode) -> str | tuple[str, ...]:
        """A non-empty identifier, or a list of them as a tuple; repeats are the builder's check."""
        if node.is_list():
            return tuple(item.require_non_empty_string() for item in node.items())
        if not isinstance(node.value, str):
            raise YamlShapeError(
                f"{node.where} must be a string or a list of strings, "
                f"got {type(node.value).__name__}"
            )
        return node.require_non_empty_string()

    @staticmethod
    def _code(node: YamlNode) -> JurisdictionCode:
        try:
            return JurisdictionCode(node.require_string())
        except InvalidJurisdictionCodeError as exc:
            raise InvalidManifestError(f"{node.where}: {exc}") from exc
