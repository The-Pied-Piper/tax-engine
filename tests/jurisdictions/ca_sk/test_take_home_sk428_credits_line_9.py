"""SK428 (2025) line 9, the basic personal amount, as the Saskatchewan take-home manifest part wires
it.

Form text (Form SK428, CRA 5008-c-25e.txt): "Line 9 and line 58040: Basic personal amount Claim
$19,491". The amount is the `ca-sk/basic_personal_amount` dataset, claimed whole through
core/credit_amount, so it is the same at every salary.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them. Saskatchewan is not yet listed in the registrations, so the
service is built here over the Saskatchewan package list of `support.py`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest

import tax_engine.jurisdictions.ca_sk
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_sk.catalog import BASIC_PERSONAL_AMOUNT
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)
from tests.kinds import non_negative

D = Decimal
PART_PATH = (
    Path(tax_engine.jurisdictions.ca_sk.__file__).parent
    / "manifests"
    / "2025"
    / "sk428_credits_line_9.yaml"
)

HEADER = dedent("""\
    jurisdiction: CA-SK
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
      name: ca-sk/sk428_credits
      required: true
      exports:
        - ca-sk/basic_personal_amount
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_sk428_credits_line_9.yaml").write_text(
        PART_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    roots = {**saskatchewan_packages().roots(), Namespace("ca-sk"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, saskatchewan_kinds(), saskatchewan_units()),
        YamlParameterSource(
            saskatchewan_packages().roots(), saskatchewan_parameter_parsers(), saskatchewan_units()
        ),
        saskatchewan_capabilities(),
    )


def line_9(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-SK"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-sk/sk428_credits"]
    return sheet.get(BASIC_PERSONAL_AMOUNT).value


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = saskatchewan_kinds().kind("ca-sk/basic_personal_amount")

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind == BASIC_PERSONAL_AMOUNT


@pytest.mark.parametrize("salary", ["20000", "200000"])
def test_line_9_is_the_basic_personal_amount_at_every_salary(tmp_path: Path, salary: str) -> None:
    assert line_9(tmp_path, salary) == D("19491.00")
