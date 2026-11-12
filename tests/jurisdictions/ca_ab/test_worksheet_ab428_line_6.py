"""Worksheet AB428 (2025) line 6, the base amount, as the Alberta manifest part wires it.

Form text (CRA 5009-d-25e.txt): "Line 6: Base amount 4,800.00". The amount is the
`ca-ab/supplemental_credit_base` dataset, claimed whole through core/credit_amount, so it is the
same at every salary. Line 6 reads nothing.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the end-to-end scaffold owns them.
"""

from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_ab
import tax_engine.jurisdictions.ca_ab.catalog
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import CreditAmountLine
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
LINE_6 = "ca-ab/worksheet_ab428_line_6"
FORM_NAME = "ca-ab/worksheet_ab428"
AB_ROOT = Path(tax_engine.jurisdictions.ca_ab.__file__).parent
PART = AB_ROOT / "manifests" / "2025" / "worksheet_ab428_line_6.yaml"
SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/supplemental_credit_base"

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
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {LINE_6}
    """)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def squashed(text: str) -> str:
    return " ".join(text.split())


def docstring_of(identifier: str) -> str:
    """The string right after the declaration of the kind `identifier` in the Alberta catalog."""
    path = Path(tax_engine.jurisdictions.ca_ab.catalog.__file__)
    body = ast.parse(path.read_text(encoding="utf-8")).body
    for statement, following in zip(body, body[1:], strict=False):
        if not (isinstance(statement, ast.Assign) and isinstance(statement.value, ast.Call)):
            continue
        constants = [each.value for each in statement.value.args if isinstance(each, ast.Constant)]
        if (
            identifier.rpartition("/")[2] in constants
            and isinstance(following, ast.Expr)
            and isinstance(following.value, ast.Constant)
        ):
            return str(following.value.value)
    raise AssertionError(f"no declaration of {identifier!r} followed by a docstring")


def service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Alberta manifest: test header, form and the real line 6 part."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_worksheet_ab428_line_6.yaml").write_text(
        PART.read_text(encoding="utf-8"), encoding="utf-8"
    )
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )


def sheet(tmp_path: Path, salary: str) -> Any:
    worksheets = service(tmp_path).compute(
        JurisdictionCode("CA-AB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (found,) = worksheets[FORM_NAME]
    return found


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_6_is_the_base_amount_at_every_salary(tmp_path: Path, salary: str) -> None:
    kind = alberta_kinds().kind(LINE_6)

    assert sheet(tmp_path, salary).get(kind).value == D("4800.00")


def test_line_6_records_one_credit_amount_line(tmp_path: Path) -> None:
    (line,) = sheet(tmp_path, "70000").trace

    assert isinstance(line, CreditAmountLine)
    assert line.basis == Credit(D("4800"))
    assert line.value == D("4800.00")


def test_the_dataset_is_the_base_amount_rounded_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(D("4800"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_the_dataset_cites_the_worksheet_text() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-d/5009-d-25e.txt",
    )


def test_the_part_names_the_worksheet_form() -> None:
    assert _part()["form"] == {"name": FORM_NAME}


def test_the_part_has_one_credit_amount_capability() -> None:
    (capability,) = _part()["capabilities"]

    assert capability == {
        "name": "core/credit_amount",
        "title": "Base amount",
        "reference": "6",
        "unit": "ca/cad",
        "params": {"amount": FAMILY},
        "produces": {"output": LINE_6},
    }
    assert list(capability) == ["name", "title", "reference", "unit", "params", "produces"]


def test_the_line_6_kind_is_a_non_negative_amount() -> None:
    kind = alberta_kinds().kind(LINE_6)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    with pytest.raises(NegativeArtifactError):
        Artifact(kind, D("-0.01"))


def test_the_line_6_docstring_quotes_the_form_text() -> None:
    doc = squashed(docstring_of(LINE_6))

    assert "Worksheet AB428" in doc
    assert "line 6" in doc
    assert '"Line 6: Base amount 4,800.00"' in doc
