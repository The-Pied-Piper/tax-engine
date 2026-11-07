"""ON428 (2025) line 44, computed from the real part files through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 44 and line 58800: Line 35 plus line 43 =".
Line 44 is one sum, core/sum of line 35 (the credits with transfers,
`ca-on/on428_credits_with_transfers_line_35`) and line 43 (the medical expenses allowable,
`ca-on/on428_medical_expenses_line_43`, "Line 43 and line 58769: Line 41 plus line 42 ="). Line 35
comes from another part, so this test declares it as the one input of its header and loads the
take-home folder's `on428_line_44.yaml` and `on428_line_43_inputs.yaml` beside it. Line 43 is an
optional input: a salary-only caller has no medical expenses, so a request that leaves it out is
read as blank, and the line 44 part reads that blank as 0. The output is
`ca-on/on428_total_credit_amounts_line_44`, exported by the form.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.manifest import Manifest
from tax_engine.registrations import JURISDICTIONS, artifact_kinds
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds

D = Decimal
CODE = JurisdictionCode("CA-ON")
LINE_35 = "ca-on/on428_credits_with_transfers_line_35"
LINE_43 = "ca-on/on428_medical_expenses_line_43"
LINE_44 = "ca-on/on428_total_credit_amounts_line_44"
PRINTED_BASIS = "Line 41 plus line 42"
PART = "on428_line_44.yaml"
INPUTS_PART = "on428_line_43_inputs.yaml"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_35}
    required: true
outputs:
  - {LINE_35}
capabilities: []
"""

FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_44}
capabilities: []
"""


def _line_44(take_home_service: TakeHomeService, line_35: str, line_43: str | None) -> Decimal:
    kinds = bundled_kinds()
    given = [Artifact(kinds.kind(LINE_35), D(line_35))]
    if line_43 is not None:
        given.append(Artifact(kinds.kind(LINE_43), D(line_43)))
    worksheet = take_home_service(HEADER, FORM, PART, INPUTS_PART).compute(CODE, 2025, *given)[
        "ca-on/on428"
    ][0]
    value = worksheet.get(kinds.kind(LINE_44)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_35", "line_44"),
    [
        # A $20,000 salary: line 35 is 13,891.75 and line 43 is blank (0), so line 44 is 13,891.75.
        ("13891.75", "13891.75"),
        # A $70,000 salary: line 35 is 17,116.23 and line 43 is blank (0), so line 44 is 17,116.23.
        ("17116.23", "17116.23"),
        # A $150,000 salary: line 35 is 17,180.58 and line 43 is blank (0), so line 44 is 17,180.58.
        ("17180.58", "17180.58"),
    ],
)
def test_line_44_is_line_35_when_line_43_is_left_out(
    take_home_service: TakeHomeService, line_35: str, line_44: str
) -> None:
    assert _line_44(take_home_service, line_35, None) == D(line_44)


def test_line_44_is_line_35_plus_line_43(take_home_service: TakeHomeService) -> None:
    # Line 35 is 17,116.23 and line 43 is 1,000.00, so line 44 is 18,116.23.
    assert _line_44(take_home_service, "17116.23", "1000.00") == D("18116.23")


def _manifest(take_home_service: TakeHomeService, tmp_path: Path) -> Manifest:
    """The temporary take-home folder the shared builder writes, loaded as a manifest."""
    take_home_service(HEADER, FORM, PART, INPUTS_PART)
    folder = tmp_path / "manifests" / "take_home"
    return YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds()).load(folder)


def test_a_request_that_leaves_out_line_43_is_read_as_blank(
    take_home_service: TakeHomeService, tmp_path: Path
) -> None:
    kinds = artifact_kinds()
    declaration = _manifest(take_home_service, tmp_path).inputs[LINE_43]
    default = declaration.default_artifact(kinds.kind(LINE_43))
    assert not declaration.required
    assert declaration.basis is not None and PRINTED_BASIS in declaration.basis
    assert default is not None and default.is_blank
