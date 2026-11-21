"""SK428 (2025) line 4, line 2 minus line 3 (cannot be negative), from the salary alone.

Form text (Form SK428, CRA 5008-c, read 2026-11-14,
https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5008-c/5008-c-25e.txt): each of the three
columns prints "Line 2: Amount from line 1" and "Line 4: Line 2 minus line 3 (cannot be negative)
=". Line 2 is a copy of line 1 (the T1 taxable income) and has no step; line 3 is the printed lower
bound of the column line 1 falls in (0.00, 53,463.00 or 152,750.00). The form prints no label for
line 4, so the step has no title.

Line 4 is one `core/subtract_not_below_zero` step with `amount` = line 1 and `less` = line 3,
rounded by `ca-sk/cent_rounding`, output `ca-sk/sk428_taxable_income_over_lower_bound_line_4`, in
the part `sk428_credits_line_4.yaml`.

The test composes the real Saskatchewan salary part, the real Schedule 8 and T1 taxable income
parts, the real `sk428_credits_line_1.yaml`, `sk428_credits_line_3.yaml` and
`sk428_credits_line_4.yaml`, and types in only the salary. The form declaration is test-local,
exporting lines 1, 3 and 4.

Figures (re-derived here with Decimal, not a CRA example): taxable income is the salary less the
enhanced CPP deduction, 9,935.00 / 69,335.00, line 3 is 0.00 / 53,463.00, so line 4 is 9,935.00 /
15,872.00. The boundary salary is derived as for line 3: one cent over the first column's upper
edge.
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
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SubtractedNotBelowZeroLine
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
from tests.manifest_support import T1_LINE_10100_INPUT

D = Decimal
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_3_PART = SK_PARTS / "sk428_credits_line_3.yaml"
LINE_4_PART = SK_PARTS / "sk428_credits_line_4.yaml"
FORM_NAME = "ca-sk/sk428_credits"
LINE_1 = "ca-sk/sk428_taxable_income_line_1"
LINE_3 = "ca-sk/sk428_bracket_lower_bound_line_3"
LINE_4 = "ca-sk/sk428_taxable_income_over_lower_bound_line_4"
ROUNDING = "ca-sk/cent_rounding"
# The real federal parts the T1 taxable-income form needs, beside the salary and line 1.
T1_PARTS = (
    "t1_taxable_income_inputs.yaml",
    "t1_employment_income.yaml",
    "t1_employment_income_line_10100.yaml",
    "t1_employment_income_line_10400.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_employment_income_line_10400_inputs.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The SK428 declaration, test-local: lines 1, 3 and 4 are composed, so it exports those.
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
    ("10000", "9935.00", "0.00", "9935.00"),
    ("70000", "69335.00", "53463.00", "15872.00"),
]
# Salaries whose taxable income sits on a column's edge: line 1 is 53,463.00 or less in column 1,
# not more than 152,750.00 in column 2. One cent more is the next column, so line 4 restarts at
# 0.01.
EDGES = [
    ("53967.69", "53463.01", "53463.00", "0.01"),
]


def _part_files() -> Iterator[Path]:
    yield T1_LINE_10100_INPUT
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield SK_PARTS / "sk428_credits_line_1.yaml"
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


def _rounding() -> Any:
    return YamlParameterSource(
        saskatchewan_packages().roots(), saskatchewan_parameter_parsers(), saskatchewan_units()
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
        # Line 3 is the top column's 152,750.00 and is never blank, so line 4 is not either.
        ("200000", "46176.00"),
        ("500000", "346176.00"),
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
        subtrahend_amount=D("53463.00"),
        rounding=_rounding().rounding,
        result=D("15872.00"),
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
    kinds = saskatchewan_kinds()

    assert LINE_4 in kinds.identifiers()
    kind = kinds.kind(LINE_4)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is sk_catalog.SK428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4
