"""MB428 (2025) line 44, the T1 net income, from the salary alone, real parts.

Form text (Form MB428, CRA 5007-c-25e.txt): "Line 44: Amount from line 23600 of your return". The
line reaches this form as the record list `ca/t1_taxable_income.net_income`, so the one step is
a core/record_total over it. The real salary, Schedule 8 and T1 taxable income parts supply that
list from the salary; the hand figures are asserted (not a CRA example): a $70,000 salary has net
income 69,335.00 (the salary less the enhanced CPP deduction).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_mb.mb428_medical_support import MB_PARTS, compute_line

D = Decimal
OUTPUT = "ca-mb/mb428_net_income_line_44"
PART = "mb428_credits_line_44.yaml"


def _parts() -> list[Path]:
    return [
        MB_PARTS / "salary.yaml",
        *form_parts("schedule_8"),
        *(
            next(FEDERAL_FORMS.rglob(name))
            for name in form_part_names("t1_taxable_income", "t1_employment_income")
        ),
    ]


@pytest.mark.parametrize(("salary", "expected"), [("70000", "69335.00"), ("150000", "148926.00")])
def test_line_44(tmp_path: Path, salary: str, expected: str) -> None:
    value = compute_line(
        tmp_path,
        PART,
        {},
        OUTPUT,
        extra_parts=_parts(),
        part_inputs={"ca/employment_income": salary},
    )

    assert value == D(expected)
