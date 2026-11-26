"""NB428 (2025) line 5, the rate of the column for lines 2 to 8, from the salary alone.

Form text (Form NB428, CRA 5004-c, read 2026-11-26,
https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5004-c/5004-c-25e.txt): "Line 5: Rate
9.4%" (column 1, line 1 is $51,306 or less), "Line 5: 14%" (column 2, more than $51,306 but not
more than $102,614), "Line 5: 16%" (column 3, more than $102,614 but not more than $190,060) and
"Line 5: 19.5%" (column 4, more than $190,060). The form prints one set of four columns and the
last has no upper boundary, so line 5 is never blank: the schedule (`ca-nb/brackets`) has no
`up_to`.

Line 5 is one `core/bracket_column_rate` step over line 1 with that schedule, output
`ca-nb/nb428_bracket_rate_line_5`, in the part `nb428_line_5.yaml`. The rate is a Decimal
held as printed, not rounded, and is not money, so the step has no unit. Titled "Rate" as the form
prints it.

The test composes the T1 employment income form, the real Schedule 8 and T1 taxable income
parts, the real `nb428_line_1.yaml` and the real `nb428_line_5.yaml`, and types in
only the salary. The form declaration is test-local, exporting lines 1 and 5.

Figures (re-derived here with Decimal, not a CRA example): taxable income is the salary less the
enhanced CPP deduction, 19,835.00 / 69,335.00, so line 5 is 9.4% / 14%; the top column (19.5%) is
checked at salaries 500,000 and 5,000,000. The edge salaries are derived below.
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
import tax_engine.jurisdictions.ca_nb
import tax_engine.jurisdictions.ca_nb.catalog as nb_catalog
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BracketColumnFigureLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_nb.support import (
    new_brunswick_capabilities,
    new_brunswick_kinds,
    new_brunswick_packages,
    new_brunswick_parameter_parsers,
    new_brunswick_units,
)
from tests.kinds import non_negative

D = Decimal
NB_PARTS = Path(tax_engine.jurisdictions.ca_nb.__file__).parent / "manifests" / "2025"
LINE_PART = NB_PARTS / "nb428_line_5.yaml"
FORM_NAME = "ca-nb/nb428"
LINE_1 = "ca-nb/nb428_taxable_income_line_1"
LINE_5 = "ca-nb/nb428_bracket_rate_line_5"
# The real federal parts the T1 taxable-income form needs, beside the salary and line 1.
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)

HEADER = dedent("""\
    jurisdiction: CA-NB
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
# The NB428 declaration, test-local: lines 1 and 5 are composed, so it exports those.
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
    ("20000", "19835.00", "0.094"),
    ("70000", "69335.00", "0.14"),
]
# Salaries whose taxable income sits on a column's edge: line 1 at exactly 51,306.00, 102,614.00 or
# 190,060.00 is still the lower column. One cent more is the next column. The salary is derived
# below: the deduction is 1% of the earnings over $3,500 to the cent below the $71,300 maximum, so
# taxable income is 0.99 of the salary plus $35.00 near the first edge and the salary less $1,074.00
# (the two additional CPP amounts at their maximum) above $81,200.
EDGES = [
    ("51788.89", "51306.00", "0.094"),
    ("51788.90", "51306.01", "0.14"),
    ("103688", "102614.00", "0.14"),
    ("103688.01", "102614.01", "0.16"),
    ("191134", "190060.00", "0.16"),
    ("191135", "190061.00", "0.195"),
]
# The percentage the trace prints for each rate.
PERCENT = {"0.094": "9.4", "0.14": "14", "0.16": "16", "0.195": "19.5"}


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield NB_PARTS / "nb428_line_1.yaml"
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
    roots = {**new_brunswick_packages().roots(), Namespace("ca-nb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, new_brunswick_kinds(), new_brunswick_units()),
        YamlParameterSource(
            new_brunswick_packages().roots(),
            new_brunswick_parameter_parsers(),
            new_brunswick_units(),
        ),
        new_brunswick_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-NB"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = new_brunswick_kinds().kind(identifier)
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
    assert artifact.value == D("0.195")


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
        "params": {"schedule": "ca-nb/brackets"},
        "consumes": {"base": LINE_1},
        "produces": {"output": LINE_5},
    }


def test_line_5_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = new_brunswick_kinds()

    assert LINE_5 in kinds.identifiers()
    kind = kinds.kind(LINE_5)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is nb_catalog.NB428_BRACKET_RATE_LINE_5
