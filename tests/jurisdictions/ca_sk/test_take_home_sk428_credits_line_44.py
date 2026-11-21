"""SK428 (2025) line 44, the net income from line 23600 of the return, from the salary, real parts.

Form text (Form SK428, CRA 5008-c-25e): "Line 44: Amount from line 23600 of your return". Line 44 is
read as the T1 form exports it, floored, `ca/t1_taxable_income.net_income`, which reaches this form
only as a record list, so it is a core/record_total over it, as line 1 is. The form prints no label
for the line, so the step has no title.

The test composes the T1 employment income form, the real Schedule 8 parts, the real T1 taxable
income parts and the real line part (`sk428_credits_line_44.yaml`), and types in only the salary.
The header and the form declaration are made up here, the form exporting line 44.

The expected figures are computed here, not typed: net income is the salary less the enhanced CPP
deduction, 1% of the pensionable earnings between the $3,500 basic exemption and the $71,300 year's
maximum pensionable earnings, plus the second additional CPP contribution, 4% of the earnings
between $71,300 and $81,200, each rounded half-up to the cent. The hand figures are asserted too
(not a CRA example).
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
LINE_PART = SK_PARTS / "sk428_credits_line_44.yaml"
KIND = "ca-sk/sk428_net_income_line_44"

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-sk/sk428_credits
      required: true
      exports:
        - ca-sk/sk428_net_income_line_44
    capabilities: []
    """)


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    yield from form_parts("t1_taxable_income", "t1_employment_income")
    yield SK_PARTS / "sk428_credits_line_44.yaml"


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


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "19835.00"), ("70000", "69335.00"), ("200000", "198926.00")]
)
def test_line_44_is_the_t1_net_income(tmp_path: Path, salary: str, expected: str) -> None:
    # 70,000: 1% of (70,000 - 3,500) = 665.00 enhanced CPP deduction, so 69,335.00.
    # 200,000: 1% of 67,800 = 678.00 plus 4% of 9,900 = 396.00, so 198,926.00.
    assert _net_income(D(salary)) == D(expected)

    assert _value(_sheet(tmp_path, salary), KIND) == D(expected)


def _step() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def test_the_part_is_one_untitled_record_total_step_over_the_t1_net_income() -> None:
    assert _step() == {
        "name": "core/record_total",
        "reference": "44",
        "unit": "ca/cad",
        "consumes": {"records": "ca/t1_taxable_income.net_income"},
        "produces": {"output": KIND},
    }


def test_line_44_is_a_registered_non_negative_amount_kind() -> None:
    kinds = saskatchewan_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is sk_catalog.SK428_NET_INCOME_LINE_44
