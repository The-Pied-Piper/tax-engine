"""Chart B row 4 for Saskatchewan: the sum of its rows of the province list."""

from __future__ import annotations

from typing import Any, ClassVar

from tax_calculator.domain.artifact import ArtifactKind
from tax_calculator.domain.capability import capability
from tax_calculator.jurisdictions.ca.capabilities.chart_b_province_total import (
    PROVINCE_SK,
    ChartBProvinceTotal,
)
from tax_calculator.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE_SALARIES


@capability(identifier="chart_b_salaries_sk_total")
class ChartBSalariesSkTotal(ChartBProvinceTotal):
    """Produces `output`: row 4 for Saskatchewan, the sum of the province list's rows for it."""

    PROVINCE: ClassVar[int] = PROVINCE_SK
    FIELD: ClassVar[ArtifactKind[Any]] = FARM_CHART_B_PROVINCE_SALARIES
