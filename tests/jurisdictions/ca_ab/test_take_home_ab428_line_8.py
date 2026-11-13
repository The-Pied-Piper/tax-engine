"""AB428 (2025) line 8, the Alberta tax on taxable income, real engine.

Form text (Form AB428, CRA 5009-c-25e.txt):
"Line 8: Line 6 plus line 7 Alberta tax on taxable income = ^". Line 6 is the tax on the excess
over the column's lower bound, rounded to the cent, and line 7 is the printed tax at the start of
that column, so line 8 is their sum. The sum is taken once, rounded half-up to the cent by
`ca-ab/cent_rounding`, which changes nothing here since both parts are already in cents. It is
blank when lines 6 and 7 are blank (a line 1 above 181,481, where the lines 2 to 8 table does not
apply).

Lines 1, 3, 4, 5 and 6 are composed from their real parts as they are: line 1
`ca-ab/ab428_taxable_income_line_1` (`ab428_credits_line_1.yaml`), line 3
`ca-ab/ab428_bracket_lower_bound_line_3` (`ab428_line_3.yaml`), line 4
`ca-ab/ab428_taxable_income_over_lower_bound_line_4` (`ab428_line_4.yaml`), line 5
`ca-ab/ab428_bracket_rate_line_5` (`ab428_credits_line_5.yaml`) and line 6
`ca-ab/ab428_tax_on_excess_line_6` (`ab428_line_6.yaml`). Line 7
`ca-ab/ab428_bracket_tax_at_start_line_7` (`ab428_line_7.yaml`) is composed as it is too. Line 8 is
one `core/sum` step over lines 6 and 7, output `ca-ab/ab428_tax_on_taxable_income_line_8`, in the
part `ab428_line_8.yaml`. The form declaration is test-local, exporting lines 1, 3, 4, 5, 6, 7
and 8.

Figures, computed from the engine's T1 taxable income: salary 20,000 gives line 1 of 19,835.00, so
line 6 is 1,586.80 and line 7 is 0.00, and line 8 is 1,586.80. Salary 70,000 gives 69,335.00, so
line 6 is 933.50 and line 7 is 4,800.00, and line 8 is 5,733.50. Salary 200,000 gives 198,926.00
(above 181,481), so line 8 is blank. Column edges: a salary of 60,570.71 gives line 1 of exactly
60,000.00 (column 1: line 6 4,800.00, line 7 0.00, line 8 4,800.00) and 60,570.72 gives 60,000.01
(column 2: line 6 0.00, line 7 4,800.00, line 8 4,800.00); 152,308.00 gives 151,234.00 (column 2:
line 6 9,123.40, line 7 4,800.00, line 8 13,923.40) and 152,308.01 gives 151,234.01 (column 3: line
6 0.00, line 7 13,923.40, line 8 13,923.40); 182,555.00 gives 181,481.00 (column 3: line 6 3,629.64,
line 7 13,923.40, line 8 17,553.04) and 182,555.01 gives blank.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_ab
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
from tax_engine.jurisdictions.ca_ab.catalog import AB428_TAX_ON_TAXABLE_INCOME_LINE_8
from tests.jurisdictions.ca_ab.support import (
    alberta_capabilities,
    alberta_kinds,
    alberta_packages,
    alberta_parameter_parsers,
    alberta_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
CODE = JurisdictionCode("CA-AB")
FORM = "ca-ab/ab428_credits"
LINE_1 = "ca-ab/ab428_taxable_income_line_1"
LINE_3 = "ca-ab/ab428_bracket_lower_bound_line_3"
LINE_4 = "ca-ab/ab428_taxable_income_over_lower_bound_line_4"
LINE_5 = "ca-ab/ab428_bracket_rate_line_5"
LINE_6 = "ca-ab/ab428_tax_on_excess_line_6"
LINE_7 = "ca-ab/ab428_bracket_tax_at_start_line_7"
LINE_8 = "ca-ab/ab428_tax_on_taxable_income_line_8"
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_1_PART = ALBERTA_PARTS / "ab428_credits_line_1.yaml"
LINE_3_PART = ALBERTA_PARTS / "ab428_line_3.yaml"
LINE_4_PART = ALBERTA_PARTS / "ab428_line_4.yaml"
LINE_5_PART = ALBERTA_PARTS / "ab428_credits_line_5.yaml"
LINE_6_PART = ALBERTA_PARTS / "ab428_line_6.yaml"
LINE_7_PART = ALBERTA_PARTS / "ab428_line_7.yaml"
LINE_8_PART = ALBERTA_PARTS / "ab428_line_8.yaml"
T1_PARTS = (
    "t1_taxable_income_inputs.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_taxable_income_line_10400_inputs.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-AB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The AB428 declaration, test-local: lines 1, 3, 4, 5, 6, 7 and 8 are composed, so it exports those.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_1}
        - {LINE_3}
        - {LINE_4}
        - {LINE_5}
        - {LINE_6}
        - {LINE_7}
        - {LINE_8}
    """)


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[tuple[str, str]]:
    """Each part's name and text, in composition order."""
    yield "salary.yaml", (ALBERTA_PARTS / "salary.yaml").read_text(encoding="utf-8")
    for found in sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml")):
        yield found.name, found.read_text(encoding="utf-8")
    for name in T1_PARTS:
        found = _federal(name)
        yield (
            name,
            inputs_without_form(found)
            if name.endswith("_inputs.yaml")
            else found.read_text("utf-8"),
        )
    yield LINE_1_PART.name, LINE_1_PART.read_text(encoding="utf-8")
    yield LINE_3_PART.name, LINE_3_PART.read_text(encoding="utf-8")
    yield LINE_4_PART.name, LINE_4_PART.read_text(encoding="utf-8")
    yield LINE_5_PART.name, LINE_5_PART.read_text(encoding="utf-8")
    yield LINE_6_PART.name, LINE_6_PART.read_text(encoding="utf-8")
    yield LINE_7_PART.name, LINE_7_PART.read_text(encoding="utf-8")
    yield LINE_8_PART.name, LINE_8_PART.read_text(encoding="utf-8")


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_TEXT, encoding="utf-8")
    for number, (name, text) in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(CODE, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))
    (sheet,) = worksheets[FORM]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = alberta_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 6 is 1,586.80 and line 7 is 0.00 (column 1).
        ("20000", "1586.80"),
        # Line 6 is 933.50 and line 7 is 4,800.00 (column 2).
        ("70000", "5733.50"),
    ],
)
def test_line_8_is_line_6_plus_line_7_for_the_salary(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_8)).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 1 of exactly 60,000.00 is column 1: line 6 4,800.00 and line 7 0.00.
        ("60570.71", "4800.00"),
        # Line 1 of 60,000.01 is column 2: line 6 0.00 and line 7 4,800.00.
        ("60570.72", "4800.00"),
        # Line 1 of exactly 151,234.00 is column 2: line 6 9,123.40 and line 7 4,800.00.
        ("152308.00", "13923.40"),
        # Line 1 of 151,234.01 is column 3: line 6 0.00 and line 7 13,923.40.
        ("152308.01", "13923.40"),
        # Line 1 of exactly 181,481.00 is column 3: line 6 3,629.64 and line 7 13,923.40.
        ("182555.00", "17553.04"),
    ],
)
def test_line_8_at_the_column_boundaries(tmp_path: Path, salary: str, expected: str) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_8)).value == D(expected)


