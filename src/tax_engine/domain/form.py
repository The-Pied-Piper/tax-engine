"""Forms: peers that run once per instance and read each other's exports.

A computation is a flat set of forms that together are the return; none is special. A form is a
group of capabilities with the artifacts it exports, never a capability itself. A `FormComposition`
is one form wired: an inner `Composition` whose outputs are the form's exports and whose inputs are
derived. The inputs of a form are the starting artifacts it reads, plus the fields of its
`instances` kind (a record-list kind, one record per instance) if it has one; a form without an
`instances` list has exactly one implicit instance. The kinds a form reads that other forms export
are its imports and are inputs too.

For each export `X` of the form `B` the engine derives the kind `B.X`: a record list of one field,
`X`, with a record per instance in instance order (one record for a form without an instances list).
Every form reads any such kind by its identifier; an export nobody reads is fine.

A `FormSet` holds the forms of one computation. It orders them by their imports and runs each
once per instance record (a form without an instances list has one) on its own `Worksheet`. It
keeps every form's exports in one store, hands each run its imports as starting artifacts and
returns a plain mapping: form name to one `Worksheet` per instance, in instance order.

A form without an instances list has a default instance list of exactly one instance, and the
limits apply to the length of its list uniformly. `max_instances` is the most records the caller
may give and `min_instances` the fewest. An `exclusive_group` is shared by forms of which at most
one may have instances: with none the group exports nothing, so what totals its forms' exports
totals to zero. The `FormSet` refuses a caller who breaks a limit with a ValidationError naming the
form or the group, and refuses at construction a group that names only one form or in which two
forms always have instances (each can never hold).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from decimal import Decimal
from typing import Any

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import Capability
from tax_engine.domain.composition import Composition
from tax_engine.domain.errors import (
    BlankNotAllowedError,
    DomainError,
    DuplicateArtifactError,
    InvalidCompositionError,
    InvalidManifestError,
    NotFoundError,
    ValidationError,
)
from tax_engine.domain.manifest import Form
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.domain.trace import FormInstanceLine, TraceLine
from tax_engine.domain.worksheet import Worksheet


class FormComposition:
    """One form wired: the capabilities of form `name` as an inner `Composition`.

    Built with `exports` and, optionally, the `instances` kind (a record list, else an
    InvalidCompositionError). The inner composition returns the exports. Its inputs are the kinds of
    `starting` (the starting artifacts of the computation) that the form's capabilities consume or
    export, plus the fields of `instances` if it has any, plus, always, its imports. A form that
    reads its own `<form>.<export>` gets, in each run, a record list of that export over the runs
    before it, in run order (empty in the first). A field of `instances` that is also among
    `starting` is an InvalidCompositionError: one kind, two values.
    An export of a `Decimal` or `int` kind or a record-list kind is also readable by every form as
    `<form>.<export>`; one of another kind (a rate, digits) is only on the form's worksheets.
    Any breach of the rules of `Composition`, an empty `exports`, an export that is another form's,
    a `max_instances` below 1, a `min_instances` below 0 or above `max_instances`, or a
    `min_instances` above 1 on a form without an instances list (its default list has one instance)
    or a malformed `exclusive_group` is an InvalidCompositionError. The form is always named in the
    message (`form 'x': ...`).
    `max_instances`, `min_instances` and `exclusive_group` are the limits the `FormSet` enforces on
    the instances.
    """

    def __init__(
        self,
        name: str,
        capabilities: Iterable[Capability],
        *,
        exports: Iterable[ArtifactKind[Any]],
        instances: ArtifactKind[Any] | None = None,
        starting: frozenset[ArtifactKind[Any]] = frozenset(),
        max_instances: int | None = None,
        min_instances: int | None = None,
        exclusive_group: str | None = None,
        blank_inputs: frozenset[ArtifactKind[Any]] = frozenset(),
    ) -> None:
        """Wire `capabilities` as the form `name`, exporting `exports`, over `instances` if any.

        At most `max_instances` and at least `min_instances` instances (no limit for `None`) may be
        given, and at most one form of the `exclusive_group` may have any. A form without
        `instances` has one instance. `blank_inputs` are the starting artifacts of the computation
        that may arrive blank; the form's own composition may take a blank for those of them it
        reads, and refuses a blank in any other input.
        """
        if instances is not None and not isinstance(instances, RecordListKind):
            raise InvalidCompositionError(
                f"form {name!r}: instances {instances.identifier!r} is not a record list"
            )
        listed = tuple(exports)
        if not listed:
            raise InvalidCompositionError(f"form {name!r}: exports must name at least one artifact")
        for export in listed:
            if export.is_form_export:
                raise InvalidCompositionError(
                    f"form {name!r}: export {export.identifier!r} is another form's export"
                )
        try:
            Form.check_limits(max_instances, min_instances, instances is not None)
            if exclusive_group is not None:
                Form.check_identifier("exclusive_group", exclusive_group)
        except InvalidManifestError as exc:
            raise InvalidCompositionError(f"form {name!r}: {exc}") from None
        wired = tuple(capabilities)
        produced = {kind for capability in wired for kind in capability.produces}
        read = {kind for capability in wired for kind in capability.consumes} | set(listed)
        self._name = name
        self._instances = instances
        self._max_instances = max_instances
        self._min_instances = min_instances
        self._exclusive_group = exclusive_group
        self._exports = listed
        self._derived = self.derive(name, listed)
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
        self._blank_inputs = blank_inputs & self._inputs
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
    def derive(name: str, exports: Iterable[ArtifactKind[Any]]) -> tuple[RecordListKind, ...]:
        """The kind `<form>.<export>` of each of the form `name`'s `exports` a record can hold.

        Each is a record list of the export's one field, in the order of the exports. An export
        that is not an amount, a count or a record list (a rate, say, or digits) has none: no
        other form reads it.
        """
        namespace, _, form_id = name.partition("/")
        return tuple(
            RecordListKind(f"{namespace}/{form_id}.{export.label}", fields=(export,))
            for export in exports
            if issubclass(export.value_type, Decimal)
            or export.value_type is int
            or isinstance(export, RecordListKind)
        )

    @property
    def name(self) -> str:
        """The form's name, `<namespace>/<snake_case>`."""
        return self._name

    @property
    def instances(self) -> RecordListKind | None:
        """The record-list kind with a record per instance; `None` without an instances list."""
        return self._instances

    @property
    def max_instances(self) -> int | None:
        """The most instances the caller may give; `None` for no maximum."""
        return self._max_instances

    @property
    def min_instances(self) -> int | None:
        """The fewest instances the caller may give; `None` for no minimum."""
        return self._min_instances

    @property
    def exclusive_group(self) -> str | None:
        """The group of which at most one form may have instances; `None` for no group."""
        return self._exclusive_group

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
    def blank_inputs(self) -> frozenset[ArtifactKind[Any]]:
        """The starting kinds this form's composition may take blank."""
        return self._blank_inputs

    @property
    def composition(self) -> Composition:
        """The inner composition, computed once per instance (one without an instances list)."""
        return self._composition


