"""The Nova Scotia take-home return (2025): T1 line 167, "Refund or balance owing".

Form text (T1 General 5006-R, line 167): "Line 167: Line 149 minus line 166. If the amount is
negative, enter it on line 48400 below. If the amount is positive, enter it on line 48500 below."
The line is titled "Refund or balance owing". The return's first output is that line, read from
the T1 tax and credits form: `return.yaml` mirrors the Newfoundland and Labrador, Saskatchewan and
Manitoba parts. Its step is
a core/record_total over the T1 form's export `ca/t1_tax_and_credits.refund_or_balance_owing`, a
cross-form read (another form's export is read only as a record list), producing the return's own
`ca/refund_or_balance_owing`. Positive is a balance owing, negative a refund. The step has no `form`
key (the return is the default form) and no params. The average rate step is pinned in
`test_take_home_return_average_tax_rate.py`; the marginal rate steps run here over stand-ins
(figures in `end_to_end/test_return_marginal_tax_rate_values.py`).

The test composes the T1 employment income form and the real `return.yaml`. The
header, the declaration of the T1 tax and credits form (exporting `ca/refund_or_balance_owing`) and
the step producing that export are made up here, because the shared scaffold and the T1 form own
them: the stand-in step takes a given `ca/total_credits` off the salary, so the figure is positive
at a salary above the credits and negative below.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_ns
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
from tests.jurisdictions.ca_ns.support import (
    nova_scotia_capabilities,
    nova_scotia_kinds,
    nova_scotia_packages,
    nova_scotia_parameter_parsers,
    nova_scotia_units,
)
from tests.take_home_stand_ins import MARGINAL_STAND_INS, STAND_INS

D = Decimal
# The shared marginal-rate stand-in with every export a rate of 0 (the salary through the gate that
# is 0 above 0), so that the sum of the return's rates stays a rate (at most 1).
# The shared marginal-rate stand-in reads the salary through `ca/marginal_rate_gate`, which is 1
# above 0; here each of its exports reads the made-up table `ex/zero_gate` instead, which is 0 above
# 0 (written to the temporary folder by `_service`).
ZERO_GATE = dedent("""\
    # Made-up gate for the test: the rate 0 at every base.
    family: ex/zero_gate
    tax_year: 2025
    kind: amount_by_band
    sources:
      - https://example.com/ex
    rounding: none
    rows:
      - {over: "0", amount: "0"}
    """)
ZERO_MARGINAL_STAND_INS = [
    (name, text.replace("ca/marginal_rate_gate", "ex/zero_gate"))
    for name, text in MARGINAL_STAND_INS
]
NS_PARTS = Path(tax_engine.jurisdictions.ca_ns.__file__).parent / "manifests" / "2025"
RETURN_PART = NS_PARTS / "return.yaml"

HEADER = dedent("""\
    jurisdiction: CA-NS
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/refund_or_balance_owing
      - ca-ns/average_tax_rate
      - ca-ns/marginal_tax_rate
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
NS428_FORM = dedent("""\
    form:
      name: ca-ns/ns428
      required: true
      exports:
        - ca-ns/ns428_bracket_rate_line_5
        - ca-ns/ns428_line_81
        - ca-ns/ns428_low_income_reduction_line_84
        - ca-ns/ns428_nova_scotia_tax_line_99
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
          amount: ca/return_employment_income
          less: ca/total_credits
        produces:
          output: ca/refund_or_balance_owing
    """)


def _salary_total(form: str) -> str:
    """The step through which a stand-in form reads the salary: a form reads another form's export
    (here the T1 employment income form's line 10100) as a record list, and totals it."""
    return dedent(f"""\
        form:
          name: {form}
        capabilities:
          - name: core/record_total
            unit: ca/cad
            consumes:
              records: ca/t1_employment_income.employment_income_line_10100
            produces:
              output: ca/return_employment_income
        """)


