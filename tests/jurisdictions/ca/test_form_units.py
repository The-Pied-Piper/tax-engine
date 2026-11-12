"""The units the federal form manifests declare, as the Ontario return loads them.

Every amount a `ca/forms/**/*.yaml` manifest declares, as an input or as the figure of a capability,
is in Canadian dollars (`ca/cad`); the CPP months input of Schedule 8 is in `core/months`. The
exceptions are listed below, each with its reason. A figure the manifests start declaring needs a
unit or an entry in the exceptions, so a new line cannot print bare. `ca/employment_income` is
declared in the Ontario manifest, so it is not listed here.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

import tax_engine.jurisdictions.ca
from tax_engine import registrations
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import Manifest

FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"

CAD = "ca/cad"

# Declared by a ca form but not in dollars. `None` is no unit.
EXCEPTIONS: dict[str, str | None] = {
    # A rate the form holds as an amount (line 73), so dollars would be wrong.
    "ca/federal_bracket_column_rate_line_73": None,
    # Schedule 8 line A, the months of CPP contributions.
    "ca/cpp_months": "core/months",
    # The 0 or 1 flags of T2204 lines 1 and 15 are counts, not money.
    "ca/t2204_line_1_count": None,
    "ca/t2204_line_15_count": None,
}


def declared() -> dict[str, str | None]:
    """The unit expected of each figure the ca form manifests declare, in or out."""
    kinds = registrations.artifact_kinds()
    found: dict[str, str | None] = {}
    for path in sorted(FORMS.rglob("*.yaml")):
        body = yaml.safe_load(path.read_text(encoding="utf-8"))
        names = [item["name"] for item in body.get("inputs") or []]
        for selection in body.get("capabilities") or []:
            names.extend(selection["produces"].values())
        for name in names:
            if name in EXCEPTIONS:
                found[name] = EXCEPTIONS[name]
            elif isinstance(kinds.kind(name), AmountKind):
                found[name] = CAD
            else:
                raise AssertionError(f"{path.name}: {name} is neither an amount nor an exception")
    return found


def units_in(manifest: Manifest) -> dict[str, str | None]:
    """The unit each figure of the ca forms and the return's inputs declares, as written."""
    units = {name: declaration.unit for name, declaration in manifest.inputs.items()}
    for form in manifest.forms:
        if form.name.startswith("ca/"):
            for selection in form.capabilities:
                for name in selection.produces.values():
                    units[name] = selection.unit
    return units


@pytest.fixture(scope="module")
def manifest() -> Manifest:
    source = YamlJurisdictionSource(
        registrations.JURISDICTIONS.roots(),
        registrations.artifact_kinds(),
        registrations.units(),
    )
    (loaded,) = source.get_jurisdiction(JurisdictionCode("CA-ON")).manifests
    return loaded


def test_the_figures_are_found() -> None:
    expected = declared()

    assert len(expected) > 90
    assert list(expected.values()).count("core/months") == 1
    assert list(expected.values()).count(CAD) > 90
    assert "ca/employment_income" not in expected


@pytest.mark.parametrize("name", sorted(declared()))
def test_each_federal_figure_declares_its_unit(manifest: Manifest, name: str) -> None:
    assert units_in(manifest)[name] == declared()[name]
