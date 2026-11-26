"""NB428 (2025) line 26, line 18 plus line 25, from the salary alone, real parts.

Form text (Form NB428, CRA 5004-C, on the ticket, read 26 Nov 2026):
"Line 26: Line 18 plus line 25".
One core/sum over line 18 and line 25, as Saskatchewan's line 32 is. Figures hand-computed
(ticket #1984): the basic personal amount 13,396.00 plus lines 19 and 21.
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
import tax_engine.jurisdictions.ca_nb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_nb.support import (
    new_brunswick_capabilities,
    new_brunswick_kinds,
    new_brunswick_packages,
    new_brunswick_parameter_parsers,
    new_brunswick_units,
)
from tests.kinds import non_negative

D = Decimal
NB_PARTS = Path(tax_engine.jurisdictions.ca_nb.__file__).parent / "manifests" / "2025"
LINE_PART = NB_PARTS / "nb428_credits_line_26.yaml"
IDENTIFIER = "ca-nb/nb428_credits_subtotal_line_26"
FEDERAL_FORM_NAMES = ("schedule_8", "t2204", "t1_employment_income")
NB_PART_NAMES = (
    "nb428_credits_line_9.yaml",
    "nb428_credits_line_18.yaml",
    "nb428_credits_line_19.yaml",
    "nb428_credits_line_21.yaml",
    "nb428_credits_line_25.yaml",
    "nb428_credits_line_26.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-NB
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-nb/nb428_credits
      required: true
      exports:
        - ca-nb/nb428_credits_subtotal_line_26
    capabilities: []
    """)


def _part_files() -> Iterator[Path]:
    for form in FEDERAL_FORM_NAMES:
        yield from form_parts(form)
    for name in NB_PART_NAMES:
        yield NB_PARTS / name


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary New Brunswick manifest of a test header, a form declaration
    and the real part files, every other namespace being the package list's own. The header and
    the form declaration are made up here, because the shared scaffold owns them."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=2):
        text = found.read_text(encoding="utf-8")
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
    roots = {**new_brunswick_packages().roots(), Namespace("ca-nb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, new_brunswick_kinds(), new_brunswick_units()),
        YamlParameterSource(
            new_brunswick_packages().roots(),
            new_brunswick_parameter_parsers(),
            new_brunswick_units(),
        ),
        new_brunswick_capabilities(),
    )


def _value(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-NB"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (sheet,) = worksheets["ca-nb/nb428_credits"]
    return D(sheet.get(new_brunswick_kinds().kind(IDENTIFIER)).value)


CASES = [("20000", "14540.75"), ("30000", "15199.75"), ("70000", "17765.23")]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_26_at_the_salary(tmp_path: Path, salary: str, expected: str) -> None:
    assert _value(tmp_path, salary) == D(expected)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = new_brunswick_kinds().kind(IDENTIFIER)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)


def test_the_part_names_the_form_and_has_the_one_step() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-nb/nb428_credits"}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "reference": "26",
        "unit": "ca/cad",
        "params": {"rounding": "ca-nb/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-nb/nb428_credits_subtotal_line_18",
                "ca-nb/nb428_cpp_ei_and_other_line_25",
            ]
        },
        "produces": {"output": IDENTIFIER},
    }
