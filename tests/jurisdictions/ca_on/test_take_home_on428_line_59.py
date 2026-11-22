"""ON428 (2025) line 59, from the real part.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 59: Amount from line 40427 of your return
multiplied by 24.63% =". Line 40427 is the T1 lines copied by provinces input, totalled from that
form's export (line 59 has no input of its own); the rate is the `ca-on/minimum_tax_rate` dataset.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tests.federal_forms import form_part_names
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
LINE_59_AMOUNT = "ca-on/on428_minimum_tax_carryover_amount_line_59"
LINE_59 = "ca-on/on428_minimum_tax_carryover_limit_line_59"
LINE_40427 = "ca/minimum_tax_carryover"
EXPORT = "ca/t1_lines_copied_by_provinces.minimum_tax_carryover_line_40427"
PARTS = (*form_part_names("t1_lines_copied_by_provinces"), "on428_line_59.yaml")
FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_59}
capabilities: []
"""


def _steps(name: str) -> list[dict[str, Any]]:
    part = yaml.safe_load((ONTARIO_PARTS / name).read_text(encoding="utf-8"))
    assert part["form"] == {"name": "ca-on/on428"}
    assert "inputs" not in part
    return list(part["capabilities"])


def _line_59(take_home_service: TakeHomeService, line_40427: str | None) -> Decimal:
    kinds = bundled_kinds()
    given = []
    if line_40427 is not None:
        given.append(Artifact(kinds.kind(LINE_40427), D(line_40427)))
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(CODE, 2025, *given)["ca-on/on428"]
    value = sheet.get(kinds.kind(LINE_59)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_40427", "expected"),
    [
        # 1,000.00 x 24.63% = 246.30.
        ("1000.00", "246.30"),
        # 0.03 x 24.63% = 0.007389, rounded half-up to 0.01.
        ("0.03", "0.01"),
        # Left out: 0.
        (None, "0.00"),
    ],
)
def test_line_59_is_24_63_percent_of_line_40427(
    take_home_service: TakeHomeService, line_40427: str | None, expected: str
) -> None:
    assert _line_59(take_home_service, line_40427) == D(expected)


def test_line_59_is_the_t1_line_40427_total_then_the_rate_step() -> None:
    total, rate = _steps("on428_line_59.yaml")

    assert total["name"] == "core/record_total"
    assert total["consumes"] == {"records": EXPORT}
    assert total["produces"] == {"output": LINE_59_AMOUNT}
    assert rate["name"] == "core/apply_rate"
    assert rate["params"] == {"rate": "ca-on/minimum_tax_rate"}
    assert rate["consumes"] == {"base": LINE_59_AMOUNT}
    assert rate["produces"] == {"output": LINE_59}
