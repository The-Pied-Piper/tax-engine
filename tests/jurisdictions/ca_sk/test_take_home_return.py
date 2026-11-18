"""The Saskatchewan take-home return (2025): T1 line 167, "Refund or balance owing", real part.

Form text (T1 General 5006-R, line 167): "Line 167: Line 149 minus line 166 ... Refund or balance
owing". The Saskatchewan return's first output is that line, read from the T1 tax and credits form:
`return.yaml` mirrors the Manitoba part (the Alberta and Ontario parts before it). Its first step is
a core/record_total over the T1 form's export `ca/t1_tax_and_credits.refund_or_balance_owing`, a
cross-form read (another form's export is read only as a record list), producing the return's own
`ca/refund_or_balance_owing`. Positive is a balance owing, negative a refund. The step has no `form`
key (the return is the default form) and no params. The steps after it read the figures of the two
rates (`end_to_end/test_return_rates.py`); here they run over stand-ins.

The test composes the real Saskatchewan salary part and the real `return.yaml`. The header, the
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

import tax_engine.jurisdictions.ca_sk
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
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)

D = Decimal
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
RETURN_PART = SK_PARTS / "return.yaml"

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/refund_or_balance_owing
      - ca-sk/average_income_tax_rate
      - ca-sk/marginal_tax_rate
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
SK428_CREDITS_FORM = dedent("""\
    form:
      name: ca-sk/sk428_credits
      required: true
      exports:
        - ca-sk/sk428_bracket_rate_line_5
    capabilities: []
    """)
SK428_FORM = dedent("""\
    form:
      name: ca-sk/sk428
      required: true
      exports:
        - ca-sk/sk428_tax_after_credits_line_67
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

# Stand-ins for the other figures the return reads (the total payable, the rates and the taxes):
# each is the salary itself or its gate, a made-up figure, because this test is about line 167
# only; the rates are in `end_to_end/test_return_rates.py`. Form, output kind, unit.
OTHER_STEPS = [
    ("ca/t1_tax_and_credits", "ca/total_payable", "ca/cad"),
    ("ca/t1_tax_and_credits", "ca/federal_bracket_column_rate_line_73", "core/percent"),
    ("ca/t1_tax_and_credits", "ca/federal_tax_after_credits", "ca/cad"),
    ("ca-sk/sk428_credits", "ca-sk/sk428_bracket_rate_line_5", "core/percent"),
    ("ca-sk/sk428", "ca-sk/sk428_tax_after_credits_line_67", "ca/cad"),
]

# salary, credits, line 167: a balance owing, a refund and zero.
CASES = [
    ("70000", "11497.09", "58502.91"),
    ("20000", "21474.91", "-1474.91"),
    ("10000", "10000.00", "0.00"),
]


def _other_step(form: str, output: str, unit: str) -> str:
    """A stand-in step for a figure the return reads: the gate of the salary for a rate (1, a rate
    is at most 1) and the salary itself for an amount."""
    if unit == "core/percent":
        step = f"""\
          - name: core/amount_by_band_rate
            unit: {unit}
            params:
              table: ca-sk/marginal_rate_gate
            consumes:
              base: ca/employment_income
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
              parts: [ca/employment_income]
            produces:
              output: {output}
        """
    return f"form:\n  name: {form}\ncapabilities:\n" + dedent(step)


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Saskatchewan manifest of a test header, the T1 and SK428 form
    declarations, the stand-in steps and the real salary and return parts."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    texts = [
        ("00_header.yaml", HEADER),
        ("01_t1_form.yaml", T1_FORM),
        ("02_credits_input.yaml", CREDITS_INPUT),
        ("03_t1_step.yaml", T1_STEP),
        ("03a_sk428_credits_form.yaml", SK428_CREDITS_FORM),
        ("03b_sk428_form.yaml", SK428_FORM),
        *[
            (f"03c_{number}.yaml", _other_step(form, out, unit))
            for number, (form, out, unit) in enumerate(OTHER_STEPS)
        ],
        ("04_salary.yaml", (SK_PARTS / "salary.yaml").read_text(encoding="utf-8")),
        ("05_return.yaml", RETURN_PART.read_text(encoding="utf-8")),
    ]
    for name, text in texts:
        (folder / name).write_text(text, encoding="utf-8")
    roots = {**saskatchewan_packages().roots(), Namespace("ca-sk"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, saskatchewan_kinds(), saskatchewan_units()),
        YamlParameterSource(
            saskatchewan_packages().roots(), saskatchewan_parameter_parsers(), saskatchewan_units()
        ),
        saskatchewan_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, credits: str) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), Artifact(TOTAL_CREDITS, D(credits))]
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-SK"), 2025, *given)
    (sheet,) = worksheets["ca-sk/return"]
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


def test_the_first_step_is_the_line_167_record_total() -> None:
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
    assert "ca-sk/average_income_tax_rate" in outputs
    assert outputs[-1] == "ca-sk/marginal_tax_rate"


def test_the_return_part_has_no_form_key() -> None:
    assert "form" not in _part()
