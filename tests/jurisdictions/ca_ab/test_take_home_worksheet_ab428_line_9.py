"""Worksheet AB428 (2025) line 9, line 7 multiplied by the line 8 rate of 25%, salary alone.

Form text (Worksheet AB428, CRA 5009-D): "Line 8: Applicable rate 25%" and "Line 9: Line 7
multiplied by the percentage from line 8 enter this amount on line 61545 of your Form AB428.".
Line 8 is a printed rate, so it is the `ca-ab/supplemental_credit_rate` dataset figure and has no
step of its own; line 9 is one core/apply_rate step over line 7, rounded half-up to the cent by the
dataset's own rule. The form prints no title text for the line, so the step is untitled. Line 7 is
floored at 0 by the form, so line 9 is never negative.

The test composes the real Alberta salary part, the real Schedule 8 and T2204 parts, the real
AB428 credits parts up to line 52, the real `worksheet_ab428_line_1.yaml`, `_line_2.yaml`,
`_line_3.yaml`, `_line_5.yaml`, `_line_6.yaml` and `_line_7.yaml` parts and the new
`worksheet_ab428_line_9.yaml`, and types in only the salary. The header and the two form
declarations (AB428 credits, exporting lines 41 and 52, and the worksheet, exporting lines 1, 2,
3, 5, 6, 7 and 9) are made up here, because the shared scaffold owns them. Alberta is not yet
listed in the registrations, so the service is built here over the Alberta package list of
`support.py`.

Figures (hand-computed from the printed forms, not a CRA example, and recomputed here from the real
parts): line 7 is 0.00 at the three salaries (line 5 is below the 4,800.00 of line 6), so line 9 is
0.00 x 0.25 = 0.00 at all three. The positive side cannot be reached by a salary alone (it turns on
only past a line 52 of 60,000), so it is exercised on the capability the part builds, over a given
line 7 and the real dataset: 100.00 x 0.25 = 25.00, and 0.02 x 0.25 = 0.005, half-up to 0.01.
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
import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rate import RATE
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import RateAppliedLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ab.catalog import (
    WORKSHEET_AB428_LINE_7,
    WORKSHEET_AB428_SUPPLEMENTAL_CREDIT_LINE_9,
)
from tax_engine.jurisdictions.core.capabilities.apply_rate import ApplyRate
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
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = ALBERTA_PARTS / "worksheet_ab428_line_9.yaml"
KIND = "ca-ab/worksheet_ab428_supplemental_credit_line_9"
LINE_7 = "ca-ab/worksheet_ab428_line_7"
RATE_FAMILY = "ca-ab/supplemental_credit_rate"

HEADER = dedent("""\
    jurisdiction: CA-AB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
CREDITS_FORM = dedent("""\
    form:
      name: ca-ab/ab428_credits
      required: true
      exports:
        - ca-ab/ab428_unused_tuition_line_41
        - ca-ab/ab428_credits_total_line_52
    capabilities: []
    """)
WORKSHEET_FORM = dedent("""\
    form:
      name: ca-ab/worksheet_ab428
      required: true
      exports:
        - ca-ab/worksheet_ab428_line_1
        - ca-ab/worksheet_ab428_line_2
        - ca-ab/worksheet_ab428_line_3
        - ca-ab/worksheet_ab428_line_5
        - ca-ab/worksheet_ab428_line_6
        - ca-ab/worksheet_ab428_line_7
        - ca-ab/worksheet_ab428_supplemental_credit_line_9
    capabilities: []
    """)

# salary, line 9: line 7 is 0.00 at all three salaries (the line 7 test pins this), times 0.25.
CASES = [("20000", "0.00"), ("70000", "0.00"), ("200000", "0.00")]


def _part_files() -> Iterator[Path]:
    yield ALBERTA_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    yield from sorted(FEDERAL_FORMS.rglob("t2204*.yaml"))
    yield ALBERTA_PARTS / "ab428_line_16.yaml"
    yield ALBERTA_PARTS / "ab428_line_25.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_27.yaml"
    yield ALBERTA_PARTS / "ab428_line_29.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_32.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_33.yaml"
    yield ALBERTA_PARTS / "ab428_line_34_inputs.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_36.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_39.yaml"
    yield ALBERTA_PARTS / "ab428_line_41_input.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_43.yaml"
    yield ALBERTA_PARTS / "ab428_line_51_inputs.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_52.yaml"
    yield ALBERTA_PARTS / "worksheet_ab428_line_1.yaml"
    yield ALBERTA_PARTS / "worksheet_ab428_line_2.yaml"
    yield ALBERTA_PARTS / "worksheet_ab428_line_3.yaml"
    yield ALBERTA_PARTS / "worksheet_ab428_line_5.yaml"
    yield ALBERTA_PARTS / "worksheet_ab428_line_6.yaml"
    yield ALBERTA_PARTS / "worksheet_ab428_line_7.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Alberta manifest of a test header, two form declarations and
    the real part files, every other namespace being the Alberta package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_credits_form.yaml").write_text(CREDITS_FORM, encoding="utf-8")
    (folder / "02_worksheet_form.yaml").write_text(WORKSHEET_FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=3):
        text = (
            inputs_without_form(found)
            if found.name.endswith("_inputs.yaml") and found.is_relative_to(FEDERAL_FORMS)
            else found.read_text(encoding="utf-8")
        )
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-AB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-ab/worksheet_ab428"]
    return sheet


