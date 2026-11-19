"""NL428 (2025) line 95, the basic reduction, as the Newfoundland and Labrador take-home
manifest part wires it.

Form text (Form NL428, CRA 5001-c-25e.txt, confirmed 2026-11-18): "Line 95 and line 61870: Basic
reduction Claim $997". The amount is the `ca-nl/low_income_reduction_basic` dataset, claimed whole
through core/credit_amount, so it is the same at every salary.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them. Newfoundland and Labrador is not yet listed in the
registrations, so the service is built here over the Newfoundland and Labrador package list of
`support.py`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest

import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_nl.catalog import LOW_INCOME_REDUCTION_BASIC
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.kinds import non_negative

D = Decimal
PART_PATH = (
    Path(tax_engine.jurisdictions.ca_nl.__file__).parent
    / "manifests"
    / "2025"
    / "nl428_line_95.yaml"
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
    """)
FORM = dedent("""\
    form:
      name: ca-nl/nl428
      required: true
      exports:
        - ca-nl/low_income_reduction_basic
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_nl428_line_95.yaml").write_text(
        PART_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        YamlParameterSource(
            newfoundland_packages().roots(), newfoundland_parameter_parsers(), newfoundland_units()
        ),
        newfoundland_capabilities(),
    )


def line_95(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-NL"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-nl/nl428"]
    return sheet.get(LOW_INCOME_REDUCTION_BASIC).value


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = newfoundland_kinds().kind("ca-nl/low_income_reduction_basic")

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind == LOW_INCOME_REDUCTION_BASIC


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_95_is_the_basic_personal_amount_at_every_salary(tmp_path: Path, salary: str) -> None:
    assert line_95(tmp_path, salary) == D("997.00")
