"""The wiring of the Saskatchewan return summary's two rates, read from the real `return.yaml`.

The steps mirror the British Columbia return without its tax reduction (Saskatchewan has none): a
`core/divide` of T1 line 43500 over the salary (`ca-sk/rate_rounding`), the federal marginal rate
(T1 line 73 rate gated on T1 line 42900 through `ca-sk/marginal_rate_gate`, exact through
`ca-sk/exact_rounding`), the Saskatchewan bracket rate (Form SK428 line 5, which prints one table of
three columns: "Rate 10.5%", "Rate 12.5%", "Rate 14.5%"), gated on SK428 line 67 "Line 62 minus
line 66 (if negative, enter "0")", and a last `core/sum` of the two marginal parts into
`ca-sk/marginal_tax_rate`. The figures are in `end_to_end/test_return_rates.py`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_sk

PART = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025" / "return.yaml"

# The produced kinds, in the order of the steps.
OUTPUTS = [
    "ca/refund_or_balance_owing",
    "ca/total_payable",
    "ca/return_employment_income",
    "ca/return_cpp_base_contributions",
    "ca/return_cpp_enhanced_contributions",
    "ca/return_ei_premium",
    "ca/return_total_deductions",
    "ca-sk/average_tax_rate",
    "ca/federal_bracket_rate_return",
    "ca/federal_tax_after_credits_return",
    "ca/federal_rate_gate",
    "ca/federal_marginal_rate",
    "ca-sk/saskatchewan_bracket_rate_return",
    "ca-sk/saskatchewan_tax_after_credits_return",
    "ca-sk/saskatchewan_rate_gate",
    "ca-sk/saskatchewan_marginal_rate",
    "ca-sk/marginal_tax_rate",
]
SALARY_RECORD = "ca/return_employment_income"
EXACT = "ca-sk/exact_rounding"
GATE = "ca-sk/marginal_rate_gate"


def _steps() -> list[dict[str, Any]]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    steps = part["capabilities"]
    assert isinstance(steps, list)
    return steps


def _producing(output: str) -> dict[str, Any]:
    (step,) = [step for step in _steps() if step["produces"] == {"output": output}]
    return step


def test_the_return_still_totals_line_167_first() -> None:
    first = _steps()[0]

    assert first["name"] == "core/record_total"
    assert first["consumes"] == {"records": "ca/t1_tax_and_credits.refund_or_balance_owing"}
    assert first["produces"] == {"output": "ca/refund_or_balance_owing"}


def test_the_steps_produce_these_kinds_in_this_order() -> None:
    assert [step["produces"]["output"] for step in _steps()] == OUTPUTS


def test_every_step_after_line_167_has_no_title_and_no_reference() -> None:
    assert len(_steps()) == len(OUTPUTS)
    for step in _steps()[1:]:
        assert "title" not in step
        assert "reference" not in step


def test_the_salary_record_totals_the_t1_line_10100_export_with_no_title_and_no_reference() -> None:
    step = _producing(SALARY_RECORD)

    assert step["name"] == "core/record_total"
    assert "title" not in step
    assert "reference" not in step
    assert step["unit"] == "ca/cad"
    assert step["consumes"] == {"records": "ca/t1_employment_income.employment_income_line_10100"}


def test_the_average_rate_divides_the_deductions_by_the_salary_rounded_half_up_once() -> None:
    total = _producing("ca/total_payable")
    divide = _producing("ca-sk/average_tax_rate")
    deductions = _producing("ca/return_total_deductions")

    assert total["consumes"] == {"records": "ca/t1_tax_and_credits.total_payable"}
    assert deductions["params"] == {"rounding": "ca-sk/exact_rounding"}
    assert deductions["consumes"]["parts"] == [
        "ca/total_payable",
        "ca/return_cpp_base_contributions",
        "ca/return_cpp_enhanced_contributions",
        "ca/return_ei_premium",
    ]
    assert divide["params"] == {"rounding": "ca/take_home_average_rate_rounding"}
    assert divide["consumes"] == {
        "dividend": "ca/return_total_deductions",
        "divisor": "ca/return_employment_income",
    }
    assert divide["produces"] == {"output": "ca-sk/average_tax_rate"}
    assert divide["unit"] == "core/percent"
    assert "title" not in divide
    assert "reference" not in divide


def test_the_federal_part_is_read_and_gated_through_the_saskatchewan_gate() -> None:
    assert _producing("ca/federal_bracket_rate_return")["consumes"] == {
        "records": "ca/t1_tax_and_credits.federal_bracket_column_rate_line_73"
    }
    assert _producing("ca/federal_tax_after_credits_return")["consumes"] == {
        "records": "ca/t1_tax_and_credits.federal_tax_after_credits"
    }
    gate = _producing("ca/federal_rate_gate")
    assert gate["name"] == "core/amount_by_band_rate"
    assert gate["params"] == {"table": GATE}
    assert gate["consumes"] == {"base": "ca/federal_tax_after_credits_return"}
    assert _producing("ca/federal_marginal_rate") == {
        "name": "core/multiply_by_rate",
        "unit": "core/percent",
        "params": {"rounding": EXACT},
        "consumes": {"base": "ca/federal_rate_gate", "rate": "ca/federal_bracket_rate_return"},
        "produces": {"output": "ca/federal_marginal_rate"},
    }


def test_the_return_reads_the_sk428_line_5_rate_as_one_record_total_with_no_sum() -> None:
    step = _producing("ca-sk/saskatchewan_bracket_rate_return")

    assert step["name"] == "core/record_total"
    assert step["unit"] == "core/percent"
    assert step["consumes"] == {"records": "ca-sk/sk428_credits.sk428_bracket_rate_line_5"}
    assert [step["produces"]["output"] for step in _steps() if step["name"] == "core/sum"] == [
        "ca/return_total_deductions",
        "ca-sk/marginal_tax_rate",
    ]


def test_the_saskatchewan_gate_reads_line_67_through_the_saskatchewan_gate_dataset() -> None:
    line_67 = _producing("ca-sk/saskatchewan_tax_after_credits_return")
    gate = _producing("ca-sk/saskatchewan_rate_gate")

    assert line_67["name"] == "core/record_total"
    assert line_67["unit"] == "ca/cad"
    assert line_67["consumes"] == {"records": "ca-sk/sk428.sk428_tax_after_credits_line_67"}
    assert gate["name"] == "core/amount_by_band_rate"
    assert gate["unit"] == "core/percent"
    assert gate["params"] == {"table": GATE}
    assert gate["consumes"] == {"base": "ca-sk/saskatchewan_tax_after_credits_return"}


def test_the_saskatchewan_marginal_rate_is_the_gate_times_the_line_5_rate_exactly() -> None:
    assert _producing("ca-sk/saskatchewan_marginal_rate") == {
        "name": "core/multiply_by_rate",
        "unit": "core/percent",
        "params": {"rounding": EXACT},
        "consumes": {
            "base": "ca-sk/saskatchewan_rate_gate",
            "rate": "ca-sk/saskatchewan_bracket_rate_return",
        },
        "produces": {"output": "ca-sk/saskatchewan_marginal_rate"},
    }


def test_the_last_step_sums_the_federal_and_the_saskatchewan_marginal_rate() -> None:
    last = _steps()[-1]

    assert last == {
        "name": "core/sum",
        "unit": "core/percent",
        "params": {"rounding": EXACT},
        "consumes": {"parts": ["ca/federal_marginal_rate", "ca-sk/saskatchewan_marginal_rate"]},
        "produces": {"output": "ca-sk/marginal_tax_rate"},
    }


def test_every_gate_uses_the_saskatchewan_gate_and_every_product_and_sum_rounds_nothing() -> None:
    gates = [step for step in _steps() if step["name"] == "core/amount_by_band_rate"]

    assert len(gates) == 2
    assert [gate["params"]["table"] for gate in gates] == [GATE, GATE]
    for step in _steps():
        if step["name"] in {"core/multiply_by_rate", "core/sum"}:
            assert step["params"]["rounding"] == EXACT
