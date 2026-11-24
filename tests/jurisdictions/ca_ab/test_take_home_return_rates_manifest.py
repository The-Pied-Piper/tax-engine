"""The wiring of the Alberta return summary's rates, read from the real `return.yaml`.

The marginal rate reads the four exports of the federal form `ca/take_home_marginal_rates`
(imported by the manifest) and adds Alberta's own part; the values are in
`end_to_end/test_return_marginal_tax_rate_values.py` and `..._gates.py`.
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


def test_the_return_still_totals_line_167_first() -> None:
    first = _steps()[0]

    assert first["name"] == "core/record_total"
    assert first["consumes"] == {"records": "ca/t1_tax_and_credits.refund_or_balance_owing"}
    assert first["produces"] == {"output": "ca/refund_or_balance_owing"}


def test_the_return_reads_the_federal_marginal_rate_form_instead_of_repeating_its_steps() -> None:
    # The federal facts (CPP, EI, the line 73 rate, the basic personal amount, the federal gate)
    # are in the `ca` package's form; the Alberta return holds none of them.
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
