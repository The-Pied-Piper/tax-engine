"""The Ontario take-home manifest asks the caller for the gross salary and for nothing else.

The take-home calculator has one input. Every other input a form declares must be optional, with
its blank rule (a fixed fallback or `compute`), or a salary-only request is refused.
"""

from __future__ import annotations

from pathlib import Path

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


def test_the_return_exports_t1_line_167_and_the_federal_marginal_rate() -> None:
    (default,) = (form for form in _manifest().forms if form.name == "ca-on/return")

    assert set(default.exports) == {"ca/refund_or_balance_owing", "ca/federal_marginal_rate"}


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
