"""ON428 (2025) line 58, from the real part.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 58: Line 56 minus line 57 (if negative, enter
"0") =". Lines 56 and 57 are declared as inputs of a test-local form (line 57 is the dividend tax
credit worksheet's result, always computed).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.application.models.calculation_request import TaxCalculationRequest
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
LINE_56 = "ca-on/on428_tax_minus_credits_line_56"
LINE_57 = "ca-on/on428_dividend_tax_credit_line_57"
LINE_58 = "ca-on/on428_tax_minus_dividend_tax_credit_line_58"
PARTS = ("on428_line_58.yaml",)
FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_58}
inputs:
  - name: {LINE_56}
    required: true
  - name: {LINE_57}
    required: true
capabilities: []
"""


def _steps(name: str) -> list[dict[str, Any]]:
    part = yaml.safe_load((ONTARIO_PARTS / name).read_text(encoding="utf-8"))
    assert part["form"] == {"name": "ca-on/on428"}
    assert "inputs" not in part
    return list(part["capabilities"])


def _line_58(take_home_service: TakeHomeService, line_56: str, line_57: str) -> Decimal:
    kinds = bundled_kinds()
    given = [
        Artifact(kinds.kind(LINE_56), D(line_56)),
        Artifact(kinds.kind(LINE_57), D(line_57)),
    ]
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        TaxCalculationRequest(CODE, 2025, tuple(given))
    )["ca-on/on428"]
    value = sheet.get(kinds.kind(LINE_58)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_56", "line_57", "expected"),
    [
        # 2,000.00 minus 500.00.
        ("2000.00", "500.00", "1500.00"),
        # 2,000.00 minus 1,950.00.
        ("2000.00", "1950.00", "50.00"),
        # Line 57 above line 56: not below zero.
        ("300.00", "1000.00", "0.00"),
        # No dividend tax credit.
        ("3311.45", "0.00", "3311.45"),
    ],
)
def test_line_58_is_line_56_minus_line_57_not_below_zero(
    take_home_service: TakeHomeService, line_56: str, line_57: str, expected: str
) -> None:
    assert _line_58(take_home_service, line_56, line_57) == D(expected)


def test_line_58_is_one_subtract_not_below_zero_step() -> None:
    (step,) = _steps("on428_line_58.yaml")

    assert step["name"] == "core/subtract_not_below_zero"
    assert step["reference"] == "58"
    assert step["consumes"] == {"amount": LINE_56, "less": LINE_57}
    assert "blank" not in step
    assert step["produces"] == {"output": LINE_58}
