"""Quebec Schedule P (TP-1.D.P-V, 2025) Part A line 10, "Amount from line 101 of your return, plus
the amount from line 105 if it is positive, minus the amount from box 211 of your RL-1 slip, if
applicable", as the Quebec take-home manifest wires it: four steps, one per operation.

TP-1 line 101 is the salary, read from the TP-1 income form; line 105 is added only if it is
positive; box 211 is subtracted. Line 105 and box 211 are the optional inputs of Work Chart 201
line 1, read as 0 when blank. The expected figures are hand-computed from the printed line, not
from a Revenu Quebec example.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
import yaml

from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_P_LINE_10,
    WORK_CHART_201_LINE_105,
    WORK_CHART_201_RL1_BOX_211,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import (
    SCHEDULE_P_FIRST_PARTS,
    schedule_p_form,
    schedule_p_worksheet,
)

D = Decimal

FORM = schedule_p_form("ca-qc/schedule_p_line_10")


def line_10(
    take_home_service: TakeHomeService, salary: str, *given: tuple[AmountKind, str]
) -> Worksheet:
    """The Schedule P worksheet of a salary, with the optional answers a test gives."""
    return schedule_p_worksheet(take_home_service, FORM, SCHEDULE_P_FIRST_PARTS, salary, *given)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_salary_only_line_10_is_the_salary(
    take_home_service: TakeHomeService, salary: str
) -> None:
    value = line_10(take_home_service, salary).get(SCHEDULE_P_LINE_10).value

    assert str(value) == f"{salary}.00"


def test_a_positive_line_105_is_added(take_home_service: TakeHomeService) -> None:
    value = (
        line_10(take_home_service, "70000", (WORK_CHART_201_LINE_105, "1234.56"))
        .get(SCHEDULE_P_LINE_10)
        .value
    )

    assert value == D("71234.56")


def test_box_211_is_subtracted(take_home_service: TakeHomeService) -> None:
    value = (
        line_10(take_home_service, "70000", (WORK_CHART_201_RL1_BOX_211, "250.25"))
        .get(SCHEDULE_P_LINE_10)
        .value
    )

    assert value == D("69749.75")


def test_line_105_and_box_211_together(take_home_service: TakeHomeService) -> None:
    value = (
        line_10(
            take_home_service,
            "70000",
            (WORK_CHART_201_LINE_105, "1000"),
            (WORK_CHART_201_RL1_BOX_211, "250"),
        )
        .get(SCHEDULE_P_LINE_10)
        .value
    )

    assert value == D("70750.00")


def test_only_the_last_step_carries_the_line_reference() -> None:
    part = yaml.safe_load((QUEBEC_PARTS / "schedule_p_line_10.yaml").read_text(encoding="utf-8"))

    assert [step["name"] for step in part["capabilities"]] == [
        "core/record_total",
        "core/record_total",
        "core/record_total",
        "core/sum_not_below_zero",
        "core/sum",
        "core/subtract",
    ]
    assert [step.get("reference") for step in part["capabilities"]] == [
        None,
        None,
        None,
        None,
        None,
        "10",
    ]
