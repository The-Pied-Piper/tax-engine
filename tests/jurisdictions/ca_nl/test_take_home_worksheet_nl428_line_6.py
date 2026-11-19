"""Worksheet NL428 (2025) line 6, line 4 multiplied by the line 5 rate of 15%, from the real parts.

Form text (Worksheet NL428, CRA 5001-D, 2025, 5001-d-25e.txt): "Line 5: Applicable rate 15%" and
"Line 6: Line 4 multiplied by the percentage from line 5 = ^". The form names no label for either
line, so the step has no title. Line 5 is a printed rate, so it is the `ca-nl/age_rate` dataset
figure and has no step of its own; line 6 is one core/apply_rate step over line 4, rounded half-up
to the cent by the dataset's own rule (the form states no rounding rule), as Saskatchewan's line 53
is. The step carries the line number as the reference "6". The kind is non-negative. The "born in
1960 or earlier" condition is not read here: line 6 is a plain product.

The test composes the real federal parts the T1 taxable income form needs (Schedule 8 and the T1
lines 15000, 23300, 23400, 23600, 23600 signed and 26000 with their inputs), the real
`worksheet_nl428_line_4.yaml` and the real `worksheet_nl428_line_6.yaml`, and types in only the
salary. The header (which declares the salary input) and the Worksheet NL428 form declaration
(exporting lines 4 and 6) are made up here, because the shared scaffold owns them. Newfoundland and
Labrador is not yet listed in the registrations, so the service is built over the package list of
`support.py`.

Figures (hand-computed with Decimal, not a CRA example). Line 4 is the salary less the enhanced CPP
deduction (2025) less 38,712.00, not below 0.00 (see the line 4 test); line 6 is 15% of line 4.
- 30,000: line 4 = 0.00, so line 6 = 0.00.
- 50,000: line 4 = 10,823.00, so line 6 = 1,623.45.
- 100,000: line 4 = 60,214.00, so line 6 = 9,032.10. 200,000: line 4 = 160,214.00, so line 6 =
  24,032.10.
- Half a cent: a salary of 39,067.98 has deduction 355.68 (1% of 35,567.98 is 355.6798), so line 2
  = 38,712.30 and line 4 = 0.30; 15% of 0.30 is 0.045, which rounds half-up to 0.05 (half-even
  would give 0.04). A salary of 39,067.69 gives line 4 = 0.01 and 15% of it is 0.0015, so 0.00.
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
import tax_engine.jurisdictions.ca_nl
import tax_engine.jurisdictions.ca_nl.catalog as nl_catalog
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rate import RATE as RATE_KIND
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BlankPassedOnLine, RateAppliedLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
CENT = D("0.01")
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
PART_4 = NL_PARTS / "worksheet_nl428_line_4.yaml"
PART = NL_PARTS / "worksheet_nl428_line_6.yaml"
LINE_4 = "ca-nl/worksheet_nl428_age_amount_line_4"
RATE = "ca-nl/age_rate"
LINE_6 = "ca-nl/worksheet_nl428_age_amount_line_6"
ROUNDING = "ca-nl/cent_rounding"
FORM_NAME = "ca-nl/nl428_worksheet"
# The real federal parts the T1 taxable-income form needs, beside the salary and the three lines.
FEDERAL_PARTS = (
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
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        title: "Employment income"
        reference: "10100"
        unit: ca/cad
        required: true
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {LINE_4}
        - {LINE_6}
    capabilities: []
    """)

# salary, line 2, line 3, line 4. Line 2 is below line 3: line 4 is the floor, 0.00.
FLOORED = [
    ("30000", "29735.00", "38712.00", "0.00"),
    ("39067.67", "38711.99", "38712.00", "0.00"),
]
# Line 2 equals line 3 exactly: the difference is 0.00 without the floor biting.
BOUNDARY = ("39067.68", "38712.00", "38712.00", "0.00")
# Line 2 above line 3.
POSITIVE = [
    ("39067.69", "38712.01", "38712.00", "0.01"),
    ("50000", "49535.00", "38712.00", "10823.00"),
    ("100000", "98926.00", "38712.00", "60214.00"),
    ("200000", "198926.00", "38712.00", "160214.00"),
]


