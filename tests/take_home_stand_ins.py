"""Stand-ins for the federal forms a province's return summary reads its take-home rates from.

The return summary part tests compose a temporary manifest of made-up forms and the real
`return.yaml`. The return reads the export `ca/average_tax_rate` of the form
`ca/take_home_average_rate`, so the stand-in form declares that export and one step for it: the
salary itself, a made-up figure, because the part tests are about other lines. The form
`ca/take_home_marginal_rates` is stood in the same way for a return that reads its four exports:
each export is the `ca/credit_rate` dataset as a rate, a made-up figure between 0 and 1.
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

MARGINAL_RATE_EXPORTS = (
    "ca/marginal_net_income_rate",
    "ca/marginal_credit_contribution_rate",
    "ca/marginal_federal_rate",
    "ca/marginal_contribution_rate",
)
MARGINAL_RATES_FORM = (
    "form:\n  name: ca/take_home_marginal_rates\n  required: true\n  exports:\n"
    + "".join(f"    - {export}\n" for export in MARGINAL_RATE_EXPORTS)
    + "capabilities: []\n"
)
MARGINAL_RATES_STEPS = "form:\n  name: ca/take_home_marginal_rates\ncapabilities:\n" + "".join(
    "  - name: core/rate_figure\n    unit: core/percent\n"
    "    params:\n      rate: ca/credit_rate\n"
    f"    produces:\n      output: {export}\n"
    for export in MARGINAL_RATE_EXPORTS
)

# File name and text of each stand-in, the form first, in the order a manifest folder reads them.
STAND_INS = [
    ("03s_average_rate_form.yaml", AVERAGE_RATE_FORM),
    ("03t_average_rate.yaml", AVERAGE_RATE_STEP),
    ("03u_marginal_rates_form.yaml", MARGINAL_RATES_FORM),
    ("03v_marginal_rates.yaml", MARGINAL_RATES_STEPS),
]
