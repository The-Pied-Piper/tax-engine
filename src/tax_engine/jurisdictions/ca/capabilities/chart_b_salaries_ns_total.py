"""Chart B row 4 for Nova Scotia: the sum of its rows of the province list."""

from __future__ import annotations

from typing import Any, ClassVar

from tax_engine.domain.artifact import ArtifactKind
from tax_engine.domain.capability import capability
from tax_engine.jurisdictions.ca.capabilities.chart_b_province_total import (
    PROVINCE_NS,
    ChartBProvinceTotal,
)
from tax_engine.jurisdictions.ca.catalog import FARM_CHART_B_PROVINCE_SALARIES


@capability(identifier="chart_b_salaries_ns_total")
class ChartBSalariesNsTotal(ChartBProvinceTotal):
    """Produces `output`: row 4 for Nova Scotia, the sum of the province list's rows for it."""

    PROVINCE: ClassVar[int] = PROVINCE_NS
    FIELD: ClassVar[ArtifactKind[Any]] = FARM_CHART_B_PROVINCE_SALARIES
