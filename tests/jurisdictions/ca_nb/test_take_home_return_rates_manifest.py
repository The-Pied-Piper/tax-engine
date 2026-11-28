"""The wiring of the New Brunswick return summary's rates, read from the real `return.yaml`.

The marginal rate reads the four exports of the federal form `ca/take_home_marginal_rates`
(imported by the manifest) and adds New Brunswick's own part; the values are in
`end_to_end/test_return_marginal_tax_rate_values.py` and `..._gates.py`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_nb

PART = Path(tax_engine.jurisdictions.ca_nb.__file__).parent / "manifests" / "2025" / "return.yaml"


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
    # are in the `ca` package's form; the New Brunswick return holds none of them.
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


def test_the_age_amount_term_is_added_beside_the_low_income_phase_out_before_the_line_97_gate() -> (
    None
):
    steps = _steps()
    outputs = [step["produces"]["output"] for step in steps]
    (reduction,) = (
        step
        for step in steps
        if step["produces"]["output"] == "ca-nb/marginal_new_brunswick_rate_with_reduction"
    )

    assert reduction["consumes"]["parts"] == [
        "ca-nb/marginal_new_brunswick_rate_after_credits",
        "ca-nb/marginal_low_income_phase_out_rate",
        "ca-nb/marginal_new_brunswick_age_credit_rate",
    ]
    assert outputs.index("ca-nb/marginal_new_brunswick_age_credit_rate") < outputs.index(
        "ca-nb/marginal_new_brunswick_rate_with_reduction"
    )
    assert outputs.index("ca-nb/marginal_new_brunswick_rate_with_reduction") < outputs.index(
        "ca-nb/new_brunswick_marginal_rate"
    )


def test_the_age_amount_term_reads_worksheet_line_4_the_claimed_amount_and_the_printed_rate() -> (
    None
):
    by_output = {step["produces"]["output"]: step for step in _steps()}

    assert by_output["ca-nb/age_income_over_threshold_return"]["consumes"] == {
        "records": "ca-nb/nb428.worksheet_nb428_age_amount_line_4"
    }
    assert by_output["ca-nb/age_amount_claimed_return"]["consumes"] == {
        "records": "ca-nb/nb428.nb428_age_amount_claimed_line_10"
    }
    assert by_output["ca-nb/age_rate_figure"]["params"] == {"rate": "ca-nb/age_rate"}
    for gate in ("ca-nb/age_income_over_threshold_gate", "ca-nb/age_amount_claimed_gate"):
        assert by_output[gate]["name"] == "core/amount_by_band_rate"
        assert by_output[gate]["params"] == {"table": "ca-nb/marginal_rate_gate"}
    assert by_output["ca-nb/marginal_new_brunswick_age_credit_rate"]["consumes"] == {
        "base": "ca-nb/marginal_age_phase_down_net_income_rate",
        "rate": "ca-nb/marginal_new_brunswick_credit_rate",
    }
