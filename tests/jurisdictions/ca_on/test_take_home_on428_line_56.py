"""ON428 (2025) line 56, from the real part.

Form text (Form ON428, CRA 5006-c-25e.txt, "Ontario minimum tax carryover:"): "Line 56: Enter the
amount from line 53 above." Line 53 is declared as an input of a test-local form.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tests.jurisdictions.ca_on.conftest import ONTARIO_PARTS, TakeHomeService
from tests.kinds import bundled_kinds

D = Decimal
CODE = JurisdictionCode("CA-ON")
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""
LINE_53 = "ca-on/on428_tax_minus_credits_line_53"
LINE_56 = "ca-on/on428_tax_minus_credits_line_56"
PARTS = ("on428_line_56.yaml",)
FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_56}
inputs:
  - name: {LINE_53}
    required: true
capabilities: []
"""


def _steps(name: str) -> list[dict[str, Any]]:
    part = yaml.safe_load((ONTARIO_PARTS / name).read_text(encoding="utf-8"))
    assert part["form"] == {"name": "ca-on/on428"}
    assert "inputs" not in part
    return list(part["capabilities"])


def test_line_56_is_the_amount_from_line_53(take_home_service: TakeHomeService) -> None:
    kinds = bundled_kinds()
    given = Artifact(kinds.kind(LINE_53), D("3311.45"))

    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(CODE, 2025, given)["ca-on/on428"]

    assert sheet.get(kinds.kind(LINE_56)).value == D("3311.45")


def test_line_56_reads_line_53_and_produces_its_own_kind() -> None:
    (step,) = _steps("on428_line_56.yaml")

    assert step["reference"] == "56"
    assert step["unit"] == "ca/cad"
    assert LINE_53 in str(step["consumes"])
    assert step["produces"] == {"output": LINE_56}
