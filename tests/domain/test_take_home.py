"""The rules of take-home pay: reading a figure, one unit, and the sums in whole cents."""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InvalidManifestError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.take_home import (
    FigureReference,
    FigureValue,
    Totals,
    rate_unit,
    shared_unit,
)
from tax_engine.domain.unit import Unit
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.manifest_support import real_manifest

D = Decimal
CAD = Unit("ca/cad")
PERCENT = Unit("core/percent")


def test_totals_are_sums_in_whole_cents() -> None:
    got = Totals.of(D("70000"), [("income_tax", D("11497.094")), ("ei", D("1077.48"))])
    assert got == Totals(
        salary=D("70000.00"),
        income_tax=D("11497.09"),
        total_deductions=D("12574.57"),
        take_home=D("57425.43"),
    )


def test_totals_with_no_income_tax_figure_have_none() -> None:
    assert Totals.of(D("100"), [("ei", D("1"))]).income_tax == D("0.00")


def test_figures_in_one_unit_share_it() -> None:
    assert shared_unit("x", [FigureValue(D(1), CAD), FigureValue(D(2), CAD)]) == CAD


@pytest.mark.parametrize(
    "values",
    [
        [FigureValue(D(1), CAD), FigureValue(D(2), PERCENT)],
        [FigureValue(D(1), None)],
        [FigureValue(D(1), CAD), FigureValue(D(2), None)],
        [],
    ],
)
def test_figures_that_do_not_share_one_unit_are_refused(values: list[FigureValue]) -> None:
    with pytest.raises(InvalidManifestError, match="CA-ON 2025: the figures do not share one unit"):
        shared_unit("CA-ON 2025", values)


def test_a_rate_without_a_unit_is_refused() -> None:
    assert rate_unit("x", FigureValue(D("0.1"), PERCENT)) == PERCENT
    with pytest.raises(InvalidManifestError, match="the rate has no unit"):
        rate_unit("x", FigureValue(D("0.1"), None))


def test_a_figure_is_read_off_the_one_worksheet_of_its_form() -> None:
    manifest = real_manifest("CA-ON")
    sheets = build_tax_computation().compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-ON"), 2025, (Artifact(EMPLOYMENT_INCOME, D(70000)),)
        )
    )
    declared = manifest.take_home
    assert declared is not None
    got = declared.income_tax.read(sheets, manifest.kinds)
    assert got.amount.quantize(D("0.01")) == D("11497.09")
    assert got.unit == CAD
    with pytest.raises(InvalidManifestError, match="not one"):
        FigureReference("ca/t1_tax_and_credits", "ca/total_payable").read(
            {"ca/t1_tax_and_credits": ()}, manifest.kinds
        )
