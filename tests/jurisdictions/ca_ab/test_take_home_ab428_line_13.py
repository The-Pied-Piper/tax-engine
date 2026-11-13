"""AB428 (2025) line 13, line 11 multiplied by the line 12 rate, real engine.

Form text (Form AB428, CRA 5009-c-25e.txt): "Line 13: Line 11 multiplied by the percentage from
line 12 = ^". Line 11 is the taxable income over the lower bound of the column line 1 falls in and
line 12 is that column's printed rate (13%, 14% or 15%), so line 13 is their product, rounded
half-up to the cent by `ca-ab/cent_rounding`. It is blank when lines 11 and 12 are blank (a line 1
of 181,481 or less, where the lines 10 to 16 table does not apply).

Lines 1, 10, 11, 12 and 13 are composed from their real parts as they are: line 1
`ca-ab/ab428_taxable_income_line_1` (`ab428_credits_line_1.yaml`), line 10
`ca-ab/ab428_bracket_lower_bound_line_10` (`ab428_line_10.yaml`), line 11
`ca-ab/ab428_taxable_income_over_lower_bound_line_11` (`ab428_line_11.yaml`) and line 12
`ca-ab/ab428_bracket_rate_line_12` (`ab428_line_12.yaml`). Line 13 is `core/multiply_by_rate` with
`base` = line 11 and `rate` = line 12, output `ca-ab/ab428_tax_on_excess_line_13`, in the part
`ab428_line_13.yaml`. The capability refuses a blank in a slot with no blank rule, so both slots
carry `pass_on`. The form declaration is test-local, exporting lines 1, 10, 11, 12 and 13.

Figures, computed here from the engine's T1 taxable income (line 1 is the salary less 1,074.00 at
these incomes): salary 20,000 and 70,000 give blank lines 11 and 12, so a blank line 13; 200,000
gives line 1 of 198,926.00, line 11 of 17,445.00 at 13%, so 2,267.85. Column edges, each computed
independently with Decimal: line 1 of 181,481.00 is blank; 181,481.01 gives line 11 0.01 at 13%
(0.0013, so 0.00); 241,974.00 is still column 13% (line 11 60,493.00, so 7,864.09) and 241,974.01
is column 14% (line 11 0.01, so 0.00); 362,961.00 is still 14% (line 11 120,987.00, so 16,938.18)
and 362,961.01 is 15% (0.0015, so 0.00); 363,961.00 gives 1,000.00 at 15%, so 150.00. Rounding:
line 11 of 0.50 at 13% is 0.065, half-up 0.07 (not the even 0.06); 0.75 at 14% is 0.105, so 0.11;
0.30 at 15% is 0.045, so 0.05; 0.05 at 14% is 0.007, so 0.01; 0.03 at 13% is 0.0039, so 0.00.
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
from tax_engine.domain.trace import BlankPassedOnLine, MultipliedByRateLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ab.catalog import AB428_TAX_ON_EXCESS_LINE_13
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
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_1_PART = ALBERTA_PARTS / "ab428_credits_line_1.yaml"
LINE_10_PART = ALBERTA_PARTS / "ab428_line_10.yaml"
LINE_11_PART = ALBERTA_PARTS / "ab428_line_11.yaml"
LINE_12_PART = ALBERTA_PARTS / "ab428_line_12.yaml"
LINE_13_PART = ALBERTA_PARTS / "ab428_line_13.yaml"
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
# The AB428 declaration, test-local: lines 1, 10, 11, 12 and 13 are composed, so it exports those.
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
        # Line 1 is 198,926.00: line 11 is 17,445.00 at 13%.
        ("200000", "2267.85"),
        # Line 1 of exactly 241,974.00 is still the 13% column: line 11 60,493.00.
        ("243048.00", "7864.09"),
        # Line 1 of exactly 362,961.00 is still the 14% column: line 11 120,987.00.
        ("364035.00", "16938.18"),
        # Line 1 of 363,961.00 is the 15% column: line 11 1,000.00.
        ("365035.00", "150.00"),
    ],
)
def test_line_13_is_line_11_times_the_line_12_rate_for_the_salary(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_13)).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 1 of 181,481.01 is the 13% column: line 11 is one cent, 0.0013 rounds to nothing.
        ("182555.01", "0.00"),
        # Line 1 of 241,974.01 is the 14% column: line 11 is one cent, 0.0014 rounds to nothing.
        ("243048.01", "0.00"),
        # Line 1 of 362,961.01 is the 15% column: line 11 is one cent, 0.0015 rounds to nothing.
        ("364035.01", "0.00"),
    ],
)
def test_line_13_just_above_each_column_edge(tmp_path: Path, salary: str, expected: str) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_13)).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # 0.03 x 13% = 0.0039: down.
        ("182555.03", "0.00"),
        # 0.50 x 13% = 0.065: exactly half goes up (half-up, not half-even 0.06).
        ("182555.50", "0.07"),
        # 0.05 x 14% = 0.007: up.
        ("243048.05", "0.01"),
        # 0.75 x 14% = 0.105: exactly half goes up (half-up, not half-even 0.10).
        ("243048.75", "0.11"),
        # 0.30 x 15% = 0.045: exactly half goes up (half-up, not half-even 0.04).
        ("364035.30", "0.05"),
    ],
)
def test_line_13_is_rounded_half_up_to_the_cent(tmp_path: Path, salary: str, expected: str) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_13)).value == D(expected)


@pytest.mark.parametrize("salary", ["20000", "70000", "182555.00"])
def test_line_13_is_blank_when_lines_11_and_12_are_blank(tmp_path: Path, salary: str) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_13)).is_blank


def test_the_blank_line_13_says_it_passed_on_the_blanks_of_lines_11_and_12(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "70000")
    # The kinds in `because` are sorted by identifier: line 12 (bracket_rate) before line 11.
    line = BlankPassedOnLine(_kind(LINE_13), (_kind(LINE_12), _kind(LINE_11)))

    assert line in sheet.trace
    assert EnglishTraceRenderer().render(line).endswith("were blank.")
    assert not any(
        isinstance(each, MultipliedByRateLine) and each.output is _kind(LINE_13)
        for each in sheet.trace
    )


def test_the_product_is_traced_with_its_base_and_rate(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "200000")

    (line,) = (
        each
        for each in sheet.trace
        if isinstance(each, MultipliedByRateLine) and each.output is _kind(LINE_13)
    )
    assert line.base_kind is _kind(LINE_11)
    assert line.base_value == D("17445.00")
    assert line.rate_kind is _kind(LINE_12)
    assert line.rate_value == D("0.13")
    assert line.result == D("2267.85")


def test_the_part_is_one_multiply_by_rate_step_over_lines_11_and_12() -> None:
    part = yaml.safe_load(LINE_13_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert list(step) == [
        "name",
        "reference",
        "unit",
        "params",
        "consumes",
        "blank",
        "produces",
    ]
    assert step == {
        "name": "core/multiply_by_rate",
        "reference": "13",
        "unit": "ca/cad",
        "params": {"rounding": "ca-ab/cent_rounding"},
        "consumes": {"base": LINE_11, "rate": LINE_12},
        "blank": {"base": "pass_on", "rate": "pass_on"},
        "produces": {"output": LINE_13},
    }


def test_line_13_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = alberta_kinds().kind(LINE_13)

    assert kind is AB428_TAX_ON_EXCESS_LINE_13
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
