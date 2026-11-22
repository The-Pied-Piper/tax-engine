"""ON428 (2025) line 60, from the real part.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 60 and line 61540: Enter whichever is less:
amount from line 58 or line 59." Lines 58 and 59 are declared as inputs of a test-local form; the
output is the existing `ca-on/on428_minimum_tax_carryover_line_60` kind.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
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
LINE_58 = "ca-on/on428_tax_minus_dividend_tax_credit_line_58"
LINE_59 = "ca-on/on428_minimum_tax_carryover_limit_line_59"
LINE_60 = "ca-on/on428_minimum_tax_carryover_line_60"
PARTS = ("on428_line_60.yaml",)
FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_60}
inputs:
  - name: {LINE_58}
    required: true
  - name: {LINE_59}
    required: true
capabilities: []
"""


def _steps(name: str) -> list[dict[str, Any]]:
    part = yaml.safe_load((ONTARIO_PARTS / name).read_text(encoding="utf-8"))
    assert part["form"] == {"name": "ca-on/on428"}
    assert "inputs" not in part
    return list(part["capabilities"])


@pytest.mark.parametrize(
    ("line_58", "line_59", "expected"),
    [
        # Line 58 less than line 59.
        ("50.00", "246.30", "50.00"),
        # Line 59 less than line 58.
        ("1500.00", "246.30", "246.30"),
        # Both 0.
        ("0.00", "0.00", "0.00"),
    ],
)
def test_line_60_is_the_lesser_of_lines_58_and_59(
    take_home_service: TakeHomeService, line_58: str, line_59: str, expected: str
) -> None:
    kinds = bundled_kinds()
    given = [Artifact(kinds.kind(LINE_58), D(line_58)), Artifact(kinds.kind(LINE_59), D(line_59))]

    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(CODE, 2025, *given)["ca-on/on428"]

    assert sheet.get(kinds.kind(LINE_60)).value == D(expected)


def test_line_60_is_one_lesser_of_step_under_the_existing_kind() -> None:
    (step,) = _steps("on428_line_60.yaml")

    assert step["name"] == "core/lesser_of"
    assert step["title"] == "Ontario minimum tax carryover"
    assert step["reference"] == "60"
    assert step["consumes"] == {"amounts": [LINE_58, LINE_59]}
    assert step["produces"] == {"output": LINE_60}
