"""AB428 (2025) line 6, line 4 multiplied by the line 5 rate, real engine.

Form text (Form AB428, CRA 5009-c-25e.txt, cra-docs repo): "Line 6: Line 4 multiplied by the
percentage from line 5 = ^". Line 4 is the taxable income over the lower bound of the column line 1
falls in and line 5 is that column's printed rate (8%, 10% or 12%), so line 6 is their product,
rounded half-up to the cent by `ca-ab/cent_rounding`. It is blank when lines 4 and 5 are blank (a
line 1 above 181,481, where the lines 2 to 8 table does not apply).

Lines 1, 3, 4 and 5 are composed from their real parts as they are: line 1
`ca-ab/ab428_taxable_income_line_1` (`ab428_credits_line_1.yaml`), line 3
`ca-ab/ab428_bracket_lower_bound_line_3` (`ab428_line_3.yaml`), line 4
`ca-ab/ab428_taxable_income_over_lower_bound_line_4` (`ab428_line_4.yaml`) and line 5
`ca-ab/ab428_bracket_rate_line_5` (`ab428_credits_line_5.yaml`). Line 6 is `core/multiply_by_rate`
with `base` = line 4 and `rate` = line 5, output `ca-ab/ab428_tax_on_excess_line_6`, in the part
`ab428_line_6.yaml`. The capability refuses a blank in a slot with no blank rule, so both slots
carry `pass_on`. The form declaration is test-local, exporting lines 1, 3, 4, 5 and 6.

Figures, computed here from the engine's T1 taxable income: salary 20,000 gives line 4 of
19,835.00 at 8%, so 1,586.80; 70,000 gives 9,335.00 at 10%, so 933.50; 200,000 gives blank lines 4
and 5, so a blank line 6. Column edges: a salary of 60,570.71 gives line 1 of exactly 60,000.00
(column 1, 8%) and 60,570.72 gives 60,000.01 (column 2, 10%, line 4 0.01); 152,308.00 gives
151,234.00 (column 2, line 4 91,234.00) and 152,308.01 gives 151,234.01 (column 3, 12%, line 4
0.01); 182,555.00 gives 181,481.00 (line 4 30,247.00) and 182,555.01 gives blank. Rounding: line 4
of 9,335.05 at 10% is 933.505, half-up 933.51 (not the even 933.50); 9,335.04 gives 933.504, so
933.50; 19,835.07 at 8% is 1,586.8056, so 1,586.81.
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
from tax_engine.jurisdictions.ca_ab.catalog import AB428_TAX_ON_EXCESS_LINE_6
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
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_1_PART = ALBERTA_PARTS / "ab428_credits_line_1.yaml"
LINE_3_PART = ALBERTA_PARTS / "ab428_line_3.yaml"
LINE_4_PART = ALBERTA_PARTS / "ab428_line_4.yaml"
LINE_5_PART = ALBERTA_PARTS / "ab428_credits_line_5.yaml"
LINE_6_PART = ALBERTA_PARTS / "ab428_line_6.yaml"
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
# The AB428 declaration, test-local: lines 1, 3, 4, 5 and 6 are composed, so it exports those.
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
        # Line 4 is 19,835.00 at 8% (column 1).
        ("20000", "1586.80"),
        # Line 4 is 9,335.00 at 10% (column 2).
        ("70000", "933.50"),
    ],
)
def test_line_6_is_line_4_times_the_line_5_rate_for_the_salary(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_6)).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 1 of exactly 60,000.00 is column 1 (8%): line 4 60,000.00.
        ("60570.71", "4800.00"),
        # Line 1 of 60,000.01 is column 2 (10%): line 4 is one cent, 0.001 rounds to nothing.
        ("60570.72", "0.00"),
        # Line 1 of exactly 151,234.00 is column 2 (10%): line 4 91,234.00.
        ("152308.00", "9123.40"),
        # Line 1 of 151,234.01 is column 3 (12%): line 4 is one cent, 0.0012 rounds to nothing.
        ("152308.01", "0.00"),
        # Line 1 of exactly 181,481.00 is column 3 (12%): line 4 30,247.00.
        ("182555.00", "3629.64"),
    ],
)
def test_line_6_at_the_column_boundaries(tmp_path: Path, salary: str, expected: str) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_6)).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # 9,335.04 x 10% = 933.504: down.
        ("70000.04", "933.50"),
        # 9,335.05 x 10% = 933.505: exactly half goes up (half-up, not half-even).
        ("70000.05", "933.51"),
        # 9,335.06 x 10% = 933.506: up.
        ("70000.06", "933.51"),
        # 19,835.06 x 8% = 1,586.8048: down.
        ("20000.06", "1586.80"),
        # 19,835.07 x 8% = 1,586.8056: up.
        ("20000.07", "1586.81"),
        # 0.04 x 12% = 0.0048: down; 0.05 x 12% = 0.006: up.
        ("152308.04", "0.00"),
        ("152308.05", "0.01"),
    ],
)
def test_line_6_is_rounded_half_up_to_the_cent(tmp_path: Path, salary: str, expected: str) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_6)).value == D(expected)


@pytest.mark.parametrize("salary", ["200000", "182555.01"])
def test_line_6_is_blank_when_lines_4_and_5_are_blank(tmp_path: Path, salary: str) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_6)).is_blank


def test_the_blank_line_6_says_it_passed_on_the_blanks_of_lines_4_and_5(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "200000")
    # The kinds in `because` are sorted by identifier: line 5 (bracket_rate) before line 4.
    line = BlankPassedOnLine(_kind(LINE_6), (_kind(LINE_5), _kind(LINE_4)))

    assert line in sheet.trace
    assert EnglishTraceRenderer().render(line).endswith("were blank.")
    assert not any(
        isinstance(each, MultipliedByRateLine) and each.output is _kind(LINE_6)
        for each in sheet.trace
    )


def test_the_product_is_traced_with_its_base_and_rate(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    (line,) = (
        each
        for each in sheet.trace
        if isinstance(each, MultipliedByRateLine) and each.output is _kind(LINE_6)
    )
    assert line.base_kind is _kind(LINE_4)
    assert line.base_value == D("9335.00")
    assert line.rate_kind is _kind(LINE_5)
    assert line.rate_value == D("0.10")
    assert line.result == D("933.50")


def test_the_part_is_one_multiply_by_rate_step_over_lines_4_and_5() -> None:
    part = yaml.safe_load(LINE_6_PART.read_text(encoding="utf-8"))

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
        "reference": "6",
        "unit": "ca/cad",
        "params": {"rounding": "ca-ab/cent_rounding"},
        "consumes": {"base": LINE_4, "rate": LINE_5},
        "blank": {"base": "pass_on", "rate": "pass_on"},
        "produces": {"output": LINE_6},
    }


def test_line_6_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = alberta_kinds().kind(LINE_6)

    assert kind is AB428_TAX_ON_EXCESS_LINE_6
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
