"""MB428 (2025) line 9, basic personal amount, read from Worksheet MB428, real parts.

Form text (Form MB428, CRA 5007-C, read 2026-11-14): "Line 9 and line 58040: Basic personal amount
(use Worksheet MB428) ^". Worksheet MB428 line 9 says to enter its amount on line 58040 of Form
MB428, so the one step is a core/record_total over the Worksheet MB428 export that gives line 9
(another form reads an export only as a record list), as line 19 reads the Schedule 8 export.

The test composes the real Manitoba salary part, the real Schedule 8 and T1 taxable income parts,
the real parts of Worksheet MB428 lines 1 to 9 and the real line part
(`mb428_credits_line_9.yaml`), and types in only the salary. The header and the two form
declarations are made up here, exporting the lines read, because the shared scaffold owns them.
The figures are hand-computed from the printed forms (not a CRA example): the amount is 15,780.00
while net income is at most $200,000, reduced between $200,000 and $400,000 and 0 from $400,000.
- $300,000: net income 298,926.00, worksheet line 8 = 7,805.26, so 15,780.00 - 7,805.26 = 7,974.74.
- $450,000: net income 448,926.00, worksheet line 8 = 19,640.26, above 15,780.00, so 0.00.
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
import tax_engine.jurisdictions.ca_mb
import tax_engine.jurisdictions.ca_mb.catalog as mb_catalog
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import RecordTotalLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)
from tests.kinds import non_negative

D = Decimal
CENT = D("0.01")
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
LINE_PART = MB_PARTS / "mb428_credits_line_9.yaml"
FORM_NAME = "ca-mb/mb428_credits"
KIND = "ca-mb/mb428_basic_personal_amount_line_9"
WORKSHEET_KIND = "ca-mb/worksheet_mb428_basic_personal_amount_line_9"
WORKSHEET_PARTS = (
    "worksheet_mb428_line_1.yaml",
    "worksheet_mb428_line_2.yaml",
    "worksheet_mb428_line_3.yaml",
    "worksheet_mb428_line_4.yaml",
    "worksheet_mb428_line_5.yaml",
    "worksheet_mb428_line_6.yaml",
    "worksheet_mb428_line_7.yaml",
    "worksheet_mb428_line_8.yaml",
    "worksheet_mb428_line_9.yaml",
)
# The real federal parts the T1 taxable-income form needs, beside the salary and the worksheet.
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-mb/worksheet_mb428
      required: true
      exports:
        - ca-mb/worksheet_mb428_basic_personal_amount_line_1
        - ca-mb/worksheet_mb428_line_2
        - ca-mb/worksheet_mb428_basic_personal_amount_line_3
        - ca-mb/worksheet_mb428_line_4
        - ca-mb/worksheet_mb428_basic_personal_amount_line_5
        - ca-mb/worksheet_mb428_line_6
        - ca-mb/worksheet_mb428_basic_personal_amount_line_7
        - ca-mb/worksheet_mb428_line_8
        - ca-mb/worksheet_mb428_basic_personal_amount_line_9
    capabilities: []
    """)
CREDITS_FORM = dedent("""\
    form:
      name: ca-mb/mb428_credits
      required: true
      exports:
        - ca-mb/mb428_basic_personal_amount_line_9
    capabilities: []
    """)

CASES = [
    ("10000", "15780.00"),
    ("200000", "15780.00"),
    ("300000", "7974.74"),
    ("450000", "0.00"),
]


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    for name in WORKSHEET_PARTS:
        yield MB_PARTS / name
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_credits_form.yaml").write_text(CREDITS_FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=3):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-MB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _net_income(salary: Decimal) -> Decimal:
    """The salary less the enhanced CPP deduction (2025): 1% of the earnings from $3,500 to
    $71,300, plus 4% of the earnings from $71,300 to $81,200."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    return salary - enhanced - second


def _worksheet_amount(salary: Decimal) -> Decimal:
    """The amount by Worksheet MB428: 15,780.00 less 15,780.00 times the share of net income over
    $200,000 of the $200,000 band, never below 0, rounded half-up to the cent."""
    amount = D("15780.00")
    share = max(_net_income(salary) - D("200000"), D(0)) / D("200000")
    return max(amount - _cent(share * amount), D(0)).quantize(CENT)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_9_is_the_worksheet_mb428_basic_personal_amount(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _worksheet_amount(D(salary)) == D(expected)
    sheet = _sheet(tmp_path, salary)
    line_9 = D(sheet.get(manitoba_kinds().kind(KIND)).value)

    assert line_9 == _worksheet_amount(D(salary))
    assert line_9 == D(expected)
    assert str(line_9) == expected
    assert not sheet.get(manitoba_kinds().kind(KIND)).is_blank


def test_the_net_income_at_the_two_reduced_salaries_is_recomputed(tmp_path: Path) -> None:
    assert _net_income(D("300000")) == D("298926.00")
    assert _net_income(D("450000")) == D("448926.00")


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_the_trace_totals_the_one_worksheet_record(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    kind = manitoba_kinds().kind(KIND)

    (line,) = [t for t in sheet.trace if isinstance(t, RecordTotalLine) and t.output == kind]
    assert line.amounts == (D(expected),)
    assert line.total == D(expected)


def _line() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_declares_exactly_one_capability() -> None:
    part = _line()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    assert len(part["capabilities"]) == 1


def test_the_one_step_is_a_titled_record_total_over_the_worksheet_export() -> None:
    (step,) = _line()["capabilities"]

    assert list(step) == ["name", "title", "reference", "unit", "consumes", "produces"]
    assert step == {
        "name": "core/record_total",
        "title": "Basic personal amount",
        "reference": "9",
        "unit": "ca/cad",
        "consumes": {
            "records": "ca-mb/worksheet_mb428.worksheet_mb428_basic_personal_amount_line_9"
        },
        "produces": {"output": KIND},
    }
    assert step["unit"] == "ca/cad"


def test_line_9_is_a_registered_non_negative_amount_kind() -> None:
    kinds = manitoba_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is mb_catalog.MB428_BASIC_PERSONAL_AMOUNT_LINE_9
