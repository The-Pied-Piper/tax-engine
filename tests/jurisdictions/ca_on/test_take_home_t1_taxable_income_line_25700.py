"""T1 line 68 and line 25700 "Add lines 58 to 67.", from the Ontario take-home manifest's part file.

Three `core/sum` steps add the ten printed lines 24400 to 25600: two unprinted subtotals of five,
each line read as 0 when the caller leaves it out, and the printed line adding the two, rounded
half-up to the cent. The part is composed here under a test-local header and form declaration with
the inputs part that declares the ten lines. The expected figures
are hand-added from the printed lines, not a CRA example.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.taxable_income import (
    DEDUCTIONS_FROM_NET_INCOME,
    T1_LINE_24400,
    T1_LINE_25100,
    T1_LINE_25400,
    T1_LINE_25500,
    T1_LINE_25600,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
PARTS = ("t1_taxable_income_line_25700_inputs.yaml", "t1_taxable_income_line_25700.yaml")
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: [ca/t1_line_25400]
capabilities: []
"""
FORM = """\
form:
  name: ca/t1_taxable_income
  required: true
  exports:
    - ca/deductions_from_net_income
"""


def line_25700(take_home_service: TakeHomeService, *given: Artifact[Decimal]) -> Decimal:
    service = take_home_service(HEADER, FORM, *PARTS)
    (worksheet,) = service.compute(ONTARIO, 2025, *given)["ca/t1_taxable_income"]
    return worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value


def test_a_salary_only_caller_has_no_deductions_from_net_income(
    take_home_service: TakeHomeService,
) -> None:
    assert line_25700(take_home_service) == D("0.00")


def test_line_25700_adds_the_lines_the_caller_gives(take_home_service: TakeHomeService) -> None:
    given = (Artifact(T1_LINE_25400, D("1000")), Artifact(T1_LINE_25100, D("250.50")))

    assert line_25700(take_home_service, *given) == D("1250.50")


def test_line_25700_adds_the_first_and_the_last_line(take_home_service: TakeHomeService) -> None:
    given = (Artifact(T1_LINE_24400, D("300")), Artifact(T1_LINE_25600, D("0.25")))

    assert line_25700(take_home_service, *given) == D("300.25")


@pytest.mark.parametrize(("amount", "expected"), [("10.005", "10.01"), ("10.004", "10.00")])
def test_the_printed_line_is_rounded_half_up_to_the_cent(
    take_home_service: TakeHomeService, amount: str, expected: str
) -> None:
    given = Artifact(T1_LINE_25500, D(amount))

    assert line_25700(take_home_service, given) == D(expected)
