"""Revenu Quebec Schedule K (TP-1.D.K-V, 2025-12), Part C, line 98, as the Quebec take-home manifest
wires it. Printed as "Add lines 90 and 97. Carry the result to line 447 of your return".

`core/sum` adds line 90 and line 97, rounded half-up to the cent by `ca-qc/cent_rounding`. Line 97
is an optional input read as 0 when left out. The group-plan answer to line 50 is checked at each
salary, and a spouse premium is given in the last tests; the form exports the line for TP-1 line
447. Line 84 and boxes 60 to 62 are given straight to the form, so a test can pick the months; the
last tests run the real Part A, B and C chains from a salary. The expected figures are
hand-computed from the printed lines, not an official example.
"""

from __future__ import annotations

import pytest
import yaml

from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_K_PREMIUM_PAYABLE_LINE_98,
    SCHEDULE_K_SPOUSE_PREMIUM_LINE_97,
)
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

LINE = "ca-qc/schedule_k_premium_payable_line_98"
PARTS = PART_D[:10]
FILE = "tp1_schedule_k_line_98.yaml"


@pytest.mark.parametrize("key", list(COLUMNS))
def test_line_98_for_a_line_84_and_the_months_given_to_part_c(
    take_home_service: TakeHomeService, key: tuple[str, str, str]
) -> None:
    sheet = part_d(take_home_service, key, PARTS)

    assert str(sheet.get(SCHEDULE_K_PREMIUM_PAYABLE_LINE_98).value) == COLUMNS[key][INDEX["98"]]


@pytest.mark.parametrize(("salary", "answer"), list(SALARY_COLUMNS))
def test_line_98_at_each_salary_and_answer_to_line_50(
    take_home_service: TakeHomeService, salary: str, answer: str
) -> None:
    sheet = salary_sheet(take_home_service, salary, answer, PARTS)

    assert (
        str(sheet.get(SCHEDULE_K_PREMIUM_PAYABLE_LINE_98).value)
        == SALARY_COLUMNS[(salary, answer)][INDEX["98"]]
    )


def test_the_part_is_as_printed() -> None:
    part = yaml.safe_load((QUEBEC_PARTS / FILE).read_text("utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    assert part["capabilities"] == [
        {
            "name": "core/sum",
            "title": "Premium payable under the Quebec prescription drug insurance plan",
            "reference": "98",
            "unit": "ca/cad",
            "params": {"rounding": "ca-qc/cent_rounding"},
            "consumes": {
                "parts": [
                    "ca-qc/schedule_k_premium_line_90",
                    "ca-qc/schedule_k_spouse_premium_line_97",
                ]
            },
            "blank": {"ca-qc/schedule_k_spouse_premium_line_97": "0"},
            "produces": {"output": LINE},
        }
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = quebec_kinds().kind(LINE)

    assert kind is SCHEDULE_K_PREMIUM_PAYABLE_LINE_98
    assert non_negative(kind)


@pytest.mark.parametrize(
    ("salary", "answer", "expected"),
    [("20000", "default", "100.00"), ("70000", "default", "855.00"), ("70000", "yes", "100.00")],
)
def test_line_98_adds_a_spouse_premium_given_on_line_97(
    take_home_service: TakeHomeService, salary: str, answer: str, expected: str
) -> None:
    sheet = salary_sheet(
        take_home_service,
        salary,
        answer,
        PARTS,
        (SCHEDULE_K_SPOUSE_PREMIUM_LINE_97, "100.00"),
    )

    assert str(sheet.get(SCHEDULE_K_PREMIUM_PAYABLE_LINE_98).value) == expected


def test_the_form_declaration_exports_line_98() -> None:
    declaration = yaml.safe_load((QUEBEC_PARTS / "tp1_schedule_k.yaml").read_text("utf-8"))

    assert LINE in declaration["form"]["exports"]
