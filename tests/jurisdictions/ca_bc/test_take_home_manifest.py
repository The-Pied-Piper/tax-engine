"""The British Columbia take-home manifest asks the caller for the gross salary only.

The take-home calculator has one input. Every other input a form declares must be optional, with
its blank rule (a fixed fallback or `compute`), or a salary-only request is refused. The return
exports line 167 and the two rates, and reads the federal marginal-rate form instead of repeating
its steps.
"""

from __future__ import annotations

from typing import Any

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.manifest import Manifest
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units
from tests.manifest_support import inputs_of

SALARY = "ca/employment_income"


def _manifest() -> Manifest:
    source = YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units())
    (manifest,) = source.get_jurisdiction(JurisdictionCode("CA-BC")).manifests
    return manifest


def _return_steps() -> list[tuple[str, dict[str, str], dict[str, Any], dict[str, str]]]:
    """The steps of the return as (name, params, consumes, produces)."""
    (default,) = (form for form in _manifest().forms if form.name == "ca-bc/return")
    return [
        (step.name, dict(step.params), dict(step.consumes), dict(step.produces))
        for step in default.capabilities
    ]


def test_the_salary_is_the_only_required_input() -> None:
    required = {
        name for name, declaration in inputs_of(_manifest()).items() if declaration.required
    }

    assert required == {SALARY}


def test_the_return_exports_line_167_and_the_two_rates() -> None:
    # The parts of the marginal rate are read inside the return by the final sum, so they are not
    # exported (nor are the gates).
    (default,) = (form for form in _manifest().forms if form.name == "ca-bc/return")

    assert set(default.exports) == {
        "ca-bc/average_tax_rate",
        "ca-bc/marginal_tax_rate",
        "ca/refund_or_balance_owing",
    }


def test_the_return_reads_the_federal_marginal_rate_form_instead_of_repeating_its_steps() -> None:
    # The federal facts (CPP, EI, the line 73 rate, the basic personal amount, the federal gate)
    # are in the `ca` package's form; the British Columbia return holds none of them.
    steps = _return_steps()
    names = {name for *_, produces in steps for name in produces.values()}

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
        consumes["records"]
        for name, _, consumes, _ in steps
        if name == "core/record_total" and "take_home_marginal_rates" in consumes["records"]
    ] == [
        "ca/take_home_marginal_rates.marginal_net_income_rate",
        "ca/take_home_marginal_rates.marginal_credit_contribution_rate",
        "ca/take_home_marginal_rates.marginal_federal_rate",
        "ca/take_home_marginal_rates.marginal_contribution_rate",
    ]


def test_the_return_still_totals_line_167() -> None:
    name, _, consumes, produces = _return_steps()[0]

    assert name == "core/record_total"
    assert consumes == {"records": "ca/t1_tax_and_credits.refund_or_balance_owing"}
    assert produces == {"output": "ca/refund_or_balance_owing"}


def test_the_return_totals_the_age_worksheet_line_4_and_the_claimed_age_amount() -> None:
    steps = _return_steps()
    totals = {
        consumes["records"]: produces["output"]
        for name, _, consumes, produces in steps
        if name == "core/record_total" and consumes["records"].startswith("ca-bc/bc428.")
    }

    assert totals["ca-bc/bc428.worksheet_bc428_age_amount_line_4"] == (
        "ca-bc/british_columbia_age_income_over_threshold_return"
    )
    assert totals["ca-bc/bc428.bc428_age_amount_claimed_line_17"] == (
        "ca-bc/british_columbia_age_amount_claimed_return"
    )


def test_the_age_credit_rate_is_the_fall_of_the_age_amount_times_the_credit_rate() -> None:
    # The printed 15% (the province's own `ca-bc/age_rate`), the two gates, the net income rate and
    # the British Columbia credit rate, multiplied in that order; the credit rate joins the rate
    # with the reduction in the sum the British Columbia gate then governs.
    steps = _return_steps()
    products = [
        (consumes["base"], consumes["rate"], produces["output"])
        for name, _, consumes, produces in steps
        if name == "core/multiply_by_rate" and "age" in produces["output"]
    ]
    (rate,) = [
        params["rate"]
        for name, params, _, produces in steps
        if name == "core/rate_figure"
        and produces["output"] == "ca-bc/marginal_british_columbia_age_rate"
    ]
    (with_reduction,) = [
        consumes["parts"]
        for name, _, consumes, produces in steps
        if name == "core/sum"
        and produces["output"] == "ca-bc/british_columbia_bracket_rate_with_reduction"
    ]

    assert rate == "ca-bc/age_rate"
    assert products == [
        (
            "ca-bc/marginal_british_columbia_age_rate",
            "ca-bc/british_columbia_age_threshold_gate",
            "ca-bc/marginal_british_columbia_age_reduction_rate_over_threshold",
        ),
        (
            "ca-bc/marginal_british_columbia_age_reduction_rate_over_threshold",
            "ca-bc/british_columbia_age_amount_gate",
            "ca-bc/marginal_british_columbia_age_reduction_rate",
        ),
        (
            "ca-bc/marginal_british_columbia_age_reduction_rate",
            "ca-bc/marginal_net_income_rate",
            "ca-bc/marginal_british_columbia_age_phase_down_net_income_rate",
        ),
        (
            "ca-bc/marginal_british_columbia_age_phase_down_net_income_rate",
            "ca-bc/marginal_british_columbia_credit_rate",
            "ca-bc/marginal_british_columbia_age_credit_rate",
        ),
    ]
    assert list(with_reduction) == [
        "ca-bc/marginal_british_columbia_rate_after_credits",
        "ca-bc/marginal_british_columbia_reduction_rate",
        "ca-bc/marginal_british_columbia_age_credit_rate",
    ]
