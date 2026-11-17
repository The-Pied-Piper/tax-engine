"""Worksheet MB428 (2025), section "Line 58040 - Basic personal amount", line 3, the income
threshold, as the Manitoba take-home manifest part wires it.

Form text (CRA 5007-d-25e.txt): "Line 3: Income threshold 200,000.00". The amount is the
`ca-mb/basic_personal_amount_threshold` dataset, claimed whole through core/credit_amount, so it is
the same at every salary.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them. Manitoba is not yet listed in the registrations, so the
service is built here over the Manitoba package list of `support.py`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_mb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)
from tests.kinds import non_negative

D = Decimal
LINE_3 = "ca-mb/worksheet_mb428_basic_personal_amount_line_3"
PART_PATH = (
    Path(tax_engine.jurisdictions.ca_mb.__file__).parent
    / "manifests"
    / "2025"
    / "worksheet_mb428_basic_personal_amount_line_3.yaml"
)

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    """)
FORM = dedent(f"""\
    form:
      name: ca-mb/worksheet_mb428
      required: true
      exports:
        - {LINE_3}
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_worksheet_mb428_basic_personal_amount_line_3.yaml").write_text(
        PART_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )


def line_3(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-MB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-mb/worksheet_mb428"]
    value = sheet.get(manitoba_kinds().kind(LINE_3)).value
    assert isinstance(value, Decimal)
    return value


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART_PATH.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


@pytest.mark.parametrize("salary", ["10000", "20000", "70000", "200000"])
def test_line_3_is_the_income_threshold_at_every_salary(tmp_path: Path, salary: str) -> None:
    assert line_3(tmp_path, salary) == D("200000.00")


def test_the_part_names_the_form_and_has_one_credit_amount_step() -> None:
    part = _part()

    assert part["form"] == {"name": "ca-mb/worksheet_mb428"}
    (step,) = part["capabilities"]
    assert step["name"] == "core/credit_amount"


def test_the_step_prints_the_title_and_reference_of_line_3() -> None:
    (step,) = _part()["capabilities"]

    assert step["title"] == "Income threshold"
    assert step["reference"] == "3"
    assert step["unit"] == "ca/cad"


def test_the_step_reads_the_dataset_and_produces_the_line_3_output() -> None:
    (step,) = _part()["capabilities"]

    assert step["params"] == {"amount": "ca-mb/basic_personal_amount_threshold"}
    assert step["produces"] == {"output": LINE_3}


def test_the_step_keys_are_in_house_order() -> None:
    (step,) = _part()["capabilities"]

    assert list(step) == ["name", "title", "reference", "unit", "params", "produces"]


def test_the_line_3_kind_is_a_registered_non_negative_amount() -> None:
    kind = manitoba_kinds().kind(LINE_3)

    assert kind.identifier == LINE_3
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
