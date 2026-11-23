"""Revenu Quebec Work Chart 201 (TP-1.D.GR-V 2025-12) line 5, as the Quebec take-home manifest part
wires it. The form prints: "Net business income (line 27 of Schedule L). If the result is negative,
enter 0." (+ 5). Line 164 of the TP-1 ("Net business income. Complete Schedule L.") is the same
figure and keeps its sign, as TP-1 line 199 adds a loss. It is an optional input of the TP-1 income
form only, which takes it once and exports it; line 5 reads that export as a record list of one
(`core/record_total`, a blank read as 0) and then floors it at 0 with `core/sum_not_below_zero` over
that one part, as Work Chart 201 line 1 takes TP-1 line 105 "if positive". The floor step produces
the existing non-negative `ca-qc/work_chart_201_net_business_income_line_5`, so line 6 is untouched.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_qc
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_LINE_164,
    TP1_TOTAL_INCOME_LINE_199,
    WORK_CHART_201_NET_BUSINESS_INCOME_LINE_5,
    WORK_CHART_201_TOTAL_LINE_6,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import TP1_PARTS

D = Decimal

QUEBEC_PARTS = Path(tax_engine.jurisdictions.ca_qc.__file__).parent / "manifests" / "2025"
PARTS = (
    *TP1_PARTS,
    "work_chart_201_line_1.yaml",
    "work_chart_201_line_2_input.yaml",
    "work_chart_201_line_3_input.yaml",
    "work_chart_201_line_4_input.yaml",
    "work_chart_201_line_5.yaml",
    "work_chart_201_line_6.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-qc/work_chart_201
      required: true
      exports:
        - ca-qc/work_chart_201_net_business_income_line_5
        - ca-qc/work_chart_201_total_line_6
    """)


def test_the_part_reads_the_line_164_export_then_floors_it_at_zero() -> None:
    part: dict[str, Any] = yaml.safe_load(
        (QUEBEC_PARTS / "work_chart_201_line_5.yaml").read_text(encoding="utf-8")
    )

    assert part == {
        "form": {"name": "ca-qc/work_chart_201"},
        "capabilities": [
            {
                "name": "core/record_total",
                "title": "TP-1 line 164",
                "unit": "ca/cad",
                "consumes": {"records": "ca-qc/tp1_income.tp1_line_164"},
                "blank": {"records": {"ca-qc/tp1_line_164": "0"}},
                "produces": {"output": "ca-qc/work_chart_201_tp1_line_164"},
            },
            {
                "name": "core/sum_not_below_zero",
                "title": "Net business income",
                "reference": "5",
                "unit": "ca/cad",
                "params": {"rounding": "ca-qc/cent_rounding"},
                "consumes": {"parts": ["ca-qc/work_chart_201_tp1_line_164"]},
                "produces": {"output": "ca-qc/work_chart_201_net_business_income_line_5"},
            },
        ],
    }


def test_the_line_5_input_is_gone_and_the_tp1_income_form_exports_line_164() -> None:
    exports = yaml.safe_load((QUEBEC_PARTS / "tp1_income.yaml").read_text(encoding="utf-8"))[
        "form"
    ]["exports"]

    assert "ca-qc/tp1_line_164" in exports
    assert not (QUEBEC_PARTS / "work_chart_201_line_5_input.yaml").exists()


@pytest.mark.parametrize(
    ("line_164", "line_5", "line_6", "line_199"),
    [
        # A loss: line 5 floors it at 0; line 199 still adds the negative (70,000 - 1,500.25).
        ("-1500.25", "0.00", "70000.00", "68499.75"),
        # A profit passes through: 70,000 + 2,500.50 on both lines.
        ("2500.50", "2500.50", "72500.50", "72500.50"),
        # Left out: read as 0 on line 5, the salary alone on line 6 and line 199.
        (None, "0.00", "70000.00", "70000.00"),
    ],
)
def test_line_5_is_line_164_floored_at_zero_while_line_199_keeps_the_sign(
    take_home_service: TakeHomeService,
    line_164: str | None,
    line_5: str,
    line_6: str,
    line_199: str,
) -> None:
    starting = [Artifact(EMPLOYMENT_INCOME, D("70000"))]
    if line_164 is not None:
        starting.append(Artifact(TP1_LINE_164, D(line_164)))
    sheets = take_home_service(HEADER, FORM, *PARTS).compute(
        TaxCalculationRequest(JurisdictionCode("CA-QC"), 2025, tuple(starting))
    )

    chart = sheets["ca-qc/work_chart_201"][0]
    assert str(chart.get(WORK_CHART_201_NET_BUSINESS_INCOME_LINE_5).value) == line_5
    assert str(chart.get(WORK_CHART_201_TOTAL_LINE_6).value) == line_6
    income = sheets["ca-qc/tp1_income"][0]
    assert str(income.get(TP1_TOTAL_INCOME_LINE_199).value) == line_199
