"""AB428 line 34, the pension income amount checked against its printed maximum, real parts.

Form text (Form AB428, CRA 5009-c-25e.txt line 142, confirmed): "Line 34 and line 58360: Pension
income amount (maximum $1,719) ^". Line 34 is an entry line with no worksheet: an amount typed above
the printed maximum is rejected with `InputAboveBoundError`, not capped. The maximum is a dataset
figure (`ca-ab/pension_income_amount_maximum`), never an input.

Two parts make the line. `ab428_pension_income_amount_maximum.yaml` is `core/credit_amount` over
that dataset and produces `ca-ab/pension_income_amount_maximum`; the maximum is an intermediate
step and carries no line number in its title, reference or kind name. `ab428_credits_line_34.yaml`
is `core/at_most`, consuming the `ca-ab/ab428_pension_income_amount` input against that maximum and
producing `ca-ab/ab428_pension_income_amount_line_34`, the figure of line 34 that line 36 adds.

The part layout is checked on the real files; the behaviour is checked through the registered
engine over the real Alberta manifest with the salary and, where stated, the pension income amount
typed in. The figures at 1,719.00 and 1,719.01 follow from the printed maximum; the 2026 ones from
the provisional 2026 maximum of 1,753.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_ab
from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.trace import AtMostLine, CreditAmountLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import artifact_kinds
from tests.jurisdictions.ca_ab.support import alberta_kinds
from tests.kinds import non_negative

D = Decimal
ALBERTA = JurisdictionCode("CA-AB")
PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
MAXIMUM_PART = PARTS / "ab428_pension_income_amount_maximum.yaml"
LINE_PART = PARTS / "ab428_credits_line_34.yaml"
INPUT = "ca-ab/ab428_pension_income_amount"
MAXIMUM = "ca-ab/pension_income_amount_maximum"
LINE_34 = "ca-ab/ab428_pension_income_amount_line_34"
LINE_36 = "ca-ab/ab428_credits_subtotal_line_36"
LINE_33 = "ca-ab/ab428_credits_subtotal_line_33"
CREDITS = "ca-ab/ab428_credits"
# Salary 70,000: line 33 is 26,692.23 without any pension income amount (line 36 test).
SALARY = "70000"
LINE_33_AT_SALARY = D("26692.23")


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _credits(year: int, pension: str | None = None) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(SALARY))]
    if pension is not None:
        given.append(Artifact(artifact_kinds().kind(INPUT), D(pension)))
    worksheets = build_tax_computation().compute(ALBERTA, year, *given)
    (sheet,) = worksheets[CREDITS]
    return sheet


def test_the_maximum_part_is_one_credit_amount_step_with_no_line_number() -> None:
    part = _part(MAXIMUM_PART)

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": CREDITS}
    (step,) = part["capabilities"]
    assert step["name"] == "core/credit_amount"
    assert step["title"] == "Pension income amount maximum"
    assert "reference" not in step
    assert step["params"] == {"amount": MAXIMUM}
    assert step["produces"] == {"output": MAXIMUM}
    assert "consumes" not in step


def test_the_line_34_part_is_one_at_most_step_over_the_input_and_the_maximum() -> None:
    part = _part(LINE_PART)

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": CREDITS}
    (step,) = part["capabilities"]
    assert step["name"] == "core/at_most"
    assert step["title"] == "Pension income amount"
    assert step["reference"] == "34"
    assert step["consumes"] == {"amount": INPUT, "bound": MAXIMUM}
    assert step["produces"] == {"output": LINE_34}
    assert "params" not in step


def test_the_input_keeps_its_name_and_default_of_0() -> None:
    part = _part(PARTS / "ab428_line_34_inputs.yaml")

    (declared,) = part["inputs"]
    assert declared["name"] == INPUT
    assert declared["required"] is False
    assert declared["default"] == "0"


@pytest.mark.parametrize("identifier", [MAXIMUM, LINE_34])
def test_the_new_kinds_are_registered_non_negative_decimal_amount_kinds(identifier: str) -> None:
    kind = alberta_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)


def test_a_salary_only_request_has_line_34_of_0_and_line_36_unchanged() -> None:
    sheet = _credits(2025)

    assert _figure(sheet, LINE_34) == D("0")
    assert _figure(sheet, LINE_36) == LINE_33_AT_SALARY


def test_the_maximum_is_1719_in_2025() -> None:
    assert _figure(_credits(2025), MAXIMUM) == D("1719.00")


def test_the_maximum_is_1753_in_2026() -> None:
    assert _figure(_credits(2026), MAXIMUM) == D("1753.00")


def test_an_amount_exactly_at_the_maximum_passes_and_flows_into_line_36() -> None:
    sheet = _credits(2025, "1719.00")

    assert _figure(sheet, LINE_34) == D("1719.00")
    assert _figure(sheet, LINE_36) == LINE_33_AT_SALARY + D("1719.00")


def test_an_amount_below_the_maximum_passes_unchanged() -> None:
    assert _figure(_credits(2025, "1000.00"), LINE_34) == D("1000.00")


def test_an_amount_one_cent_above_the_maximum_is_rejected() -> None:
    with pytest.raises(InputAboveBoundError):
        _credits(2025, "1719.01")


def test_the_rejection_names_both_kinds() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        _credits(2025, "1719.01")

    assert INPUT in str(raised.value)
    assert MAXIMUM in str(raised.value)


def test_a_2026_amount_at_its_maximum_of_1753_passes() -> None:
    sheet = _credits(2026, "1753.00")

    assert _figure(sheet, LINE_34) == D("1753.00")


def test_a_2026_amount_one_cent_above_1753_is_rejected() -> None:
    with pytest.raises(InputAboveBoundError):
        _credits(2026, "1753.01")


def test_the_2025_maximum_does_not_bound_a_2026_request() -> None:
    # 1,719.01 is above the 2025 maximum but below the 2026 one of 1,753.
    assert _figure(_credits(2026, "1719.01"), LINE_34) == D("1719.01")


def test_the_trace_has_one_at_most_line_and_one_credit_amount_line_for_the_maximum() -> None:
    sheet = _credits(2025, "1000.00")

    at_most = [line for line in sheet.trace if isinstance(line, AtMostLine)]
    maximum = [
        line
        for line in sheet.trace
        if isinstance(line, CreditAmountLine) and line.output.identifier == MAXIMUM
    ]
    (line_34,) = at_most
    (maximum_line,) = maximum
    assert line_34.output.identifier == LINE_34
    assert line_34.amount_kind.identifier == INPUT
    assert line_34.amount_value == D("1000.00")
    assert line_34.bound.identifier == MAXIMUM
    assert line_34.bound_value == D("1719.00")
    assert maximum_line.value == D("1719.00")
