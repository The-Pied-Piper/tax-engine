"""The British Columbia take-home return (2025): T1 line 167, "Refund or balance owing", real part.

Form text (T1 General 5006-R, line 167): "Line 167: Line 149 minus line 166 ... Refund or balance
owing". The British Columbia return's first output is that line, read from the T1 tax and credits
form: `return.yaml` mirrors the Alberta and Ontario parts. Its first step is a core/record_total
over the T1 form's export `ca/t1_tax_and_credits.refund_or_balance_owing`, a cross-form read
(another form's export is read only as a record list), producing the return's own
`ca/refund_or_balance_owing`. Positive is a balance owing, negative a refund. The step has no `form`
key (the return is the default form) and no params. The steps after it read the figures of the two
rates (`end_to_end/test_return_marginal_tax_rate.py`); here they run over stand-ins.

The test composes the T1 employment income form and the real `return.yaml` over
a temporary manifest. The header, the declaration of the T1 tax and credits form (exporting
`ca/refund_or_balance_owing`) and the step producing that export are made up here, because the
shared scaffold and the T1 form own them: the stand-in step takes a given `ca/total_credits` off
the salary, so the figure is positive at a salary above the credits and negative below.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.refund import REFUND_OR_BALANCE_OWING, TOTAL_CREDITS
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.take_home_stand_ins import MARGINAL_STAND_INS, STAND_INS

D = Decimal
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
RETURN_PART = BC_PARTS / "return.yaml"

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/refund_or_balance_owing
      - ca-bc/average_tax_rate
      - ca-bc/marginal_tax_rate
    capabilities: []
    """)
T1_FORM = dedent("""\
    form:
      name: ca/t1_tax_and_credits
      required: true
      exports:
        - ca/refund_or_balance_owing
        - ca/total_payable
    capabilities: []
    """)
BC428_FORM = dedent("""\
    form:
      name: ca-bc/bc428
      required: true
      exports:
        - ca-bc/bc428_bracket_rate_line_5
        - ca-bc/bc428_bracket_rate_line_12
        - ca-bc/bc428_reduction_clawback_line_78
        - ca-bc/bc428_british_columbia_tax_reduction_line_79
        - ca-bc/bc428_tax_after_reduction_line_80
        - ca-bc/worksheet_bc428_age_amount_line_4
        - ca-bc/bc428_age_amount_claimed_line_17
    capabilities: []
    """)
CREDITS_INPUT = dedent("""\
    form:
      name: ca/t1_tax_and_credits
    inputs:
      - name: ca/total_credits
        title: "Total credits"
        reference: "48200"
        unit: ca/cad
        required: true
    """)
