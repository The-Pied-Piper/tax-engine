"""The Alberta take-home return (2025): T1 line 167, "Refund or balance owing", real part.

Form text (T1 General 5006-R, line 167): "Line 167: Line 149 minus line 166 ... Refund or balance
owing". The Alberta return's one output is that line, read from the T1 tax and credits form:
`return.yaml` mirrors the Ontario part. Its one step is a core/record_total over the T1 form's
export `ca/t1_tax_and_credits.refund_or_balance_owing`, a cross-form read (another form's export is
read only as a record list), producing the return's own `ca/refund_or_balance_owing`. Positive is
a balance owing, negative a refund. The step has no `form` key (the return is the default form) and
no params.

The test composes the real Alberta salary part and the real `return.yaml`. The header, the
declaration of the T1 tax and credits form (exporting `ca/refund_or_balance_owing`) and the step
producing that export are made up here, because the shared scaffold and the T1 form own them: the
stand-in step takes a given `ca/total_credits` off the salary, so the figure is positive at a
salary above the credits and negative below.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.refund import REFUND_OR_BALANCE_OWING, TOTAL_CREDITS
from tests.jurisdictions.ca_ab.support import (
    alberta_capabilities,
    alberta_kinds,
    alberta_packages,
    alberta_parameter_parsers,
    alberta_units,
)

D = Decimal
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
RETURN_PART = ALBERTA_PARTS / "return.yaml"

HEADER = dedent("""\
    jurisdiction: CA-AB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/refund_or_balance_owing
    capabilities: []
    """)
T1_FORM = dedent("""\
    form:
      name: ca/t1_tax_and_credits
      required: true
      exports:
        - ca/refund_or_balance_owing
    capabilities: []
    """)
CREDITS_INPUT = dedent("""\
    inputs:
      - name: ca/total_credits
        title: "Total credits"
        reference: "48200"
        unit: ca/cad
        required: true
    """)
# The stand-in for the T1 line 167 step: the salary less the given credits, signed.
T1_STEP = dedent("""\
    form:
      name: ca/t1_tax_and_credits
    capabilities:
      - name: core/subtract
        unit: ca/cad
        params:
          rounding: ca/cent_rounding
        consumes:
          amount: ca/employment_income
          less: ca/total_credits
        produces:
          output: ca/refund_or_balance_owing
    """)

# salary, credits, line 167: a balance owing, a refund and zero.
CASES = [
    ("70000", "11497.09", "58502.91"),
    ("20000", "21474.91", "-1474.91"),
    ("10000", "10000.00", "0.00"),
]


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Alberta manifest of a test header, the T1 form declaration, the
    stand-in step and the real salary and return parts."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    texts = [
        ("00_header.yaml", HEADER),
        ("01_t1_form.yaml", T1_FORM),
        ("02_credits_input.yaml", CREDITS_INPUT),
        ("03_t1_step.yaml", T1_STEP),
        ("04_salary.yaml", (ALBERTA_PARTS / "salary.yaml").read_text(encoding="utf-8")),
        ("05_return.yaml", RETURN_PART.read_text(encoding="utf-8")),
    ]
    for name, text in texts:
        (folder / name).write_text(text, encoding="utf-8")
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, credits: str) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), Artifact(TOTAL_CREDITS, D(credits))]
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-AB"), 2025, *given)
    (sheet,) = worksheets["ca-ab/return"]
    return sheet


@pytest.mark.parametrize(("salary", "credits", "expected"), CASES)
def test_the_return_totals_line_167_at_each_salary(
    tmp_path: Path, salary: str, credits: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, credits)

    assert sheet.get(REFUND_OR_BALANCE_OWING).value == D(expected)


def test_the_trace_has_a_row_for_line_167(tmp_path: Path) -> None:
    rows = EnglishTraceRenderer().render_all(_sheet(tmp_path, "20000", "21474.91").trace)

    assert any("Refund or balance owing" in row and "-1474.91" in row for row in rows)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(RETURN_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_has_one_record_total_step_and_no_form_key() -> None:
    part = _part()

    assert list(part) == ["capabilities"]
    (step,) = part["capabilities"]
    assert list(step) == ["name", "title", "reference", "unit", "consumes", "produces"]
    assert step["name"] == "core/record_total"
    assert step["title"] == "Refund or balance owing"
    assert step["reference"] == "167"
    assert step["unit"] == "ca/cad"
    assert step["consumes"] == {"records": "ca/t1_tax_and_credits.refund_or_balance_owing"}
    assert step["produces"] == {"output": "ca/refund_or_balance_owing"}
