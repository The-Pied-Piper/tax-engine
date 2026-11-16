"""BC479 (2025) line 7, the threshold, as the British Columbia take-home manifest part wires it.

Form text (Form BC479, CRA 5010-TC, read 2026-11-14): "Line 7: If you had a spouse or common-law
partner on December 31, 2025, enter $18,000. If not, enter $15,000." The $15,000 branch applies: a
single filer. The $18,000 branch is not built. The amount is the `ca-bc/sales_tax_credit_threshold`
dataset, claimed whole through core/credit_amount, so it is the same at every salary.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them. The service is built here over the British Columbia package
list of `support.py`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import BC479_THRESHOLD_LINE_7
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative

D = Decimal
PART_PATH = (
    Path(tax_engine.jurisdictions.ca_bc.__file__).parent
    / "manifests"
    / "2025"
    / "bc479_line_7.yaml"
)
KIND = "ca-bc/bc479_threshold_line_7"

HEADER = dedent("""\
    jurisdiction: CA-BC
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
      name: ca-bc/bc479
      required: true
      exports:
        - ca-bc/bc479_threshold_line_7
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_bc479_line_7.yaml").write_text(
        PART_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    roots = {**british_columbia_packages().roots(), Namespace("ca-bc"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, british_columbia_kinds(), british_columbia_units()),
        YamlParameterSource(
            british_columbia_packages().roots(),
            british_columbia_parameter_parsers(),
            british_columbia_units(),
        ),
        british_columbia_capabilities(),
    )


def line_7(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-BC"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-bc/bc479"]
    return sheet.get(BC479_THRESHOLD_LINE_7).value


@pytest.mark.parametrize("salary", ["17000", "20000", "30000", "70000", "200000"])
def test_line_7_is_the_threshold_at_every_salary(tmp_path: Path, salary: str) -> None:
    assert line_7(tmp_path, salary) == D("15000.00")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART_PATH.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_credit_amount_step() -> None:
    assert _part() == {
        "form": {"name": "ca-bc/bc479"},
        "capabilities": [
            {
                "name": "core/credit_amount",
                "reference": "7",
                "unit": "ca/cad",
                "params": {"amount": "ca-bc/sales_tax_credit_threshold"},
                "produces": {"output": KIND},
            }
        ],
    }


def test_line_7_is_a_registered_non_negative_amount_kind() -> None:
    kind = british_columbia_kinds().kind(KIND)

    assert kind is BC479_THRESHOLD_LINE_7
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
