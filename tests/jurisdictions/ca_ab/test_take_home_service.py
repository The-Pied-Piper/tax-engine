"""The Alberta `take_home_service` fixture (`conftest.py`) builds the engine over a temporary
Alberta manifest of a test header, a form declaration and real part files.

This module exercises it with one real Alberta part, AB428 line 5 (`ab428_credits_line_5.yaml`),
as `test_take_home_ab428_credits_line_5.py` does over the Alberta package list of `support.py`:
here the kinds, units, capabilities and parameter parsers are the ones `tax_engine.registrations`
builds, so Alberta must be listed there. Form text (Form AB428, CRA 5009-c-25e.txt): "Line 5:
Rate 8%", "Line 5: Rate 10%" and "Line 5: Rate 12%"; line 5 is the printed rate of the column that
line 1 (the taxable income) falls in. Line 1 is given directly: 19,835.00 and 69,335.00 are the
taxable incomes at salaries of 20,000 and 70,000 (hand-computed, as in that test).
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ab.conftest import TakeHomeService
from tests.kinds import bundled_kinds

D = Decimal
LINE_1 = "ca-ab/ab428_taxable_income_line_1"
LINE_5 = "ca-ab/ab428_bracket_rate_line_5"
HEADER = dedent(f"""\
    jurisdiction: CA-AB
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: {LINE_1}
        required: true
    outputs:
      - {LINE_1}
    capabilities: []
    """)
FORM = dedent(f"""\
    form:
      name: ca-ab/ab428_credits
      required: true
      exports:
        - {LINE_5}
    capabilities: []
    """)


def _amount_kind(identifier: str) -> AmountKind:
    kind = bundled_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


@pytest.mark.parametrize(("line_1", "expected"), [("19835.00", "0.08"), ("69335.00", "0.10")])
def test_the_fixture_computes_a_real_alberta_part(
    take_home_service: TakeHomeService, line_1: str, expected: str
) -> None:
    service = take_home_service(HEADER, FORM, "ab428_credits_line_5.yaml")

    worksheets = service.compute(
        JurisdictionCode("CA-AB"), 2025, Artifact(_amount_kind(LINE_1), D(line_1))
    )

    (sheet,) = worksheets["ca-ab/ab428_credits"]
    assert sheet.get(_amount_kind(LINE_5)).value == D(expected)
