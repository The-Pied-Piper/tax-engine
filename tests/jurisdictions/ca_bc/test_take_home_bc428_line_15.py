"""BC428 (2025) line 15, the British Columbia tax on taxable income for lines 9 to 15, real engine.

Form text (Form BC428, CRA 5010-C, read 2026-11-14): "Column 1: Line 1 is more than $137,407 but not
more than $186,306 / Line 15: Line 13 plus line 14 British Columbia tax on taxable income = ^", and
the same Line 15 under "Column 2: Line 1 is more than $186,306 but not more than $259,829" and
"Column 3: Line 1 is more than $259,829". Line 13 is the tax on the part of line 1 over the column's
lower bound, rounded to the cent, and line 14 is the printed tax at the start of that column
(10,801.15, 17,989.30, 30,341.16), so line 15 is their sum. The sum is taken once, rounded
half-up to the cent by `ca-bc/cent_rounding`, which changes nothing since both parts are already
in cents. It is blank when lines 13 and 14 are blank (a line 1 of 137,407.00 or less, where the
lines 9 to 15 table does not apply).

Lines 1, 10, 11, 12, 13 and 14 are composed from their real parts as they are: line 1
`ca-bc/bc428_taxable_income_line_1` (`bc428_line_1.yaml`), line 10
`ca-bc/bc428_bracket_lower_bound_line_10` (`bc428_line_10.yaml`), line 11
`ca-bc/bc428_taxable_income_over_lower_bound_line_11` (`bc428_line_11.yaml`), line 12
`ca-bc/bc428_bracket_rate_line_12` (`bc428_line_12.yaml`), line 13 `ca-bc/bc428_bracket_tax_line_13`
(`bc428_line_13.yaml`) and line 14 `ca-bc/bc428_bracket_tax_at_start_line_14`
(`bc428_line_14.yaml`). Line 15 is one `core/sum` step over lines 13 and 14, output
`ca-bc/bc428_tax_on_taxable_income_line_15`, in the part `bc428_line_15.yaml`. The form declaration
is test-local. The service is built over the package list of `support.py`.

Figures (hand-computed, not a CRA example): taxable income is the salary less the CPP
enhanced and second-ceiling amounts, 16,865.00 / 69,335.00 / 198,926.00, so
line 15 is blank for salaries of 17,000 / 70,000, and for 200,000 it is
2,120.16 + 17,989.30 = 20,109.46 (line 11 is 12,620.00 at 16.8%).

Column edges are driven from a given line 1 (the T1 parts are left out), with line 13 =
(line 1 - lower bound) x rate, half-up to the cent, and line 15 = line 13 + printed start:
- 186306.00: 48899.00 x 0.147 = 7188.15300, so 7188.15; + 10801.15 = 17989.30.
- 300000.00: 40171.00 x 0.205 = 8235.05500, so 8235.06; + 30341.16 = 38576.22.
- 137,407.00 or less: blank.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BlankPassedOnLine, SumLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import (
    BC428_TAX_ON_TAXABLE_INCOME_LINE_15,
    BC428_TAXABLE_INCOME_LINE_1,
)
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
LINE_10 = "ca-bc/bc428_bracket_lower_bound_line_10"
LINE_11 = "ca-bc/bc428_taxable_income_over_lower_bound_line_11"
LINE_12 = "ca-bc/bc428_bracket_rate_line_12"
LINE_13 = "ca-bc/bc428_bracket_tax_line_13"
LINE_14 = "ca-bc/bc428_bracket_tax_at_start_line_14"
LINE_15 = "ca-bc/bc428_tax_on_taxable_income_line_15"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
LINE_PARTS = tuple(
    BC_PARTS / f"bc428_line_{number}.yaml" for number in ("1", "10", "11", "12", "13", "14", "15")
)
LINE_15_PART = BC_PARTS / "bc428_line_15.yaml"
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
# The BC428 declaration, test-local: lines 1 and 10 to 15 are composed, so it exports those.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_1}
        - {LINE_10}
        - {LINE_11}
        - {LINE_12}
        - {LINE_13}
        - {LINE_14}
        - {LINE_15}
    capabilities: []
    """)

DIRECT_HEADER = dedent(f"""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: {LINE_1}
        required: true
    outputs:
      - {LINE_1}
    capabilities: []
    """)
