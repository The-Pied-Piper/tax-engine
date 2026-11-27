"""NS428 (2025) line 19, add lines 9 to 18, from the salary alone, real parts.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF; its text version matches
on these lines): "Add lines 9 to 18." Lines 10 to 18 are blank claims outside the salary-only
scope and are not built, so the sum has one part, line 9 (a sum with one part, as Saskatchewan's
line 20 and Newfoundland and Labrador's line 25 are).
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
import tax_engine.jurisdictions.ca_ns
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ns.catalog import NS428_CREDITS_SUBTOTAL_LINE_19
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_ns.support import (
    nova_scotia_capabilities,
    nova_scotia_kinds,
    nova_scotia_packages,
    nova_scotia_parameter_parsers,
    nova_scotia_units,
)
from tests.kinds import non_negative

D = Decimal
NS_PARTS = Path(tax_engine.jurisdictions.ca_ns.__file__).parent / "manifests" / "2025"
LINE_PART = NS_PARTS / "ns428_line_19.yaml"
IDENTIFIER = "ca-ns/ns428_credits_subtotal_line_19"
FEDERAL_FORM_NAMES = (
    "schedule_8",
    "t2204",
    "t1_employment_income",
    "t1_taxable_income",
    "t1_lines_copied_by_provinces",
    "schedule_9",
)
NS_PART_NAMES = (
    "ns428_line_9.yaml",
    "ns428_line_10_input.yaml",
    "ns428_line_10_worksheet_lines_1_to_3.yaml",
    "ns428_line_10_worksheet_lines_4_to_7.yaml",
    "ns428_line_10.yaml",
    "ns428_line_19.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-NS
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-ns/ns428
      required: true
      exports:
        - ca-ns/ns428_credits_subtotal_line_19
    capabilities: []
    """)


def _part_files() -> Iterator[Path]:
    for form in FEDERAL_FORM_NAMES:
        yield from form_parts(form)
    for name in NS_PART_NAMES:
        yield NS_PARTS / name


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Nova Scotia manifest of a test header, a form declaration
    and the real part files, every other namespace being the package list's own. The header and
    the form declaration are made up here, because the shared scaffold owns them."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=2):
        text = found.read_text(encoding="utf-8")
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
    roots = {**nova_scotia_packages().roots(), Namespace("ca-ns"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, nova_scotia_kinds(), nova_scotia_units()),
        YamlParameterSource(
            nova_scotia_packages().roots(),
            nova_scotia_parameter_parsers(),
            nova_scotia_units(),
        ),
        nova_scotia_capabilities(),
    )


def _value(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-NS"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (sheet,) = worksheets["ca-ns/ns428"]
    return D(sheet.get(nova_scotia_kinds().kind(IDENTIFIER)).value)


CASES = [("20000", "11744.00"), ("200000", "11744.00")]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_19_at_the_salary(tmp_path: Path, salary: str, expected: str) -> None:
    assert _value(tmp_path, salary) == D(expected)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(IDENTIFIER)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is NS428_CREDITS_SUBTOTAL_LINE_19
    assert IDENTIFIER in nova_scotia_kinds().identifiers()


def test_the_part_names_the_form_and_has_the_one_step() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ns/ns428"}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "reference": "19",
        "unit": "ca/cad",
        "params": {"rounding": "ca-ns/cent_rounding"},
        "consumes": {"parts": ["ca-ns/basic_personal_amount", "ca-ns/ns428_age_amount_line_10"]},
        "produces": {"output": IDENTIFIER},
    }
