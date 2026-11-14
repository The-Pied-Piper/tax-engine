"""BC428 (2025) line 6, line 4 multiplied by the line 5 rate, real engine.

Form text (Form BC428, CRA 5010-C, read 2026-11-14): "Column 1: Line 1 is $49,279 or less / Line 6:
Line 4 multiplied by the percentage from line 5 = ^", and the same Line 6 under "Column 2: Line 1
is more than $49,279 but not more than $98,560", "Column 3: Line 1 is more than $98,560 but not
more than $113,158" and "Column 4: Line 1 is more than $113,158 but not more than $137,407". Line 4
is the taxable income over the lower bound of the column line 1 falls in and line 5 is that column's
printed rate (5.06%, 7.7%, 10.5% or 12.29%), so line 6 is their product, rounded half-up to the cent
by `ca-bc/cent_rounding` (the BC forms print no rounding rule; this follows Alberta and Ontario). It
is blank when lines 4 and 5 are blank (a line 1 above 137,407, where the lines 2 to 8 table does not
apply).

Lines 1, 3, 4 and 5 are composed from their real parts as they are: line 1
`ca-bc/bc428_taxable_income_line_1` (`bc428_line_1.yaml`), line 3
`ca-bc/bc428_bracket_lower_bound_line_3` (`bc428_line_3.yaml`), line 4
`ca-bc/bc428_taxable_income_over_lower_bound_line_4` (`bc428_line_4.yaml`) and line 5
`ca-bc/bc428_bracket_rate_line_5` (`bc428_line_5.yaml`). Line 6 is `core/multiply_by_rate` with
`base` = line 4 and `rate` = line 5, output `ca-bc/bc428_bracket_tax_line_6`, in the part
`bc428_line_6.yaml`. The capability refuses a blank in a slot with no blank rule, so both slots
carry `pass_on`. The form declaration is test-local. British Columbia is not in
`registrations.JURISDICTIONS`, so the service is built over the package list of `support.py`.

Figures (ticket, hand-computed, not a CRA example): taxable income is the salary less the CPP
enhanced and second-ceiling amounts, 16,865.00 / 19,835.00 / 29,735.00 / 69,335.00 / 198,926.00, so
line 6 is 853.37 (16,865.00 x 0.0506 = 853.369) / 1,003.65 (1,003.651) / 1,504.59 (1,504.591) /
1,544.31 (20,056.00 x 0.077 = 1,544.312) / blank. The column edges and the half-up cases are driven
from a given line 1 (the T1 parts are left out), as the line 5 test does for its thresholds: line 1
of 49,279.00 is column 1 (line 4 49,279.00, 2,493.5174, so 2,493.52) and 49,279.01 is column 2 (line
4 0.01, 0.00077, so 0.00). Rounding: line 4 of 25.00 at 5.06% is 1.265, half-up 1.27 (not the even
1.26); line 4 of 5.00 at 7.7% is 0.385, so 0.39; line 4 of 1.00 at 10.5% is 0.105, so 0.11.
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
from tax_engine.domain.trace import BlankPassedOnLine, MultipliedByRateLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import (
    BC428_BRACKET_TAX_LINE_6,
    BC428_TAXABLE_INCOME_LINE_1,
)
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
LINE_3 = "ca-bc/bc428_bracket_lower_bound_line_3"
LINE_4 = "ca-bc/bc428_taxable_income_over_lower_bound_line_4"
LINE_5 = "ca-bc/bc428_bracket_rate_line_5"
LINE_6 = "ca-bc/bc428_bracket_tax_line_6"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_1_PART = BC_PARTS / "bc428_line_1.yaml"
LINE_3_PART = BC_PARTS / "bc428_line_3.yaml"
LINE_4_PART = BC_PARTS / "bc428_line_4.yaml"
LINE_5_PART = BC_PARTS / "bc428_line_5.yaml"
LINE_6_PART = BC_PARTS / "bc428_line_6.yaml"
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
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The BC428 declaration, test-local: lines 1, 3, 4, 5 and 6 are composed, so it exports those.
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
        - {LINE_6}
    capabilities: []
    """)


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[tuple[str, str]]:
    """Each part's name and text, in composition order."""
    yield "salary.yaml", (BC_PARTS / "salary.yaml").read_text(encoding="utf-8")
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
        # Line 4 is 16,865.00 at 5.06%: 853.369.
        ("17000", "853.37"),
        # Line 4 is 19,835.00 at 5.06%: 1,003.651.
        ("20000", "1003.65"),
        # Line 4 is 29,735.00 at 5.06%: 1,504.591.
        ("30000", "1504.59"),
        # Line 4 is 20,056.00 at 7.7% (column 2): 1,544.312.
        ("70000", "1544.31"),
    ],
)
def test_line_6_is_line_4_times_the_line_5_rate_for_the_worked_salaries(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_6)).value == D(expected)


