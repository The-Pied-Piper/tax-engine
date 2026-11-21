"""BC428 (2025) line 66, the minimum tax carryover times 34.9%, from the real parts, real engine.

Form text (Form BC428, CRA 5010-C, read 2026-11-14): "British Columbia minimum tax carryover:",
"Line 66 and line 61540: Amount from line 40427 of your return multiplied by 34.9% = ^". The input
is the amount from line 40427 of the return (`ca-bc/bc428_minimum_tax_carryover_amount`), which
the inputs part declares as optional, read as 0 when left out. Line 66 is one calculation: 34.9%
of the amount, a printed rate held in the `ca-bc/minimum_tax_rate` dataset, rounded half-up to
the cent. The output is `ca-bc/bc428_minimum_tax_carryover_line_66`. The step is titled with the
heading the form prints above the line.

The salary part, the inputs part and the line 66 part are loaded under a test-local header and
form declaration over the British Columbia package list of `support.py`, as Alberta's line 64
test does. The expected figures (0.00 at every salary, the amount being blank) are hand-computed
from the ticket, not a CRA example.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_bc.catalog import BC428_MINIMUM_TAX_CARRYOVER_LINE_66
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
MINIMUM_TAX_CARRYOVER = "ca/minimum_tax_carryover"
CODE = JurisdictionCode("CA-BC")
AMOUNT = "ca-bc/bc428_minimum_tax_carryover_amount"
LINE_66 = "ca-bc/bc428_minimum_tax_carryover_line_66"
SALARY = "ca/employment_income"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
PART = BC_PARTS / "bc428_line_66.yaml"

HEADER = dedent(f"""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - {SALARY}
    capabilities: []
    """)
FORM = dedent(f"""\
    form:
      name: ca-bc/bc428
      required: true
      exports:
        - {LINE_66}
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest of a test header, a form declaration
    and the real salary, inputs and line 66 parts, every other namespace being the list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, name in enumerate(["salary.yaml", PART.name], start=2):
        text = (BC_PARTS / name).read_text(encoding="utf-8")
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
    for number, found in enumerate(form_parts("t1_lines_copied_by_provinces"), start=20):
        text = (
            inputs_without_form(found)
            if found.name.endswith("_inputs.yaml")
            else found.read_text(encoding="utf-8")
        )
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
    roots = {**british_columbia_packages().roots(), Namespace("ca-bc"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, british_columbia_kinds(), british_columbia_units()),
        YamlParameterSource(
            british_columbia_packages().roots(),
            british_columbia_parameter_parsers(),
            british_columbia_units(),
        ),
        british_columbia_capabilities(),
    )


def _line_66(tmp_path: Path, salary: str, amount: str | None) -> Decimal:
    kinds = british_columbia_kinds()
    given = [Artifact(kinds.kind(SALARY), D(salary))]
    if amount is not None:
        given.append(Artifact(kinds.kind(MINIMUM_TAX_CARRYOVER), D(amount)))
    (sheet,) = _service(tmp_path).compute(CODE, 2025, *given)["ca-bc/bc428"]
    value = sheet.get(kinds.kind(LINE_66)).value
    assert isinstance(value, Decimal)
    return value


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-bc/bc428"}
    *_, step = part["capabilities"]
    assert isinstance(step, dict)
    return step


@pytest.mark.parametrize("salary", ["17000", "200000"])
def test_a_salary_only_caller_who_leaves_out_the_amount_gets_0(tmp_path: Path, salary: str) -> None:
    # The amount is left out, read as 0 by the inputs part, so line 66 is 0.00 at every salary.
    assert _line_66(tmp_path, salary, None) == D("0.00")


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        # An amount of 1000: 34.9% of 1000 is 349.00.
        ("1000", "349.00"),
        # 0.02 x 34.9% = 0.00698, rounded half-up to 0.01.
        ("0.02", "0.01"),
    ],
)
def test_line_66_is_34_point_9_percent_of_the_amount_rounded_half_up(
    tmp_path: Path, amount: str, expected: str
) -> None:
    assert _line_66(tmp_path, "70000", amount) == D(expected)


def test_the_part_is_one_apply_rate_step_over_the_line_66_amount() -> None:
    assert _step() == {
        "name": "core/apply_rate",
        "title": "British Columbia minimum tax carryover",
        "reference": "66 box B",
        "unit": "ca/cad",
        "params": {"rate": "ca-bc/minimum_tax_rate"},
        "consumes": {"base": AMOUNT},
        "produces": {"output": LINE_66},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = british_columbia_kinds().kind(LINE_66)

    assert kind is BC428_MINIMUM_TAX_CARRYOVER_LINE_66
    assert isinstance(kind, AmountKind)
    assert kind.identifier == LINE_66
    assert kind.value_type is Decimal
    assert non_negative(kind)


def test_the_amount_is_a_record_total_of_the_t1_line_40427_export_with_no_input_of_its_own() -> (
    None
):
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert "inputs" not in part
    assert part["capabilities"][0] == {
        "name": "core/record_total",
        "title": "Amount from line 40427 of your return",
        "reference": "66 box A",
        "unit": "ca/cad",
        "consumes": {"records": "ca/t1_lines_copied_by_provinces.minimum_tax_carryover_line_40427"},
        "produces": {"output": AMOUNT},
    }
