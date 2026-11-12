"""Forms: peers that run once per instance and read each other's exports.

See docs/forms.md for instances, limits and the derived `<form>.<export>` kinds.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from types import MappingProxyType
from typing import Any

from tax_engine.domain.artifact import Artifact, ArtifactKind, ArtifactRegistry
from tax_engine.domain.blank import BLANK
from tax_engine.domain.capability import Capability
from tax_engine.domain.composition import Composition
from tax_engine.domain.errors import (
    BlankNotAllowedError,
    DomainError,
    DuplicateArtifactError,
    InvalidCompositionError,
    NotFoundError,
    ValidationError,
)
from tax_engine.domain.figure_names import ImportedFigure
from tax_engine.domain.kinds import RecordListKind
from tax_engine.domain.manifest import Form, InputDeclaration
from tax_engine.domain.record_list import Record, RecordList
from tax_engine.domain.trace import FormInstanceLine, TraceLine
from tax_engine.domain.unit import Unit
from tax_engine.domain.worksheet import Worksheet


class FormComposition:
    """One form wired: the capabilities of form `name` as an inner `Composition`.

    Its inputs are the `starting` kinds the capabilities consume or export, the fields of
    `instances` (a record-list kind, else InvalidCompositionError), and its imports. A form reading
    its own `<form>.<export>` gets the record list over the runs before it (empty in the first). A
    field of `instances` that is also in `starting` is an InvalidCompositionError. Rule breaches
    name the form (`form 'x': ...`). Exports of an amount, count or record-list kind are readable as
    `<form>.<export>`; others only on the form's worksheets.
    """

    def __init__(
        self,
        form: Form,
        capabilities: Iterable[Capability],
        *,
        kinds: ArtifactRegistry,
        starting: frozenset[ArtifactKind[Any]] = frozenset(),
        defaults: Iterable[Artifact[Any]] = (),
        field_defaults: Iterable[Artifact[Any]] = (),
        declared: Iterable[InputDeclaration] = (),
        units: Mapping[str, Unit] | None = None,
    ) -> None:
        """Wire `capabilities` as `form`, whose names `kinds` resolves to artifact kinds.

        `defaults` are what a starting artifact is read as when left out, and `field_defaults` the
        same for an `instances` field left blank; an input or field whose default is blank may
        arrive blank, and any other blank is refused. `declared` gives the `title` and `reference`
        of the inputs and fields this form reads. `units` holds the units the manifest names, by
        name, which is every name `declared`, a field or a selection uses.
        """
        name = form.name
        instances = None if form.instances is None else kinds.kind(form.instances)
        if instances is not None and not isinstance(instances, RecordListKind):
            raise InvalidCompositionError(
                f"form {name!r}: instances {instances.identifier!r} is not a record list"
            )
        listed = tuple(kinds.kind(identifier) for identifier in form.exports)
        wired = tuple(capabilities)
        produced = {kind for capability in wired for kind in capability.produces}
        read = {kind for capability in wired for kind in capability.consumes} | set(listed)
        self._form = form
        by_name = {} if instances is None else {kind.identifier: kind for kind in instances.fields}
        # A field the form's `instances` does not have is the manifest's own check to refuse; here
        # it is skipped. A title and a reference are only for the input kinds the form reads.
        printed = [(kinds.kind(d.name), d) for d in declared if kinds.kind(d.name) in read] + [
            (by_name[d.name], d) for d in form.fields if d.name in by_name
        ]
        produced_by = [
            (kinds.kind(next(iter(selection.produces.values()))), selection)
            for selection in form.capabilities
        ]
        # A kind that is an input is never also produced (the composition refuses it), so an
        # input's entry and a step's never share a kind.
        self._figure_titles = {
            kind.label: found.title for kind, found in printed if found.title is not None
        } | {kind.label: found.title for kind, found in produced_by if found.title is not None}
        self._figure_references = {
            kind.label: found.reference for kind, found in printed if found.reference is not None
        } | {
            kind.label: found.reference
            for kind, found in produced_by
            if found.reference is not None
        }
        known = {} if units is None else units
        self._unit_claims = tuple(
            (kind, how, None if found.unit is None else known[found.unit])
            for how, claims in (("read", printed), ("produced", produced_by))
            for kind, found in claims
        )
        self._figure_units = {
            kind.label: unit for kind, _, unit in self._unit_claims if unit is not None
        }
        self._instances = instances
        self._exports = listed
        self._derived = form.derived_kinds(kinds)
        foreign = frozenset(kind for kind in read - produced if kind.is_form_export)
        self._earlier = frozenset(kind for kind in self._derived if kind in foreign)
        self._imports = foreign - self._earlier
        fields = frozenset(instances.fields) if instances is not None else frozenset()
        clash = fields & starting
        if clash:
            kind = min(clash, key=Composition.sort_key)
            raise InvalidCompositionError(
                f"form {name!r}: instance field {kind.label!r} is also a starting artifact"
            )
        self._inputs = fields | frozenset(read & starting)
        self._field_defaults = {artifact.kind: artifact for artifact in field_defaults}
        self._blank_inputs = (
            self._blank_kinds(defaults, self._field_defaults.values()) & self._inputs
        )
        stray = self._field_defaults.keys() - fields
        if stray:
            kind = min(stray, key=Composition.sort_key)
            raise InvalidCompositionError(
                f"form {name!r}: default for {kind.label!r}, which is not a field of its instances"
            )
        try:
            self._composition = Composition(
                wired,
                inputs=self._inputs | self._imports | self._earlier,
                outputs=frozenset(listed),
                blank_inputs=self._blank_inputs,
            )
        except InvalidCompositionError as exc:
            raise InvalidCompositionError(f"form {name!r}: {exc}") from exc

    @staticmethod
    def _blank_kinds(*defaults: Iterable[Artifact[Any]]) -> frozenset[ArtifactKind[Any]]:
        """The kinds whose default is blank: those may arrive blank."""
        return frozenset(a.kind for group in defaults for a in group if a.is_blank)

    @property
    def title(self) -> str | None:
        """The readable title of the form, as its manifest gives it; `None` for none."""
        return self._form.title

    @property
    def figure_titles(self) -> Mapping[str, str]:
        """The readable title of each titled figure of the form, by the figure's label."""
        return MappingProxyType(self._figure_titles)

    @property
    def figure_references(self) -> Mapping[str, str]:
        """What the form prints beside each figure it prints, by the figure's label."""
        return MappingProxyType(self._figure_references)

    @property
    def figure_units(self) -> Mapping[str, Unit]:
        """The unit of each figure of the form that has one, by the figure's label."""
        return MappingProxyType(self._figure_units)

    @property
    def unit_claims(self) -> tuple[tuple[ArtifactKind[Any], str, Unit | None], ...]:
        """The unit this form gives each figure it prints, as `(kind, "read" or "produced", unit)`;
        `None` for a figure it gives none.
        """
        return self._unit_claims

    @property
    def name(self) -> str:
        """The form's name, `<namespace>/<snake_case>`."""
        return self._form.name

    @property
    def instances(self) -> RecordListKind | None:
        """The record-list kind with a record per instance; `None` without an instances list."""
        return self._instances

    @property
    def max_instances(self) -> int | None:
        """The most instances the caller may give; `None` for no maximum."""
        return self._form.max_instances

    @property
    def min_instances(self) -> int | None:
        """The fewest instances the caller may give; `None` for no minimum."""
        return self._form.min_instances

    @property
    def exclusive_group(self) -> str | None:
        """The group of which at most one form may have instances; `None` for no group."""
        return self._form.exclusive_group

    @property
    def exports(self) -> tuple[ArtifactKind[Any], ...]:
        """The kinds the form exports, in order."""
        return self._exports

    @property
    def derived(self) -> tuple[RecordListKind, ...]:
        """The kind `<form>.<export>` of each export a record can hold, in export order."""
        return self._derived

    @property
    def inputs(self) -> frozenset[ArtifactKind[Any]]:
        """The kinds the form starts from, imports aside: starting artifacts it reads and fields."""
        return self._inputs

    @property
    def imports(self) -> frozenset[ArtifactKind[Any]]:
        """The kinds of other forms' exports that this form reads."""
        return self._imports

    @property
    def earlier(self) -> frozenset[RecordListKind]:
        """The form's own derived kinds that it reads; a run gets the earlier runs' values."""
        return self._earlier

    @property
    def field_defaults(self) -> Mapping[ArtifactKind[Any], Artifact[Any]]:
        """The artifact each field is read as when a record leaves it blank, by field kind."""
        return self._field_defaults

    @property
    def blank_inputs(self) -> frozenset[ArtifactKind[Any]]:
        """The starting kinds this form's composition may take blank."""
        return self._blank_inputs

    @property
    def composition(self) -> Composition:
        """The inner composition, computed once per instance (one without an instances list)."""
        return self._composition


