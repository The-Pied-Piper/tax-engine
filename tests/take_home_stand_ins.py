"""Stand-ins for the forms a province's return summary reads for the take-home average rate.

The return summary part tests compose a temporary manifest of made-up forms and the real
`return.yaml`. The return reads the CPP (Schedule 8) and EI (T2204 line 16) exports, so each
stand-in form declares those exports and one step per export: the salary itself, a made-up figure,
because the part tests are about other lines.
"""

from __future__ import annotations

from textwrap import dedent

SCHEDULE_8_FORM = dedent("""\
    form:
      name: ca/schedule_8
      required: true
      exports:
        - ca/schedule_8_cpp_base_contributions_on_return
        - ca/schedule_8_cpp_enhanced_contributions_on_return
    capabilities: []
    """)
T2204_FORM = dedent("""\
    form:
      name: ca/t2204
      required: true
      exports:
        - ca/t2204_line_16
    capabilities: []
    """)


def _salary_step(form: str, output: str) -> str:
    return dedent(f"""\
        form:
          name: {form}
        capabilities:
          - name: core/record_total
            unit: ca/cad
            consumes:
              records: ca/t1_employment_income.employment_income_line_10100
            produces:
              output: {output}
        """)


# File name and text of each stand-in, forms first, in the order a manifest folder reads them.
STAND_INS = [
    ("03s_schedule_8_form.yaml", SCHEDULE_8_FORM),
    ("03s_t2204_form.yaml", T2204_FORM),
    (
        "03t_schedule_8_base.yaml",
        _salary_step("ca/schedule_8", "ca/schedule_8_cpp_base_contributions_on_return"),
    ),
    (
        "03t_schedule_8_enhanced.yaml",
        _salary_step("ca/schedule_8", "ca/schedule_8_cpp_enhanced_contributions_on_return"),
    ),
    ("03t_t2204_line_16.yaml", _salary_step("ca/t2204", "ca/t2204_line_16")),
]


def _zero_steps(form: str, outputs: tuple[str, ...]) -> str:
    """Stand-ins that make each of `outputs` 0: the salary taken off itself (two kinds of it)."""
    subtracts = "".join(
        f"""\
  - name: core/subtract
    unit: ca/cad
    params:
      rounding: ca/cent_rounding
    consumes:
      amount: ca/return_employment_income
      less: ca/marginal_salary
    produces:
      output: {output}
"""
        for output in outputs
    )
    return f"""\
form:
  name: {form}
capabilities:
  - name: core/record_total
    unit: ca/cad
    consumes:
      records: ca/t1_employment_income.employment_income_line_10100
    produces:
      output: ca/return_employment_income
  - name: core/record_total
    unit: ca/cad
    consumes:
      records: ca/t1_employment_income.employment_income_line_10100
    produces:
      output: ca/marginal_salary
{subtracts}"""


# The same forms with every contribution 0, for the tests whose figures are the income tax alone.
ZERO_STAND_INS = [
    ("03s_schedule_8_form.yaml", SCHEDULE_8_FORM),
    ("03s_t2204_form.yaml", T2204_FORM),
    (
        "03t_schedule_8.yaml",
        _zero_steps(
            "ca/schedule_8",
            (
                "ca/schedule_8_cpp_base_contributions_on_return",
                "ca/schedule_8_cpp_enhanced_contributions_on_return",
            ),
        ),
    ),
    ("03t_t2204.yaml", _zero_steps("ca/t2204", ("ca/t2204_line_16",))),
]
