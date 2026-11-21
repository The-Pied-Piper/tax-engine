"""NL428 (2025) line 16, the basic personal amount, as the Newfoundland and Labrador take-home
manifest part wires it.

Form text (Form NL428, CRA 5001-c-25e.txt): "Line 16 and line 58040: Basic personal amount Claim
$11,067". The amount is the `ca-nl/basic_personal_amount` dataset, claimed whole through
core/credit_amount, so it is the same at every salary.

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

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_nl.catalog import BASIC_PERSONAL_AMOUNT
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.kinds import non_negative
from tests.manifest_support import T1_LINE_10100_FORM, T1_LINE_10100_INPUT, T1_LINE_10100_STEP

D = Decimal
PART_PATH = (
    Path(tax_engine.jurisdictions.ca_nl.__file__).parent
    / "manifests"
    / "2025"
    / "nl428_credits_line_16.yaml"
)

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-nl/nl428_credits
      required: true
      exports:
        - ca-nl/basic_personal_amount
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "00_t1_salary.yaml").write_text(
        T1_LINE_10100_INPUT.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (folder / "00_t1_form.yaml").write_text(
        T1_LINE_10100_FORM.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (folder / "00_t1_line_10100.yaml").write_text(
        T1_LINE_10100_STEP.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_nl428_credits_line_16.yaml").write_text(
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


def line_16(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-NL"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-nl/nl428_credits"]
    return sheet.get(BASIC_PERSONAL_AMOUNT).value


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = newfoundland_kinds().kind("ca-nl/basic_personal_amount")

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind == BASIC_PERSONAL_AMOUNT


@pytest.mark.parametrize("salary", ["20000", "200000"])
def test_line_16_is_the_basic_personal_amount_at_every_salary(tmp_path: Path, salary: str) -> None:
    assert line_16(tmp_path, salary) == D("11067.00")
