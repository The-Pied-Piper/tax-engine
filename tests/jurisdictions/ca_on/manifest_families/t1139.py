"""The CA-ON manifest entries of Form T1139 "Reconciliation of 2025 Business Income for Tax
Purposes" (see `test_manifest_t1139.py`).

Two forms. The row form `ca/t1139` is Parts 2 to 5 for one business, run once for each record of
its list `ca/t1139_businesses`: amounts A, H and I (the net income, line 9946, of the statements the
record names), the formulas of amounts B, C and 3H, amounts D, E and G, lines J and L, and the
amount to report and the net income of the statements it takes the place of, on the line of the
business. The summary form `ca/t1139_return` runs once: for each of the lines 13500, 13700, 13900,
14100 and 14300 it takes the statements' net income, leaves out what a Form T1139 takes the place of
and adds what the forms report. T1 reads each line as
`ca/t1139_return.t1139_<line>_income_on_return` (see `03_income.yaml` and the copies of those
steps).

The return selects none of the steps of the forms and declares no output for them, as for Form T746.
"""

from __future__ import annotations

from tax_engine.domain.capabilities.choose_by_count import ChooseByCount
from tax_engine.domain.capabilities.lesser_of import LesserOf
from tax_engine.domain.capabilities.record_positive_total import RecordPositiveTotal
from tax_engine.domain.capabilities.record_total import RecordTotal
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_engine.domain.capabilities.times_count import TimesCount
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.capabilities.apply_ratio_or_zero import ApplyRatioOrZero
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.capabilities.count_refused_by_conditions import (
    CountRefusedByConditions,
)
from tax_engine.jurisdictions.ca.capabilities.statement_amounts_total import (
    StatementAmountsTotal,
)
from tax_engine.jurisdictions.ca.capabilities.statement_profits_total import (
    StatementProfitsTotal,
)
from tax_engine.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_engine.jurisdictions.ca.catalog import (
    FARMING_INCOME,
    FISHING_INCOME,
    NET_ON_BUSINESS_LINE,
    NET_ON_COMMISSION_LINE,
    NET_ON_PROFESSIONAL_LINE,
    T1139_A_STATEMENTS,
    T1139_AMOUNT_2A,
    T1139_AMOUNT_2B,
    T1139_AMOUNT_2C,
    T1139_AMOUNT_2D,
    T1139_AMOUNT_2E,
    T1139_AMOUNT_2F,
    T1139_AMOUNT_2H,
    T1139_AMOUNT_2I,
    T1139_AMOUNT_2J,
    T1139_AMOUNT_2K,
    T1139_AMOUNT_2L,
    T1139_AMOUNT_2M,
    T1139_AMOUNT_2N,
    T1139_AMOUNT_3A,
    T1139_AMOUNT_3B,
    T1139_AMOUNT_3C,
    T1139_AMOUNT_3D,
    T1139_AMOUNT_3E,
    T1139_AMOUNT_3F,
    T1139_AMOUNT_3H,
    T1139_AMOUNT_3H_CHOSEN,
    T1139_AMOUNT_A,
    T1139_AMOUNT_B,
    T1139_AMOUNT_B_CHOSEN,
    T1139_AMOUNT_C,
    T1139_AMOUNT_C_CHOSEN,
    T1139_AMOUNT_D,
    T1139_AMOUNT_E,
    T1139_AMOUNT_G,
    T1139_AMOUNT_H,
    T1139_AMOUNT_I,
    T1139_AMOUNT_J,
    T1139_AMOUNT_L,
    T1139_BUSINESS_INCOME_ON_RETURN,
    T1139_BUSINESS_PROFIT_ON_RETURN,
    T1139_CANCELLING_ELECTION,
    T1139_CANCELLING_ELECTION_CHECKED,
    T1139_COMMISSION_INCOME_ON_RETURN,
    T1139_COMMISSION_PROFIT_ON_RETURN,
    T1139_DESIGNATED_AMOUNT,
    T1139_DESIGNATED_OR_FORMULA_AMOUNT,
    T1139_DESIGNATES_AMOUNT,
    T1139_DESIGNATES_AMOUNT_CHECKED,
    T1139_FARMING_INCOME_ON_RETURN,
    T1139_FARMING_PROFIT_ON_RETURN,
    T1139_FISHING_INCOME_ON_RETURN,
    T1139_FISHING_PROFIT_ON_RETURN,
    T1139_FORMULA,
    T1139_FORMULA_AMOUNT_FOR_C,
    T1139_FORMULA_CHECKED,
    T1139_FORMULA_IS_3H,
    T1139_FORMULA_IS_B,
    T1139_FORMULA_IS_C,
    T1139_H_STATEMENTS,
    T1139_I_STATEMENTS,
    T1139_KEPT_ON_BUSINESS_LINE,
    T1139_KEPT_ON_COMMISSION_LINE,
    T1139_KEPT_ON_FARMING_LINE,
    T1139_KEPT_ON_FISHING_LINE,
    T1139_KEPT_ON_PROFESSIONAL_LINE,
    T1139_KEPT_PROFITS_ON_BUSINESS_LINE,
    T1139_KEPT_PROFITS_ON_COMMISSION_LINE,
    T1139_KEPT_PROFITS_ON_FARMING_LINE,
    T1139_KEPT_PROFITS_ON_FISHING_LINE,
    T1139_KEPT_PROFITS_ON_PROFESSIONAL_LINE,
    T1139_LAST_YEARS_ADDITIONAL_INCOME,
    T1139_LINE,
    T1139_LINE_CHECKED,
    T1139_NET_INCOME_REPLACED,
    T1139_NET_INCOME_REPORTED,
    T1139_ON_BUSINESS_LINE,
    T1139_ON_COMMISSION_LINE,
    T1139_ON_FARMING_LINE,
    T1139_ON_FISHING_LINE,
    T1139_ON_PROFESSIONAL_LINE,
    T1139_PROFESSIONAL_INCOME_ON_RETURN,
    T1139_PROFESSIONAL_PROFIT_ON_RETURN,
    T1139_PROFIT_A,
    T1139_PROFIT_H,
    T1139_PROFIT_HI,
    T1139_PROFIT_I,
    T1139_PROFIT_REPLACED,
    T1139_PROFIT_REPLACED_ON_BUSINESS_LINE,
    T1139_PROFIT_REPLACED_ON_COMMISSION_LINE,
    T1139_PROFIT_REPLACED_ON_FARMING_LINE,
    T1139_PROFIT_REPLACED_ON_FISHING_LINE,
    T1139_PROFIT_REPLACED_ON_PROFESSIONAL_LINE,
    T1139_REPLACED_ON_BUSINESS_LINE,
    T1139_REPLACED_ON_COMMISSION_LINE,
    T1139_REPLACED_ON_FARMING_LINE,
    T1139_REPLACED_ON_FISHING_LINE,
    T1139_REPLACED_ON_PROFESSIONAL_LINE,
    T1139_REPLACED_PROFITS_TOTAL_ON_BUSINESS_LINE,
    T1139_REPLACED_PROFITS_TOTAL_ON_COMMISSION_LINE,
    T1139_REPLACED_PROFITS_TOTAL_ON_FARMING_LINE,
    T1139_REPLACED_PROFITS_TOTAL_ON_FISHING_LINE,
    T1139_REPLACED_PROFITS_TOTAL_ON_PROFESSIONAL_LINE,
    T1139_REPLACED_TOTAL_ON_BUSINESS_LINE,
    T1139_REPLACED_TOTAL_ON_COMMISSION_LINE,
    T1139_REPLACED_TOTAL_ON_FARMING_LINE,
    T1139_REPLACED_TOTAL_ON_FISHING_LINE,
    T1139_REPLACED_TOTAL_ON_PROFESSIONAL_LINE,
    T1139_REPORTED_ON_BUSINESS_LINE,
    T1139_REPORTED_ON_COMMISSION_LINE,
    T1139_REPORTED_ON_FARMING_LINE,
    T1139_REPORTED_ON_FISHING_LINE,
    T1139_REPORTED_ON_PROFESSIONAL_LINE,
    T1139_REPORTED_PROFITS_TOTAL_ON_BUSINESS_LINE,
    T1139_REPORTED_PROFITS_TOTAL_ON_COMMISSION_LINE,
    T1139_REPORTED_PROFITS_TOTAL_ON_FARMING_LINE,
    T1139_REPORTED_PROFITS_TOTAL_ON_FISHING_LINE,
    T1139_REPORTED_PROFITS_TOTAL_ON_PROFESSIONAL_LINE,
    T1139_REPORTED_TOTAL_ON_BUSINESS_LINE,
    T1139_REPORTED_TOTAL_ON_COMMISSION_LINE,
    T1139_REPORTED_TOTAL_ON_FARMING_LINE,
    T1139_REPORTED_TOTAL_ON_FISHING_LINE,
    T1139_REPORTED_TOTAL_ON_PROFESSIONAL_LINE,
    T1139_STATEMENT_PROFITS_ON_BUSINESS_LINE,
    T1139_STATEMENT_PROFITS_ON_COMMISSION_LINE,
    T1139_STATEMENT_PROFITS_ON_FARMING_LINE,
    T1139_STATEMENT_PROFITS_ON_FISHING_LINE,
    T1139_STATEMENT_PROFITS_ON_PROFESSIONAL_LINE,
    T1139_STATEMENTS_ON_BUSINESS_LINE,
    T1139_STATEMENTS_ON_COMMISSION_LINE,
    T1139_STATEMENTS_ON_FARMING_LINE,
    T1139_STATEMENTS_ON_FISHING_LINE,
    T1139_STATEMENTS_ON_PROFESSIONAL_LINE,
)

