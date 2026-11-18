"""The Saskatchewan artifact catalog: Saskatchewan's own kinds, named from the Saskatchewan forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_sk import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

SK428_TAXABLE_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "sk428_taxable_income_line_1", non_negative=True
)
"""Taxable income, Form SK428 Line 1 "Enter your taxable income from line 26000 of your return": the
T1 taxable income, read directly by lines 3 and 4."""

SK428_TAX_ON_TAXABLE_INCOME_LINE_8 = AmountKind.declare(
    CATALOG, "sk428_tax_on_taxable_income_line_8", non_negative=True
)
"""Saskatchewan tax on taxable income, SK428 line 8 "Line 6 plus line 7 Saskatchewan tax on taxable
income =": line 6 plus line 7, read by line 58 on the tax form."""

SK428_EI_PREMIUMS_LINE_24 = AmountKind.declare(
    CATALOG, "sk428_ei_premiums_line_24", non_negative=True
)
"""EI premiums credit amount, SK428 line 24 (line 58300) "Amount from line 31200 of your return": a
copy of T2204 line 16, the EI premiums credit amount."""

SK428_PENSION_INCOME_AMOUNT = AmountKind.declare(
    CATALOG, "sk428_pension_income_amount", non_negative=True
)
"""Pension income amount, SK428 line 33 "Line 33 and line 58360: Pension income amount (maximum
$1,000)": the amount the filer claims, a caller input that is read as 0 when it is left out."""

SK428_MEDICAL_EXPENSES_LINE_50 = AmountKind.declare(
    CATALOG, "sk428_medical_expenses_line_50", non_negative=True
)
"""Medical expenses, SK428 line 50 (line 58769) "Line 48 plus line 49 =": line 48 plus line 49, an
optional input; a blank is read as 0 by the line 51 step."""

SK428_DONATIONS_CREDIT_LINE_56 = AmountKind.declare(
    CATALOG, "sk428_donations_credit_line_56", non_negative=True
)
"""Donations and gifts credit, SK428 line 56 (58969) "Line 56 and 58969: Line 54 plus line
55 =": a caller input, read as blank when left out; line 57 reads it."""

SK428_NON_REFUNDABLE_CREDITS_LINE_57 = AmountKind.declare(
    CATALOG, "sk428_non_refundable_credits_line_57", non_negative=True
)
"""Saskatchewan non-refundable tax credits, SK428 line 57 "Line 57 and line 61500: Line 53 plus line
56 Enter this amount on line 63. Saskatchewan non-refundable tax credits =": line 53 plus line 56,
read by line 63 on the tax form."""

SK428_SASKATCHEWAN_TAX_LINE_82 = AmountKind.declare(
    CATALOG, "sk428_saskatchewan_tax_line_82", non_negative=True
)
"""Saskatchewan tax, SK428 line 82 "Enter this amount on line 42800 of your return.": the
Saskatchewan tax, entered on T1 line 42800."""

BASIC_PERSONAL_AMOUNT = AmountKind.declare(CATALOG, "basic_personal_amount", non_negative=True)
"""Basic personal amount, SK428 line 9 and line 58040 "Basic personal amount Claim $19,491": the
amount claimed, one of the credit amounts that the Saskatchewan non-refundable credits total is
built from."""

SK428_CPP_CONTRIBUTIONS_LINE_22 = AmountKind.declare(
    CATALOG, "sk428_cpp_contributions_line_22", non_negative=True
)
"""CPP or QPP contributions, SK428 line 22 and line 58240 "Amount from line 30800 of your return": a
copy of Schedule 8 line 25, the CPP base contributions on the return."""

SK428_FARM_CAPITAL_GAINS_CREDIT_LINE_59 = AmountKind.declare(
    CATALOG, "sk428_farm_capital_gains_credit_line_59", non_negative=True
)
"""Saskatchewan farm and small business capital gains tax credit, SK428 line 59 (line 61499) "Line
59 and line 61499: Saskatchewan farm and small business capital gains tax credit (complete Form
T1237)": a caller input, read as blank when left out; line 60 reads it."""

SK428_TAX_ON_SPLIT_INCOME_LINE_61 = AmountKind.declare(CATALOG, "sk428_tax_on_split_income_line_61")
"""Saskatchewan tax on split income, SK428 line 61 (line 61510) "Line 61 and line 61510:
Saskatchewan tax on split income (complete Form T1206)": a caller input, read as blank when left
out."""

SK428_DIVIDEND_TAX_CREDIT_LINE_64 = AmountKind.declare(
    CATALOG, "sk428_dividend_tax_credit_line_64", non_negative=True
)
"""Saskatchewan dividend tax credit, SK428 line 64 (line 61520) "Line 64 and line 61520:
Saskatchewan dividend tax credit (use Worksheet SK428)": a caller input, read as blank when left
out."""

SK428_MINIMUM_TAX_CARRYOVER_AMOUNT_LINE_65 = AmountKind.declare(
    CATALOG, "sk428_minimum_tax_carryover_amount_line_65", non_negative=True
)
"""Saskatchewan minimum tax carryover amount, SK428 line 65 (line 61540) "Amount from line 40427
of your return": the amount from line 40427 of the T1 return, an optional input, box A of the line,
read as blank when left out."""

SK428_MINIMUM_TAX_T691_AMOUNT_LINE_68 = AmountKind.declare(
    CATALOG, "sk428_minimum_tax_t691_amount_line_68"
)
"""Saskatchewan additional tax for minimum tax purposes, SK428 line 68 "Line 68: Form T691: Line 1
minus Line 2 of Part 7 multiplied by 50%": the amount from Form T691, an optional input that a
salary-only caller leaves out. The 50% multiply is a separate step."""
