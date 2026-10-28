"""The CA-ON manifest entries of Form T90 "Income Exempt from Tax under the Indian Act" (see
`test_manifest_t90.py`).

The form `ca/t90` runs once (it has no instances): the sixteen amounts the filer enters on lines 1
to 19 (line 10019 is the unnumbered "EI maternity and parental benefits and PPIP benefits included
on line 9"), the check of line 10019 against line 9, and the printed sums and differences of
lines 4, 14, 16, 18 and 20. Its exports are line 4 "Total exempt working income 10000", line 20
"Net exempt income 10026" and the checked line 10019, read by Schedule 6 (the Canada workers
benefit) through the form-qualified names `ca/t90.t90_...`.

The return selects none of the steps of the form (the form's own steps run with the form), and
declares no output for it, as the section of Form T1206 does.
"""

from __future__ import annotations

from tax_calculator.domain.capabilities.at_most import AtMost
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca.catalog import (
    T90_COVID_19_PAYMENTS,
    T90_CPP_QPP_BENEFITS,
    T90_DEDUCTIONS_RELATING_TO_EXEMPT_INCOME,
    T90_EI_MATERNITY_PARENTAL_PPIP_BENEFITS,
    T90_EI_MATERNITY_PARENTAL_PPIP_BENEFITS_CHECKED,
    T90_EI_PPIP_AND_OTHER_BENEFITS,
    T90_EXEMPT_WORKING_INCOME,
    T90_INTEREST_DIVIDENDS_INVESTMENT_INCOME,
    T90_LINE_14,
    T90_LINE_16,
    T90_NET_EXEMPT_INCOME,
    T90_NET_RENTAL_INCOME,
    T90_NET_RENTAL_LOSSES,
    T90_NET_SELF_EMPLOYMENT_INCOME,
    T90_NET_SELF_EMPLOYMENT_LOSSES,
    T90_OTHER_EMPLOYMENT_INCOME,
    T90_OTHER_EXEMPT_INCOME,
    T90_OTHER_PENSIONS_AND_SUPERANNUATION,
    T90_RRSP_RRIF_PENSION_TRANSFER_INCOME,
    T90_SOCIAL_ASSISTANCE_PAYMENTS,
    T90_T4_BOX_71_EMPLOYMENT_INCOME,
    T90_TOTAL_EXEMPT_INCOME,
)

FORM = "ca/t90"

# The sixteen amounts of the form, as the filer enters them (line 10019 included), in
# `01j_t90_inputs.yaml`.
INPUTS = frozenset(
    {
        "ca/t90_t4_box_71_employment_income",
        "ca/t90_other_employment_income",
        "ca/t90_net_self_employment_income",
        "ca/t90_cpp_qpp_benefits",
        "ca/t90_rrsp_rrif_pension_transfer_income",
        "ca/t90_covid_19_payments",
        "ca/t90_other_pensions_and_superannuation",
        "ca/t90_ei_ppip_and_other_benefits",
        "ca/t90_ei_maternity_parental_ppip_benefits",
        "ca/t90_interest_dividends_investment_income",
        "ca/t90_net_rental_income",
        "ca/t90_social_assistance_payments",
        "ca/t90_other_exempt_income",
        "ca/t90_net_rental_losses",
        "ca/t90_net_self_employment_losses",
        "ca/t90_deductions_relating_to_exempt_income",
    }
)

# The exports of the form, read by the Schedule 6 wiring: line 4, the checked line 10019 and
# line 20.
EXPORTS = frozenset(
    {
        "ca/t90_exempt_working_income",
        "ca/t90_ei_maternity_parental_ppip_benefits_checked",
        "ca/t90_net_exempt_income",
    }
)

# The return selects no step of the form and reads no output of it in this family.
OUTPUTS: frozenset[str] = frozenset()
STEPS: set[CapabilitySelection] = set()
WIRING: set[object] = set()

