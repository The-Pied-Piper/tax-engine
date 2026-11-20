"""Quebec Schedule P (TP-1.D.P-V, 2025) Part A line 29, "Subtract line 22 from line 18 and, if
applicable, subtract line 42 from line 38. Work income", column "You", as the Quebec take-home
manifest wires it: one `core/subtract` of line 22 from line 18, a blank line 22 read as 0, with no
floor (the form prints none), rounded half-up to the cent. The form part exports the figure.

The expected work income of a salary-only filer is the salary: hand-computed from the printed
lines (line 10 is the salary, lines 12 to 15 and 22 are blank), not from a Revenu Quebec example."""

from __future__ import annotations

from decimal import Decimal

import pytest
import yaml

from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_P_DEDUCTIBLE_INCOME_LINE_22,
    SCHEDULE_P_WORK_INCOME_LINE_29,
    TP1_LINE_105,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import SCHEDULE_P_FIRST_PARTS, schedule_p_worksheet

PARTS = (
    *SCHEDULE_P_FIRST_PARTS,
    "schedule_p_line_12_inputs.yaml",
    "schedule_p_line_13_inputs.yaml",
    "schedule_p_line_14_inputs.yaml",
    "schedule_p_line_15_inputs.yaml",
    "schedule_p_line_18.yaml",
    "schedule_p_line_22_inputs.yaml",
    "schedule_p_line_29.yaml",
)
FORM = (QUEBEC_PARTS / "schedule_p.yaml").read_text(encoding="utf-8")


def test_the_form_part_names_titles_and_exports_the_form() -> None:
    part = yaml.safe_load(FORM)

    assert list(part["form"]) == ["name", "title", "required", "exports"]
    assert part["form"]["name"] == "ca-qc/schedule_p"
    assert part["form"]["title"] == "Schedule P: Tax Credits Respecting the Work Premium"
    assert part["form"]["exports"] == ["ca-qc/schedule_p_work_income_line_29"]
    assert part["capabilities"] == []


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_salary_only_work_income_is_the_salary(
    take_home_service: TakeHomeService, salary: str
) -> None:
    value = (
        schedule_p_worksheet(take_home_service, FORM, PARTS, salary)
        .get(SCHEDULE_P_WORK_INCOME_LINE_29)
        .value
    )

    assert str(value) == f"{salary}.00"


def test_line_22_is_subtracted_from_line_18(take_home_service: TakeHomeService) -> None:
    sheet = schedule_p_worksheet(
        take_home_service,
        FORM,
        PARTS,
        "70000",
        (TP1_LINE_105, "500"),
        (SCHEDULE_P_DEDUCTIBLE_INCOME_LINE_22, "250.50"),
    )

    assert sheet.get(SCHEDULE_P_WORK_INCOME_LINE_29).value == Decimal("70249.50")


def test_the_work_income_is_not_floored(take_home_service: TakeHomeService) -> None:
    sheet = schedule_p_worksheet(
        take_home_service,
        FORM,
        PARTS,
        "100",
        (SCHEDULE_P_DEDUCTIBLE_INCOME_LINE_22, "250.00"),
    )

    assert sheet.get(SCHEDULE_P_WORK_INCOME_LINE_29).value == Decimal("-150.00")
