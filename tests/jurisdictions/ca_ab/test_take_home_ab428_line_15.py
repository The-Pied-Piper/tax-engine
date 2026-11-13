"""AB428 (2025) line 15, the Alberta tax on taxable income, real engine.

Form text (Form AB428, CRA 5009-c): "Line 15: Line 13 plus line 14 Alberta tax on taxable income =
^". Line 13 is the tax on the excess over the column's lower bound, rounded to the cent, and line 14
is the printed tax at the start of that column, so line 15 is their sum. The sum is taken once,
rounded half-up to the cent by `ca-ab/cent_rounding`, which changes nothing here since both parts
are already in cents. It is blank when lines 13 and 14 are blank (a line 1 of 181,481 or less,
where the lines 9 to 15 table does not apply).

Lines 1, 10, 11, 12, 13 and 14 are composed from their real parts as they are: line 1
`ca-ab/ab428_taxable_income_line_1` (`ab428_credits_line_1.yaml`), line 10
`ca-ab/ab428_bracket_lower_bound_line_10` (`ab428_line_10.yaml`), line 11
`ca-ab/ab428_taxable_income_over_lower_bound_line_11` (`ab428_line_11.yaml`), line 12
`ca-ab/ab428_bracket_rate_line_12` (`ab428_line_12.yaml`), line 13
`ca-ab/ab428_tax_on_excess_line_13` (`ab428_line_13.yaml`) and line 14
`ca-ab/ab428_bracket_tax_at_start_line_14` (`ab428_line_14.yaml`). Line 15 is one `core/sum` step
over lines 13 and 14, output `ca-ab/ab428_tax_on_taxable_income_line_15`, in the part
`ab428_line_15.yaml`. The form declaration is test-local, exporting lines 1, 10, 11, 12, 13, 14
and 15.

Figures, computed here from the engine's T1 taxable income (line 1 is the salary less 1,074.00 at
these incomes): salary 20,000 and 70,000 give blank lines 13 and 14, so a blank line 15; 200,000
gives line 1 of 198,926.00, line 13 of 2,267.85 and line 14 of 17,553.04, so 19,820.89. Column
edges, each computed independently with Decimal: line 1 of 181,481.00 is blank; 181,481.01 gives
0.00 + 17,553.04 = 17,553.04; 241,974.00 gives 7,864.09 + 17,553.04 = 25,417.13; 241,974.01 gives
0.00 + 25,417.13 = 25,417.13; 362,961.00 gives 16,938.18 + 25,417.13 = 42,355.31; 362,961.01 gives
0.00 + 42,355.31 = 42,355.31; 363,961.00 gives 150.00 + 42,355.31 = 42,505.31.
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
LINE_10 = "ca-ab/ab428_bracket_lower_bound_line_10"
LINE_11 = "ca-ab/ab428_taxable_income_over_lower_bound_line_11"
LINE_12 = "ca-ab/ab428_bracket_rate_line_12"
LINE_13 = "ca-ab/ab428_tax_on_excess_line_13"
LINE_14 = "ca-ab/ab428_bracket_tax_at_start_line_14"
LINE_15 = "ca-ab/ab428_tax_on_taxable_income_line_15"
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_1_PART = ALBERTA_PARTS / "ab428_credits_line_1.yaml"
LINE_10_PART = ALBERTA_PARTS / "ab428_line_10.yaml"
LINE_11_PART = ALBERTA_PARTS / "ab428_line_11.yaml"
LINE_12_PART = ALBERTA_PARTS / "ab428_line_12.yaml"
LINE_13_PART = ALBERTA_PARTS / "ab428_line_13.yaml"
LINE_14_PART = ALBERTA_PARTS / "ab428_line_14.yaml"
LINE_15_PART = ALBERTA_PARTS / "ab428_line_15.yaml"
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
# The AB428 declaration, test-local: lines 1, 10 to 15 are composed, so it exports those.
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
    yield LINE_10_PART.name, LINE_10_PART.read_text(encoding="utf-8")
    yield LINE_11_PART.name, LINE_11_PART.read_text(encoding="utf-8")
    yield LINE_12_PART.name, LINE_12_PART.read_text(encoding="utf-8")
    yield LINE_13_PART.name, LINE_13_PART.read_text(encoding="utf-8")
    yield LINE_14_PART.name, LINE_14_PART.read_text(encoding="utf-8")
    yield LINE_15_PART.name, LINE_15_PART.read_text(encoding="utf-8")


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
        # Line 1 is 198,926.00: line 13 is 2,267.85 and line 14 is 17,553.04.
        ("200000", "19820.89"),
        # Line 1 of 181,481.01 is column 1: line 13 0.00 and line 14 17,553.04.
        ("182555.01", "17553.04"),
        # Line 1 of exactly 241,974.00 is still column 1: line 13 7,864.09 and line 14 17,553.04.
        ("243048.00", "25417.13"),
        # Line 1 of 241,974.01 is column 2: line 13 0.00 and line 14 25,417.13.
        ("243048.01", "25417.13"),
        # Line 1 of exactly 362,961.00 is still column 2: line 13 16,938.18 and line 14 25,417.13.
        ("364035.00", "42355.31"),
        # Line 1 of 362,961.01 is column 3: line 13 0.00 and line 14 42,355.31.
        ("364035.01", "42355.31"),
        # Line 1 of 363,961.00 is column 3: line 13 150.00 and line 14 42,355.31.
        ("365035.00", "42505.31"),
    ],
)
def test_line_15_is_line_13_plus_line_14_for_the_salary(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_15)).value == D(expected)


@pytest.mark.parametrize("salary", ["20000", "70000", "182555.00"])
def test_line_15_is_blank_when_lines_13_and_14_are_blank(tmp_path: Path, salary: str) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_15)).is_blank


@pytest.mark.parametrize("salary", ["20000", "70000"])
def test_the_blank_line_15_says_it_passed_on_the_blanks_of_lines_13_and_14(
    tmp_path: Path, salary: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    # The kinds in `because` are sorted by identifier: line 14 (bracket_tax_at_start) first.
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
        (_kind(LINE_13), D("2267.85")),
        (_kind(LINE_14), D("17553.04")),
    ]
    assert line.total == D("19820.89")


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
        "title": "Alberta tax on taxable income",
        "reference": "15",
        "unit": "ca/cad",
        "params": {"rounding": "ca-ab/cent_rounding"},
        "consumes": {"parts": [LINE_13, LINE_14]},
        "blank": {LINE_13: "pass_on", LINE_14: "pass_on"},
        "produces": {"output": LINE_15},
    }


def test_line_15_is_a_registered_non_negative_decimal_amount_kind() -> None:
    from tax_engine.jurisdictions.ca_ab.catalog import AB428_TAX_ON_TAXABLE_INCOME_LINE_15

    kind = alberta_kinds().kind(LINE_15)

    assert kind is AB428_TAX_ON_TAXABLE_INCOME_LINE_15
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
