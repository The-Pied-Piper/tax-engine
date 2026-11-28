"""BC479 (2025 and 2026) line 9, the basic sales tax credit, over the optional year of birth.

Form text (Form BC479, CRA 5010-TC, read 2026-11-14): "Line 9 and line 60330: Basic sales tax
credit Claim $75". The amount is the `ca-bc/sales_tax_credit_basic` dataset, claimed through
core/credit_amount.

The form prints no age condition. The BC guide, CRA 5010-PC (Form BC479, Sales tax credit): "You
can claim this credit if, on December 31, 2025, you were a resident of British Columbia and you
met any of the following conditions: You were 19 years of age or older / You had a spouse or
common-law partner / You were a parent of a child". The engine models a filer with no spouse or
child, so a filer under 19 at the end of the year has no credit: line 9 is 0.00. The year of birth
is the T1's optional `ca/birth_year`; a request that leaves it out claims the credit in full. The
cutoff year is 2006 for 2025 and 2007 for 2026 (age 19 on 31 December; 2026 is provisional).

The test composes the real line 9 part and the T1's copied-lines form beside a test-local header
and form declaration, and types in only, in some tests, the year of birth.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest
import yaml

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tax_engine.jurisdictions.ca_bc.catalog import BC479_BASIC_SALES_TAX_CREDIT_LINE_9
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_bc.conftest import BC_PARTS, TakeHomeService
from tests.jurisdictions.ca_bc.support import british_columbia_kinds
from tests.kinds import non_negative

D = Decimal
FORM_NAME = "ca-bc/bc479"
PARTS = (*form_part_names("t1_lines_copied_by_provinces"), "bc479_line_9.yaml")
HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-bc/bc479
      required: true
      exports:
        - ca-bc/bc479_basic_sales_tax_credit_line_9
    """)


def _line_9(take_home_service: TakeHomeService, year: int, birth_year: int | None) -> Decimal:
    given = () if birth_year is None else (Artifact(BIRTH_YEAR, birth_year),)
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        TaxCalculationRequest(JurisdictionCode("CA-BC"), year, given)
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet.get(BC479_BASIC_SALES_TAX_CREDIT_LINE_9).value


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize("birth_year", [None, 1980, 1955, 1990])
def test_line_9_is_the_printed_claim_when_19_or_older_or_the_year_is_left_out(
    take_home_service: TakeHomeService, year: int, birth_year: int | None
) -> None:
    assert _line_9(take_home_service, year, birth_year) == D("75.00")


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize("age", [0, 5, 16, 17, 18])
def test_line_9_is_zero_when_under_19_at_the_end_of_the_year(
    take_home_service: TakeHomeService, year: int, age: int
) -> None:
    assert _line_9(take_home_service, year, year - age) == D("0.00")


@pytest.mark.parametrize(
    ("year", "birth_year", "expected"),
    [
        (2025, 2006, "75.00"),
        (2025, 2007, "0.00"),
        (2026, 2007, "75.00"),
        (2026, 2008, "0.00"),
    ],
)
def test_the_cutoff_year_moves_with_the_tax_year(
    take_home_service: TakeHomeService, year: int, birth_year: int, expected: str
) -> None:
    assert _line_9(take_home_service, year, birth_year) == D(expected)


def test_the_part_reads_the_flag_claims_the_dataset_figure_and_multiplies_them() -> None:
    part = yaml.safe_load((BC_PARTS / "bc479_line_9.yaml").read_text(encoding="utf-8"))

    assert part["form"] == {"name": FORM_NAME}
    flag, claim, line = part["capabilities"]
    assert flag["name"] == "core/first_record_count"
    assert flag["consumes"] == {"records": "ca/t1_lines_copied_by_provinces.age_19_or_older"}
    assert flag["produces"] == {"output": "ca-bc/bc479_age_19_or_older"}
    assert claim["name"] == "core/credit_amount"
    assert claim["params"] == {"amount": "ca-bc/sales_tax_credit_basic"}
    assert claim["produces"] == {"output": "ca-bc/bc479_basic_sales_tax_credit_claim_line_9"}
    assert line["name"] == "core/times_count"
    assert line["title"] == "Basic sales tax credit"
    assert line["reference"] == "9"
    assert line["blank"] == {"count": "1"}
    assert line["produces"] == {"output": "ca-bc/bc479_basic_sales_tax_credit_line_9"}


def test_the_basic_sales_tax_credit_is_a_non_negative_amount_kind() -> None:
    kind = british_columbia_kinds().kind("ca-bc/bc479_basic_sales_tax_credit_line_9")

    assert kind is BC479_BASIC_SALES_TAX_CREDIT_LINE_9
    assert non_negative(kind)