class FormSet:
    """The forms of a computation, run in the order of their imports.

    Construction raises InvalidCompositionError naming the forms for a duplicate form, an instances
    kind not among `inputs`, an input that is a form's derived `<form>.<export>` kind, an invalid
    exclusive group, an unexported import, an import cycle, or an input no form reads. A form's read
    of its own derived export is not a cycle.
    """

    def __init__(
        self,
        forms: Iterable[FormComposition],
        *,
        inputs: frozenset[ArtifactKind[Any]],
        defaults: Iterable[Artifact[Any]] = (),
    ) -> None:
        """Wire `forms` into a computation that starts from the artifacts of the kinds `inputs`.

        `defaults` are what an input left out, or blank where the default is a value, is read as;
        each is of one of the `inputs`, once.
        """
        listed = tuple(forms)
        self._check_names(listed)
        self._check_instances(listed, inputs)
        self._check_groups(listed)
        self._producers: dict[ArtifactKind[Any], str] = {
            kind: form.name for form in listed for kind in form.derived
        }
        self._check_not_derived(inputs)
        self._check_imports(listed)
        self._check_units(listed)
        self._check_inputs_are_read(listed, inputs)
        self._defaults = self._index_defaults(defaults, inputs)
        self._inputs = inputs
        self._forms = self._order(listed)

    @property
    def forms(self) -> tuple[FormComposition, ...]:
        """The forms in the order they run."""
        return self._forms

    def form(self, name: str) -> FormComposition:
        """The form `name`, else a NotFoundError."""
        for form in self._forms:
            if form.name == name:
                return form
        raise NotFoundError(f"no form {name!r}")

    def compute(self, *artifacts: Artifact[Any]) -> dict[str, tuple[Worksheet, ...]]:
        """Run every form on `artifacts`: one of each input kind, instances kinds among them.

        Each form runs once per record of its instances, in `forms` order. The result maps each
        form's name to its worksheets in instance order (none if its instances list is empty). A
        DomainError from a run is raised with `<form>, instance N: ` (N from 1) before its message.
        Two values for one kind are a DuplicateArtifactError; a kind that is a form's export is an
        InvalidCompositionError. A breach of the instance limits is a ValidationError naming the
        form or group, before any form runs. A worksheet traces each starting input it read as its
        default; field defaults are not traced.
        """
        kinds = [artifact.kind for artifact in artifacts]
        counts = Counter(kinds)
        for kind in kinds:
            if counts[kind] > 1:
                raise DuplicateArtifactError(f"two starting values for {kind.label!r}")
        given = {artifact.kind: artifact for artifact in artifacts}
        defaulted: set[ArtifactKind[Any]] = set()
        for kind, default in self._defaults.items():
            # Left out, or given blank where the default is a value: the default is what is read.
            was = given.get(kind)
            if was is None or (was.is_blank and not default.is_blank):
                defaulted.add(kind)
            given[kind] = self._read_as(was, default)
        self._check_given(given)
        self._check_limits(given)
        store: dict[ArtifactKind[Any], Artifact[Any]] = {}
        worksheets: dict[str, tuple[Worksheet, ...]] = {}
        for form in self._forms:
            ran = tuple(self._runs(form, given, store, frozenset(defaulted)))
            worksheets[form.name] = ran
            for derived in form.derived:
                store[derived] = self._export_of(derived, ran)
        return worksheets

    def trace(self, worksheets: Mapping[str, Sequence[Worksheet]]) -> tuple[TraceLine, ...]:
        """A `FormInstanceLine` per worksheet of `worksheets` that has trace lines, in the order the
        forms run.

        The position counts every worksheet from 1; a form with no steps has no line.
        """
        return tuple(
            FormInstanceLine(form.name, position, worksheet.trace, worksheet)
            for form in self._forms
            for position, worksheet in enumerate(worksheets.get(form.name, ()), start=1)
            if worksheet.trace
        )

    def _runs(
        self,
        form: FormComposition,
        given: Mapping[ArtifactKind[Any], Artifact[Any]],
        store: Mapping[ArtifactKind[Any], Artifact[Any]],
        defaulted: frozenset[ArtifactKind[Any]],
    ) -> Iterable[Worksheet]:
        imported = [store[kind] for kind in sorted(form.imports, key=Composition.sort_key)]
        instances = form.instances
        fields = () if instances is None else instances.fields
        shared = [
            given[kind]
            for kind in sorted(form.inputs - frozenset(fields), key=Composition.sort_key)
        ]
        done: list[Worksheet] = []
        if instances is None:
            yield self._run(
                form, 1, [*shared, *imported, *self._earlier_runs(form, done)], defaulted
            )
            return
        for position, record in enumerate(given[instances].value.records, start=1):
            starting = [self._field(form, record, kind) for kind in fields]
            earlier = self._earlier_runs(form, done)
            worksheet = self._run(
                form, position, [*shared, *starting, *imported, *earlier], defaulted
            )
            done.append(worksheet)
            yield worksheet

    @staticmethod
    def _field(form: FormComposition, record: Record, kind: ArtifactKind[Any]) -> Artifact[Any]:
        """The field `kind` of `record` as a starting artifact: blank, or the form's default for
        it if the default is a value, when the record leaves it blank."""
        given = Artifact(kind, BLANK if record.is_blank(kind) else record[kind])
        return FormSet._read_as(given, form.field_defaults.get(kind))

    @staticmethod
    def _read_as(given: Artifact[Any] | None, default: Artifact[Any] | None) -> Artifact[Any]:
        """What is read for an input or field: the default when it is left out, or given blank
        where the default is a value; else what was given."""
        if given is not None and not (
            given.is_blank and default is not None and not default.is_blank
        ):
            return given
        assert default is not None  # nothing given and no default: callers only pass one of them
        return default

    @staticmethod
    def _earlier_runs(form: FormComposition, done: Sequence[Worksheet]) -> list[Artifact[Any]]:
        """The form's own derived kinds it reads, over the runs before this one."""
        earlier: list[Artifact[Any]] = []
        for derived in sorted(form.earlier, key=Composition.sort_key):
            earlier.append(FormSet._export_of(derived, done))
        return earlier

    @staticmethod
    def _export_of(derived: RecordListKind, ran: Sequence[Worksheet]) -> Artifact[Any]:
        """The derived kind as a record list of its export over the worksheets `ran`, in order.

        A blank export is a blank field of its record, and the step that reads it decides.
        """
        (export,) = derived.fields
        listed: list[dict[ArtifactKind[Any], object]] = []
        for worksheet in ran:
            made = worksheet.get(export)
            listed.append({export: BLANK if made.is_blank else made.value})
        return Artifact(derived, RecordList(derived.fields, listed))

    def _imported_figures(self, form: FormComposition) -> dict[str, ImportedFigure]:
        """Each figure `form` imports, by label, as the form that exports it prints it."""
        found: dict[str, ImportedFigure] = {}
        for kind in form.imports:
            exporter = self.form(self._producers[kind])
            assert isinstance(kind, RecordListKind)  # a form export is read as a record list
            (export,) = kind.fields
            found[export.label] = ImportedFigure(
                exporter.title,
                exporter.figure_titles.get(export.label),
                exporter.figure_references.get(export.label),
                exporter.instances is None,
                exporter.figure_units.get(export.label),
            )
        return found

    def _run(
        self,
        form: FormComposition,
        position: int,
        starting: list[Artifact[Any]],
        defaulted: frozenset[ArtifactKind[Any]],
    ) -> Worksheet:
        try:
            return form.composition.compute(
                *starting,
                form_title=form.title,
                figure_titles=form.figure_titles,
                figure_references=form.figure_references,
                figure_units=form.figure_units,
                imported_figures=self._imported_figures(form),
                defaulted=defaulted,
            )
        except DomainError as exc:
            exc.args = (f"{form.name}, instance {position}: {exc}",)
            raise

    def _check_given(self, given: Mapping[ArtifactKind[Any], Artifact[Any]]) -> None:
        self._check_not_derived(given.keys())
        Composition.check_starting_kinds(given.keys(), self._inputs)
        # The form set itself reads each instances list, so it cannot take a blank one; any other
        # blank goes on to the composition of each form that reads it, which checks its own.
        listed = {form.instances for form in self._forms if form.instances is not None}
        blank = [kind for kind in sorted(listed, key=Composition.sort_key) if given[kind].is_blank]
        if blank:
            raise BlankNotAllowedError(
                f"{ArtifactKind.labels(blank)} may not be left blank: "
                "the forms need its list of instances"
            )
        # A form with no instances never runs, so its composition cannot refuse a blank; no form
        # taking a blank input is a refusal here.
        accepted = {kind for form in self._forms for kind in form.blank_inputs}
        refused = [
            kind for kind, artifact in given.items() if artifact.is_blank and kind not in accepted
        ]
        if refused:
            raise BlankNotAllowedError(
                f"{ArtifactKind.labels(refused)} may not be left blank in this computation"
            )

    @staticmethod
    def _index_defaults(
        defaults: Iterable[Artifact[Any]], inputs: frozenset[ArtifactKind[Any]]
    ) -> dict[ArtifactKind[Any], Artifact[Any]]:
        found: dict[ArtifactKind[Any], Artifact[Any]] = {}
        for artifact in defaults:
            if artifact.kind not in inputs:
                raise InvalidCompositionError(
                    f"default for {artifact.kind.label!r}, which is not an input of the computation"
                )
            if artifact.kind in found:
                raise InvalidCompositionError(f"two defaults for {artifact.kind.label!r}")
            found[artifact.kind] = artifact
        return found

    @staticmethod
    def _check_units(forms: Sequence[FormComposition]) -> None:
        """Refuse a figure that two forms give different units: its producer and its readers, or
        readers among themselves; a figure with a unit in one form and none in another differs."""
        seen: dict[ArtifactKind[Any], tuple[str, Unit | None, str]] = {}
        for form in forms:
            for kind, how, unit in form.unit_claims:
                first = seen.setdefault(kind, (form.name, unit, how))
                if first[1] != unit:
                    raise InvalidCompositionError(
                        f"figure {kind.label!r} is {first[2]} in {FormSet._in(first[1])} by "
                        f"{first[0]!r} but {how} in {FormSet._in(unit)} by {form.name!r}"
                    )

    @staticmethod
    def _in(unit: Unit | None) -> str:
        return "no unit" if unit is None else repr(unit.name)

    def _check_not_derived(self, kinds: Iterable[ArtifactKind[Any]]) -> None:
        derived = set(kinds) & self._producers.keys()
        if derived:
            verb = "is" if len(derived) == 1 else "are"
            raise InvalidCompositionError(
                f"{ArtifactKind.labels(derived)} {verb} exported by a form, not an input"
            )

    def _check_limits(self, given: Mapping[ArtifactKind[Any], Artifact[Any]]) -> None:
        used: dict[str, str] = {}
        for form in sorted(self._forms, key=lambda each: each.name):
            instances = form.instances
            count = 1 if instances is None else len(given[instances].value.records)
            if form.max_instances is not None and count > form.max_instances:
                raise ValidationError(
                    f"form {form.name!r} allows at most {form.max_instances} instance(s), "
                    f"got {count}"
                )
            if form.min_instances is not None and count < form.min_instances:
                raise ValidationError(
                    f"form {form.name!r} needs at least {form.min_instances} instance(s), "
                    f"got {count}"
                )
            group = form.exclusive_group
            if group is None or count == 0:
                continue
            if group in used:
                raise ValidationError(
                    f"forms {used[group]!r} and {form.name!r} both have instances, "
                    f"but are in exclusive group {group!r}"
                )
            used[group] = form.name

    @staticmethod
    def _check_groups(forms: tuple[FormComposition, ...]) -> None:
        members: dict[str, list[str]] = {}
        for form in forms:
            if form.exclusive_group is not None:
                members.setdefault(form.exclusive_group, []).append(form.name)
        for group, names in members.items():
            if len(names) == 1:
                raise InvalidCompositionError(
                    f"exclusive group {group!r} names only form {names[0]!r}"
                )
            always = [
                form.name
                for form in forms
                if form.exclusive_group == group
                and (form.instances is None or (form.min_instances or 0) >= 1)
            ]
            if len(always) > 1:
                listed = " and ".join(repr(each) for each in always)
                raise InvalidCompositionError(
                    f"exclusive group {group!r}: forms {listed} can never hold: "
                    "each always has at least one instance"
                )

    @staticmethod
    def _check_names(forms: tuple[FormComposition, ...]) -> None:
        names = [form.name for form in forms]
        for each in names:
            if names.count(each) > 1:
                raise InvalidCompositionError(f"form {each!r} is listed more than once")

    @staticmethod
    def _check_instances(
        forms: tuple[FormComposition, ...], inputs: frozenset[ArtifactKind[Any]]
    ) -> None:
        for form in forms:
            if form.instances is not None and form.instances not in inputs:
                raise InvalidCompositionError(
                    f"form {form.name!r}: instances {form.instances.identifier!r} "
                    "is not an input of the computation"
                )

    def _check_imports(self, forms: tuple[FormComposition, ...]) -> None:
        for form in forms:
            for kind in sorted(form.imports, key=Composition.sort_key):
                if kind not in self._producers:
                    raise InvalidCompositionError(
                        f"form {form.name!r}: no form exports {kind.label!r}, which it imports"
                    )

    def _check_inputs_are_read(
        self, forms: tuple[FormComposition, ...], inputs: frozenset[ArtifactKind[Any]]
    ) -> None:
        read = {kind for form in forms for kind in form.inputs}
        read |= {form.instances for form in forms if form.instances is not None}
        unread = inputs - read
        if unread:
            kind = min(unread, key=Composition.sort_key)
            raise InvalidCompositionError(f"input {kind.label!r} is consumed by nothing")

    def _order(self, forms: tuple[FormComposition, ...]) -> tuple[FormComposition, ...]:
        """The forms so that each runs after every form it imports from; ties by name."""
        needs = {form.name: {self._producers[kind] for kind in form.imports} for form in forms}
        pending = sorted(forms, key=lambda form: form.name)
        done: set[str] = set()
        order: list[FormComposition] = []
        while pending:
            chosen = next((form for form in pending if needs[form.name] <= done), None)
            if chosen is None:
                cycle = self._on_cycle({form.name: needs[form.name] for form in pending})
                names = ", ".join(repr(each) for each in sorted(cycle))
                raise InvalidCompositionError(f"cycle involving forms {names}")
            pending.remove(chosen)
            order.append(chosen)
            done.add(chosen.name)
        return tuple(order)

    @staticmethod
    def _on_cycle(stuck: Mapping[str, set[str]]) -> set[str]:
        """The stuck forms that import from each other, without those only downstream of them."""
        remaining = set(stuck)
        while True:
            sinks = {
                form for form in remaining if not any(form in stuck[other] for other in remaining)
            }
            if not sinks:
                return remaining
            remaining -= sinks
