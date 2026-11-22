"""ON428 (2025) line 28, as the Ontario take-home manifest part wires it.

Form text (ON428, CRA 5006-c-25e.txt): "Line 28: Line 26 plus line 27 =".
Line 26 is "Amount from line 25 of the previous page", a copy of line 25, so it has no capability of
its own: the part reads line 25 directly. Line 27 is "Line 27 and line 58360: Pension income amount
(maximum $1,762)", an optional input with blank fallback 0 (on428_line_27_inputs.yaml), rejected
above the maximum by on428_line_27.yaml. Line 28 is one core/sum over line 25 then the line 27
step's output, `ca-on/on428_pension_income_amount_line_27`.

Line 25 is `ca-on/on428_credits_subtotal_line_25` (produced by another ticket), a plain starting
input here. The header and the form's export are made up here, because the shared scaffold owns
them.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest
import yaml

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca_on.catalog import (
    ON428_CREDITS_SUBTOTAL_LINE_25,
    ON428_CREDITS_WITH_PENSION_LINE_28,
    ON428_PENSION_INCOME_AMOUNT,
)
from tests.jurisdictions.ca_on.conftest import ONTARIO_PARTS, TakeHomeService

D = Decimal
PART = "on428_line_28.yaml"
INPUTS_PART = "on428_line_27_inputs.yaml"
LINE_27_PART = "on428_line_27.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    """)
FORM = dedent("""\
    form:
      name: ca-on/on428
      required: true
      exports:
        - ca-on/on428_credits_with_pension_line_28
    inputs:
      - name: ca-on/on428_credits_subtotal_line_25
        required: true
    """)


def line_28(
    take_home_service: TakeHomeService, line_25: str, pension: str | None = None
) -> Decimal:
    artifacts = [Artifact(ON428_CREDITS_SUBTOTAL_LINE_25, D(line_25))]
    if pension is not None:
        artifacts.append(Artifact(ON428_PENSION_INCOME_AMOUNT, D(pension)))
    worksheets = take_home_service(HEADER, FORM, PART, INPUTS_PART, LINE_27_PART).compute(
        TaxCalculationRequest(JurisdictionCode("CA-ON"), 2025, tuple(artifacts))
    )
    (sheet,) = worksheets["ca-on/on428"]
    return sheet.get(ON428_CREDITS_WITH_PENSION_LINE_28).value


@pytest.mark.parametrize(
    ("line_25", "expected"),
    [
        # Worked figures, computed by hand from the printed form (not a CRA example).
        ("13891.75", "13891.75"),
        ("17180.58", "17180.58"),
    ],
)
def test_line_28_is_line_25_when_the_pension_amount_is_left_out(
    take_home_service: TakeHomeService, line_25: str, expected: str
) -> None:
    assert line_28(take_home_service, line_25) == D(expected)


def test_line_28_adds_the_pension_amount_to_line_25(take_home_service: TakeHomeService) -> None:
    assert line_28(take_home_service, "17116.23", "1762") == D("18878.23")


def test_line_28_reads_the_line_27_step_so_an_amount_above_the_maximum_is_rejected(
    take_home_service: TakeHomeService,
) -> None:
    with pytest.raises(InputAboveBoundError):
        line_28(take_home_service, "17116.23", "1762.01")


def test_line_28_consumes_the_line_27_kind_not_the_input_kind() -> None:
    part = yaml.safe_load((ONTARIO_PARTS / PART).read_text(encoding="utf-8"))

    (step,) = part["capabilities"]
    assert step["consumes"]["parts"] == [
        "ca-on/on428_credits_subtotal_line_25",
        "ca-on/on428_pension_income_amount_line_27",
    ]
