"""ChartBZoneATotal: Form T2222 Step 3, Chart B, "(A) Total (add all the amounts under Column 6)".

The lowest of columns 3, 4 and 5 of each trip in a prescribed northern zone (Zone A, 1), added;
see `ChartBZoneTotal`.
"""

from __future__ import annotations

from typing import ClassVar

from tax_calculator.domain.capability import capability
from tax_calculator.jurisdictions.ca.capabilities.chart_b_zone_total import ZONE_A, ChartBZoneTotal


@capability(identifier="chart_b_zone_a_total")
class ChartBZoneATotal(ChartBZoneTotal):
    """Produces `total`: the lowest amount of each consumed trip in Zone A, added."""

    ZONE: ClassVar[int] = ZONE_A