def _rate_source() -> YamlParameterSource:
    return YamlParameterSource(
        alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
    )


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_9_is_line_7_times_25_percent_at_each_salary(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    # Line 7 is recomputed from the real parts, not only taken from the ticket.
    assert sheet.get(WORKSHEET_AB428_LINE_7).value == D("0.00")
    line_9 = sheet.get(WORKSHEET_AB428_SUPPLEMENTAL_CREDIT_LINE_9).value
    assert line_9 == D(expected)
    assert str(line_9) == "0.00"
    assert line_9.as_tuple().exponent == -2
    assert not line_9.is_signed()


def test_the_step_traces_one_rate_applied_line_with_the_cent_rounding(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    kinds = alberta_kinds()
    data = _rate_source().get(RATE_FAMILY, 2025, RATE)

    (line,) = [
        t for t in sheet.trace if isinstance(t, RateAppliedLine) and t.output is kinds.kind(KIND)
    ]
    assert line == RateAppliedLine(
        output=kinds.kind(KIND),
        base=kinds.kind(LINE_7),
        base_amount=D("0.00"),
        rate=data.values,
        rounding=data.rounding,
        result=D("0.00"),
    )


def test_the_rate_row_reads_in_english_with_the_rounding_named(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    rows = EnglishTraceRenderer().render_all(sheet.trace)

    assert [row for row in rows if "worksheet ab428 line 7 (" in row and "25%" in row] == [
        "25% of worksheet ab428 line 7 (0.00) gives 0.00 (rounded to the nearest cent)."
    ]


def _line_9_at(line_7_amount: str) -> Decimal:
    """Line 9 over a given line 7: the capability the part builds, with the real dataset."""
    kinds = alberta_kinds()
    line_7, line_9 = kinds.kind(LINE_7), kinds.kind(KIND)
    assert isinstance(line_7, AmountKind)
    assert isinstance(line_9, AmountKind)
    result = ApplyRate(_rate_source().get(RATE_FAMILY, 2025, RATE), line_7, line_9).compute(
        (Artifact(line_7, D(line_7_amount)),)
    )
    (output,) = result.outputs
    value: Decimal = output.value
    return value


@pytest.mark.parametrize(
    ("line_7", "expected"),
    [
        ("0.00", "0.00"),
        ("0.01", "0.00"),
        ("0.02", "0.01"),
        ("0.06", "0.02"),
        ("100.00", "25.00"),
        ("452.00", "113.00"),
        ("1234.56", "308.64"),
        ("0.03", "0.01"),
    ],
)
def test_line_9_is_a_quarter_of_line_7_rounded_half_up_to_the_cent(
    line_7: str, expected: str
) -> None:
    line_9 = _line_9_at(line_7)

    assert line_9 == D(expected)
    assert isinstance(line_9, Decimal)
    assert line_9.as_tuple().exponent == -2


def test_the_positive_row_reads_in_english_with_the_rounding_named() -> None:
    kinds = alberta_kinds()
    line_7, line_9 = kinds.kind(LINE_7), kinds.kind(KIND)
    assert isinstance(line_7, AmountKind)
    assert isinstance(line_9, AmountKind)
    result = ApplyRate(_rate_source().get(RATE_FAMILY, 2025, RATE), line_7, line_9).compute(
        (Artifact(line_7, D("100.00")),)
    )

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "25% of worksheet ab428 line 7 (100.00) gives 25.00 (rounded to the nearest cent).",
    )


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_apply_rate_step() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ab/worksheet_ab428"}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/apply_rate",
        "reference": "9",
        "unit": "ca/cad",
        "params": {"rate": RATE_FAMILY},
        "consumes": {"base": LINE_7},
        "produces": {"output": KIND},
    }


def test_line_9_is_the_registered_non_negative_decimal_amount_kind() -> None:
    kinds = alberta_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert kind is WORKSHEET_AB428_SUPPLEMENTAL_CREDIT_LINE_9
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
