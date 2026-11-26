"""NS428 (2025) line 9, the basic personal amount, as the Nova Scotia manifest part wires it.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026): "Line 9 and line 58040: Basic personal
amount Claim $11,744". The amount is the `ca-ns/basic_personal_amount` dataset, claimed whole
through core/credit_amount, so it is the same at every salary.
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
from tax_engine.jurisdictions.ca_ns.catalog import BASIC_PERSONAL_AMOUNT
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
LINE_PART = NS_PARTS / "ns428_line_9.yaml"
IDENTIFIER = "ca-ns/basic_personal_amount"
FEDERAL_FORM_NAMES = ("t1_employment_income",)
NS_PART_NAMES = ("ns428_line_9.yaml",)

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
        - ca-ns/basic_personal_amount
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
def test_line_9_at_the_salary(tmp_path: Path, salary: str, expected: str) -> None:
    assert _value(tmp_path, salary) == D(expected)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(IDENTIFIER)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is BASIC_PERSONAL_AMOUNT
    assert IDENTIFIER in nova_scotia_kinds().identifiers()


def test_the_part_names_the_form_and_has_the_one_step() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ns/ns428"}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/credit_amount",
        "title": "Basic personal amount",
        "reference": "9",
        "unit": "ca/cad",
        "params": {"amount": "ca-ns/basic_personal_amount"},
        "produces": {"output": IDENTIFIER},
    }
