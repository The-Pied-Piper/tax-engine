"""SK428 (2025) line 32, line 21 plus line 31, from the salary alone, real parts.

Form text (Form SK428, CRA 5008-C): "Line 21: Amount from line 20 of the previous page" and
"Line 32: Line 21 plus line 31 =". Line 21 is a copy of line 20, so it has no step; line 32 is a
core/sum over line 20 (the credits subtotal, here the basic personal amount alone) and line 31
(CPP or QPP, EI and the other lines), as Ontario's line 25 is. The form prints no label for line
32, so the step has no title.

The test composes the T1 employment income form, the real Schedule 8 and T2204 parts and the
real line parts (`sk428_credits_line_9.yaml`, `_line_20.yaml`, `_line_22.yaml`, `_line_24.yaml`,
`_line_31.yaml`, `_line_32.yaml`), and types in only the salary. The form declaration is made up
here, exporting the lines read, because the real form part exports only the lines already built.
The figures are not a CRA example: they are re-derived below with Decimal from the printed basic
personal amount dataset (19,491), CPP at 4.95% of the salary above the $3,500 basic exemption to a
maximum of $3,356.10, and EI at 1.64% to the $65,700 maximum insurable earnings, each rounded
half-up to the cent.
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
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_sk.catalog import SK428_CREDITS_SUBTOTAL_LINE_32
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)
from tests.kinds import non_negative

D = Decimal
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
PART = SK_PARTS / "sk428_credits_line_32.yaml"
IDENTIFIER = "ca-sk/sk428_credits_subtotal_line_32"
BASIC_PERSONAL_AMOUNT = D("19491")

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-sk/sk428_credits
      required: true
      exports:
        - ca-sk/basic_personal_amount
        - ca-sk/sk428_credits_subtotal_line_20
        - ca-sk/sk428_cpp_contributions_line_22
        - ca-sk/sk428_ei_premiums_line_24
        - ca-sk/sk428_cpp_ei_and_other_line_31
        - ca-sk/sk428_credits_subtotal_line_32
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
    line_31 = (_cpp(salary) + _ei(salary)).quantize(D("0.01"), ROUND_HALF_UP)
    return BASIC_PERSONAL_AMOUNT.quantize(D("0.01")) + line_31


def _part_files() -> Iterator[Path]:
    yield from form_parts("t1_employment_income")
    yield from form_parts("t1_taxable_income")
    yield from form_parts("t1_lines_copied_by_provinces")
    yield from form_parts("schedule_8")
    yield from form_parts("t2204")
    yield SK_PARTS / "sk428_credits_line_9.yaml"
    yield SK_PARTS / "sk428_credits_line_10_worksheet_lines_1_to_3.yaml"
    yield SK_PARTS / "sk428_credits_line_10_worksheet_lines_4_to_7.yaml"
    yield SK_PARTS / "sk428_credits_line_10.yaml"
    yield SK_PARTS / "sk428_credits_line_19.yaml"
    yield SK_PARTS / "sk428_credits_line_20.yaml"
    yield SK_PARTS / "sk428_credits_line_22.yaml"
    yield SK_PARTS / "sk428_credits_line_24.yaml"
    yield SK_PARTS / "sk428_credits_line_31.yaml"
    yield PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Saskatchewan manifest of a test header, a form declaration and
    the real part files, every other namespace being the Saskatchewan package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(dict.fromkeys(_part_files()), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"),
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


def _line_32(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-SK"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (sheet,) = worksheets["ca-sk/sk428_credits"]
    return sheet.get(SK428_CREDITS_SUBTOTAL_LINE_32).value


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-sk/sk428_credits"}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


# salary, line 32. At $200,000 EI and CPP are both at their maximum.
@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("20000", "20635.75"),
        ("200000", "23924.58"),
    ],
)
def test_line_32_adds_line_21_and_line_31(tmp_path: Path, salary: str, expected: str) -> None:
    assert _expected(salary) == D(expected)
    assert _line_32(tmp_path, salary) == D(expected)


def test_the_part_is_one_untitled_sum_step_over_lines_20_and_31() -> None:
    assert _step() == {
        "name": "core/sum",
        "reference": "32",
        "unit": "ca/cad",
        "params": {"rounding": "ca-sk/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-sk/sk428_credits_subtotal_line_20",
                "ca-sk/sk428_cpp_ei_and_other_line_31",
            ]
        },
        "produces": {"output": IDENTIFIER},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = saskatchewan_kinds().kind(IDENTIFIER)

    assert kind is SK428_CREDITS_SUBTOTAL_LINE_32
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
