"""AB428 (2025) line 41, rounded to the cent when it is taken (#831), from the salary alone.

Form text (Form AB428, CRA 5009-c-25e.txt): "Line 41 and line 58560: Your unused tuition and
education amounts (attach Schedule AB(S11))"; Worksheet AB428 (CRA 5009-D): "Line 2: Amount from
line 58560 of your Form AB428". Line 41 is an optional input, blank for a salary-only filer. One
core/sum step over the input alone, as line 25 is over line 16 (`ab428_line_25.yaml`), reads the
blank as 0, rounds to the cent and produces `ca-ab/ab428_unused_tuition_rounded_line_41`, which the
form exports in place of the raw input; line 43 and Worksheet AB428 line 2 read that figure, so
line 43 (through lines 52 and Worksheet line 1) and line 2 agree to the cent.

The test composes the real Alberta salary part, the real Schedule 8 and T2204 parts, the real AB428
credits parts up to line 52 and the real Worksheet AB428 lines 1, 2, 3 and 5 parts, with the new
`ab428_credits_line_41.yaml`, and types in only the salary and line 41. The figures are
hand-computed from the printed forms (not a CRA example): line 52 is 26,692.23 at salary 70,000 with
line 41 blank, so Worksheet line 1 is 26,692.23 plus the rounded line 41, line 2 is the rounded line
41, line 3 is 26,692.23 and line 5 is 2,135.38 (8% of 26,692.23 is 2,135.3784).
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
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ab.catalog import (
    AB428_UNUSED_TUITION_LINE_41,
    WORKSHEET_AB428_LINE_1,
    WORKSHEET_AB428_LINE_2,
    WORKSHEET_AB428_LINE_3,
    WORKSHEET_AB428_LINE_5,
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
LINE_PART = ALBERTA_PARTS / "ab428_credits_line_41.yaml"
IDENTIFIER = "ca-ab/ab428_unused_tuition_rounded_line_41"

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
    capabilities: []
    """)


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
    yield LINE_PART
    yield ALBERTA_PARTS / "ab428_credits_line_43.yaml"
    yield ALBERTA_PARTS / "ab428_line_51_inputs.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_52.yaml"
    yield ALBERTA_PARTS / "worksheet_ab428_line_1.yaml"
    yield ALBERTA_PARTS / "worksheet_ab428_line_2.yaml"
    yield ALBERTA_PARTS / "worksheet_ab428_line_3.yaml"
    yield ALBERTA_PARTS / "worksheet_ab428_line_5.yaml"


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


def _sheets(tmp_path: Path, salary: str, *extra: Artifact[Decimal]) -> tuple[Worksheet, Worksheet]:
    """The AB428 credits sheet and the Worksheet AB428 sheet."""
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), *extra]
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-AB"), 2025, *given)
    (credits,) = worksheets["ca-ab/ab428_credits"]
    (worksheet,) = worksheets["ca-ab/worksheet_ab428"]
    return credits, worksheet


def _line_41(value: str) -> Artifact[Decimal]:
    return Artifact(AB428_UNUSED_TUITION_LINE_41, D(value))


def test_a_blank_line_41_is_0_at_70000_and_prints_the_steps_own_left_blank_row(
    tmp_path: Path,
) -> None:
    credits, worksheet = _sheets(tmp_path, "70000")

    assert credits.get(alberta_kinds().kind(IDENTIFIER)).value == D("0.00")
    assert worksheet.get(WORKSHEET_AB428_LINE_1).value == D("26692.23")
    assert worksheet.get(WORKSHEET_AB428_LINE_2).value == D("0.00")
    rows = EnglishTraceRenderer().render_all(credits.trace)
    assert any("Left blank, taken as 0" in row for row in rows)


# line 41 given, the line 41 step, Worksheet lines 1, 2, 3 and 5. The ticket's observed table
# (100.005: line 2 of 100.005 and line 3 of 26,692.24) is the bug and must no longer occur.
CASES = [
    ("100.00", "100.00", "26792.23", "100.00", "26692.23", "2135.38"),
    ("100.005", "100.01", "26792.24", "100.01", "26692.23", "2135.38"),
    ("100.004", "100.00", "26792.23", "100.00", "26692.23", "2135.38"),
]


@pytest.mark.parametrize(("given", "step", "line_1", "line_2", "line_3", "line_5"), CASES)
def test_line_41_is_rounded_to_the_cent_and_every_reader_agrees(
    tmp_path: Path, given: str, step: str, line_1: str, line_2: str, line_3: str, line_5: str
) -> None:
    credits, worksheet = _sheets(tmp_path, "70000", _line_41(given))

    assert credits.get(alberta_kinds().kind(IDENTIFIER)).value == D(step)
    assert worksheet.get(WORKSHEET_AB428_LINE_1).value == D(line_1)
    assert worksheet.get(WORKSHEET_AB428_LINE_2).value == D(line_2)
    assert worksheet.get(WORKSHEET_AB428_LINE_3).value == D(line_3)
    assert worksheet.get(WORKSHEET_AB428_LINE_5).value == D(line_5)


def test_line_2_never_prints_a_non_cent_amount(tmp_path: Path) -> None:
    _, worksheet = _sheets(tmp_path, "70000", _line_41("100.005"))
    rows = EnglishTraceRenderer().render_all(worksheet.trace)

    assert not any("100.005" in row for row in rows)
    assert worksheet.get(WORKSHEET_AB428_LINE_2).value.as_tuple().exponent == -2


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_sum_step_like_line_25() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ab/ab428_credits"}
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
        "name": "core/sum",
        "reference": "41",
        "unit": "ca/cad",
        "params": {"rounding": "ca-ab/cent_rounding"},
        "consumes": {"parts": ["ca-ab/ab428_unused_tuition_line_41"]},
        "blank": {"ca-ab/ab428_unused_tuition_line_41": "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_rounded_line_41_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = alberta_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = kinds.kind(IDENTIFIER)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
