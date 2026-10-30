"""Unit tests for the Chart B row 1 total of Nova Scotia.

Identifier `ca/chart_b_gross_income_ns_total`. The shared cases are in `ProvinceTotalCases`.
"""

from __future__ import annotations

from typing import Any

from tax_engine.jurisdictions.ca.capabilities.chart_b_gross_income_ns_total import (
    ChartBGrossIncomeNsTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_province_total import PROVINCE_NS
from tax_engine.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE_GROSS_INCOME
from tests.jurisdictions.ca.capabilities.chart_b_provinces import ProvinceTotalCases


class TestChartBGrossIncomeNsTotal(ProvinceTotalCases):
    CAPABILITY: Any = ChartBGrossIncomeNsTotal
    IDENTIFIER = "ca/chart_b_gross_income_ns_total"
    MODULE = "chart_b_gross_income_ns_total"
    PROVINCE = PROVINCE_NS
    FIELD = FARM_CHART_B_PROVINCE_GROSS_INCOME
