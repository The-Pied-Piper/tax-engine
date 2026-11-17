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
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
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
