"""Worksheet AB428 (2025) line 2, the amount from AB428 line 41, as the manifest part wires it.

Form text (CRA 5009-d-25e.txt): "Line 2: Amount from line 58560 of your Form AB428 ^". Line 2 is a
calculation, not an input: its one step is a core/record_total over the AB428 line 41 export
(`ca-ab/ab428_credits.ab428_unused_tuition_rounded_line_41`), as Ontario's line 1 reads a
cross-form export. The form prints no title text for the line, so the step is untitled. The export
is the line 41 step's whole-cent figure (#831), never blank, so line 2 has no blank rule and prints
no "left blank" row of its own; a line 41 with fractional cents is rounded before line 2 copies it.

The real line part, the real line 41 input part and the real line 41 step part are loaded from the
package. The header and the two form declarations (AB428 credits, exporting line 41, and the
worksheet, exporting line 2) are made up here, because the shared scaffold owns them. Alberta is
not yet listed in the registrations, so the service is built here over the Alberta package list
of `support.py`. The zero figures at every salary follow from line 41 being blank and read as 0
(not a CRA example).
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

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
    WORKSHEET_AB428_LINE_2,
)
from tests.jurisdictions.ca_ab.support import (
    alberta_capabilities,
    alberta_kinds,
    alberta_packages,
    alberta_parameter_parsers,
    alberta_units,
)
from tests.kinds import non_negative

D = Decimal
PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
LINE_PART = PARTS / "worksheet_ab428_line_2.yaml"
INPUT_PART = PARTS / "ab428_line_41_input.yaml"
LINE_41_PART = PARTS / "ab428_credits_line_41.yaml"
KIND = "ca-ab/worksheet_ab428_line_2"

HEADER = dedent("""\
    jurisdiction: CA-AB
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    """)
CREDITS_FORM = dedent("""\
    form:
      name: ca-ab/ab428_credits
      required: true
      exports:
        - ca-ab/ab428_unused_tuition_rounded_line_41
    capabilities: []
    """)
WORKSHEET_FORM = dedent("""\
    form:
      name: ca-ab/worksheet_ab428
      required: true
      exports:
        - ca-ab/worksheet_ab428_line_2
    capabilities: []
    """)


def _part_files() -> Iterator[Path]:
    yield INPUT_PART
    yield LINE_41_PART
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_credits_form.yaml").write_text(CREDITS_FORM, encoding="utf-8")
    (folder / "02_worksheet_form.yaml").write_text(WORKSHEET_FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=3):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"), encoding="utf-8"
        )
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, *extra: Artifact[Decimal]) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-AB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary)), *extra
    )
    (sheet,) = worksheets["ca-ab/worksheet_ab428"]
    return sheet


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_2_is_zero_at_every_salary_as_line_41_is_blank(tmp_path: Path, salary: str) -> None:
    assert _sheet(tmp_path, salary).get(WORKSHEET_AB428_LINE_2).value == D("0.00")


def test_line_2_is_line_41_when_it_is_given(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(AB428_UNUSED_TUITION_LINE_41, D("1500.00")))

    assert sheet.get(WORKSHEET_AB428_LINE_2).value == D("1500.00")


@pytest.mark.parametrize(
    ("line_41", "expected"),
    [("100.00", "100.00"), ("100.005", "100.01"), ("100.004", "100.00")],
)
def test_line_2_is_line_41_rounded_to_the_cent(tmp_path: Path, line_41: str, expected: str) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(AB428_UNUSED_TUITION_LINE_41, D(line_41)))

    assert sheet.get(WORKSHEET_AB428_LINE_2).value == D(expected)


def test_line_2_never_prints_a_non_cent_amount(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(AB428_UNUSED_TUITION_LINE_41, D("100.005")))
    rows = EnglishTraceRenderer().render_all(sheet.trace)

    assert not any("100.005" in row for row in rows)
    assert any("100.01" in row for row in rows)


def test_a_blank_line_41_prints_no_left_blank_row_on_line_2(tmp_path: Path) -> None:
    rows = EnglishTraceRenderer().render_all(_sheet(tmp_path, "70000").trace)

    assert not any("left blank, taken as 0" in row.lower() for row in rows)


def _line() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_record_total_step() -> None:
    part = _line()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ab/worksheet_ab428"}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "consumes", "produces"]
    assert step["name"] == "core/record_total"
    assert step["reference"] == "2"
    assert step["unit"] == "ca/cad"
    assert step["consumes"] == {
        "records": "ca-ab/ab428_credits.ab428_unused_tuition_rounded_line_41"
    }
    assert step["produces"] == {"output": KIND}


def test_line_2_is_a_registered_non_negative_amount_kind() -> None:
    kinds = alberta_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is WORKSHEET_AB428_LINE_2
