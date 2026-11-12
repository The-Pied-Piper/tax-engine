"""Schedule 6 (5000-S6, 2025) line 28, the Canada workers benefit to T1 line 45300, as the Ontario
take-home manifest parts wire it.

Form text (5000-S6 2025, cra-docs/docs/cra-forms-2025/5000-s6-25e.txt, lines 310-311): "Line 28:
Line 22
minus line 27 (if negative, enter "0") If you are not completing Step 3, enter this amount on line
45300 of your return." Line 22 is the basic benefit before reduction
(`ca/cwb_basic_benefit_line_22`, from schedule_6_line_22.yaml) and line 27 is the reduction amount
(`ca/cwb_reduction_line_27`, from schedule_6_line_27.yaml). Line 28 is one
core/subtract_not_below_zero of line 27 from line 22, so the result is floored at zero. The
take-home filer does not complete Step 3 (no disability tax credit), so line 28 is the figure that
goes to T1 line 45300.

The test loads the parts of test_take_home_schedule_6_line_27.py, then the line 1, 5, 6, 17, 18,
20, 21 and 22 parts that line 22 needs, and the line 24 and 25 parts that line 27 needs, then the
line 28 part under test. The manifest parts are loaded from the package. The header and the form's
export are made up here, because the shared scaffold owns them.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.canada_workers_benefit import CWB_BENEFIT_LINE_28
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME, OTHER_EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService

D = Decimal
# The parts of test_take_home_schedule_6_line_27.py, with the line 1, 5, 6, 17, 18, 20, 21 and 22
# parts that line 22 reads inserted in form order, then the line 28 part under test.
PARTS = (
    "salary.yaml",
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
    "t1_taxable_income_inputs.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_taxable_income_line_10400_inputs.yaml",
    "schedule_6_line_1.yaml",
    "schedule_6_line_5.yaml",
    "schedule_6_line_6.yaml",
    "schedule_6_line_7.yaml",
    "schedule_6_line_10.yaml",
    "schedule_6_line_11_inputs.yaml",
    "schedule_6_line_12.yaml",
    "schedule_6_line_13.yaml",
    "schedule_6_line_14_inputs.yaml",
    "schedule_6_line_15.yaml",
    "schedule_6_line_17.yaml",
    "schedule_6_line_18.yaml",
    "schedule_6_line_20.yaml",
    "schedule_6_line_21.yaml",
    "schedule_6_line_22.yaml",
    "schedule_6_line_24.yaml",
    "schedule_6_line_25.yaml",
    "schedule_6_line_27.yaml",
    "schedule_6_line_28.yaml",
)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca/schedule_6
      required: true
      exports:
        - ca/cwb_benefit_line_28
    """)


def line_28(take_home_service: TakeHomeService, salary: str, other: str | None = None) -> Decimal:
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if other is not None:
        artifacts.append(Artifact(OTHER_EMPLOYMENT_INCOME, D(other)))
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-ON"), 2025, *artifacts
    )
    (sheet,) = worksheets["ca/schedule_6"]
    return sheet.get(CWB_BENEFIT_LINE_28).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 22 is $0.00 and line 27 is $0.00, so line 28 is $0.00.
        ("2000", "0.00"),
        # Line 22 is $810.00 and line 27 is $0.00 (line 25 is $0.00), so line 28 is $810.00.
        ("6000", "810.00"),
        # Line 22 is $1,633.00 and line 27 is $0.00 (line 25 is $0.00), so line 28 is $1,633.00.
        ("20000", "1633.00"),
        # Line 22 is $1,633.00 and line 27 is $432.00, so line 28 is $1,201.00.
        ("30000", "1201.00"),
        # Line 22 is $1,633.00 and line 27 is $1,174.50, so line 28 is $458.50.
        ("35000", "458.50"),
        # Line 22 is $1,633.00 and line 27 is $1,917.00, which is more than line 22. The difference
        # is -$284.00, floored at zero, so line 28 is $0.00.
        ("40000", "0.00"),
        # Line 22 is $1,633.00 and line 27 is $6,372.00, which is more than line 22. The difference
        # is floored at zero, so line 28 is $0.00.
        ("70000", "0.00"),
    ],
)
def test_schedule_6_line_28_is_line_22_minus_line_27_not_below_zero(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = line_28(take_home_service, salary)
    assert value == D(expected)
    assert value.as_tuple().exponent == -2


@pytest.mark.parametrize("salary", ["40000", "70000"])
def test_schedule_6_line_28_is_zero_when_line_27_exceeds_line_22(
    take_home_service: TakeHomeService, salary: str
) -> None:
    # Line 27 (the reduction) is more than line 22 (the basic benefit) at these salaries, so the
    # subtraction is negative and the form's "(if negative, enter "0")" makes line 28 zero, not a
    # negative amount on T1 line 45300.
    value = line_28(take_home_service, salary)
    assert value == D("0.00")
    assert value.as_tuple().exponent == -2


def test_schedule_6_line_28_counts_other_employment_income(
    take_home_service: TakeHomeService,
) -> None:
    # $20,000 salary and $10,000 other employment income (line 10400): line 1 is $30,000.00, so
    # working income is $30,000.00 and net income is $29,835.00. Line 22 is $1,633.00 and line 27
    # is $447.00 (15% of the $2,980.00 over $26,855.00), so line 28 is $1,186.00. Salary alone
    # leaves line 28 at $1,633.00.
    value = line_28(take_home_service, "20000", "10000")
    assert value == D("1186.00")
    assert value.as_tuple().exponent == -2
