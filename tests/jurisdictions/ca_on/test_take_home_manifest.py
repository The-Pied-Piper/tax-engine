"""The Ontario take-home manifest asks the caller for the gross salary and for nothing else.

The take-home calculator has one input. Every other input a form declares must be optional, with
its blank rule (a fixed fallback or `compute`), or a salary-only request is refused.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.manifest import Manifest
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units

SALARY = "ca/employment_income"


def _manifest() -> Manifest:
    source = YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units())
    (manifest,) = source.get_jurisdiction(JurisdictionCode("CA-ON")).manifests
    return manifest


def test_the_salary_is_the_only_required_input() -> None:
    required = {name for name, declaration in _manifest().inputs.items() if declaration.required}

    assert required == {SALARY}


def test_the_return_exports_the_signed_total_tax_of_t1_line_167_and_the_marginal_rate_pieces() -> (
    None
):
    (default,) = (form for form in _manifest().forms if form.name == "ca-on/return")

    assert default.exports == (
        "ca-on/ontario_bracket_rate_return",
        "ca-on/ontario_surtax_factor",
        "ca-on/return_health_premium_slope",
        "ca/refund_or_balance_owing",
    )


def test_schedule_8_is_a_required_form_without_instances() -> None:
    (schedule_8,) = (form for form in _manifest().forms if form.name == "ca/schedule_8")

    assert schedule_8.required
    assert schedule_8.instances is None


def test_schedule_8_exports_the_cpp_figures_the_t1_and_on428_read() -> None:
    (schedule_8,) = (form for form in _manifest().forms if form.name == "ca/schedule_8")

    assert set(schedule_8.exports) == {
        "ca/schedule_8_cpp_base_contributions_on_return",
        "ca/schedule_8_cpp_enhanced_contributions_on_return",
    }


def test_the_federal_forms_are_imported_in_the_order_the_manifest_lists_them() -> None:
    names = [form.name for form in _manifest().forms]

    imported = [
        "ca/t1_taxable_income",
        "ca/t1_tax_and_credits",
        "ca/schedule_6",
        "ca/schedule_8",
        "ca/t2204",
    ]
    assert names[1 : 1 + len(imported)] == imported


def test_the_t1_reads_the_provincial_tax_ontario_supplies() -> None:
    (on428,) = (form for form in _manifest().forms if form.name == "ca-on/on428")

    assert dict(on428.supplies) == {"ca/provincial_tax.amount": "ca-on/on428_ontario_tax_line_90"}


def test_the_ontario_manifest_declares_the_federal_inputs_by_importing_their_forms() -> None:
    own = {
        path.name
        for path in Path(tax_engine.jurisdictions.ca_on.__file__).parent.rglob("*_inputs.yaml")
    }

    assert not {name for name in own if not name.startswith("on428_")}
    assert {
        "ca/cpp_months",
        "ca/other_employment_income",
        "ca/social_benefits_repayment",
    } <= set(_manifest().inputs)


def test_on428_exports_line_90_the_surtax_base_line_65_and_the_line_5_rate() -> None:
    (on428,) = (form for form in _manifest().forms if form.name == "ca-on/on428")

    assert set(on428.exports) == {
        "ca-on/on428_ontario_tax_line_90",
        "ca-on/on428_surtax_base_line_65",
        "ca-on/on428_bracket_column_rate_line_5",
    }


def _return_steps() -> list[tuple[str, dict[str, str], dict[str, Any], dict[str, str]]]:
    """The steps of the return as (name, params, consumes, produces)."""
    (default,) = (form for form in _manifest().forms if form.name == "ca-on/return")
    return [
        (step.name, dict(step.params), dict(step.consumes), dict(step.produces))
        for step in default.capabilities
    ]


def test_the_return_reads_line_65_into_its_own_artifact_and_gives_the_surtax_factor() -> None:
    # The return totals the one amount of ON428's export of line 65 (the export of another form is
    # read as a record list) into its own artifact, then `ca-on/surtax_factor` reads that artifact
    # and the datasets of lines 66 and 67. Titles, references and units are not pinned here.
    steps = _return_steps()

    assert (
        "core/record_total",
        {},
        {"records": "ca-on/on428.on428_surtax_base_line_65"},
        {"output": "ca-on/ontario_surtax_base"},
    ) in steps
    assert (
        "ca-on/surtax_factor",
        {"line_66": "ca-on/surtax_line_66", "line_67": "ca-on/surtax_line_67"},
        {"base": "ca-on/ontario_surtax_base"},
        {"output": "ca-on/ontario_surtax_factor"},
    ) in steps


def test_the_return_reads_the_on428_line_5_bracket_rate() -> None:
    assert (
        "core/record_total",
        {},
        {"records": "ca-on/on428.on428_bracket_column_rate_line_5"},
        {"output": "ca-on/ontario_bracket_rate_return"},
    ) in _return_steps()


def test_the_return_still_totals_line_167() -> None:
    assert (
        "core/record_total",
        {},
        {"records": "ca/t1_tax_and_credits.refund_or_balance_owing"},
        {"output": "ca/refund_or_balance_owing"},
    ) in _return_steps()
