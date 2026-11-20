"""MB428 (2025) line 28, add lines 19 to 27, from the salary alone, real parts.

Form text (Form MB428, Manitoba Tax, CRA 5007-c-25e.txt, line 103, read 2026-11-14): "Line 28: Add
lines 19 to 27. = ^". Lines 20 and 22 (self-employment CPP and EI) and 23 to 27 (volunteer
firefighters, search and rescue, fitness, children's arts, adoption) are optional claims a
salary-only filer does not have, so they are skipped, as Alberta's line 32 skips its equivalents.
Line 28 is one core/sum over the two parts built so far, line 19 (CPP or QPP contributions,
`mb428_credits_line_19.yaml`) and line 21 (employment insurance premiums,
`mb428_credits_line_21.yaml`).

The test composes the real Manitoba salary part, the real Schedule 8 and T2204 parts, the real line
19 and line 21 parts and the new `mb428_credits_line_28.yaml`, and types in only the salary. The
form declaration is made up here, exporting only line 28. The figures are hand-computed from the
printed forms (not a CRA example).
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
import tax_engine.jurisdictions.ca_mb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_mb.catalog import MB428_CPP_EI_AND_OTHER_LINE_28
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)
from tests.kinds import non_negative
from tests.manifest_support import T1_LINE_10100_FORM, inputs_without_form

D = Decimal
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = MB_PARTS / "mb428_credits_line_28.yaml"
IDENTIFIER = "ca-mb/mb428_cpp_ei_and_other_line_28"

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-mb/mb428_credits
      required: true
      exports:
        - ca-mb/mb428_cpp_ei_and_other_line_28
    capabilities: []
    """)

# salary, line 28. At $200,000 both lines 19 and 21 are at their maximums.
CASES = [
    ("10000", "485.75"),
    ("200000", "4433.58"),
]


def _part_files() -> Iterator[Path]:
    yield MB_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    yield from sorted(FEDERAL_FORMS.rglob("t2204*.yaml"))
    yield T1_LINE_10100_FORM
    yield FEDERAL_FORMS / "t1_taxable_income" / "t1_taxable_income_line_10100.yaml"
    yield MB_PARTS / "mb428_credits_line_19.yaml"
    yield MB_PARTS / "mb428_credits_line_21.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, a form declaration and the
    real part files, every other namespace being the Manitoba package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=2):
        text = (
            inputs_without_form(found)
            if found.name.endswith("_inputs.yaml") and found.is_relative_to(FEDERAL_FORMS)
            else found.read_text(encoding="utf-8")
        )
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(),
            manitoba_parameter_parsers(),
            manitoba_units(),
        ),
        manitoba_capabilities(),
    )


def _line_28(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-MB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-mb/mb428_credits"]
    return sheet.get(MB428_CPP_EI_AND_OTHER_LINE_28).value


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_28_adds_lines_19_and_21(tmp_path: Path, salary: str, expected: str) -> None:
    assert _line_28(tmp_path, salary) == D(expected)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_sum_step_like_alberta_line_32() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-mb/mb428_credits"}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "28",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-mb/mb428_cpp_contributions_line_19",
                "ca-mb/mb428_ei_premiums_line_21",
            ]
        },
        "produces": {"output": IDENTIFIER},
    }


def test_line_28_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = manitoba_kinds().kind(IDENTIFIER)

    assert kind is MB428_CPP_EI_AND_OTHER_LINE_28
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
