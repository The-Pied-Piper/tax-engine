"""T1 line 68 and line 25700 "Add lines 58 to 67.", from the Ontario take-home manifest's part file.

Three `core/sum` steps add the ten printed lines 24400 to 25600: two unprinted subtotals of five,
each line read as 0 when the caller leaves it out, and the printed line adding the two, rounded
half-up to the cent. The part is composed here under a test-local header and form declaration with
the inputs part that declares the ten lines. The expected figures
are hand-added from the printed lines, not a CRA example.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca.catalog.taxable_income import (
    DEDUCTIONS_FROM_NET_INCOME,
    T1_LINE_24400,
    T1_LINE_25100,
    T1_LINE_25400,
    T1_LINE_25500,
    T1_LINE_25600,
)
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
PARTS = ("t1_taxable_income_line_25700_inputs.yaml", "t1_taxable_income_line_25700.yaml")
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: [ca/t1_line_25400]
capabilities: []
"""
FORM = """\
form:
  name: ca/t1_taxable_income
  required: true
  exports:
    - ca/deductions_from_net_income
"""


def line_25700(take_home_service: TakeHomeService, *given: Artifact[Decimal]) -> Decimal:
    service = take_home_service(HEADER, FORM, *PARTS)
    (worksheet,) = service.compute(ONTARIO, 2025, *given)["ca/t1_taxable_income"]
    return worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value


def test_a_salary_only_caller_has_no_deductions_from_net_income(
    take_home_service: TakeHomeService,
) -> None:
    assert line_25700(take_home_service) == D("0.00")


def test_line_25700_adds_the_lines_the_caller_gives(take_home_service: TakeHomeService) -> None:
    given = (Artifact(T1_LINE_25400, D("1000")), Artifact(T1_LINE_25100, D("250.50")))

    assert line_25700(take_home_service, *given) == D("1250.50")


def test_line_25700_adds_the_first_and_the_last_line(take_home_service: TakeHomeService) -> None:
    given = (Artifact(T1_LINE_24400, D("300")), Artifact(T1_LINE_25600, D("0.25")))

    assert line_25700(take_home_service, *given) == D("300.25")


@pytest.mark.parametrize(("amount", "expected"), [("10.005", "10.01"), ("10.004", "10.00")])
def test_the_printed_line_is_rounded_half_up_to_the_cent(
    take_home_service: TakeHomeService, amount: str, expected: str
) -> None:
    given = Artifact(T1_LINE_25500, D(amount))

    assert line_25700(take_home_service, given) == D(expected)


def test_the_printed_line_rounds_once_so_sub_cent_parts_in_different_subtotals_add_first(
    take_home_service: TakeHomeService,
) -> None:
    given = (Artifact(T1_LINE_24400, D("0.005")), Artifact(T1_LINE_25500, D("0.005")))

    assert line_25700(take_home_service, *given) == D("0.01")


FIRST = [f"ca/t1_line_{line}" for line in ("24400", "24900", "25000", "25100", "25200")]
LAST = [f"ca/t1_line_{line}" for line in ("25300", "25395", "25400", "25500", "25600")]


def _subtotal(title: str, parts: list[str], output: str) -> dict[str, object]:
    return {
        "name": "core/sum",
        "title": title,
        "unit": "ca/cad",
        "params": {"rounding": "ca/exact_rounding"},
        "consumes": {"parts": parts},
        "blank": {name: "0" for name in parts},
        "produces": {"output": f"ca/{output}"},
    }


def test_the_part_is_two_subtotals_and_a_sum_with_the_lines_read_as_zero() -> None:
    path = next(TAKE_HOME.rglob("t1_taxable_income_line_25700.yaml"))
    part: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca/t1_taxable_income"}
    first, last, step = part["capabilities"]
    # Two unprinted subtotals keep the sentence of the numbered line short; the line adds them.
    assert first == _subtotal(
        "Lines 24400 to 25200 added up", FIRST, "t1_lines_24400_to_25200_subtotal"
    )
    assert last == _subtotal(
        "Lines 25300 to 25600 added up", LAST, "t1_lines_25300_to_25600_subtotal"
    )
    assert step == {
        "name": "core/sum",
        "title": "Deductions from net income",
        "reference": "25700",
        "unit": "ca/cad",
        "params": {"rounding": "ca/cent_rounding"},
        "consumes": {
            "parts": [
                "ca/t1_lines_24400_to_25200_subtotal",
                "ca/t1_lines_25300_to_25600_subtotal",
            ]
        },
        "produces": {"output": "ca/deductions_from_net_income"},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    assert isinstance(DEDUCTIONS_FROM_NET_INCOME, AmountKind)
    assert DEDUCTIONS_FROM_NET_INCOME.non_negative
