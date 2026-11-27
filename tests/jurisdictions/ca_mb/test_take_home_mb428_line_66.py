"""MB428 (2025) line 66, the T691 amount times 50%, from the real parts, real engine.

Form text (Form MB428, CRA 5007-C, read 2026-11-17): "Manitoba additional tax for minimum tax
purposes:" / "Line 66: Form T691: line 1 minus line 2 of Part 7 ^" / "multiplied by 50% = ^". The
input is the amount from Form T691 (`ca-mb/mb428_t691_amount_line_66`), the total of the T691
line 1 minus line 2 export (the T691 form owns the input), read as 0 when left out. Line 66 is one
calculation: 50% of the amount, a printed rate held in the `ca-mb/minimum_tax_rate` dataset,
rounded half-up to the cent. The output is `ca-mb/mb428_additional_tax_minimum_tax_line_66`. The
step is titled with the heading the form prints above the line, "Manitoba additional tax for
minimum tax purposes". The T691 form and the line 66 part are loaded under a test-local header and
form declaration, over the Manitoba package list of `support.py`."""

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
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import CapabilityContractError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca_mb.catalog import MB428_ADDITIONAL_TAX_MINIMUM_TAX_LINE_66
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)
from tests.kinds import non_negative
from tests.t691_support import line_1_minus_line_2

D = Decimal
CODE = JurisdictionCode("CA-MB")
FORM_NAME = "ca-mb/mb428"
AMOUNT = "ca-mb/mb428_t691_amount_line_66"
T691_EXPORT = "ca/t691.t691_line_1_minus_line_2_of_part_7"
LINE_66 = "ca-mb/mb428_additional_tax_minimum_tax_line_66"
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
PART = MB_PARTS / "mb428_line_66.yaml"

HEADER = dedent("""\
    jurisdiction: CA-MB
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
        - {LINE_66}
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, a form declaration and the
    real salary, inputs and line 66 parts, every other namespace being the package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    parts = [*form_parts("t691"), PART]
    for number, part in enumerate(dict.fromkeys(parts), start=2):
        text = part.read_text(encoding="utf-8")
        (folder / f"{number:02d}_{part.name}").write_text(text, encoding="utf-8")
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, amount: str | None) -> Worksheet:
    given: list[Artifact[Any]] = []
    if amount is not None:
        given.extend(line_1_minus_line_2(amount))
    (sheet,) = _service(tmp_path).compute(TaxCalculationRequest(CODE, 2025, tuple(given)))[
        FORM_NAME
    ]
    return sheet


def _line_66(tmp_path: Path, salary: str, amount: str | None) -> Decimal:
    value = _sheet(tmp_path, salary, amount).get(manitoba_kinds().kind(LINE_66)).value
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


@pytest.mark.parametrize("salary", ["10000", "200000"])
def test_a_salary_only_caller_who_leaves_out_the_amount_gets_0(tmp_path: Path, salary: str) -> None:
    # The amount is left out, read as 0 by the step's blank rule, so line 66 is 0.00 throughout.
    value = _line_66(tmp_path, salary, None)

    assert value == D("0.00")
    assert str(value) == "0.00"


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        # An amount of 1000.00: 50% of 1000.00 is 500.00.
        ("1000.00", "500.00"),
        # 5,000.00 x 50% = 2,500.00.
        ("5000.00", "2500.00"),
        # 0.01 x 50% = 0.005, a tie, rounded half-up to 0.01.
        ("0.01", "0.01"),
    ],
)
def test_line_66_is_50_percent_of_the_amount_rounded_half_up(
    tmp_path: Path, amount: str, expected: str
) -> None:
    value = _line_66(tmp_path, "70000", amount)

    assert value == D(expected)
    assert str(value) == expected


def test_line_2_above_line_1_is_refused_at_the_t691_figure(tmp_path: Path) -> None:
    # Line 1 minus line 2 of -1,000.00: the T691 figure is not below 0, so the engine refuses it
    # there, once; line 66 never sees a negative.
    with pytest.raises(CapabilityContractError, match="part_7 -1000.00"):
        _line_66(tmp_path, "70000", "-1000.00")


def test_a_negative_line_2_alone_still_gives_a_positive_amount(tmp_path: Path) -> None:
    # Line 2 is signed: line 1 of 1,000.00 minus line 2 of -200.00 is 1,200.00, 50% is 600.00.
    kinds = manitoba_kinds()
    given = [
        Artifact(kinds.kind("ca/t691_minimum_amount"), D("1000.00")),
        Artifact(kinds.kind("ca/t691_basic_federal_tax"), D("-200.00")),
    ]
    (sheet,) = _service(tmp_path).compute(TaxCalculationRequest(CODE, 2025, tuple(given)))[
        "ca-mb/mb428"
    ]

    assert sheet.get(kinds.kind(LINE_66)).value == D("600.00")


def test_the_part_is_one_apply_rate_step_over_the_line_66_amount() -> None:
    assert _step() == {
        "name": "core/apply_rate",
        "title": "Manitoba additional tax for minimum tax purposes",
        "reference": "66",
        "unit": "ca/cad",
        "params": {"rate": "ca-mb/minimum_tax_rate"},
        "consumes": {"base": AMOUNT},
        "produces": {"output": LINE_66},
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
    assert _step()["title"] == "Manitoba additional tax for minimum tax purposes"


def test_the_kinds_are_registered_non_negative_decimal_amounts() -> None:
    kinds = manitoba_kinds()
    kind = kinds.kind(LINE_66)

    assert kind is MB428_ADDITIONAL_TAX_MINIMUM_TAX_LINE_66
    assert isinstance(kind, AmountKind)
    assert kind.identifier == LINE_66
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert non_negative(kinds.kind(AMOUNT))


def test_the_amount_is_a_record_total_of_the_t691_export_with_no_input_of_its_own() -> None:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert "inputs" not in part
    first = part["capabilities"][0]
    assert first["name"] == "core/record_total"
    assert first["title"] == "Form T691: line 1 minus line 2 of Part 7"
    assert first["unit"] == "ca/cad"
    assert first["consumes"] == {"records": T691_EXPORT}
    assert first["produces"] == {"output": AMOUNT}
