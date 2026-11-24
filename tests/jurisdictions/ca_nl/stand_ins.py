"""Stand-in for the federal marginal-rate form the Newfoundland and Labrador return summary reads.

The return summary part test composes a temporary manifest of made-up forms and the real
`return.yaml`. The return reads the four exports of `ca/take_home_marginal_rates`, so the stand-in
form declares them and one step for each: the salary through the
`ca-nl/low_income_reduction_line_86_gate` dataset, which is 0 for any salary above 0, so every
rate is 0 (a made-up figure; the part test is about line 167). The average-rate stand-in the
provinces share is in `tests/take_home_stand_ins.py`.
"""

from __future__ import annotations

MARGINAL_RATE_EXPORTS = (
    "marginal_net_income_rate",
    "marginal_credit_contribution_rate",
    "marginal_federal_rate",
    "marginal_contribution_rate",
)
MARGINAL_RATES_FORM = (
    "form:\n  name: ca/take_home_marginal_rates\n  required: true\n  exports:\n"
    + "".join(f"    - ca/{name}\n" for name in MARGINAL_RATE_EXPORTS)
    + "capabilities: []\n"
)
MARGINAL_RATES_STEPS = (
    "form:\n  name: ca/take_home_marginal_rates\ncapabilities:\n"
    "  - name: core/record_total\n    unit: ca/cad\n    consumes:\n"
    "      records: ca/t1_employment_income.employment_income_line_10100\n"
    "    produces:\n      output: ca/return_employment_income\n"
    + "".join(
        "  - name: core/amount_by_band_rate\n    unit: core/percent\n    params:\n"
        "      table: ca-nl/low_income_reduction_line_86_gate\n    consumes:\n"
        "      base: ca/return_employment_income\n"
        f"    produces:\n      output: ca/{name}\n"
        for name in MARGINAL_RATE_EXPORTS
    )
)
MARGINAL_RATES_STAND_INS = [
    ("03u_marginal_rates_form.yaml", MARGINAL_RATES_FORM),
    ("03v_marginal_rates_steps.yaml", MARGINAL_RATES_STEPS),
]
