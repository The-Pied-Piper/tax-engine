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
