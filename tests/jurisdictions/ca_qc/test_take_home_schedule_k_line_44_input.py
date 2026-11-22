"""The Schedule K line 44 input (2025), as the Quebec take-home manifest part declares it.

Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part A, line 44: "If you did not have a spouse on
December 31, 2025, but you had a dependent child (see line 447 in the guide for the definition),
enter $12,350. If you had more than one dependent child, enter $16,570." The form asks whether the
filer had a dependent child and whether more than one, so the input is the number of dependent
children, a count, left blank by a salary-only caller; line 44 reads the blank as 0.

The real part is loaded under a test-local header and form declaration over the Quebec package list
of `support.py`.
"""

from __future__ import annotations

from pathlib import Path

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.kinds import CountKind
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_K_DEPENDENT_CHILDREN_LINE_44
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds, quebec_packages, quebec_units
from tests.kinds import non_negative
from tests.manifest_support import input_named

IDENTIFIER = SCHEDULE_K_DEPENDENT_CHILDREN_LINE_44.identifier
PART = "tp1_schedule_k_line_44_input.yaml"
PRINTED_BASIS = (
    "If you did not have a spouse on December 31, 2025, but you had a dependent child "
    "(see line 447 in the guide for the definition), enter $12,350. If you had more than one "
    "dependent child, enter $16,570."
)
HEADER = """\
jurisdiction: CA-QC
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""
FORM = f"""\
form:
  name: ca-qc/tp1_schedule_k
  required: true
  exports:
    - {IDENTIFIER}
capabilities: []
"""


def _manifest(take_home_service: TakeHomeService, tmp_path: Path) -> Manifest:
    take_home_service(HEADER, FORM, PART)
    folder = tmp_path / "manifests" / "2025"
    return YamlJurisdictionSource(quebec_packages().roots(), quebec_kinds(), quebec_units()).load(
        folder
    )


def test_the_part_declares_the_count_as_optional_and_blank(
    take_home_service: TakeHomeService, tmp_path: Path
) -> None:
    declaration = input_named(_manifest(take_home_service, tmp_path), IDENTIFIER)
    default = declaration.default_artifact(quebec_kinds().kind(IDENTIFIER))

    assert IDENTIFIER == "ca-qc/schedule_k_dependent_children_line_44"
    assert not declaration.required
    assert declaration.reference == "44"
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank


def test_the_count_is_a_registered_non_negative_count() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is SCHEDULE_K_DEPENDENT_CHILDREN_LINE_44
    assert isinstance(kind, CountKind)
    assert non_negative(kind)
