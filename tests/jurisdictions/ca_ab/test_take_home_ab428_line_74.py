"""AB428 (2025) line 74, Alberta supplemental tax credit from Worksheet AB428 line 9, real parts.

Form text (Form AB428, CRA 5009-c): "Line 74 and line 61545: Alberta supplemental tax credit (use
Worksheet AB428)". Line 9 of the worksheet says "enter this amount on line 61545 of your Form
AB428". Line 74 is a calculation, not an input: its one step is a core/record_total over the line 9
export of `ca-ab/worksheet_ab428` (`ca-ab/worksheet_ab428_supplemental_credit_line_9`), a
cross-form read as line 62 reads line 58. The form prints no title for the line beyond its label,
so the step is untitled. Line 9 is always computed, so the step has no blank rule. The source line 9
is never negative, and the form prints no floor on line 74, so line 74 has none of its own: the kind
is non-negative only because the one amount it carries is.

The test composes the real Alberta salary part, the real Schedule 8 and T2204 parts, the real AB428
credits parts up to line 52, the real `worksheet_ab428_line_1.yaml`, `_line_2.yaml`, `_line_3.yaml`,
`_line_5.yaml`, `_line_6.yaml`, `_line_7.yaml` and `_line_9.yaml` parts and the new
`ab428_line_74.yaml`, and types in only the salary. The header and the three form declarations
(AB428 credits, exporting lines 41 and 52, the worksheet, exporting lines 1, 2, 3, 5, 6, 7 and 9,
and AB428, exporting line 74) are made up here, because the shared scaffold owns them.

Figures: worksheet line 5 is 1,877.42, 2,135.38 and 2,140.53 at the three salaries, below the
4,800.00 of line 6, so line 7 and line 9 are 0.00 and so is line 74 at all three. The positive side
cannot be reached by a salary alone (line 9 turns on only past a line 52 of 60,000), so it is
exercised on the capability the part builds, over a given line 9 record list: 25.00 gives 25.00 and
113.00 gives 113.00, and an empty list totals 0.00.
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
from tax_engine.domain.kinds import AmountKind, RecordListKind
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ab.catalog import (
    AB428_SUPPLEMENTAL_TAX_CREDIT_LINE_74,
    WORKSHEET_AB428_LINE_5,
    WORKSHEET_AB428_LINE_7,
    WORKSHEET_AB428_SUPPLEMENTAL_CREDIT_LINE_9,
)
from tax_engine.jurisdictions.core.capabilities.record_total import RecordTotal
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
LINE_PART = ALBERTA_PARTS / "ab428_line_74.yaml"
KIND = "ca-ab/ab428_supplemental_tax_credit_line_74"
LINE_9_FIELD = "ca-ab/worksheet_ab428_supplemental_credit_line_9"
LINE_9_LIST = "ca-ab/worksheet_ab428.worksheet_ab428_supplemental_credit_line_9"

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
AB428_FORM = dedent("""\
    form:
      name: ca-ab/ab428
      required: true
      exports:
        - ca-ab/ab428_supplemental_tax_credit_line_74
    capabilities: []
    """)

# salary, line 5 (below the 4,800.00 of line 6, so lines 7, 9 and 74 are 0.00 at all three).
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
    for number in (1, 2, 3, 5, 6, 7, 9):
        yield ALBERTA_PARTS / f"worksheet_ab428_line_{number}.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Alberta manifest of a test header, three form declarations and
    the real part files, every other namespace being the Alberta package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_credits_form.yaml").write_text(CREDITS_FORM, encoding="utf-8")
    (folder / "02_worksheet_form.yaml").write_text(WORKSHEET_FORM, encoding="utf-8")
    (folder / "03_ab428_form.yaml").write_text(AB428_FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=4):
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


def _sheets(tmp_path: Path, salary: str) -> dict[str, Worksheet]:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-AB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (ab428,) = worksheets["ca-ab/ab428"]
    (worksheet,) = worksheets["ca-ab/worksheet_ab428"]
    return {"ab428": ab428, "worksheet": worksheet}


@pytest.mark.parametrize(("salary", "line_5"), CASES)
def test_line_74_is_line_9_at_each_salary(tmp_path: Path, salary: str, line_5: str) -> None:
    sheets = _sheets(tmp_path, salary)
    worksheet = sheets["worksheet"]

    # The zero is proved from the real parts, not assumed: line 5 is below line 6's 4,800.00.
    assert worksheet.get(WORKSHEET_AB428_LINE_5).value == D(line_5)
    assert D(line_5) < D("4800.00")
    assert worksheet.get(WORKSHEET_AB428_LINE_7).value == D("0.00")
    assert worksheet.get(WORKSHEET_AB428_SUPPLEMENTAL_CREDIT_LINE_9).value == D("0.00")
    line_74 = sheets["ab428"].get(AB428_SUPPLEMENTAL_TAX_CREDIT_LINE_74).value
    assert line_74 == D("0.00")
    assert str(line_74) == "0.00"
    assert line_74.as_tuple().exponent == -2
    assert not line_74.is_signed()


def test_the_trace_has_a_row_for_line_74(tmp_path: Path) -> None:
    rows = EnglishTraceRenderer().render_all(_sheets(tmp_path, "70000")["ab428"].trace)

    assert rows[-1] == ("Worksheet ab428 supplemental credit line 9 of item 1 (0.00) gives 0.00.")


def _line_74_over(*line_9_amounts: str) -> tuple[Decimal, tuple[str, ...]]:
    """Line 74 over given line 9 records: the capability the part builds, over the real kinds."""
    kinds = alberta_kinds()
    field, line_74 = kinds.kind(LINE_9_FIELD), kinds.kind(KIND)
    assert isinstance(field, AmountKind)
    assert isinstance(line_74, AmountKind)
    records = RecordListKind(LINE_9_LIST, fields=(field,))
    given = Artifact(records, RecordList(records.fields, [{field: D(a)} for a in line_9_amounts]))
    result = RecordTotal(records, line_74).compute((given,))
    (output,) = result.outputs
    value: Decimal = output.value
    return value, EnglishTraceRenderer().render_all(result.trace)


@pytest.mark.parametrize(
    ("line_9", "expected"),
    [("25.00", "25.00"), ("113.00", "113.00"), ("0.00", "0.00"), ("0.01", "0.01")],
)
def test_line_74_is_the_one_line_9_amount_exactly(line_9: str, expected: str) -> None:
    line_74, _ = _line_74_over(line_9)

    assert line_74 == D(expected)
    assert str(line_74) == expected
    assert line_74.as_tuple().exponent == -2


def test_line_74_of_no_line_9_records_is_zero() -> None:
    line_74, rows = _line_74_over()

    assert line_74 == D("0")
    assert rows == ("No items, so 0.00.",)


def test_the_positive_row_reads_in_english() -> None:
    _, rows = _line_74_over("113.00")

    assert rows == ("Worksheet ab428 supplemental credit line 9 of item 1 (113.00) gives 113.00.",)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_record_total_step() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ab/ab428"}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "consumes", "produces"]
    assert step["name"] == "core/record_total"
    assert step["reference"] == "74"
    assert step["unit"] == "ca/cad"
    assert step["consumes"] == {"records": LINE_9_LIST}
    assert step["produces"] == {"output": KIND}


def test_line_74_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = alberta_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert kind is AB428_SUPPLEMENTAL_TAX_CREDIT_LINE_74
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
