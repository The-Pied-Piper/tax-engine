"""SK428 (2025) line 3, the lower bound of the column for lines 2 to 8, from the salary alone.

Form text (Form SK428, CRA 5008-c, read 2026-11-14,
https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5008-c/5008-c-25e.txt): "Column 1: Line 1
is $53,463 or less / Line 3: 0.00", "Column 2: Line 1 is more than $53,463 but not more than
$152,750 / Line 3: 53,463.00", "Column 3: Line 1 is more than $152,750 / Line 3: 152,750.00". The
form prints one set of three columns and the last has no upper boundary, so line 3 is never blank:
the schedule (`ca-sk/brackets`) has no `up_to`.

Line 3 is one `core/bracket_column_lower_bound` step over line 1 with that schedule, output
`ca-sk/sk428_bracket_lower_bound_line_3`, in the part `sk428_credits_line_3.yaml`. The form does not
name line 3, so the step has no title.

The test composes the T1 employment income form, the real Schedule 8 and T1 taxable income
parts, the real `sk428_credits_line_1.yaml` and the real `sk428_credits_line_3.yaml`, and types in
only the salary. The form declaration is test-local, exporting lines 1 and 3.

Figures (re-derived here with Decimal, not a CRA example): taxable income is the salary less the
enhanced CPP deduction, 9,935.00 / 69,335.00, so line 3 is 0.00 / 53,463.00; the top column
(152,750.00) is checked at salaries 500,000 and 5,000,000. The boundary salary is derived below: the
deduction is 1% of the earnings over $3,500 to the cent below the $71,300 maximum, so taxable income
is 0.99 of the salary plus $35.00 near the first edge.
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
import tax_engine.jurisdictions.ca_sk
import tax_engine.jurisdictions.ca_sk.catalog as sk_catalog
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BracketColumnFigureLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)
from tests.kinds import non_negative

D = Decimal
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
LINE_PART = SK_PARTS / "sk428_credits_line_3.yaml"
FORM_NAME = "ca-sk/sk428_credits"
LINE_1 = "ca-sk/sk428_taxable_income_line_1"
LINE_3 = "ca-sk/sk428_bracket_lower_bound_line_3"
# The real federal parts the T1 taxable-income form needs, beside the salary and line 1.
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
# The SK428 declaration, test-local: lines 1 and 3 are composed, so it exports those.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {LINE_1}
        - {LINE_3}
    capabilities: []
    """)

CASES = [
    ("10000", "9935.00", "0.00"),
    ("70000", "69335.00", "53463.00"),
]
# A salary whose taxable income sits on a column's edge: line 1 is 53,463.00 or less in column 1,
# so 53,463.00 is still column 1. One cent more is the next column.
EDGES = [
    ("53967.68", "53463.00", "0.00"),
]


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield SK_PARTS / "sk428_credits_line_1.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    roots = {**saskatchewan_packages().roots(), Namespace("ca-sk"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, saskatchewan_kinds(), saskatchewan_units()),
        YamlParameterSource(
            saskatchewan_packages().roots(), saskatchewan_parameter_parsers(), saskatchewan_units()
        ),
        saskatchewan_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-SK"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = saskatchewan_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


@pytest.mark.parametrize(("salary", "line_1", "expected"), [*CASES, *EDGES])
def test_line_3_is_the_lower_bound_of_the_column_line_1_falls_in(
    tmp_path: Path, salary: str, line_1: str, expected: str
) -> None:
    value = _sheet(tmp_path, salary).get(_kind(LINE_3)).value

    assert value == D(expected)
    assert str(value) == expected


@pytest.mark.parametrize("salary", ["500000", "5000000"])
def test_line_3_has_no_blank_above_the_top_column(tmp_path: Path, salary: str) -> None:
    artifact = _sheet(tmp_path, salary).get(_kind(LINE_3))

    assert not artifact.is_blank
    assert artifact.value == D("152750.00")


@pytest.mark.parametrize(("salary", "line_1", "expected"), CASES)
def test_the_trace_names_the_bracket_line_1_falls_in(
    tmp_path: Path, salary: str, line_1: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    line = BracketColumnFigureLine(
        output=_kind(LINE_3),
        base=_kind(LINE_1),
        base_amount=D(line_1),
        name="lower bound",
        figure=D(expected),
    )

    assert line in sheet.trace
    assert (
        EnglishTraceRenderer()
        .render(line)
        .endswith(f"falls in the bracket that starts at {D(expected):.2f}.")
    )


def test_the_part_is_one_untitled_bracket_column_lower_bound_step_over_line_1() -> None:
    part: Any = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/bracket_column_lower_bound",
        "reference": "3",
        "unit": "ca/cad",
        "params": {"schedule": "ca-sk/brackets"},
        "consumes": {"base": LINE_1},
        "produces": {"output": LINE_3},
    }


def test_line_3_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = saskatchewan_kinds()

    assert LINE_3 in kinds.identifiers()
    kind = kinds.kind(LINE_3)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is sk_catalog.SK428_BRACKET_LOWER_BOUND_LINE_3
