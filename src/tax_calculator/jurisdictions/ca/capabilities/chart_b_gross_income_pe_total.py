"""Chart B row 1 for Prince Edward Island: the sum of its rows of the province list."""

from __future__ import annotations

from typing import Any, ClassVar

from tax_calculator.domain.artifact import ArtifactKind
from tax_calculator.domain.capability import capability
from tax_calculator.jurisdictions.ca.capabilities.chart_b_province_total import (
    PROVINCE_PE,
    ChartBProvinceTotal,
)
from tax_calculator.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE_GROSS_INCOME


@capability(identifier="chart_b_gross_income_pe_total")
class ChartBGrossIncomePeTotal(ChartBProvinceTotal):
    """Produces `output`: row 1 for Prince Edward Island, the sum of the province list's rows."""

    PROVINCE: ClassVar[int] = PROVINCE_PE
    FIELD: ClassVar[ArtifactKind[Any]] = FARM_CHART_B_PROVINCE_GROSS_INCOME