ROW_FORM = "ca/t1139"
SUMMARY_FORM = "ca/t1139_return"
BUSINESSES_LIST = "ca/t1139_businesses"

# The starting input of the forms: the list of the businesses the row form runs over.
INPUTS = frozenset({BUSINESSES_LIST})

ROW_EXPORTS = frozenset(
    {
        "ca/t1139_replaced_on_business_line",
        "ca/t1139_replaced_on_commission_line",
        "ca/t1139_replaced_on_farming_line",
        "ca/t1139_replaced_on_fishing_line",
        "ca/t1139_replaced_on_professional_line",
        "ca/t1139_profit_replaced_on_business_line",
        "ca/t1139_profit_replaced_on_professional_line",
        "ca/t1139_profit_replaced_on_commission_line",
        "ca/t1139_profit_replaced_on_farming_line",
        "ca/t1139_profit_replaced_on_fishing_line",
        "ca/t1139_reported_on_business_line",
        "ca/t1139_reported_on_commission_line",
        "ca/t1139_reported_on_farming_line",
        "ca/t1139_reported_on_fishing_line",
        "ca/t1139_reported_on_professional_line",
    }
)
SUMMARY_EXPORTS = frozenset(
    {
        "ca/t1139_business_income_on_return",
        "ca/t1139_commission_income_on_return",
        "ca/t1139_farming_income_on_return",
        "ca/t1139_fishing_income_on_return",
        "ca/t1139_professional_income_on_return",
        "ca/t1139_business_profit_on_return",
        "ca/t1139_professional_profit_on_return",
        "ca/t1139_commission_profit_on_return",
        "ca/t1139_farming_profit_on_return",
        "ca/t1139_fishing_profit_on_return",
    }
)

# The return selects no step of the forms and reads no output of them in this family.
OUTPUTS: frozenset[str] = frozenset()
STEPS: set[CapabilitySelection] = set()
WIRING: set[object] = set()

# The statements' lists the forms read: the net income, line 9946, of each statement of Forms T2125
# (by the line of its code), T2042 and T2121, and the return's farming lines.
T2125_NET_ON_BUSINESS_LINES = RecordListKind(
    "ca/t2125.net_on_business_line", fields=(NET_ON_BUSINESS_LINE,)
)
T2125_NET_ON_PROFESSIONAL_LINES = RecordListKind(
    "ca/t2125.net_on_professional_line", fields=(NET_ON_PROFESSIONAL_LINE,)
)
T2125_NET_ON_COMMISSION_LINES = RecordListKind(
    "ca/t2125.net_on_commission_line", fields=(NET_ON_COMMISSION_LINE,)
)
T2042_FARMING_INCOME_LINES = RecordListKind("ca/t2042.farming_income", fields=(FARMING_INCOME,))
T2121_FISHING_INCOME_LINES = RecordListKind("ca/t2121.fishing_income", fields=(FISHING_INCOME,))
FARM_LOSS_FARMING_INCOME_LINES = RecordListKind(
    "ca/farm_loss.farming_income", fields=(FARMING_INCOME,)
)
# The lists T1 totals for lines 13500 to 14300: the exports of the summary form.
BUSINESS_INCOME_ON_RETURN_LINES = RecordListKind(
    "ca/t1139_return.t1139_business_income_on_return", fields=(T1139_BUSINESS_INCOME_ON_RETURN,)
)
PROFESSIONAL_INCOME_ON_RETURN_LINES = RecordListKind(
    "ca/t1139_return.t1139_professional_income_on_return",
    fields=(T1139_PROFESSIONAL_INCOME_ON_RETURN,),
)
COMMISSION_INCOME_ON_RETURN_LINES = RecordListKind(
    "ca/t1139_return.t1139_commission_income_on_return", fields=(T1139_COMMISSION_INCOME_ON_RETURN,)
)
FARMING_INCOME_ON_RETURN_LINES = RecordListKind(
    "ca/t1139_return.t1139_farming_income_on_return", fields=(T1139_FARMING_INCOME_ON_RETURN,)
)
FISHING_INCOME_ON_RETURN_LINES = RecordListKind(
    "ca/t1139_return.t1139_fishing_income_on_return", fields=(T1139_FISHING_INCOME_ON_RETURN,)
)
# The profit of each business on each self-employment line of the return, from Form T1139's summary
# form (`ca/t1139_return`): a Form T1139 counts its amount G or L and each statement counts alone, a
# loss counting 0, so the readers take "use only the profit amounts" of each business. Each is a
# record list of one amount field, as the summary form exports it.
BUSINESS_PROFIT_ON_RETURN_LINES = RecordListKind(
    "ca/t1139_return.t1139_business_profit_on_return", fields=(T1139_BUSINESS_PROFIT_ON_RETURN,)
)
PROFESSIONAL_PROFIT_ON_RETURN_LINES = RecordListKind(
    "ca/t1139_return.t1139_professional_profit_on_return",
    fields=(T1139_PROFESSIONAL_PROFIT_ON_RETURN,),
)
COMMISSION_PROFIT_ON_RETURN_LINES = RecordListKind(
    "ca/t1139_return.t1139_commission_profit_on_return", fields=(T1139_COMMISSION_PROFIT_ON_RETURN,)
)
FARMING_PROFIT_ON_RETURN_LINES = RecordListKind(
    "ca/t1139_return.t1139_farming_profit_on_return", fields=(T1139_FARMING_PROFIT_ON_RETURN,)
)
FISHING_PROFIT_ON_RETURN_LINES = RecordListKind(
    "ca/t1139_return.t1139_fishing_profit_on_return", fields=(T1139_FISHING_PROFIT_ON_RETURN,)
)
LIST_T1139_REPLACED_ON_BUSINESS_LINE = RecordListKind(
    "ca/t1139.t1139_replaced_on_business_line", fields=(T1139_REPLACED_ON_BUSINESS_LINE,)
)
LIST_T1139_REPLACED_ON_COMMISSION_LINE = RecordListKind(
    "ca/t1139.t1139_replaced_on_commission_line", fields=(T1139_REPLACED_ON_COMMISSION_LINE,)
)
LIST_T1139_REPLACED_ON_FARMING_LINE = RecordListKind(
    "ca/t1139.t1139_replaced_on_farming_line", fields=(T1139_REPLACED_ON_FARMING_LINE,)
)
LIST_T1139_REPLACED_ON_FISHING_LINE = RecordListKind(
    "ca/t1139.t1139_replaced_on_fishing_line", fields=(T1139_REPLACED_ON_FISHING_LINE,)
)
LIST_T1139_REPLACED_ON_PROFESSIONAL_LINE = RecordListKind(
    "ca/t1139.t1139_replaced_on_professional_line", fields=(T1139_REPLACED_ON_PROFESSIONAL_LINE,)
)
LIST_T1139_REPORTED_ON_BUSINESS_LINE = RecordListKind(
    "ca/t1139.t1139_reported_on_business_line", fields=(T1139_REPORTED_ON_BUSINESS_LINE,)
)
LIST_T1139_REPORTED_ON_COMMISSION_LINE = RecordListKind(
    "ca/t1139.t1139_reported_on_commission_line", fields=(T1139_REPORTED_ON_COMMISSION_LINE,)
)
LIST_T1139_REPORTED_ON_FARMING_LINE = RecordListKind(
    "ca/t1139.t1139_reported_on_farming_line", fields=(T1139_REPORTED_ON_FARMING_LINE,)
)
LIST_T1139_REPORTED_ON_FISHING_LINE = RecordListKind(
    "ca/t1139.t1139_reported_on_fishing_line", fields=(T1139_REPORTED_ON_FISHING_LINE,)
)
LIST_T1139_REPORTED_ON_PROFESSIONAL_LINE = RecordListKind(
    "ca/t1139.t1139_reported_on_professional_line", fields=(T1139_REPORTED_ON_PROFESSIONAL_LINE,)
)

