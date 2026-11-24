"""The units the federal form manifests declare, as the registered returns load them.

Every amount a `ca/forms/**/*.yaml` manifest declares, as an input or as the figure of a capability,
is in Canadian dollars (`ca/cad`); the CPP months input of Schedule 8 is in `core/months`. The
exceptions are listed below, each with its reason. A figure the manifests start declaring needs a
unit or an entry in the exceptions, so a new line cannot print bare. `ca/employment_income` is
declared in the Ontario manifest, so it is not listed here.
"""

from __future__ import annotations

from collections.abc import Sequence

import pytest
import yaml

from tax_engine import registrations
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import Manifest
from tests.federal_forms import FEDERAL_FORMS
from tests.manifest_support import inputs_of

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
    # The take-home marginal rate form works in rates (a fraction of a dollar per dollar of salary).
    "ca/marginal_federal_bracket_column_rate": "core/percent",
    "ca/marginal_federal_gate": "core/percent",
    "ca/marginal_cpp_base_rate": "core/percent",
    "ca/marginal_cpp_first_additional_rate": "core/percent",
    "ca/marginal_cpp_second_additional_rate": "core/percent",
    "ca/marginal_ei_rate": "core/percent",
    "ca/marginal_salary_gate": "core/percent",
    "ca/marginal_net_income_rate_before_cpp2": "core/percent",
    "ca/marginal_net_income_rate": "core/percent",
    "ca/marginal_credit_contribution_rate": "core/percent",
    "ca/marginal_federal_contribution_credit_rate": "core/percent",
    "ca/marginal_federal_bracket_rate": "core/percent",
    "ca/marginal_federal_bpa_phase_down_gate": "core/percent",
    "ca/marginal_phase_down_net_income_rate": "core/percent",
    "ca/marginal_federal_bpa_reduction_rate": "core/percent",
    "ca/marginal_federal_bpa_credit_rate": "core/percent",
    "ca/marginal_federal_rate_before_credits": "core/percent",
    "ca/marginal_federal_rate_after_credits": "core/percent",
    "ca/marginal_federal_rate": "core/percent",
    "ca/marginal_contribution_rate": "core/percent",
}


def declared() -> dict[str, str | None]:
    """The unit expected of each figure the ca form manifests declare, in or out."""
    kinds = registrations.artifact_kinds()
    found: dict[str, str | None] = {}
    for path in sorted(FEDERAL_FORMS.rglob("*.yaml")):
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


def units_in(manifests: Sequence[Manifest]) -> dict[str, str | None]:
    """The unit each figure of the ca forms and the returns' inputs declares, as written.

    A federal form is imported by the returns that use it (the T691 by the provinces that read it,
    not by Ontario), so the figures are read over every registered return's manifest; a form
    imported by several declares the same unit in each.
    """
    units: dict[str, str | None] = {}
    for manifest in manifests:
        units.update({name: d.unit for name, d in inputs_of(manifest).items()})
        for form in manifest.forms:
            if form.name.startswith("ca/"):
                for selection in form.capabilities:
                    for name in selection.produces.values():
                        units[name] = selection.unit
    return units


@pytest.fixture(scope="module")
def manifests() -> list[Manifest]:
    source = YamlJurisdictionSource(
        registrations.JURISDICTIONS.roots(),
        registrations.artifact_kinds(),
        registrations.units(),
    )
    return [
        source.get_jurisdiction(code).manifest_for(2025)
        for code in registrations.JURISDICTIONS.jurisdiction_codes()
    ]


def test_the_figures_are_found() -> None:
    expected = declared()

    assert len(expected) > 90
    assert list(expected.values()).count("core/months") == 1
    assert list(expected.values()).count(CAD) > 90
    assert expected["ca/employment_income"] == CAD  # the salary, declared by the T1 income form


@pytest.mark.parametrize("name", sorted(declared()))
def test_each_federal_figure_declares_its_unit(manifests: list[Manifest], name: str) -> None:
    assert units_in(manifests)[name] == declared()[name]
