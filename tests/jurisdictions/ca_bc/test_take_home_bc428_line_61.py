"""BC428 (2025) line 61, British Columbia tax on taxable income from line 8 or 15, real parts.

Form text (Form BC428, CRA 5010-C, read 2026-11-14): "Line 61: British Columbia tax on taxable
income from line 8 or 15 ^". Under line 8: "If you completed lines 2 to 8 for a column above,
enter the amount from line 8 on line 61 and continue on line 16." Under line 15: "If you completed
lines 9 to 15 for a column above, enter the amount from line 15 on line 61 and continue on line 16."

Line 61 is one calculation step, the British Columbia capability `ca-bc/tax_on_taxable_income`
(`bc428_line_61.yaml`), not a copy line. Lines 8, 15 and 61 are on one form, `ca-bc/bc428`, so the
step consumes the two plain amounts (not record lists, as Alberta's does across forms) and gives
the one that has a figure; the other is blank because line 1 is outside its table. Its output is
`ca-bc/bc428_british_columbia_tax_on_taxable_income_line_61`.

The salary is the only input. Line 61 is composed from the real parts that lead to it: the salary,
the federal T1 taxable income parts, line 1, lines 3 to 8 and lines 10 to 15 (`bc428_line_*.yaml`)
and line 61. The form declaration is test-local (the real `bc428.yaml` exports line 91, which is not
built). The service is built over the package list of `support.py`.

Figures (hand-computed from the printed form, not a CRA example; a salary of 17,000 /
200,000 is a taxable income, line 1, of 16,865.00 / 198,926.00):
- Column 1 of lines 2 to 8 (line 1 at most 49,279): rate 5.06%, line 7 is 0.00.
  16,865.00 x 5.06% = 853.369, so 853.37.
- Column 2 (more than 49,279 but not more than 98,560): rate 7.7%, line 7 is 2,493.52.
  69,335.00 - 49,279.00 = 20,056.00; x 7.7% = 1,544.312, so 1,544.31; + 2,493.52 = 4,037.83.
- Lines 9 to 15, column 2 (more than 186,306 but not more than 259,829): rate 16.8%, line 14 is
  17,989.30. 198,926.00 - 186,306.00 = 12,620.00; x 16.8% = 2,120.16; + 17,989.30 = 20,109.46.
Line 61 is 853.37 / 20,109.46: line 8 gives the first and line 15 the second.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_bc
import tax_engine.jurisdictions.ca_bc.trace_english  # noqa: F401  (registers the renderers)
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import (
    BC428_BRITISH_COLUMBIA_TAX_ON_TAXABLE_INCOME_LINE_61,
)
from tax_engine.jurisdictions.ca_bc.trace import TaxOnTaxableIncomeLine
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
CODE = JurisdictionCode("CA-BC")
FORM = "ca-bc/bc428"
LINE_1 = "ca-bc/bc428_taxable_income_line_1"
LINE_8 = "ca-bc/bc428_tax_on_taxable_income_line_8"
LINE_15 = "ca-bc/bc428_tax_on_taxable_income_line_15"
LINE_61 = "ca-bc/bc428_british_columbia_tax_on_taxable_income_line_61"
TITLE = "British Columbia tax on taxable income from line 8 or 15"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
PART = BC_PARTS / "bc428_line_61.yaml"
# The real British Columbia parts, in composition order: line 1, lines 3 to 8, lines 10 to 15,
# line 61.
LINE_PARTS = (
    *(BC_PARTS / f"bc428_line_{number}.yaml" for number in (1, 3, 4, 5, 6, 7, 8)),
    *(BC_PARTS / f"bc428_line_{number}.yaml" for number in (10, 11, 12, 13, 14, 15)),
    PART,
)
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The BC428 declaration, test-local: line 61 is the only export, as the step under test.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_61}
    capabilities: []
    """)
