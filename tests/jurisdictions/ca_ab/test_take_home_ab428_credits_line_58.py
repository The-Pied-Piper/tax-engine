"""AB428 (2025) line 58, line 54 plus line 57, from the salary alone, real parts.

Form text (Form AB428, CRA 5009-c): "Line 58 and line 61500: Line 54 plus line 57 Enter this amount
on line 62. Alberta non-refundable tax credits =". Line 57, "Line 57 and line 58969: Line 55 plus
line 56", is the donations credit, an optional input, blank for a salary-only filer (lines 55 and
56 are not built). Line 58 is one core/sum over line 54 and the line 57 input, as Ontario line 50
is; the blank line 57 is read as 0 and the step prints its own "Left blank, taken as 0" row.

The test composes the real Alberta salary part, the real Schedule 8 and T2204 parts, the real line
16, line 25, line 27, line 29, line 32, line 33, line 36, line 39, line 43 and line 52 parts, the
line 34 inputs part, the line 41 input part, the line 51 inputs part, the line 54 part, the line 57
input part and the new `ab428_credits_line_58.yaml`, and types in only the salary (and, in some
tests, line 57). The form declaration is made up here, exporting only line 54 and line 58. The
figures are hand-computed from the printed forms (not a CRA example): line 54 is 1,877.42, 2,135.38
and 2,140.53 at the three salaries, plus line 57 of 0 when blank.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
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
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ab.catalog import (
    AB428_CREDITS_AT_RATE_LINE_54,
    AB428_DONATIONS_CREDIT_LINE_57,
    AB428_NON_REFUNDABLE_CREDITS_LINE_58,
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
LINE_PART = ALBERTA_PARTS / "ab428_credits_line_58.yaml"
IDENTIFIER = "ca-ab/ab428_non_refundable_credits_line_58"

HEADER = dedent("""\
    jurisdiction: CA-AB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-ab/ab428_credits
      required: true
      exports:
        - ca-ab/ab428_credits_at_rate_line_54
        - ca-ab/ab428_non_refundable_credits_line_58
    capabilities: []
    """)

# salary, line 58: line 54 (1,877.42, 2,135.38 and 2,140.53, as the line 54 test pins) plus line 57,
# blank and read as 0; lines 55 and 56 are not built.
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
    yield ALBERTA_PARTS / "ab428_credits_line_54.yaml"
    yield ALBERTA_PARTS / "ab428_line_57_inputs.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Alberta manifest of a test header, a form declaration and the
    real part files, every other namespace being the Alberta package list's own."""
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
    (sheet,) = worksheets["ca-ab/ab428_credits"]
    return sheet


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_58_is_line_54_when_line_57_is_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(AB428_NON_REFUNDABLE_CREDITS_LINE_58).value == D(expected)
    assert sheet.get(AB428_CREDITS_AT_RATE_LINE_54).value == D(expected)


def test_line_58_adds_line_57_when_it_is_given(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(AB428_DONATIONS_CREDIT_LINE_57, D("100.00")))

    assert sheet.get(AB428_CREDITS_AT_RATE_LINE_54).value == D("2135.38")
    assert sheet.get(AB428_NON_REFUNDABLE_CREDITS_LINE_58).value == D("2235.38")


def test_line_58_is_rounded_half_up_to_the_cent(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(AB428_DONATIONS_CREDIT_LINE_57, D("100.005")))

    # 2,135.38 plus 100.005 is 2,235.385, rounded half-up to 2,235.39.
    assert sheet.get(AB428_NON_REFUNDABLE_CREDITS_LINE_58).value == D("2235.39")


def _left_blank_rows(rows: Sequence[str]) -> int:
    return sum("Left blank, taken as 0" in row for row in rows)


def test_a_blank_line_57_prints_the_steps_own_left_blank_row(tmp_path: Path) -> None:
    given_dir = tmp_path / "given"
    given_dir.mkdir()
    blank = EnglishTraceRenderer().render_all(_sheet(tmp_path, "70000").trace)
    given = EnglishTraceRenderer().render_all(
        _sheet(given_dir, "70000", Artifact(AB428_DONATIONS_CREDIT_LINE_57, D("100.00"))).trace
    )

    # Other steps on the sheet print their own blank rows either way; line 58's is the difference.
    assert _left_blank_rows(blank) == _left_blank_rows(given) + 1


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_sum_step_like_ontario_line_50() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ab/ab428_credits"}
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
        "title": "Alberta non-refundable tax credits",
        "reference": "58",
        "unit": "ca/cad",
        "params": {"rounding": "ca-ab/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-ab/ab428_credits_at_rate_line_54",
                "ca-ab/ab428_donations_credit_line_57",
            ]
        },
        "blank": {"ca-ab/ab428_donations_credit_line_57": "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_line_58_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = alberta_kinds().kind(IDENTIFIER)

    assert kind is AB428_NON_REFUNDABLE_CREDITS_LINE_58
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
