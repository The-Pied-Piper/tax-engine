"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capabilities.tiered_surcharge import TieredSurcharge
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca.catalog import (
    AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE,
    AMT_MINIMUM_TAX_CARRYOVER_APPLIED,
)
from tax_calculator.jurisdictions.ca_on.catalog import (
    MINIMUM_TAX_CARRYOVER_CREDIT,
    ONTARIO_MINIMUM_TAX,
    ONTARIO_MINIMUM_TAX_CARRYOVER_APPLIED,
    ONTARIO_SURTAX,
    ONTARIO_SURTAX_BASE,
    ONTARIO_TAX_AFTER_MINIMUM_TAX_CARRYOVER,
    ONTARIO_TAX_LESS_DIVIDEND_CREDIT,
    ONTARIO_TAX_WITH_SPLIT_INCOME,
    WORKSHEET_ON428_LINE_1,
    WORKSHEET_ON428_LINE_2,
    WORKSHEET_ON428_LINE_3,
    WORKSHEET_ON428_LINE_6,
    WORKSHEET_ON428_LINE_7,
    WORKSHEET_ON428_LINE_8,
)

INPUTS = frozenset[str]()

OUTPUTS = frozenset[str]()

STEPS = {
    # ON428 line 59 "Amount from line 40427 of your return multiplied by 24.63%": the minimum tax
    # carryover applied on the T1 (T691 Part 8 line 12) at the Ontario minimum tax rate.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/minimum_tax_rate"},
        consumes={"base": "ca/amt_minimum_tax_carryover_applied"},
        produces={"output": "ca-on/minimum_tax_carryover_credit"},
    ),
    # ON428 line 60 and line 61540 "Enter whichever is less: amount from line 58 or line 59."
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca-on/ontario_tax_less_dividend_credit",
                "ca-on/minimum_tax_carryover_credit",
            )
        },
        produces={"output": "ca-on/ontario_minimum_tax_carryover_applied"},
    ),
    # ON428 line 61 "Line 55 minus line 60 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/ontario_tax_with_split_income",
            "less": "ca-on/ontario_minimum_tax_carryover_applied",
        },
        produces={"output": "ca-on/ontario_tax_after_minimum_tax_carryover"},
    ),
    # Worksheet ON428 line 1 "Amount from line 11 of Part 5 of your Form T691 multiplied by
    # 24.63%".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/minimum_tax_rate"},
        consumes={"base": "ca/amt_alternative_minimum_tax_payable"},
        produces={"output": "ca-on/worksheet_on428_line_1"},
    ),
    # Worksheet ON428 line 2 "Amount from line 65 of your Form ON428".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca-on/ontario_surtax_base",)},
        produces={"output": "ca-on/worksheet_on428_line_2"},
    ),
    # Worksheet ON428 line 3 "Line 1 plus line 2 =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca-on/worksheet_on428_line_1", "ca-on/worksheet_on428_line_2")},
        produces={"output": "ca-on/worksheet_on428_line_3"},
    ),
    # Worksheet ON428 lines 4 to 6: "(Line 3 Minus $5,710) multiplied by 20%" and "(Line 3 Minus
    # $7,307) multiplied by 36%", each "if negative, enter "0"", and line 6 "Line 4 plus line 5 =".
    CapabilitySelection(
        name="core/tiered_surcharge",
        params={"tiers": "ca-on/surtax"},
        consumes={"base": "ca-on/worksheet_on428_line_3"},
        produces={"output": "ca-on/worksheet_on428_line_6"},
    ),
    # Worksheet ON428 line 7 "Amount from line 68 of your Form ON428".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca-on/ontario_surtax",)},
        produces={"output": "ca-on/worksheet_on428_line_7"},
    ),
    # Worksheet ON428 line 8 "Line 6 minus line 7 =", with no floor printed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca-on/worksheet_on428_line_6",
            "less": "ca-on/worksheet_on428_line_7",
        },
        produces={"output": "ca-on/worksheet_on428_line_8"},
    ),
    # Worksheet ON428 line 9 "Line 1 plus line 8 Enter this amount on line 72 of your Form
    # ON428.", which is ON428 line 72.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca-on/worksheet_on428_line_1", "ca-on/worksheet_on428_line_8")},
        produces={"output": "ca-on/ontario_minimum_tax"},
    ),
}

WIRING = {
    (
        ApplyRate,
        frozenset({AMT_MINIMUM_TAX_CARRYOVER_APPLIED}),
        frozenset({MINIMUM_TAX_CARRYOVER_CREDIT}),
    ),
    (
        LesserOf,
        frozenset({ONTARIO_TAX_LESS_DIVIDEND_CREDIT, MINIMUM_TAX_CARRYOVER_CREDIT}),
        frozenset({ONTARIO_MINIMUM_TAX_CARRYOVER_APPLIED}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({ONTARIO_TAX_WITH_SPLIT_INCOME, ONTARIO_MINIMUM_TAX_CARRYOVER_APPLIED}),
        frozenset({ONTARIO_TAX_AFTER_MINIMUM_TAX_CARRYOVER}),
    ),
    (
        ApplyRate,
        frozenset({AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE}),
        frozenset({WORKSHEET_ON428_LINE_1}),
    ),
    (Sum, frozenset({ONTARIO_SURTAX_BASE}), frozenset({WORKSHEET_ON428_LINE_2})),
    (
        Sum,
        frozenset({WORKSHEET_ON428_LINE_1, WORKSHEET_ON428_LINE_2}),
        frozenset({WORKSHEET_ON428_LINE_3}),
    ),
    (TieredSurcharge, frozenset({WORKSHEET_ON428_LINE_3}), frozenset({WORKSHEET_ON428_LINE_6})),
    (Sum, frozenset({ONTARIO_SURTAX}), frozenset({WORKSHEET_ON428_LINE_7})),
    (
        Subtract,
        frozenset({WORKSHEET_ON428_LINE_6, WORKSHEET_ON428_LINE_7}),
        frozenset({WORKSHEET_ON428_LINE_8}),
    ),
    (
        Sum,
        frozenset({WORKSHEET_ON428_LINE_1, WORKSHEET_ON428_LINE_8}),
        frozenset({ONTARIO_MINIMUM_TAX}),
    ),
}
