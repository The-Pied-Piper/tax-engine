"""The wiring of the Manitoba return summary's two rates, read from the real `return.yaml`.

The steps mirror the British Columbia return, with the Manitoba basic personal amount phase-out
(Worksheet MB428, "Line 58040 - Basic personal amount") in the place of its tax reduction: a
`core/divide` of T1 line 43500 over the salary (`ca-mb/rate_rounding`), the federal marginal rate
(T1 line 73 rate gated on T1 line 42900 through `ca-mb/marginal_rate_gate`, exact through
`ca-mb/exact_rounding`), the Manitoba bracket rate (MB428 line 5, never blank, so no sum), the
Manitoba tax after credits (MB428 line 65 "Line 60 minus line 64 (if negative, enter "0")") through
the same gate, and the phase-out chain built from the printed worksheet lines in steps: line 8 read
through the `ca-mb/reduction_slope` dataset (0 where line 8 is 0.00, the printed MB428 line 52 rate
0.108 from one cent), the ratio of line 7 over line 5 (15,780 / 200,000 = 0.0789), the ratio times
the slope (the credit rate of the amount's fall), that times the gate of line 9 (the amount is
still above zero), added to the bracket rate before the line 65 gate multiplies it, and a last
`core/sum` of the two marginal parts into `ca-mb/marginal_tax_rate`. The figures are in
`end_to_end/test_return_rates.py`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_mb

PART = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025" / "return.yaml"

# The produced kinds, in the order of the steps.
OUTPUTS = [
    "ca/refund_or_balance_owing",
    "ca/total_payable",
    "ca/return_employment_income",
    "ca-mb/average_income_tax_rate",
    "ca/federal_bracket_rate_return",
    "ca/federal_tax_after_credits_return",
    "ca/federal_rate_gate",
    "ca/federal_marginal_rate",
    "ca-mb/manitoba_bracket_rate_return",
    "ca-mb/manitoba_tax_after_credits_return",
    "ca-mb/manitoba_rate_gate",
    "ca-mb/manitoba_phase_out_amount_return",
    "ca-mb/manitoba_basic_personal_amount_return",
    "ca-mb/manitoba_base_amount_return",
    "ca-mb/manitoba_income_threshold_return",
    "ca-mb/manitoba_basic_personal_amount_gate",
    "ca-mb/manitoba_reduction_slope",
    "ca-mb/manitoba_phase_out_ratio",
    "ca-mb/manitoba_phase_out_credit_rate",
    "ca-mb/manitoba_phase_out_rate",
    "ca-mb/manitoba_bracket_rate_with_phase_out",
    "ca-mb/manitoba_marginal_rate",
    "ca-mb/marginal_tax_rate",
]
EXACT = "ca-mb/exact_rounding"
GATE = "ca-mb/marginal_rate_gate"
SLOPE_TABLE = "ca-mb/reduction_slope"


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
        # The salary total the average rate divides by carries a title and no reference.
        if step["produces"] != {"output": "ca/return_employment_income"}:
            assert "title" not in step
        assert "reference" not in step


def test_the_average_rate_divides_the_total_payable_by_the_salary_rounded_half_up_once() -> None:
    total = _producing("ca/total_payable")
    salary = _producing("ca/return_employment_income")
    divide = _producing("ca-mb/average_income_tax_rate")

    assert total["name"] == "core/record_total"
    assert total["consumes"] == {"records": "ca/t1_tax_and_credits.total_payable"}
    assert salary["name"] == "core/record_total"
    assert salary["consumes"] == {"records": "ca/t1_employment_income.employment_income_line_10100"}
    assert divide["name"] == "core/divide"
    assert divide["unit"] == "core/percent"
    assert divide["params"] == {"rounding": "ca-mb/rate_rounding"}
    assert divide["consumes"] == {
        "dividend": "ca/total_payable",
        "divisor": "ca/return_employment_income",
    }


def test_the_federal_part_is_read_and_gated_as_the_british_columbia_one_through_the_mb_gate() -> (
    None
):
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


def test_the_return_reads_the_mb428_line_5_rate_and_it_is_never_blank() -> None:
    step = _producing("ca-mb/manitoba_bracket_rate_return")

    assert step["name"] == "core/record_total"
    assert step["unit"] == "core/percent"
    assert step["consumes"] == {"records": "ca-mb/mb428_credits.mb428_bracket_rate_line_5"}
    assert "blank" not in step


def test_only_the_phase_out_and_the_two_marginal_parts_are_sums() -> None:
    sums = [step for step in _steps() if step["name"] == "core/sum"]

    assert [step["produces"]["output"] for step in sums] == [
        "ca-mb/manitoba_bracket_rate_with_phase_out",
        "ca-mb/marginal_tax_rate",
    ]


def test_the_manitoba_gate_reads_line_65_through_the_mb_gate_dataset() -> None:
    line_65 = _producing("ca-mb/manitoba_tax_after_credits_return")
    gate = _producing("ca-mb/manitoba_rate_gate")

    assert line_65["name"] == "core/record_total"
    assert line_65["unit"] == "ca/cad"
    assert line_65["consumes"] == {"records": "ca-mb/mb428.mb428_tax_after_credits_line_65"}
    assert gate["name"] == "core/amount_by_band_rate"
    assert gate["unit"] == "core/percent"
    assert gate["params"] == {"table": GATE}
    assert gate["consumes"] == {"base": "ca-mb/manitoba_tax_after_credits_return"}


def test_the_worksheet_lines_are_totalled_from_the_worksheet_form_in_amounts() -> None:
    expected = {
        "ca-mb/manitoba_phase_out_amount_return": "worksheet_mb428_line_8",
        "ca-mb/manitoba_basic_personal_amount_return": (
            "worksheet_mb428_basic_personal_amount_line_9"
        ),
        "ca-mb/manitoba_base_amount_return": "worksheet_mb428_basic_personal_amount_line_7",
        "ca-mb/manitoba_income_threshold_return": "worksheet_mb428_basic_personal_amount_line_5",
    }

    for output, line in expected.items():
        step = _producing(output)
        assert step["name"] == "core/record_total"
        assert step["unit"] == "ca/cad"
        assert step["consumes"] == {"records": f"ca-mb/worksheet_mb428.{line}"}
        assert "blank" not in step


def test_the_basic_personal_amount_gate_reads_line_9_through_the_mb_gate_dataset() -> None:
    gate = _producing("ca-mb/manitoba_basic_personal_amount_gate")

    assert gate["name"] == "core/amount_by_band_rate"
    assert gate["unit"] == "core/percent"
    assert gate["params"] == {"table": GATE}
    assert gate["consumes"] == {"base": "ca-mb/manitoba_basic_personal_amount_return"}


def test_the_reduction_slope_reads_line_8_through_the_slope_dataset() -> None:
    slope = _producing("ca-mb/manitoba_reduction_slope")

    assert slope["name"] == "core/amount_by_band_rate"
    assert slope["unit"] == "core/percent"
    assert slope["params"] == {"table": SLOPE_TABLE}
    assert slope["consumes"] == {"base": "ca-mb/manitoba_phase_out_amount_return"}


def test_the_phase_out_ratio_is_the_base_amount_over_the_income_threshold_exactly() -> None:
    assert _producing("ca-mb/manitoba_phase_out_ratio") == {
        "name": "core/divide",
        "unit": "core/percent",
        "params": {"rounding": EXACT},
        "consumes": {
            "dividend": "ca-mb/manitoba_base_amount_return",
            "divisor": "ca-mb/manitoba_income_threshold_return",
        },
        "produces": {"output": "ca-mb/manitoba_phase_out_ratio"},
    }


def test_the_phase_out_credit_rate_is_the_ratio_times_the_slope_exactly() -> None:
    assert _producing("ca-mb/manitoba_phase_out_credit_rate") == {
        "name": "core/multiply_by_rate",
        "unit": "core/percent",
        "params": {"rounding": EXACT},
        "consumes": {
            "base": "ca-mb/manitoba_phase_out_ratio",
            "rate": "ca-mb/manitoba_reduction_slope",
        },
        "produces": {"output": "ca-mb/manitoba_phase_out_credit_rate"},
    }


def test_the_phase_out_rate_is_the_basic_personal_amount_gate_times_the_credit_rate_exactly() -> (
    None
):
    assert _producing("ca-mb/manitoba_phase_out_rate") == {
        "name": "core/multiply_by_rate",
        "unit": "core/percent",
        "params": {"rounding": EXACT},
        "consumes": {
            "base": "ca-mb/manitoba_basic_personal_amount_gate",
            "rate": "ca-mb/manitoba_phase_out_credit_rate",
        },
        "produces": {"output": "ca-mb/manitoba_phase_out_rate"},
    }


def test_the_bracket_rate_with_the_phase_out_adds_the_phase_out_rate_exactly() -> None:
    assert _producing("ca-mb/manitoba_bracket_rate_with_phase_out") == {
        "name": "core/sum",
        "unit": "core/percent",
        "params": {"rounding": EXACT},
        "consumes": {
            "parts": [
                "ca-mb/manitoba_bracket_rate_return",
                "ca-mb/manitoba_phase_out_rate",
            ]
        },
        "produces": {"output": "ca-mb/manitoba_bracket_rate_with_phase_out"},
    }


def test_the_manitoba_marginal_rate_gates_the_bracket_rate_with_the_phase_out() -> None:
    assert _producing("ca-mb/manitoba_marginal_rate") == {
        "name": "core/multiply_by_rate",
        "unit": "core/percent",
        "params": {"rounding": EXACT},
        "consumes": {
            "base": "ca-mb/manitoba_rate_gate",
            "rate": "ca-mb/manitoba_bracket_rate_with_phase_out",
        },
        "produces": {"output": "ca-mb/manitoba_marginal_rate"},
    }


def test_the_last_step_sums_the_federal_and_the_manitoba_marginal_rate() -> None:
    last = _steps()[-1]

    assert last == {
        "name": "core/sum",
        "unit": "core/percent",
        "params": {"rounding": EXACT},
        "consumes": {"parts": ["ca/federal_marginal_rate", "ca-mb/manitoba_marginal_rate"]},
        "produces": {"output": "ca-mb/marginal_tax_rate"},
    }


def test_every_gate_uses_its_table_and_every_product_and_sum_of_rates_rounds_nothing() -> None:
    gates = [step for step in _steps() if step["name"] == "core/amount_by_band_rate"]

    assert len(gates) == 4
    assert [gate["params"]["table"] for gate in gates] == [GATE, GATE, GATE, SLOPE_TABLE]
    for step in _steps():
        if step["name"] in {"core/multiply_by_rate", "core/sum"}:
            assert step["params"]["rounding"] == EXACT
    divides = [step for step in _steps() if step["name"] == "core/divide"]
    assert [step["params"]["rounding"] for step in divides] == ["ca-mb/rate_rounding", EXACT]
