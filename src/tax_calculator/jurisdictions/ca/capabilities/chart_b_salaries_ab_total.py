"""Chart B row 4 for Alberta: the sum of its rows of the province list."""

from __future__ import annotations

from typing import Any, ClassVar

from tax_calculator.domain.artifact import ArtifactKind
from tax_calculator.domain.capability import capability
from tax_calculator.jurisdictions.ca.capabilities.chart_b_province_total import (
    PROVINCE_AB,
    ChartBProvinceTotal,
)
from tax_calculator.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE_SALARIES


@capability(identifier="chart_b_salaries_ab_total")
class ChartBSalariesAbTotal(ChartBProvinceTotal):
    """Produces `output`: row 4 for Alberta, the sum of the province list's Alberta rows."""

    PROVINCE: ClassVar[int] = PROVINCE_AB
    FIELD: ClassVar[ArtifactKind[Any]] = FARM_CHART_B_PROVINCE_SALARIES
