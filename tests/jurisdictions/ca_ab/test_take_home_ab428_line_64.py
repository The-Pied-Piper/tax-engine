"""AB428 (2025) line 64, the minimum tax carryover times 35%, from the real parts, real engine.

Form text (Form AB428, CRA 5009-c-25e.txt): "Line 64 and line 61540: Amount from line 40427 of your
return / multiplied by 35% = ^". The input is the amount from line 40427 of the return
(`ca-ab/ab428_minimum_tax_carryover_amount_line_64`), which the inputs part declares as optional,
read as 0 when left out. Line 64 is one calculation: 35% of the amount, a printed rate held in the
`ca-ab/minimum_tax_rate` dataset, rounded half-up to the cent. The output is
`ca-ab/ab428_minimum_tax_carryover_line_64`. The step is titled with the heading the form prints
above the line, "Alberta minimum tax carryover:".

The salary part, the inputs part and the line 64 part are loaded under a test-local header and form
declaration, as Ontario's line 87 test does, over the Alberta package list of `support.py`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_ab.catalog import AB428_MINIMUM_TAX_CARRYOVER_LINE_64
from tests.jurisdictions.ca_ab.support import (
    alberta_capabilities,
    alberta_kinds,
    alberta_packages,
    alberta_parameter_parsers,
    alberta_units,
)
from tests.kinds import non_negative

D = Decimal
CODE = JurisdictionCode("CA-AB")
AMOUNT = "ca-ab/ab428_minimum_tax_carryover_amount_line_64"
LINE_64 = "ca-ab/ab428_minimum_tax_carryover_line_64"
SALARY = "ca/employment_income"
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
PART = ALBERTA_PARTS / "ab428_line_64.yaml"

HEADER = dedent(f"""\
    jurisdiction: CA-AB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - {SALARY}
    capabilities: []
    """)
FORM = dedent(f"""\
    form:
      name: ca-ab/ab428
      required: true
      exports:
        - {LINE_64}
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Alberta manifest of a test header, a form declaration and the
    real salary, inputs and line 64 parts, every other namespace being the package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, name in enumerate(["salary.yaml", "ab428_line_64_inputs.yaml", PART.name], start=2):
        text = (ALBERTA_PARTS / name).read_text(encoding="utf-8")
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )


def _line_64(tmp_path: Path, salary: str, amount: str | None) -> Decimal:
    kinds = alberta_kinds()
    given = [Artifact(kinds.kind(SALARY), D(salary))]
    if amount is not None:
        given.append(Artifact(kinds.kind(AMOUNT), D(amount)))
    (sheet,) = _service(tmp_path).compute(CODE, 2025, *given)["ca-ab/ab428"]
    value = sheet.get(kinds.kind(LINE_64)).value
    assert isinstance(value, Decimal)
    return value


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ab/ab428"}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_salary_only_caller_who_leaves_out_the_amount_gets_0(tmp_path: Path, salary: str) -> None:
    # The amount is left out, read as 0 by the inputs part, so line 64 is 0.00 at every salary.
    assert _line_64(tmp_path, salary, None) == D("0.00")


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        # An amount of 1000.00: 35% of 1000.00 is 350.00.
        ("1000.00", "350.00"),
        # An amount of 0 gives 0.
        ("0", "0.00"),
        # 10.01 x 35% = 3.5035, rounded to 3.50.
        ("10.01", "3.50"),
        # 0.01 x 35% = 0.0035, rounded to 0.00.
        ("0.01", "0.00"),
        # 0.02 x 35% = 0.007, rounded half-up to 0.01.
        ("0.02", "0.01"),
        # 10.10 x 35% = 3.535, a tie, rounded half-up to 3.54.
        ("10.10", "3.54"),
    ],
)
def test_line_64_is_35_percent_of_the_amount_rounded_half_up(
    tmp_path: Path, amount: str, expected: str
) -> None:
    assert _line_64(tmp_path, "70000", amount) == D(expected)


def test_the_part_is_one_apply_rate_step_over_the_line_64_amount() -> None:
    assert _step() == {
        "name": "core/apply_rate",
        "title": "Alberta minimum tax carryover",
        "reference": "64 box B",
        "unit": "ca/cad",
        "params": {"rate": "ca-ab/minimum_tax_rate"},
        "consumes": {"base": AMOUNT},
        "produces": {"output": LINE_64},
    }


def test_the_step_is_titled_with_the_heading_the_form_prints_above_the_line() -> None:
    assert _step()["title"] == "Alberta minimum tax carryover"


def test_the_step_keys_mirror_the_ontario_on428_line_87_part() -> None:
    assert list(_step()) == [
        "name",
        "title",
        "reference",
        "unit",
        "params",
        "consumes",
        "produces",
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = alberta_kinds().kind(LINE_64)

    assert kind is AB428_MINIMUM_TAX_CARRYOVER_LINE_64
    assert isinstance(kind, AmountKind)
    assert kind.identifier == LINE_64
    assert kind.value_type is Decimal
    assert non_negative(kind)