LIST_T1139_PROFIT_REPLACED_ON_BUSINESS_LINE = RecordListKind(
    "ca/t1139.t1139_profit_replaced_on_business_line",
    fields=(T1139_PROFIT_REPLACED_ON_BUSINESS_LINE,),
)
LIST_T1139_PROFIT_REPLACED_ON_PROFESSIONAL_LINE = RecordListKind(
    "ca/t1139.t1139_profit_replaced_on_professional_line",
    fields=(T1139_PROFIT_REPLACED_ON_PROFESSIONAL_LINE,),
)
LIST_T1139_PROFIT_REPLACED_ON_COMMISSION_LINE = RecordListKind(
    "ca/t1139.t1139_profit_replaced_on_commission_line",
    fields=(T1139_PROFIT_REPLACED_ON_COMMISSION_LINE,),
)
LIST_T1139_PROFIT_REPLACED_ON_FARMING_LINE = RecordListKind(
    "ca/t1139.t1139_profit_replaced_on_farming_line",
    fields=(T1139_PROFIT_REPLACED_ON_FARMING_LINE,),
)
LIST_T1139_PROFIT_REPLACED_ON_FISHING_LINE = RecordListKind(
    "ca/t1139.t1139_profit_replaced_on_fishing_line",
    fields=(T1139_PROFIT_REPLACED_ON_FISHING_LINE,),
)

