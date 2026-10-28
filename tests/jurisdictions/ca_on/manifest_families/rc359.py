"""The CA-ON manifest entries of Form RC359 (see `test_manifest.py` and `test_manifest_rc359.py`).

RC359 is a form of the manifest: its selections belong to the form `ca/rc359` (`FORM_STEPS`), run
once for each employer of `ca/rc359_employers` (any number, none included), whose fields are the
form's inputs (`FORM_INPUTS`). The form exports line 7 "Excess EPSP amount" and line 9 "Tax on
excess EPSP amount" (`FORM_EXPORTS`). The return reads line 9 of every copy through its record
total, which is T1 line 41800's part `ca/rc359_tax_total` (`STEPS` and `WIRING`); the sum that
adds it into `ca/special_taxes` is the `core/sum` step of the family `net_tax`. Line 7 is read by
nothing on this return (line 22900 is wired separately), so the return declares no output for it.
"""

from __future__ import annotations

from tax_calculator.domain.capabilities.amount_by_count import AmountForCount
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.record_total import RecordTotal
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.jurisdictions.ca.capabilities.apply_percentage import ApplyPercentage
from tax_calculator.jurisdictions.ca.catalog import (
    RC359_EMPLOYMENT_INCOME,
    RC359_EPSP_CONTRIBUTIONS,
    RC359_EXCESS_EPSP_AMOUNT,
    RC359_LINE_4,
    RC359_LINE_6,
    RC359_LINE_8,
    RC359_OTHER_EMPLOYMENT_INCOME,
    RC359_PROVINCE,
    RC359_TAX_ON_EXCESS_EPSP,
    RC359_TAX_TOTAL,
)

# The form's export line 9, read by the return as `ca/rc359.<export label>`: a record list of the
# export's one field, one record for each copy of the form.
EXCESS_EPSP_AMOUNT_PER_EMPLOYER = RecordListKind(
    "ca/rc359.rc359_excess_epsp_amount", fields=(RC359_EXCESS_EPSP_AMOUNT,)
)
TAX_ON_EXCESS_EPSP_PER_EMPLOYER = RecordListKind(
    "ca/rc359.rc359_tax_on_excess_epsp", fields=(RC359_TAX_ON_EXCESS_EPSP,)
)

INPUTS = frozenset({"ca/rc359_employers"})

FORM_INPUTS = frozenset(
    {
        "ca/rc359_epsp_contributions",
        "ca/rc359_employment_income",
        "ca/rc359_other_employment_income",
        "ca/rc359_province",
    }
)

# The form's selections, one for each line that computes: line 5 is the rate of its dataset, so
# lines 5 and 6 are one `core/apply_rate` step.
FORM_STEPS = {
    # Form RC359 line 4 "Line 2 minus line 3": the employment income less the security options and
    # other employment income. No floor is printed, so the figure may be negative.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/rc359_employment_income",
            "less": "ca/rc359_other_employment_income",
        },
        produces={"output": "ca/rc359_line_4"},
    ),
    # Form RC359 line 5 "Rate × 20%" and line 6 "Line 4 multiplied by the percentage from line 5":
    # the line 4 figure at the rate of its dataset.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/rc359_employment_income_rate"},
        consumes={"base": "ca/rc359_line_4"},
        produces={"output": "ca/rc359_line_6"},
    ),
    # Form RC359 line 7 "Line 1 minus line 6 (if negative, enter "0")": the contributions less
    # line 6, not below zero. The excess EPSP amount.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/rc359_epsp_contributions",
            "less": "ca/rc359_line_6",
        },
        produces={"output": "ca/rc359_excess_epsp_amount"},
    ),
    # Form RC359 line 8 "Enter the rate for your province or territory of residence at the end of
    # the year using the charts below.": the printed rate for the province code of the copy.
    CapabilitySelection(
        name="core/amount_by_count",
        params={"table": "ca/rc359_province_percentage"},
        consumes={"count": "ca/rc359_province"},
        produces={"output": "ca/rc359_line_8"},
    ),
    # Form RC359 line 9 "Line 7 multiplied by the percentage from line 8": the excess EPSP amount
    # at the printed percentage, rounded once to the cent.
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/rc359_tax_rounding"},
        consumes={
            "amount": "ca/rc359_excess_epsp_amount",
            "percentage": "ca/rc359_line_8",
        },
        produces={"output": "ca/rc359_tax_on_excess_epsp"},
    ),
}

FORM_EXPORTS = (
    "ca/rc359_excess_epsp_amount",
    "ca/rc359_tax_on_excess_epsp",
)

# The form exports line 7 and line 9; the return reads line 9 through `ca/rc359.<export>`, and
# line 7 is read by nothing on this return, so the return declares no output for the form.
OUTPUTS: frozenset[str] = frozenset()

# T1 line 41800 "Special taxes", the total of the form's line 9 over the copies, which the sum of
# `ca/special_taxes` takes as its last part.
STEPS = {
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/rc359.rc359_tax_on_excess_epsp"},
        produces={"output": "ca/rc359_tax_total"},
    ),
}

FORM_WIRING = {
    (
        Subtract,
        frozenset({RC359_EMPLOYMENT_INCOME, RC359_OTHER_EMPLOYMENT_INCOME}),
        frozenset({RC359_LINE_4}),
    ),
    (ApplyRate, frozenset({RC359_LINE_4}), frozenset({RC359_LINE_6})),
    (
        SubtractNotBelowZero,
        frozenset({RC359_EPSP_CONTRIBUTIONS, RC359_LINE_6}),
        frozenset({RC359_EXCESS_EPSP_AMOUNT}),
    ),
    (AmountForCount, frozenset({RC359_PROVINCE}), frozenset({RC359_LINE_8})),
    (
        ApplyPercentage,
        frozenset({RC359_EXCESS_EPSP_AMOUNT, RC359_LINE_8}),
        frozenset({RC359_TAX_ON_EXCESS_EPSP}),
    ),
}

WIRING = {
    (
        RecordTotal,
        frozenset({TAX_ON_EXCESS_EPSP_PER_EMPLOYER}),
        frozenset({RC359_TAX_TOTAL}),
    ),
}
