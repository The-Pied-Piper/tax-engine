"""The Ontario take-home manifest asks the caller for the gross salary and for nothing else.

The take-home calculator has one input. Every other input a form declares must be optional, with
its blank rule (a fixed fallback or `compute`), or a salary-only request is refused.
"""

from __future__ import annotations

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.manifest import Manifest
from tax_engine.registrations import JURISDICTIONS, artifact_kinds

SALARY = "ca/employment_income"


def _manifest() -> Manifest:
    source = YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds())
    (manifest,) = source.get_jurisdiction(JurisdictionCode("CA-ON")).manifests
    return manifest


def test_the_salary_is_the_only_required_input() -> None:
    required = {name for name, declaration in _manifest().inputs.items() if declaration.required}

    assert required == {SALARY}


def test_the_return_exports_the_signed_total_tax_of_t1_line_167() -> None:
    (default,) = (form for form in _manifest().forms if form.name == "ca-on/return")

    assert default.exports == ("ca/refund_or_balance_owing",)


def test_schedule_8_is_a_required_form_without_instances() -> None:
    (schedule_8,) = (form for form in _manifest().forms if form.name == "ca/schedule_8")

    assert schedule_8.required
    assert schedule_8.instances is None
