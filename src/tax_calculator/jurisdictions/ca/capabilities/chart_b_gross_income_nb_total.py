"""Chart B row 1 for New Brunswick: the sum of its rows of the province list."""

from __future__ import annotations

from typing import Any, ClassVar

from tax_calculator.domain.artifact import ArtifactKind
from tax_calculator.domain.capability import capability
from tax_calculator.jurisdictions.ca.capabilities.chart_b_province_total import (
    PROVINCE_NB,
    ChartBProvinceTotal,
)
from tax_calculator.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE_GROSS_INCOME


@capability(identifier="chart_b_gross_income_nb_total")
class ChartBGrossIncomeNbTotal(ChartBProvinceTotal):
    """Produces `output`: row 1 for New Brunswick, the sum of the province list's rows for it."""

    PROVINCE: ClassVar[int] = PROVINCE_NB
    FIELD: ClassVar[ArtifactKind[Any]] = FARM_CHART_B_PROVINCE_GROSS_INCOME
