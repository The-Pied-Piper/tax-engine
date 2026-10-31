"""Jurisdiction manifest: which capabilities run for a jurisdiction, and from which tax year.

A manifest selects capabilities and fills their slots (design.md §4): parameter slots with
families, artifact slots with artifact identifiers. The slots themselves are declared in code.
A manifest is a flat set of forms, peers that together are the return (a form is a named group of
selections with the artifacts it exports), and the identifiers of the artifacts the computation
starts from.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from tax_engine.domain.errors import InvalidManifestError, InvalidRegistrationError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace


@dataclass(frozen=True, slots=True)
class CapabilitySelection:
    """One capability chosen by a manifest, with its slots filled by identifier.

    `params` maps parameter slots to families; `consumes` and `produces` map artifact slots to
    artifact identifiers, and a consumed slot may instead map to a list of identifiers, kept in
    order as a tuple. `blank` maps a consumed slot to what a blank in it does: the text of the
    fallback value taken in its place, or `pass_on`; a slot not named refuses a blank. Each is
    kept as a read-only copy of what it was given.
    """

    name: str
    params: Mapping[str, str]
    consumes: Mapping[str, str | tuple[str, ...]]
    produces: Mapping[str, str]
    blank: Mapping[str, str] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("params", "produces", "blank"):
            object.__setattr__(self, name, MappingProxyType(dict(getattr(self, name))))
        # A list of identifiers becomes a tuple, so the selection stays frozen and hashable.
        consumes = {
            slot: named if isinstance(named, str) else tuple(named)
            for slot, named in self.consumes.items()
        }
        object.__setattr__(self, "consumes", MappingProxyType(consumes))

    def __hash__(self) -> int:
        """Hash by value, like the frozen dataclass it is; the read-only mappings are unhashable."""
        bindings = (self.params, self.consumes, self.produces, self.blank)
        return hash((self.name, *(frozenset(mapping.items()) for mapping in bindings)))


@dataclass(frozen=True, slots=True)
class Form:
    """A named group of selections run once per instance, with the artifacts it exports.

    A form is a peer of the others, not a capability: `instances` is the identifier of the
    record-list kind the caller supplies, one record per instance, or `None` for a form without an
    instances list, which has one instance; `exports` are the identifiers of the artifacts the form
    produces, each readable by every form (itself aside) as `<name>.<local id of the export>`. All
    are plain identifiers
    `<namespace>/<snake_case>`: the dotted identifier is built by the engine, never written.
    `exports` and `capabilities` (the form's selections) are kept as tuples copied from what was
    given. The inputs of a form are not declared: they are derived from its selections.

    A form without `instances` has a default instance list of one instance, and the limits apply to
    its count. `max_instances` is the most instances a caller may give (an integer of at least 1;
    `None` for no maximum) and `min_instances` the fewest (an integer of at least 0, 0 meaning no
    minimum; `None` for none); the minimum may not be above the maximum. `exclusive_group` is an
    identifier shared by forms of which at most one may have instances (`None` for no group).
    """

    name: str
    instances: str | None
    exports: tuple[str, ...]
    capabilities: tuple[CapabilitySelection, ...]
    max_instances: int | None = None
    min_instances: int | None = None
    exclusive_group: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "exports", tuple(self.exports))
        object.__setattr__(self, "capabilities", tuple(self.capabilities))
        self.check_identifier("name", self.name)
        if self.instances is not None:
            self.check_identifier("instances", self.instances)
        if not self.exports:
            raise InvalidManifestError("exports must name at least one artifact")
        self.check_exports("exports", self.exports)
        try:
            self.check_limits(self.max_instances, self.min_instances, self.instances is not None)
        except InvalidManifestError as exc:
            raise InvalidManifestError(f"form {self.name!r}: {exc}") from None
        if self.exclusive_group is not None:
            self.check_identifier("exclusive_group", self.exclusive_group)

    @staticmethod
    def check_limits(
        max_instances: object, min_instances: object, has_instances_list: bool
    ) -> None:
        """Refuse limits no instance count could satisfy; the message does not name the form.

        Each given limit must be an integer (a boolean is not): `max_instances` at least 1,
        `min_instances` at least 0 and not above the maximum. A form without an instances list has
        one instance, so a `min_instances` above 1 can never hold.
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

    `forms` are the peers that together are the return, in a tuple of at least one form with
    distinct names. `inputs` are the identifiers of the artifacts a computation starts from: a
    non-empty set, among them the instances kind of each form, which the caller supplies with the
    rest. Each form's own inputs are derived from its selections.
    """

    jurisdiction: JurisdictionCode
    version: int
    valid_from_tax_year: int
    inputs: frozenset[str]
    forms: tuple[Form, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "forms", tuple(self.forms))
        if not self.forms:
            raise InvalidManifestError("forms must name at least one form")
        names = [found.name for found in self.forms]
        for name in names:
            if names.count(name) > 1:
                raise InvalidManifestError(f"form {name!r} is listed more than once")
        if not self.inputs:
            raise InvalidManifestError("inputs must name at least one artifact")
