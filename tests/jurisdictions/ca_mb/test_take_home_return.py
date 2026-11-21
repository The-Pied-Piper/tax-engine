"""The Manitoba take-home return (2025): T1 line 167, "Refund or balance owing", real part.

Form text (T1 General 5006-R, line 167): "Line 167: Line 149 minus line 166 ... Refund or balance
owing". The Manitoba return's one output is that line, read from the T1 tax and credits form:
`return.yaml` mirrors the Alberta part (the Ontario part before it). Its one step is a
core/record_total over the T1 form's export `ca/t1_tax_and_credits.refund_or_balance_owing`, a
cross-form read (another form's export is read only as a record list), producing the return's own
`ca/refund_or_balance_owing`. Positive is a balance owing, negative a refund. The step has no `form`
key (the return is the default form) and no params. The steps after it read the figures of the two
rates (`end_to_end/test_return_rates.py`); here they run over stand-ins.

The test composes the T1 employment income form and the real `return.yaml`. The header, the
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

import tax_engine.jurisdictions.ca_mb
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
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)
from tests.manifest_support import T1_LINE_10100_FORM, T1_LINE_10100_INPUT, T1_LINE_10100_STEP

D = Decimal
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
RETURN_PART = MB_PARTS / "return.yaml"

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/refund_or_balance_owing
      - ca-mb/average_income_tax_rate
      - ca-mb/marginal_tax_rate
    capabilities: []
    """)
T1_FORM = dedent("""\
    form:
      name: ca/t1_tax_and_credits
      required: true
      exports:
        - ca/refund_or_balance_owing
        - ca/total_payable
        - ca/federal_bracket_column_rate_line_73
        - ca/federal_tax_after_credits
    capabilities: []
    """)
CREDITS_FORM = dedent("""\
    form:
      name: ca-mb/mb428_credits
      required: true
      exports:
        - ca-mb/mb428_bracket_rate_line_5
    capabilities: []
    """)
MB428_FORM = dedent("""\
    form:
      name: ca-mb/mb428
      required: true
      exports:
        - ca-mb/mb428_tax_after_credits_line_65
    capabilities: []
    """)
WORKSHEET_FORM = dedent("""\
    form:
      name: ca-mb/worksheet_mb428
      required: true
      exports:
        - ca-mb/worksheet_mb428_basic_personal_amount_line_5
        - ca-mb/worksheet_mb428_basic_personal_amount_line_7
        - ca-mb/worksheet_mb428_line_8
        - ca-mb/worksheet_mb428_basic_personal_amount_line_9
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
          amount: ca/canada_employment_amount_line_1
          less: ca/total_credits
        produces:
          output: ca/refund_or_balance_owing
    """)

# The salary belongs to the T1 employment income form, so a stand-in step in another form reads it
# as that form's own total of the T1 line 10100 export, as the real forms do. Each form takes one
# real kind that form's line 10100 total would hold (the kinds are made up here for the stand-ins:
# a form needs a kind of its own, and no stand-in form has one for the salary).
SALARY_OF = {
    "ca/t1_tax_and_credits": "ca/canada_employment_amount_line_1",
    "ca-mb/mb428_credits": "ca/schedule_8_employment_income_line_10100",
    "ca-mb/mb428": "ca/t2204_employment_income_line_10100",
    "ca-mb/worksheet_mb428": "ca/cwb_employment_income_line_10100",
}


def _salary_total(form: str) -> str:
    """The stand-in form's own total of the T1 line 10100 export."""
    return dedent(f"""\
        form:
          name: {form}
        capabilities:
          - name: core/record_total
            unit: ca/cad
            consumes:
              records: ca/t1_employment_income.employment_income_line_10100
            produces:
              output: {SALARY_OF[form]}
        """)


