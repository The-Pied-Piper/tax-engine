"""T1 (5006-R, 2025) line 48200 "Total credits": the three parts the form adds are exported, so a
caller can list each by its title and line.

Form text (T1 General 5006-R, CRA 5006-R-25E.txt, page 8): "Line 166 and line 48200: Add lines 150
to 165. Total credits", with line 153 and line 45000 "Employment insurance (EI) overpayment", line
155 and line 45300 "Canada workers benefit (CWB)" and line 165 and line 47900 "Provincial or
territorial credits".

The real bundled manifest of each province but Quebec (which has its own T1) is run from a salary.
The form's exports include the three kinds; the figures are the ones the form's own steps produce.
Line 47900 is blank where no provincial credits form supplies it.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.manifest import Manifest
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import JURISDICTIONS, units
from tests.kinds import bundled_kinds

D = Decimal
FORM = "ca/t1_tax_and_credits"
LINE_45000 = "ca/ei_overpayment_line_45000"
LINE_45300 = "ca/cwb_line_45300"
LINE_47900 = "ca/provincial_credits_line_47900"
PROVINCES = ["CA-ON", "CA-AB", "CA-BC", "CA-MB", "CA-NB", "CA-NL", "CA-SK"]


def _manifest(province: str) -> Manifest:
    source = YamlJurisdictionSource(JURISDICTIONS.roots(), bundled_kinds(), units())
    (manifest,) = source.get_jurisdiction(JurisdictionCode(province)).manifests
    return manifest


def _t1(province: str, salary: str) -> Worksheet:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            JurisdictionCode(province), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize("province", PROVINCES)
def test_the_t1_exports_the_three_parts_of_line_48200(province: str) -> None:
    (t1,) = (form for form in _manifest(province).forms if form.name == FORM)

    assert {LINE_45000, LINE_45300, LINE_47900} <= set(t1.exports)


@pytest.mark.parametrize(
    ("salary", "ei_overpayment", "cwb"),
    [("20000", "0.00", "1633.00"), ("2010", "22.96", "0.00"), ("70000", "0.00", "0.00")],
)
def test_ontario_line_45000_and_line_45300(salary: str, ei_overpayment: str, cwb: str) -> None:
    sheet = _t1("CA-ON", salary)
    kinds = bundled_kinds()

    assert sheet.get(kinds.kind(LINE_45000)).value == D(ei_overpayment)
    assert sheet.get(kinds.kind(LINE_45300)).value == D(cwb)


@pytest.mark.parametrize("province", ["CA-ON", "CA-AB", "CA-SK", "CA-NL", "CA-NB"])
def test_line_47900_is_blank_where_no_provincial_credits_form_supplies_it(province: str) -> None:
    assert _t1(province, "20000").get(bundled_kinds().kind(LINE_47900)).is_blank


def test_british_columbia_line_47900_is_the_bc479_line_45_and_is_0_with_no_rent() -> None:
    line_47900 = _t1("CA-BC", "20000").get(bundled_kinds().kind(LINE_47900))

    assert not line_47900.is_blank
    assert line_47900.value == D("0.00")
