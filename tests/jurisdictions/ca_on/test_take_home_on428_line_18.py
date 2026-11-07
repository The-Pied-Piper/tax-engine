"""ON428 (2025) line 18, the total of lines 9 to 17, as the Ontario take-home manifest wires it.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 18: Add lines 9, 10, 13, 16, and 17."

The ticket builds line 18 as a `core/sum` over the one part it reads: line 9, the basic personal
amount (`ca-on/basic_personal_amount`). Lines 10, 13, 16 and 17 are left out: the take-home filer is
single, Ontario resident all year, under 65, with no spouse or dependants, so the age, spouse,
dependant and caregiver amounts do not apply. The sum has one part, not a copy of line 9, so the
step is still built (one form line, one capability). The line 18 total is the same at every salary,
because line 9 is the same at every salary.

The temporary form declares both the line 9 export and the line 18 export. The real line 9 part and
the real line 18 part are composed beside a test-local header and form declaration.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_on.catalog import ON428_PERSONAL_AMOUNTS_SUBTOTAL_LINE_18
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService

D = Decimal
PART_LINE_9 = "on428_line_9.yaml"
PART_LINE_18 = "on428_line_18.yaml"
PARTS = (PART_LINE_9, PART_LINE_18)

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    """)
FORM = dedent("""\
    form:
      name: ca-on/on428
      required: true
      exports:
        - ca-on/basic_personal_amount
        - ca-on/on428_personal_amounts_subtotal_line_18
    """)


def line_18(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-on/on428"]
    return sheet.get(ON428_PERSONAL_AMOUNTS_SUBTOTAL_LINE_18).value


@pytest.mark.parametrize("salary", ["20000", "70000", "150000"])
def test_line_18_is_the_total_of_line_9_at_every_salary(
    take_home_service: TakeHomeService, salary: str
) -> None:
    assert line_18(take_home_service, salary) == D("12747.00")


def test_line_18_reads_only_line_9_and_leaves_out_the_ontario_only_lines() -> None:
    """Lines 10, 13, 16 and 17 are not read: the sum's only part is ca-on/basic_personal_amount."""
    matches = list(TAKE_HOME.rglob(PART_LINE_18))
    assert len(matches) == 1, f"the take-home folder has no {PART_LINE_18} part"
    part = yaml.safe_load(matches[0].read_text(encoding="utf-8"))
    (capability,) = part["capabilities"]
    assert capability["name"] == "core/sum"
    assert capability["consumes"]["parts"] == ["ca-on/basic_personal_amount"]
    assert capability["produces"]["output"] == "ca-on/on428_personal_amounts_subtotal_line_18"
