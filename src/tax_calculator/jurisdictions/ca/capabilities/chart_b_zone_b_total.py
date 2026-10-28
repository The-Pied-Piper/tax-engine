"""ChartBZoneBTotal: Form T2222 Step 3, Chart B, "(B) Total (add all the amounts under Column 7)".

The lowest of columns 3, 4 and 5 of each trip in a prescribed intermediate zone (Zone B, 2),
added; see `ChartBZoneTotal`.
"""

from __future__ import annotations

from typing import ClassVar

from tax_calculator.domain.capability import capability
from tax_calculator.jurisdictions.ca.capabilities.chart_b_zone_total import ZONE_B, ChartBZoneTotal


@capability(identifier="chart_b_zone_b_total")
class ChartBZoneBTotal(ChartBZoneTotal):
    """Produces `total`: the lowest amount of each consumed trip in Zone B, added."""

    ZONE: ClassVar[int] = ZONE_B
