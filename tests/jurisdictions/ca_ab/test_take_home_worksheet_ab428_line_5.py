"""Worksheet AB428 (2025) line 5, line 3 multiplied by the line 4 rate of 8%, from the salary alone.

Form text (Worksheet AB428, CRA 5009-D): "Line 4: Alberta non-refundable tax credit rate 8%" and
"Line 5: Line 3 multiplied by the percentage from line 4 = ^". Line 4 is a printed rate, so it is
the `ca-ab/credit_rate` dataset figure (the same 8% as AB428 line 53) and has no step of its own;
line 5 is one core/apply_rate step over line 3, rounded half-up to the cent by the dataset's own
rule. The form prints no title text for the line, so the step is untitled.

The test composes the real Alberta salary part, the real Schedule 8 and T2204 parts, the real
AB428 credits parts up to line 52, the real `worksheet_ab428_line_1.yaml`,
`worksheet_ab428_line_2.yaml` and `worksheet_ab428_line_3.yaml` parts and the new
`worksheet_ab428_line_5.yaml`, and types in only the salary (and, in one test, line 41). The
header and the two form declarations (AB428 credits, exporting lines 41 and 52, and the
worksheet, exporting lines 1, 2, 3 and 5) are made up here, because the shared scaffold owns them.
Alberta is not yet listed in the registrations, so the service is built here over the Alberta
package list of `support.py`. The figures are hand-computed from the printed forms (not a CRA
example): line 3 is 23,467.75, 26,692.23 and 26,756.58 at the three salaries (line 41 blank, so
line 3 equals line 52), times 0.08, half-up to the cent. A given line 41 raises line 1 and line 2
together, so line 3 and line 5 do not move.
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
    AB428_UNUSED_TUITION_LINE_41,
    WORKSHEET_AB428_LINE_3,
    WORKSHEET_AB428_LINE_5,
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
LINE_PART = ALBERTA_PARTS / "worksheet_ab428_line_5.yaml"
KIND = "ca-ab/worksheet_ab428_line_5"
LINE_3 = "ca-ab/worksheet_ab428_line_3"
RATE_FAMILY = "ca-ab/credit_rate"

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
    capabilities: []
    """)

# salary, line 5: line 3 (23,467.75, 26,692.23 and 26,756.58, as the line 3 test pins) times 0.08,
# half-up to the cent: 1,877.42 (1,877.4200), 2,135.38 (2,135.3784) and 2,140.53 (2,140.5264).
CASES = [("20000", "1877.42"), ("70000", "2135.38"), ("200000", "2140.53")]


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


def _sheet(tmp_path: Path, salary: str, *extra: Artifact[Decimal]) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), *extra]
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-AB"), 2025, *given)
    (sheet,) = worksheets["ca-ab/worksheet_ab428"]
    return sheet


def _rate_source() -> YamlParameterSource:
    return YamlParameterSource(
        alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
    )


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_5_is_line_3_times_8_percent_at_each_salary(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(WORKSHEET_AB428_LINE_5).value == D(expected)
    assert sheet.get(WORKSHEET_AB428_LINE_5).value.as_tuple().exponent == -2


def test_a_given_line_41_does_not_change_line_5(tmp_path: Path) -> None:
    # Line 41 raises line 1 and line 2 together (28,192.23 and 1,500.00 at salary 70,000), so
    # line 3 stays 26,692.23 and line 5 stays 2,135.38.
    sheet = _sheet(tmp_path, "70000", Artifact(AB428_UNUSED_TUITION_LINE_41, D("1500.00")))

    assert sheet.get(WORKSHEET_AB428_LINE_3).value == D("26692.23")
    assert sheet.get(WORKSHEET_AB428_LINE_5).value == D("2135.38")


def test_the_step_traces_one_rate_applied_line_with_the_cent_rounding(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    kinds = alberta_kinds()
    data = _rate_source().get(RATE_FAMILY, 2025, RATE)

    (line,) = [
        t for t in sheet.trace if isinstance(t, RateAppliedLine) and t.output is kinds.kind(KIND)
    ]
    assert line == RateAppliedLine(
        output=kinds.kind(KIND),
        base=kinds.kind(LINE_3),
        base_amount=D("26692.23"),
        rate=data.values,
        rounding=data.rounding,
        result=D("2135.38"),
    )


def test_the_rate_row_reads_in_english_with_the_rounding_named(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    rows = EnglishTraceRenderer().render_all(sheet.trace)

    assert [row for row in rows if "worksheet ab428 line 3" in row] == [
        "8% of worksheet ab428 line 3 (26692.23) gives 2135.38 (rounded to the nearest cent)."
    ]


def _line_5_at(line_3_amount: str) -> Decimal:
    """Line 5 over a given line 3: the capability the part builds, with the real dataset."""
    kinds = alberta_kinds()
    line_3, line_5 = kinds.kind(LINE_3), kinds.kind(KIND)
    assert isinstance(line_3, AmountKind)
    assert isinstance(line_5, AmountKind)
    result = ApplyRate(_rate_source().get(RATE_FAMILY, 2025, RATE), line_3, line_5).compute(
        (Artifact(line_3, D(line_3_amount)),)
    )
    (output,) = result.outputs
    value: Decimal = output.value
    return value


@pytest.mark.parametrize(
    ("line_3", "expected"),
    [
        ("0.00", "0.00"),
        ("0.0624", "0.00"),
        ("0.0625", "0.01"),
        ("1.5624", "0.12"),
        ("1.5625", "0.13"),
        ("26692.23", "2135.38"),
    ],
)
def test_line_5_rounds_half_up_to_the_cent_at_the_half_cent_boundary(
    line_3: str, expected: str
) -> None:
    assert _line_5_at(line_3) == D(expected)


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
        "reference": "5",
        "unit": "ca/cad",
        "params": {"rate": RATE_FAMILY},
        "consumes": {"base": LINE_3},
        "produces": {"output": KIND},
    }


def test_line_5_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = alberta_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert kind is WORKSHEET_AB428_LINE_5
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
