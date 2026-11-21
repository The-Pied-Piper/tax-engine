"""SK428 (2025) line 51, line 42 plus line 50, from the salary alone, real parts.

Form text (Form SK428, CRA 5008-c): "Line 51 and line 58800: Line 42 plus line 50 = ^". Lines 43 to
49, the medical expense working, are not built; line 50, "Line 50 and line 58769: Line 48 plus
line 49", is an optional input, blank for a salary-only filer. Line 51 is one core/sum over line 42
and the line 50 input, as Alberta line 52 is over line 43 and line 51; the blank line 50 is read
as 0 and the step prints its own "Left blank, taken as 0" row. The form prints no label for line
51, so the step has no title.

The test composes the real Saskatchewan salary part, the real Schedule 8 and T2204 parts, the real
line parts (`sk428_credits_line_9.yaml`, `_line_20.yaml`, `_line_22.yaml`, `_line_24.yaml`,
`_line_31.yaml`, `_line_32.yaml`, `_line_33.yaml`, `_line_35.yaml`, `_line_38.yaml`,
`_line_42.yaml`), the real `sk428_line_33_inputs.yaml`, the real
`sk428_credits_line_50_input.yaml` and the new `sk428_credits_line_51.yaml`, and
types in only the salary (and, in one test, line 50). The form
declaration is made up here, exporting only line 51. The figures are not a CRA example: they are
re-derived below with Decimal from the printed basic personal amount dataset (19,491), CPP at 4.95%
of the salary above the $3,500 basic exemption to a maximum of $3,356.10, and EI at 1.64% to the
$65,700 maximum insurable earnings, each rounded half-up to the cent. Line 42 is 20,635.75
and 23,924.58 at the two salaries, plus line 50 of 0 when blank.
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
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_sk.catalog import (
    SK428_CREDITS_TOTAL_LINE_51,
    SK428_MEDICAL_EXPENSES_LINE_50,
)
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)
from tests.kinds import non_negative
from tests.manifest_support import T1_LINE_10100_FORM, T1_LINE_10100_INPUT

D = Decimal
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
PART = SK_PARTS / "sk428_credits_line_51.yaml"
IDENTIFIER = "ca-sk/sk428_credits_total_line_51"
BASIC_PERSONAL_AMOUNT = D("19491")

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
        - ca-sk/sk428_credits_total_line_51
    capabilities: []
    """)

# salary, line 51: line 42 (20,635.75 and 23,924.58, re-derived by hand below) plus
# line 50, blank and read as 0; lines 43 to 49 are not built.
CASES = [("20000", "20635.75"), ("200000", "23924.58")]


def _cpp(salary: str) -> Decimal:
    """Line 22 by hand: 4.95% of the salary above the $3,500 basic exemption, at most $3,356.10."""
    above = max(D(salary) - D("3500"), D("0"))
    return min((above * D("0.0495")).quantize(D("0.01"), ROUND_HALF_UP), D("3356.10"))


def _ei(salary: str) -> Decimal:
    """Line 24 by hand: 1.64% of the salary to the $65,700 maximum, at most $1,077.48."""
    return min(D(salary), D("65700")) * D("0.0164")


def _expected(salary: str, medical: str = "0") -> Decimal:
    """Line 51 by hand: line 42 (equal to line 32 here) plus line 50."""
    line_31 = (_cpp(salary) + _ei(salary)).quantize(D("0.01"), ROUND_HALF_UP)
    line_32 = BASIC_PERSONAL_AMOUNT.quantize(D("0.01")) + line_31
    return line_32 + D(medical)


def _part_files() -> Iterator[Path]:
    yield T1_LINE_10100_INPUT
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    yield from sorted(FEDERAL_FORMS.rglob("t2204*.yaml"))
    yield T1_LINE_10100_FORM
    yield FEDERAL_FORMS / "t1_employment_income" / "t1_employment_income_line_10100.yaml"
    yield SK_PARTS / "sk428_credits_line_9.yaml"
    yield SK_PARTS / "sk428_credits_line_20.yaml"
    yield SK_PARTS / "sk428_credits_line_22.yaml"
    yield SK_PARTS / "sk428_credits_line_24.yaml"
    yield SK_PARTS / "sk428_line_33_inputs.yaml"
    yield SK_PARTS / "sk428_credits_line_31.yaml"
    yield SK_PARTS / "sk428_credits_line_32.yaml"
    yield SK_PARTS / "sk428_credits_line_33.yaml"
    yield SK_PARTS / "sk428_credits_line_35.yaml"
    yield SK_PARTS / "sk428_credits_line_38.yaml"
    yield SK_PARTS / "sk428_credits_line_42.yaml"
    yield SK_PARTS / "sk428_credits_line_50_input.yaml"
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


def _sheet(tmp_path: Path, salary: str, *extra: Artifact[Decimal]) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), *extra]
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-SK"), 2025, *given)
    (sheet,) = worksheets["ca-sk/sk428_credits"]
    return sheet


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_51_is_line_42_when_line_50_is_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _expected(salary) == D(expected)
    assert _sheet(tmp_path, salary).get(SK428_CREDITS_TOTAL_LINE_51).value == D(expected)


def test_line_51_adds_line_50_when_it_is_given(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(SK428_MEDICAL_EXPENSES_LINE_50, D("1500.00")))

    assert _expected("70000", "1500.00") == D("25360.23")
    assert sheet.get(SK428_CREDITS_TOTAL_LINE_51).value == D("25360.23")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_sum_step_like_alberta_line_52() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-sk/sk428_credits"}
    (step,) = part["capabilities"]
    assert list(step) == [
        "name",
        "reference",
        "unit",
        "params",
        "consumes",
        "blank",
        "produces",
    ]
    assert step == {
        "name": "core/sum",
        "reference": "51",
        "unit": "ca/cad",
        "params": {"rounding": "ca-sk/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-sk/sk428_credits_subtotal_line_42",
                "ca-sk/sk428_medical_expenses_line_50",
            ]
        },
        "blank": {"ca-sk/sk428_medical_expenses_line_50": "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_line_51_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = saskatchewan_kinds().kind(IDENTIFIER)

    assert kind is SK428_CREDITS_TOTAL_LINE_51
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
