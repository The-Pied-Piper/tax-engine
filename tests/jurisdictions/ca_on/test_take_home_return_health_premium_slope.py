"""The Return summary's health premium slope: the rate of the ON428 line 89 chart row (step 5 of 7
of the marginal-rate series), from the real `ca-on/health_premium_rows` dataset through the real
engine.

Form text (Form ON428, CRA 5006-c-25e.txt, docs/cra-forms-2025/5006-c-25e.txt): line 89 "Ontario
health premium (complete the chart below)"; the chart's rows are each a flat amount or a sloped
amount (the income over a threshold, times 6% or 25%, plus an amount). The slope is the printed
rate of the row the taxable income falls in, and 0 for a flat row. No new figure is printed: the
rates are in the dataset (`ca-on/health_premium_rows`, 2025.yaml). Rows that carry a rate: 6% from
20,000 to 25,000 and from 36,000 to 38,500; 25% from 48,000 to 48,600, from 72,000 to 72,600 and
from 200,000 to 200,600. A base exactly at a row's start falls in the lower row, as `band_for` does.

The Return summary (the default form of the 2025 manifest, `return.yaml`) takes two steps, neither
an export: (a) `core/record_total` of `ca/t1_taxable_income.taxable_income` into
`ca-on/return_taxable_income`, and (b) `core/amount_by_band_rate` over that and the dataset into
`ca-on/return_health_premium_slope`. The edge figures are run with the taxable income given
directly (as test_take_home_on428_line_5.py does) and step (b) written in a test-local form; one
test runs the real manifest from the salary and reads the two figures from the Return summary's
trace, since neither is exported.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.trace import AmountByBandRateLine, RecordTotalLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import (
    TAKE_HOME,
    TakeHomeService,
    header_without_imports,
)
from tests.kinds import bundled_kinds

D = Decimal
CODE = JurisdictionCode("CA-ON")
FORM_NAME = "ca-on/return_health_premium_slope_test"
TAXABLE_INCOME = "ca-on/return_taxable_income"
SLOPE = "ca-on/return_health_premium_slope"
ROWS = "ca-on/health_premium_rows"

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {TAXABLE_INCOME}
    required: true
outputs:
  - {TAXABLE_INCOME}
capabilities: []
"""

FORM = f"""\
form:
  name: {FORM_NAME}
  required: true
  exports:
    - {SLOPE}
capabilities:
  - name: core/amount_by_band_rate
    parameters:
      table: {ROWS}
    consumes:
      base: {TAXABLE_INCOME}
    produces:
      output: {SLOPE}
"""


def _slope(take_home_service: TakeHomeService, taxable_income: str) -> Decimal:
    kinds = bundled_kinds()
    given = [Artifact(kinds.kind(TAXABLE_INCOME), D(taxable_income))]
    worksheet = take_home_service(HEADER, FORM).compute(CODE, 2025, *given)[FORM_NAME][0]
    value = worksheet.get(kinds.kind(SLOPE)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("taxable_income", "expected"),
    [
        # Inside each sloped row.
        ("22000.00", "0.06"),
        ("37000.00", "0.06"),
        ("48300.00", "0.25"),
        ("72300.00", "0.25"),
        ("200300.00", "0.25"),
    ],
)
def test_the_slope_is_the_rate_of_the_sloped_row_the_taxable_income_falls_in(
    take_home_service: TakeHomeService, taxable_income: str, expected: str
) -> None:
    assert _slope(take_home_service, taxable_income) == D(expected)


@pytest.mark.parametrize(
    "taxable_income",
    [
        # The $20,000 salary (19,835.00), the $70,000 salary (69,335.00, a flat $600 row) and the
        # $150,000 salary (148,926.00): flat rows.
        "0.00",
        "19835.00",
        "30000.00",
        "42000.00",
        "69335.00",
        "148926.00",
        "250000.00",
    ],
)
def test_the_slope_in_a_flat_row_is_zero(
    take_home_service: TakeHomeService, taxable_income: str
) -> None:
    assert _slope(take_home_service, taxable_income) == D("0")


@pytest.mark.parametrize(
    ("taxable_income", "expected"),
    [
        # A base exactly at a row's start is in the lower row.
        ("20000.00", "0"),  # the flat row below the 6% row
        ("25000.00", "0.06"),  # the end of the 6% row: still in it
        ("36000.00", "0"),
        ("38500.00", "0.06"),
        ("48000.00", "0"),
        ("48600.00", "0.25"),
        ("72000.00", "0"),
        ("72600.00", "0.25"),  # the 25% row 72,000-72,600 ends here: still in it
        ("200000.00", "0"),
        ("200600.00", "0.25"),
        # One cent above a start is in the sloped row; one cent above an end is in the flat row.
        ("20000.01", "0.06"),
        ("72000.01", "0.25"),
        ("72600.01", "0"),
        ("200600.01", "0"),
    ],
)
def test_the_slope_at_a_row_edge_is_the_rate_of_the_lower_row(
    take_home_service: TakeHomeService, taxable_income: str, expected: str
) -> None:
    assert _slope(take_home_service, taxable_income) == D(expected)


# --- the real Return summary, from the salary ---------------------------------------------------

RETURN = (TAKE_HOME / "return.yaml").read_text(encoding="utf-8")
PARTS = (
    "salary.yaml",
    *(
        part.name
        for part in sorted(TAKE_HOME.rglob("*.yaml"))
        if part.name not in {"manifest.yaml", "return.yaml", "salary.yaml"}
    ),
)


def _return_summary(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    worksheets = take_home_service(header_without_imports(), RETURN, *PARTS).compute(
        CODE, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (summary,) = worksheets["ca-on/return"]
    return summary


@pytest.mark.parametrize(
    ("salary", "taxable_income", "slope"),
    [
        # $70,000: taxable income 69,335.00 is in a flat $600 row, so the slope is 0.
        ("70000", "69335.00", "0"),
        # $20,000: 19,835.00 is in the flat row "$20,000 or less", so 0.
        ("20000", "19835.00", "0"),
        # $150,000: 148,926.00 is in the flat $750 row, so 0.
        ("150000", "148926.00", "0"),
    ],
)
def test_the_real_return_summary_takes_the_taxable_income_and_its_slope_as_steps(
    take_home_service: TakeHomeService, salary: str, taxable_income: str, slope: str
) -> None:
    kinds = bundled_kinds()
    summary = _return_summary(take_home_service, salary)

    totals = [
        line
        for line in summary.trace
        if isinstance(line, RecordTotalLine) and line.output == kinds.kind(TAXABLE_INCOME)
    ]
    slopes = [
        line
        for line in summary.trace
        if isinstance(line, AmountByBandRateLine) and line.output == kinds.kind(SLOPE)
    ]
    assert [line.total for line in totals] == [D(taxable_income)]
    assert [line.result for line in slopes] == [D(slope)]
    assert [line.base_amount for line in slopes] == [D(taxable_income)]
    assert summary.get(kinds.kind(TAXABLE_INCOME)).value == D(taxable_income)
    assert summary.get(kinds.kind(SLOPE)).value == D(slope)
