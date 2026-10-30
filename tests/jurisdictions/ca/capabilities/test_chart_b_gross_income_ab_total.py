"""Unit tests for the Chart B row 1 total of Alberta.

Identifier `ca/chart_b_gross_income_ab_total`. The shared cases are in `ProvinceTotalCases`.
"""

from __future__ import annotations

from typing import Any

from tax_engine.jurisdictions.ca.capabilities.chart_b_gross_income_ab_total import (
    ChartBGrossIncomeAbTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_province_total import PROVINCE_AB
from tax_engine.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE_GROSS_INCOME
from tests.jurisdictions.ca.capabilities.chart_b_provinces import ProvinceTotalCases


class TestChartBGrossIncomeAbTotal(ProvinceTotalCases):
    CAPABILITY: Any = ChartBGrossIncomeAbTotal
    IDENTIFIER = "ca/chart_b_gross_income_ab_total"
    MODULE = "chart_b_gross_income_ab_total"
    PROVINCE = PROVINCE_AB
    FIELD = FARM_CHART_B_PROVINCE_GROSS_INCOME
