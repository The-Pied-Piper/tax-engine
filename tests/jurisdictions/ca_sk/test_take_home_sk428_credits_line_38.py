"""SK428 (2025) line 38, lines 35 to 37 added, from the salary alone, real parts.

Form text (Form SK428, CRA 5008-c-25e.txt line 123): "Line 38: Add lines 35 to 37. =". Line 38 is
a core/sum over line 35 alone, as Ontario's line 77 (`on428_line_77.yaml`, "Add lines 74 to 76")
is a core/sum over line 74 alone: a sum with one contributing part is still built. Lines 36 and 37
are not built, so they add nothing (zero for a salary-only filer). The pension income amount on
line 33 flows through line 35. The form prints no label for line 38, so the step has no title.

The test composes the real Saskatchewan salary part, the real Schedule 8 and T2204 parts, the real
line parts (`sk428_credits_line_9.yaml`, `_line_20.yaml`, `_line_22.yaml`, `_line_24.yaml`,
`_line_31.yaml`, `_line_32.yaml`, `_line_33.yaml`, `_line_35.yaml`, `_line_38.yaml`) and the real
`sk428_line_33_inputs.yaml`, and types in only the salary, or the salary and a pension income
amount. The form declaration is made up here, exporting the lines read, because the real form part
exports only the lines already built. The figures are not a CRA example: they are re-derived below
with Decimal from the printed basic personal amount dataset (19,491), CPP at 4.95% of the salary
above the $3,500 basic exemption to a maximum of $3,356.10, and EI at 1.64% to the $65,700 maximum
insurable earnings, each rounded half-up to the cent.
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
from tax_engine.jurisdictions.ca_sk.catalog import (
    SK428_CREDITS_SUBTOTAL_LINE_38,
    SK428_PENSION_INCOME_AMOUNT,
)
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
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
PART = SK_PARTS / "sk428_credits_line_38.yaml"
IDENTIFIER = "ca-sk/sk428_credits_subtotal_line_38"
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
        - ca-sk/basic_personal_amount
        - ca-sk/sk428_credits_subtotal_line_20
        - ca-sk/sk428_cpp_contributions_line_22
        - ca-sk/sk428_ei_premiums_line_24
        - ca-sk/sk428_cpp_ei_and_other_line_31
        - ca-sk/sk428_credits_subtotal_line_32
        - ca-sk/sk428_credits_subtotal_line_35
        - ca-sk/sk428_credits_subtotal_line_38
    capabilities: []
    """)


def _cpp(salary: str) -> Decimal:
    """Line 22 by hand: 4.95% of the salary above the $3,500 basic exemption, at most $3,356.10."""
    above = max(D(salary) - D("3500"), D("0"))
    return min((above * D("0.0495")).quantize(D("0.01"), ROUND_HALF_UP), D("3356.10"))


def _ei(salary: str) -> Decimal:
    """Line 24 by hand: 1.64% of the salary to the $65,700 maximum, at most $1,077.48."""
    return min(D(salary), D("65700")) * D("0.0164")


def _expected(salary: str, pension: str = "0") -> Decimal:
    line_31 = (_cpp(salary) + _ei(salary)).quantize(D("0.01"), ROUND_HALF_UP)
    line_32 = BASIC_PERSONAL_AMOUNT.quantize(D("0.01")) + line_31
    return line_32 + D(pension)


def _part_files() -> Iterator[Path]:
    yield SK_PARTS / "salary.yaml"
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


def _line_38(service: TaxComputationService, salary: str, pension: str | None = None) -> Decimal:
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if pension is not None:
        artifacts.append(Artifact(SK428_PENSION_INCOME_AMOUNT, D(pension)))
    worksheets = service.compute(JurisdictionCode("CA-SK"), 2025, *artifacts)
    (sheet,) = worksheets["ca-sk/sk428_credits"]
    return sheet.get(SK428_CREDITS_SUBTOTAL_LINE_38).value


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-sk/sk428_credits"}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


# salary, line 38 with the pension input left out. At $200,000 EI and CPP are both at
# their maximum. Lines 34, 36 and 37 are not built, so line 38 equals line 32.
@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("20000", "20635.75"),
        ("200000", "23924.58"),
    ],
)
def test_line_38_adds_lines_35_to_37_with_the_pension_left_out(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _expected(salary) == D(expected)
    assert _line_38(_service(tmp_path), salary) == D(expected)


# salary, pension income amount, line 38.
@pytest.mark.parametrize(
    ("salary", "pension", "expected"),
    [
        ("70000", "1000", "24860.23"),
        ("20000", "0", "20635.75"),
    ],
)
def test_line_38_adds_the_pension_income_amount_entered_on_line_33(
    tmp_path: Path, salary: str, pension: str, expected: str
) -> None:
    service = _service(tmp_path)

    assert _expected(salary, pension) == D(expected)
    assert _line_38(service, salary, pension) == D(expected)
    assert _line_38(service, salary, pension) - _line_38(service, salary) == D(pension)


def test_the_part_is_one_untitled_sum_step_over_line_35_alone() -> None:
    assert _step() == {
        "name": "core/sum",
        "reference": "38",
        "unit": "ca/cad",
        "params": {"rounding": "ca-sk/cent_rounding"},
        "consumes": {"parts": ["ca-sk/sk428_credits_subtotal_line_35"]},
        "produces": {"output": IDENTIFIER},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = saskatchewan_kinds().kind(IDENTIFIER)

    assert kind is SK428_CREDITS_SUBTOTAL_LINE_38
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
