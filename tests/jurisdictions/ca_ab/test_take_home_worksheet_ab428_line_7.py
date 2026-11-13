"""Worksheet AB428 (2025) line 7, line 5 minus line 6 (not below 0), from the real parts.

Form text (Worksheet AB428, CRA 5009-D):
"Line 7: Line 5 minus line 6 (if negative, enter \\"0\\") = ^".
Line 7 is one core/subtract_not_below_zero step over line 5 (`amount`) and line 6 (`less`), rounded
half-up to the cent by the dataset's own rule. Lines 5 and 6 are never blank (line 6 is the printed
base amount of 4,800.00 and line 5 is signed but always present), so the step has no blank rule.
The form prints no title text for the line, so the step is untitled.

The test composes the real Alberta salary part, the real Schedule 8 and T2204 parts, the real
AB428 credits parts up to line 52, the real `worksheet_ab428_line_1.yaml`,
`worksheet_ab428_line_2.yaml`, `worksheet_ab428_line_3.yaml`, `worksheet_ab428_line_5.yaml` and
`worksheet_ab428_line_6.yaml` parts and the new `worksheet_ab428_line_7.yaml`, and types in only
the salary. The header and the two form declarations (AB428 credits, exporting lines 41 and 52,
and the worksheet, exporting lines 1, 2, 3, 5, 6 and 7) are made up here, because the shared
scaffold owns them. Alberta is not yet listed in the registrations, so the service is built here
over the Alberta package list of `support.py`.

Figures (hand-computed from the printed forms, not a CRA example, and recomputed here from the real
parts): line 5 is 1,877.42, 2,135.38 and 2,140.53 at the three salaries and line 6 is 4,800.00, so
line 7 is 0.00 at all three (line 5 is below line 6). The positive side of the subtraction cannot
be reached by a salary alone (it turns on only past a line 52 of 60,000), so it is exercised on the
capability the part builds, over given lines 5 and 6 and the real dataset.
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
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BlankPassedOnLine, SubtractedNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ab.catalog import (
    WORKSHEET_AB428_LINE_5,
    WORKSHEET_AB428_LINE_6,
    WORKSHEET_AB428_LINE_7,
)
from tax_engine.jurisdictions.core.capabilities.subtract_not_below_zero import (
    SubtractNotBelowZero,
)
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
LINE_PART = ALBERTA_PARTS / "worksheet_ab428_line_7.yaml"
KIND = "ca-ab/worksheet_ab428_line_7"
LINE_5 = "ca-ab/worksheet_ab428_line_5"
LINE_6 = "ca-ab/worksheet_ab428_line_6"
ROUNDING = "ca-ab/cent_rounding"

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
        - ca-ab/ab428_unused_tuition_rounded_line_41
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
    capabilities: []
    """)

# salary, line 5 (the line 5 test pins these), line 6 (the printed base amount), line 7: line 5 is
# below line 6 at every salary, so line 7 is the floor, 0.00.
CASES = [
    ("20000", "1877.42", "4800.00", "0.00"),
    ("70000", "2135.38", "4800.00", "0.00"),
    ("200000", "2140.53", "4800.00", "0.00"),
]


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
    yield ALBERTA_PARTS / "ab428_credits_line_41.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_43.yaml"
    yield ALBERTA_PARTS / "ab428_line_51_inputs.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_52.yaml"
    yield ALBERTA_PARTS / "worksheet_ab428_line_1.yaml"
    yield ALBERTA_PARTS / "worksheet_ab428_line_2.yaml"
    yield ALBERTA_PARTS / "worksheet_ab428_line_3.yaml"
    yield ALBERTA_PARTS / "worksheet_ab428_line_5.yaml"
    yield ALBERTA_PARTS / "worksheet_ab428_line_6.yaml"
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


