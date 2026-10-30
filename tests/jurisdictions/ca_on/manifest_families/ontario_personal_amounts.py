"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.at_most import AtMost
from tax_engine.domain.capabilities.capped_amount import CappedAmount
from tax_engine.domain.capabilities.choose_by_count import ChooseByCount
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.lesser_of import LesserOf
from tax_engine.domain.capabilities.progressive_tax import ProgressiveTax
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capabilities.times_count import TimesCount
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.jurisdictions.ca.capabilities.amount_or_divided_by_rate import (
    AmountOrDividedByRate,
)
from tax_engine.jurisdictions.ca.capabilities.other_dependants_medical import (
    OtherDependantsMedical,
)
from tax_engine.jurisdictions.ca.catalog import (
    ADOPTION_EXPENSE_CHILDREN,
    BORN_IN_1960_OR_EARLIER_CHECKED,
    CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    DEPENDANT_NET_INCOME,
    DISABILITY_SELF_CARE_EXPENSES,
    EI_PREMIUMS,
    EI_PREMIUMS_ON_SELF_EMPLOYMENT,
    ELIGIBLE_DEPENDANTS_CHECKED,
    ELIGIBLE_FOR_DISABILITY_AMOUNT_CHECKED,
    MEDICAL_EXPENSES,
    NET_INCOME,
    OTHER_DEPENDANTS,
    PENSION_INCOME_CREDIT,
    SPOUSE_NET_INCOME,
    SPOUSE_NOT_SEPARATED_90_DAYS_CHECKED,
    SPOUSE_RETURN_TAXABLE_INCOME,
    SPOUSES_CLAIMED_CHECKED,
    TAXABLE_INCOME,
    TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO,
    UNDER_18_ON_DECEMBER_31_CHECKED,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tax_engine.jurisdictions.ca_on.capabilities.capped_record_total import (
    OntarioCappedRecordTotal,
)
from tax_engine.jurisdictions.ca_on.capabilities.caregiver_amount import OntarioCaregiverAmount
from tax_engine.jurisdictions.ca_on.capabilities.disability_transfer_amount import (
    OntarioDisabilityTransferAmount,
)
from tax_engine.jurisdictions.ca_on.catalog import (
    CAREGIVER_DEPENDANTS,
    ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_MAXIMUM,
    ELIGIBLE_DEPENDANT_BASE,
    ONTARIO_BASIC_TAX,
)

INPUTS = frozenset(
    {
        "ca-on/caregiver_dependants",
        "ca-on/disability_dependants",
        # Schedule ON(S11) line 1 "Enter your unused Ontario tuition and education amounts from your
        # 2024 notice of assessment or reassessment": a caller input, the figure on that notice, not
        # a calculation on this return (as Schedule 7 line 1 is for RRSPs).
        "ca-on/unused_tuition_amounts_brought_forward",
        # Schedule ON(S2) lines 1 to 3, 6 to 8 and the Ontario tax on line 5: figures from another
        # person's Form ON428, caller inputs (their lines 58080, 58360, 58440, 58040, 24, 58560
        # and 8), one set for the one spouse. Their line 26000 and the separation count are the
        # federal Schedule 2's inputs again.
        "ca-on/spouse_return_ontario_age_amount",
        "ca-on/spouse_return_ontario_pension_income_amount",
        "ca-on/spouse_return_ontario_disability_amount",
        "ca-on/spouse_return_ontario_basic_tax",
        "ca-on/spouse_return_ontario_basic_personal_amount",
        "ca-on/spouse_return_ontario_line_24",
        "ca-on/spouse_return_ontario_unused_tuition_amount",
    }
)

# Schedule ON(S11) line 8 "Unused provincial tuition and education amounts available to carry
# forward to a future year", which nothing else on the return reads (the carryforward is for a
# future year).
OUTPUTS = frozenset(
    {
        "ca-on/unused_tuition_carried_forward",
    }
)

STEPS = {
    CapabilitySelection(
        name="core/progressive_tax",
        params={"schedule": "ca-on/brackets"},
        consumes={"base": "ca/taxable_income"},
        produces={"output": "ca-on/ontario_basic_tax"},
    ),
    # ON428 line 58040 has no reduction: the Ontario basic personal amount dataset becomes an
    # artifact of the same name, the first part of ON428's total of credit amounts.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/basic_personal_amount"},
        consumes={},
        produces={"output": "ca-on/basic_personal_amount"},
    ),
    # Worksheet ON428, "Line 58080 - Age amount": line 1 "Maximum amount 6,223.00", the
    # dataset as an artifact of the same name.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/age_maximum"},
        consumes={},
        produces={"output": "ca-on/age_maximum"},
    ),
    # Line 3 "Income threshold 46,330.00", the dataset as an artifact of the same name.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/age_income_threshold"},
        consumes={},
        produces={"output": "ca-on/age_income_threshold"},
    ),
    # Line 2 "Amount from line 23600 of your return", the TOSI-adjusted net income of Form T1206
    # Part 1 line 6 in its place, not below zero, and line 4 "Line 2 minus line 3 (if negative,
    # enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/tosi_adjusted_net_income_not_below_zero",
            "less": "ca-on/age_income_threshold",
        },
        produces={"output": "ca-on/age_income_over_threshold"},
    ),
    # Line 5 "Applicable rate 15%" and line 6 "Line 4 multiplied by the percentage from line
    # 5".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/age_rate"},
        consumes={"base": "ca-on/age_income_over_threshold"},
        produces={"output": "ca-on/age_reduction"},
    ),
    # Line 7 "Line 1 minus line 6 (if negative, enter "0") Enter this amount on line 58080 of
    # your Form ON428."
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca-on/age_maximum", "less": "ca-on/age_reduction"},
        produces={"output": "ca-on/age_amount_before_count"},
    ),
    # ON428 line 10 and line 58080 "Age amount (if you were born in 1960 or earlier) (use
    # Worksheet ON428) (maximum $6,223)": line 7 once if born in 1960 or earlier, else 0.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca-on/age_amount_before_count",
            "count": "ca/born_in_1960_or_earlier_checked",
        },
        produces={"output": "ca-on/age_amount"},
    ),
    # ON428 line 11 "Base amount 11,905.00": the dataset becomes an artifact of the same name.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/spouse_base"},
        consumes={},
        produces={"output": "ca-on/spouse_base"},
    ),
    # Line 12 "Your spouse's or common-law partner's net income from line 23600 of their
    # return", and line 13 (line 58120) "Line 11 minus line 12 (if negative, enter "0")
    # (maximum $10,823)", before its maximum, then at most it.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca-on/spouse_base", "less": "ca/spouse_net_income"},
        produces={"output": "ca-on/spouse_amount_before_maximum"},
    ),
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca-on/spouse_maximum"},
        consumes={"base": "ca-on/spouse_amount_before_maximum"},
        produces={"output": "ca-on/spouse_amount_before_count"},
    ),
    # Line 58120 for each spouse or common-law partner amount claimed, the T1 line 30300
    # count.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca-on/spouse_amount_before_count",
            "count": "ca/spouses_claimed_checked",
        },
        produces={"output": "ca-on/spouse_amount"},
    ),
    # ON428 line 14 "Base amount 11,905.00": the dataset becomes an artifact of the same name.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/eligible_dependant_base"},
        consumes={},
        produces={"output": "ca-on/eligible_dependant_base"},
    ),
    # ON428 line 15 "Your eligible dependant's net income from line 23600 of their return",
    # the federal Schedule 5 line 4 figure, and line 16 (line 58160) "Line 14 minus line 15
    # (if negative, enter "0") (maximum $10,823)", before its maximum, then at most it.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/eligible_dependant_base",
            "less": "ca/dependant_net_income",
        },
        produces={"output": "ca-on/eligible_dependant_amount_before_maximum"},
    ),
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca-on/eligible_dependant_maximum"},
        consumes={"base": "ca-on/eligible_dependant_amount_before_maximum"},
        produces={"output": "ca-on/eligible_dependant_amount_before_count"},
    ),
    # Line 58160 for each eligible dependant claimed, the T1 line 30400 count.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca-on/eligible_dependant_amount_before_count",
            "count": "ca/eligible_dependants_checked",
        },
        produces={"output": "ca-on/eligible_dependant_amount"},
    ),
    # ON428 line 39 "Line 37 multiplied by the percentage from line 38" (line 37 "Amount from
    # line 23600 of your return", line 38 "Applicable rate 3%"): 3% of the net income.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca-on/medical_net_income_rate"},
        consumes={"base": "ca/net_income"},
        produces={"output": "ca-on/medical_net_income_share"},
    ),
    # ON428 line 40 "Enter whichever is less: $2,885 or the amount on line 39."
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca-on/medical_threshold_ceiling"},
        consumes={"base": "ca-on/medical_net_income_share"},
        produces={"output": "ca-on/medical_threshold"},
    ),
    # ON428 line 41 "Line 36 minus line 40 (if negative, enter "0")": line 36 is the filer's
    # medical expenses, the caller input of T1 line 107 (line 33099), shared with the T1.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/medical_expenses", "less": "ca-on/medical_threshold"},
        produces={"output": "ca-on/medical_expenses_over_threshold"},
    ),
    # ON428 line 42 and line 58729 "Allowable amount of medical expenses for other dependants
    # (use Worksheet ON428)"; Worksheet ON428, line 58729, for each dependant: line 1 "Medical
    # expenses for other dependant", line 2 "Enter the amount from line 40 of the dependant's
    # Form ON428.", line 3 "Line 1 minus line 2 (if negative, enter "0") (maximum $15,551 per
    # dependant)", and line 4 "Add the amounts from line 3 of columns 1, 2, and 3 (and others,
    # if any). Enter this amount on line 58729 of your Form ON428." The same people as T1 line
    # 33199, so the same record list.
    CapabilitySelection(
        name="ca/other_dependants_medical",
        params={"reduction": "ca-on/other_dependants_medical_reduction"},
        consumes={"dependants": "ca/other_dependants"},
        produces={"output": "ca-on/other_dependants_medical"},
    ),
    # ON428 line 43 and line 58769 "Line 41 plus line 42".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": ("ca-on/medical_expenses_over_threshold", "ca-on/other_dependants_medical")
        },
        produces={"output": "ca-on/medical_claim"},
    ),
    # ON428 line 17 and line 58185 "Ontario caregiver amount (use Worksheet ON428)", Worksheet
    # ON428 "Line 58185 - Ontario caregiver amount": for each dependant, line 1 "Base amount
    # 26,562.00" less line 2 "Dependant's net income from line 23600 of their return", line 3
    # "Line 1 minus line 2 (if negative, enter "0") (maximum $6,008 per dependant)", line 4
    # "Amount claimed for this dependant on line 58160 of your Form ON428, if any", line 5
    # "Allowable amount for this dependant: line 3 minus line 4 (if negative, enter "0")" and
    # line 6 "Add the amounts from line 5 of columns 1, 2, and 3 (and others, if any). Enter
    # this amount on line 58185 of your Form ON428."
    CapabilitySelection(
        name="ca-on/caregiver_amount",
        params={
            "base": "ca-on/caregiver_base_amount",
            "maximum": "ca-on/caregiver_maximum_amount",
        },
        consumes={
            "dependants": "ca-on/caregiver_dependants",
            "eligible_dependant_amount": "ca-on/eligible_dependant_amount",
            "eligible_dependants": "ca/eligible_dependants_checked",
        },
        produces={"output": "ca-on/caregiver_amount"},
    ),
    # ON428 line 23 and line 58330 "Adoption expenses", each child capped at $15,551 (T2203 note
    # (5)), the filer's share of the expenses. Each child's eligible expenses are a record of the
    # same list the federal line 31300 reads, capped one by one and then added up.
    CapabilitySelection(
        name="ca-on/capped_record_total",
        params={"cap": "ca-on/adoption_expenses_maximum"},
        consumes={"records": "ca/adoption_expense_children"},
        produces={"output": "ca-on/adoption_credit"},
    ),
    # ON428 line 27 and line 58360 "Pension income amount (maximum $1,762)": the lesser of $1,762
    # and the amount on line 31400 (CRA's line 31400 web page, a listed check).
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca-on/pension_income_maximum"},
        consumes={"base": "ca/pension_income_credit"},
        produces={"output": "ca-on/pension_income_credit"},
    ),
    # ON428 line 29 and line 58440 "Disability amount for self (claim $10,298 or, if you were under
    # 18 years of age, use Worksheet ON428)", Worksheet ON428 "Line 58440 - Disability amount for
    # self": line 1 "Base amount 10,298.00", the dataset as an artifact of the same name.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/disability_self_base_amount"},
        consumes={},
        produces={"output": "ca-on/disability_self_base_amount"},
    ),
    # Line 2 "Maximum amount 6,007.00", the dataset as an artifact of the same name.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/disability_self_supplement_maximum"},
        consumes={},
        produces={"output": "ca-on/disability_self_supplement_maximum"},
    ),
    # Line 4 "Threshold for child and attendant care expenses 3,518.00", the dataset as an
    # artifact of the same name. Line 3 "Total child care and attendant care expenses for you,
    # claimed by you or another person" is the same caller's input as the federal line 3,
    # ca/disability_self_care_expenses.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/disability_self_care_threshold"},
        consumes={},
        produces={"output": "ca-on/disability_self_care_threshold"},
    ),
    # Line 5 "Line 3 minus line 4 (if negative, enter "0") =".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/disability_self_care_expenses",
            "less": "ca-on/disability_self_care_threshold",
        },
        produces={"output": "ca-on/disability_self_care_over_threshold"},
    ),
    # Line 6 "Line 2 minus line 5 (if negative, enter "0") =".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/disability_self_supplement_maximum",
            "less": "ca-on/disability_self_care_over_threshold",
        },
        produces={"output": "ca-on/disability_self_supplement"},
    ),
    # Line 7 "Line 1 plus line 6 Enter this amount on line 58440 of your Form ON428. (maximum
    # $16,305) =": the sum needs no cap, as line 6 is at most the maximum amount 6,007.00.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca-on/disability_self_base_amount",
                "ca-on/disability_self_supplement",
            )
        },
        produces={"output": "ca-on/disability_self_worksheet_amount"},
    ),
    # ON428 line 29 "claim $10,298 or, if you were under 18 years of age, use Worksheet ON428": the
    # base amount for a filer 18 or older on December 31, 2025, the line 7 worksheet amount for a
    # filer under 18.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/under_18_on_december_31_checked",
            "when_none": "ca-on/disability_self_base_amount",
            "when_any": "ca-on/disability_self_worksheet_amount",
        },
        produces={"output": "ca-on/disability_amount_for_self_if_eligible"},
    ),
    # "If you qualify for the disability amount" (the CRA approved Form T2201): the amount once if
    # the filer qualifies, else 0.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca-on/disability_amount_for_self_if_eligible",
            "count": "ca/eligible_for_disability_amount_checked",
        },
        produces={"output": "ca-on/disability_amount_for_self"},
    ),
    # ON428 line 30 and line 58480 "Disability amount transferred from a dependant (use
    # Worksheet ON428)", Worksheet ON428 "Line 58480 - Disability amount transferred from a
    # dependant": for each dependant, line 1 "Base amount 10,298.00", line 2 "Maximum amount
    # 6,007.00", line 4 "Threshold for child and attendant care expenses 3,518.00", line 7
    # "Line 1 plus line 6 (maximum $16,305) =", line 8 "Enter the amount from line 28 of the
    # dependant's Form ON428.", line 12 "Enter whichever is less: amount from line 7 or line
    # 11. Allowable amount for this dependant" and "Enter the total of allowable amounts
    # claimed for all dependants on line 58480 of your Form ON428."
    CapabilitySelection(
        name="ca-on/disability_transfer_amount",
        params={
            "base": "ca-on/disability_transfer_base_amount",
            "supplement": "ca-on/disability_transfer_supplement_maximum",
            "threshold": "ca-on/disability_transfer_care_threshold",
            "maximum": "ca-on/disability_transfer_maximum",
        },
        consumes={"dependants": "ca-on/disability_dependants"},
        produces={"output": "ca-on/disability_transferred_amount"},
    ),
    # Schedule ON(S11) line 2 "Enter the amount from line 26000 of your return on line 2 if it is
    # $52,886 or less. If it is more than $52,886, enter the result of the following calculation:"
    # "Line 2: Amount from line 8 of your Form ON428" "divided by 5.05% =": the taxable income
    # passes through at or below the dataset's threshold, and over it the Ontario tax on taxable
    # income (ON428 line 8) is divided by the rate, rounded half-up to the cent.
    CapabilitySelection(
        name="ca/amount_or_divided_by_rate",
        params={"limit": "ca-on/unused_tuition_limit"},
        consumes={
            "amount": "ca/taxable_income",
            "dividend": "ca-on/ontario_basic_tax",
        },
        produces={"output": "ca-on/unused_tuition_income_cap"},
    ),
    # ON428 line 31 "Line 31: Add lines 28 to 30. =": the credit amounts the form totals before
    # medical expenses, as its lines 1 to 25 carry them (the basic personal amount, the age, spouse,
    # eligible dependant and caregiver amounts, the CPP and EI contributions), and line 30 (the
    # disability amount transferred from a dependant). The adoption and pension amounts (lines 23
    # and 27) and the disability amount for self (line 29) are in it too; the student loan interest
    # (line 32) is not, as it comes after line 31.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca-on/basic_personal_amount",
                "ca-on/age_amount",
                "ca-on/spouse_amount",
                "ca-on/eligible_dependant_amount",
                "ca-on/caregiver_amount",
                "ca/cpp_base_contributions_on_return",
                "ca/cpp_base_contributions_on_self_employment_and_other_earnings",
                "ca/ei_premiums",
                "ca/ei_premiums_on_self_employment",
                "ca-on/adoption_credit",
                "ca-on/pension_income_credit",
                "ca-on/disability_amount_for_self",
                "ca-on/disability_transferred_amount",
            )
        },
        produces={"output": "ca-on/credit_amounts_through_disability_transfer"},
    ),
    # Schedule ON(S11) line 4 "Line 2 minus line 3 (if negative, enter "0") =", line 3 being
    # "Enter the amount from line 31 of your Form ON428.", not below zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/unused_tuition_income_cap",
            "less": "ca-on/credit_amounts_through_disability_transfer",
        },
        produces={"output": "ca-on/unused_tuition_room"},
    ),
    # Schedule ON(S11) line 5 "Enter whichever is less: amount from line 1 or line 4. Enter this
    # amount on line 58560 of your Form ON428. Your unused Ontario tuition and education amounts
    # claimed for 2025": the lesser of line 1 and line 4. ON428 line 33 and line 58560 takes it, in
    # the non-refundable credit amounts.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca-on/unused_tuition_amounts_brought_forward",
                "ca-on/unused_tuition_room",
            ),
        },
        produces={"output": "ca-on/unused_tuition_claimed"},
    ),
    # Schedule ON(S11) line 8 "Line 6 minus line 7 Unused provincial tuition and education amounts
    # available to carry forward to a future year =". Lines 6 and 7 are copies of line 1 and
    # line 5 (the carryforward section), so they have no steps: line 8 is line 1 minus line 5.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca-on/unused_tuition_amounts_brought_forward",
            "less": "ca-on/unused_tuition_claimed",
        },
        produces={"output": "ca-on/unused_tuition_carried_forward"},
    ),
    # Schedule ON(S2) line 1 and line 59020 "Enter the amount from line 58080 of their Form ON428.",
    # against the age maximum of ON428 line 58080 "(maximum $6,223)" (`ca-on/age_maximum`): an
    # amount above it is an input error, not capped, and the checked amount is what line 4 adds.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca-on/spouse_return_ontario_age_amount",
            "bound": "ca-on/age_maximum",
        },
        produces={"output": "ca-on/spouse_return_ontario_age_amount_checked"},
    ),
    # Schedule ON(S2) line 2 and line 59050 "Enter the amount from line 58360 of their Form ON428.
    # (maximum $1,762)": the maximum as a dataset of the same name, an artifact of its own, then
    # the amount checked against it the same way.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/spouse_return_ontario_pension_income_amount_maximum"},
        consumes={},
        produces={"output": "ca-on/spouse_return_ontario_pension_income_amount_maximum"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca-on/spouse_return_ontario_pension_income_amount",
            "bound": "ca-on/spouse_return_ontario_pension_income_amount_maximum",
        },
        produces={"output": "ca-on/spouse_return_ontario_pension_income_amount_checked"},
    ),
    # Schedule ON(S2) line 3 and line 59070 "Enter the amount from line 58440 of their Form ON428.",
    # against the maximum printed on Worksheet ON428 line 7 for line 58440, "(maximum $16,305)".
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca-on/spouse_return_ontario_disability_amount_maximum"},
        consumes={},
        produces={"output": "ca-on/spouse_return_ontario_disability_amount_maximum"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca-on/spouse_return_ontario_disability_amount",
            "bound": "ca-on/spouse_return_ontario_disability_amount_maximum",
        },
        produces={"output": "ca-on/spouse_return_ontario_disability_amount_checked"},
    ),
    # Schedule ON(S2) line 4 "Add lines 1 to 3. =": the three amounts as checked, the line 1, 2 and
    # 3 amounts that are at or under their maximums.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca-on/spouse_return_ontario_age_amount_checked",
                "ca-on/spouse_return_ontario_pension_income_amount_checked",
                "ca-on/spouse_return_ontario_disability_amount_checked",
            )
        },
        produces={"output": "ca-on/spouse_transferable_amounts"},
    ),
    # Schedule ON(S2) line 5 "Enter the amount from line 26000 of their return on line 5 if it is
    # $52,886 or less. If it is more than $52,886, enter the result of the following calculation:
    # Amount from line 8 of their Form ON428 divided by 5.05% =": their line 26000 is the federal
    # Schedule 2's input, their ON428 line 8 a caller input.
    CapabilitySelection(
        name="ca/amount_or_divided_by_rate",
        params={"limit": "ca-on/spouse_transfer_income_limit"},
        consumes={
            "amount": "ca/spouse_return_taxable_income",
            "dividend": "ca-on/spouse_return_ontario_basic_tax",
        },
        produces={"output": "ca-on/spouse_income_for_transfer"},
    ),
    # Schedule ON(S2) line 6 "Amount from line 58040 of their Form ON428", against the basic
    # personal amount of ON428 line 9 "Claim $12,747" (`ca-on/basic_personal_amount`): an amount
    # above it is an input error, not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca-on/spouse_return_ontario_basic_personal_amount",
            "bound": "ca-on/basic_personal_amount",
        },
        produces={"output": "ca-on/spouse_return_ontario_basic_personal_amount_checked"},
    ),
    # Schedule ON(S2) line 6 (checked), line 7 "Amount from line 24 of their Form ON428" and line 8
    # "Amount from line 58560 of their Form ON428", caller inputs, and line 9 "Add lines 6 to 8. =".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca-on/spouse_return_ontario_basic_personal_amount_checked",
                "ca-on/spouse_return_ontario_line_24",
                "ca-on/spouse_return_ontario_unused_tuition_amount",
            )
        },
        produces={"output": "ca-on/spouse_credits_used"},
    ),
    # Schedule ON(S2) line 10 and line 59120 "Line 5 minus line 9 (if negative, enter "0") =".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/spouse_income_for_transfer",
            "less": "ca-on/spouse_credits_used",
        },
        produces={"output": "ca-on/spouse_adjusted_taxable_income"},
    ),
    # Schedule ON(S2) line 11 "Line 4 minus line 10 (if negative, enter "0")".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca-on/spouse_transferable_amounts",
            "less": "ca-on/spouse_adjusted_taxable_income",
        },
        produces={"output": "ca-on/spouse_unused_amounts"},
    ),
    # Schedule ON(S2) "You can claim these amounts if you are eligible to claim the equivalent
    # federal amounts on your federal Schedule 2." and line 11 "Enter this amount on line 58640 of
    # your Form ON428. Provincial amounts transferred from your spouse or common-law partner",
    # ON428 line 34 and line 58640 "Amounts transferred from your spouse or common-law partner
    # (attach Schedule ON(S2))": line 11 is counted once when the filer was not separated for 90
    # days or more including December 31, 2025 and not at all when separated, the federal Schedule
    # 2's caller count again.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca-on/spouse_unused_amounts",
            "count": "ca/spouse_not_separated_90_days_checked",
        },
        produces={"output": "ca-on/amounts_transferred_from_spouse"},
    ),
}

