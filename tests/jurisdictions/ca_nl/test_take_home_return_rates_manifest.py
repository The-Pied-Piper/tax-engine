"""The wiring of the Newfoundland and Labrador return summary's rates, read from the real
`return.yaml`.

The marginal rate reads the four exports of the federal form `ca/take_home_marginal_rates`
(imported by the manifest) and adds Newfoundland and Labrador's own part; the values are in
`end_to_end/test_return_marginal_tax_rate_values.py` and `..._gates.py`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_nl

PART = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025" / "return.yaml"


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
    # are in the `ca` package's form; the Newfoundland and Labrador return holds none of them.
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


def test_the_age_amount_fall_is_read_from_the_forms_that_export_it() -> None:
    reads = [
        step["consumes"]["records"]
        for step in _steps()
        if step["name"] == "core/record_total"
        and step["produces"]["output"]
        in {"ca-nl/marginal_age_income_over_threshold", "ca-nl/marginal_age_amount_claimed"}
    ]

    assert reads == [
        "ca-nl/nl428_worksheet.worksheet_nl428_age_amount_line_4",
        "ca-nl/nl428_credits.nl428_age_amount_claimed_line_17",
    ]


def test_the_age_term_is_added_to_the_bracket_rate_before_the_contribution_credit_comes_off() -> (
    None
):
    by_output = {step["produces"]["output"]: step for step in _steps()}
    before = "ca-nl/marginal_newfoundland_and_labrador_rate_before_credits"
    after = "ca-nl/marginal_newfoundland_and_labrador_rate_after_credits"

    assert by_output[before]["consumes"] == {
        "parts": [
            "ca-nl/marginal_newfoundland_and_labrador_bracket_rate",
            "ca-nl/marginal_newfoundland_and_labrador_age_credit_rate",
        ]
    }
    assert by_output[after]["consumes"] == {
        "amount": before,
        "less": "ca-nl/marginal_newfoundland_and_labrador_contribution_credit_rate",
    }


def test_the_age_term_is_the_fall_rate_times_the_part_left_times_the_credit_rate() -> None:
    by_output = {step["produces"]["output"]: step for step in _steps()}
    term = "ca-nl/marginal_newfoundland_and_labrador_age_credit_rate"

    assert by_output["ca-nl/marginal_age_rate"]["params"] == {"rate": "ca-nl/age_rate"}
    assert by_output["ca-nl/marginal_age_reduction_rate_over_threshold"]["consumes"] == {
        "base": "ca-nl/marginal_age_rate",
        "rate": "ca-nl/marginal_age_threshold_gate",
    }
    assert by_output["ca-nl/marginal_age_reduction_rate"]["consumes"] == {
        "base": "ca-nl/marginal_age_reduction_rate_over_threshold",
        "rate": "ca-nl/marginal_age_amount_gate",
    }
    assert by_output["ca-nl/marginal_age_phase_down_net_income_rate"]["consumes"] == {
        "base": "ca-nl/marginal_age_reduction_rate",
        "rate": "ca-nl/marginal_net_income_rate",
    }
    assert by_output[term]["consumes"] == {
        "base": "ca-nl/marginal_age_phase_down_net_income_rate",
        "rate": "ca-nl/marginal_newfoundland_and_labrador_credit_rate",
    }
    for gate in ("ca-nl/marginal_age_threshold_gate", "ca-nl/marginal_age_amount_gate"):
        assert by_output[gate]["params"] == {"table": "ca-nl/marginal_rate_gate"}
