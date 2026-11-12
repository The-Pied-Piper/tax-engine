"""Reads jurisdictions from YAML manifest files. Implements JurisdictionSource.

The manifest format is described in docs/manifest-format.md.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable, Iterable, Mapping
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
from tax_engine.domain.unit import Unit, UnitRegistry

_MANIFEST_KEYS = frozenset(
    {"jurisdiction", "version", "valid_from_tax_year", "inputs", "outputs", "capabilities"}
)
_OPTIONAL_MANIFEST_KEYS = frozenset({"title", "imports"})
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
        "supplies",
    }
)
_IMPORTED_PART_KEYS = frozenset({"form", "capabilities", "inputs"})
_OPTIONAL_INPUT_KEYS = frozenset({"default", "basis", "title", "reference", "unit"})
_DEFAULT_FORM = "return"
_CAPABILITY_KEYS = frozenset({"name", "produces"})
_OPTIONAL_CAPABILITY_KEYS = frozenset({"params", "consumes", "blank", "title", "reference", "unit"})
_SCALAR_KEYS = ("jurisdiction", "version", "valid_from_tax_year", "title")
_IDENTIFIER_LISTS = ("inputs", "outputs", "imports")
_PATTERNS = ("*.yaml", "*.yml")


class _ImportEntry(NamedTuple):
    """One `imports` entry: the form and the dataset families it reads in place of its own."""

    name: str
    datasets: Mapping[str, str]


class _LoadedImports(NamedTuple):
    """The forms a manifest imports and the input declarations their parts carry."""

    forms: tuple[Form, ...]
    inputs: tuple[InputDeclaration, ...]


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
    supplies: Mapping[str, str]

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
            supplies=self.supplies,
        )


class YamlJurisdictionSource:
    """Jurisdictions read from the `manifests/` directory of each jurisdiction package."""

    def __init__(
        self,
        roots: Mapping[Namespace, Path],
        kinds: ArtifactRegistry,
        units: UnitRegistry | None = None,
    ) -> None:
        """Read manifests under each namespace's package directory in `roots`.

        Each manifest is built with `kinds`, which reads and checks what it declares, and `units`,
        where the units it names are looked up; with none, a manifest may name no unit.
        """
        self._roots = dict(roots)
        self._kinds = kinds
        self._units = UnitRegistry() if units is None else units

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
            return self._manifest(
                document,
                imported=lambda imports: self._imported(
                    imports, {}, self._input_owners(document, path)
                ),
            )
        except (
            InvalidManifestError,
            YamlShapeError,
            UnknownRegistrationError,
            InvalidRegistrationError,
        ) as exc:
            raise InvalidManifestError(f"{path}: {exc}") from exc

    @staticmethod
    def _input_owners(document: YamlNode, path: Path) -> dict[str, Path]:
        """The inputs a whole-file manifest declares, each owned by the file."""
        return {
            item.field("name").require_string(): path for item in document.field("inputs").items()
        }

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
        form_parts: dict[str, Path] = {}
        for part in parts:
            contents = self._part(part)
            if "form" in contents:
                name = self._join_form(part, contents, form_selections, declarations)
                form_parts.setdefault(name, part)
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
        import_owners = identifier_owners["imports"]
        for name in form_selections.keys() & import_owners.keys():
            raise InvalidManifestError(
                f"{form_parts[name]}: form {name!r} is imported in {import_owners[name]}: "
                "an imported form's parts are in its own package"
            )
        self._check_suppliers(declarations)
        if form_selections:
            lists.setdefault("capabilities", [])  # the default form may have none beside the others
        try:
            return self._manifest(
                YamlNode.root({**merged, **lists}, "manifest"),
                lambda default: tuple(
                    self._form(name, selections, declarations, default)
                    for name, selections in form_selections.items()
                ),
                lambda imports: self._imported(imports, import_owners, identifier_owners["inputs"]),
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
    ) -> str:
        """Give the `capabilities` of a part with a `form:` key to its form, noting its declaration.

        Takes `form` and `capabilities` out of `contents` and gives the form's name; a second part
        declaring the exports of a form is rejected, naming the part that did, and so is a manifest
        `title` beside `form:`.
        """
        name, declared = self._form_header(contents.pop("form"))
        if "title" in contents:
            raise InvalidManifestError(
                f"{part}: form {name!r}: the manifest `title` belongs to the default form; "
                "the form's own title goes in its `form:` block"
            )
        if contents.keys() & {"outputs", "imports"}:
            raise InvalidManifestError(
                f"{part}: form {name!r}: exports are declared in the form: block, so the part "
                "takes no `outputs` or `imports`"
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
        return name

    @staticmethod
    def _check_suppliers(declarations: dict[str, tuple[Path, _Declaration]]) -> None:
        """Refuse a neutral identifier two forms supply, naming the part of the second."""
        owners: dict[str, tuple[str, Path]] = {}
        for name, (part, declared) in declarations.items():
            for neutral in declared.supplies:
                if neutral in owners:
                    other, where = owners[neutral]
                    raise InvalidManifestError(
                        f"{part}: form {name!r}: supplies {neutral!r}, which form {other!r} "
                        f"already supplies in {where}"
                    )
                owners[neutral] = (name, part)

    def _imported(
        self,
        imports: tuple[_ImportEntry, ...],
        owners: Mapping[str, Path],
        input_owners: dict[str, Path],
    ) -> _LoadedImports:
        """The forms `imports` name, in order, each from the parts in its package's `forms/`
        folder, with the inputs those parts declare.

        `owners` gives the part that lists each import, to name in an error. `input_owners` gives
        the part that declares each input of the manifest; the imported parts are added to it, so
        an input declared twice is refused as it is between two parts of a manifest.
        """
        found = [
            self._imported_form(entry.name, owners.get(entry.name), input_owners, entry.datasets)
            for entry in imports
        ]
        return _LoadedImports(
            forms=tuple(form for form, _ in found),
            inputs=tuple(declaration for _, inputs in found for declaration in inputs),
        )

    def _imported_form(
        self,
        identifier: str,
        owner: Path | None,
        input_owners: dict[str, Path],
        datasets: Mapping[str, str],
    ) -> tuple[Form, tuple[InputDeclaration, ...]]:
        """The form `identifier` of the parts in `<package>/forms/<local id>/` and the inputs
        they declare; each part names that form and carries `capabilities` and `inputs`.

        Each family of `datasets` replaces itself in the parameters the form's selections read.
        """
        namespace, _, local_id = identifier.partition("/")
        prefix = "" if owner is None else f"{owner}: "
        root = self._roots.get(Namespace(namespace))
        if root is None:
            raise InvalidManifestError(
                f"{prefix}imports {identifier!r}: no jurisdiction package declares namespace "
                f"{namespace!r}"
            )
        folder = root / "forms" / local_id
        parts = self._parts(folder)
        if not parts:
            raise InvalidManifestError(f"{prefix}imports {identifier!r}: no parts in {folder}")
        selections: dict[str, list[CapabilitySelection]] = {}
        declarations: dict[str, tuple[Path, _Declaration]] = {}
        inputs: list[InputDeclaration] = []
        for part in parts:
            contents = self._part(part)
            self._check_imported_part(part, identifier, contents)
            if "inputs" in contents:
                node = contents.pop("inputs")
                self._claim_identifiers("inputs", node, part, input_owners)
                inputs.extend(self._declarations(node, self._input_kind))
            name = self._join_form(part, contents, selections, declarations)
            if name != identifier:
                raise InvalidManifestError(
                    f"{part}: form {name!r}: a part of the imported form {identifier!r} names "
                    "another form"
                )
        default = Namespace(namespace).identifier(_DEFAULT_FORM)
        chosen = self._rebound(
            selections.get(identifier, []), datasets, f"{prefix}imports {identifier!r}"
        )
        form = self._form(identifier, chosen, declarations, default)
        return form, tuple(inputs)

    @staticmethod
    def _rebound(
        selections: list[CapabilitySelection], datasets: Mapping[str, str], who: str
    ) -> list[CapabilitySelection]:
        """`selections` reading each family of `datasets` as the family it maps to.

        Only `params` change; artifacts keep their names. A family no selection reads is refused.
        """
        if not datasets:
            return selections
        used: set[str] = set()
        chosen: list[CapabilitySelection] = []
        for selection in selections:
            used.update(datasets.keys() & set(selection.params.values()))
            params = {
                slot: datasets.get(family, family) for slot, family in selection.params.items()
            }
            chosen.append(dataclasses.replace(selection, params=params))
        for family in datasets.keys() - used:
            raise InvalidManifestError(f"{who}: dataset {family!r} is read by no part of the form")
        return chosen

    @staticmethod
    def _check_imported_part(part: Path, identifier: str, contents: dict[str, YamlNode]) -> None:
        """Refuse a part of an imported form without a `form:` key or with a manifest key."""
        if "form" not in contents:
            raise InvalidManifestError(
                f"{part}: imported form {identifier!r}: a part needs a `form:` key"
            )
        for key in contents.keys() - _IMPORTED_PART_KEYS:
            raise InvalidManifestError(
                f"{part}: imported form {identifier!r}: key {key!r} belongs to the importing "
                "manifest, not to a part of the form"
            )

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
        supplies = node.optional_field("supplies")
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
                ("supplies", supplies),
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
            supplies={} if supplies is None else supplies.string_mapping(),
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
            if "imports" in contents:
                self._import_list(contents["imports"])
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
            if key == "inputs":
                identifier = item.field("name").require_string()
            elif key == "imports":
                identifier = YamlJurisdictionSource._import_name(item)
            else:
                identifier = item.require_string()
            if identifier in owners:
                raise InvalidManifestError(
                    f"{part}: {key}[{index}]: {identifier!r} is already listed in "
                    f"{owners[identifier]}"
                )
            owners[identifier] = part

    def _import_list(self, node: YamlNode) -> tuple[_ImportEntry, ...]:
        """The entries of an `imports` list, in order, no form repeated.

        An entry is a form identifier, or a mapping of `form` and `datasets`, a non-empty mapping
        from a family the form reads to the family to read instead.
        """
        entries: list[_ImportEntry] = []
        for item in node.items():
            name = self._import_name(item)
            if name in {entry.name for entry in entries}:
                raise YamlShapeError(f"{item.where}: {name!r} is listed more than once")
            Form.check_identifier("import", name)
            entries.append(_ImportEntry(name, self._rebinds(item)))
        return tuple(entries)

    @staticmethod
    def _import_name(item: YamlNode) -> str:
        """The form identifier an `imports` entry names, in either of its shapes."""
        identifier = (
            item.field("form").require_string() if item.is_mapping() else item.require_string()
        )
        if not identifier:
            raise YamlShapeError(f"{item.where} must not be empty")
        return identifier

    @staticmethod
    def _rebinds(item: YamlNode) -> dict[str, str]:
        """The families an `imports` entry has the form read in place of its own."""
        if not item.is_mapping():
            return {}
        item.require_mapping(frozenset({"form"}), optional=frozenset({"datasets"}))
        node = item.optional_field("datasets")
        if node is None:
            return {}
        datasets = node.string_mapping()
        if not datasets:
            raise YamlShapeError(f"{node.where} must name at least one family")
        for source, target in datasets.items():
            Form.check_identifier("dataset", source)
            Form.check_identifier("dataset", target)
        return datasets

    def _manifest(
        self,
        document: YamlNode,
        forms_beside: Callable[[str], tuple[Form, ...]] = lambda _: (),
        imported: Callable[[tuple[_ImportEntry, ...]], _LoadedImports] = lambda _: _LoadedImports(
            (), ()
        ),
    ) -> Manifest:
        """The manifest of `document`, whose selections and `outputs` are the default form's.

        `forms_beside` gives the other forms, from the name the default form takes, and `imported`
        the forms the `imports` name, which run between the two.
        """
        doc = document.require_mapping(_MANIFEST_KEYS, optional=_OPTIONAL_MANIFEST_KEYS)
        code = self._code(doc.field("jurisdiction"))
        inputs = self._declarations(doc.field("inputs"), self._input_kind)
        outputs = self._identifiers(doc.field("outputs"))
        if not outputs:
            raise InvalidManifestError("outputs must name at least one artifact")
        Form.check_exports("outputs", sorted(outputs))
        default = code.namespace.identifier(_DEFAULT_FORM)
        title = doc.optional_field("title")
        imports = doc.optional_field("imports")
        found = _LoadedImports((), ()) if imports is None else imported(self._import_list(imports))
        forms_imported = found.forms
        declared_inputs = {declaration.name: declaration for declaration in inputs}
        declared_inputs.update((declaration.name, declaration) for declaration in found.inputs)
        forms = (
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
            *forms_imported,
            *forms_beside(default),
        )
        manifest = Manifest(
            jurisdiction=code,
            version=doc.field("version").require_integer(),
            valid_from_tax_year=doc.field("valid_from_tax_year").require_integer(),
            inputs=declared_inputs,
            artifacts=self._kinds,
            units_by_name=self._units_named(code, declared_inputs, forms),
            forms=forms,
        )
        self._check_supplied(manifest, forms_imported)
        return manifest

    def _units_named(
        self, code: JurisdictionCode, inputs: Mapping[str, InputDeclaration], forms: Iterable[Form]
    ) -> dict[str, Unit]:
        """Each unit the declarations name, found for the jurisdiction `code`, by name.

        A name that is declared nowhere it looks, or in several places, is an InvalidManifestError.
        """
        declared = [(f"input {name!r}", declaration.unit) for name, declaration in inputs.items()]
        for form in forms:
            declared.extend(
                (f"field {field.name!r} of form {form.name!r}", field.unit) for field in form.fields
            )
            declared.extend((selection.name, selection.unit) for selection in form.capabilities)
        found: dict[str, Unit] = {}
        for who, name in declared:
            if name is None or name in found:
                continue
            try:
                found[name] = self._units.resolve(name, code)
            except (UnknownRegistrationError, InvalidRegistrationError) as exc:
                raise InvalidManifestError(f"{who}: {exc}") from None
        return found

    @staticmethod
    def _check_supplied(manifest: Manifest, imported: tuple[Form, ...]) -> None:
        """Refuse an imported form that reads a derived figure no form of the manifest derives."""
        derived = {
            kind.identifier
            for form in manifest.forms
            for kind in form.derived_kinds(manifest.artifacts)
        }
        for form in imported:
            for selection in form.capabilities:
                for slot in selection.consumes.values():
                    for identifier in (slot,) if isinstance(slot, str) else slot:
                        if "." in identifier and identifier not in derived:
                            raise InvalidManifestError(
                                f"form {form.name!r}: needs {identifier!r}, which no form of "
                                "this manifest supplies"
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
        """One input or field: its `name`, `required`, and for an optional one `default` and
        `basis`.

        `default` is written as the value (`null` for blank); `title`, `reference` and `unit` (the
        name of a unit, resolved when the manifest is built) may also be given.
        """
        fields = entry.require_mapping(
            frozenset({"name"}), optional=_OPTIONAL_INPUT_KEYS | {"required"}
        )
        name = fields.field("name").require_non_empty_string()
        required = fields.optional_field("required")
        if required is None:
            raise InvalidManifestError(f"input {name!r}: required must be declared true or false")
        default = fields.optional_field("default")
        basis = fields.optional_field("basis")
        title = fields.optional_field("title")
        reference = fields.optional_field("reference")
        unit = fields.optional_field("unit")
        return InputDeclaration(
            name=name,
            required=required.require_boolean(),
            default=None if default is None else self._default(name, default, kind_of(name)),
            basis=None if basis is None else basis.require_non_empty_string(),
            title=None if title is None else self._title(title),
            reference=None if reference is None else self._title(reference),
            unit=None if unit is None else unit.require_non_empty_string(),
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
        unit = fields.optional_field("unit")
        return CapabilitySelection(
            name=name,
            params=self._bindings(fields.optional_field("params")),
            consumes=consumes,
            produces=self._produced(fields.field("produces")),
            blank=self._blank_rules(name, blank, consumes),
            blank_fields=self._field_blank_rules(name, blank, consumes),
            title=None if title is None else self._title(title),
            reference=None if reference is None else self._title(reference),
            unit=None if unit is None else unit.require_non_empty_string(),
        )

    def _blank_rules(
        self,
        who: str,
        node: YamlNode | None,
        consumes: Mapping[str, str | tuple[str, ...]],
    ) -> dict[str, BlankRule]:
        """What a blank does in each slot, or each artifact in a list slot, `node` names.

        `pass_on` and `compute` are the rules `PASS_ON` and `COMPUTE`; anything else is a fallback
        number read as the value type of the kinds the slot (or the one artifact) takes.
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
        """What a blank does in each record field `node` names under a slot, as a mapping of field
        identifier to rule.

        `pass_on` and `compute` are the rules `PASS_ON` and `COMPUTE`; anything else is a fallback
        number read as the value type of the field's kind.
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