# Stand-ins for the other figures the return reads (the total payable): each amount is the salary
# itself, a made-up figure, because this test is about line 167 only; the average rate is in
# `test_take_home_return_average_tax_rate.py`. Form, output kind, unit.
OTHER_STEPS = [
    ("ca/t1_tax_and_credits", "ca/total_payable", "ca/cad"),
    ("ca/t1_tax_and_credits", "ca/federal_bracket_column_rate_line_73", "core/percent"),
    ("ca/t1_tax_and_credits", "ca/federal_tax_after_credits", "ca/cad"),
    ("ca-ns/ns428", "ca-ns/ns428_bracket_rate_line_5", "core/percent"),
    ("ca-ns/ns428", "ca-ns/ns428_line_81", "ca/cad"),
    ("ca-ns/ns428", "ca-ns/ns428_low_income_reduction_line_84", "ca/cad"),
    ("ca-ns/ns428", "ca-ns/ns428_nova_scotia_tax_line_99", "ca/cad"),
]

# salary, credits, line 167: a balance owing and zero (the refund is the trace test below).
CASES = [
    ("70000", "11497.09", "58502.91"),
    ("10000", "10000.00", "0.00"),
]


def _other_step(form: str, output: str, unit: str) -> str:
    """A stand-in step for a figure the return reads: a gate of the salary for a rate (0 or 1, a
    rate is at most 1) and the salary itself for an amount."""
    if unit == "core/percent":
        table = "ca-ns/marginal_rate_gate"
        step = f"""\
          - name: core/amount_by_band_rate
            unit: {unit}
            params:
              table: {table}
            consumes:
              base: ca/return_employment_income
            produces:
              output: {output}
        """
        return f"form:\n  name: {form}\ncapabilities:\n" + dedent(step)
    step = f"""\
        - name: core/sum
          unit: {unit}
          params:
            rounding: ca/cent_rounding
          consumes:
            parts: [ca/return_employment_income]
          produces:
            output: {output}
    """
    return f"form:\n  name: {form}\ncapabilities:\n" + dedent(step)


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Nova Scotia manifest of a test header, the T1 form
    declaration, the stand-in step and the real salary and return parts."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    texts = [
        ("00_header.yaml", HEADER),
        ("01_t1_form.yaml", T1_FORM),
        ("02_credits_input.yaml", CREDITS_INPUT),
        ("03_t1_step.yaml", T1_STEP),
        ("03a_ns428_form.yaml", NS428_FORM),
        *[
            (f"03b_{number}_salary.yaml", _salary_total(form))
            for number, form in enumerate(("ca/t1_tax_and_credits", "ca-ns/ns428"))
        ],
        *[
            (f"03d_{number}.yaml", _other_step(form, out, unit))
            for number, (form, out, unit) in enumerate(OTHER_STEPS)
        ],
        *(
            (f"04_{part.name}", part.read_text(encoding="utf-8"))
            for part in form_parts("t1_employment_income")
        ),
        *STAND_INS,
        *ZERO_MARGINAL_STAND_INS,
        ("05_return.yaml", RETURN_PART.read_text(encoding="utf-8")),
    ]
    for name, text in texts:
        (folder / name).write_text(text, encoding="utf-8")
    datasets = tmp_path / "ex" / "parameters" / "zero_gate"
    datasets.mkdir(parents=True)
    (datasets / "2025.yaml").write_text(ZERO_GATE, encoding="utf-8")
    roots = {**nova_scotia_packages().roots(), Namespace("ca-ns"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, nova_scotia_kinds(), nova_scotia_units()),
        YamlParameterSource(
            {**nova_scotia_packages().roots(), Namespace("ex"): tmp_path / "ex"},
            nova_scotia_parameter_parsers(),
            nova_scotia_units(),
        ),
        nova_scotia_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, credits: str) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), Artifact(TOTAL_CREDITS, D(credits))]
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(JurisdictionCode("CA-NS"), 2025, tuple(given))
    )
    (sheet,) = worksheets["ca-ns/return"]
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


def test_the_return_part_has_no_form_key() -> None:
    assert "form" not in _part()


def test_the_return_has_a_step_beyond_line_167_for_the_average_rate() -> None:
    outputs = [step["produces"]["output"] for step in _part()["capabilities"]]

    assert outputs[0] == "ca/refund_or_balance_owing"
    assert "ca-ns/average_tax_rate" in outputs


def test_the_return_has_the_marginal_rate_as_its_last_step() -> None:
    outputs = [step["produces"]["output"] for step in _part()["capabilities"]]

    assert outputs[0] == "ca/refund_or_balance_owing"
    assert outputs[-1] == "ca-ns/marginal_tax_rate"
