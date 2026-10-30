"""Unit tests for the Chart B row 1 total of Prince Edward Island.

Identifier `ca/chart_b_gross_income_pe_total`. The shared cases are in `ProvinceTotalCases`.
"""

from __future__ import annotations

from typing import Any

from tax_engine.jurisdictions.ca.capabilities.chart_b_gross_income_pe_total import (
    ChartBGrossIncomePeTotal,
)
from tax_engine.jurisdictions.ca.capabilities.chart_b_province_total import PROVINCE_PE
from tax_engine.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE_GROSS_INCOME
from tests.jurisdictions.ca.capabilities.chart_b_provinces import ProvinceTotalCases


class TestChartBGrossIncomePeTotal(ProvinceTotalCases):
    CAPABILITY: Any = ChartBGrossIncomePeTotal
    IDENTIFIER = "ca/chart_b_gross_income_pe_total"
    MODULE = "chart_b_gross_income_pe_total"
    PROVINCE = PROVINCE_PE
    FIELD = FARM_CHART_B_PROVINCE_GROSS_INCOME
