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
# The four exports a return summary reads from the federal marginal-rate form, as made-up rates (a
# rate is at most 1): the gate of the salary (1) for three of them, and 0 for the credit-earning
# contribution rate, the difference of two of those, so that no credit exceeds the tax it comes off.
MARGINAL_RATES_STEPS = dedent("""\
    form:
      name: ca/take_home_marginal_rates
    capabilities:
      - name: core/record_total
        unit: ca/cad
        consumes:
          records: ca/t1_employment_income.employment_income_line_10100
        produces:
          output: ca/return_employment_income
      - name: core/amount_by_band_rate
        unit: core/percent
        params:
          table: ca/marginal_rate_gate
        consumes:
          base: ca/return_employment_income
        produces:
          output: ca/marginal_net_income_rate
      - name: core/amount_by_band_rate
        unit: core/percent
        params:
          table: ca/marginal_rate_gate
        consumes:
          base: ca/return_employment_income
        produces:
          output: ca/marginal_federal_rate
      - name: core/amount_by_band_rate
        unit: core/percent
        params:
          table: ca/marginal_rate_gate
        consumes:
          base: ca/return_employment_income
        produces:
          output: ca/marginal_contribution_rate
      - name: core/subtract
        unit: core/percent
        params:
          rounding: ca/cent_rounding
        consumes:
          amount: ca/marginal_net_income_rate
          less: ca/marginal_federal_rate
        produces:
          output: ca/marginal_credit_contribution_rate
    """)

# File name and text of each stand-in of the marginal-rate form, in the order a manifest folder
# reads them.
MARGINAL_RATES_STAND_INS = [
    ("03u_marginal_rates_form.yaml", MARGINAL_RATES_FORM),
    ("03v_marginal_rates.yaml", MARGINAL_RATES_STEPS),
]