def test_line_6_is_blank_when_line_1_is_above_137407(tmp_path: Path) -> None:
    assert _sheet(tmp_path, "200000").get(_kind(LINE_6)).is_blank


def _direct(tmp_path: Path, taxable_income: str) -> Artifact[Decimal]:
    """Line 6 from a given line 1, through the real parts and dataset, without the T1 parts."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(DIRECT_HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(DIRECT_FORM, encoding="utf-8")
    for number, part in enumerate((LINE_3_PART, LINE_4_PART, LINE_5_PART, LINE_6_PART), start=2):
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
    return sheet.get(_kind(LINE_6))


@pytest.mark.parametrize(
    ("taxable_income", "expected"),
    [
        ("0.00", "0.00"),
        # Column 1 at its top: 49,279.00 x 5.06% = 2,493.5174.
        ("49279.00", "2493.52"),
        # Column 2, one cent over the bound: 0.01 x 7.7% = 0.00077.
        ("49279.01", "0.00"),
        # Line 4 of 1.00 at 7.7%: 0.077.
        ("49280.00", "0.08"),
        # Column 2 at its top: 49,281.00 x 7.7% = 3,794.637.
        ("98560.00", "3794.64"),
        # Column 3, one cent over the bound: 0.01 x 10.5% = 0.00105.
        ("98560.01", "0.00"),
        # Column 3 at its top: 14,598.00 x 10.5% = 1,532.79.
        ("113158.00", "1532.79"),
        # Column 4, one cent over the bound: 0.01 x 12.29% = 0.001229.
        ("113158.01", "0.00"),
        # Line 4 of 1.00 at 12.29%: 0.1229.
        ("113159.00", "0.12"),
        # Column 4 at its top: 24,249.00 x 12.29% = 2,980.2021.
        ("137407.00", "2980.20"),
    ],
)
def test_line_6_at_and_just_above_each_column_boundary(
    tmp_path: Path, taxable_income: str, expected: str
) -> None:
    assert _direct(tmp_path, taxable_income).value == D(expected)


@pytest.mark.parametrize(
    ("taxable_income", "expected"),
    [
        # 25.00 x 5.06% = 1.2650: exactly half goes up (half-up, not half-even 1.26).
        ("25.00", "1.27"),
        # 5.00 x 7.7% = 0.385: half goes up (not half-even 0.38).
        ("49284.00", "0.39"),
        # 4.99 x 7.7% = 0.38423: down.
        ("49283.99", "0.38"),
        # 1.00 x 10.5% = 0.105: half goes up (not half-even 0.10).
        ("98561.00", "0.11"),
        # 16,865.00 x 5.06% = 853.369: the third decimal rounds up.
        ("16865.00", "853.37"),
    ],
)
def test_line_6_is_rounded_half_up_to_the_cent(
    tmp_path: Path, taxable_income: str, expected: str
) -> None:
    assert _direct(tmp_path, taxable_income).value == D(expected)


def test_line_6_one_cent_above_the_table_is_blank(tmp_path: Path) -> None:
    assert _direct(tmp_path, "137407.01").is_blank


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
    assert line.base_value == D("20056.00")
    assert line.rate_kind is _kind(LINE_5)
    assert line.rate_value == D("0.077")
    assert line.result == D("1544.31")


def test_the_product_is_traced_in_english(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "17000")

    (line,) = (
        each
        for each in sheet.trace
        if isinstance(each, MultipliedByRateLine) and each.output is _kind(LINE_6)
    )
    text = EnglishTraceRenderer().render(line)
    assert "(5.06%) of" in text
    assert "16865.00" in text
    assert text.endswith("853.37 (rounded to the nearest cent).")


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
        "params": {"rounding": "ca-bc/cent_rounding"},
        "consumes": {"base": LINE_4, "rate": LINE_5},
        "blank": {"base": "pass_on", "rate": "pass_on"},
        "produces": {"output": LINE_6},
    }


def test_line_6_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = british_columbia_kinds().kind(LINE_6)

    assert kind is BC428_BRACKET_TAX_LINE_6
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
