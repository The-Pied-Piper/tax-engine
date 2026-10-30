"""Unit tests for the Chart B Zone B total of Form T2222 (`ca/chart_b_zone_b_total`).

Form T2222, Step 3, Chart B: "Enter the lowest amount from column 3, 4, or 5 in the column for the
prescribed zone(s) you resided in at the time of the trip.", then "(B) Total (add all the
amounts under Column 7) =" (Zone B). The capability has one consumed slot `trips` (a record list
with a record for each trip: its individual, its zone, 1 for Zone A and 2 for Zone B, and
columns 3, 4 and 5), one produced slot `total` and no parameter slot. It takes, for each trip in
Zone B, the lowest of the three columns and totals them, exactly: it has no dataset, so it never
rounds. A trip in the other zone adds nothing. An individual is only named, no capability reads
it. A trip whose zone is neither 1 nor 2 is an InvalidRecordError naming the item by its position
from 1. It records one `ItemLesserOfLine` for each trip in Zone B, named by the trip's position
in the list, and then one `ItemsTotalLine`.

The figures are CRA's own, from the form's examples 3 and 4.
"""

from __future__ import annotations

from typing import Any

from tax_engine.jurisdictions.ca.capabilities.chart_b_zone_b_total import ChartBZoneBTotal
from tests.jurisdictions.ca.capabilities.chart_b_trips import ZONE_A, ZONE_B, ZoneTotalCases


class TestChartBZoneBTotal(ZoneTotalCases):
    CAPABILITY: Any = ChartBZoneBTotal
    IDENTIFIER = "ca/chart_b_zone_b_total"
    MODULE = "chart_b_zone_b_total"
    OWN_ZONE = ZONE_B
    OTHER_ZONE = ZONE_A
    MIXED_TOTAL = "2100"
