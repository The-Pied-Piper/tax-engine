"""Stand-in for the federal form a province's return summary reads the take-home average rate from.

The return summary part tests compose a temporary manifest of made-up forms and the real
`return.yaml`. The return reads the export `ca/average_tax_rate` of the form
`ca/take_home_average_rate`, so the stand-in form declares that export and one step for it: the
salary itself, a made-up figure, because the part tests are about other lines.
"""

from __future__ import annotations

from textwrap import dedent

AVERAGE_RATE_FORM = dedent("""\
    form:
      name: ca/take_home_average_rate
      required: true
      exports:
        - ca/average_tax_rate
    capabilities: []
    """)
AVERAGE_RATE_STEP = dedent("""\
    form:
      name: ca/take_home_average_rate
    capabilities:
      - name: core/record_total
        unit: core/percent
        consumes:
          records: ca/t1_employment_income.employment_income_line_10100
        produces:
          output: ca/average_tax_rate
    """)

# File name and text of each stand-in, the form first, in the order a manifest folder reads them.
STAND_INS = [
    ("03s_average_rate_form.yaml", AVERAGE_RATE_FORM),
    ("03t_average_rate.yaml", AVERAGE_RATE_STEP),
]


# The federal marginal-rate form a province's return summary also reads: its four exports, each the
# salary through a gate dataset of the province that is 0 for any salary above 0, so every rate is
# 0 (made-up figures; the part tests are about line 167). The caller names the gate dataset.
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


def marginal_rates_stand_ins(zero_gate: str) -> list[tuple[str, str]]:
    """File name and text of the marginal-rate stand-in form and its steps, over `zero_gate`."""
    steps = (
        "form:\n  name: ca/take_home_marginal_rates\ncapabilities:\n"
        "  - name: core/record_total\n    unit: ca/cad\n    consumes:\n"
        "      records: ca/t1_employment_income.employment_income_line_10100\n"
        "    produces:\n      output: ca/return_employment_income\n"
        + "".join(
            "  - name: core/amount_by_band_rate\n    unit: core/percent\n    params:\n"
            f"      table: {zero_gate}\n    consumes:\n"
            "      base: ca/return_employment_income\n"
            f"    produces:\n      output: ca/{name}\n"
            for name in MARGINAL_RATE_EXPORTS
        )
    )
    return [
        ("03u_marginal_rates_form.yaml", MARGINAL_RATES_FORM),
        ("03v_marginal_rates_steps.yaml", steps),
    ]
