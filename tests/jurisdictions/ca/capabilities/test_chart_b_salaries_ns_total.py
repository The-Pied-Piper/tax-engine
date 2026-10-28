"""Unit tests for the Chart B row 4 total of Nova Scotia.

Identifier `ca/chart_b_salaries_ns_total`. The shared cases are in `ProvinceTotalCases`.
"""

from __future__ import annotations

from typing import Any

from tax_calculator.jurisdictions.ca.capabilities.chart_b_province_total import PROVINCE_NS
from tax_calculator.jurisdictions.ca.capabilities.chart_b_salaries_ns_total import (
    ChartBSalariesNsTotal,
)
from tax_calculator.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE_SALARIES
from tests.jurisdictions.ca.capabilities.chart_b_provinces import ProvinceTotalCases


class TestChartBSalariesNsTotal(ProvinceTotalCases):
    CAPABILITY: Any = ChartBSalariesNsTotal
    IDENTIFIER = "ca/chart_b_salaries_ns_total"
    MODULE = "chart_b_salaries_ns_total"
    PROVINCE = PROVINCE_NS
    FIELD = FARM_CHART_B_PROVINCE_SALARIES
