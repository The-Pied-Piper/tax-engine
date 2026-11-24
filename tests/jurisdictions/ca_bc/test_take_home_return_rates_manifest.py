"""The wiring of the British Columbia return summary's two rates, read from the real `return.yaml`.

The steps mirror the Alberta return, with the British Columbia tax reduction the Ontario return
also has (the payroll factor S of T4127, BC428 lines 73 to 79): a `core/divide` of T1 line 43500
over the salary (`ca-bc/rate_rounding`), the federal marginal rate (T1 line 73 rate gated on T1
line 42900 through `ca-bc/marginal_rate_gate`, exact through `ca-bc/exact_rounding`), the British
Columbia bracket rate (BC428 line 5 plus line 12, one of them blank), the tax reduction's slope
(3.56% where BC428 line 78 is above zero, from the `ca-bc/reduction_slope` dataset, switched off
where line 79 is zero), and a last `core/sum` of the two marginal parts into
`ca-bc/marginal_tax_rate`. The bracket rate plus the slope is gated on BC428 line 80 "Line 72 minus
line 79 (if negative, enter "0")". The figures are in `end_to_end/test_return_rates.py`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_bc

PART = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025" / "return.yaml"

# The produced kinds, in the order of the steps.
OUTPUTS = [
    "ca/refund_or_balance_owing",
    "ca-bc/average_tax_rate",
    "ca/federal_bracket_rate_return",
    "ca/federal_tax_after_credits_return",
    "ca/federal_rate_gate",
    "ca/federal_marginal_rate",
    "ca-bc/british_columbia_bracket_rate_line_5_return",
    "ca-bc/british_columbia_bracket_rate_line_12_return",
    "ca-bc/british_columbia_bracket_rate_return",
    "ca-bc/british_columbia_tax_after_reduction_return",
    "ca-bc/british_columbia_rate_gate",
    "ca-bc/british_columbia_tax_reduction_return",
    "ca-bc/british_columbia_reduction_gate",
    "ca-bc/british_columbia_reduction_clawback_return",
    "ca-bc/british_columbia_reduction_slope",
    "ca-bc/british_columbia_reduction_phase_out_rate",
    "ca-bc/british_columbia_bracket_rate_with_reduction",
    "ca-bc/british_columbia_marginal_rate",
    "ca-bc/marginal_tax_rate",
]
EXACT = "ca-bc/exact_rounding"
GATE = "ca-bc/marginal_rate_gate"


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


def test_the_federal_part_is_read_and_gated_as_the_alberta_one_through_the_bc_gate() -> None:
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


def test_the_return_reads_the_bc428_line_5_and_line_12_rates_with_a_blank_read_as_0() -> None:
    for line, output in (
        ("5", "ca-bc/british_columbia_bracket_rate_line_5_return"),
        ("12", "ca-bc/british_columbia_bracket_rate_line_12_return"),
    ):
        step = _producing(output)
        assert step["name"] == "core/record_total"
        assert step["unit"] == "core/percent"
        assert step["consumes"] == {"records": f"ca-bc/bc428.bc428_bracket_rate_line_{line}"}
        assert step["blank"] == {"records": {f"ca-bc/bc428_bracket_rate_line_{line}": "0"}}


def test_the_bracket_rate_is_the_exact_sum_of_the_line_5_and_the_line_12_rate() -> None:
    assert _producing("ca-bc/british_columbia_bracket_rate_return") == {
        "name": "core/sum",
        "unit": "core/percent",
        "params": {"rounding": EXACT},
        "consumes": {
            "parts": [
                "ca-bc/british_columbia_bracket_rate_line_5_return",
                "ca-bc/british_columbia_bracket_rate_line_12_return",
            ]
        },
        "produces": {"output": "ca-bc/british_columbia_bracket_rate_return"},
    }


def test_the_british_columbia_gate_reads_line_80_through_the_bc_gate_dataset() -> None:
    line_80 = _producing("ca-bc/british_columbia_tax_after_reduction_return")
    gate = _producing("ca-bc/british_columbia_rate_gate")

    assert line_80["name"] == "core/record_total"
    assert line_80["unit"] == "ca/cad"
    assert line_80["consumes"] == {"records": "ca-bc/bc428.bc428_tax_after_reduction_line_80"}
    assert gate["name"] == "core/amount_by_band_rate"
    assert gate["unit"] == "core/percent"
    assert gate["params"] == {"table": GATE}
    assert gate["consumes"] == {"base": "ca-bc/british_columbia_tax_after_reduction_return"}


def test_the_reduction_gate_reads_line_79_through_the_bc_gate_dataset() -> None:
    line_79 = _producing("ca-bc/british_columbia_tax_reduction_return")
    gate = _producing("ca-bc/british_columbia_reduction_gate")

    assert line_79["name"] == "core/record_total"
    assert line_79["unit"] == "ca/cad"
    assert line_79["consumes"] == {
        "records": "ca-bc/bc428.bc428_british_columbia_tax_reduction_line_79"
    }
    assert gate["name"] == "core/amount_by_band_rate"
    assert gate["unit"] == "core/percent"
    assert gate["params"] == {"table": GATE}
    assert gate["consumes"] == {"base": "ca-bc/british_columbia_tax_reduction_return"}


def test_the_reduction_slope_reads_line_78_through_the_slope_dataset() -> None:
    line_78 = _producing("ca-bc/british_columbia_reduction_clawback_return")
    slope = _producing("ca-bc/british_columbia_reduction_slope")

    assert line_78["name"] == "core/record_total"
    assert line_78["unit"] == "ca/cad"
    assert line_78["consumes"] == {"records": "ca-bc/bc428.bc428_reduction_clawback_line_78"}
    assert slope["name"] == "core/amount_by_band_rate"
    assert slope["unit"] == "core/percent"
    assert slope["params"] == {"table": "ca-bc/reduction_slope"}
    assert slope["consumes"] == {"base": "ca-bc/british_columbia_reduction_clawback_return"}


def test_the_phase_out_rate_is_the_reduction_gate_times_the_slope_exactly() -> None:
    assert _producing("ca-bc/british_columbia_reduction_phase_out_rate") == {
        "name": "core/multiply_by_rate",
        "unit": "core/percent",
        "params": {"rounding": EXACT},
        "consumes": {
            "base": "ca-bc/british_columbia_reduction_gate",
            "rate": "ca-bc/british_columbia_reduction_slope",
        },
        "produces": {"output": "ca-bc/british_columbia_reduction_phase_out_rate"},
    }


def test_the_bracket_rate_with_the_reduction_adds_the_phase_out_rate_exactly() -> None:
    assert _producing("ca-bc/british_columbia_bracket_rate_with_reduction") == {
        "name": "core/sum",
        "unit": "core/percent",
        "params": {"rounding": EXACT},
        "consumes": {
            "parts": [
                "ca-bc/british_columbia_bracket_rate_return",
                "ca-bc/british_columbia_reduction_phase_out_rate",
            ]
        },
        "produces": {"output": "ca-bc/british_columbia_bracket_rate_with_reduction"},
    }


def test_the_british_columbia_marginal_rate_gates_the_bracket_rate_with_the_reduction() -> None:
    assert _producing("ca-bc/british_columbia_marginal_rate") == {
        "name": "core/multiply_by_rate",
        "unit": "core/percent",
        "params": {"rounding": EXACT},
        "consumes": {
            "base": "ca-bc/british_columbia_rate_gate",
            "rate": "ca-bc/british_columbia_bracket_rate_with_reduction",
        },
        "produces": {"output": "ca-bc/british_columbia_marginal_rate"},
    }


def test_the_last_step_sums_the_federal_and_the_british_columbia_marginal_rate() -> None:
    last = _steps()[-1]

    assert last == {
        "name": "core/sum",
        "unit": "core/percent",
        "params": {"rounding": EXACT},
        "consumes": {"parts": ["ca/federal_marginal_rate", "ca-bc/british_columbia_marginal_rate"]},
        "produces": {"output": "ca-bc/marginal_tax_rate"},
    }


def test_every_gate_uses_the_bc_gate_and_every_product_and_sum_of_rates_rounds_nothing() -> None:
    gates = [step for step in _steps() if step["name"] == "core/amount_by_band_rate"]

    assert len(gates) == 4
    assert [gate["params"]["table"] for gate in gates] == [
        GATE,
        GATE,
        GATE,
        "ca-bc/reduction_slope",
    ]
    for step in _steps():
        if step["name"] in {"core/multiply_by_rate", "core/sum"}:
            assert step["params"]["rounding"] == EXACT
