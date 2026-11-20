"""Quebec Schedule P (TP-1.D.P-V, 2025) Part A line 18, "Add lines 10 through 15 and, if
applicable, lines 30 through 35", column "You", as the Quebec take-home manifest wires it: one
`core/sum` of line 10 and the optional lines 12 to 15, each blank read as 0, rounded half-up to the
cent. The spouse lines are left out."""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_P_LINE_18,
    SCHEDULE_P_SCHEDULE_L_INCOME_LINE_14,
    WORK_CHART_201_LINE_107,
    WORK_CHART_201_RESEARCH_GRANTS_LINE_3,
    WORK_CHART_201_WEPP_PAYMENTS_LINE_4,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import (
    SCHEDULE_P_FIRST_PARTS,
    schedule_p_form,
    schedule_p_worksheet,
)

PARTS = (
    *SCHEDULE_P_FIRST_PARTS,
    "schedule_p_line_14_inputs.yaml",
    "schedule_p_line_18.yaml",
)
FORM = schedule_p_form("ca-qc/schedule_p_line_18")


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_salary_only_line_18_is_the_salary(
    take_home_service: TakeHomeService, salary: str
) -> None:
    value = (
        schedule_p_worksheet(take_home_service, FORM, PARTS, salary).get(SCHEDULE_P_LINE_18).value
    )

    assert str(value) == f"{salary}.00"


def test_lines_12_to_15_are_added_to_line_10(take_home_service: TakeHomeService) -> None:
    sheet = schedule_p_worksheet(
        take_home_service,
        FORM,
        PARTS,
        "70000",
        (WORK_CHART_201_LINE_107, "100.10"),
        (WORK_CHART_201_RESEARCH_GRANTS_LINE_3, "200.20"),
        (SCHEDULE_P_SCHEDULE_L_INCOME_LINE_14, "300.30"),
        (WORK_CHART_201_WEPP_PAYMENTS_LINE_4, "400.40"),
    )

    assert sheet.get(SCHEDULE_P_LINE_18).value == Decimal("71001.00")
