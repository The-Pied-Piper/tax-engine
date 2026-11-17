"""ON428 (2025) line 27, the pension income amount, rejected above its printed maximum.

Form text (Form ON428, Ontario Tax, CRA 5006-c-25e.txt line 117): "Line 27 and line 58360: Pension
income amount (maximum $1,762)". No arithmetic is printed, so line 27 is an entry line: the entered
amount is rejected above the printed maximum, not capped. The maximum is the
`ca-on/pension_income_amount_maximum` dataset, supplied by a first `core/credit_amount` step that
carries no title, no reference and no line number (it is not a line of the form); the second step,
`core/at_most`, is line 27 and carries "Pension income amount" and "27". The input defaults to 0,
so no blank rule is needed.

The real input part and the new `on428_line_27.yaml` are loaded under a test-local header and form,
the shared scaffold owning those, and only the salary is typed in (plus the pension amount).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_on.catalog import ON428_PENSION_INCOME_AMOUNT
from tests.jurisdictions.ca_on.conftest import ONTARIO_PARTS, TakeHomeService
from tests.kinds import bundled_kinds, non_negative

D = Decimal
PART = "on428_line_27.yaml"
INPUTS_PART = "on428_line_27_inputs.yaml"
MAXIMUM = "ca-on/on428_pension_income_amount_maximum"
LINE_27 = "ca-on/on428_pension_income_amount_line_27"
PENSION = "ca-on/on428_pension_income_amount"
FORM_NAME = "ca-on/on428"

HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: ca/employment_income
    required: true
outputs:
  - ca/employment_income
"""
FORM = """\
form:
  name: ca-on/on428
  required: true
  exports:
    - ca-on/on428_pension_income_amount_line_27
"""


def _line_27(take_home_service: TakeHomeService, pension: str | None = None) -> Decimal:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D("70000"))]
    if pension is not None:
        given.append(Artifact(ON428_PENSION_INCOME_AMOUNT, D(pension)))
    service = take_home_service(HEADER, FORM, INPUTS_PART, PART)
    worksheets = service.compute(JurisdictionCode("CA-ON"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return D(sheet.get(bundled_kinds().kind(LINE_27)).value)


def test_an_amount_at_the_maximum_passes_unchanged(take_home_service: TakeHomeService) -> None:
    assert _line_27(take_home_service, "1762") == D("1762.00")


def test_an_amount_below_the_maximum_passes_unchanged(take_home_service: TakeHomeService) -> None:
    assert _line_27(take_home_service, "250.50") == D("250.50")


def test_an_amount_of_zero_passes(take_home_service: TakeHomeService) -> None:
    assert _line_27(take_home_service, "0") == D("0")


def test_a_salary_only_run_reads_the_default_0(take_home_service: TakeHomeService) -> None:
    assert _line_27(take_home_service) == D("0")


def test_one_cent_above_the_maximum_is_rejected_not_capped(
    take_home_service: TakeHomeService,
) -> None:
    with pytest.raises(InputAboveBoundError):
        _line_27(take_home_service, "1762.01")


def _part() -> dict[str, Any]:
    part = yaml.safe_load((ONTARIO_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_two_steps_in_order() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    first, second = part["capabilities"]
    assert first["name"] == "core/credit_amount"
    assert second["name"] == "core/at_most"


def test_the_first_step_supplies_the_printed_maximum_with_no_title_and_no_reference() -> None:
    first, _ = _part()["capabilities"]

    assert "title" not in first
    assert "reference" not in first
    assert first == {
        "name": "core/credit_amount",
        "unit": "ca/cad",
        "params": {"amount": "ca-on/pension_income_amount_maximum"},
        "produces": {"output": MAXIMUM},
    }


def test_the_second_step_is_line_27_titled_and_referenced() -> None:
    _, second = _part()["capabilities"]

    assert second == {
        "name": "core/at_most",
        "title": "Pension income amount",
        "reference": "27",
        "unit": "ca/cad",
        "consumes": {"amount": PENSION, "bound": MAXIMUM},
        "produces": {"output": LINE_27},
    }


@pytest.mark.parametrize("identifier", [MAXIMUM, LINE_27])
def test_each_new_kind_is_a_registered_non_negative_decimal_amount_kind(identifier: str) -> None:
    kind = bundled_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
