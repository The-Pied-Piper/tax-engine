"""Unit tests for the Chart B row 1 total of Ontario.

Identifier `ca/chart_b_gross_income_on_total`. The shared cases are in `ProvinceTotalCases`.
"""

from __future__ import annotations

from typing import Any

from tax_engine.jurisdictions.ca.capabilities.chart_b_gross_income_on_total import (
    ChartBGrossIncomeOnTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_province_total import PROVINCE_ON
from tax_engine.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE_GROSS_INCOME
from tests.jurisdictions.ca.capabilities.chart_b_provinces import ProvinceTotalCases


class TestChartBGrossIncomeOnTotal(ProvinceTotalCases):
    CAPABILITY: Any = ChartBGrossIncomeOnTotal
    IDENTIFIER = "ca/chart_b_gross_income_on_total"
    MODULE = "chart_b_gross_income_on_total"
    PROVINCE = PROVINCE_ON
    FIELD = FARM_CHART_B_PROVINCE_GROSS_INCOME
