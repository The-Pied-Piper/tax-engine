"""SK428 (2025) line 31, the sum of lines 22 to 30, from the salary alone, real parts.

Form text (Form SK428, CRA 5008-C): "Line 31: Add lines 22 to 30." Line 22 is the CPP or QPP
contributions (line 30800 of the return, Schedule 8 line 25) and line 24 is the EI premiums (line
31200 of the return, T2204 line 16). Lines 23 and 25 to 30 are a block of blank optional lines, zero
for a salary-only filer, so they are not built and line 31 is a core/sum over lines 22 and 24, as
Ontario's line 24 is (`on428_line_24.yaml`). The form prints no label for line 31, so the step has
no title.

The test composes the real Saskatchewan salary part, the real Schedule 8 and T2204 parts and the
three real line parts (`sk428_credits_line_22.yaml`, `sk428_credits_line_24.yaml`,
`sk428_credits_line_31.yaml`), and types in only the salary. The form declaration is made up here,
exporting the lines read, because the real form part exports only the lines already built. The
figures are not a CRA example: they are re-derived below with Decimal from the printed rates, CPP
at 4.95% of the salary above the $3,500 basic exemption to a maximum of $3,356.10, and EI at 1.64%
to the $65,700 maximum insurable earnings, each rounded half-up to the cent.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_sk
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_sk.catalog import SK428_CPP_EI_AND_OTHER_LINE_31
from tests.federal_forms import FEDERAL_FORMS, form_parts
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)
from tests.kinds import non_negative
from tests.manifest_support import T1_LINE_10100_FORM, inputs_without_form

D = Decimal
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
PART = SK_PARTS / "sk428_credits_line_31.yaml"
IDENTIFIER = "ca-sk/sk428_cpp_ei_and_other_line_31"

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-sk/sk428_credits
      required: true
      exports:
        - ca-sk/sk428_cpp_contributions_line_22
        - ca-sk/sk428_ei_premiums_line_24
        - ca-sk/sk428_cpp_ei_and_other_line_31
    capabilities: []
    """)


def _cpp(salary: str) -> Decimal:
    """Line 22 by hand: 4.95% of the salary above the $3,500 basic exemption, at most $3,356.10."""
    above = max(D(salary) - D("3500"), D("0"))
    return min((above * D("0.0495")).quantize(D("0.01"), ROUND_HALF_UP), D("3356.10"))


def _ei(salary: str) -> Decimal:
    """Line 24 by hand: 1.64% of the salary to the $65,700 maximum, at most $1,077.48."""
    return min(D(salary), D("65700")) * D("0.0164")


def _expected(salary: str) -> Decimal:
    return (_cpp(salary) + _ei(salary)).quantize(D("0.01"), ROUND_HALF_UP)


def _part_files() -> Iterator[Path]:
    yield SK_PARTS / "salary.yaml"
    yield from form_parts("schedule_8")
    yield from form_parts("t2204")
    yield T1_LINE_10100_FORM
    yield FEDERAL_FORMS / "t1_employment_income" / "t1_employment_income_line_10100.yaml"
    yield SK_PARTS / "sk428_credits_line_22.yaml"
    yield SK_PARTS / "sk428_credits_line_24.yaml"
    yield PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Saskatchewan manifest of a test header, a form declaration and
    the real part files, every other namespace being the Saskatchewan package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            inputs_without_form(part)
            if part.name.endswith("_inputs.yaml") and part.is_relative_to(FEDERAL_FORMS)
            else part.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    roots = {**saskatchewan_packages().roots(), Namespace("ca-sk"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, saskatchewan_kinds(), saskatchewan_units()),
        YamlParameterSource(
            saskatchewan_packages().roots(),
            saskatchewan_parameter_parsers(),
            saskatchewan_units(),
        ),
        saskatchewan_capabilities(),
    )


def _line_31(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-SK"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-sk/sk428_credits"]
    return sheet.get(SK428_CPP_EI_AND_OTHER_LINE_31).value


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-sk/sk428_credits"}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


# salary, line 31. At $200,000 EI and CPP are both at their maximum.
@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("20000", "1144.75"),
        ("200000", "4433.58"),
    ],
)
def test_line_31_adds_lines_22_and_24(tmp_path: Path, salary: str, expected: str) -> None:
    assert _expected(salary) == D(expected)
    assert _line_31(tmp_path, salary) == D(expected)


def test_the_part_is_one_untitled_sum_step_over_lines_22_and_24() -> None:
    assert _step() == {
        "name": "core/sum",
        "reference": "31",
        "unit": "ca/cad",
        "params": {"rounding": "ca-sk/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-sk/sk428_cpp_contributions_line_22",
                "ca-sk/sk428_ei_premiums_line_24",
            ]
        },
        "produces": {"output": IDENTIFIER},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = saskatchewan_kinds().kind(IDENTIFIER)

    assert kind is SK428_CPP_EI_AND_OTHER_LINE_31
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
