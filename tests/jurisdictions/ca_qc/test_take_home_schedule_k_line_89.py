"""Revenu Quebec Schedule K (TP-1.D.K-V, 2025-12), Part C, line 89, as the Quebec take-home manifest
wires it. Printed as "Subtract line 88 from line 87".

`core/subtract` takes line 88 off line 87, rounded half-up to the cent by `ca-qc/cent_rounding`.
Line 84 and boxes 60 to 62 are given straight to the form, so a test can pick the months; the last
tests run the real Part A, B and C chains from a salary. The expected figures are hand-computed
from the printed lines, not an official example.
"""

from __future__ import annotations

import pytest
import yaml

from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_K_PREMIUM_REMAINING_LINE_89
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_k_part_d_support import (
    COLUMNS,
    INDEX,
    PART_D,
    SALARY_COLUMNS,
    part_d,
    salary_sheet,
)
from tests.jurisdictions.ca_qc.schedule_k_support import FORM_NAME
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

LINE = "ca-qc/schedule_k_premium_remaining_line_89"
PARTS = PART_D[3:10]
FILE = "tp1_schedule_k_line_89.yaml"


@pytest.mark.parametrize("key", list(COLUMNS))
def test_line_89_for_a_line_84_and_the_months_given_to_part_c(
    take_home_service: TakeHomeService, key: tuple[str, str, str]
) -> None:
    sheet = part_d(take_home_service, key, PARTS)

    assert str(sheet.get(SCHEDULE_K_PREMIUM_REMAINING_LINE_89).value) == COLUMNS[key][INDEX["89"]]


@pytest.mark.parametrize(("salary", "answer"), list(SALARY_COLUMNS))
def test_line_89_at_each_salary_and_answer_to_line_50(
    take_home_service: TakeHomeService, salary: str, answer: str
) -> None:
    sheet = salary_sheet(take_home_service, salary, answer, PARTS)

    assert (
        str(sheet.get(SCHEDULE_K_PREMIUM_REMAINING_LINE_89).value)
        == SALARY_COLUMNS[(salary, answer)][INDEX["89"]]
    )


def test_the_part_is_as_printed() -> None:
    part = yaml.safe_load((QUEBEC_PARTS / FILE).read_text("utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    assert part["capabilities"] == [
        {
            "name": "core/subtract",
            "reference": "89",
            "unit": "ca/cad",
            "params": {"rounding": "ca-qc/cent_rounding"},
            "consumes": {
                "amount": "ca-qc/schedule_k_maximum_premium_line_87",
                "less": "ca-qc/schedule_k_months_premium_line_88",
            },
            "produces": {"output": LINE},
        }
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = quebec_kinds().kind(LINE)

    assert kind is SCHEDULE_K_PREMIUM_REMAINING_LINE_89
    assert non_negative(kind)
