"""Unit tests for the manifest key `unit:` on YamlJurisdictionSource.

An input, a field of a form's instances list and a capability selection may name a `unit:`, which
the source resolves against the `UnitRegistry` it is given for the manifest's jurisdiction (core's
units, the jurisdiction's own, a province's federal ones). The manifest keeps the name. A name no
one declares fails at load, naming the file. A selection's unit belongs to the one figure it
produces. Everything here is made up.
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.errors import InvalidManifestError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind, RecordListKind
from tax_engine.domain.manifest import CapabilitySelection, InputDeclaration, Manifest
from tax_engine.domain.registry import Namespace
from tax_engine.domain.unit import Placement, UnitCatalog, UnitRegistry
from tests.kinds import AutoKinds

EX_ON = JurisdictionCode("EX-ON")

HEADER = """\
jurisdiction: EX-ON
version: 1
valid_from_tax_year: 2025
outputs: [ex/y]
"""

GROSS_RENT = AmountKind("ex/gross_rent")
EXPENSES = AmountKind("ex/expenses")
RENTALS = RecordListKind("ex/rentals", fields=(GROSS_RENT, EXPENSES))


def units() -> UnitRegistry:
    registry = UnitRegistry()
    for namespace, name, singular, plural, placement in (
        ("core", "moons", "moon", "moons", Placement.AFTER),
        ("ex", "crowns", "EX$", "EX$", Placement.BEFORE),
        ("ex-on", "ducats", "ON$", "ON$", Placement.BEFORE),
    ):
        catalog = UnitCatalog(Namespace(namespace))
        catalog.declare(name, singular, plural, placement)
        registry.register_catalog(catalog)
    return registry


def source(directory: Path, registry: UnitRegistry | None = None) -> YamlJurisdictionSource:
    kinds = AutoKinds()
    kinds.register("ex/rentals", RENTALS)
    return YamlJurisdictionSource(
        {Namespace("ex-on"): directory / "ex-on"},
        kinds,
        units=units() if registry is None else registry,
    )


def load(directory: Path, body: str, registry: UnitRegistry | None = None) -> Manifest:
    path = directory / "ex-on" / "manifests" / "v1.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HEADER + dedent(body), encoding="utf-8")
    (manifest,) = source(directory, registry).get_jurisdiction(EX_ON).manifests
    return manifest


def load_folder(directory: Path, field: str) -> Manifest:
    """A folder manifest (a form needs one) whose form `ex/rental` has the field `field`."""
    folder = directory / "ex-on" / "manifests" / "v1"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "00-header.yaml").write_text(
        HEADER + "inputs: [{name: ex/rentals, required: true}]\ncapabilities: []\n",
        encoding="utf-8",
    )
    (folder / "01-rental.yaml").write_text(
        dedent(
            f"""\
            form:
              name: ex/rental
              required: true
              instances: ex/rentals
              exports: [ex/n]
              fields:
                - {field}
                - {{name: ex/expenses, required: true}}
            capabilities:
              - {{name: ex/a, produces: {{output: ex/n}}}}
            """
        ),
        encoding="utf-8",
    )
    (manifest,) = source(directory).get_jurisdiction(EX_ON).manifests
    return manifest


def test_an_input_may_name_a_unit(tmp_path: Path) -> None:
    manifest = load(
        tmp_path,
        """\
        inputs:
          - {name: ex/rent, required: true, unit: crowns}
          - {name: ex/term, required: false, default: "12", basis: "L", unit: moons}
          - {name: ex/plain, required: true}
        capabilities: []
        """,
    )

    assert manifest.inputs["ex/rent"] == InputDeclaration("ex/rent", True, unit="crowns")
    assert manifest.inputs["ex/term"].unit == "moons"
    assert manifest.inputs["ex/plain"].unit is None


def test_a_selection_may_name_the_unit_of_the_figure_it_produces(tmp_path: Path) -> None:
    manifest = load(
        tmp_path,
        """\
        inputs: [{name: ex/x, required: true}]
        capabilities:
          - {name: ex/a, unit: crowns, produces: {output: ex/y}}
          - {name: ex/b, produces: {output: ex/z}}
        """,
    )
    (form,) = manifest.forms

    assert form.capabilities[0] == CapabilitySelection(
        name="ex/a", params={}, consumes={}, produces={"output": "ex/y"}, unit="crowns"
    )
    assert form.capabilities[1].unit is None


def test_a_field_of_a_forms_instances_may_name_a_unit(tmp_path: Path) -> None:
    manifest = load_folder(tmp_path, "{name: ex/gross_rent, required: true, unit: crowns}")

    (form,) = (f for f in manifest.forms if f.name == "ex/rental")
    assert form.fields[0] == InputDeclaration("ex/gross_rent", True, unit="crowns")
    assert form.fields[1].unit is None


def test_a_unit_keeps_its_name_as_the_manifest_wrote_it(tmp_path: Path) -> None:
    manifest = load(
        tmp_path,
        """\
        inputs: [{name: ex/rent, required: true, reference: "4", unit: ducats}]
        capabilities: []
        """,
    )

    declared = manifest.inputs["ex/rent"]
    assert (declared.reference, declared.unit) == ("4", "ducats")


@pytest.mark.parametrize("name", ["crowns", "moons", "ducats"])
def test_a_unit_of_core_the_package_or_its_federal_package_resolves(
    tmp_path: Path, name: str
) -> None:
    # EX-ON sees core (moons), its own package (ducats) and its federal one (crowns).
    manifest = load(
        tmp_path,
        f"""\
        inputs: [{{name: ex/rent, required: true, unit: {name}}}]
        capabilities: []
        """,
    )

    assert manifest.inputs["ex/rent"].unit == name


def test_an_unknown_unit_on_an_input_fails_at_load_naming_the_file_and_the_input(
    tmp_path: Path,
) -> None:
    with pytest.raises(InvalidManifestError, match="input 'ex/rent': unit 'furlongs'") as caught:
        load(
            tmp_path,
            """\
            inputs: [{name: ex/rent, required: true, unit: furlongs}]
            capabilities: []
            """,
        )

    assert str(tmp_path / "ex-on" / "manifests" / "v1.yaml") in str(caught.value)


def test_an_unknown_unit_on_a_selection_fails_at_load(tmp_path: Path) -> None:
    with pytest.raises(InvalidManifestError, match="ex/a: unit 'furlongs'"):
        load(
            tmp_path,
            """\
            inputs: [{name: ex/x, required: true}]
            capabilities:
              - {name: ex/a, unit: furlongs, produces: {output: ex/y}}
            """,
        )


def test_an_unknown_unit_on_a_field_fails_at_load(tmp_path: Path) -> None:
    with pytest.raises(InvalidManifestError, match="unit 'furlongs'"):
        load_folder(tmp_path, "{name: ex/gross_rent, required: true, unit: furlongs}")


def test_a_unit_of_a_sibling_province_is_unknown(tmp_path: Path) -> None:
    registry = units()
    other = UnitCatalog(Namespace("ex-ab"))
    other.declare("florins", "AB$", "AB$", Placement.BEFORE)
    registry.register_catalog(other)

    with pytest.raises(InvalidManifestError, match="unit 'florins'"):
        load(
            tmp_path,
            """\
            inputs: [{name: ex/rent, required: true, unit: florins}]
            capabilities: []
            """,
            registry,
        )


def test_a_source_given_no_units_refuses_any_unit(tmp_path: Path) -> None:
    path = tmp_path / "ex-on" / "manifests" / "v1.yaml"
    path.parent.mkdir(parents=True)
    path.write_text(
        HEADER + "inputs: [{name: ex/rent, required: true, unit: moons}]\ncapabilities: []\n",
        encoding="utf-8",
    )

    with pytest.raises(InvalidManifestError, match="unit 'moons'"):
        YamlJurisdictionSource(
            {Namespace("ex-on"): tmp_path / "ex-on"}, AutoKinds()
        ).get_jurisdiction(EX_ON)


@pytest.mark.parametrize("given", ['""', '"   "', "null", "5", "[]", "Moons", "ex/moons"])
def test_a_unit_must_be_a_unit_name(tmp_path: Path, given: str) -> None:
    with pytest.raises(InvalidManifestError, match="unit"):
        load(
            tmp_path,
            f"""\
            inputs: [{{name: ex/rent, required: true, unit: {given}}}]
            capabilities: []
            """,
        )


def test_a_unit_belongs_to_the_one_figure_a_selection_produces(tmp_path: Path) -> None:
    with pytest.raises(
        InvalidManifestError, match="unit belongs to the one figure a selection produces"
    ):
        load(
            tmp_path,
            """\
            inputs: [{name: ex/x, required: true}]
            capabilities:
              - {name: ex/a, unit: moons, produces: {output: ex/y, other: ex/z}}
            """,
        )


# --- the manifest holds the units it names, resolved ---------------------------------------------


def test_a_manifest_holds_each_unit_its_declarations_name_by_name(tmp_path: Path) -> None:
    manifest = load(
        tmp_path,
        """\
        inputs:
          - {name: ex/rent, required: true, unit: crowns}
          - {name: ex/term, required: false, default: "12", basis: "L", unit: moons}
          - {name: ex/plain, required: true}
        capabilities:
          - {name: ex/a, unit: ducats, produces: {output: ex/y}}
          - {name: ex/b, unit: crowns, produces: {output: ex/z}}
        """,
    )
    registry = units()

    assert dict(manifest.units_by_name) == {
        "crowns": registry.get("ex/crowns"),
        "moons": registry.get("core/moons"),
        "ducats": registry.get("ex-on/ducats"),
    }
    assert manifest.units_by_name["crowns"].singular == "EX$"


def test_a_manifest_naming_no_unit_holds_none(tmp_path: Path) -> None:
    manifest = load(
        tmp_path,
        """\
        inputs: [{name: ex/rent, required: true}]
        capabilities: []
        """,
    )

    assert dict(manifest.units_by_name) == {}


def test_a_manifest_holds_the_unit_of_a_field_of_a_forms_instances(tmp_path: Path) -> None:
    manifest = load_folder(tmp_path, "{name: ex/gross_rent, required: true, unit: crowns}")

    assert set(manifest.units_by_name) == {"crowns"}


def test_each_manifest_of_a_jurisdiction_holds_only_the_units_it_names(tmp_path: Path) -> None:
    load(
        tmp_path,
        """\
        inputs: [{name: ex/rent, required: true, unit: crowns}]
        capabilities: []
        """,
    )
    later = tmp_path / "ex-on" / "manifests" / "v2.yaml"
    later.write_text(
        HEADER.replace("version: 1", "version: 2").replace("2025", "2026")
        + "inputs: [{name: ex/rent, required: true, unit: moons}]\ncapabilities: []\n",
        encoding="utf-8",
    )

    jurisdiction = source(tmp_path).get_jurisdiction(EX_ON)

    held = {m.version: set(m.units_by_name) for m in jurisdiction.manifests}
    assert held == {1: {"crowns"}, 2: {"moons"}}


def test_a_unit_name_declared_in_two_places_a_manifest_sees_is_refused_at_load(
    tmp_path: Path,
) -> None:
    registry = units()
    twin = UnitCatalog(Namespace("ex-on"))
    twin.declare("crowns", "ON$", "ON$", Placement.BEFORE)
    registry.register_catalog(twin)

    with pytest.raises(InvalidManifestError, match="unit 'crowns'.*ambiguous"):
        load(
            tmp_path,
            """\
            inputs: [{name: ex/rent, required: true, unit: crowns}]
            capabilities: []
            """,
            registry,
        )