# The steps of the form, one for each printed line that computes, with its line in the comment.
FORM_STEPS = {
    # Line 4 "Add lines 1 to 3." (Total exempt working income 10000): lines 1, 2 and 3.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t90_t4_box_71_employment_income",
                "ca/t90_other_employment_income",
                "ca/t90_net_self_employment_income",
            )
        },
        produces={"output": "ca/t90_exempt_working_income"},
    ),
    # Line 10019 "EI maternity and parental benefits and PPIP benefits included on line 9": the
    # amount is part of line 9, so it is refused above line 9 and never capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t90_ei_maternity_parental_ppip_benefits",
            "bound": "ca/t90_ei_ppip_and_other_benefits",
        },
        produces={"output": "ca/t90_ei_maternity_parental_ppip_benefits_checked"},
    ),
    # Line 14 "Add lines 4 to 13.": line 4 and lines 5 to 13 except line 10019, which line 9 holds.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t90_exempt_working_income",
                "ca/t90_cpp_qpp_benefits",
                "ca/t90_rrsp_rrif_pension_transfer_income",
                "ca/t90_covid_19_payments",
                "ca/t90_other_pensions_and_superannuation",
                "ca/t90_ei_ppip_and_other_benefits",
                "ca/t90_interest_dividends_investment_income",
                "ca/t90_net_rental_income",
                "ca/t90_social_assistance_payments",
                "ca/t90_other_exempt_income",
            )
        },
        produces={"output": "ca/t90_line_14"},
    ),
    # Line 16 "Line 14 minus line 15": the net rental losses. No floor is printed, so it is signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/t90_line_14", "less": "ca/t90_net_rental_losses"},
        produces={"output": "ca/t90_line_16"},
    ),
    # Line 18 "Line 16 minus line 17" (Total exempt income): the net self-employment losses.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/t90_line_16", "less": "ca/t90_net_self_employment_losses"},
        produces={"output": "ca/t90_total_exempt_income"},
    ),
    # Line 20 "Line 18 minus line 19 (if negative, show in brackets)" (Net exempt income 10026): the
    # deductions relating to exempt income. Signed: a negative result is shown in brackets.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t90_total_exempt_income",
            "less": "ca/t90_deductions_relating_to_exempt_income",
        },
        produces={"output": "ca/t90_net_exempt_income"},
    ),
}

# The wiring of the form's steps, as `test_manifest_t90.py` reads it from the composed form: the
# capability class, the kinds it consumes and the kinds it produces.
FORM_WIRING = {
    (
        AtMost,
        frozenset({T90_EI_MATERNITY_PARENTAL_PPIP_BENEFITS, T90_EI_PPIP_AND_OTHER_BENEFITS}),
        frozenset({T90_EI_MATERNITY_PARENTAL_PPIP_BENEFITS_CHECKED}),
    ),
    (
        Sum,
        frozenset(
            {
                T90_T4_BOX_71_EMPLOYMENT_INCOME,
                T90_OTHER_EMPLOYMENT_INCOME,
                T90_NET_SELF_EMPLOYMENT_INCOME,
            }
        ),
        frozenset({T90_EXEMPT_WORKING_INCOME}),
    ),
    (
        Sum,
        frozenset(
            {
                T90_EXEMPT_WORKING_INCOME,
                T90_CPP_QPP_BENEFITS,
                T90_RRSP_RRIF_PENSION_TRANSFER_INCOME,
                T90_COVID_19_PAYMENTS,
                T90_OTHER_PENSIONS_AND_SUPERANNUATION,
                T90_EI_PPIP_AND_OTHER_BENEFITS,
                T90_INTEREST_DIVIDENDS_INVESTMENT_INCOME,
                T90_NET_RENTAL_INCOME,
                T90_SOCIAL_ASSISTANCE_PAYMENTS,
                T90_OTHER_EXEMPT_INCOME,
            }
        ),
        frozenset({T90_LINE_14}),
    ),
    (
        Subtract,
        frozenset({T90_LINE_14, T90_NET_RENTAL_LOSSES}),
        frozenset({T90_LINE_16}),
    ),
    (
        Subtract,
        frozenset({T90_LINE_16, T90_NET_SELF_EMPLOYMENT_LOSSES}),
        frozenset({T90_TOTAL_EXEMPT_INCOME}),
    ),
    (
        Subtract,
        frozenset({T90_TOTAL_EXEMPT_INCOME, T90_DEDUCTIONS_RELATING_TO_EXEMPT_INCOME}),
        frozenset({T90_NET_EXEMPT_INCOME}),
    ),
}
