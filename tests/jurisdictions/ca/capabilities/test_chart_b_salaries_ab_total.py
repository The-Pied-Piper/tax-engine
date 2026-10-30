"""Unit tests for the Chart B row 4 total of Alberta.

Identifier `ca/chart_b_salaries_ab_total`. The shared cases are in `ProvinceTotalCases`.
"""

from __future__ import annotations

from typing import Any

from tax_engine.jurisdictions.ca.capabilities.chart_b_province_total import PROVINCE_AB
from tax_engine.jurisdictions.ca.capabilities.chart_b_salaries_ab_total import (
    ChartBSalariesAbTotal,
)
from tax_engine.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE_SALARIES
from tests.jurisdictions.ca.capabilities.chart_b_provinces import ProvinceTotalCases


class TestChartBSalariesAbTotal(ProvinceTotalCases):
    CAPABILITY: Any = ChartBSalariesAbTotal
    IDENTIFIER = "ca/chart_b_salaries_ab_total"
    MODULE = "chart_b_salaries_ab_total"
    PROVINCE = PROVINCE_AB
    FIELD = FARM_CHART_B_PROVINCE_SALARIES