class FormSet:
    """The forms of a computation, run in the order of their imports.

    Construction fails with InvalidCompositionError naming the forms for a form listed twice, an
    instances kind that is not among `inputs`, an exclusive group naming one form or two forms that
    always have instances, an input that is a form's derived `<form>.<export>` kind, an import that
    no form exports, a cycle of imports, or an input that no form reads (an instances kind is read
    by its form). A form's read of its own derived export is not a cycle: see `FormComposition`.
    """

    def __init__(
        self,
        forms: Iterable[FormComposition],
        *,
        inputs: frozenset[ArtifactKind[Any]],
        defaults: Iterable[Artifact[Any]] = (),
    ) -> None:
        """Wire `forms` into a computation that starts from the artifacts of the kinds `inputs`.

        `defaults` are the artifacts a caller who leaves out an input of that kind, or gives it
        blank when the default is a value, is read as giving (a blank default among them);
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

        Each form runs once per record of its instances (a form without an instances list has one
        instance), in `forms` order, on a worksheet of the starting artifacts it reads, its record's
        fields and its imports. The result maps each form's name to its worksheets in instance
        order, none if its instances list is empty.
        A DomainError from a run is raised as itself; its message starts with the form and the
        instance position (`<form>, instance N: ...`, N being 1 for a form without an instances
        list). A kind given that is a form's export is refused: the forms derive it,
        and two values for one kind are a DuplicateArtifactError, as in a `Worksheet`. More
        instances of a form than its `max_instances`, fewer than its `min_instances` (a form without
        an instances list has one), or instances of two forms of one exclusive
        group, are a ValidationError naming the form or the group, before any form runs.
        """
        kinds = [artifact.kind for artifact in artifacts]
        counts = Counter(kinds)
        for kind in kinds:
            if counts[kind] > 1:
                raise DuplicateArtifactError(f"two starting values for {kind.label!r}")
        given = {artifact.kind: artifact for artifact in artifacts}
        for kind, default in self._defaults.items():
            # Left out, or given blank where the default is a value: the default is what is read.
            if kind not in given or (given[kind].is_blank and not default.is_blank):
                given[kind] = default
        self._check_given(given)
        self._check_limits(given)
        store: dict[ArtifactKind[Any], Artifact[Any]] = {}
        worksheets: dict[str, tuple[Worksheet, ...]] = {}
        for form in self._forms:
            ran = tuple(self._runs(form, given, store))
            worksheets[form.name] = ran
            for derived in form.derived:
                store[derived] = self._export_of(derived, ran)
        return worksheets

    def trace(self, worksheets: Mapping[str, Sequence[Worksheet]]) -> tuple[TraceLine, ...]:
        """A `FormInstanceLine` per worksheet of `worksheets` that has trace lines, in the order the
        forms run.

        The position is from 1, counting every worksheet; a form without an instances list has one
        instance, 1. A form with no steps (it only exports its input) has no line.
        """
        return tuple(
            FormInstanceLine(form.name, position, worksheet.trace)
            for form in self._forms
            for position, worksheet in enumerate(worksheets.get(form.name, ()), start=1)
            if worksheet.trace
        )

    def _runs(
        self,
        form: FormComposition,
        given: Mapping[ArtifactKind[Any], Artifact[Any]],
        store: Mapping[ArtifactKind[Any], Artifact[Any]],
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
            yield self._run(form, 1, [*shared, *imported, *self._earlier_runs(form, done)])
            return
        for position, record in enumerate(given[instances].value.records, start=1):
            starting = [Artifact(kind, record[kind]) for kind in fields]
            earlier = self._earlier_runs(form, done)
            worksheet = self._run(form, position, [*shared, *starting, *imported, *earlier])
            done.append(worksheet)
            yield worksheet

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

        A blank export has no place in a record, so it is a BlankNotAllowedError naming the
        instance.
        """
        (export,) = derived.fields
        for position, worksheet in enumerate(ran, start=1):
            if worksheet.get(export).is_blank:
                raise BlankNotAllowedError(
                    f"{derived.identifier.partition('.')[0]}, instance {position}: "
                    f"{export.label!r} is blank, and a form cannot export a blank"
                )
        listed = [{export: worksheet.get(export).value} for worksheet in ran]
        return Artifact(derived, RecordList(derived.fields, listed))

    @staticmethod
    def _run(form: FormComposition, position: int, starting: list[Artifact[Any]]) -> Worksheet:
        try:
            return form.composition.compute(*starting)
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
