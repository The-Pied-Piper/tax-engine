"""SK428 (2025) line 48, line 43 minus line 47, not below zero, from the salary, real parts.

Form text (Form SK428, CRA 5008-c-25e): "Line 43 and line 58689: Amount from line 33099 of your
return" and "Line 48: Line 43 minus line 47 (if negative, enter "0") =". Line 48 is one
core/subtract_not_below_zero step over line 43, the optional medical expenses input
(`sk428_credits_line_43_input.yaml`), and line 47 (`sk428_credits_line_47.yaml`). A request that
leaves line 43 blank has no medical expenses, so the blank is read as 0 and line 48 is 0.00. The
form prints no label for the line, so the step has no title.

The test composes the T1 employment income form, the real Schedule 8 and T1 taxable income
parts and the real lines 43, 44, 46, 47 and 48 parts, and types in the salary and, where a case
gives it, line 43. The header and the form declaration are made up here, the form exporting line 48.

The hand figures are asserted (not a CRA example): net income is the salary less the enhanced CPP
deduction, line 47 is the lesser of 3% of it and 2,681.00, and line 48 is line 43 less line 47, not
below 0.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_sk
import tax_engine.jurisdictions.ca_sk.catalog as sk_catalog
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)
from tests.kinds import non_negative

D = Decimal
CENT = D("0.01")
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
FORM_NAME = "ca-sk/sk428_credits"
LINE_PART = SK_PARTS / "sk428_credits_line_48.yaml"
LINE_43 = "ca-sk/sk428_medical_expenses_line_43"
LINE_47 = "ca-sk/sk428_medical_expenses_limited_amount_line_47"
KIND = "ca-sk/sk428_medical_expenses_over_limit_line_48"

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-sk/sk428_credits
      required: true
      exports:
        - ca-sk/sk428_medical_expenses_over_limit_line_48
    capabilities: []
    """)


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    yield from form_parts("t1_taxable_income", "t1_employment_income")
    yield SK_PARTS / "sk428_credits_line_43_input.yaml"
    yield SK_PARTS / "sk428_credits_line_44.yaml"
    yield SK_PARTS / "sk428_credits_line_46.yaml"
    yield SK_PARTS / "sk428_credits_line_47.yaml"
    yield SK_PARTS / "sk428_credits_line_48.yaml"


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Saskatchewan manifest of a test header, a form declaration and
    the real part files, every other namespace being the Saskatchewan package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    roots = {**saskatchewan_packages().roots(), Namespace("ca-sk"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, saskatchewan_kinds(), saskatchewan_units()),
        YamlParameterSource(
            saskatchewan_packages().roots(), saskatchewan_parameter_parsers(), saskatchewan_units()
        ),
        saskatchewan_capabilities(),
    )


def _sheet(
    tmp_path: Path, salary: str, line_43: str | None = None, line_49: str | None = None
) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_43 is not None:
        given.append(Artifact(sk_catalog.SK428_MEDICAL_EXPENSES_LINE_43, D(line_43)))
    if line_49 is not None:
        given.append(
            Artifact(sk_catalog.SK428_OTHER_DEPENDANTS_MEDICAL_EXPENSES_LINE_49, D(line_49))
        )
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-SK"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(saskatchewan_kinds().kind(identifier)).value)


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _net_income(salary: Decimal) -> Decimal:
    """The salary less the enhanced CPP deduction (2025): 1% of the earnings from $3,500 to
    $71,300, plus 4% of the earnings from $71,300 to $81,200, each half-up to the cent."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    return salary - enhanced - second


def _line_46(salary: Decimal) -> Decimal:
    return _cent(_net_income(salary) * D("0.03"))


def _line_47(salary: Decimal) -> Decimal:
    return min(D("2681"), _line_46(salary))


# salary, line 43, line 48. Line 47 is 595.05 at 20,000 and 2,080.05 at 70,000 (3% of net income
# 19,835.00 / 69,335.00), and 2,681.00 at 200,000 (the ceiling).
CASES = [
    ("70000", None, "0.00"),
    ("70000", "5000.00", "2919.95"),
    ("70000", "1000.00", "0.00"),
    ("200000", "5000.00", "2319.00"),
]


@pytest.mark.parametrize(("salary", "line_43", "expected"), CASES)
def test_line_48_is_line_43_less_line_47_not_below_zero(
    tmp_path: Path, salary: str, line_43: str | None, expected: str
) -> None:
    # 70,000 with 5,000.00: 5,000.00 - 2,080.05 = 2,919.95. With 1,000.00: 1,000.00 - 2,080.05
    # is negative, so 0.00. 200,000 with 5,000.00: 5,000.00 - 2,681.00 = 2,319.00. Blank: 0.00.
    assert max(D(line_43 or "0") - _line_47(D(salary)), D(0)) == D(expected)

    assert _value(_sheet(tmp_path, salary, line_43), KIND) == D(expected)


def _step() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def test_the_part_is_one_untitled_subtract_not_below_zero_step_with_a_blank_line_43() -> None:
    assert _step() == {
        "name": "core/subtract_not_below_zero",
        "reference": "48",
        "unit": "ca/cad",
        "params": {"rounding": "ca-sk/cent_rounding"},
        "consumes": {"amount": LINE_43, "less": LINE_47},
        "blank": {"amount": "0"},
        "produces": {"output": KIND},
    }


def test_line_48_is_a_registered_non_negative_amount_kind() -> None:
    kinds = saskatchewan_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is sk_catalog.SK428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_48
