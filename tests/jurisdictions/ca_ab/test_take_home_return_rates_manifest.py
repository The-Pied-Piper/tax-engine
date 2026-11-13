"""The wiring of the Alberta return summary's two rates, read from the real `return.yaml`.

The steps mirror the Ontario return without its surtax, health premium and tax reduction: a
`core/divide` of T1 line 43500 over the salary (`ca-ab/rate_rounding`), the federal marginal rate
(T1 line 73 rate gated on T1 line 42900 through `ca-ab/marginal_rate_gate`, exact through
`ca-ab/exact_rounding`), the Alberta bracket rate (AB428 line 5 plus line 12, one of them blank)
gated on AB428 line 68, and a last `core/sum` of the two marginal parts into
`ca-ab/marginal_tax_rate`. The names of the Alberta intermediate kinds are not pinned here, only
the reads, the datasets and the produced outputs. The figures are in
`end_to_end/test_return_rates.py`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_ab

PART = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025" / "return.yaml"


def _steps() -> list[dict[str, Any]]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    steps = part["capabilities"]
    assert isinstance(steps, list)
    return steps


def _by_name(name: str) -> list[dict[str, Any]]:
    return [step for step in _steps() if step["name"] == name]


def _record_totals_of(records: str) -> list[dict[str, Any]]:
    return [
        step for step in _by_name("core/record_total") if step["consumes"]["records"] == records
    ]


def test_the_return_still_totals_line_167_first() -> None:
    first = _steps()[0]

    assert first["name"] == "core/record_total"
    assert first["consumes"] == {"records": "ca/t1_tax_and_credits.refund_or_balance_owing"}
    assert first["produces"] == {"output": "ca/refund_or_balance_owing"}


def test_the_average_rate_divides_the_total_payable_by_the_salary_rounded_half_up_once() -> None:
    (total,) = _record_totals_of("ca/t1_tax_and_credits.total_payable")
    (divide,) = _by_name("core/divide")

    assert total["produces"] == {"output": "ca/total_payable"}
    assert divide["params"] == {"rounding": "ca-ab/rate_rounding"}
    assert divide["consumes"] == {
        "dividend": "ca/total_payable",
        "divisor": "ca/employment_income",
    }
    assert divide["produces"] == {"output": "ca-ab/average_income_tax_rate"}
    assert divide["unit"] == "core/percent"
    assert "title" not in divide
    assert "reference" not in divide


def test_the_return_reads_the_federal_line_73_rate_and_line_42900() -> None:
    (rate,) = _record_totals_of("ca/t1_tax_and_credits.federal_bracket_column_rate_line_73")
    (tax,) = _record_totals_of("ca/t1_tax_and_credits.federal_tax_after_credits")

    assert rate["produces"] == {"output": "ca/federal_bracket_rate_return"}
    assert tax["produces"] == {"output": "ca/federal_tax_after_credits_return"}


def test_the_federal_gate_reads_line_42900_through_the_alberta_gate_dataset_exactly() -> None:
    gates = [
        step
        for step in _by_name("core/amount_by_band_rate")
        if step["consumes"] == {"base": "ca/federal_tax_after_credits_return"}
    ]
    (gate,) = gates

    assert gate["params"] == {"table": "ca-ab/marginal_rate_gate"}
    assert gate["produces"] == {"output": "ca/federal_rate_gate"}
    assert {
        "name": "core/multiply_by_rate",
        "unit": "core/percent",
        "params": {"rounding": "ca-ab/exact_rounding"},
        "consumes": {"base": "ca/federal_rate_gate", "rate": "ca/federal_bracket_rate_return"},
        "produces": {"output": "ca/federal_marginal_rate"},
    } in _steps()


def test_the_return_reads_the_ab428_line_5_and_line_12_rates_and_line_68() -> None:
    assert _record_totals_of("ca-ab/ab428_credits.ab428_bracket_rate_line_5")
    assert _record_totals_of("ca-ab/ab428_credits.ab428_bracket_rate_line_12")
    assert _record_totals_of("ca-ab/ab428.ab428_tax_line_68")


def test_the_alberta_gate_reads_line_68_through_the_alberta_gate_dataset() -> None:
    (line_68,) = _record_totals_of("ca-ab/ab428.ab428_tax_line_68")
    base = line_68["produces"]["output"]
    (gate,) = [
        step for step in _by_name("core/amount_by_band_rate") if step["consumes"] == {"base": base}
    ]

    assert gate["params"] == {"table": "ca-ab/marginal_rate_gate"}


def test_every_gated_rate_and_the_marginal_sum_round_nothing_and_every_gate_is_alberta_s() -> None:
    steps = _steps()

    assert _by_name("core/amount_by_band_rate")
    assert _by_name("core/sum")
    for step in steps:
        if step["name"] == "core/amount_by_band_rate":
            assert step["params"] == {"table": "ca-ab/marginal_rate_gate"}
        if step["name"] in {"core/multiply_by_rate", "core/sum"}:
            assert step["params"]["rounding"] == "ca-ab/exact_rounding"


def test_the_last_step_sums_the_federal_and_the_alberta_marginal_rate_into_the_marginal_rate() -> (
    None
):
    last = _steps()[-1]

    assert last["name"] == "core/sum"
    assert last["unit"] == "core/percent"
    assert last["consumes"]["parts"][0] == "ca/federal_marginal_rate"
    assert len(last["consumes"]["parts"]) == 2
    assert last["produces"] == {"output": "ca-ab/marginal_tax_rate"}
    assert "title" not in last
    assert "reference" not in last
