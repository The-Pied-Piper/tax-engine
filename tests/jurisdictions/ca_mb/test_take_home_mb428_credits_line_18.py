"""MB428 (2025) line 18, the credits subtotal, as the Manitoba take-home manifest parts wire it.

Form text (Form MB428, CRA 5007-C, read 2026-11-14): "Line 18: Add lines 9, 10, 13, 16, and 17."
Lines 10, 13, 16 and 17 (age, spouse, eligible dependant and infirm dependants amounts) are not
built: a salary-only single filer has none, so only line 9, the basic personal amount, contributes,
at every salary. Alberta's line 25 (`ab428_line_25.yaml`) is the analogue. The form does not name
the line, so the step has no title. The figures are hand-computed from the printed forms (not a CRA
example): line 9 is 15,780.00 while net income is at most $200,000, and net income is 9,935.00 /
198,926.00 at salaries of 10,000 / 200,000.

The test composes the T1 employment income form, the real Schedule 8 and T1 taxable income parts,
the real parts of Worksheet MB428 lines 1 to 9, the real line 9 part (`mb428_credits_line_9.yaml`)
and the real line part (`mb428_credits_line_18.yaml`), and types in only the salary. The header and
the two form declarations are made up here, exporting the lines read, because the shared scaffold
owns them.
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
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SumLine
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
LINE_9_PART = MB_PARTS / "mb428_credits_line_9.yaml"
LINE_PART = MB_PARTS / "mb428_credits_line_18.yaml"
FORM_NAME = "ca-mb/mb428_credits"
LINE_9 = "ca-mb/mb428_basic_personal_amount_line_9"
KIND = "ca-mb/mb428_credits_subtotal_line_18"
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
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-mb/worksheet_mb428
      required: true
      exports:
        - ca-mb/worksheet_mb428_line_1
        - ca-mb/worksheet_mb428_line_2
        - ca-mb/worksheet_mb428_line_3
        - ca-mb/worksheet_mb428_line_4
        - ca-mb/worksheet_mb428_line_5
        - ca-mb/worksheet_mb428_line_6
        - ca-mb/worksheet_mb428_line_7
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
        - ca-mb/mb428_credits_subtotal_line_18
    capabilities: []
    """)

SALARIES = ["10000", "200000"]
EXPECTED = "15780.00"
NET_INCOMES = {
    "10000": "9935.00",
    "200000": "198926.00",
}


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    for name in WORKSHEET_PARTS:
        yield MB_PARTS / name
    yield LINE_9_PART
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


@pytest.mark.parametrize("salary", SALARIES)
def test_line_18_is_line_9_alone_at_every_salary(tmp_path: Path, salary: str) -> None:
    assert _net_income(D(salary)) == D(NET_INCOMES[salary])
    assert _net_income(D(salary)) <= D("200000")
    sheet = _sheet(tmp_path, salary)
    line_18 = sheet.get(manitoba_kinds().kind(KIND))

    assert D(line_18.value) == D(EXPECTED)
    assert str(D(line_18.value)) == EXPECTED
    assert D(line_18.value) == D(sheet.get(manitoba_kinds().kind(LINE_9)).value)
    assert not line_18.is_blank


@pytest.mark.parametrize("salary", SALARIES)
def test_the_trace_sums_line_9_alone(tmp_path: Path, salary: str) -> None:
    sheet = _sheet(tmp_path, salary)
    kinds = manitoba_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, SumLine) and t.output == kinds.kind(KIND)]
    assert [(kind, value) for kind, value in line.parts] == [(kinds.kind(LINE_9), D(EXPECTED))]
    assert line.total == D(EXPECTED)


@pytest.mark.parametrize("salary", SALARIES)
def test_the_sum_is_traced_in_english_with_its_rounding_rule(tmp_path: Path, salary: str) -> None:
    sheet = _sheet(tmp_path, salary)
    kinds = manitoba_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, SumLine) and t.output == kinds.kind(KIND)]
    assert (
        EnglishTraceRenderer().render(line, sheet)
        == "Line 9 (CA$15780.00) gives CA$15780.00 (rounded to the nearest cent)."
    )


def _line() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_declares_exactly_one_capability() -> None:
    part = _line()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    assert len(part["capabilities"]) == 1


def test_the_one_step_is_an_untitled_sum_of_line_9_alone() -> None:
    (step,) = _line()["capabilities"]

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "18",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {"parts": [LINE_9]},
        "produces": {"output": KIND},
    }
    assert "title" not in step


def test_line_18_is_a_registered_non_negative_amount_kind() -> None:
    kinds = manitoba_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is mb_catalog.MB428_CREDITS_SUBTOTAL_LINE_18