# salary, the line line 61 takes, line 61: line 8 gives the first four, line 15 the fifth.
CASES = [
    ("17000", LINE_8, "853.37"),
    ("200000", LINE_15, "20109.46"),
]


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[tuple[str, str]]:
    """Each part's name and text, in composition order."""
    yield "salary.yaml", (BC_PARTS / "salary.yaml").read_text(encoding="utf-8")
    for found in form_parts("schedule_8"):
        yield found.name, found.read_text(encoding="utf-8")
    for name in T1_PARTS:
        found = _federal(name)
        yield (
            name,
            inputs_without_form(found)
            if name.endswith("_inputs.yaml")
            else found.read_text("utf-8"),
        )
    for part in LINE_PARTS:
        yield part.name, part.read_text(encoding="utf-8")


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest: a test header, the test-local form
    declaration and the real parts from the salary to line 61."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_TEXT, encoding="utf-8")
    for number, (name, text) in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
    roots = {**british_columbia_packages().roots(), Namespace("ca-bc"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, british_columbia_kinds(), british_columbia_units()),
        YamlParameterSource(
            british_columbia_packages().roots(),
            british_columbia_parameter_parsers(),
            british_columbia_units(),
        ),
        british_columbia_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(CODE, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))
    (sheet,) = worksheets[FORM]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = british_columbia_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


@pytest.mark.parametrize(("salary", "used", "expected"), CASES)
def test_line_61_is_the_line_that_has_a_figure(
    tmp_path: Path, salary: str, used: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(_kind(LINE_61)).value == D(expected)


@pytest.mark.parametrize(("salary", "used", "expected"), CASES)
def test_line_61_traces_one_line_naming_the_line_it_took(
    tmp_path: Path, salary: str, used: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    (line,) = [t for t in sheet.trace if isinstance(t, TaxOnTaxableIncomeLine)]
    blank = LINE_15 if used == LINE_8 else LINE_8
    assert line == TaxOnTaxableIncomeLine(
        output=_kind(LINE_61),
        used=_kind(used),
        used_amount=D(expected),
        left_blank=_kind(blank),
    )


@pytest.mark.parametrize(("salary", "used", "expected"), CASES)
def test_the_line_it_took_has_the_figure_and_the_other_is_blank(
    tmp_path: Path, salary: str, used: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    other = LINE_15 if used == LINE_8 else LINE_8

    assert sheet.get(_kind(used)).value == D(expected)
    assert sheet.get(_kind(other)).is_blank


def test_line_61_equals_the_real_line_8_for_a_salary_in_the_lines_2_to_8_table(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "20000")

    assert sheet.get(_kind(LINE_61)).value == sheet.get(_kind(LINE_8)).value


def test_line_61_equals_the_real_line_15_for_a_salary_in_the_lines_9_to_15_table(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "200000")

    assert sheet.get(_kind(LINE_61)).value == sheet.get(_kind(LINE_15)).value


def test_the_english_trace_names_the_lines_and_shows_cents(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "20000")

    sentences = EnglishTraceRenderer().render_all(
        [t for t in sheet.trace if isinstance(t, TaxOnTaxableIncomeLine)], sheet
    )

    # The lines are on the same form, so they are named as "line 8" and "line 15", with no form.
    assert sentences == ("Line 8 (CA$1003.65), with line 15 left blank, gives CA$1003.65.",)


# The two refusals (both lines blank, both lines with a figure) cannot arise from a salary: line 1
# is always in exactly one of the two tables. They are pinned on the capability itself in
# tests/jurisdictions/ca_bc/capabilities/test_tax_on_taxable_income.py.


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def test_the_part_is_one_step_that_reads_lines_8_and_15_of_the_same_form() -> None:
    assert _step() == {
        "name": "ca-bc/tax_on_taxable_income",
        "title": TITLE,
        "reference": "61",
        "unit": "ca/cad",
        "consumes": {"line_8": LINE_8, "line_15": LINE_15},
        "blank": {"line_8": "compute", "line_15": "compute"},
        "produces": {"output": LINE_61},
    }


def test_the_step_keys_are_in_the_order_of_the_alberta_part() -> None:
    # name, title, reference, unit, then the slots (no params here): consumes, blank, produces.
    assert list(_step()) == [
        "name",
        "title",
        "reference",
        "unit",
        "consumes",
        "blank",
        "produces",
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = british_columbia_kinds().kind(LINE_61)

    assert kind is BC428_BRITISH_COLUMBIA_TAX_ON_TAXABLE_INCOME_LINE_61
    assert isinstance(kind, AmountKind)
    assert kind.identifier == LINE_61
    assert kind.value_type is Decimal
    assert non_negative(kind)
