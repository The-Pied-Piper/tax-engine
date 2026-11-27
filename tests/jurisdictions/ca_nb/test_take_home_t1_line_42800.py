"""T1 line 42800 (2025) reads NB428 line 97, over the real New Brunswick 2025 manifest.

Form text (Form NB428, CRA 5004-C, line 97): "Enter this amount on line 42800 of your return. New
Brunswick tax". The form supplies `ca/provincial_tax.amount`, and the federal T1 forms the real
manifest imports read it. Figures hand-computed on the ticket (blank claims are 0). New Brunswick is
not yet listed in the registrations, so the engine is built over the package list of `support.py`;
the same salary-only credit figures as the listed provinces' T1 tests are checked here for that
reason.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_nb.support import (
    new_brunswick_capabilities,
    new_brunswick_kinds,
    new_brunswick_packages,
    new_brunswick_parameter_parsers,
    new_brunswick_units,
)

D = Decimal
POLITICAL = "ca-nb/nb428_political_contribution_credit_line_92"


def _service() -> TaxComputationService:
    return TaxComputationService(
        YamlJurisdictionSource(
            new_brunswick_packages().roots(), new_brunswick_kinds(), new_brunswick_units()
        ),
        YamlParameterSource(
            new_brunswick_packages().roots(),
            new_brunswick_parameter_parsers(),
            new_brunswick_units(),
        ),
        new_brunswick_capabilities(),
    )


def _kind(identifier: str) -> AmountKind:
    kind = new_brunswick_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _sheet(form: str, salary: str, given: dict[str, str] | None = None) -> Worksheet:
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    artifacts += [Artifact(_kind(name), D(value)) for name, value in (given or {}).items()]
    worksheets = _service().compute(
        TaxCalculationRequest(JurisdictionCode("CA-NB"), 2025, tuple(artifacts))
    )
    (sheet,) = worksheets[form]
    return sheet


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    value = sheet.get(_kind(identifier)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("salary", "tax"), [("20000", "0.00"), ("30000", "798.76"), ("70000", "5676.89")]
)
def test_t1_line_42800_is_nb428_line_97(salary: str, tax: str) -> None:
    line_97 = _value(_sheet("ca-nb/nb428", salary), "ca-nb/nb428_new_brunswick_tax_line_97")
    line_42800 = _value(_sheet("ca/t1_tax_and_credits", salary), "ca/provincial_tax_line_42800")

    assert line_97 == D(tax)
    assert line_42800 == D(tax)


def test_a_claim_on_line_92_lowers_t1_line_42800() -> None:
    sheet = _sheet("ca/t1_tax_and_credits", "70000", {POLITICAL: "100.00"})

    assert _value(sheet, "ca/provincial_tax_line_42800") == D("5576.89")


def test_a_salary_only_caller_has_the_federal_credits_of_the_listed_provinces() -> None:
    sheet = _sheet("ca/t1_tax_and_credits", "70000")

    assert _value(sheet, "ca/cpp_base_contributions_line_87") == D("0.00")
    assert _value(sheet, "ca/credits_subtotal_line_96") == D("5840.23")
    assert _value(sheet, "ca/credit_amounts_line_106") == D("21969.23")
    assert _value(sheet, "ca/medical_claim") == D("0.00")
    assert _value(sheet, "ca/non_refundable_credit_amounts") == D("21969.23")
    assert _value(sheet, "ca/non_refundable_tax_credits") == D("3185.54")
    assert _value(sheet, "ca/credits_against_basic_federal_tax") == D("3185.54")


def test_the_t1_exports_the_three_parts_of_line_48200() -> None:
    sheet = _sheet("ca/t1_tax_and_credits", "20000")

    for identifier in (
        "ca/ei_overpayment_line_45000",
        "ca/cwb_line_45300",
        "ca/provincial_credits_line_47900",
    ):
        assert sheet.get(_kind(identifier)) is not None
