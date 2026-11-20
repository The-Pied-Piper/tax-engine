"""Revenu Quebec Schedule K (TP-1.D.K-V, 2025-12), Part C, line 88, the printed 63.83 of the box 61
row, as the Quebec take-home manifest wires it. Printed as "Number of months entered in box 61 x
$63.83".

`core/credit_amount` takes the printed 63.83 from the `ca-qc/schedule_k_monthly_amount_box_61`
dataset, claimed whole; it is not a line of the form. Line 84 and boxes 60 to 62 are given
straight to the form to show that no input changes it; the last tests run the real Part A, B and C
chains from a salary.
"""

from __future__ import annotations

import pytest
import yaml

from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_K_MONTHLY_AMOUNT_BOX_61
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_k_part_d_support import (
    COLUMNS,
    PART_D,
    SALARY_COLUMNS,
    part_d,
    salary_sheet,
)
from tests.jurisdictions.ca_qc.schedule_k_support import FORM_NAME
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

LINE = "ca-qc/schedule_k_monthly_amount_box_61"
PARTS = PART_D[6:7]
FILE = "tp1_schedule_k_line_88_box_61_amount.yaml"


@pytest.mark.parametrize("key", list(COLUMNS))
def test_line_88_box_61_amount_for_a_line_84_and_the_months_given_to_part_c(
    take_home_service: TakeHomeService, key: tuple[str, str, str]
) -> None:
    sheet = part_d(take_home_service, key, PARTS)

    assert str(sheet.get(SCHEDULE_K_MONTHLY_AMOUNT_BOX_61).value) == "63.83"


@pytest.mark.parametrize(("salary", "answer"), list(SALARY_COLUMNS))
def test_line_88_box_61_amount_at_each_salary_and_answer_to_line_50(
    take_home_service: TakeHomeService, salary: str, answer: str
) -> None:
    sheet = salary_sheet(take_home_service, salary, answer, PARTS)

    assert str(sheet.get(SCHEDULE_K_MONTHLY_AMOUNT_BOX_61).value) == "63.83"


def test_the_part_is_as_printed() -> None:
    part = yaml.safe_load((QUEBEC_PARTS / FILE).read_text("utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    assert part["capabilities"] == [
        {
            "name": "core/credit_amount",
            "unit": "ca/cad",
            "params": {"amount": "ca-qc/schedule_k_monthly_amount_box_61"},
            "produces": {"output": LINE},
        }
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = quebec_kinds().kind(LINE)

    assert kind is SCHEDULE_K_MONTHLY_AMOUNT_BOX_61
    assert non_negative(kind)
