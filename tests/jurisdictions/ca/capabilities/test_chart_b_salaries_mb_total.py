"""Unit tests for the Chart B row 4 total of Manitoba.

Identifier `ca/chart_b_salaries_mb_total`. The shared cases are in `ProvinceTotalCases`.
"""

from __future__ import annotations

from typing import Any

from tax_calculator.jurisdictions.ca.capabilities.chart_b_province_total import PROVINCE_MB
from tax_calculator.jurisdictions.ca.capabilities.chart_b_salaries_mb_total import (
    ChartBSalariesMbTotal,
)
from tax_calculator.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE_SALARIES
from tests.jurisdictions.ca.capabilities.chart_b_provinces import ProvinceTotalCases


class TestChartBSalariesMbTotal(ProvinceTotalCases):
    CAPABILITY: Any = ChartBSalariesMbTotal
    IDENTIFIER = "ca/chart_b_salaries_mb_total"
    MODULE = "chart_b_salaries_mb_total"
    PROVINCE = PROVINCE_MB
    FIELD = FARM_CHART_B_PROVINCE_SALARIES
