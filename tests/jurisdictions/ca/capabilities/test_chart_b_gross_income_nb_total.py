"""Unit tests for the Chart B row 1 total of New Brunswick.

Identifier `ca/chart_b_gross_income_nb_total`. The shared cases are in `ProvinceTotalCases`.
"""

from __future__ import annotations

from typing import Any

from tax_calculator.jurisdictions.ca.capabilities.chart_b_gross_income_nb_total import (
    ChartBGrossIncomeNbTotal,
)
from tax_calculator.jurisdictions.ca.capabilities.chart_b_province_total import PROVINCE_NB
from tax_calculator.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE_GROSS_INCOME
from tests.jurisdictions.ca.capabilities.chart_b_provinces import ProvinceTotalCases


class TestChartBGrossIncomeNbTotal(ProvinceTotalCases):
    CAPABILITY: Any = ChartBGrossIncomeNbTotal
    IDENTIFIER = "ca/chart_b_gross_income_nb_total"
    MODULE = "chart_b_gross_income_nb_total"
    PROVINCE = PROVINCE_NB
    FIELD = FARM_CHART_B_PROVINCE_GROSS_INCOME