# The salary is the T1 employment income form's input, so a stand-in step of another form reads it
# as that form's own copy of the T1 export (line 10100), taken by a record total at its start.
SALARY_COPY = """\
form:
  name: {form}
capabilities:
  - name: core/record_total
    unit: ca/cad
    consumes:
      records: ca/t1_employment_income.employment_income_line_10100
    produces:
      output: ca/employment_income_line_10100
"""

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
          amount: ca/employment_income_line_10100
          less: ca/total_credits
        produces:
          output: ca/refund_or_balance_owing
    """)

# Stand-ins for the other figures the return reads (the total payable, the rates, the taxes and the
# reduction): each is the salary itself, a made-up figure, because this test is about line 167 only;
# the rates are in `end_to_end/test_return_marginal_tax_rate.py`. Form, output kind, unit.
OTHER_STEPS = [
    ("ca/t1_tax_and_credits", "ca/total_payable", "ca/cad"),
    ("ca-bc/bc428", "ca-bc/bc428_bracket_rate_line_5", "core/percent"),
    ("ca-bc/bc428", "ca-bc/bc428_bracket_rate_line_12", "core/percent"),
    ("ca-bc/bc428", "ca-bc/bc428_reduction_clawback_line_78", "ca/cad"),
    ("ca-bc/bc428", "ca-bc/bc428_british_columbia_tax_reduction_line_79", "ca/cad"),
    ("ca-bc/bc428", "ca-bc/bc428_tax_after_reduction_line_80", "ca/cad"),
    ("ca-bc/bc428", "ca-bc/worksheet_bc428_age_amount_line_4", "ca/cad"),
    ("ca-bc/bc428", "ca-bc/bc428_age_amount_claimed_line_17", "ca/cad"),
]

# salary, credits, line 167: a balance owing and zero.
CASES = [
    ("70000", "11497.09", "58502.91"),
    ("10000", "10000.00", "0.00"),
]


def _other_step(form: str, output: str, unit: str) -> str:
    """A stand-in step for a figure the return reads: the gate of the salary for a rate (1, a rate
    is at most 1, so the line 5 bracket rate is that 1 and covers the credits that come off it; the
    line 12 bracket rate is the difference of two equal amounts, so 0) and the salary itself for an
    amount."""
    if output.endswith("line_12"):
        step = f"""\
          - name: core/subtract
            unit: {unit}
            params:
              rounding: ca/cent_rounding
            consumes:
              amount: ca-bc/bc428_reduction_clawback_line_78
              less: ca-bc/bc428_british_columbia_tax_reduction_line_79
            produces:
              output: {output}
        """
    elif unit == "core/percent":
        step = f"""\
          - name: core/amount_by_band_rate
            unit: {unit}
            params:
              table: ca-bc/marginal_rate_gate
            consumes:
              base: ca/employment_income_line_10100
            produces:
              output: {output}
        """
    else:
        step = f"""\
          - name: core/sum
            unit: {unit}
            params:
              rounding: ca/cent_rounding
            consumes:
              parts: [ca/employment_income_line_10100]
            produces:
              output: {output}
        """
    return f"form:\n  name: {form}\ncapabilities:\n" + dedent(step)


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest of a test header, the T1 form
    declaration, the stand-in step and the real salary and return parts."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    texts = [
        ("00_header.yaml", HEADER),
        ("01_t1_form.yaml", T1_FORM),
        *(
            (f"04_{part.name}", part.read_text(encoding="utf-8"))
            for part in form_parts("t1_employment_income")
        ),
        ("01b_salary_copy_t1.yaml", SALARY_COPY.format(form="ca/t1_tax_and_credits")),
        ("01c_salary_copy_bc428.yaml", SALARY_COPY.format(form="ca-bc/bc428")),
        ("02_credits_input.yaml", CREDITS_INPUT),
        ("03_t1_step.yaml", T1_STEP),
        ("03a_bc428_form.yaml", BC428_FORM),
        *[
            (f"03b_{number}.yaml", _other_step(form, out, unit))
            for number, (form, out, unit) in enumerate(OTHER_STEPS)
        ],
        *STAND_INS,
        *MARGINAL_STAND_INS,
        ("05_return.yaml", RETURN_PART.read_text(encoding="utf-8")),
    ]
    for name, text in texts:
        (folder / name).write_text(text, encoding="utf-8")
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


def _sheet(tmp_path: Path, salary: str, credits: str) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), Artifact(TOTAL_CREDITS, D(credits))]
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(JurisdictionCode("CA-BC"), 2025, tuple(given))
    )
    (sheet,) = worksheets["ca-bc/return"]
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


def test_the_first_step_is_the_line_167_record_total_and_the_part_has_no_form_key() -> None:
    part = _part()

    assert list(part) == ["capabilities"]
    step = part["capabilities"][0]
    assert list(step) == ["name", "title", "reference", "unit", "consumes", "produces"]
    assert step["name"] == "core/record_total"
    assert step["title"] == "Refund or balance owing"
    assert step["reference"] == "167"
    assert step["unit"] == "ca/cad"
    assert step["consumes"] == {"records": "ca/t1_tax_and_credits.refund_or_balance_owing"}
    assert step["produces"] == {"output": "ca/refund_or_balance_owing"}


def test_the_return_has_steps_beyond_line_167_for_the_two_rates() -> None:
    outputs = [step["produces"]["output"] for step in _part()["capabilities"]]

    assert outputs[0] == "ca/refund_or_balance_owing"
    assert "ca-bc/average_tax_rate" in outputs
    assert outputs[-1] == "ca-bc/marginal_tax_rate"
