"""The Newfoundland and Labrador forms export the lines the return summary's marginal rate reads.

Through the engine over the real manifest folder (the `service` fixture; Newfoundland and Labrador
is not yet registered): the NL428 form holds the line 101, line 104 and line 105 figures it
exports, the credits form holds the line 5 and line 12 rates, and the return summary holds
the marginal rate. The export lists themselves are pinned in `test_form_nl428.py` and
`test_form_nl428_credits.py`.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_nl.support import newfoundland_kinds

D = Decimal


def _sheet(service: TaxComputationService, salary: str, form: str) -> Worksheet:
    worksheets = service.compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-NL"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (sheet,) = worksheets[form]
    return sheet


def _value(sheet: Worksheet, name: str) -> Decimal:
    kind = newfoundland_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def test_the_return_summary_holds_each_of_its_three_outputs(
    service: TaxComputationService,
) -> None:
    sheet = _sheet(service, "70000", "ca-nl/return")

    for name in (
        "ca/refund_or_balance_owing",
        "ca-nl/average_tax_rate",
        "ca-nl/marginal_tax_rate",
    ):
        assert isinstance(_value(sheet, name), Decimal)


@pytest.mark.parametrize(
    ("salary", "line_5", "line_12"),
    [("70000", "0.145", None), ("250000", None, "0.198")],
)
def test_the_credits_form_exports_the_line_5_and_line_12_rates(
    service: TaxComputationService, salary: str, line_5: str | None, line_12: str | None
) -> None:
    # Line 5 is the rate of table 1 (taxable income up to 220,910) and line 12 of table 2 (above
    # it); the one that does not apply is blank, which the sheet may hold as nothing or as 0.
    sheet = _sheet(service, salary, "ca-nl/nl428_credits")

    for name, expected in (
        ("ca-nl/nl428_bracket_rate_line_5", line_5),
        ("ca-nl/nl428_bracket_rate_line_12", line_12),
    ):
        if expected is not None:
            assert _value(sheet, name) == D(expected)


@pytest.mark.parametrize(
    ("salary", "line_101", "line_104", "line_105"),
    [
        ("20000", "0.00", "997.00", "0.00"),
        ("28000", "3827.00", "384.68", "921.72"),
    ],
)
def test_the_nl428_form_exports_lines_101_104_and_105(
    service: TaxComputationService, salary: str, line_101: str, line_104: str, line_105: str
) -> None:
    sheet = _sheet(service, salary, "ca-nl/nl428")

    assert _value(sheet, "ca-nl/nl428_line_101") == D(line_101)
    assert _value(sheet, "ca-nl/nl428_line_104") == D(line_104)
    assert _value(sheet, "ca-nl/nl428_newfoundland_and_labrador_tax_line_105") == D(line_105)
