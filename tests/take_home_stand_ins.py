"""Stand-ins for the federal forms a province's return summary reads its take-home rates from.

The return summary part tests compose a temporary manifest of made-up forms and the real
`return.yaml`. The return reads the export `ca/average_tax_rate` of the form
`ca/take_home_average_rate`, so the stand-in form declares that export and one step for it: the
salary itself, a made-up figure, because the part tests are about other lines. The same goes for
the four exports of the form `ca/take_home_marginal_rates` that a province's marginal rate reads
(the federal credit rate, a made-up figure that is a valid rate).
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

MARGINAL_RATES_EXPORTS = (
    "marginal_net_income_rate",
    "marginal_credit_contribution_rate",
    "marginal_federal_rate",
    "marginal_contribution_rate",
)
MARGINAL_RATES_FORM = (
    "form:\n"
    "  name: ca/take_home_marginal_rates\n"
    "  required: true\n"
    "  exports:\n"
    + "".join(f"    - ca/{name}\n" for name in MARGINAL_RATES_EXPORTS)
    + "capabilities: []\n"
)
MARGINAL_RATES_STEPS = "form:\n  name: ca/take_home_marginal_rates\ncapabilities:\n" + "".join(
    "  - name: core/rate_figure\n"
    "    unit: core/percent\n"
    "    params:\n"
    "      rate: ca/credit_rate\n"
    "    produces:\n"
    f"      output: ca/{name}\n"
    for name in MARGINAL_RATES_EXPORTS
)

# File name and text of each stand-in, the form first, in the order a manifest folder reads them.
STAND_INS = [
    ("03s_average_rate_form.yaml", AVERAGE_RATE_FORM),
    ("03t_average_rate.yaml", AVERAGE_RATE_STEP),
    ("03u_marginal_rates_form.yaml", MARGINAL_RATES_FORM),
    ("03v_marginal_rates.yaml", MARGINAL_RATES_STEPS),
]

MARGINAL_RATES_FORM = dedent("""\
    form:
      name: ca/take_home_marginal_rates
      required: true
      exports:
        - ca/marginal_net_income_rate
        - ca/marginal_credit_contribution_rate
        - ca/marginal_federal_rate
        - ca/marginal_contribution_rate
    capabilities: []
    """)


MARGINAL_RATES_STEPS = dedent("""\
    form:
      name: ca/take_home_marginal_rates
    capabilities:
      - name: core/record_total
        unit: ca/cad
        consumes:
          records: ca/t1_employment_income.employment_income_line_10100
        produces:
          output: ca/marginal_salary
      - name: core/amount_by_band_rate
        unit: core/percent
        params:
          table: ca/marginal_rate_gate
        consumes:
          base: ca/marginal_salary
        produces:
          output: ca/marginal_net_income_rate
      - name: core/amount_by_band_rate
        unit: core/percent
        params:
          table: ca/marginal_rate_gate
        consumes:
          base: ca/marginal_salary
        produces:
          output: ca/marginal_credit_contribution_rate
      - name: core/amount_by_band_rate
        unit: core/percent
        params:
          table: ca/marginal_rate_gate
        consumes:
          base: ca/marginal_salary
        produces:
          output: ca/marginal_federal_rate
      - name: core/amount_by_band_rate
        unit: core/percent
        params:
          table: ca/marginal_rate_gate
        consumes:
          base: ca/marginal_salary
        produces:
          output: ca/marginal_contribution_rate
    """)

# The form and its steps, for the return-part tests whose return also reads the four exports of the
# federal marginal rate form. Each export is a rate, so it is a gate of the salary (1), not the
# salary itself.
MARGINAL_STAND_INS = [
    ("03u_marginal_rates_form.yaml", MARGINAL_RATES_FORM),
    ("03v_marginal_rates.yaml", MARGINAL_RATES_STEPS),
]
