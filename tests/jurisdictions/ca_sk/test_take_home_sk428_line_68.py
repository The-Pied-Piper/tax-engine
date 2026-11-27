"""SK428 (2025) line 68, the Form T691 amount times 50%, from the real parts, real engine.

Form text (Form SK428, CRA 5008-C): "Saskatchewan additional tax for minimum tax purposes:" / "Line
68: Form T691: Line 1 minus Line 2 of Part 7 ^ multiplied by 50% = ^". The input is the Form T691
amount (`ca-sk/sk428_minimum_tax_t691_amount_line_68`), the total of the T691 export (the
T691 form owns the input), 0 when left out. Line 68 box B is one calculation: 50% of the amount, a
printed rate held in the `ca-sk/minimum_tax_rate` dataset, rounded half-up to the cent. The output
is `ca-sk/sk428_minimum_tax_additional_line_68`. The step is titled with the heading the form
prints above the line, "Saskatchewan additional tax for minimum tax purposes". The T1 employment
income form, the T691 form and the line 68 part are loaded under a test-local header and form
declaration, over the Saskatchewan package list of `support.py`."""

from __future__ import annotations

from decimal import Decimal
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
from tax_engine.domain.errors import CapabilityContractError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca_sk.catalog import SK428_MINIMUM_TAX_ADDITIONAL_LINE_68
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)
from tests.t691_support import line_1_minus_line_2

D = Decimal
CODE = JurisdictionCode("CA-SK")
FORM_NAME = "ca-sk/sk428"
AMOUNT = "ca-sk/sk428_minimum_tax_t691_amount_line_68"
T691_EXPORT = "ca/t691.t691_line_1_minus_line_2_of_part_7"
LINE_68 = "ca-sk/sk428_minimum_tax_additional_line_68"
SALARY = "ca/employment_income"
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
# The T1 employment income form owns the salary input: its declaration, its line 10100 step and
# the input part, as the real parts have them.
T1_PARTS = (*form_parts("t1_employment_income", "t691"),)
PART = SK_PARTS / "sk428_line_68.yaml"

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {LINE_68}
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Saskatchewan manifest of a test header, a form declaration and
    the real salary, inputs and line 68 parts, the other namespaces being the package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    parts = [*T1_PARTS, PART]
    for number, part in enumerate(dict.fromkeys(parts), start=2):
        text = part.read_text(encoding="utf-8")
        (folder / f"{number:02d}_{part.name}").write_text(text, encoding="utf-8")
    roots = {**saskatchewan_packages().roots(), Namespace("ca-sk"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, saskatchewan_kinds(), saskatchewan_units()),
        YamlParameterSource(
            saskatchewan_packages().roots(), saskatchewan_parameter_parsers(), saskatchewan_units()
        ),
        saskatchewan_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, amount: str | None) -> Worksheet:
    kinds = saskatchewan_kinds()
    given = [Artifact(kinds.kind(SALARY), D(salary))]
    if amount is not None:
        given.extend(line_1_minus_line_2(amount))
    (sheet,) = _service(tmp_path).compute(TaxCalculationRequest(CODE, 2025, tuple(given)))[
        FORM_NAME
    ]
    return sheet


def _line_68(tmp_path: Path, salary: str, amount: str | None) -> Decimal:
    value = _sheet(tmp_path, salary, amount).get(saskatchewan_kinds().kind(LINE_68)).value
    assert isinstance(value, Decimal)
    return value


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    *_, step = part["capabilities"]
    assert isinstance(step, dict)
    return step


@pytest.mark.parametrize("salary", ["0", "70000"])
def test_a_salary_only_caller_who_leaves_out_the_amount_gets_0(tmp_path: Path, salary: str) -> None:
    # The amount is left out, filled with 0 by the input's default, so line 68 is 0.00 throughout.
    value = _line_68(tmp_path, salary, None)

    assert value == D("0.00")
    assert str(value) == "0.00"


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        # An amount of 10000: 50% of 10000 is 5000.00.
        ("10000", "5000.00"),
        # 5000 x 50% = 2500.00.
        ("5000", "2500.00"),
        # An amount of 0 gives 0.
        ("0", "0.00"),
        # 0.01 x 50% = 0.005, a tie, rounded half-up to 0.01.
        ("0.01", "0.01"),
    ],
)
def test_line_68_is_50_percent_of_the_amount_rounded_half_up(
    tmp_path: Path, amount: str, expected: str
) -> None:
    value = _line_68(tmp_path, "70000", amount)

    assert value == D(expected)
    assert str(value) == expected


def test_the_part_is_one_apply_rate_step_over_the_line_68_amount() -> None:
    assert _step() == {
        "name": "core/apply_rate",
        "title": "Saskatchewan additional tax for minimum tax purposes",
        "reference": "68 box B",
        "unit": "ca/cad",
        "params": {"rate": "ca-sk/minimum_tax_rate"},
        "consumes": {"base": AMOUNT},
        "produces": {"output": LINE_68},
    }


def test_the_step_keys_are_in_the_order_of_the_neighbouring_parts() -> None:
    assert list(_step()) == [
        "name",
        "title",
        "reference",
        "unit",
        "params",
        "consumes",
        "produces",
    ]


def test_the_step_is_titled_with_the_heading_the_form_prints_above_the_line() -> None:
    assert _step()["title"] == "Saskatchewan additional tax for minimum tax purposes"


def test_the_kind_is_a_registered_decimal_amount() -> None:
    kind = saskatchewan_kinds().kind(LINE_68)

    assert kind is SK428_MINIMUM_TAX_ADDITIONAL_LINE_68
    assert isinstance(kind, AmountKind)
    assert kind.identifier == LINE_68
    assert kind.value_type is Decimal


def test_the_amount_is_a_record_total_of_the_t691_export_with_no_input_of_its_own() -> None:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert "inputs" not in part
    first = part["capabilities"][0]
    assert first["name"] == "core/record_total"
    assert first["title"] == "Form T691: line 1 minus line 2 of Part 7"
    assert first["unit"] == "ca/cad"
    assert first["consumes"] == {"records": T691_EXPORT}
    assert first["produces"] == {"output": AMOUNT}


def test_line_2_above_line_1_is_refused_at_the_t691_figure(tmp_path: Path) -> None:
    # Line 1 minus line 2 of Part 7 is -10000 (line 2 of 10000, line 1 blank): the T691 figure is
    # not below 0, so the engine refuses it there, once; line 68 never sees a negative.
    with pytest.raises(CapabilityContractError, match="t691_line_1_minus_line_2_of_part_7 -10000"):
        _line_68(tmp_path, "70000", "-10000")
