"""SK428 (2025) line 5, the rate of the column for lines 2 to 8, from the salary alone.

Form text (Form SK428, CRA 5008-c, read 2026-11-14,
https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5008-c/5008-c-25e.txt): "Line 5: Rata
10.5%" (column 1, line 1 is $53,463 or less), "Line 5: Rata 12.5%" (column 2, line 1 is more than
$53,463 but not more than $152,750) and "Line 5: Rata 14.5%" (column 3, line 1 is more than
$152,750); the text file prints "Rata" for "Rate", a transcription typo that leaves the figures
alone. The form prints one set of three columns and the last has no upper boundary, so line 5 is
never blank: the schedule (`ca-sk/brackets`) has no `up_to`.

Line 5 is one `core/bracket_column_rate` step over line 1 with that schedule, output
`ca-sk/sk428_bracket_rate_line_5`, in the part `sk428_credits_line_5.yaml`. The rate is a Decimal
held as printed, not rounded, and is not money, so the step has no unit. Titled "Rate" as the form
prints it.

The test composes the real Saskatchewan salary part, the real Schedule 8 and T1 taxable income
parts, the real `sk428_credits_line_1.yaml` and the real `sk428_credits_line_5.yaml`, and types in
only the salary. The form declaration is test-local, exporting lines 1 and 5.

Figures (re-derived here with Decimal, not a CRA example): taxable income is the salary less the
enhanced CPP deduction, 9,935.00 / 69,335.00, so line 5 is 10.5% / 12.5%; the top column (14.5%) is
checked at salaries 500,000 and 5,000,000. The boundary salary is derived below: the deduction is 1%
of the earnings over $3,500 to the cent below the $71,300 maximum, so taxable income is 0.99 of the
salary plus $35.00 near the first edge.
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
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = SK_PARTS / "sk428_credits_line_5.yaml"
FORM_NAME = "ca-sk/sk428_credits"
LINE_1 = "ca-sk/sk428_taxable_income_line_1"
LINE_5 = "ca-sk/sk428_bracket_rate_line_5"
# The real federal parts the T1 taxable-income form needs, beside the salary and line 1.
T1_PARTS = (
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
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The SK428 declaration, test-local: lines 1 and 5 are composed, so it exports those.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {LINE_1}
        - {LINE_5}
    capabilities: []
    """)

CASES = [
    ("10000", "9935.00", "0.105"),
    ("70000", "69335.00", "0.125"),
]
# A salary whose taxable income sits on a column's edge: line 1 is 53,463.00 or less in column 1,
# so 53,463.00 is still column 1. One cent more is the next column.
EDGES = [
    ("53967.68", "53463.00", "0.105"),
]
# The percentage the trace prints for each rate.
PERCENT = {"0.105": "10.5", "0.125": "12.5", "0.145": "14.5"}


def _part_files() -> Iterator[Path]:
    yield SK_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
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
            inputs_without_form(part)
            if part.name.endswith("_inputs.yaml") and part.is_relative_to(FEDERAL_FORMS)
            else part.read_text(encoding="utf-8"),
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
def test_line_5_is_the_rate_of_the_column_line_1_falls_in(
    tmp_path: Path, salary: str, line_1: str, expected: str
) -> None:
    value = _sheet(tmp_path, salary).get(_kind(LINE_5)).value

    assert value == D(expected)
    assert isinstance(value, Decimal)


@pytest.mark.parametrize("salary", ["500000", "5000000"])
def test_line_5_has_no_blank_above_the_top_column(tmp_path: Path, salary: str) -> None:
    artifact = _sheet(tmp_path, salary).get(_kind(LINE_5))

    assert not artifact.is_blank
    assert artifact.value == D("0.145")


@pytest.mark.parametrize(("salary", "line_1", "expected"), CASES)
def test_the_trace_names_the_rate_of_the_bracket_line_1_falls_in(
    tmp_path: Path, salary: str, line_1: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    line = BracketColumnFigureLine(
        output=_kind(LINE_5),
        base=_kind(LINE_1),
        base_amount=D(line_1),
        name="rate",
        figure=D(expected),
    )

    assert line in sheet.trace
    assert (
        EnglishTraceRenderer()
        .render(line)
        .endswith(f"falls in a bracket with the rate {PERCENT[expected]}%.")
    )


def test_the_part_is_one_titled_bracket_column_rate_step_over_line_1() -> None:
    part: Any = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "title", "reference", "params", "consumes", "produces"]
    assert step == {
        "name": "core/bracket_column_rate",
        "title": "Rate",
        "reference": "5",
        "params": {"schedule": "ca-sk/brackets"},
        "consumes": {"base": LINE_1},
        "produces": {"output": LINE_5},
    }


def test_line_5_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = saskatchewan_kinds()

    assert LINE_5 in kinds.identifiers()
    kind = kinds.kind(LINE_5)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is sk_catalog.SK428_BRACKET_RATE_LINE_5
