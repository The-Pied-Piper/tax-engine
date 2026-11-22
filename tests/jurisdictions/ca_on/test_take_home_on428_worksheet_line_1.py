"""Worksheet ON428 (ON428 line 72) line 1, from the real part.

Form text (Worksheet ON428, CRA 5006-d-25e.txt): "Line 1: Amount from line 11 of Part 5 of your
Form T691 multiplied by 24.63% =". Line 11 of Part 5 is the T691's export, totalled from that form
(the worksheet has no input of its own); the rate is the `ca-on/minimum_tax_rate` dataset, the
24.63% that line 59 prints too.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds
from tests.on428_worksheet_support import CODE, HEADER, steps

D = Decimal
PART_5_LINE_11_INPUT = "ca/t691_line_7_minus_line_10"
EXPORT = "ca/t691.t691_part_5_line_11_amount"
AMOUNT = "ca-on/on428_worksheet_t691_amount_line_1"
LINE_1 = "ca-on/on428_worksheet_basic_additional_tax_line_1"
PARTS = (*form_part_names("t691"), "on428_worksheet_line_1.yaml")
FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_1}
capabilities: []
"""


def _line_1(take_home_service: TakeHomeService, part_5_line_11: str | None) -> Decimal:
    kinds = bundled_kinds()
    given = []
    if part_5_line_11 is not None:
        given.append(Artifact(kinds.kind(PART_5_LINE_11_INPUT), D(part_5_line_11)))
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        TaxCalculationRequest(CODE, 2025, tuple(given))
    )["ca-on/on428"]
    value = sheet.get(kinds.kind(LINE_1)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("part_5_line_11", "expected"),
    [
        # 10,000.00 x 24.63% = 2,463.00.
        ("10000.00", "2463.00"),
        # 0.03 x 24.63% = 0.007389, rounded half-up to 0.01.
        ("0.03", "0.01"),
        # Left out: 0.
        (None, "0.00"),
    ],
)
def test_line_1_is_24_63_percent_of_part_5_line_11(
    take_home_service: TakeHomeService, part_5_line_11: str | None, expected: str
) -> None:
    assert _line_1(take_home_service, part_5_line_11) == D(expected)


def test_line_1_is_the_t691_part_5_line_11_total_then_the_rate_step() -> None:
    total, rate = steps("on428_worksheet_line_1.yaml")

    assert total["name"] == "core/record_total"
    assert total["consumes"] == {"records": EXPORT}
    assert total["produces"] == {"output": AMOUNT}
    assert rate["name"] == "core/apply_rate"
    assert rate["params"] == {"rate": "ca-on/minimum_tax_rate"}
    assert rate["consumes"] == {"base": AMOUNT}
    assert rate["produces"] == {"output": LINE_1}
