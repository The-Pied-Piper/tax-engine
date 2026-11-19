"""The wiring of the Newfoundland and Labrador return summary's marginal rate, read from the real
`return.yaml`.

The steps mirror the British Columbia return, with the low-income tax reduction as British
Columbia's tax reduction (NL428 lines 95 to 104): the federal marginal rate (T1 line 73 rate gated
on T1 line 42900 through `ca-nl/marginal_rate_gate`, exact through `ca-nl/exact_rounding`), the
Newfoundland and Labrador bracket rate (NL428 line 5 plus line 12, one of them blank), the
reduction's slope (16% where NL428 line 103 is above zero, from the `ca-nl/reduction_slope`
dataset, switched off where line 104 is zero), and a last `core/sum` of the two marginal parts into
`ca-nl/marginal_tax_rate`. The bracket rate plus the slope is gated on NL428 line 105 "Line 94
minus line 104 (if negative, enter "0")". The figures are in
`end_to_end/test_return_marginal_rates.py`. The average rate is pinned in
`test_take_home_return_average_rate_manifest.py`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_nl

PART = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025" / "return.yaml"

# The produced kinds of the marginal rate, in the order of the steps (after line 167).
OUTPUTS = [
    "ca/federal_bracket_rate_return",
    "ca/federal_tax_after_credits_return",
    "ca/federal_rate_gate",
    "ca/federal_marginal_rate",
    "ca-nl/newfoundland_and_labrador_bracket_rate_line_5_return",
    "ca-nl/newfoundland_and_labrador_bracket_rate_line_12_return",
    "ca-nl/newfoundland_and_labrador_bracket_rate_return",
    "ca-nl/newfoundland_and_labrador_tax_after_reduction_return",
    "ca-nl/newfoundland_and_labrador_rate_gate",
    "ca-nl/newfoundland_and_labrador_low_income_reduction_return",
    "ca-nl/newfoundland_and_labrador_reduction_gate",
    "ca-nl/newfoundland_and_labrador_reduction_clawback_return",
    "ca-nl/newfoundland_and_labrador_reduction_slope",
    "ca-nl/newfoundland_and_labrador_reduction_phase_out_rate",
    "ca-nl/newfoundland_and_labrador_bracket_rate_with_reduction",
    "ca-nl/newfoundland_and_labrador_marginal_rate",
    "ca-nl/marginal_tax_rate",
]
EXACT = "ca-nl/exact_rounding"
GATE = "ca-nl/marginal_rate_gate"


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


def test_the_marginal_rate_steps_produce_these_kinds_in_this_order() -> None:
    produced = [step["produces"]["output"] for step in _steps()]

    assert [output for output in produced if output in OUTPUTS] == OUTPUTS
    assert produced[-1] == "ca-nl/marginal_tax_rate"


def test_every_marginal_rate_step_has_no_title_and_no_reference() -> None:
    steps = [step for step in _steps() if step["produces"]["output"] in OUTPUTS]

    assert len(steps) == len(OUTPUTS)
    for step in steps:
        assert "title" not in step
        assert "reference" not in step


def test_the_federal_part_is_read_and_gated_as_the_british_columbia_one_through_the_nl_gate() -> (
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


def test_the_return_reads_the_nl428_line_5_and_line_12_rates_with_a_blank_read_as_0() -> None:
    for line, output in (
        ("5", "ca-nl/newfoundland_and_labrador_bracket_rate_line_5_return"),
        ("12", "ca-nl/newfoundland_and_labrador_bracket_rate_line_12_return"),
    ):
        step = _producing(output)
        assert step["name"] == "core/record_total"
        assert step["unit"] == "core/percent"
        assert step["consumes"] == {
            "records": f"ca-nl/nl428_credits.nl428_bracket_rate_line_{line}"
        }
        assert step["blank"] == {"records": {f"ca-nl/nl428_bracket_rate_line_{line}": "0"}}


def test_the_bracket_rate_is_the_exact_sum_of_the_line_5_and_the_line_12_rate() -> None:
    assert _producing("ca-nl/newfoundland_and_labrador_bracket_rate_return") == {
        "name": "core/sum",
        "unit": "core/percent",
        "params": {"rounding": EXACT},
        "consumes": {
            "parts": [
                "ca-nl/newfoundland_and_labrador_bracket_rate_line_5_return",
                "ca-nl/newfoundland_and_labrador_bracket_rate_line_12_return",
            ]
        },
        "produces": {"output": "ca-nl/newfoundland_and_labrador_bracket_rate_return"},
    }


def test_the_newfoundland_gate_reads_line_105_through_the_nl_gate_dataset() -> None:
    line_105 = _producing("ca-nl/newfoundland_and_labrador_tax_after_reduction_return")
    gate = _producing("ca-nl/newfoundland_and_labrador_rate_gate")

    assert line_105["name"] == "core/record_total"
    assert line_105["unit"] == "ca/cad"
    assert line_105["consumes"] == {
        "records": "ca-nl/nl428.nl428_newfoundland_and_labrador_tax_line_105"
    }
    assert gate["name"] == "core/amount_by_band_rate"
    assert gate["unit"] == "core/percent"
    assert gate["params"] == {"table": GATE}
    assert gate["consumes"] == {
        "base": "ca-nl/newfoundland_and_labrador_tax_after_reduction_return"
    }


def test_the_reduction_gate_reads_line_104_through_the_nl_gate_dataset() -> None:
    line_104 = _producing("ca-nl/newfoundland_and_labrador_low_income_reduction_return")
    gate = _producing("ca-nl/newfoundland_and_labrador_reduction_gate")

    assert line_104["name"] == "core/record_total"
    assert line_104["unit"] == "ca/cad"
    assert line_104["consumes"] == {"records": "ca-nl/nl428.nl428_line_104"}
    assert gate["name"] == "core/amount_by_band_rate"
    assert gate["unit"] == "core/percent"
    assert gate["params"] == {"table": GATE}
    assert gate["consumes"] == {
        "base": "ca-nl/newfoundland_and_labrador_low_income_reduction_return"
    }


def test_the_reduction_slope_reads_line_103_through_the_slope_dataset() -> None:
    line_103 = _producing("ca-nl/newfoundland_and_labrador_reduction_clawback_return")
    slope = _producing("ca-nl/newfoundland_and_labrador_reduction_slope")

    assert line_103["name"] == "core/record_total"
    assert line_103["unit"] == "ca/cad"
    assert line_103["consumes"] == {"records": "ca-nl/nl428.nl428_line_103"}
    assert slope["name"] == "core/amount_by_band_rate"
    assert slope["unit"] == "core/percent"
    assert slope["params"] == {"table": "ca-nl/reduction_slope"}
    assert slope["consumes"] == {
        "base": "ca-nl/newfoundland_and_labrador_reduction_clawback_return"
    }


def test_the_phase_out_rate_is_the_reduction_gate_times_the_slope_exactly() -> None:
    assert _producing("ca-nl/newfoundland_and_labrador_reduction_phase_out_rate") == {
        "name": "core/multiply_by_rate",
        "unit": "core/percent",
        "params": {"rounding": EXACT},
        "consumes": {
            "base": "ca-nl/newfoundland_and_labrador_reduction_gate",
            "rate": "ca-nl/newfoundland_and_labrador_reduction_slope",
        },
        "produces": {"output": "ca-nl/newfoundland_and_labrador_reduction_phase_out_rate"},
    }


def test_the_bracket_rate_with_the_reduction_adds_the_phase_out_rate_exactly() -> None:
    assert _producing("ca-nl/newfoundland_and_labrador_bracket_rate_with_reduction") == {
        "name": "core/sum",
        "unit": "core/percent",
        "params": {"rounding": EXACT},
        "consumes": {
            "parts": [
                "ca-nl/newfoundland_and_labrador_bracket_rate_return",
                "ca-nl/newfoundland_and_labrador_reduction_phase_out_rate",
            ]
        },
        "produces": {"output": "ca-nl/newfoundland_and_labrador_bracket_rate_with_reduction"},
    }


def test_the_newfoundland_marginal_rate_gates_the_bracket_rate_with_the_reduction() -> None:
    assert _producing("ca-nl/newfoundland_and_labrador_marginal_rate") == {
        "name": "core/multiply_by_rate",
        "unit": "core/percent",
        "params": {"rounding": EXACT},
        "consumes": {
            "base": "ca-nl/newfoundland_and_labrador_rate_gate",
            "rate": "ca-nl/newfoundland_and_labrador_bracket_rate_with_reduction",
        },
        "produces": {"output": "ca-nl/newfoundland_and_labrador_marginal_rate"},
    }


def test_the_last_step_sums_the_federal_and_the_newfoundland_marginal_rate() -> None:
    last = _steps()[-1]

    assert last == {
        "name": "core/sum",
        "unit": "core/percent",
        "params": {"rounding": EXACT},
        "consumes": {
            "parts": ["ca/federal_marginal_rate", "ca-nl/newfoundland_and_labrador_marginal_rate"]
        },
        "produces": {"output": "ca-nl/marginal_tax_rate"},
    }


def test_every_gate_uses_the_nl_gate_and_every_product_and_sum_of_rates_rounds_nothing() -> None:
    gates = [step for step in _steps() if step["name"] == "core/amount_by_band_rate"]

    assert len(gates) == 4
    assert [gate["params"]["table"] for gate in gates] == [
        GATE,
        GATE,
        GATE,
        "ca-nl/reduction_slope",
    ]
    for step in _steps():
        if step["name"] in {"core/multiply_by_rate", "core/sum"}:
            assert step["params"]["rounding"] == EXACT
