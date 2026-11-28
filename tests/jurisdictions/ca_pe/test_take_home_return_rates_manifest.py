"""The wiring of the Prince Edward Island return summary's rates, read from the real
`return.yaml`.

The marginal rate reads the four exports of the federal form `ca/take_home_marginal_rates`
(imported by the manifest) and adds Prince Edward Island's own part; the values are in
`end_to_end/test_return_marginal_tax_rate_values.py` and `..._gates.py`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_pe

PART = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025" / "return.yaml"


def _steps() -> list[dict[str, Any]]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    steps = part["capabilities"]
    assert isinstance(steps, list)
    return steps


def test_the_return_still_totals_line_167_first() -> None:
    first = _steps()[0]

    assert first["name"] == "core/record_total"
    assert first["consumes"] == {"records": "ca/t1_tax_and_credits.refund_or_balance_owing"}
    assert first["produces"] == {"output": "ca/refund_or_balance_owing"}


def test_the_return_reads_the_federal_marginal_rate_form_instead_of_repeating_its_steps() -> None:
    # The federal facts (CPP, EI, the line 73 rate, the basic personal amount, the federal gate)
    # are in the `ca` package's form; the Prince Edward Island return holds none of them.
    steps = _steps()
    names = {step["produces"]["output"] for step in steps}

    assert (
        not {
            "ca/federal_bracket_rate_return",
            "ca/federal_tax_after_credits_return",
            "ca/federal_rate_gate",
            "ca/federal_marginal_rate",
        }
        & names
    )
    assert [
        step["consumes"]["records"]
        for step in steps
        if step["name"] == "core/record_total"
        and "take_home_marginal_rates" in step["consumes"]["records"]
    ] == [
        "ca/take_home_marginal_rates.marginal_net_income_rate",
        "ca/take_home_marginal_rates.marginal_credit_contribution_rate",
        "ca/take_home_marginal_rates.marginal_federal_rate",
        "ca/take_home_marginal_rates.marginal_contribution_rate",
    ]


def test_every_step_after_line_167_has_no_title_and_no_reference() -> None:
    for step in _steps()[1:]:
        assert "title" not in step
        assert "reference" not in step


def test_the_age_amount_term_reads_the_two_pe428_exports_and_enters_the_rate_after_credits() -> (
    None
):
    steps = _steps()
    outputs = [step["produces"]["output"] for step in steps]
    by_output = {step["produces"]["output"]: step for step in steps}

    assert by_output["ca-pe/marginal_age_income_over_threshold"]["consumes"] == {
        "records": "ca-pe/pe428.worksheet_pe428_age_amount_line_4"
    }
    assert by_output["ca-pe/marginal_age_amount_claimed"]["consumes"] == {
        "records": "ca-pe/pe428.pe428_age_amount_claimed_line_10"
    }
    assert by_output["ca-pe/marginal_age_rate"]["params"] == {"rate": "ca-pe/age_rate"}
    assert by_output["ca-pe/marginal_prince_edward_island_age_credit_rate"]["consumes"] == {
        "base": "ca-pe/marginal_age_phase_down_net_income_rate",
        "rate": "ca-pe/marginal_prince_edward_island_credit_rate",
    }
    assert by_output["ca-pe/marginal_prince_edward_island_rate_with_reduction"]["consumes"] == {
        "parts": [
            "ca-pe/marginal_prince_edward_island_rate_after_credits",
            "ca-pe/marginal_prince_edward_island_age_credit_rate",
            "ca-pe/marginal_low_income_phase_out_rate",
        ]
    }
    # The age term comes before the sum it is a part of, and the line 97 gate multiplies the sum.
    assert outputs.index("ca-pe/marginal_prince_edward_island_age_credit_rate") < outputs.index(
        "ca-pe/marginal_prince_edward_island_rate_with_reduction"
    )
    assert by_output["ca-pe/prince_edward_island_marginal_rate"]["consumes"] == {
        "base": "ca-pe/prince_edward_island_rate_gate",
        "rate": "ca-pe/marginal_prince_edward_island_rate_with_reduction",
    }