DIRECT_FORM = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_15}
    capabilities: []
    """)


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


def _direct(tmp_path: Path, taxable_income: str) -> Artifact[Decimal]:
    """Line 15 from a given line 1, through the real parts and dataset, without the T1 parts."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(DIRECT_HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(DIRECT_FORM, encoding="utf-8")
    for number, part in enumerate(LINE_PARTS[1:], start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"), encoding="utf-8"
        )
    given = Artifact(BC428_TAXABLE_INCOME_LINE_1, D(taxable_income))
    roots = {**british_columbia_packages().roots(), Namespace("ca-bc"): tmp_path}
    service = TaxComputationService(
        YamlJurisdictionSource(roots, british_columbia_kinds(), british_columbia_units()),
        YamlParameterSource(
            british_columbia_packages().roots(),
            british_columbia_parameter_parsers(),
            british_columbia_units(),
        ),
        british_columbia_capabilities(),
    )
    (sheet,) = service.compute(CODE, 2025, given)[FORM]
    return sheet.get(_kind(LINE_15))


@pytest.mark.parametrize("salary", ["17000", "70000"])
def test_line_15_is_blank_when_lines_13_and_14_are_blank(tmp_path: Path, salary: str) -> None:
    # Line 1 is 16,865.00 and 69,335.00, at or below 137,407: lines 9 to 15 do not apply.
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(_kind(LINE_13)).is_blank
    assert sheet.get(_kind(LINE_14)).is_blank
    assert sheet.get(_kind(LINE_15)).is_blank


def test_a_salary_of_200000_gives_line_13_plus_line_14(tmp_path: Path) -> None:
    # Line 1 is 198,926.00 (column 2): line 13 is 2,120.16 and line 14 is 17,989.30.
    sheet = _sheet(tmp_path, "200000")

    assert sheet.get(_kind(LINE_1)).value == D("198926.00")
    assert sheet.get(_kind(LINE_13)).value == D("2120.16")
    assert sheet.get(_kind(LINE_14)).value == D("17989.30")
    assert sheet.get(_kind(LINE_15)).value == D("20109.46")


@pytest.mark.parametrize(
    ("taxable_income", "expected"),
    [
        # Column 1 at its top: line 13 7,188.15 (48,899.00 x 14.7% = 7,188.153), line 14 10,801.15.
        ("186306.00", "17989.30"),
        # Column 3: line 13 8,235.06 (40,171.00 x 20.5% = 8,235.055, half-up), line 14 30,341.16.
        ("300000.00", "38576.22"),
    ],
)
def test_line_15_at_and_just_above_each_column_boundary(
    tmp_path: Path, taxable_income: str, expected: str
) -> None:
    assert _direct(tmp_path, taxable_income).value == D(expected)


@pytest.mark.parametrize("taxable_income", ["49279.00", "137407.00"])
def test_line_15_is_blank_at_and_below_137407(tmp_path: Path, taxable_income: str) -> None:
    assert _direct(tmp_path, taxable_income).is_blank


def test_the_blank_line_15_says_it_passed_on_the_blanks_of_lines_13_and_14(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "20000")
    # The kinds in `because` are sorted by identifier: line 14 (bracket_tax_at_start) comes first.
    line = BlankPassedOnLine(_kind(LINE_15), (_kind(LINE_14), _kind(LINE_13)))

    assert line in sheet.trace
    assert EnglishTraceRenderer().render(line).endswith("were blank.")
    assert not any(
        isinstance(each, SumLine) and each.output is _kind(LINE_15) for each in sheet.trace
    )


def test_the_sum_is_traced_with_its_parts_in_the_order_they_are_wired(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "200000")

    (line,) = (
        each for each in sheet.trace if isinstance(each, SumLine) and each.output is _kind(LINE_15)
    )
    assert [(kind, value) for kind, value in line.parts] == [
        (_kind(LINE_13), D("2120.16")),
        (_kind(LINE_14), D("17989.30")),
    ]
    assert line.total == D("20109.46")


def test_the_sum_is_traced_in_english(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "200000")

    (line,) = (
        each for each in sheet.trace if isinstance(each, SumLine) and each.output is _kind(LINE_15)
    )
    text = EnglishTraceRenderer().render(line)
    assert "2120.16" in text
    assert "17989.30" in text
    assert "20109.46" in text


def test_the_part_is_one_sum_step_over_lines_13_and_14() -> None:
    part = yaml.safe_load(LINE_15_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert list(step) == [
        "name",
        "title",
        "reference",
        "unit",
        "params",
        "consumes",
        "blank",
        "produces",
    ]
    assert step == {
        "name": "core/sum",
        "title": "British Columbia tax on taxable income",
        "reference": "15",
        "unit": "ca/cad",
        "params": {"rounding": "ca-bc/cent_rounding"},
        "consumes": {"parts": [LINE_13, LINE_14]},
        "blank": {LINE_13: "pass_on", LINE_14: "pass_on"},
        "produces": {"output": LINE_15},
    }


def test_line_15_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = british_columbia_kinds().kind(LINE_15)

    assert kind is BC428_TAX_ON_TAXABLE_INCOME_LINE_15
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
