"""BC428 (2025) line 4, the taxable income over the column's lower bound, real engine.

Form text (Form BC428, CRA 5010-C, read 2026-11-14): "Column 1: Line 1 is $49,279 or less / Line 4:
Line 2 minus line 3 (cannot be negative) =", and the same Line 4 under "Column 2: Line 1 is more
than $49,279 but not more than $98,560", "Column 3: Line 1 is more than $98,560 but not more than
$113,158" and "Column 4: Line 1 is more than $113,158 but not more than $137,407". Line 2 is a copy
of line 1 (the T1 taxable income, line 26000) and line 3 is the printed lower bound of the column
that line 1 falls in. Line 4 is therefore line 1 less line 3, floored at zero, and it is blank when
line 3 is blank (a line 1 above 137,407, where the lines 2 to 8 table does not apply).

Line 1 is `ca-bc/bc428_taxable_income_line_1`, its part `bc428_line_1.yaml` (#903), and line 3 is
`ca-bc/bc428_bracket_lower_bound_line_3`, its part `bc428_line_3.yaml` (#906); both are composed as
they are. Line 4 is `core/subtract_not_below_zero` with `amount` = line 1 and `less` = line 3,
output `ca-bc/bc428_taxable_income_over_lower_bound_line_4`, in the part `bc428_line_4.yaml`. Line 2
is a copy of line 1 and has no step of its own.

The real parts composed: the British Columbia salary, Schedule 8, the T1 taxable-income parts, lines
1, 3 and 4. The form declaration is test-local, exporting lines 1, 3 and 4. The service is built
over the package list of `support.py`.

Figures (ticket, hand-computed): taxable income is the salary less the CPP enhanced and
second-ceiling amounts, 16,865.00 / 69,335.00 / 198,926.00, so line 4 is
16,865.00 (column 1, line 3 0.00), 20,056.00 for $70,000 (69,335.00 less
49,279.00) and blank for $200,000. The salaries at the column edges are those of the line 3 test,
whose line 1 figures are checked there; line 1 moves a dollar at a time with the salary (the CPP
amounts are rounded), so the cent over the bound is reached at the lower edge only.
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
from tax_engine.domain.trace import BlankPassedOnLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import BC428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative
from tests.manifest_support import T1_LINE_10100_INPUT

D = Decimal
CODE = JurisdictionCode("CA-BC")
FORM = "ca-bc/bc428"
LINE_1 = "ca-bc/bc428_taxable_income_line_1"
LINE_3 = "ca-bc/bc428_bracket_lower_bound_line_3"
LINE_4 = "ca-bc/bc428_taxable_income_over_lower_bound_line_4"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_1_PART = BC_PARTS / "bc428_line_1.yaml"
LINE_3_PART = BC_PARTS / "bc428_line_3.yaml"
LINE_4_PART = BC_PARTS / "bc428_line_4.yaml"
T1_PARTS = (
    "t1_taxable_income_inputs.yaml",
    "t1_employment_income.yaml",
    "t1_employment_income_line_10100.yaml",
    "t1_employment_income_line_10400.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_employment_income_line_10400_inputs.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The BC428 declaration, test-local: lines 1 and 3 are composed, so it exports those.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_1}
        - {LINE_3}
        - {LINE_4}
    capabilities: []
    """)


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[tuple[str, str]]:
    """Each part's name and text, in composition order."""
    yield T1_LINE_10100_INPUT.name, T1_LINE_10100_INPUT.read_text(encoding="utf-8")
    for found in sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml")):
        yield found.name, found.read_text(encoding="utf-8")
    for name in T1_PARTS:
        found = _federal(name)
        yield (
            name,
            found.read_text("utf-8"),
        )
    yield LINE_1_PART.name, LINE_1_PART.read_text(encoding="utf-8")
    yield LINE_3_PART.name, LINE_3_PART.read_text(encoding="utf-8")
    yield LINE_4_PART.name, LINE_4_PART.read_text(encoding="utf-8")


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


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 1 is 16,865.00 and line 3 is 0.00 (column 1): line 4 is line 1 itself.
        ("17000", "16865.00"),
        # Line 1 is 69,335.00 and line 3 is 49,279.00 (column 2).
        ("70000", "20056.00"),
    ],
)
def test_line_4_is_line_1_minus_line_3_for_the_salary(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_4)).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 1 of exactly 49,279.00 is column 1 (line 3 0.00): line 4 is 49,279.00.
        ("49741.41", "49279.00"),
        # Line 1 of 49,279.01 is column 2 (line 3 49,279.00): line 4 is one cent.
        ("49741.42", "0.01"),
    ],
)
def test_line_4_is_not_below_zero_at_the_column_boundaries(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_4)).value == D(expected)


@pytest.mark.parametrize("salary", ["200000", "138482"])
def test_line_4_is_blank_when_line_3_is_blank(tmp_path: Path, salary: str) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_4)).is_blank


def test_the_blank_line_4_says_it_passed_on_line_3s_blank(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "200000")
    line = BlankPassedOnLine(_kind(LINE_4), (_kind(LINE_3),))

    assert line in sheet.trace
    assert EnglishTraceRenderer().render(line).endswith("was blank.")


def test_the_part_is_one_subtract_not_below_zero_step_over_lines_1_and_3() -> None:
    part = yaml.safe_load(LINE_4_PART.read_text(encoding="utf-8"))

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
        "name": "core/subtract_not_below_zero",
        "reference": "4",
        "unit": "ca/cad",
        "params": {"rounding": "ca-bc/cent_rounding"},
        "consumes": {"amount": LINE_1, "less": LINE_3},
        "blank": {"less": "pass_on"},
        "produces": {"output": LINE_4},
    }


def test_line_4_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = british_columbia_kinds().kind(LINE_4)

    assert kind is BC428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