def _part_files() -> Iterator[Path]:
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    for name in FEDERAL_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield PART_4
    yield PART


def _parameters() -> YamlParameterSource:
    return YamlParameterSource(
        newfoundland_packages().roots(), newfoundland_parameter_parsers(), newfoundland_units()
    )


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Newfoundland and Labrador manifest of a test header, a form
    declaration and the real part files, every other namespace being the package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=2):
        text = (
            inputs_without_form(found)
            if found.name.endswith("_inputs.yaml") and found.is_relative_to(FEDERAL_FORMS)
            else found.read_text(encoding="utf-8")
        )
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        _parameters(),
        newfoundland_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-NL"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(newfoundland_kinds().kind(identifier)).value)


def _steps() -> list[dict[str, Any]]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    steps = part["capabilities"]
    assert isinstance(steps, list)
    return steps


def _expected(salary: str) -> Decimal:
    """Line 6 recomputed from the salary: 15% of the line 4 figure, rounded half-up to the cent."""
    net_income = salary_net_income(D(salary))
    line_4 = max(net_income - D("38712.00"), D(0))
    return _cent(line_4 * D("0.15"))


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def salary_net_income(salary: Decimal) -> Decimal:
    """The salary less the enhanced CPP deduction (2025): 1% of the earnings from $3,500 to
    $71,300, plus 4% of the earnings from $71,300 to $81,200."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    return salary - enhanced - second


# salary, line 4, line 6.
CASES = [
    ("30000", "0.00", "0.00"),
    ("50000", "10823.00", "1623.45"),
    ("100000", "60214.00", "9032.10"),
    ("200000", "160214.00", "24032.10"),
    # Half a cent: 0.30 x 0.15 = 0.045 rounds half-up to 0.05 (half-even would give 0.04).
    ("39067.98", "0.30", "0.05"),
    # 0.01 x 0.15 = 0.0015 rounds to 0.00.
    ("39067.69", "0.01", "0.00"),
]


@pytest.mark.parametrize(("salary", "line_4", "expected"), CASES)
def test_line_6_is_line_4_times_15_percent(
    tmp_path: Path, salary: str, line_4: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert _value(sheet, LINE_4) == D(line_4)
    assert _expected(salary) == D(expected)
    line_6 = _value(sheet, LINE_6)
    assert line_6 == D(expected)
    assert str(line_6) == expected


def test_line_6_is_never_blank_and_traces_no_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "50000")

    assert not sheet.get(newfoundland_kinds().kind(LINE_6)).is_blank
    assert not [t for t in sheet.trace if isinstance(t, BlankPassedOnLine)]
    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)
    assert not any("left blank, taken as" in row.lower() for row in rows)


def test_the_row_traces_the_product_with_the_dataset_rate_and_rounding(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "50000")
    kinds = newfoundland_kinds()
    dataset = _parameters().get(RATE, 2025, RATE_KIND)

    (line,) = [t for t in sheet.trace if isinstance(t, RateAppliedLine)]
    assert line == RateAppliedLine(
        output=kinds.kind(LINE_6),
        base=kinds.kind(LINE_4),
        base_amount=D("10823.00"),
        rate=dataset.values,
        rounding=dataset.rounding,
        result=D("1623.45"),
    )
    assert dataset.values.value == D("0.15")


def test_the_row_reads_in_english_with_the_rate_and_rounding(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "50000")

    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    (row,) = [row for row in rows if "1623.45" in row]
    assert "10823.00" in row
    assert "15" in row
    assert "rounded to the nearest cent" in row


def test_the_part_is_one_untitled_apply_rate_step_carrying_the_reference_6() -> None:
    (step,) = _steps()

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/apply_rate",
        "reference": "6",
        "unit": "ca/cad",
        "params": {"rate": RATE},
        "consumes": {"base": LINE_4},
        "produces": {"output": LINE_6},
    }


def test_line_6_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = newfoundland_kinds().kind(LINE_6)

    assert kind is nl_catalog.WORKSHEET_NL428_AGE_AMOUNT_LINE_6
    assert LINE_6.startswith("ca-nl/")
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
