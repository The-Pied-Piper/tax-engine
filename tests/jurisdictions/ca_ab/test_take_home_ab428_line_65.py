"""AB428 (2025) line 65, add lines 62 to 64, real parts.

Form text (Form AB428, CRA 5009-c): "Line 65: Add lines 62 to 64. = ^". One core/sum step, rounded
half-up to the cent by `ca-ab/cent_rounding`, over line 62 (the credits from line 58), line 63
(the Alberta dividend tax credit, an optional input) and line 64 (the minimum tax carryover, the
35% result, box B). The form prints no title for the line beyond its label, so the step is
untitled. Line 63 is left blank by a salary-only filer, so the step has a blank rule reading it as
0 and prints its own "Left blank, taken as 0" row; line 62 and line 64 are always computed (the
line 64 amount, box A, defaults to 0), so they need none. The form prints no floor on line 65, but
every addend is non-negative, so the kind is non-negative.

The test composes the real Alberta salary part, the real Schedule 8 and T2204 parts, the real AB428
credits parts up to line 58, the line 62 part, the line 63 input part, the line 64 input and
calculation parts, and the new `ab428_line_65.yaml`, and types in only the salary, plus line 63
and the line 64 amount where a case needs them. The header and the two form declarations (AB428
credits, exporting line 58, and AB428, exporting line 65) are made up here, because the shared
scaffold owns them. At the three salaries line 62 is 1,877.42, 2,135.38 and 2,140.53 (the line 58
test) and lines 63 and 64 are 0, so line 65 is the same.
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
    AB428_CREDITS_FROM_LINE_58_LINE_62,
    AB428_CREDITS_SUBTOTAL_LINE_65,
    AB428_DIVIDEND_TAX_CREDIT_LINE_63,
    AB428_MINIMUM_TAX_CARRYOVER_AMOUNT_LINE_64,
    AB428_MINIMUM_TAX_CARRYOVER_LINE_64,
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
LINE_PART = ALBERTA_PARTS / "ab428_line_65.yaml"
IDENTIFIER = "ca-ab/ab428_credits_subtotal_line_65"

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
        - ca-ab/ab428_non_refundable_credits_line_58
    capabilities: []
    """)
AB428_FORM = dedent("""\
    form:
      name: ca-ab/ab428
      required: true
      exports:
        - ca-ab/ab428_credits_subtotal_line_65
    capabilities: []
    """)

# salary, line 65: line 62 (line 58, as the line 58 test pins) plus lines 63 and 64 of 0.
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
    yield ALBERTA_PARTS / "ab428_credits_line_58.yaml"
    yield ALBERTA_PARTS / "ab428_line_62.yaml"
    yield ALBERTA_PARTS / "ab428_line_63_inputs.yaml"
    yield ALBERTA_PARTS / "ab428_line_64_inputs.yaml"
    yield ALBERTA_PARTS / "ab428_line_64.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Alberta manifest of a test header, two form declarations and
    the real part files, every other namespace being the Alberta package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_credits_form.yaml").write_text(CREDITS_FORM, encoding="utf-8")
    (folder / "02_ab428_form.yaml").write_text(AB428_FORM, encoding="utf-8")
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
    (sheet,) = worksheets["ca-ab/ab428"]
    return sheet


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_65_is_line_62_when_lines_63_and_64_are_empty(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(AB428_CREDITS_SUBTOTAL_LINE_65).value == D(expected)
    assert sheet.get(AB428_CREDITS_FROM_LINE_58_LINE_62).value == D(expected)
    assert sheet.get(AB428_MINIMUM_TAX_CARRYOVER_LINE_64).value == D("0")


def test_line_65_adds_lines_63_and_64_when_they_are_given(tmp_path: Path) -> None:
    sheet = _sheet(
        tmp_path,
        "70000",
        Artifact(AB428_DIVIDEND_TAX_CREDIT_LINE_63, D("100.00")),
        Artifact(AB428_MINIMUM_TAX_CARRYOVER_AMOUNT_LINE_64, D("1000")),
    )

    assert sheet.get(AB428_MINIMUM_TAX_CARRYOVER_LINE_64).value == D("350.00")
    # 2,135.38 plus 100.00 plus 350.00.
    assert sheet.get(AB428_CREDITS_SUBTOTAL_LINE_65).value == D("2585.38")


def test_line_65_is_rounded_half_up_to_the_cent(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(AB428_DIVIDEND_TAX_CREDIT_LINE_63, D("0.005")))

    # 2,135.38 plus 0.005 is 2,135.385, rounded half-up to 2,135.39.
    assert sheet.get(AB428_CREDITS_SUBTOTAL_LINE_65).value == D("2135.39")


def _left_blank_rows(rows: Sequence[str]) -> int:
    return sum("Left blank, taken as 0" in row for row in rows)


def test_a_blank_line_63_prints_the_steps_own_left_blank_row(tmp_path: Path) -> None:
    given_dir = tmp_path / "given"
    given_dir.mkdir()
    blank = EnglishTraceRenderer().render_all(_sheet(tmp_path, "70000").trace)
    given = EnglishTraceRenderer().render_all(
        _sheet(given_dir, "70000", Artifact(AB428_DIVIDEND_TAX_CREDIT_LINE_63, D("100.00"))).trace
    )

    # Other steps on the sheet print their own blank rows either way; line 65's is the difference.
    assert _left_blank_rows(blank) == _left_blank_rows(given) + 1


def test_the_trace_has_a_row_for_line_65(tmp_path: Path) -> None:
    rows = EnglishTraceRenderer().render_all(_sheet(tmp_path, "70000").trace)

    assert any(("2135.38" in row or "2,135.38" in row) and "gives" in row for row in rows)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_sum_step() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ab/ab428"}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "blank", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "65",
        "unit": "ca/cad",
        "params": {"rounding": "ca-ab/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-ab/ab428_credits_from_line_58_line_62",
                "ca-ab/ab428_dividend_tax_credit_line_63",
                "ca-ab/ab428_minimum_tax_carryover_line_64",
            ]
        },
        "blank": {"ca-ab/ab428_dividend_tax_credit_line_63": "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_line_65_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = alberta_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = kinds.kind(IDENTIFIER)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is AB428_CREDITS_SUBTOTAL_LINE_65