ROW_STEPS = {
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t1139_cancelling_election"},
        produces={"output": "ca/t1139_cancelling_election_checked"},
    ),
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/t1139_designates_amount"},
        produces={"output": "ca/t1139_designates_amount_checked"},
    ),
    # Part 4 "Report amount G ... For business income, enter it at line 13500": a line number that
    # is none of 1 to 5 names no line and is refused.
    CapabilitySelection(
        name="ca/count_refused_by_conditions",
        params={"conditions": "ca/t1139_line_refused"},
        consumes={"count": "ca/t1139_line"},
        produces={"output": "ca/t1139_line_checked"},
    ),
    # Part 2 "Use only one of the formulas below": the formula used is the filer's choice, 0 to 3.
    CapabilitySelection(
        name="ca/count_refused_by_conditions",
        params={"conditions": "ca/t1139_formula_refused"},
        consumes={"count": "ca/t1139_formula"},
        produces={"output": "ca/t1139_formula_checked"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t1139_line_is_business"},
        consumes={"counts": ("ca/t1139_line_checked",), "amounts": ()},
        produces={"output": "ca/t1139_on_business_line"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t1139_line_is_professional"},
        consumes={"counts": ("ca/t1139_line_checked",), "amounts": ()},
        produces={"output": "ca/t1139_on_professional_line"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t1139_line_is_commission"},
        consumes={"counts": ("ca/t1139_line_checked",), "amounts": ()},
        produces={"output": "ca/t1139_on_commission_line"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t1139_line_is_farming"},
        consumes={"counts": ("ca/t1139_line_checked",), "amounts": ()},
        produces={"output": "ca/t1139_on_farming_line"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t1139_line_is_fishing"},
        consumes={"counts": ("ca/t1139_line_checked",), "amounts": ()},
        produces={"output": "ca/t1139_on_fishing_line"},
    ),
    CapabilitySelection(
        name="ca/statement_amounts_total",
        params={},
        consumes={
            "records": (
                "ca/t2125.net_on_business_line",
                "ca/t2125.net_on_professional_line",
                "ca/t2125.net_on_commission_line",
                "ca/t2042.farming_income",
                "ca/t2121.fishing_income",
            ),
            "line": "ca/t1139_line_checked",
            "positions": "ca/t1139_a_statements",
        },
        produces={"total": "ca/t1139_amount_a"},
    ),
    CapabilitySelection(
        name="ca/statement_amounts_total",
        params={},
        consumes={
            "records": (
                "ca/t2125.net_on_business_line",
                "ca/t2125.net_on_professional_line",
                "ca/t2125.net_on_commission_line",
                "ca/t2042.farming_income",
                "ca/t2121.fishing_income",
            ),
            "line": "ca/t1139_line_checked",
            "positions": "ca/t1139_h_statements",
        },
        produces={"total": "ca/t1139_amount_h"},
    ),
    CapabilitySelection(
        name="ca/statement_amounts_total",
        params={},
        consumes={
            "records": (
                "ca/t2125.net_on_business_line",
                "ca/t2125.net_on_professional_line",
                "ca/t2125.net_on_commission_line",
                "ca/t2042.farming_income",
                "ca/t2121.fishing_income",
            ),
            "line": "ca/t1139_line_checked",
            "positions": "ca/t1139_i_statements",
        },
        produces={"total": "ca/t1139_amount_i"},
    ),
    CapabilitySelection(
        name="ca/statement_profits_total",
        params={},
        consumes={
            "records": (
                "ca/t2125.net_on_business_line",
                "ca/t2125.net_on_professional_line",
                "ca/t2125.net_on_commission_line",
                "ca/t2042.farming_income",
                "ca/t2121.fishing_income",
            ),
            "line": "ca/t1139_line_checked",
            "positions": "ca/t1139_a_statements",
        },
        produces={"total": "ca/t1139_profit_a"},
    ),
    CapabilitySelection(
        name="ca/statement_profits_total",
        params={},
        consumes={
            "records": (
                "ca/t2125.net_on_business_line",
                "ca/t2125.net_on_professional_line",
                "ca/t2125.net_on_commission_line",
                "ca/t2042.farming_income",
                "ca/t2121.fishing_income",
            ),
            "line": "ca/t1139_line_checked",
            "positions": "ca/t1139_h_statements",
        },
        produces={"total": "ca/t1139_profit_h"},
    ),
    CapabilitySelection(
        name="ca/statement_profits_total",
        params={},
        consumes={
            "records": (
                "ca/t2125.net_on_business_line",
                "ca/t2125.net_on_professional_line",
                "ca/t2125.net_on_commission_line",
                "ca/t2042.farming_income",
                "ca/t2121.fishing_income",
            ),
            "line": "ca/t1139_line_checked",
            "positions": "ca/t1139_i_statements",
        },
        produces={"total": "ca/t1139_profit_i"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/t1139_amount_2a", "ca/t1139_amount_2b")},
        produces={"output": "ca/t1139_amount_2c"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/t1139_amount_a", "less": "ca/t1139_amount_2c"},
        produces={"output": "ca/t1139_amount_2d"},
    ),
    CapabilitySelection(
        name="ca/apply_ratio_or_zero",
        params={"rounding": "ca/t1139_rounding"},
        consumes={
            "amount": "ca/t1139_amount_2d",
            "numerator": "ca/t1139_amount_2e",
            "denominator": "ca/t1139_amount_2f",
        },
        produces={"output": "ca/t1139_amount_b"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/t1139_amount_2i", "ca/t1139_amount_2j")},
        produces={"output": "ca/t1139_amount_2k"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/t1139_amount_2h", "less": "ca/t1139_amount_2k"},
        produces={"output": "ca/t1139_amount_2l"},
    ),
    CapabilitySelection(
        name="ca/apply_ratio_or_zero",
        params={"rounding": "ca/t1139_rounding"},
        consumes={
            "amount": "ca/t1139_amount_2l",
            "numerator": "ca/t1139_amount_2m",
            "denominator": "ca/t1139_amount_2n",
        },
        produces={"output": "ca/t1139_formula_amount_for_c"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/t1139_designated_amount", "ca/t1139_formula_amount_for_c")},
        produces={"output": "ca/t1139_designated_or_formula_amount"},
    ),
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t1139_designates_amount_checked",
            "when_none": "ca/t1139_formula_amount_for_c",
            "when_any": "ca/t1139_designated_or_formula_amount",
        },
        produces={"output": "ca/t1139_amount_c"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/t1139_amount_3a", "ca/t1139_amount_3b")},
        produces={"output": "ca/t1139_amount_3c"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/t1139_amount_a", "less": "ca/t1139_amount_3c"},
        produces={"output": "ca/t1139_amount_3d"},
    ),
    CapabilitySelection(
        name="ca/apply_ratio_or_zero",
        params={"rounding": "ca/t1139_rounding"},
        consumes={
            "amount": "ca/t1139_amount_3d",
            "numerator": "ca/t1139_amount_3e",
            "denominator": "ca/t1139_amount_3f",
        },
        produces={"output": "ca/t1139_amount_3h"},
    ),
    # Part 4 "Enter either amount B, C, or 3H based on the formula you used above": amount
    # B when that is the formula used, 0 for the others.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t1139_formula_is_b"},
        consumes={"counts": ("ca/t1139_formula_checked",), "amounts": ()},
        produces={"output": "ca/t1139_formula_is_b"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t1139_amount_b", "count": "ca/t1139_formula_is_b"},
        produces={"output": "ca/t1139_amount_b_chosen"},
    ),
    # Part 4 "Enter either amount B, C, or 3H based on the formula you used above": amount
    # C when that is the formula used, 0 for the others.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t1139_formula_is_c"},
        consumes={"counts": ("ca/t1139_formula_checked",), "amounts": ()},
        produces={"output": "ca/t1139_formula_is_c"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t1139_amount_c", "count": "ca/t1139_formula_is_c"},
        produces={"output": "ca/t1139_amount_c_chosen"},
    ),
    # Part 4 "Enter either amount B, C, or 3H based on the formula you used above": amount
    # 3H when that is the formula used, 0 for the others.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/t1139_formula_is_3h"},
        consumes={"counts": ("ca/t1139_formula_checked",), "amounts": ()},
        produces={"output": "ca/t1139_formula_is_3h"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t1139_amount_3h", "count": "ca/t1139_formula_is_3h"},
        produces={"output": "ca/t1139_amount_3h_chosen"},
    ),
    # Part 4 amount D, at least 0 (Part 2: "if the amount you calculate is negative, the CRA
    # considers it to be zero").
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/t1139_amount_b_chosen",
                "ca/t1139_amount_c_chosen",
                "ca/t1139_amount_3h_chosen",
            )
        },
        produces={"output": "ca/t1139_amount_d"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t1139_amount_a", "ca/t1139_amount_d")},
        produces={"output": "ca/t1139_amount_e"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/t1139_amount_e", "less": "ca/t1139_last_years_additional_income"},
        produces={"output": "ca/t1139_amount_g"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t1139_amount_h", "ca/t1139_amount_i")},
        produces={"output": "ca/t1139_amount_j"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/t1139_amount_j", "less": "ca/t1139_last_years_additional_income"},
        produces={"output": "ca/t1139_amount_l"},
    ),
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t1139_cancelling_election_checked",
            "when_none": "ca/t1139_amount_g",
            "when_any": "ca/t1139_amount_l",
        },
        produces={"output": "ca/t1139_net_income_reported"},
    ),
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t1139_cancelling_election_checked",
            "when_none": "ca/t1139_amount_a",
            "when_any": "ca/t1139_amount_j",
        },
        produces={"output": "ca/t1139_net_income_replaced"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t1139_profit_h", "ca/t1139_profit_i")},
        produces={"output": "ca/t1139_profit_hi"},
    ),
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/t1139_cancelling_election_checked",
            "when_none": "ca/t1139_profit_a",
            "when_any": "ca/t1139_profit_hi",
        },
        produces={"output": "ca/t1139_profit_replaced"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t1139_net_income_reported", "count": "ca/t1139_on_business_line"},
        produces={"output": "ca/t1139_reported_on_business_line"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t1139_net_income_reported",
            "count": "ca/t1139_on_professional_line",
        },
        produces={"output": "ca/t1139_reported_on_professional_line"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t1139_net_income_reported", "count": "ca/t1139_on_commission_line"},
        produces={"output": "ca/t1139_reported_on_commission_line"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t1139_net_income_reported", "count": "ca/t1139_on_farming_line"},
        produces={"output": "ca/t1139_reported_on_farming_line"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t1139_net_income_reported", "count": "ca/t1139_on_fishing_line"},
        produces={"output": "ca/t1139_reported_on_fishing_line"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t1139_net_income_replaced", "count": "ca/t1139_on_business_line"},
        produces={"output": "ca/t1139_replaced_on_business_line"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t1139_net_income_replaced",
            "count": "ca/t1139_on_professional_line",
        },
        produces={"output": "ca/t1139_replaced_on_professional_line"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t1139_net_income_replaced", "count": "ca/t1139_on_commission_line"},
        produces={"output": "ca/t1139_replaced_on_commission_line"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t1139_net_income_replaced", "count": "ca/t1139_on_farming_line"},
        produces={"output": "ca/t1139_replaced_on_farming_line"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t1139_net_income_replaced", "count": "ca/t1139_on_fishing_line"},
        produces={"output": "ca/t1139_replaced_on_fishing_line"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t1139_profit_replaced", "count": "ca/t1139_on_business_line"},
        produces={"output": "ca/t1139_profit_replaced_on_business_line"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t1139_profit_replaced", "count": "ca/t1139_on_professional_line"},
        produces={"output": "ca/t1139_profit_replaced_on_professional_line"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t1139_profit_replaced", "count": "ca/t1139_on_commission_line"},
        produces={"output": "ca/t1139_profit_replaced_on_commission_line"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t1139_profit_replaced", "count": "ca/t1139_on_farming_line"},
        produces={"output": "ca/t1139_profit_replaced_on_farming_line"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t1139_profit_replaced", "count": "ca/t1139_on_fishing_line"},
        produces={"output": "ca/t1139_profit_replaced_on_fishing_line"},
    ),
}

SUMMARY_STEPS = {
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2125.net_on_business_line"},
        produces={"output": "ca/t1139_statements_on_business_line"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139.t1139_replaced_on_business_line"},
        produces={"output": "ca/t1139_replaced_total_on_business_line"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139.t1139_reported_on_business_line"},
        produces={"output": "ca/t1139_reported_total_on_business_line"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t1139_statements_on_business_line",
            "less": "ca/t1139_replaced_total_on_business_line",
        },
        produces={"output": "ca/t1139_kept_on_business_line"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": ("ca/t1139_kept_on_business_line", "ca/t1139_reported_total_on_business_line")
        },
        produces={"output": "ca/t1139_business_income_on_return"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2125.net_on_professional_line"},
        produces={"output": "ca/t1139_statements_on_professional_line"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139.t1139_replaced_on_professional_line"},
        produces={"output": "ca/t1139_replaced_total_on_professional_line"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139.t1139_reported_on_professional_line"},
        produces={"output": "ca/t1139_reported_total_on_professional_line"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t1139_statements_on_professional_line",
            "less": "ca/t1139_replaced_total_on_professional_line",
        },
        produces={"output": "ca/t1139_kept_on_professional_line"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t1139_kept_on_professional_line",
                "ca/t1139_reported_total_on_professional_line",
            )
        },
        produces={"output": "ca/t1139_professional_income_on_return"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2125.net_on_commission_line"},
        produces={"output": "ca/t1139_statements_on_commission_line"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139.t1139_replaced_on_commission_line"},
        produces={"output": "ca/t1139_replaced_total_on_commission_line"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139.t1139_reported_on_commission_line"},
        produces={"output": "ca/t1139_reported_total_on_commission_line"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t1139_statements_on_commission_line",
            "less": "ca/t1139_replaced_total_on_commission_line",
        },
        produces={"output": "ca/t1139_kept_on_commission_line"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t1139_kept_on_commission_line",
                "ca/t1139_reported_total_on_commission_line",
            )
        },
        produces={"output": "ca/t1139_commission_income_on_return"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/farm_loss.farming_income"},
        produces={"output": "ca/t1139_statements_on_farming_line"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139.t1139_replaced_on_farming_line"},
        produces={"output": "ca/t1139_replaced_total_on_farming_line"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139.t1139_reported_on_farming_line"},
        produces={"output": "ca/t1139_reported_total_on_farming_line"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t1139_statements_on_farming_line",
            "less": "ca/t1139_replaced_total_on_farming_line",
        },
        produces={"output": "ca/t1139_kept_on_farming_line"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": ("ca/t1139_kept_on_farming_line", "ca/t1139_reported_total_on_farming_line")
        },
        produces={"output": "ca/t1139_farming_income_on_return"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2121.fishing_income"},
        produces={"output": "ca/t1139_statements_on_fishing_line"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139.t1139_replaced_on_fishing_line"},
        produces={"output": "ca/t1139_replaced_total_on_fishing_line"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139.t1139_reported_on_fishing_line"},
        produces={"output": "ca/t1139_reported_total_on_fishing_line"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t1139_statements_on_fishing_line",
            "less": "ca/t1139_replaced_total_on_fishing_line",
        },
        produces={"output": "ca/t1139_kept_on_fishing_line"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": ("ca/t1139_kept_on_fishing_line", "ca/t1139_reported_total_on_fishing_line")
        },
        produces={"output": "ca/t1139_fishing_income_on_return"},
    ),
    CapabilitySelection(
        name="core/record_positive_total",
        params={},
        consumes={"records": "ca/t2125.net_on_business_line"},
        produces={"output": "ca/t1139_statement_profits_on_business_line"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139.t1139_profit_replaced_on_business_line"},
        produces={"output": "ca/t1139_replaced_profits_total_on_business_line"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t1139_statement_profits_on_business_line",
            "less": "ca/t1139_replaced_profits_total_on_business_line",
        },
        produces={"output": "ca/t1139_kept_profits_on_business_line"},
    ),
    CapabilitySelection(
        name="core/record_positive_total",
        params={},
        consumes={"records": "ca/t1139.t1139_reported_on_business_line"},
        produces={"output": "ca/t1139_reported_profits_total_on_business_line"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t1139_kept_profits_on_business_line",
                "ca/t1139_reported_profits_total_on_business_line",
            )
        },
        produces={"output": "ca/t1139_business_profit_on_return"},
    ),
    CapabilitySelection(
        name="core/record_positive_total",
        params={},
        consumes={"records": "ca/t2125.net_on_professional_line"},
        produces={"output": "ca/t1139_statement_profits_on_professional_line"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139.t1139_profit_replaced_on_professional_line"},
        produces={"output": "ca/t1139_replaced_profits_total_on_professional_line"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t1139_statement_profits_on_professional_line",
            "less": "ca/t1139_replaced_profits_total_on_professional_line",
        },
        produces={"output": "ca/t1139_kept_profits_on_professional_line"},
    ),
    CapabilitySelection(
        name="core/record_positive_total",
        params={},
        consumes={"records": "ca/t1139.t1139_reported_on_professional_line"},
        produces={"output": "ca/t1139_reported_profits_total_on_professional_line"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t1139_kept_profits_on_professional_line",
                "ca/t1139_reported_profits_total_on_professional_line",
            )
        },
        produces={"output": "ca/t1139_professional_profit_on_return"},
    ),
    CapabilitySelection(
        name="core/record_positive_total",
        params={},
        consumes={"records": "ca/t2125.net_on_commission_line"},
        produces={"output": "ca/t1139_statement_profits_on_commission_line"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139.t1139_profit_replaced_on_commission_line"},
        produces={"output": "ca/t1139_replaced_profits_total_on_commission_line"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t1139_statement_profits_on_commission_line",
            "less": "ca/t1139_replaced_profits_total_on_commission_line",
        },
        produces={"output": "ca/t1139_kept_profits_on_commission_line"},
    ),
    CapabilitySelection(
        name="core/record_positive_total",
        params={},
        consumes={"records": "ca/t1139.t1139_reported_on_commission_line"},
        produces={"output": "ca/t1139_reported_profits_total_on_commission_line"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t1139_kept_profits_on_commission_line",
                "ca/t1139_reported_profits_total_on_commission_line",
            )
        },
        produces={"output": "ca/t1139_commission_profit_on_return"},
    ),
    CapabilitySelection(
        name="core/record_positive_total",
        params={},
        consumes={"records": "ca/t2042.farming_income"},
        produces={"output": "ca/t1139_statement_profits_on_farming_line"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139.t1139_profit_replaced_on_farming_line"},
        produces={"output": "ca/t1139_replaced_profits_total_on_farming_line"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t1139_statement_profits_on_farming_line",
            "less": "ca/t1139_replaced_profits_total_on_farming_line",
        },
        produces={"output": "ca/t1139_kept_profits_on_farming_line"},
    ),
    CapabilitySelection(
        name="core/record_positive_total",
        params={},
        consumes={"records": "ca/t1139.t1139_reported_on_farming_line"},
        produces={"output": "ca/t1139_reported_profits_total_on_farming_line"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t1139_kept_profits_on_farming_line",
                "ca/t1139_reported_profits_total_on_farming_line",
            )
        },
        produces={"output": "ca/t1139_farming_profit_on_return"},
    ),
    CapabilitySelection(
        name="core/record_positive_total",
        params={},
        consumes={"records": "ca/t2121.fishing_income"},
        produces={"output": "ca/t1139_statement_profits_on_fishing_line"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139.t1139_profit_replaced_on_fishing_line"},
        produces={"output": "ca/t1139_replaced_profits_total_on_fishing_line"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t1139_statement_profits_on_fishing_line",
            "less": "ca/t1139_replaced_profits_total_on_fishing_line",
        },
        produces={"output": "ca/t1139_kept_profits_on_fishing_line"},
    ),
    CapabilitySelection(
        name="core/record_positive_total",
        params={},
        consumes={"records": "ca/t1139.t1139_reported_on_fishing_line"},
        produces={"output": "ca/t1139_reported_profits_total_on_fishing_line"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t1139_kept_profits_on_fishing_line",
                "ca/t1139_reported_profits_total_on_fishing_line",
            )
        },
        produces={"output": "ca/t1139_fishing_profit_on_return"},
    ),
}

# The wiring of the steps, as `test_manifest_t1139.py` reads it from the composed forms: the
# capability class, the kinds it consumes and the kinds it produces.
ROW_WIRING = {
    (
        YesOrNoCount,
        frozenset({T1139_CANCELLING_ELECTION}),
        frozenset({T1139_CANCELLING_ELECTION_CHECKED}),
    ),
    (
        YesOrNoCount,
        frozenset({T1139_DESIGNATES_AMOUNT}),
        frozenset({T1139_DESIGNATES_AMOUNT_CHECKED}),
    ),
    (CountRefusedByConditions, frozenset({T1139_LINE}), frozenset({T1139_LINE_CHECKED})),
    (CountRefusedByConditions, frozenset({T1139_FORMULA}), frozenset({T1139_FORMULA_CHECKED})),
    (CountByConditions, frozenset({T1139_LINE_CHECKED}), frozenset({T1139_ON_BUSINESS_LINE})),
    (CountByConditions, frozenset({T1139_LINE_CHECKED}), frozenset({T1139_ON_PROFESSIONAL_LINE})),
    (CountByConditions, frozenset({T1139_LINE_CHECKED}), frozenset({T1139_ON_COMMISSION_LINE})),
    (CountByConditions, frozenset({T1139_LINE_CHECKED}), frozenset({T1139_ON_FARMING_LINE})),
    (CountByConditions, frozenset({T1139_LINE_CHECKED}), frozenset({T1139_ON_FISHING_LINE})),
    (
        StatementAmountsTotal,
        frozenset(
            {
                T2125_NET_ON_BUSINESS_LINES,
                T2125_NET_ON_PROFESSIONAL_LINES,
                T2125_NET_ON_COMMISSION_LINES,
                T2042_FARMING_INCOME_LINES,
                T2121_FISHING_INCOME_LINES,
                T1139_LINE_CHECKED,
                T1139_A_STATEMENTS,
            }
        ),
        frozenset({T1139_AMOUNT_A}),
    ),
    (
        StatementAmountsTotal,
        frozenset(
            {
                T2125_NET_ON_BUSINESS_LINES,
                T2125_NET_ON_PROFESSIONAL_LINES,
                T2125_NET_ON_COMMISSION_LINES,
                T2042_FARMING_INCOME_LINES,
                T2121_FISHING_INCOME_LINES,
                T1139_LINE_CHECKED,
                T1139_H_STATEMENTS,
            }
        ),
        frozenset({T1139_AMOUNT_H}),
    ),
    (
        StatementAmountsTotal,
        frozenset(
            {
                T2125_NET_ON_BUSINESS_LINES,
                T2125_NET_ON_PROFESSIONAL_LINES,
                T2125_NET_ON_COMMISSION_LINES,
                T2042_FARMING_INCOME_LINES,
                T2121_FISHING_INCOME_LINES,
                T1139_LINE_CHECKED,
                T1139_I_STATEMENTS,
            }
        ),
        frozenset({T1139_AMOUNT_I}),
    ),
    (LesserOf, frozenset({T1139_AMOUNT_2A, T1139_AMOUNT_2B}), frozenset({T1139_AMOUNT_2C})),
    (Subtract, frozenset({T1139_AMOUNT_A, T1139_AMOUNT_2C}), frozenset({T1139_AMOUNT_2D})),
    (
        ApplyRatioOrZero,
        frozenset({T1139_AMOUNT_2D, T1139_AMOUNT_2E, T1139_AMOUNT_2F}),
        frozenset({T1139_AMOUNT_B}),
    ),
    (LesserOf, frozenset({T1139_AMOUNT_2I, T1139_AMOUNT_2J}), frozenset({T1139_AMOUNT_2K})),
    (Subtract, frozenset({T1139_AMOUNT_2H, T1139_AMOUNT_2K}), frozenset({T1139_AMOUNT_2L})),
    (
        ApplyRatioOrZero,
        frozenset({T1139_AMOUNT_2L, T1139_AMOUNT_2M, T1139_AMOUNT_2N}),
        frozenset({T1139_FORMULA_AMOUNT_FOR_C}),
    ),
    (
        LesserOf,
        frozenset({T1139_DESIGNATED_AMOUNT, T1139_FORMULA_AMOUNT_FOR_C}),
        frozenset({T1139_DESIGNATED_OR_FORMULA_AMOUNT}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                T1139_DESIGNATES_AMOUNT_CHECKED,
                T1139_FORMULA_AMOUNT_FOR_C,
                T1139_DESIGNATED_OR_FORMULA_AMOUNT,
            }
        ),
        frozenset({T1139_AMOUNT_C}),
    ),
    (LesserOf, frozenset({T1139_AMOUNT_3A, T1139_AMOUNT_3B}), frozenset({T1139_AMOUNT_3C})),
    (Subtract, frozenset({T1139_AMOUNT_A, T1139_AMOUNT_3C}), frozenset({T1139_AMOUNT_3D})),
    (
        ApplyRatioOrZero,
        frozenset({T1139_AMOUNT_3D, T1139_AMOUNT_3E, T1139_AMOUNT_3F}),
        frozenset({T1139_AMOUNT_3H}),
    ),
    (
        CountByConditions,
        frozenset({T1139_FORMULA_CHECKED}),
        frozenset({T1139_FORMULA_IS_B}),
    ),
    (
        TimesCount,
        frozenset({T1139_AMOUNT_B, T1139_FORMULA_IS_B}),
        frozenset({T1139_AMOUNT_B_CHOSEN}),
    ),
    (
        CountByConditions,
        frozenset({T1139_FORMULA_CHECKED}),
        frozenset({T1139_FORMULA_IS_C}),
    ),
    (
        TimesCount,
        frozenset({T1139_AMOUNT_C, T1139_FORMULA_IS_C}),
        frozenset({T1139_AMOUNT_C_CHOSEN}),
    ),
    (
        CountByConditions,
        frozenset({T1139_FORMULA_CHECKED}),
        frozenset({T1139_FORMULA_IS_3H}),
    ),
    (
        TimesCount,
        frozenset({T1139_AMOUNT_3H, T1139_FORMULA_IS_3H}),
        frozenset({T1139_AMOUNT_3H_CHOSEN}),
    ),
    (
        SumNotBelowZero,
        frozenset({T1139_AMOUNT_B_CHOSEN, T1139_AMOUNT_C_CHOSEN, T1139_AMOUNT_3H_CHOSEN}),
        frozenset({T1139_AMOUNT_D}),
    ),
    (Sum, frozenset({T1139_AMOUNT_A, T1139_AMOUNT_D}), frozenset({T1139_AMOUNT_E})),
    (
        Subtract,
        frozenset({T1139_AMOUNT_E, T1139_LAST_YEARS_ADDITIONAL_INCOME}),
        frozenset({T1139_AMOUNT_G}),
    ),
    (Sum, frozenset({T1139_AMOUNT_H, T1139_AMOUNT_I}), frozenset({T1139_AMOUNT_J})),
    (
        Subtract,
        frozenset({T1139_AMOUNT_J, T1139_LAST_YEARS_ADDITIONAL_INCOME}),
        frozenset({T1139_AMOUNT_L}),
    ),
    (
        ChooseByCount,
        frozenset({T1139_CANCELLING_ELECTION_CHECKED, T1139_AMOUNT_G, T1139_AMOUNT_L}),
        frozenset({T1139_NET_INCOME_REPORTED}),
    ),
    (
        ChooseByCount,
        frozenset({T1139_CANCELLING_ELECTION_CHECKED, T1139_AMOUNT_A, T1139_AMOUNT_J}),
        frozenset({T1139_NET_INCOME_REPLACED}),
    ),
    (
        TimesCount,
        frozenset({T1139_NET_INCOME_REPORTED, T1139_ON_BUSINESS_LINE}),
        frozenset({T1139_REPORTED_ON_BUSINESS_LINE}),
    ),
    (
        TimesCount,
        frozenset({T1139_NET_INCOME_REPORTED, T1139_ON_PROFESSIONAL_LINE}),
        frozenset({T1139_REPORTED_ON_PROFESSIONAL_LINE}),
    ),
    (
        TimesCount,
        frozenset({T1139_NET_INCOME_REPORTED, T1139_ON_COMMISSION_LINE}),
        frozenset({T1139_REPORTED_ON_COMMISSION_LINE}),
    ),
    (
        TimesCount,
        frozenset({T1139_NET_INCOME_REPORTED, T1139_ON_FARMING_LINE}),
        frozenset({T1139_REPORTED_ON_FARMING_LINE}),
    ),
    (
        TimesCount,
        frozenset({T1139_NET_INCOME_REPORTED, T1139_ON_FISHING_LINE}),
        frozenset({T1139_REPORTED_ON_FISHING_LINE}),
    ),
    (
        TimesCount,
        frozenset({T1139_NET_INCOME_REPLACED, T1139_ON_BUSINESS_LINE}),
        frozenset({T1139_REPLACED_ON_BUSINESS_LINE}),
    ),
    (
        TimesCount,
        frozenset({T1139_NET_INCOME_REPLACED, T1139_ON_PROFESSIONAL_LINE}),
        frozenset({T1139_REPLACED_ON_PROFESSIONAL_LINE}),
    ),
    (
        TimesCount,
        frozenset({T1139_NET_INCOME_REPLACED, T1139_ON_COMMISSION_LINE}),
        frozenset({T1139_REPLACED_ON_COMMISSION_LINE}),
    ),
    (
        TimesCount,
        frozenset({T1139_NET_INCOME_REPLACED, T1139_ON_FARMING_LINE}),
        frozenset({T1139_REPLACED_ON_FARMING_LINE}),
    ),
    (
        TimesCount,
        frozenset({T1139_NET_INCOME_REPLACED, T1139_ON_FISHING_LINE}),
        frozenset({T1139_REPLACED_ON_FISHING_LINE}),
    ),
    (
        StatementProfitsTotal,
        frozenset(
            {
                T2125_NET_ON_BUSINESS_LINES,
                T2125_NET_ON_PROFESSIONAL_LINES,
                T2125_NET_ON_COMMISSION_LINES,
                T2042_FARMING_INCOME_LINES,
                T2121_FISHING_INCOME_LINES,
                T1139_LINE_CHECKED,
                T1139_A_STATEMENTS,
            }
        ),
        frozenset({T1139_PROFIT_A}),
    ),
    (
        StatementProfitsTotal,
        frozenset(
            {
                T2125_NET_ON_BUSINESS_LINES,
                T2125_NET_ON_PROFESSIONAL_LINES,
                T2125_NET_ON_COMMISSION_LINES,
                T2042_FARMING_INCOME_LINES,
                T2121_FISHING_INCOME_LINES,
                T1139_LINE_CHECKED,
                T1139_H_STATEMENTS,
            }
        ),
        frozenset({T1139_PROFIT_H}),
    ),
    (
        StatementProfitsTotal,
        frozenset(
            {
                T2125_NET_ON_BUSINESS_LINES,
                T2125_NET_ON_PROFESSIONAL_LINES,
                T2125_NET_ON_COMMISSION_LINES,
                T2042_FARMING_INCOME_LINES,
                T2121_FISHING_INCOME_LINES,
                T1139_LINE_CHECKED,
                T1139_I_STATEMENTS,
            }
        ),
        frozenset({T1139_PROFIT_I}),
    ),
    (Sum, frozenset({T1139_PROFIT_H, T1139_PROFIT_I}), frozenset({T1139_PROFIT_HI})),
    (
        ChooseByCount,
        frozenset({T1139_CANCELLING_ELECTION_CHECKED, T1139_PROFIT_A, T1139_PROFIT_HI}),
        frozenset({T1139_PROFIT_REPLACED}),
    ),
    (
        TimesCount,
        frozenset({T1139_PROFIT_REPLACED, T1139_ON_BUSINESS_LINE}),
        frozenset({T1139_PROFIT_REPLACED_ON_BUSINESS_LINE}),
    ),
    (
        TimesCount,
        frozenset({T1139_PROFIT_REPLACED, T1139_ON_PROFESSIONAL_LINE}),
        frozenset({T1139_PROFIT_REPLACED_ON_PROFESSIONAL_LINE}),
    ),
    (
        TimesCount,
        frozenset({T1139_PROFIT_REPLACED, T1139_ON_COMMISSION_LINE}),
        frozenset({T1139_PROFIT_REPLACED_ON_COMMISSION_LINE}),
    ),
    (
        TimesCount,
        frozenset({T1139_PROFIT_REPLACED, T1139_ON_FARMING_LINE}),
        frozenset({T1139_PROFIT_REPLACED_ON_FARMING_LINE}),
    ),
    (
        TimesCount,
        frozenset({T1139_PROFIT_REPLACED, T1139_ON_FISHING_LINE}),
        frozenset({T1139_PROFIT_REPLACED_ON_FISHING_LINE}),
    ),
}
SUMMARY_WIRING = {
    (
        RecordTotal,
        frozenset({T2125_NET_ON_BUSINESS_LINES}),
        frozenset({T1139_STATEMENTS_ON_BUSINESS_LINE}),
    ),
    (
        RecordTotal,
        frozenset({LIST_T1139_REPLACED_ON_BUSINESS_LINE}),
        frozenset({T1139_REPLACED_TOTAL_ON_BUSINESS_LINE}),
    ),
    (
        RecordTotal,
        frozenset({LIST_T1139_REPORTED_ON_BUSINESS_LINE}),
        frozenset({T1139_REPORTED_TOTAL_ON_BUSINESS_LINE}),
    ),
    (
        Subtract,
        frozenset({T1139_STATEMENTS_ON_BUSINESS_LINE, T1139_REPLACED_TOTAL_ON_BUSINESS_LINE}),
        frozenset({T1139_KEPT_ON_BUSINESS_LINE}),
    ),
    (
        Sum,
        frozenset({T1139_KEPT_ON_BUSINESS_LINE, T1139_REPORTED_TOTAL_ON_BUSINESS_LINE}),
        frozenset({T1139_BUSINESS_INCOME_ON_RETURN}),
    ),
    (
        RecordTotal,
        frozenset({T2125_NET_ON_PROFESSIONAL_LINES}),
        frozenset({T1139_STATEMENTS_ON_PROFESSIONAL_LINE}),
    ),
    (
        RecordTotal,
        frozenset({LIST_T1139_REPLACED_ON_PROFESSIONAL_LINE}),
        frozenset({T1139_REPLACED_TOTAL_ON_PROFESSIONAL_LINE}),
    ),
    (
        RecordTotal,
        frozenset({LIST_T1139_REPORTED_ON_PROFESSIONAL_LINE}),
        frozenset({T1139_REPORTED_TOTAL_ON_PROFESSIONAL_LINE}),
    ),
    (
        Subtract,
        frozenset(
            {T1139_STATEMENTS_ON_PROFESSIONAL_LINE, T1139_REPLACED_TOTAL_ON_PROFESSIONAL_LINE}
        ),
        frozenset({T1139_KEPT_ON_PROFESSIONAL_LINE}),
    ),
    (
        Sum,
        frozenset({T1139_KEPT_ON_PROFESSIONAL_LINE, T1139_REPORTED_TOTAL_ON_PROFESSIONAL_LINE}),
        frozenset({T1139_PROFESSIONAL_INCOME_ON_RETURN}),
    ),
    (
        RecordTotal,
        frozenset({T2125_NET_ON_COMMISSION_LINES}),
        frozenset({T1139_STATEMENTS_ON_COMMISSION_LINE}),
    ),
    (
        RecordTotal,
        frozenset({LIST_T1139_REPLACED_ON_COMMISSION_LINE}),
        frozenset({T1139_REPLACED_TOTAL_ON_COMMISSION_LINE}),
    ),
    (
        RecordTotal,
        frozenset({LIST_T1139_REPORTED_ON_COMMISSION_LINE}),
        frozenset({T1139_REPORTED_TOTAL_ON_COMMISSION_LINE}),
    ),
    (
        Subtract,
        frozenset({T1139_STATEMENTS_ON_COMMISSION_LINE, T1139_REPLACED_TOTAL_ON_COMMISSION_LINE}),
        frozenset({T1139_KEPT_ON_COMMISSION_LINE}),
    ),
    (
        Sum,
        frozenset({T1139_KEPT_ON_COMMISSION_LINE, T1139_REPORTED_TOTAL_ON_COMMISSION_LINE}),
        frozenset({T1139_COMMISSION_INCOME_ON_RETURN}),
    ),
    (
        RecordTotal,
        frozenset({FARM_LOSS_FARMING_INCOME_LINES}),
        frozenset({T1139_STATEMENTS_ON_FARMING_LINE}),
    ),
    (
        RecordTotal,
        frozenset({LIST_T1139_REPLACED_ON_FARMING_LINE}),
        frozenset({T1139_REPLACED_TOTAL_ON_FARMING_LINE}),
    ),
    (
        RecordTotal,
        frozenset({LIST_T1139_REPORTED_ON_FARMING_LINE}),
        frozenset({T1139_REPORTED_TOTAL_ON_FARMING_LINE}),
    ),
    (
        Subtract,
        frozenset({T1139_STATEMENTS_ON_FARMING_LINE, T1139_REPLACED_TOTAL_ON_FARMING_LINE}),
        frozenset({T1139_KEPT_ON_FARMING_LINE}),
    ),
    (
        Sum,
        frozenset({T1139_KEPT_ON_FARMING_LINE, T1139_REPORTED_TOTAL_ON_FARMING_LINE}),
        frozenset({T1139_FARMING_INCOME_ON_RETURN}),
    ),
    (
        RecordTotal,
        frozenset({T2121_FISHING_INCOME_LINES}),
        frozenset({T1139_STATEMENTS_ON_FISHING_LINE}),
    ),
    (
        RecordTotal,
        frozenset({LIST_T1139_REPLACED_ON_FISHING_LINE}),
        frozenset({T1139_REPLACED_TOTAL_ON_FISHING_LINE}),
    ),
    (
        RecordTotal,
        frozenset({LIST_T1139_REPORTED_ON_FISHING_LINE}),
        frozenset({T1139_REPORTED_TOTAL_ON_FISHING_LINE}),
    ),
    (
        Subtract,
        frozenset({T1139_STATEMENTS_ON_FISHING_LINE, T1139_REPLACED_TOTAL_ON_FISHING_LINE}),
        frozenset({T1139_KEPT_ON_FISHING_LINE}),
    ),
    (
        Sum,
        frozenset({T1139_KEPT_ON_FISHING_LINE, T1139_REPORTED_TOTAL_ON_FISHING_LINE}),
        frozenset({T1139_FISHING_INCOME_ON_RETURN}),
    ),
    (
        RecordPositiveTotal,
        frozenset({T2125_NET_ON_BUSINESS_LINES}),
        frozenset({T1139_STATEMENT_PROFITS_ON_BUSINESS_LINE}),
    ),
    (
        RecordTotal,
        frozenset({LIST_T1139_PROFIT_REPLACED_ON_BUSINESS_LINE}),
        frozenset({T1139_REPLACED_PROFITS_TOTAL_ON_BUSINESS_LINE}),
    ),
    (
        RecordPositiveTotal,
        frozenset({LIST_T1139_REPORTED_ON_BUSINESS_LINE}),
        frozenset({T1139_REPORTED_PROFITS_TOTAL_ON_BUSINESS_LINE}),
    ),
    (
        Subtract,
        frozenset(
            {
                T1139_STATEMENT_PROFITS_ON_BUSINESS_LINE,
                T1139_REPLACED_PROFITS_TOTAL_ON_BUSINESS_LINE,
            }
        ),
        frozenset({T1139_KEPT_PROFITS_ON_BUSINESS_LINE}),
    ),
    (
        Sum,
        frozenset(
            {T1139_KEPT_PROFITS_ON_BUSINESS_LINE, T1139_REPORTED_PROFITS_TOTAL_ON_BUSINESS_LINE}
        ),
        frozenset({T1139_BUSINESS_PROFIT_ON_RETURN}),
    ),
    (
        RecordPositiveTotal,
        frozenset({T2125_NET_ON_PROFESSIONAL_LINES}),
        frozenset({T1139_STATEMENT_PROFITS_ON_PROFESSIONAL_LINE}),
    ),
    (
        RecordTotal,
        frozenset({LIST_T1139_PROFIT_REPLACED_ON_PROFESSIONAL_LINE}),
        frozenset({T1139_REPLACED_PROFITS_TOTAL_ON_PROFESSIONAL_LINE}),
    ),
    (
        RecordPositiveTotal,
        frozenset({LIST_T1139_REPORTED_ON_PROFESSIONAL_LINE}),
        frozenset({T1139_REPORTED_PROFITS_TOTAL_ON_PROFESSIONAL_LINE}),
    ),
    (
        Subtract,
        frozenset(
            {
                T1139_STATEMENT_PROFITS_ON_PROFESSIONAL_LINE,
                T1139_REPLACED_PROFITS_TOTAL_ON_PROFESSIONAL_LINE,
            }
        ),
        frozenset({T1139_KEPT_PROFITS_ON_PROFESSIONAL_LINE}),
    ),
    (
        Sum,
        frozenset(
            {
                T1139_KEPT_PROFITS_ON_PROFESSIONAL_LINE,
                T1139_REPORTED_PROFITS_TOTAL_ON_PROFESSIONAL_LINE,
            }
        ),
        frozenset({T1139_PROFESSIONAL_PROFIT_ON_RETURN}),
    ),
    (
        RecordPositiveTotal,
        frozenset({T2125_NET_ON_COMMISSION_LINES}),
        frozenset({T1139_STATEMENT_PROFITS_ON_COMMISSION_LINE}),
    ),
    (
        RecordTotal,
        frozenset({LIST_T1139_PROFIT_REPLACED_ON_COMMISSION_LINE}),
        frozenset({T1139_REPLACED_PROFITS_TOTAL_ON_COMMISSION_LINE}),
    ),
    (
        RecordPositiveTotal,
        frozenset({LIST_T1139_REPORTED_ON_COMMISSION_LINE}),
        frozenset({T1139_REPORTED_PROFITS_TOTAL_ON_COMMISSION_LINE}),
    ),
    (
        Subtract,
        frozenset(
            {
                T1139_STATEMENT_PROFITS_ON_COMMISSION_LINE,
                T1139_REPLACED_PROFITS_TOTAL_ON_COMMISSION_LINE,
            }
        ),
        frozenset({T1139_KEPT_PROFITS_ON_COMMISSION_LINE}),
    ),
    (
        Sum,
        frozenset(
            {T1139_KEPT_PROFITS_ON_COMMISSION_LINE, T1139_REPORTED_PROFITS_TOTAL_ON_COMMISSION_LINE}
        ),
        frozenset({T1139_COMMISSION_PROFIT_ON_RETURN}),
    ),
    (
        RecordPositiveTotal,
        frozenset({T2042_FARMING_INCOME_LINES}),
        frozenset({T1139_STATEMENT_PROFITS_ON_FARMING_LINE}),
    ),
    (
        RecordTotal,
        frozenset({LIST_T1139_PROFIT_REPLACED_ON_FARMING_LINE}),
        frozenset({T1139_REPLACED_PROFITS_TOTAL_ON_FARMING_LINE}),
    ),
    (
        RecordPositiveTotal,
        frozenset({LIST_T1139_REPORTED_ON_FARMING_LINE}),
        frozenset({T1139_REPORTED_PROFITS_TOTAL_ON_FARMING_LINE}),
    ),
    (
        Subtract,
        frozenset(
            {T1139_STATEMENT_PROFITS_ON_FARMING_LINE, T1139_REPLACED_PROFITS_TOTAL_ON_FARMING_LINE}
        ),
        frozenset({T1139_KEPT_PROFITS_ON_FARMING_LINE}),
    ),
    (
        Sum,
        frozenset(
            {T1139_KEPT_PROFITS_ON_FARMING_LINE, T1139_REPORTED_PROFITS_TOTAL_ON_FARMING_LINE}
        ),
        frozenset({T1139_FARMING_PROFIT_ON_RETURN}),
    ),
    (
        RecordPositiveTotal,
        frozenset({T2121_FISHING_INCOME_LINES}),
        frozenset({T1139_STATEMENT_PROFITS_ON_FISHING_LINE}),
    ),
    (
        RecordTotal,
        frozenset({LIST_T1139_PROFIT_REPLACED_ON_FISHING_LINE}),
        frozenset({T1139_REPLACED_PROFITS_TOTAL_ON_FISHING_LINE}),
    ),
    (
        RecordPositiveTotal,
        frozenset({LIST_T1139_REPORTED_ON_FISHING_LINE}),
        frozenset({T1139_REPORTED_PROFITS_TOTAL_ON_FISHING_LINE}),
    ),
    (
        Subtract,
        frozenset(
            {T1139_STATEMENT_PROFITS_ON_FISHING_LINE, T1139_REPLACED_PROFITS_TOTAL_ON_FISHING_LINE}
        ),
        frozenset({T1139_KEPT_PROFITS_ON_FISHING_LINE}),
    ),
    (
        Sum,
        frozenset(
            {T1139_KEPT_PROFITS_ON_FISHING_LINE, T1139_REPORTED_PROFITS_TOTAL_ON_FISHING_LINE}
        ),
        frozenset({T1139_FISHING_PROFIT_ON_RETURN}),
    ),
}
