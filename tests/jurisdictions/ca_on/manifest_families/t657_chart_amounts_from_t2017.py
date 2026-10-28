"""The CA-ON manifest entries of the amounts Form T657 takes "from line 6 / line 12 of Form T2017"
(`test_manifest.py`).

The steps are in the manifest part `04d_t657_chart_amounts_from_t2017.yaml`. Each is the total, over
the dispositions of the lists of the row forms (lines 2 to 4 for QFFP, lines 8 to 10 for QSBCS) that
the chart takes, of the change in the reserve of each (`ca/t2017_row_change`); the dispositions a
chart takes are the conditions `ca/t657_chart_NNNN_dispositions`. The chart amounts are no longer
inputs of the return.
"""

from __future__ import annotations

from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca import catalog
from tax_calculator.jurisdictions.ca.capabilities.t2017_reserve_total_for_period import (
    T2017ReserveTotalForPeriod,
)
from tax_calculator.jurisdictions.ca.catalog import (
    T2017_LINE_2_RESERVE_ROWS,
    T2017_LINE_3_RESERVE_ROWS,
    T2017_LINE_4_RESERVE_ROWS,
    T2017_LINE_8_RESERVE_ROWS,
    T2017_LINE_9_RESERVE_ROWS,
    T2017_LINE_10_RESERVE_ROWS,
)
from tests.jurisdictions.ca_on.manifest_families.t2017_reserve import ROW_CHANGES

# The chart or part, with the dataset of the dispositions it takes, the kind of its amount from
# line 6 (QFFP) and of its amount from line 12 (QSBCS), by the name each had.
CHARTS = (
    ("t657_chart_2016_dispositions", "T657_CHART_2016_AMOUNT_D", "T657_CHART_2016_AMOUNT_E"),
    *(
        (
            f"t657_chart_{year}_dispositions",
            f"T657_CHART_{year}_AMOUNT_F",
            f"T657_CHART_{year}_AMOUNT_G",
        )
        for year in range(2017, 2024)
    ),
    *(
        (
            f"t657_chart_2024_period_{period}_dispositions",
            f"T657_CHART_2024_PERIOD_{period}_AMOUNT_F",
            f"T657_CHART_2024_PERIOD_{period}_AMOUNT_G",
        )
        for period in (1, 2)
    ),
    *(
        (
            f"t657_chart_2025_part_{part}_dispositions",
            f"T657_PART_{part}_AMOUNT_I",
            f"T657_PART_{part}_AMOUNT_J",
        )
        for part in (1, 2)
    ),
)
QFFP_LISTS = (T2017_LINE_2_RESERVE_ROWS, T2017_LINE_3_RESERVE_ROWS, T2017_LINE_4_RESERVE_ROWS)
QSBCS_LISTS = (T2017_LINE_8_RESERVE_ROWS, T2017_LINE_9_RESERVE_ROWS, T2017_LINE_10_RESERVE_ROWS)

INPUTS: frozenset[str] = frozenset()
OUTPUTS: frozenset[str] = frozenset()


def step(dataset: str, lines: tuple[int, int, int], product: str) -> CapabilitySelection:
    return CapabilitySelection(
        name="ca/t2017_reserve_total_for_period",
        params={"conditions": f"ca/{dataset}"},
        consumes={
            "rows": tuple(f"ca/t2017_line_{line}_reserve_rows" for line in lines),
            "amounts": tuple(f"ca/t2017_line_{line}_reserve.t2017_row_change" for line in lines),
        },
        produces={"total": f"ca/{product}"},
    )


STEPS: set[CapabilitySelection] = set()
WIRING: set[object] = set()
for dataset, qffp, qsbcs in CHARTS:
    for lines, lists, constant in (
        ((2, 3, 4), QFFP_LISTS, qffp),
        ((8, 9, 10), QSBCS_LISTS, qsbcs),
    ):
        kind = getattr(catalog, constant)
        STEPS.add(step(dataset, lines, kind.identifier.removeprefix("ca/")))
        WIRING.add(
            (
                T2017ReserveTotalForPeriod,
                frozenset({*lists, *(ROW_CHANGES[line] for line in lines)}),
                frozenset({kind}),
            )
        )
