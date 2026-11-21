"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part A, line 10, as the Quebec take-home
manifest wires it. Printed as "Total income ... plus the amount for income averaging for forest
producers".

Line 10 reads TP-1 line 199 (`core/record_total`) and adds the forest producers' averaging amount of
line 276 (`core/sum`, rounded half-up to the cent by `ca-qc/cent_rounding`). Line 276 is an optional
input, read as 0 when the caller leaves it out.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_FOREST_PRODUCER_AVERAGING_LINE_276,
    TP1_LINE_164,
    TP1_SCHEDULE_F_INCOME_LINE_10,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import SALARY_PARTS

D = Decimal

PARTS = (
    *SALARY_PARTS,
    "tp1_income.yaml",
    "tp1_income_line_105_input.yaml",
    "tp1_income_line_107_input.yaml",
    "tp1_income_line_box_211_input.yaml",
    "tp1_income_line_110_input.yaml",
    "tp1_income_line_111_input.yaml",
    "tp1_income_line_114_input.yaml",
    "tp1_income_line_119_input.yaml",
    "tp1_income_line_122_input.yaml",
    "tp1_income_line_123_input.yaml",
    "tp1_income_line_128_input.yaml",
    "tp1_income_line_130_input.yaml",
    "tp1_income_line_136_input.yaml",
    "tp1_income_line_139_input.yaml",
    "tp1_income_line_142_input.yaml",
    "tp1_income_line_147_input.yaml",
    "tp1_income_line_148_input.yaml",
    "tp1_income_line_154_input.yaml",
    "tp1_income_line_164_input.yaml",
    "tp1_income_line_199.yaml",
    "tp1_income_line_97_input.yaml",
    "tp1_income_line_97.yaml",
    "tp1_income_line_98_input.yaml",
    "tp1_income_line_98.yaml",
    "tp1_income_line_98_1_input.yaml",
    "tp1_income_line_98_1.yaml",
    "tp1_income_line_98_2_input.yaml",
    "tp1_income_line_98_2.yaml",
    "tp1_schedule_f_line_10_input.yaml",
    "tp1_schedule_f_line_10.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    """)
FORM = dedent("""\
    form:
      name: ca-qc/tp1_schedule_f
      required: true
      exports:
        - ca-qc/tp1_schedule_f_income_line_10
    """)


def schedule_f(
    take_home_service: TakeHomeService, salary: str, *given: tuple[AmountKind, str]
) -> Worksheet:
    """The Schedule F worksheet for a salary; every optional input is left out unless in `given`."""
    starting = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    starting.extend(Artifact(kind, D(value)) for kind, value in given)
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"), 2025, *starting
    )["ca-qc/tp1_schedule_f"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "20000.00"), ("70000", "70000.00"), ("200000", "200000.00")],
)
def test_a_salary_only_line_10_is_line_199(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = schedule_f(take_home_service, salary).get(TP1_SCHEDULE_F_INCOME_LINE_10).value

    assert str(value) == expected


def test_the_forest_averaging_amount_is_added(take_home_service: TakeHomeService) -> None:
    given = (TP1_FOREST_PRODUCER_AVERAGING_LINE_276, "1234.56")
    value = schedule_f(take_home_service, "70000", given).get(TP1_SCHEDULE_F_INCOME_LINE_10).value

    assert str(value) == "71234.56"


def test_the_sum_is_rounded_half_up_to_the_cent(take_home_service: TakeHomeService) -> None:
    given = (TP1_FOREST_PRODUCER_AVERAGING_LINE_276, "0.005")
    value = schedule_f(take_home_service, "70000", given).get(TP1_SCHEDULE_F_INCOME_LINE_10).value

    assert str(value) == "70000.01"


def test_a_business_loss_above_the_salary_gives_a_negative_line_10(
    take_home_service: TakeHomeService,
) -> None:
    """TP-1 line 199 is signed (a business loss is a minus), so line 10 carries it as printed:
    20,000.00 - 50,000.00 = -30,000.00."""
    given = (TP1_LINE_164, "-50000")
    value = schedule_f(take_home_service, "20000", given).get(TP1_SCHEDULE_F_INCOME_LINE_10).value

    assert str(value) == "-30000.00"
