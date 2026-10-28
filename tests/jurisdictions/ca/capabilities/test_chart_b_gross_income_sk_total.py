"""Unit tests for the Chart B row 1 total of Saskatchewan.

Identifier `ca/chart_b_gross_income_sk_total`. The shared cases are in `ProvinceTotalCases`.
"""

from __future__ import annotations

from typing import Any

from tax_calculator.jurisdictions.ca.capabilities.chart_b_gross_income_sk_total import (
    ChartBGrossIncomeSkTotal,
)
from tax_calculator.jurisdictions.ca.capabilities.chart_b_province_total import PROVINCE_SK
from tax_calculator.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE_GROSS_INCOME
from tests.jurisdictions.ca.capabilities.chart_b_provinces import ProvinceTotalCases


class TestChartBGrossIncomeSkTotal(ProvinceTotalCases):
    CAPABILITY: Any = ChartBGrossIncomeSkTotal
    IDENTIFIER = "ca/chart_b_gross_income_sk_total"
    MODULE = "chart_b_gross_income_sk_total"
    PROVINCE = PROVINCE_SK
    FIELD = FARM_CHART_B_PROVINCE_GROSS_INCOME
