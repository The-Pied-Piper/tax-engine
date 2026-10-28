"""Unit tests for the Chart B row 4 total of Newfoundland and Labrador.

Identifier `ca/chart_b_salaries_nl_total`. The shared cases are in `ProvinceTotalCases`.
"""

from __future__ import annotations

from typing import Any

from tax_calculator.jurisdictions.ca.capabilities.chart_b_province_total import PROVINCE_NL
from tax_calculator.jurisdictions.ca.capabilities.chart_b_salaries_nl_total import (
    ChartBSalariesNlTotal,
)
from tax_calculator.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE_SALARIES
from tests.jurisdictions.ca.capabilities.chart_b_provinces import ProvinceTotalCases


class TestChartBSalariesNlTotal(ProvinceTotalCases):
    CAPABILITY: Any = ChartBSalariesNlTotal
    IDENTIFIER = "ca/chart_b_salaries_nl_total"
    MODULE = "chart_b_salaries_nl_total"
    PROVINCE = PROVINCE_NL
    FIELD = FARM_CHART_B_PROVINCE_SALARIES
