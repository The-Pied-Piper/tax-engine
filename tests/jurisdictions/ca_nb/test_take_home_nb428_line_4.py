"""NB428 (2025) line 4, line 2 minus line 3 (cannot be negative), from the salary alone.

Form text (Form NB428, CRA 5004-c, read 2026-11-26,
https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5004-c/5004-c-25e.txt): each of the four
columns prints "Line 2: Amount from line 1" and "Line 4: Line 2 minus line 3 (cannot be negative)
=". Line 2 is a copy of line 1 (the T1 taxable income) and has no step; line 3 is the printed lower
bound of the column line 1 falls in (0.00, 51,306.00, 102,614.00 or 190,060.00). The form prints no
label for line 4, so the step has no title.

Line 4 is one `core/subtract_not_below_zero` step with `amount` = line 1 and `less` = line 3,
rounded by `ca-nb/cent_rounding`, output `ca-nb/nb428_taxable_income_over_lower_bound_line_4`, in
the part `nb428_line_4.yaml`.

The test composes the T1 employment income form, the real Schedule 8 and T1 taxable income
parts, the real `nb428_line_1.yaml`, `nb428_line_3.yaml` and
`nb428_line_4.yaml`, and types in only the salary. The form declaration is test-local,
exporting lines 1, 3 and 4.

Figures (re-derived here with Decimal, not a CRA example): taxable income is the salary less the
enhanced CPP deduction, 19,835.00 / 69,335.00, line 3 is 0.00 / 51,306.00, so line 4 is 19,835.00 /
18,029.00. The edge salaries are derived as for line 3: at an upper edge line 4 is the column's full
width, one cent over it line 4 restarts at 0.01.
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
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SubtractedNotBelowZeroLine
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
LINE_3_PART = NB_PARTS / "nb428_line_3.yaml"
LINE_4_PART = NB_PARTS / "nb428_line_4.yaml"
FORM_NAME = "ca-nb/nb428"
LINE_1 = "ca-nb/nb428_taxable_income_line_1"
LINE_3 = "ca-nb/nb428_bracket_lower_bound_line_3"
LINE_4 = "ca-nb/nb428_taxable_income_over_lower_bound_line_4"
ROUNDING = "ca-nb/cent_rounding"
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
# The NB428 declaration, test-local: lines 1, 3 and 4 are composed, so it exports those.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {LINE_1}
        - {LINE_3}
        - {LINE_4}
    capabilities: []
    """)

# (salary, line 1, line 3, line 4)
CASES = [
    ("20000", "19835.00", "0.00", "19835.00"),
    ("70000", "69335.00", "51306.00", "18029.00"),
]
# Salaries whose taxable income sits on a column's edge: line 1 at exactly 51,306.00, 102,614.00 or
# 190,060.00 is still the lower column. One cent more is the next column, so line 4 restarts at 0.01. The salary is
# derived below: the deduction is 1% of the earnings over $3,500 to the cent below the $71,300 maximum, so
# taxable income is 0.99 of the salary plus $35.00 near the first edge and the salary less $1,074.00
# (the two additional CPP amounts at their maximum) above $81,200.
EDGES = [
    ("51788.89", "51306.00", "0.00", "51306.00"),
    ("51788.90", "51306.01", "51306.00", "0.01"),
    ("103688", "102614.00", "51306.00", "51308.00"),
    ("103688.01", "102614.01", "102614.00", "0.01"),
    ("191134", "190060.00", "102614.00", "87446.00"),
    ("191135", "190061.00", "190060.00", "1.00"),
]


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield NB_PARTS / "nb428_line_1.yaml"
    yield LINE_3_PART
    yield LINE_4_PART


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


def _rounding() -> Any:
    return YamlParameterSource(
        new_brunswick_packages().roots(), new_brunswick_parameter_parsers(), new_brunswick_units()
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


@pytest.mark.parametrize(("salary", "line_1", "line_3", "expected"), CASES)
def test_line_4_is_line_1_less_line_3_for_the_salary(
    tmp_path: Path, salary: str, line_1: str, line_3: str, expected: str
) -> None:
    value = _sheet(tmp_path, salary).get(_kind(LINE_4)).value

    assert value == D(expected)
    assert str(value) == expected


@pytest.mark.parametrize(("salary", "line_1", "line_3", "expected"), EDGES)
def test_line_4_is_line_1_less_line_3_at_the_column_edges(
    tmp_path: Path, salary: str, line_1: str, line_3: str, expected: str
) -> None:
    value = _sheet(tmp_path, salary).get(_kind(LINE_4)).value

    assert value == D(expected)
    assert str(value) == expected


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 3 is the top column's 190,060.00 and is never blank, so line 4 is not either.
        ("500000", "308866.00"),
        ("5000000", "4808866.00"),
    ],
)
def test_line_4_is_not_blank_above_the_top_column(
    tmp_path: Path, salary: str, expected: str
) -> None:
    artifact = _sheet(tmp_path, salary).get(_kind(LINE_4))

    assert not artifact.is_blank
    assert artifact.value == D(expected)


def test_the_trace_records_the_subtraction_at_70000(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    (line,) = [t for t in sheet.trace if isinstance(t, SubtractedNotBelowZeroLine)]
    assert line == SubtractedNotBelowZeroLine(
        output=_kind(LINE_4),
        minuend=_kind(LINE_1),
        minuend_amount=D("69335.00"),
        subtrahend=_kind(LINE_3),
        subtrahend_amount=D("51306.00"),
        rounding=_rounding().rounding,
        result=D("18029.00"),
    )


def test_the_part_is_one_untitled_subtract_not_below_zero_step_over_lines_1_and_3() -> None:
    part: Any = yaml.safe_load(LINE_4_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert "title" not in step
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "4",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_1, "less": LINE_3},
        "produces": {"output": LINE_4},
    }


def test_line_4_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = new_brunswick_kinds()

    assert LINE_4 in kinds.identifiers()
    kind = kinds.kind(LINE_4)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is nb_catalog.NB428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4
