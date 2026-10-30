"""Unit tests for the Chart B row 1 total of Manitoba.

Identifier `ca/chart_b_gross_income_mb_total`. The shared cases are in `ProvinceTotalCases`.
"""

from __future__ import annotations

from typing import Any

from tax_engine.jurisdictions.ca.capabilities.chart_b_gross_income_mb_total import (
    ChartBGrossIncomeMbTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_province_total import PROVINCE_MB
from tax_engine.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE_GROSS_INCOME
from tests.jurisdictions.ca.capabilities.chart_b_provinces import ProvinceTotalCases


class TestChartBGrossIncomeMbTotal(ProvinceTotalCases):
    CAPABILITY: Any = ChartBGrossIncomeMbTotal
    IDENTIFIER = "ca/chart_b_gross_income_mb_total"
    MODULE = "chart_b_gross_income_mb_total"
    PROVINCE = PROVINCE_MB
    FIELD = FARM_CHART_B_PROVINCE_GROSS_INCOME
