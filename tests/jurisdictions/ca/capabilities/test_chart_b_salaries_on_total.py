"""Unit tests for the Chart B row 4 total of Ontario.

Identifier `ca/chart_b_salaries_on_total`. The shared cases are in `ProvinceTotalCases`.
"""

from __future__ import annotations

from typing import Any

from tax_engine.jurisdictions.ca.capabilities.chart_b_province_total import PROVINCE_ON
from tax_engine.jurisdictions.ca.capabilities.chart_b_salaries_on_total import (
    ChartBSalariesOnTotal,
)
from tax_engine.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE_SALARIES
from tests.jurisdictions.ca.capabilities.chart_b_provinces import ProvinceTotalCases


class TestChartBSalariesOnTotal(ProvinceTotalCases):
    CAPABILITY: Any = ChartBSalariesOnTotal
    IDENTIFIER = "ca/chart_b_salaries_on_total"
    MODULE = "chart_b_salaries_on_total"
    PROVINCE = PROVINCE_ON
    FIELD = FARM_CHART_B_PROVINCE_SALARIES
