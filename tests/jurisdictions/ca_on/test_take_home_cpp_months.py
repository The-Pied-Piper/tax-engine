"""The Ontario take-home manifest's Schedule 8 line A: the months CPP applied.

Schedule 8 (form 5000-S8), Part 2: "Enter "12" on line A below unless any of the following
conditions apply". A salary-only caller meets none of conditions a) to h), so a request that
leaves the months out is read as 12, which `amount_by_count` needs (it refuses a blank count).
"""

from __future__ import annotations

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.registrations import JURISDICTIONS, artifact_kinds

LINE_A = "ca/cpp_months"
PRINTED_BASIS = 'Enter "12" on line A below unless any of the following conditions apply'


def test_a_request_that_leaves_out_the_months_is_read_as_twelve() -> None:
    kinds = artifact_kinds()
    source = YamlJurisdictionSource(JURISDICTIONS.roots(), kinds)
    (manifest,) = source.get_jurisdiction(JurisdictionCode("CA-ON")).manifests
    declaration = manifest.inputs[LINE_A]
    default = declaration.default_artifact(kinds.kind(LINE_A))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.value == 12
