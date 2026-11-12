"""AB428 (2025) line 16, the basic personal amount, as the Alberta take-home manifest part wires it.

Form text (Form AB428, CRA 5009-c-25e.txt): "Line 16 and line 58040: Basic personal amount
Claim $22,323". The amount is the `ca-ab/basic_personal_amount` dataset, claimed whole through
core/credit_amount, so it is the same at every salary.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them. Alberta is not yet listed in the registrations, so the
service is built here over the Alberta package list of `support.py`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_ab.support import (
    alberta_capabilities,
    alberta_kinds,
    alberta_packages,
    alberta_parameter_parsers,
    alberta_units,
)
from tests.kinds import non_negative

D = Decimal
KIND = "ca-ab/basic_personal_amount"
PART_PATH = (
    Path(tax_engine.jurisdictions.ca_ab.__file__).parent
    / "manifests"
    / "2025"
    / "ab428_line_16.yaml"
)

HEADER = dedent("""\
    jurisdiction: CA-AB
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
      name: ca-ab/ab428_credits
      required: true
      exports:
        - ca-ab/basic_personal_amount
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_ab428_line_16.yaml").write_text(
        PART_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )


def line_16(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-AB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-ab/ab428_credits"]
    kind = alberta_kinds().kind(KIND)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_16_is_the_basic_personal_amount_at_every_salary(tmp_path: Path, salary: str) -> None:
    assert line_16(tmp_path, salary) == D("22323.00")


def _capability() -> dict[str, Any]:
    part = yaml.safe_load(PART_PATH.read_text(encoding="utf-8"))
    (capability,) = part["capabilities"]
    assert isinstance(capability, dict)
    return capability


def test_the_part_names_the_form() -> None:
    assert yaml.safe_load(PART_PATH.read_text(encoding="utf-8"))["form"]["name"] == (
        "ca-ab/ab428_credits"
    )


def test_the_part_is_a_credit_amount_titled_and_referenced_as_printed() -> None:
    capability = _capability()

    assert capability["name"] == "core/credit_amount"
    assert capability["title"] == "Basic personal amount"
    assert capability["reference"] == "16"
    assert capability["unit"] == "ca/cad"


def test_the_part_takes_the_dataset_and_produces_the_kind() -> None:
    capability = _capability()

    assert capability["params"] == {"amount": KIND}
    assert capability["produces"] == {"output": KIND}


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kinds = alberta_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