WIRING = {
    (ProgressiveTax, frozenset({TAXABLE_INCOME}), frozenset({ONTARIO_BASIC_TAX})),
    (CreditAmount, frozenset(), frozenset({ontario.BASIC_PERSONAL_AMOUNT})),
    (ApplyRate, frozenset({NET_INCOME}), frozenset({ontario.MEDICAL_NET_INCOME_SHARE})),
    (
        CappedAmount,
        frozenset({ontario.MEDICAL_NET_INCOME_SHARE}),
        frozenset({ontario.MEDICAL_THRESHOLD}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({MEDICAL_EXPENSES, ontario.MEDICAL_THRESHOLD}),
        frozenset({ontario.MEDICAL_EXPENSES_OVER_THRESHOLD}),
    ),
    (
        OtherDependantsMedical,
        frozenset({OTHER_DEPENDANTS}),
        frozenset({ontario.OTHER_DEPENDANTS_MEDICAL}),
    ),
    (
        Sum,
        frozenset({ontario.MEDICAL_EXPENSES_OVER_THRESHOLD, ontario.OTHER_DEPENDANTS_MEDICAL}),
        frozenset({ontario.MEDICAL_CLAIM}),
    ),
    (CreditAmount, frozenset(), frozenset({ontario.AGE_MAXIMUM})),
    (CreditAmount, frozenset(), frozenset({ontario.AGE_INCOME_THRESHOLD})),
    (
        SubtractNotBelowZero,
        frozenset({TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO, ontario.AGE_INCOME_THRESHOLD}),
        frozenset({ontario.AGE_INCOME_OVER_THRESHOLD}),
    ),
    (
        ApplyRate,
        frozenset({ontario.AGE_INCOME_OVER_THRESHOLD}),
        frozenset({ontario.AGE_REDUCTION}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({ontario.AGE_MAXIMUM, ontario.AGE_REDUCTION}),
        frozenset({ontario.AGE_AMOUNT_BEFORE_COUNT}),
    ),
    (
        TimesCount,
        frozenset({ontario.AGE_AMOUNT_BEFORE_COUNT, BORN_IN_1960_OR_EARLIER_CHECKED}),
        frozenset({ontario.AGE_AMOUNT}),
    ),
    (CreditAmount, frozenset(), frozenset({ontario.SPOUSE_BASE})),
    (
        SubtractNotBelowZero,
        frozenset({ontario.SPOUSE_BASE, SPOUSE_NET_INCOME}),
        frozenset({ontario.SPOUSE_AMOUNT_BEFORE_MAXIMUM}),
    ),
    (
        CappedAmount,
        frozenset({ontario.SPOUSE_AMOUNT_BEFORE_MAXIMUM}),
        frozenset({ontario.SPOUSE_AMOUNT_BEFORE_COUNT}),
    ),
    (
        TimesCount,
        frozenset({ontario.SPOUSE_AMOUNT_BEFORE_COUNT, SPOUSES_CLAIMED_CHECKED}),
        frozenset({ontario.SPOUSE_AMOUNT}),
    ),
    (CreditAmount, frozenset(), frozenset({ELIGIBLE_DEPENDANT_BASE})),
    (
        SubtractNotBelowZero,
        frozenset({ELIGIBLE_DEPENDANT_BASE, DEPENDANT_NET_INCOME}),
        frozenset({ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_MAXIMUM}),
    ),
    (
        CappedAmount,
        frozenset({ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_MAXIMUM}),
        frozenset({ontario.ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_COUNT}),
    ),
    (
        TimesCount,
        frozenset({ontario.ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_COUNT, ELIGIBLE_DEPENDANTS_CHECKED}),
        frozenset({ontario.ELIGIBLE_DEPENDANT_AMOUNT}),
    ),
    (
        OntarioCaregiverAmount,
        frozenset(
            {CAREGIVER_DEPENDANTS, ontario.ELIGIBLE_DEPENDANT_AMOUNT, ELIGIBLE_DEPENDANTS_CHECKED}
        ),
        frozenset({ontario.CAREGIVER_AMOUNT}),
    ),
    (
        OntarioCappedRecordTotal,
        frozenset({ADOPTION_EXPENSE_CHILDREN}),
        frozenset({ontario.ADOPTION_CREDIT}),
    ),
    (
        CappedAmount,
        frozenset({PENSION_INCOME_CREDIT}),
        frozenset({ontario.PENSION_INCOME_CREDIT}),
    ),
    (CreditAmount, frozenset(), frozenset({ontario.DISABILITY_SELF_BASE_AMOUNT})),
    (CreditAmount, frozenset(), frozenset({ontario.DISABILITY_SELF_SUPPLEMENT_MAXIMUM})),
    (CreditAmount, frozenset(), frozenset({ontario.DISABILITY_SELF_CARE_THRESHOLD})),
    (
        SubtractNotBelowZero,
        frozenset({DISABILITY_SELF_CARE_EXPENSES, ontario.DISABILITY_SELF_CARE_THRESHOLD}),
        frozenset({ontario.DISABILITY_SELF_CARE_OVER_THRESHOLD}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {
                ontario.DISABILITY_SELF_SUPPLEMENT_MAXIMUM,
                ontario.DISABILITY_SELF_CARE_OVER_THRESHOLD,
            }
        ),
        frozenset({ontario.DISABILITY_SELF_SUPPLEMENT}),
    ),
    (
        Sum,
        frozenset({ontario.DISABILITY_SELF_BASE_AMOUNT, ontario.DISABILITY_SELF_SUPPLEMENT}),
        frozenset({ontario.DISABILITY_SELF_WORKSHEET_AMOUNT}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                UNDER_18_ON_DECEMBER_31_CHECKED,
                ontario.DISABILITY_SELF_BASE_AMOUNT,
                ontario.DISABILITY_SELF_WORKSHEET_AMOUNT,
            }
        ),
        frozenset({ontario.DISABILITY_AMOUNT_FOR_SELF_IF_ELIGIBLE}),
    ),
    (
        TimesCount,
        frozenset(
            {ontario.DISABILITY_AMOUNT_FOR_SELF_IF_ELIGIBLE, ELIGIBLE_FOR_DISABILITY_AMOUNT_CHECKED}
        ),
        frozenset({ontario.DISABILITY_AMOUNT_FOR_SELF}),
    ),
    (
        OntarioDisabilityTransferAmount,
        frozenset({ontario.DISABILITY_DEPENDANTS}),
        frozenset({ontario.DISABILITY_TRANSFERRED_AMOUNT}),
    ),
    (
        AmountOrDividedByRate,
        frozenset({TAXABLE_INCOME, ONTARIO_BASIC_TAX}),
        frozenset({ontario.UNUSED_TUITION_INCOME_CAP}),
    ),
    (
        Sum,
        frozenset(
            {
                ontario.BASIC_PERSONAL_AMOUNT,
                ontario.AGE_AMOUNT,
                ontario.SPOUSE_AMOUNT,
                ontario.ELIGIBLE_DEPENDANT_AMOUNT,
                ontario.CAREGIVER_AMOUNT,
                CPP_BASE_CONTRIBUTIONS_ON_RETURN,
                CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
                EI_PREMIUMS,
                EI_PREMIUMS_ON_SELF_EMPLOYMENT,
                ontario.ADOPTION_CREDIT,
                ontario.PENSION_INCOME_CREDIT,
                ontario.DISABILITY_AMOUNT_FOR_SELF,
                ontario.DISABILITY_TRANSFERRED_AMOUNT,
            }
        ),
        frozenset({ontario.CREDIT_AMOUNTS_THROUGH_DISABILITY_TRANSFER}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {
                ontario.UNUSED_TUITION_INCOME_CAP,
                ontario.CREDIT_AMOUNTS_THROUGH_DISABILITY_TRANSFER,
            }
        ),
        frozenset({ontario.UNUSED_TUITION_ROOM}),
    ),
    (
        LesserOf,
        frozenset({ontario.UNUSED_TUITION_AMOUNTS_BROUGHT_FORWARD, ontario.UNUSED_TUITION_ROOM}),
        frozenset({ontario.UNUSED_TUITION_CLAIMED}),
    ),
    (
        Subtract,
        frozenset({ontario.UNUSED_TUITION_AMOUNTS_BROUGHT_FORWARD, ontario.UNUSED_TUITION_CLAIMED}),
        frozenset({ontario.UNUSED_TUITION_CARRIED_FORWARD}),
    ),
    (
        CreditAmount,
        frozenset(),
        frozenset({ontario.SPOUSE_RETURN_ONTARIO_PENSION_INCOME_AMOUNT_MAXIMUM}),
    ),
    (
        CreditAmount,
        frozenset(),
        frozenset({ontario.SPOUSE_RETURN_ONTARIO_DISABILITY_AMOUNT_MAXIMUM}),
    ),
    (
        AtMost,
        frozenset({ontario.SPOUSE_RETURN_ONTARIO_AGE_AMOUNT, ontario.AGE_MAXIMUM}),
        frozenset({ontario.SPOUSE_RETURN_ONTARIO_AGE_AMOUNT_CHECKED}),
    ),
    (
        AtMost,
        frozenset(
            {
                ontario.SPOUSE_RETURN_ONTARIO_PENSION_INCOME_AMOUNT,
                ontario.SPOUSE_RETURN_ONTARIO_PENSION_INCOME_AMOUNT_MAXIMUM,
            }
        ),
        frozenset({ontario.SPOUSE_RETURN_ONTARIO_PENSION_INCOME_AMOUNT_CHECKED}),
    ),
    (
        AtMost,
        frozenset(
            {
                ontario.SPOUSE_RETURN_ONTARIO_DISABILITY_AMOUNT,
                ontario.SPOUSE_RETURN_ONTARIO_DISABILITY_AMOUNT_MAXIMUM,
            }
        ),
        frozenset({ontario.SPOUSE_RETURN_ONTARIO_DISABILITY_AMOUNT_CHECKED}),
    ),
    (
        Sum,
        frozenset(
            {
                ontario.SPOUSE_RETURN_ONTARIO_AGE_AMOUNT_CHECKED,
                ontario.SPOUSE_RETURN_ONTARIO_PENSION_INCOME_AMOUNT_CHECKED,
                ontario.SPOUSE_RETURN_ONTARIO_DISABILITY_AMOUNT_CHECKED,
            }
        ),
        frozenset({ontario.SPOUSE_TRANSFERABLE_AMOUNTS}),
    ),
    (
        AmountOrDividedByRate,
        frozenset({SPOUSE_RETURN_TAXABLE_INCOME, ontario.SPOUSE_RETURN_ONTARIO_BASIC_TAX}),
        frozenset({ontario.SPOUSE_INCOME_FOR_TRANSFER}),
    ),
    (
        AtMost,
        frozenset(
            {ontario.SPOUSE_RETURN_ONTARIO_BASIC_PERSONAL_AMOUNT, ontario.BASIC_PERSONAL_AMOUNT}
        ),
        frozenset({ontario.SPOUSE_RETURN_ONTARIO_BASIC_PERSONAL_AMOUNT_CHECKED}),
    ),
    (
        Sum,
        frozenset(
            {
                ontario.SPOUSE_RETURN_ONTARIO_BASIC_PERSONAL_AMOUNT_CHECKED,
                ontario.SPOUSE_RETURN_ONTARIO_LINE_24,
                ontario.SPOUSE_RETURN_ONTARIO_UNUSED_TUITION_AMOUNT,
            }
        ),
        frozenset({ontario.SPOUSE_CREDITS_USED}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({ontario.SPOUSE_INCOME_FOR_TRANSFER, ontario.SPOUSE_CREDITS_USED}),
        frozenset({ontario.SPOUSE_ADJUSTED_TAXABLE_INCOME}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({ontario.SPOUSE_TRANSFERABLE_AMOUNTS, ontario.SPOUSE_ADJUSTED_TAXABLE_INCOME}),
        frozenset({ontario.SPOUSE_UNUSED_AMOUNTS}),
    ),
    (
        TimesCount,
        frozenset({ontario.SPOUSE_UNUSED_AMOUNTS, SPOUSE_NOT_SEPARATED_90_DAYS_CHECKED}),
        frozenset({ontario.AMOUNTS_TRANSFERRED_FROM_SPOUSE}),
    ),
}