def _rounding() -> Any:
    return YamlParameterSource(
        alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


def _amount_kind(identifier: str) -> AmountKind:
    kind = alberta_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


@pytest.mark.parametrize(("salary", "line_5", "line_6", "expected"), CASES)
def test_line_7_is_zero_while_line_5_is_below_line_6_at_each_salary(
    tmp_path: Path, salary: str, line_5: str, line_6: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    # Line 5 and line 6 are recomputed from the real parts, not only taken from the ticket.
    assert sheet.get(WORKSHEET_AB428_LINE_5).value == D(line_5)
    assert sheet.get(WORKSHEET_AB428_LINE_6).value == D(line_6)
    line_7 = sheet.get(WORKSHEET_AB428_LINE_7).value
    assert line_7 == D(expected)
    # The floor is the cent zero of the rounding dataset: printed 0.00, never -0.00.
    assert str(line_7) == "0.00"
    assert line_7.as_tuple().exponent == -2
    assert not line_7.is_signed()


def test_line_7_is_never_blank_and_traces_no_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    assert not sheet.get(WORKSHEET_AB428_LINE_7).is_blank
    assert not [t for t in sheet.trace if isinstance(t, BlankPassedOnLine)]


def test_the_step_traces_one_subtracted_not_below_zero_line_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "70000")
    kinds = alberta_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, SubtractedNotBelowZeroLine)]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(KIND),
        minuend=kinds.kind(LINE_5),
        minuend_amount=D("2135.38"),
        subtrahend=kinds.kind(LINE_6),
        subtrahend_amount=D("4800.00"),
        rounding=_rounding().rounding,
        result=D("0.00"),
    )


def test_the_floored_row_reads_in_english_with_the_rounding_named(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    rows = EnglishTraceRenderer().render_all(sheet.trace)

    assert [row for row in rows if "not below 0" in row] == [
        "Worksheet ab428 line 5 (2135.38) less worksheet ab428 line 6 (4800.00), not below 0, "
        "gives 0.00 (rounded to the nearest cent)."
    ]


def _line_7_at(line_5_amount: str, line_6_amount: str) -> Artifact[Decimal]:
    """Line 7 over given lines 5 and 6: the capability the part builds, with the real dataset."""
    line_5, line_6, line_7 = _amount_kind(LINE_5), _amount_kind(LINE_6), _amount_kind(KIND)
    capability = SubtractNotBelowZero(_rounding(), line_5, line_6, line_7)
    result = capability.compute(
        (Artifact(line_5, D(line_5_amount)), Artifact(line_6, D(line_6_amount)))
    )
    (output,) = result.outputs
    return output


@pytest.mark.parametrize(
    ("line_5", "line_6", "expected"),
    [
        # Line 5 above line 6: the difference.
        ("4800.01", "4800.00", "0.01"),
        ("5000.00", "4800.00", "200.00"),
        ("5252.00", "4800.00", "452.00"),
        # Exactly equal: the cent zero, not negative.
        ("4800.00", "4800.00", "0.00"),
        # Line 5 below line 6: the floor.
        ("4799.99", "4800.00", "0.00"),
        ("2135.38", "4800.00", "0.00"),
        # Line 5 is signed (a negative line 3), so the floor also catches a negative minuend.
        ("-40.00", "4800.00", "0.00"),
        ("0.00", "4800.00", "0.00"),
    ],
)
def test_line_7_is_line_5_minus_line_6_not_below_zero_to_the_cent(
    line_5: str, line_6: str, expected: str
) -> None:
    line_7 = _line_7_at(line_5, line_6).value

    assert line_7 == D(expected)
    assert line_7.as_tuple().exponent == -2
    assert not line_7.is_signed()


def test_a_floored_zero_and_an_exact_equal_are_the_same_positive_cent_zero() -> None:
    below = _line_7_at("100.00", "4800.00").value
    equal = _line_7_at("4800.00", "4800.00").value

    assert str(below) == str(equal) == "0.00"
    assert not below.is_signed()
    assert not equal.is_signed()


def test_the_positive_row_traces_the_subtraction_with_the_rounding_named() -> None:
    kinds = alberta_kinds()
    line_5, line_6, line_7 = _amount_kind(LINE_5), _amount_kind(LINE_6), _amount_kind(KIND)
    result = SubtractNotBelowZero(_rounding(), line_5, line_6, line_7).compute(
        (Artifact(line_5, D("5252.00")), Artifact(line_6, D("4800.00")))
    )

    (line,) = result.trace
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(KIND),
        minuend=kinds.kind(LINE_5),
        minuend_amount=D("5252.00"),
        subtrahend=kinds.kind(LINE_6),
        subtrahend_amount=D("4800.00"),
        rounding=_rounding().rounding,
        result=D("452.00"),
    )


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_step_with_no_blank_rule() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ab/worksheet_ab428"}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "7",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_5, "less": LINE_6},
        "produces": {"output": KIND},
    }


def test_line_7_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = alberta_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert kind is WORKSHEET_AB428_LINE_7
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
