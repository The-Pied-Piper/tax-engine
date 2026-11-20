"""NL428 (2025) line 53, line 48 minus line 52 (not below 0), from the salary, real parts.

Form text (Form NL428, CRA 5001-C, confirmed 2026-11-18): "Line 53: Line 48 minus line 52 (if
negative, enter "0") =". Line 53 is one core/subtract_not_below_zero step over line 48, the optional
medical expenses input (`nl428_credits_line_48_input.yaml`), and line 52
(`nl428_credits_line_52.yaml`), rounded half-up to the cent. A request that leaves line 48 blank
has no medical expenses, so the blank is read as 0 and line 53 is 0.00. The form prints no label for
the line, so the step has no title.

The test composes the real Schedule 8 parts, the real T1 taxable income parts and the real lines 48,
49, 51, 52 and 53 parts, and types in the salary and, where a case gives one, line 48. The header,
the salary input and the form declaration are made up here, the form exporting line 53.

The hand figures are asserted (not a CRA example): net income is the salary less the enhanced CPP
deduction, line 51 is 3% of it half-up to the cent, line 52 is the lesser of that and 2,410.00, and
line 53 is line 48 less line 52, not below 0.
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
import tax_engine.jurisdictions.ca_nl
import tax_engine.jurisdictions.ca_nl.catalog as nl_catalog
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
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_49_PART = NL_PARTS / "nl428_credits_line_49.yaml"
LINE_51_PART = NL_PARTS / "nl428_credits_line_51.yaml"
LINE_52_PART = NL_PARTS / "nl428_credits_line_52.yaml"
LINE_48_PART = NL_PARTS / "nl428_credits_line_48_input.yaml"
LINE_PART = NL_PARTS / "nl428_credits_line_53.yaml"
FORM_NAME = "ca-nl/nl428_credits"
LINE_52 = "ca-nl/nl428_medical_expenses_limited_amount_line_52"
LINE_48 = "ca-nl/nl428_medical_expenses_line_48"
KIND = "ca-nl/nl428_medical_expenses_over_limit_line_53"
# The real federal parts the T1 taxable-income form needs, beside the salary and lines 49 to 52.
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
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-nl/nl428_credits
      required: true
      exports:
        - ca-nl/nl428_medical_expenses_over_limit_line_53
    capabilities: []
    """)

# salary, line 51 (3% of net income), line 52 (the lesser of line 51 and 2,410.00). Net income is
# 9,935.00 / 19,835.00 / 69,335.00 / 198,926.00.
# salary, line 48, line 52, line 53. Net income is 9,935.00 / 19,835.00 / 69,335.00 / 198,926.00;
# line 52 is the lesser of 3% of it and 2,410.00.
CASES = [
    ("20000", None, "595.05", "0.00"),
    ("20000", "3000", "595.05", "2404.95"),
    ("70000", "2000", "2080.05", "0.00"),
    ("200000", "5000", "2410.00", "2590.00"),
]


def _part_files() -> Iterator[Path]:
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield LINE_49_PART
    yield LINE_51_PART
    yield LINE_52_PART
    yield LINE_48_PART
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
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        YamlParameterSource(
            newfoundland_packages().roots(), newfoundland_parameter_parsers(), newfoundland_units()
        ),
        newfoundland_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, line_48: str | None = None) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_48 is not None:
        given.append(Artifact(nl_catalog.NL428_MEDICAL_EXPENSES_LINE_48, D(line_48)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(newfoundland_kinds().kind(identifier)).value)


@pytest.mark.parametrize(("salary", "line_48", "line_52", "expected"), CASES)
def test_line_53_is_line_48_less_line_52_not_below_zero(
    tmp_path: Path, salary: str, line_48: str | None, line_52: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, line_48)

    assert _value(sheet, LINE_52) == D(line_52)
    assert _value(sheet, KIND) == D(expected)


def test_a_blank_line_48_is_read_as_zero_and_prints_its_own_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    assert any("left blank, taken as" in row.lower() for row in rows)


def test_a_given_line_48_prints_no_left_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", "3000")

    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    assert any("2080.05" in row and "3000.00" in row for row in rows)
    assert not any("left blank, taken as" in row.lower() for row in rows)


def _step() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def test_the_part_is_one_untitled_subtract_not_below_zero_step() -> None:
    assert _step() == {
        "name": "core/subtract_not_below_zero",
        "reference": "53",
        "unit": "ca/cad",
        "params": {"rounding": "ca-nl/cent_rounding"},
        "consumes": {"amount": LINE_48, "less": LINE_52},
        "blank": {"amount": "0"},
        "produces": {"output": KIND},
    }


def test_line_53_is_a_registered_non_negative_amount_kind() -> None:
    kinds = newfoundland_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is nl_catalog.NL428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_53
