"""The British Columbia `take_home_service` fixture (`conftest.py`) builds the engine over a
temporary British Columbia manifest of a test header, a form declaration and real part files.

This module exercises it with one real British Columbia part, BC428 line 5 (`bc428_line_5.yaml`),
as `test_take_home_bc428_line_5.py` does over the British Columbia package list of `support.py`:
here the kinds, units, capabilities and parameter parsers are the ones `tax_engine.registrations`
builds, so British Columbia must be listed there. Form text (Form BC428, CRA 5010-c): "Line 5:
Rate 5.06%", "Line 5: Rate 7.7%", "Line 5: Rate 10.5%" and "Line 5: Rate 12.29%"; line 5 is the
printed rate of the column that line 1 (the taxable income) falls in. Line 1 is given directly:
19,835.00 and 69,335.00 are the taxable incomes at salaries of 20,000 and 70,000 (hand-computed, as
in that test), so the rates are 0.0506 and 0.077.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_bc.conftest import TakeHomeService
from tests.kinds import bundled_kinds

D = Decimal
LINE_1 = "ca-bc/bc428_taxable_income_line_1"
LINE_5 = "ca-bc/bc428_bracket_rate_line_5"
HEADER = dedent(f"""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - {LINE_1}
    capabilities: []
    """)
FORM = dedent(f"""\
    form:
      name: ca-bc/bc428
      required: true
      exports:
        - {LINE_5}
    capabilities: []
    # Line 1 is the caller's, owned by this form, whose line 5 step reads it.
    inputs:
      - name: {LINE_1}
        required: true
    """)


def _amount_kind(identifier: str) -> AmountKind:
    kind = bundled_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


@pytest.mark.parametrize(("line_1", "expected"), [("19835.00", "0.0506"), ("69335.00", "0.077")])
def test_the_fixture_computes_a_real_british_columbia_part(
    take_home_service: TakeHomeService, line_1: str, expected: str
) -> None:
    service = take_home_service(HEADER, FORM, "bc428_line_5.yaml")

    worksheets = service.compute(
        JurisdictionCode("CA-BC"), 2025, Artifact(_amount_kind(LINE_1), D(line_1))
    )

    (sheet,) = worksheets["ca-bc/bc428"]
    assert sheet.get(_amount_kind(LINE_5)).value == D(expected)