@pytest.mark.parametrize("salary", ["200000", "182555.01"])
def test_line_8_is_blank_when_lines_6_and_7_are_blank(tmp_path: Path, salary: str) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_8)).is_blank


def test_the_blank_line_8_says_it_passed_on_the_blanks_of_lines_6_and_7(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "200000")
    # The kinds in `because` are sorted by identifier: line 7 (bracket_tax_at_start) before line 6.
    line = BlankPassedOnLine(_kind(LINE_8), (_kind(LINE_7), _kind(LINE_6)))

    assert line in sheet.trace
    assert EnglishTraceRenderer().render(line).endswith("were blank.")
    assert not any(
        isinstance(each, SumLine) and each.output is _kind(LINE_8) for each in sheet.trace
    )


def test_the_sum_is_traced_with_its_parts_in_the_order_they_are_wired(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    (line,) = (
        each for each in sheet.trace if isinstance(each, SumLine) and each.output is _kind(LINE_8)
    )
    assert [(kind, value) for kind, value in line.parts] == [
        (_kind(LINE_6), D("933.50")),
        (_kind(LINE_7), D("4800.00")),
    ]
    assert line.total == D("5733.50")


def test_the_part_is_one_sum_step_over_lines_6_and_7() -> None:
    part = yaml.safe_load(LINE_8_PART.read_text(encoding="utf-8"))

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
        "title": "Alberta tax on taxable income",
        "reference": "8",
        "unit": "ca/cad",
        "params": {"rounding": "ca-ab/cent_rounding"},
        "consumes": {"parts": [LINE_6, LINE_7]},
        "blank": {LINE_6: "pass_on", LINE_7: "pass_on"},
        "produces": {"output": LINE_8},
    }


def test_line_8_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = alberta_kinds().kind(LINE_8)

    assert kind is AB428_TAX_ON_TAXABLE_INCOME_LINE_8
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
