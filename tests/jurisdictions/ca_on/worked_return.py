"""Worked returns: human-reviewed YAML files of a return's inputs and expected lines.

A file under `returns/` names its `jurisdiction` and `tax_year`, describes the taxpayer, lists
the `sources` its figures were checked against, and maps artifact identifiers to figures under
`inputs` and, per form, under `expected`. Every figure is a quoted string, so YAML never reads it
as a number: an amount is a decimal string, and a count (an `int` kind, under `inputs` or
`expected`) is a string of decimal digits with no sign and no leading zero, such as "0" or "3". A
record list (under `inputs`, or under `expected` for a line the return produces as a list, such as
T776 Area A's closing UCC) is a list of mappings, one per record in order, each keyed by its fields'
identifiers with figures spelled as above; `[]` is no records. A rate (a `Rate` kind, only under
`expected`) is a quoted decimal from 0 to 1, such as "0.55". Digits (a digits kind, under
`inputs` or `expected`, as a carried entry is listed under both) are quoted text kept as
entered, such as "012345678", or `""` for a box left blank. `WorkedReturn.load` checks that
shape and resolves each identifier through an artifact registry; every failure is a
WorkedReturnError naming the file and the key, except a value its kind refuses, such as a
negative amount, a rate above 1 or digits of the wrong length, which is the kind's own error.
An input given as `null` is a blank line, which the engine reads as the manifest's default.
A line or input the file leaves out is blank: `with_blanks` fills it in against the manifest's
declared inputs and outputs (a record list left out is no records, as an input and as an
expected line).
Under `expected` every key names a form (the return's own form, `<namespace>/return`, and each
form of the manifest); its value is a list with one entry per instance, in order, each a mapping
of artifact identifiers to figures (spelled as above) to check against that instance's own
worksheet. A form without instances has the one entry. `form_expected` keeps them, and
`check_forms` checks each names a form of the manifest and has an entry per instance. A form's
instances go under `inputs` as a record list of its instances kind.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, replace
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

from tax_engine.adapters.outbound.yaml_support import YamlNode, YamlShapeError
from tax_engine.domain.artifact import Artifact, ArtifactKind, ArtifactRegistry
from tax_engine.domain.blank import BLANK
from tax_engine.domain.digits import DigitsKind
from tax_engine.domain.errors import (
    InvalidJurisdictionCodeError,
    InvalidRegistrationError,
    UnknownRegistrationError,
)
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.manifest import Form
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.record_list import RecordList, RecordListKind

_SECTIONS = frozenset({"jurisdiction", "tax_year", "description", "sources", "inputs", "expected"})


class WorkedReturnError(ValueError):
    """A worked-return file is malformed or names something its manifest cannot leave blank."""


@dataclass(frozen=True)
class FormExpectation:
    """The lines a worked return expects of the instances of the form `form`.

    `instances` has one entry per instance, in instance order: the artifacts of that instance's
    own worksheet, as read from the file. An instance with nothing to check has no artifacts.
    """

    form: str
    instances: tuple[tuple[Artifact[Any], ...], ...]


@dataclass(frozen=True)
class WorkedReturn:
    """One worked return read from `path`: its starting artifacts and the lines it expects.

    `form_expected` are the lines per instance of each form, in file order; `expected` those of the
    return's own form (the form of the manifest's own selections, named `<namespace>/return` by
    convention), which has the one instance.
    """

    path: Path
    jurisdiction: JurisdictionCode
    tax_year: int
    description: str
    sources: tuple[str, ...]
    inputs: tuple[Artifact[Any], ...]
    form_expected: tuple[FormExpectation, ...]

    @property
    def return_form(self) -> str:
        """The name of the return's own form."""
        return self.jurisdiction.namespace.identifier("return")

    @property
    def expected(self) -> tuple[Artifact[Any], ...]:
        """The lines expected of the return's own worksheet; none when the file gives none.

        The return's own form has the one instance, which `check_forms` enforces.
        """
        for found in self.form_expected:
            if found.form == self.return_form:
                return found.instances[0] if found.instances else ()
        return ()

    @classmethod
    def discover(cls, directory: Path) -> tuple[Path, ...]:
        """Every `*.yaml` file directly in `directory`, in name order."""
        return tuple(sorted(directory.glob("*.yaml")))

    @classmethod
    def load(cls, path: Path, artifacts: ArtifactRegistry) -> WorkedReturn:
        """Read the worked return at `path`, resolving its identifiers through `artifacts`.

        Raises WorkedReturnError naming the file and the offending key.
        """
        try:
            root = YamlNode.load(path, path.name).require_mapping(_SECTIONS)
            form_expected = cls._expected(root.field("expected"), artifacts)
            return cls(
                path=path,
                jurisdiction=cls._jurisdiction(root.field("jurisdiction")),
                tax_year=root.field("tax_year").require_integer(),
                description=root.field("description").require_non_empty_string(),
                sources=cls._sources(root.field("sources")),
                inputs=cls._artifacts(root.field("inputs"), artifacts, inputs=True),
                form_expected=form_expected,
            )
        except (YamlShapeError, yaml.YAMLError) as exc:
            raise WorkedReturnError(f"{path}: {exc}") from None

    def with_blanks(
        self, inputs: frozenset[str], outputs: frozenset[str], artifacts: ArtifactRegistry
    ) -> WorkedReturn:
        """This return with every blank line of the form filled in, as the filer left it blank.

        `inputs` are the identifiers the manifest declares and `outputs` the exports of the return's
        own form. A declared input the file leaves out is entered as blank: 0 for an amount or a
        count, no records for a record list, the empty text for digits. A declared output the file
        leaves out is expected to be 0, or the empty text for digits, so a line that fires on a
        return not meant to trigger it still fails. Raises WorkedReturnError naming the file and
        the identifier for one `artifacts` does not know or that holds no blank.
        """
        given = {artifact.kind.identifier for artifact in self.inputs}
        listed = {artifact.kind.identifier for artifact in self.expected}
        blanks = self._blanks(sorted(outputs - listed), "expected", artifacts)
        own = FormExpectation(self.return_form, (self.expected + blanks,))
        others = tuple(found for found in self.form_expected if found.form != self.return_form)
        # The return's own entry keeps the position the file gave it, else it comes first.
        position = next(
            (n for n, found in enumerate(self.form_expected) if found.form == self.return_form),
            0,
        )
        return replace(
            self,
            inputs=self.inputs + self._blanks(sorted(inputs - given), "inputs", artifacts),
            form_expected=(*others[:position], own, *others[position:]),
        )

    def check_forms(self, forms: Iterable[Form], artifacts: ArtifactRegistry) -> None:
        """Check each form expectation of this return against the forms of the manifest.

        Raises WorkedReturnError naming the file for an expectation of a form not in `forms`, for
        an instances identifier that is not a record list and for one with other than an entry
        per instance (a form without instances has the one).
        """
        forms = tuple(forms)
        self._check_expectations({form.name: form for form in forms}, artifacts)

    def _check_expectations(self, forms: dict[str, Form], artifacts: ArtifactRegistry) -> None:
        """Each expectation names a form of the manifest, with an entry per instance."""
        for expectation in self.form_expected:
            if expectation.form not in forms:
                raise WorkedReturnError(
                    f"{self.path}: expected: {expectation.form!r} is not a form of the manifest"
                )
            form = forms[expectation.form]
            if form.instances is None:
                instances = 1
            else:
                kind = self._instances_kind(form, artifacts)
                (given,) = (a for a in self.inputs if a.kind == kind)
                instances = len(given.value.records)
            entries = len(expectation.instances)
            if entries != instances:
                raise WorkedReturnError(
                    f"{self.path}: expected: {expectation.form!r} has {entries} "
                    f"{'entry' if entries == 1 else 'entries'} for {instances} "
                    f"{'instance' if instances == 1 else 'instances'}"
                )

    def _instances_kind(self, form: Form, artifacts: ArtifactRegistry) -> RecordListKind:
        assert form.instances is not None  # only a form with instances has an instances kind
        try:
            kind = artifacts.kind(form.instances)
        except (UnknownRegistrationError, InvalidRegistrationError) as exc:
            raise WorkedReturnError(
                f"{self.path}: form {form.name!r}: unknown instances {form.instances!r} ({exc})"
            ) from None
        if not isinstance(kind, RecordListKind):
            raise WorkedReturnError(
                f"{self.path}: form {form.name!r}: instances {form.instances!r} "
                "is not a record list"
            )
        return kind

    def _blanks(
        self, identifiers: list[str], section: str, artifacts: ArtifactRegistry
    ) -> tuple[Artifact[Any], ...]:
        result: list[Artifact[Any]] = []
        for identifier in identifiers:
            try:
                kind = artifacts.kind(identifier)
            except (UnknownRegistrationError, InvalidRegistrationError) as exc:
                raise WorkedReturnError(
                    f"{self.path}: {section}: unknown artifact identifier {identifier!r} ({exc})"
                ) from None
            if kind.value_type is Decimal:
                result.append(Artifact(kind, Decimal(0)))
            elif kind.value_type is int:
                result.append(Artifact(kind, 0))
            elif isinstance(kind, RecordListKind):
                result.append(Artifact(kind, RecordList(kind.fields, [])))
            elif isinstance(kind, DigitsKind):
                result.append(Artifact(kind, ""))
            else:
                raise WorkedReturnError(
                    f"{self.path}: {section}: {identifier!r} holds a "
                    f"{kind.value_type.__name__}, which has no blank"
                )
        return tuple(result)

    @staticmethod
    def _jurisdiction(node: YamlNode) -> JurisdictionCode:
        try:
            return JurisdictionCode(node.require_non_empty_string())
        except InvalidJurisdictionCodeError as exc:
            raise YamlShapeError(f"{node.where}: {exc}") from None

    @staticmethod
    def _sources(node: YamlNode) -> tuple[str, ...]:
        sources = tuple(item.require_non_empty_string() for item in node.items())
        if not sources:
            raise YamlShapeError(f"{node.where} must not be empty")
        return sources

    @staticmethod
    def _count(node: YamlNode) -> int:
        text = node.require_string()
        try:
            return node.parse_whole_number()
        except YamlShapeError:
            raise YamlShapeError(f"{node.where} is not a count: {text!r}") from None

    @staticmethod
    def _records(node: YamlNode, kind: RecordListKind) -> RecordList:
        """`node` read as a list of records of `kind`'s fields; a nested list reads the same."""
        keys = frozenset(field.identifier for field in kind.fields)
        records: list[dict[ArtifactKind[Any], Decimal | int | RecordList]] = []
        for item in node.items():
            item.require_mapping(keys)
            record: dict[ArtifactKind[Any], Decimal | int | RecordList] = {}
            for field in kind.fields:
                value = item.field(field.identifier)
                if isinstance(field, RecordListKind):
                    record[field] = WorkedReturn._records(value, field)
                elif field.value_type is int:
                    record[field] = WorkedReturn._count(value)
                else:
                    record[field] = value.parse_decimal()
            records.append(record)
        return RecordList(kind.fields, records)

    @classmethod
    def _expected(cls, node: YamlNode, artifacts: ArtifactRegistry) -> tuple[FormExpectation, ...]:
        """The `expected` section: per form, in file order, the lines of each instance."""
        fields = node.fields()
        if not fields:
            raise YamlShapeError(f"{node.where} must not be empty")
        return tuple(
            FormExpectation(
                key,
                tuple(cls._read(item.fields(), artifacts, inputs=False) for item in value.items()),
            )
            for key, value in fields
        )

    @classmethod
    def _artifacts(
        cls, node: YamlNode, artifacts: ArtifactRegistry, *, inputs: bool
    ) -> tuple[Artifact[Any], ...]:
        fields = node.fields()
        if not fields:
            raise YamlShapeError(f"{node.where} must not be empty")
        return cls._read(fields, artifacts, inputs=inputs)

    @staticmethod
    def _read(
        fields: list[tuple[str, YamlNode]], artifacts: ArtifactRegistry, *, inputs: bool
    ) -> tuple[Artifact[Any], ...]:
        result: list[Artifact[Any]] = []
        for identifier, value in fields:
            try:
                kind = artifacts.kind(identifier)
            except (UnknownRegistrationError, InvalidRegistrationError) as exc:
                raise YamlShapeError(
                    f"{value.where}: unknown artifact identifier {identifier!r} ({exc})"
                ) from None
            if inputs and value.value is None:
                result.append(Artifact(kind, BLANK))  # `null`: the line left blank
            elif kind.value_type is Decimal:
                result.append(Artifact(kind, value.parse_decimal()))
            elif kind.value_type is int:
                result.append(Artifact(kind, WorkedReturn._count(value)))
            elif isinstance(kind, RecordListKind):
                result.append(Artifact(kind, WorkedReturn._records(value, kind)))
            elif isinstance(kind, DigitsKind):
                result.append(Artifact(kind, value.require_string()))
            elif not inputs and kind.value_type is Rate:
                result.append(Artifact(kind, Rate(value.parse_decimal())))
            else:
                accepted = (
                    "an amount, a count, a record list or digits"
                    if inputs
                    else "an amount, a count, a record list, a rate or digits"
                )
                raise YamlShapeError(
                    f"{value.where}: {identifier!r} holds a {kind.value_type.__name__}, "
                    f"not {accepted}"
                )
        return tuple(result)
