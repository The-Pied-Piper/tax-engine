"""Unit tests for the Chart B row 4 total of Prince Edward Island.

Identifier `ca/chart_b_salaries_pe_total`. The shared cases are in `ProvinceTotalCases`.
"""

from __future__ import annotations

from typing import Any

from tax_calculator.jurisdictions.ca.capabilities.chart_b_province_total import PROVINCE_PE
from tax_calculator.jurisdictions.ca.capabilities.chart_b_salaries_pe_total import (
    ChartBSalariesPeTotal,
)
from tax_calculator.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE_SALARIES
from tests.jurisdictions.ca.capabilities.chart_b_provinces import ProvinceTotalCases


class TestChartBSalariesPeTotal(ProvinceTotalCases):
    CAPABILITY: Any = ChartBSalariesPeTotal
    IDENTIFIER = "ca/chart_b_salaries_pe_total"
    MODULE = "chart_b_salaries_pe_total"
    PROVINCE = PROVINCE_PE
    FIELD = FARM_CHART_B_PROVINCE_SALARIES
