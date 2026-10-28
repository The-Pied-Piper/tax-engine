"""Reads parameter datasets from YAML files. Implements ParameterSource.

The source takes a mapping of namespace -> jurisdiction package directory. A dataset for
family `ex-on/brackets` and tax year 2025 lives at `<roots[ex-on]>/parameters/brackets/2025.yaml`:
the family's first segment is its namespace, and the rest (which may nest) is its path under
`parameters/`. Every file has the same envelope
(family, tax_year, kind, sources, rounding) plus keys specific to its kind,
which that kind's parser reads. The file must declare the family, year and kind
that were asked for. An absent file is NotFoundError: a year is never carried
forward. Decimals are YAML strings ("0.145") so they never pass through float.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path

import yaml

from tax_calculator.adapters.outbound.parameter_parsers.parser import OptionalKeysParser
from tax_calculator.adapters.outbound.parameter_parsers.registry import ParameterParserRegistry
from tax_calculator.adapters.outbound.yaml_support import YamlNode, YamlShapeError
from tax_calculator.domain.errors import DomainError, InvalidParameterDataError, NotFoundError
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.registry import Namespace

_FAMILY = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*(/[a-z0-9]+([_-][a-z0-9]+)*)+")
_ENVELOPE_KEYS = frozenset({"family", "tax_year", "kind", "sources", "rounding"})


class YamlParameterSource:
    """Parameter datasets read from the `parameters/` directory of each jurisdiction package."""

    def __init__(
        self, roots: Mapping[Namespace, Path], parsers: ParameterParserRegistry | None = None
    ) -> None:
        """Read datasets under each namespace's package directory in `roots`, parsing each with
        its kind's parser from `parsers` (by default the shared ParameterParserRegistry)."""
        self._roots = dict(roots)
        self._parsers = parsers if parsers is not None else ParameterParserRegistry.shared()

    def get[T](self, family: str, tax_year: int, kind: ParameterKind[T]) -> ParameterDataset[T]:
        """Read `<root>/parameters/<family rest>/<tax_year>.yaml`; parse it with `kind`'s parser.

        The file must declare the same family, year and kind; see ParameterSource.get for errors.
        """
        parser = self._parsers.for_kind(kind)
        path = self._path(family, tax_year)
        try:
            document = YamlNode.load(path, "dataset")
            declared_kind = document.field("kind").require_string()
        except (OSError, yaml.YAMLError, YamlShapeError) as exc:
            raise InvalidParameterDataError(f"{path}: {exc}") from exc
        if declared_kind != kind.name:
            raise InvalidParameterDataError(
                f"{path}: kind {declared_kind!r} does not match the requested {kind.name!r}"
            )
        try:
            optional = (
                parser.optional_keys if isinstance(parser, OptionalKeysParser) else frozenset()
            )
            doc = document.require_mapping(_ENVELOPE_KEYS | parser.body_keys, optional=optional)
            self._check_identity(doc, family, tax_year)
            return ParameterDataset(
                family=family,
                tax_year=tax_year,
                kind=kind,
                values=parser.parse(doc),
                rounding=doc.field("rounding").parse_rounding_rule(),
                sources=self._sources(doc.field("sources")),
            )
        except (YamlShapeError, DomainError) as exc:
            raise InvalidParameterDataError(f"{path}: {exc}") from exc

    def _path(self, family: str, tax_year: int) -> Path:
        if not _FAMILY.fullmatch(family):
            raise ValueError(f"invalid parameter family {family!r}: expected e.g. 'ex-on/brackets'")
        namespace_name, rest = family.split("/", 1)
        namespace = Namespace(namespace_name)
        if namespace not in self._roots:
            raise NotFoundError(
                f"no {family} dataset: no jurisdiction package declares "
                f"namespace {namespace.name!r}"
            )
        path = self._roots[namespace] / "parameters" / rest / f"{tax_year}.yaml"
        if not path.is_file():
            raise NotFoundError(
                f"no {family} dataset for tax year {tax_year} (expected {path}); "
                "an absent year is never carried forward"
            )
        return path

    @staticmethod
    def _check_identity(doc: YamlNode, family: str, tax_year: int) -> None:
        declared_family = doc.field("family").require_string()
        if declared_family != family:
            raise YamlShapeError(f"family {declared_family!r} does not match {family!r}")
        declared_year = doc.field("tax_year").require_integer()
        if declared_year != tax_year:
            raise YamlShapeError(f"tax_year {declared_year} does not match {tax_year}")

    @staticmethod
    def _sources(node: YamlNode) -> tuple[str, ...]:
        entries = node.items()
        if not entries:
            raise YamlShapeError("sources must list at least one source")
        return tuple(entry.require_string() for entry in entries)
