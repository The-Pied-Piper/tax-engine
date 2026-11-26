"""PE428 (2025) line 9, the basic personal amount, as the Prince Edward Island take-home manifest
part wires it.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 9 and line 58040: Basic personal amount Claim
$14,650". The amount is the `ca-pe/basic_personal_amount` dataset, claimed whole through
core/credit_amount, so it is the same at every salary.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_pe
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_pe.catalog import BASIC_PERSONAL_AMOUNT
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import HEADER, SALARY_PARTS, compute, form, value
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
LINE_9 = "ca-pe/basic_personal_amount"
PART_NAME = "pe428_credits_line_9.yaml"
PART = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025" / PART_NAME


@pytest.mark.parametrize("salary", ["20000", "30000", "70000", "200000"])
def test_line_9_is_the_basic_personal_amount_at_every_salary(
    take_home_service: TakeHomeService, salary: str
) -> None:
    service = take_home_service(HEADER, form(LINE_9), *SALARY_PARTS, PART_NAME)

    assert value(compute(service, salary), LINE_9) == D("14650.00")


def test_the_part_is_one_credit_amount_step_over_the_dataset() -> None:
    part: dict[str, Any] = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-pe/pe428_credits"}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/credit_amount",
        "title": "Basic personal amount",
        "reference": "9",
        "unit": "ca/cad",
        "params": {"amount": "ca-pe/basic_personal_amount"},
        "produces": {"output": LINE_9},
    }


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind(LINE_9)

    assert kind is BASIC_PERSONAL_AMOUNT
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
