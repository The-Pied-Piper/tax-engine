"""ON428 (2025) line 37, the net income from line 23600 of the return, from the salary, real parts.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 37: Amount from line 23600 of your return". Line
37 is read as the T1 form exports it, floored, `ca/t1_taxable_income.net_income`, which reaches this
form only as a record list, so it is a core/record_total over it, as line 1 is. The form prints no
label for the line, so the step has no title.

The test runs the real take-home manifest and types in only the salary. The expected figures are
computed here, not typed: net income is the salary less the enhanced CPP deduction, 1% of the
pensionable earnings between the $3,500 basic exemption and the $71,300 year's maximum pensionable
earnings, plus the second additional CPP contribution, 4% of the earnings between $71,300 and
$81,200, each rounded half-up to the cent. The hand figures are asserted too (not a CRA example).
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_on
from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_on.catalog import ON428_NET_INCOME_LINE_37
from tests.kinds import bundled_kinds, non_negative

D = Decimal
CENT = D("0.01")
LINE_PART = Path(tax_engine.jurisdictions.ca_on.__file__).parent / (
    "manifests/2025/on428_line_37.yaml"
)
KIND = "ca-on/on428_net_income_line_37"
CASES = [
    ("20000", "19835.00"),
    ("200000", "198926.00"),
]


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _net_income(salary: Decimal) -> Decimal:
    """The salary less the enhanced CPP deduction (2025): 1% of the earnings from $3,500 to
    $71,300, plus 4% of the earnings from $71,300 to $81,200."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    return salary - enhanced - second


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_37_is_the_t1_net_income(salary: str, expected: str) -> None:
    assert _net_income(D(salary)) == D(expected)

    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-ON"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (sheet,) = worksheets["ca-on/on428"]

    assert sheet.get(ON428_NET_INCOME_LINE_37).value == D(expected)


def _step() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-on/on428"}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def test_the_part_is_one_untitled_record_total_step_over_the_t1_net_income() -> None:
    assert _step() == {
        "name": "core/record_total",
        "reference": "37",
        "unit": "ca/cad",
        "consumes": {"records": "ca/t1_taxable_income.net_income"},
        "produces": {"output": KIND},
    }


def test_line_37_is_a_registered_non_negative_amount_kind() -> None:
    kinds = bundled_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is ON428_NET_INCOME_LINE_37