# Stand-ins for the other figures the return reads (the total payable, the rates, the taxes and the
# worksheet lines): each amount is the salary itself and each rate is the slope chart's 0.108,
# made-up figures, because this test is about line 167 only; the rates are in
# `end_to_end/test_return_rates.py`. Form, output kind, unit.
OTHER_STEPS = [
    ("ca/t1_tax_and_credits", "ca/total_payable", "ca/cad"),
    ("ca/t1_tax_and_credits", "ca/federal_bracket_column_rate_line_73", "core/percent"),
    ("ca/t1_tax_and_credits", "ca/federal_tax_after_credits", "ca/cad"),
    ("ca-mb/mb428_credits", "ca-mb/mb428_bracket_rate_line_5", "core/percent"),
    ("ca-mb/mb428", "ca-mb/mb428_tax_after_credits_line_65", "ca/cad"),
    ("ca-mb/worksheet_mb428", "ca-mb/worksheet_mb428_basic_personal_amount_line_5", "ca/cad"),
    ("ca-mb/worksheet_mb428", "ca-mb/worksheet_mb428_basic_personal_amount_line_7", "ca/cad"),
    ("ca-mb/worksheet_mb428", "ca-mb/worksheet_mb428_line_8", "ca/cad"),
    ("ca-mb/worksheet_mb428", "ca-mb/worksheet_mb428_basic_personal_amount_line_9", "ca/cad"),
]

# salary, credits, line 167: a balance owing and zero (the refund is the trace test's).
CASES = [
    ("70000", "11497.09", "58502.91"),
    ("10000", "10000.00", "0.00"),
]


def _other_step(form: str, output: str, unit: str) -> str:
    """A stand-in step for a figure the return reads: the slope chart's 0.108 for a rate (a rate is
    at most 1, and the salary is above 0) and the salary itself for an amount."""
    salary = SALARY_OF[form]
    if unit == "core/percent":
        step = f"""\
          - name: core/amount_by_band_rate
            unit: {unit}
            params:
              table: ca-mb/reduction_slope
            consumes:
              base: {salary}
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
              parts: [{salary}]
            produces:
              output: {output}
        """
    return f"form:\n  name: {form}\ncapabilities:\n" + dedent(step)


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, the T1 form declaration, the
    stand-in step and the real salary and return parts."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    texts = [
        ("00_header.yaml", HEADER),
        ("01_t1_form.yaml", T1_FORM),
        ("02_credits_input.yaml", CREDITS_INPUT),
        ("03_t1_step.yaml", T1_STEP),
        *[(f"03s_{number}.yaml", _salary_total(form)) for number, form in enumerate(SALARY_OF)],
        ("03a_credits_form.yaml", CREDITS_FORM),
        ("03b_mb428_form.yaml", MB428_FORM),
        ("03c_worksheet_form.yaml", WORKSHEET_FORM),
        *[
            (f"03d_{number}.yaml", _other_step(form, out, unit))
            for number, (form, out, unit) in enumerate(OTHER_STEPS)
        ],
        ("04_salary.yaml", T1_LINE_10100_INPUT.read_text(encoding="utf-8")),
        ("04a_t1_employment_income_form.yaml", T1_LINE_10100_FORM.read_text(encoding="utf-8")),
        ("04b_t1_line_10100.yaml", T1_LINE_10100_STEP.read_text(encoding="utf-8")),
        ("05_return.yaml", RETURN_PART.read_text(encoding="utf-8")),
    ]
    for name, text in texts:
        (folder / name).write_text(text, encoding="utf-8")
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, credits: str) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), Artifact(TOTAL_CREDITS, D(credits))]
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-MB"), 2025, *given)
    (sheet,) = worksheets["ca-mb/return"]
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


def test_the_sheet_carries_the_printed_title_and_reference(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", "11497.09")
    label = REFUND_OR_BALANCE_OWING.label

    assert sheet.title(label) == "Refund or balance owing"
    assert sheet.reference(label) == "167"


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
    assert "ca-mb/average_income_tax_rate" in outputs
    assert outputs[-1] == "ca-mb/marginal_tax_rate"
