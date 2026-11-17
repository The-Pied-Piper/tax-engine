"""AB428 line 72, the political contributions credit checked against its printed maximum.

Form text (Form AB428, CRA 5009-c-25e.txt line 238, confirmed): "Line 72: Alberta political
contributions tax credit (use Worksheet AB428) (maximum $1,000)". Worksheet AB428 is not built, so
line 72 is an entry line: an amount typed above the printed maximum is rejected with
`InputAboveBoundError` (a `ValidationError`), not capped. The maximum is a dataset figure
(`ca-ab/political_contributions_tax_credit_maximum`), never an input.

Two parts make the line. `ab428_political_contributions_tax_credit_maximum.yaml` is
`core/credit_amount` over that dataset and produces the maximum kind; it carries no line number in
its title, reference or kind name. `ab428_line_72.yaml` is `core/at_most`, consuming the optional
input `ca-ab/ab428_political_contributions_credit_line_72` (name and null default unchanged)
against that maximum, with the blank rule `pass_on` (a blank input leaves line 72 blank), and
producing `ca-ab/ab428_alberta_political_contributions_tax_credit_line_72`, which line 73 reads.

The behaviour is checked through the registered engine over the real Alberta manifest with the
salary (70,000, where line 70 is 3,598.12 in 2025 and 3,534.79 in 2026) and, where stated, the
credit typed in.
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
from tax_engine.domain.errors import InputAboveBoundError, ValidationError
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
MAXIMUM_PART = PARTS / "ab428_political_contributions_tax_credit_maximum.yaml"
LINE_PART = PARTS / "ab428_line_72.yaml"
INPUT_PART = PARTS / "ab428_line_72_input.yaml"
INPUT = "ca-ab/ab428_political_contributions_credit_line_72"
MAXIMUM = "ca-ab/political_contributions_tax_credit_maximum"
LINE_72 = "ca-ab/ab428_alberta_political_contributions_tax_credit_line_72"
LINE_70 = "ca-ab/ab428_tax_line_70"
LINE_73 = "ca-ab/ab428_tax_line_73"
RETURN = "ca-ab/return"
LINE_167 = "ca/refund_or_balance_owing"
FORM = "ca-ab/ab428"
SALARY = "70000"
LINE_70_AT_SALARY = {2025: D("3598.12"), 2026: D("3534.79")}
# Salary-only T1 line 167 (the take-home is the salary less CPP, EI and this), unchanged.
LINE_167_AT_SALARY = {2025: D("11183.76"), 2026: D("10812.98")}


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def _figure(sheet: Worksheet, name: str) -> Any:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _sheet(year: int, credit: str | None = None) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(SALARY))]
    if credit is not None:
        given.append(Artifact(artifact_kinds().kind(INPUT), D(credit)))
    worksheets = build_tax_computation().compute(ALBERTA, year, *given)
    (sheet,) = worksheets[FORM]
    return sheet


def test_the_maximum_part_is_one_credit_amount_step_with_no_line_number() -> None:
    part = _part(MAXIMUM_PART)

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step["name"] == "core/credit_amount"
    assert step["title"] == "Political contributions tax credit maximum"
    assert "reference" not in step
    assert step["params"] == {"amount": MAXIMUM}
    assert step["produces"] == {"output": MAXIMUM}
    assert "consumes" not in step
    assert "72" not in MAXIMUM


def test_the_line_72_part_is_one_at_most_step_that_passes_a_blank_on() -> None:
    part = _part(LINE_PART)

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step["name"] == "core/at_most"
    assert step["title"] == "Alberta political contributions tax credit"
    assert step["reference"] == "72"
    assert step["unit"] == "ca/cad"
    assert step["consumes"] == {"amount": INPUT, "bound": MAXIMUM}
    assert step["blank"] == {"amount": "pass_on"}
    assert step["produces"] == {"output": LINE_72}
    assert "params" not in step


def test_the_input_keeps_its_name_and_default_of_null() -> None:
    part = _part(INPUT_PART)

    (declared,) = part["inputs"]
    assert declared["name"] == INPUT
    assert declared["required"] is False
    assert declared["default"] is None


def test_line_73_reads_the_line_72_output_not_the_input() -> None:
    part = _part(PARTS / "ab428_line_73.yaml")

    (step,) = part["capabilities"]
    assert step["consumes"] == {"amount": LINE_70, "less": LINE_72}
    assert step["blank"] == {"less": "0"}


@pytest.mark.parametrize("identifier", [MAXIMUM, LINE_72])
def test_the_new_kinds_are_registered_non_negative_decimal_amount_kinds(identifier: str) -> None:
    kind = alberta_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)


@pytest.mark.parametrize("year", [2025, 2026])
def test_a_salary_only_request_leaves_line_72_blank_and_line_73_equals_line_70(year: int) -> None:
    sheet = _sheet(year)

    assert sheet.get(alberta_kinds().kind(LINE_72)).is_blank
    assert _figure(sheet, LINE_73) == LINE_70_AT_SALARY[year]
    assert _figure(sheet, LINE_70) == LINE_70_AT_SALARY[year]


@pytest.mark.parametrize("year", [2025, 2026])
def test_the_salary_only_return_figure_is_unchanged(year: int) -> None:
    (summary,) = build_tax_computation().compute(
        ALBERTA, year, Artifact(EMPLOYMENT_INCOME, D(SALARY))
    )[RETURN]

    assert _figure(summary, LINE_167) == LINE_167_AT_SALARY[year]


def test_the_maximum_is_1000_in_2025() -> None:
    assert _figure(_sheet(2025), MAXIMUM) == D("1000.00")


def test_the_maximum_is_1000_in_2026() -> None:
    assert _figure(_sheet(2026), MAXIMUM) == D("1000.00")


def test_an_amount_exactly_at_the_maximum_passes_and_reduces_line_73() -> None:
    sheet = _sheet(2025, "1000.00")

    assert _figure(sheet, LINE_72) == D("1000.00")
    assert _figure(sheet, LINE_73) == LINE_70_AT_SALARY[2025] - D("1000.00")
    assert _figure(sheet, LINE_73) == D("2598.12")


def test_an_amount_below_the_maximum_passes_unchanged() -> None:
    assert _figure(_sheet(2025, "250.50"), LINE_72) == D("250.50")


def test_an_amount_of_zero_passes() -> None:
    assert _figure(_sheet(2025, "0"), LINE_72) == D("0")


def test_an_amount_one_cent_above_the_maximum_is_rejected_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        _sheet(2025, "1000.01")


def test_the_rejection_is_a_validation_error() -> None:
    with pytest.raises(ValidationError):
        _sheet(2025, "1000.01")


def test_the_rejection_names_both_kinds() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        _sheet(2025, "1000.01")

    assert INPUT in str(raised.value)
    assert MAXIMUM in str(raised.value)


def test_a_2026_amount_at_its_maximum_passes() -> None:
    assert _figure(_sheet(2026, "1000.00"), LINE_72) == D("1000.00")


def test_a_2026_amount_one_cent_above_the_maximum_is_rejected() -> None:
    with pytest.raises(InputAboveBoundError):
        _sheet(2026, "1000.01")


def test_the_trace_has_one_at_most_line_and_one_credit_amount_line_for_the_maximum() -> None:
    sheet = _sheet(2025, "500.00")

    at_most = [line for line in sheet.trace if isinstance(line, AtMostLine)]
    maximum = [
        line
        for line in sheet.trace
        if isinstance(line, CreditAmountLine) and line.output.identifier == MAXIMUM
    ]
    (line_72,) = [line for line in at_most if line.output.identifier == LINE_72]
    (maximum_line,) = maximum
    assert line_72.amount_kind.identifier == INPUT
    assert line_72.amount_value == D("500.00")
    assert line_72.bound.identifier == MAXIMUM
    assert line_72.bound_value == D("1000.00")
    assert maximum_line.value == D("1000.00")
