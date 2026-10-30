"""Chart B row 1 for Ontario: the sum of its rows of the province list."""

from __future__ import annotations

from typing import Any, ClassVar

from tax_engine.domain.artifact import ArtifactKind
from tax_engine.domain.capability import capability
from tax_engine.jurisdictions.ca.capabilities.chart_b_province_total import (
    PROVINCE_ON,
    ChartBProvinceTotal,
)
from tax_engine.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE_GROSS_INCOME


@capability(identifier="chart_b_gross_income_on_total")
class ChartBGrossIncomeOnTotal(ChartBProvinceTotal):
    """Produces `output`: row 1 for Ontario, the sum of the province list's Ontario rows."""

    PROVINCE: ClassVar[int] = PROVINCE_ON
    FIELD: ClassVar[ArtifactKind[Any]] = FARM_CHART_B_PROVINCE_GROSS_INCOME
