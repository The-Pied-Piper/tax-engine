"""The federal catalog: alternative minimum tax, Form T691.

Part 1 of the form: the adjusted taxable income, from the film property, the rental and leasing
property, the tax shelter amounts, the resource property, the capital gains, the gifts of
publicly listed securities, the security options deductions, the losses of other years, the
deductions, the non-deductible expenses, the applicable rate, the dividends, the lifetime capital
gains exemption, the capital gains deductions, the basic exemption, the federal tax rate and the
credits. Part 9 of the form: the resource
property and flow-through shares. Part 2 of the form: the basic federal tax. Part 8 of the form:
the minimum tax carryover applied on line 40427. Part 3 of the form: the federal surtax, the
federal tax payable and the regular net federal tax payable. Part 4 of the form: the special
foreign tax credit. Part 5 of the form: the obligation to pay alternative minimum tax, from the net
minimum tax payable to the alternative minimum tax payable. Part 6 of the form: the federal tax
payable under the alternative minimum tax, from the basic federal tax less the split income tax to
the greater of the federal tax with the surtax and the split income tax after the credits. Part 7 of
the form: the additional taxes paid for minimum tax carryover, from the basic federal tax with the
recapture to the foreign credit share. Part 8 of the form, from line 13: the balance of the minimum
tax carryover available for later years and the total available for 2026, less the unapplied 2018
carryover.
"""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.jurisdictions.ca.catalog.base import CATALOG

AMT_FILM_PROPERTY_CCA_AND_CARRYING_CHARGES = CATALOG.declare(
    "amt_film_property_cca_and_carrying_charges", Decimal, non_negative=True
)
"""Film property CCA and carrying charges, Form T691 Part 1 line 2 "Capital cost allowance (CCA)
and carrying charges (2) claimed on certified film property acquired before March 1996 (usually
included on lines 22100 and 23200 of your return)": a starting amount, the caller's figure."""

AMT_FILM_PROPERTY_INCOME_BEFORE_CCA = CATALOG.declare(
    "amt_film_property_income_before_cca", Decimal, non_negative=True
)
"""Net income from film property before CCA and carrying charges, Form T691 Part 1 line 3 "Net
income from film property before CCA and carrying charges (if negative, enter "0") (3)": a
starting amount, the caller's figure, not below zero."""

AMT_FILM_PROPERTY_ADJUSTMENT = CATALOG.declare(
    "amt_film_property_adjustment", Decimal, non_negative=True
)
"""Film property adjustment, Form T691 Part 1 line 4 (67820) "Line 2 minus line 3 (if negative,
enter "0")": line 2 less line 3, not below zero."""

AMT_RENTAL_PROPERTY_CCA_AND_CARRYING_CHARGES = CATALOG.declare(
    "amt_rental_property_cca_and_carrying_charges", Decimal, non_negative=True
)
"""Rental and leasing property CCA and carrying charges, Form T691 Part 1 line 5 "CCA and carrying
charges (2) claimed on rental and leasing property (included on line 12600 of your return)": a
starting amount, the caller's figure."""

AMT_RENTAL_PROPERTY_INCOME_BEFORE_CCA = CATALOG.declare(
    "amt_rental_property_income_before_cca", Decimal, non_negative=True
)
"""Net income from rental and leasing property before CCA and carrying charges, Form T691 Part 1
line 6 "Net income from rental and leasing property before CCA and carrying charges (if negative,
enter "0") (3)": a starting amount, the caller's figure, not below zero."""

AMT_RENTAL_PROPERTY_ADJUSTMENT = CATALOG.declare(
    "amt_rental_property_adjustment", Decimal, non_negative=True
)
"""Rental and leasing property adjustment, Form T691 Part 1 line 7 (67830) "Line 5 minus line 6 (if
negative, enter "0")": line 5 less line 6, not below zero."""

AMT_TAX_SHELTER_LOSSES = CATALOG.declare("amt_tax_shelter_losses", Decimal, non_negative=True)
"""Losses from partnerships that are tax shelters, Form T691 Part 1 line 8 "Losses from partnerships
that are tax shelters (4)": a starting amount, the caller's figure."""

AMT_TAX_SHELTER_DEDUCTIBLE_AMOUNTS = CATALOG.declare(
    "amt_tax_shelter_deductible_amounts", Decimal, non_negative=True
)
"""Amounts deductible for properties that are tax shelters, Form T691 Part 1 line 9 "Amounts
deductible for properties that are tax shelters (5)": a starting amount, the caller's figure."""

AMT_LIMITED_PARTNER_CARRYING_CHARGES = CATALOG.declare(
    "amt_limited_partner_carrying_charges", Decimal, non_negative=True
)
"""Carrying charges of a limited or non-active partner, Form T691 Part 1 line 10 "Carrying charges
(2) for acquiring an interest in a partnership of which you are a limited or non-active partner,
or which owns a rental or leasing property or a film property (included on line 22100 of your
return) (6)": a starting amount, the caller's figure."""

AMT_TAX_SHELTER_ADJUSTMENTS = CATALOG.declare(
    "amt_tax_shelter_adjustments", Decimal, non_negative=True
)
"""Tax shelters, limited partnerships and non-active partners adjustment, Form T691 Part 1 line 11
(67840) "Add lines 8 to 10.": lines 8, 9 and 10 added."""

AMT_PART_1_SUBTOTAL = CATALOG.declare("amt_part_1_subtotal", Decimal)
"""Adjusted taxable income subtotal, Form T691 Part 1 line 12 "Add lines 1, 4, 7, and 11.": the
signed taxable income of line 1 (`taxable_income_signed`, the amount that would be on line 26000
of the return if negative were shown in brackets) plus lines 4, 7 and 11, in line order. The
subtotal can be negative, so it is signed."""

AMT_RESOURCE_EXPENDITURES = CATALOG.declare("amt_resource_expenditures", Decimal, non_negative=True)
"""Resource expenditures, depletion allowances and carrying charges, Form T691 Part 9 line 1 "Total
of all resource expenditures, depletion allowances and carrying charges for resource property and
flow-through shares (included on lines 22100, 22400, and 23200 of your return)": a starting amount,
the caller's figure."""

AMT_RESOURCE_PRODUCTION_INCOME = CATALOG.declare(
    "amt_resource_production_income", Decimal, non_negative=True
)
"""Income from the production of petroleum, natural gas and minerals, Form T691 Part 9 line 2
"Income (including royalties) from production of petroleum, natural gas and minerals, before
carrying charges, resource expenditures, and depletion allowances included on line 1 (if negative,
enter "0")": a starting amount, the caller's figure, not below zero."""

AMT_RESOURCE_FOREIGN_PROPERTY_INCOME = CATALOG.declare(
    "amt_resource_foreign_property_income", Decimal, non_negative=True
)
"""Income from foreign resource properties, Form T691 Part 9 line 3 "Income from dispositions of
foreign resource properties, and recovery of exploration and development expenses before carrying
charges, resource expenditures and depletion allowances included on line 1 (if negative, enter
"0")": a starting amount, the caller's figure, not below zero."""

AMT_CLASS_43_1_INCOME = CATALOG.declare("amt_class_43_1_income", Decimal, non_negative=True)
"""Income from Class 43.1 or 43.2 property, Form T691 Part 9 line 4 "Income from property, or from a
business of selling the product of property, described in Class 43.1 or 43.2 in Schedule II of the
Income Tax Regulations before resource expenditures and depletion allowances included on line 1 (if
negative, enter "0")": a starting amount, the caller's figure, not below zero."""

AMT_RESOURCE_INCOME_TOTAL = CATALOG.declare("amt_resource_income_total", Decimal, non_negative=True)
"""Resource income total, Form T691 Part 9 line 5 "Add lines 2 to 4.": lines 2, 3 and 4 added."""

AMT_RESOURCE_PROPERTY_AND_FLOW_THROUGH_SHARES = CATALOG.declare(
    "amt_resource_property_and_flow_through_shares", Decimal, non_negative=True
)
"""Resource property and flow-through shares, Form T691 Part 9 line 6 "Line 1 minus line 5 (if
negative, enter "0")" and "Resource property and flow-through share 67860 =", the amount entered on
line 14 of Part 1: line 1 less line 5, not below zero."""

AMT_MORTGAGE_FORECLOSURE_CAPITAL_GAINS = CATALOG.declare(
    "amt_mortgage_foreclosure_capital_gains", Decimal
)
"""Capital gains or losses from mortgage foreclosures and conditional sales repossessions, Form
T691 Part 1 line 16 "Capital gains or losses arising from mortgage foreclosures and conditional
sales repossessions from lines 12400 and 15500 of Schedule 3": the two foreclosure totals of
Schedule 3, a loss in brackets."""

AMT_TREATY_EXEMPT_CAPITAL_GAINS = CATALOG.declare(
    "amt_treaty_exempt_capital_gains", Decimal, non_negative=True
)
"""Capital gains exempt under a tax treaty, Form T691 Part 1 line 17 "Part of total capital gains
included on line 15 that is exempt from Canadian tax under a tax treaty (included on line 25600 of
your return)": a starting amount, the caller's figure."""

AMT_TREATY_EXEMPT_CAPITAL_GAINS_CHECKED = CATALOG.declare(
    "amt_treaty_exempt_capital_gains_checked", Decimal, non_negative=True
)
"""Capital gains exempt under a tax treaty after the check, Form T691 Part 1 line 17 "Part of total
capital gains included on line 15 that is exempt from Canadian tax under a tax treaty (included on
line 25600 of your return)": the amount of `ca/amt_treaty_exempt_capital_gains` after the check that
it is not more than `ca/capital_gain` (`core/at_most`). Line 17 is part of line 15, so an amount
above it is an input error, not capped. Line 19 reads this amount."""

AMT_TREATY_EXEMPT_CAPITAL_GAINS_WITHIN_ADDITIONAL_DEDUCTIONS = CATALOG.declare(
    "amt_treaty_exempt_capital_gains_within_additional_deductions", Decimal, non_negative=True
)
"""Capital gains exempt under a tax treaty within line 25600, Form T691 Part 1 line 17 "(included on
line 25600 of your return)": the amount of `ca/amt_treaty_exempt_capital_gains_checked` after the
check that it is not more than `ca/additional_deductions_total` (`core/at_most`). Line 17 is
included on line 25600, so an amount above it is an input error, not capped. Line 19 reads this
amount."""

AMT_GRADUATED_RATE_ESTATE_CAPITAL_GAINS = CATALOG.declare(
    "amt_graduated_rate_estate_capital_gains", Decimal, non_negative=True
)
"""Capital gains from graduated rate estates, Form T691 Part 1 line 18 "Certain capital gains from
graduated rate estates (for details, contact its legal representative)": a starting amount, the
caller's figure."""

AMT_CAPITAL_GAINS_ADJUSTMENTS = CATALOG.declare("amt_capital_gains_adjustments", Decimal)
"""Capital gains adjustments, Form T691 Part 1 line 19 "Add lines 16 to 18.": lines 16, 17 and 18
added, a loss in brackets."""

AMT_NET_CAPITAL_GAINS_AFTER_ADJUSTMENTS = CATALOG.declare(
    "amt_net_capital_gains_after_adjustments", Decimal
)
"""Capital gains after adjustments, Form T691 Part 1 line 20 "Line 15 minus line 19 (if negative,
show in brackets)": the capital gain of line 15 (`capital_gain`, from line 19700 of Schedule 3)
less line 19, shown in brackets when negative."""

AMT_CAPITAL_GAINS_DIFFERENCE = CATALOG.declare("amt_capital_gains_difference", Decimal)
"""Capital gains after adjustments less the taxable capital gains, Form T691 Part 1 line 22 "Line 20
minus line 21 (if negative, do not show in brackets.)": line 20 less line 21 (line 12700 of the
return, the taxable capital gains), left signed."""

AMT_CAPITAL_GAINS_ADDED = CATALOG.declare("amt_capital_gains_added", Decimal)
"""Capital gains added, Form T691 Part 1 line 23 "If line 20 is positive, enter the amount from line
22. If line 20 is negative, enter whichever is less: the amount from line 21 or line 22 (show in
brackets).": line 22 when line 20 is not negative, otherwise the lesser of line 21 and line 22 as a
negative amount."""

AMT_CAPITAL_GAINS_ADDED_NOT_BELOW_ZERO = CATALOG.declare(
    "amt_capital_gains_added_not_below_zero", Decimal, non_negative=True
)
"""Capital gains added, not below zero: not a form line. Part 1 line 23 with a loss taken as 0, the
most Part 4 line 3 may claim, so a loss on line 23 still accepts a claim of 0."""

AMT_CAPITAL_GAIN_NOT_BELOW_ZERO = CATALOG.declare(
    "amt_capital_gain_not_below_zero", Decimal, non_negative=True
)
"""Capital gains of line 15, not below zero: not a form line. Part 1 line 15 with a loss taken as 0,
the most Part 1 line 17 may claim, so a loss on line 15 still accepts an amount of 0."""

AMT_PUBLICLY_LISTED_GIFTS_TOTAL = CATALOG.declare(
    "amt_publicly_listed_gifts_total", Decimal, non_negative=True
)
"""Capital gains on gifts of publicly listed securities, Form T691 Part 1 line 24 "Total amount of
lines 68230 and 68250 of Column 7 of Form T1170": a starting amount, the caller's figure."""

AMT_PUBLICLY_LISTED_GIFTS_T1170_LINE_68231 = CATALOG.declare(
    "amt_publicly_listed_gifts_t1170_line_68231", Decimal, non_negative=True
)
"""Amount from line 68231 of Form T1170, Form T691 Part 1 line 25 "Amount from line 68231 of Form
T1170": a starting amount, the caller's figure."""

AMT_PUBLICLY_LISTED_GIFTS_NET = CATALOG.declare("amt_publicly_listed_gifts_net", Decimal)
"""Capital gains on gifts of publicly listed securities less the T1170 amount, Form T691 Part 1 line
26 "Line 24 minus line 25": line 24 less line 25, a loss in brackets."""

AMT_PUBLICLY_LISTED_GIFTS_ADJUSTMENT = CATALOG.declare(
    "amt_publicly_listed_gifts_adjustment", Decimal
)
"""Adjustment for gifts of publicly listed securities, Form T691 Part 1 line 26 "× 30%" of "Line 24
minus line 25": the net of line 24 less line 25 at the 30% of its dataset, rounded to the cent,
a loss in brackets."""

AMT_ADJUSTED_INCOME_WITH_GAINS = CATALOG.declare("amt_adjusted_income_with_gains", Decimal)
"""Adjusted taxable income with the gains, Form T691 Part 1 line 27 "Add lines 13, 14, 23, and 26.":
line 13 (the amount from line 12), line 14 (the amount from line 6 of Part 9), line 23 and line 26
in line order, a loss in brackets."""

AMT_T1212_LINE_29_DEFERRED_SECURITY_OPTIONS = CATALOG.declare(
    "amt_t1212_line_29_deferred_security_options", Decimal, non_negative=True
)
"""Deferred security options benefits, Form T691 Part 1 line 29 "Amount from line 2 of Form T1212,
Statement of Deferred Security Options Benefits (7)": footnote (7) of the form says "If you disposed
of securities, include 50% of the amount from line 2 of Form T1212", so this is the 50% amount of
the form `ca/t1212`, read as the total of its one record."""

AMT_SECURITY_OPTIONS_D_TOTAL = CATALOG.declare(
    "amt_security_options_d_total", Decimal, non_negative=True
)
"""Security options deduction under paragraph 110(1)(d), Form T691 Part 1 line 30 "Line 28 plus
line 29" "67910 =": lines 28 and 29 added."""

AMT_SECURITY_OPTION_PUBLICLY_LISTED_GIFTS = CATALOG.declare(
    "amt_security_option_publicly_listed_gifts", Decimal, non_negative=True
)
"""Gifts of publicly listed securities acquired under a security option plan, Form T691 Part 1
line 31 "Gifts of publicly listed securities acquired under a security option plan included on line
24900 of your return" "67914": a starting amount, the caller's figure."""

AMT_SECURITY_OPTION_GIFTS_DEDUCTION = CATALOG.declare(
    "amt_security_option_gifts_deduction", Decimal, non_negative=True
)
"""Security option gifts deduction, Form T691 Part 1 line 31 "× 40% =": the 40% of line 31's gifts,
from its dataset, rounded to the cent."""

AMT_SECURITY_OPTIONS_NET = CATALOG.declare("amt_security_options_net", Decimal, non_negative=True)
"""Security options deduction net of the gifts deduction, Form T691 Part 1 line 32 "Line 30 minus
line 31 (if negative, enter "0")": line 30 less line 31, not below zero."""

AMT_PROSPECTOR_OR_GRUBSTAKER_DEDUCTION = CATALOG.declare(
    "amt_prospector_or_grubstaker_deduction", Decimal, non_negative=True
)
"""Deduction for a security received as a prospector or grubstaker, Form T691 Part 1 line 36
"Deduction included on line 24900 of your return for a security received as a prospector or
grubstaker": a starting amount, the caller's figure."""

AMT_DEFERRED_PROFIT_SHARING_PLAN_DEDUCTION = CATALOG.declare(
    "amt_deferred_profit_sharing_plan_deduction", Decimal, non_negative=True
)
"""Deduction for certain dispositions of securities from a deferred profit-sharing plan, Form T691
Part 1 line 37 "Deduction included on line 24900 of your return for certain dispositions of
securities received from a deferred profit-sharing plan": a starting amount, the caller's figure."""

AMT_SECURITY_OPTIONS_D1_TOTAL = CATALOG.declare(
    "amt_security_options_d1_total", Decimal, non_negative=True
)
"""Security options deductions under paragraph 110(1)(d.1), Form T691 Part 1 line 38 "Add lines 35
to 37." "67918 =": lines 35, 36 and 37 added."""

AMT_LIMITED_PARTNERSHIP_DIFFERENCE_NO_ELECTION = CATALOG.declare(
    "amt_limited_partnership_difference_no_election", Decimal, non_negative=True
)
"""Limited partnership losses difference with no election, Form T691 Part 1 line 39 "If you have
not filed an election (8), enter the difference between those losses and the amount of losses
deductible (9) for AMT purposes": a starting amount, the caller's figure."""

AMT_LIMITED_PARTNERSHIP_DIFFERENCE_ELECTION = CATALOG.declare(
    "amt_limited_partnership_difference_election", Decimal, non_negative=True
)
"""Limited partnership losses difference with an election, Form T691 Part 1 line 40 "If you have
filed an election (8), enter the difference between those losses and the amount of losses
deductible (9) for AMT purposes": a starting amount, the caller's figure, from line 67920."""

AMT_NON_CAPITAL_LOSSES_DIFFERENCE = CATALOG.declare(
    "amt_non_capital_losses_difference", Decimal, non_negative=True
)
"""Non-capital losses difference, Form T691 Part 1 line 41 "If you claimed non-capital losses,
including restricted farm losses or farm losses, incurred in another year on line 25200 of your
2025 return, indicate the difference between those losses and the losses that are deductible for
AMT purposes": a starting amount, the caller's figure."""

AMT_NON_CAPITAL_LOSSES_DIFFERENCE_CHECKED = CATALOG.declare(
    "amt_non_capital_losses_difference_checked", Decimal, non_negative=True
)
"""Non-capital losses difference after the check, Form T691 Part 1 line 41 "indicate the difference
between those losses and the losses that are deductible for AMT purposes": the amount of
`ca/amt_non_capital_losses_difference` after the check that it is not more than the non-capital
losses on line 25200 of the return, `ca/non_capital_losses_on_line_25200`
(`core/at_most`). The difference cannot exceed the losses, as line 50 subtracts it from them, so an
amount above them is an input error, not capped. Lines 43 and 50 read this amount."""

AMT_NET_CAPITAL_LOSSES_DIFFERENCE = CATALOG.declare(
    "amt_net_capital_losses_difference", Decimal, non_negative=True
)
"""Net capital losses difference, Form T691 Part 1 line 42 "If you claimed net capital losses,
incurred in another year on line 25300 of your 2025 return, indicate the difference between those
losses and the losses that are deductible for AMT purposes": a starting amount, the caller's
figure, from line 67922."""

AMT_NET_CAPITAL_LOSSES_DIFFERENCE_CHECKED = CATALOG.declare(
    "amt_net_capital_losses_difference_checked", Decimal, non_negative=True
)
"""Net capital losses difference after the check, Form T691 Part 1 line 42 "indicate the difference
between those losses and the losses that are deductible for AMT purposes": the amount of
`ca/amt_net_capital_losses_difference` after the check that it is not more than the net capital
losses of other years on line 25300 of the return, `ca/net_capital_losses_of_other_years`
(`core/at_most`). The difference cannot exceed those losses, so an amount above them is an input
error, not capped. Line 43 reads this amount."""

AMT_OTHER_YEARS_LOSSES_TOTAL = CATALOG.declare(
    "amt_other_years_losses_total", Decimal, non_negative=True
)
"""Losses of other years difference, Form T691 Part 1 line 43 "Line 39 or 40, as applicable, plus
line 41 and 42": the one of lines 39 and 40 that applies, with lines 41 and 42, in line order."""

AMT_LIMITED_PARTNERSHIP_DIFFERENCE_APPLIED = CATALOG.declare(
    "amt_limited_partnership_difference_applied", Decimal, non_negative=True
)
"""Limited partnership losses difference applied, Form T691 Part 1 line 46 "Amount from line 39 or
40, as applicable": the one of lines 39 and 40 that applies."""

AMT_LIMITED_PARTNERSHIP_DIFFERENCE_APPLIED_CHECKED = CATALOG.declare(
    "amt_limited_partnership_difference_applied_checked", Decimal, non_negative=True
)
"""Limited partnership losses difference applied after the check, Form T691 Part 1 line 46 "Amount
from line 39 or 40, as applicable": the amount of `ca/amt_limited_partnership_difference_applied`
after the check that it is not more than the limited partnership losses of other years on line
25100 of the return, `ca/limited_partnership_losses_of_other_years_checked` (`core/at_most`). The
difference cannot exceed the losses, as line 47 subtracts it from them, so an amount above them is
an input error, not capped. Line 47 reads this amount."""

AMT_LIMITED_PARTNERSHIP_LOSSES_ADJUSTMENT = CATALOG.declare(
    "amt_limited_partnership_losses_adjustment", Decimal
)
"""Limited partnership losses of other years adjustment, Form T691 Part 1 line 47 "Line 45 minus
line 46": the limited partnership losses of other years (line 25100 of the return) less line 46, a
loss in brackets."""

AMT_NON_CAPITAL_LOSSES_ADJUSTMENT = CATALOG.declare("amt_non_capital_losses_adjustment", Decimal)
"""Non-capital losses of other years adjustment, Form T691 Part 1 line 50 "Line 48 minus line 49":
the non-capital losses of other years (line 25200 of the return) less line 49, a loss in
brackets."""

AMT_LOSSES_AND_DEDUCTIONS_SUBTOTAL = CATALOG.declare("amt_losses_and_deductions_subtotal", Decimal)
"""Losses and deductions subtotal, Form T691 Part 1 line 53 "Add lines 47, 50, 51, and 52.": lines
47, 50, 51 (the union dues of line 21200) and 52 (the child care expenses of line 21400), a loss in
brackets when line 47 or 50 is one."""

AMT_PPIP_PREMIUMS_DEDUCTION = CATALOG.declare(
    "amt_ppip_premiums_deduction", Decimal, non_negative=True
)
"""Deduction for PPIP premiums on self-employment income, Form T691 Part 1 line 59 "Deduction for
PPIP premiums on self-employment income from line 22300 of your return (Quebec only)": a starting
amount, the caller's figure. A resident of Ontario on December 31, 2025 has no such line, so an
amount above 0 is refused (see `amt_ppip_premiums_in_ontario_checked`)."""

AMT_DEDUCTIONS_TOTAL = CATALOG.declare("amt_deductions_total", Decimal)
"""Deductions total, Form T691 Part 1 line 63 "Add lines 54 to 62.": line 53 carried and lines 55
to 62 in line order, a loss in brackets when line 53 is one."""

AMT_NON_DEDUCTIBLE_INTEREST = CATALOG.declare(
    "amt_non_deductible_interest", Decimal, non_negative=True
)
"""Interest expenses on money borrowed to earn income, Form T691 Part 1 line 64 "Interest expenses
on money borrowed to earn income or to purchase an annuity contract (included on line 22100 of your
return)": a starting amount, the caller's figure."""

AMT_LIFE_INSURANCE_PREMIUMS_AS_COLLATERAL = CATALOG.declare(
    "amt_life_insurance_premiums_as_collateral", Decimal, non_negative=True
)
"""Premiums on life insurance policies used as collateral, Form T691 Part 1 line 65 "Premiums on
life insurance policies used as collateral for money borrowed to earn income from property
(included on line 22100 of your return)": a starting amount, the caller's figure."""

AMT_FINANCING_EXPENSES = CATALOG.declare("amt_financing_expenses", Decimal, non_negative=True)
"""Financing expenses on money borrowed to earn income from property, Form T691 Part 1 line 66
"Financing expenses on money borrowed to earn income from property (included on line 22100 of your
return)": a starting amount, the caller's figure."""

AMT_INVESTMENT_COUNSEL_FEES = CATALOG.declare(
    "amt_investment_counsel_fees", Decimal, non_negative=True
)
"""Investment counsel fees, Form T691 Part 1 line 67 "Investment counsel fees (included on line
22100 of your return)": a starting amount, the caller's figure."""

AMT_NON_DEDUCTIBLE_PROPERTY_EXPENSES = CATALOG.declare(
    "amt_non_deductible_property_expenses", Decimal, non_negative=True
)
"""Non-deductible property expenses, Form T691 Part 1 line 68 "Add lines 64 to 67" "67924 =": lines
64 to 67 added."""

AMT_COMMISSION_EMPLOYMENT_EXPENSES = CATALOG.declare(
    "amt_commission_employment_expenses", Decimal, non_negative=True
)
"""Employment expenses of a commission employee, Form T691 Part 1 line 70 "Employment expenses
claimed and calculated as a commission employee (excluding amounts claimed as a salaried
employee)": a starting amount, the caller's figure."""

AMT_LEGAL_AND_ACCOUNTING_EXPENSES = CATALOG.declare(
    "amt_legal_and_accounting_expenses", Decimal, non_negative=True
)
"""Legal and accounting expenses, Form T691 Part 1 line 71 "Legal and accounting expenses": a
starting amount, the caller's figure."""

AMT_REPAYMENT_OF_SALARY_AND_WAGES = CATALOG.declare(
    "amt_repayment_of_salary_and_wages", Decimal, non_negative=True
)
"""Repayment of salary and wages, Form T691 Part 1 line 72 "Repayment of salary and wages": a
starting amount, the caller's figure."""

AMT_EXCESS_EPSP_AMOUNTS = CATALOG.declare("amt_excess_epsp_amounts", Decimal, non_negative=True)
"""Excess Employee Profits Share Plan amounts, Form T691 Part 1 line 73 "Excess Employee Profits
Share Plan (EPSP) amounts": a starting amount, the caller's figure."""

AMT_FORFEITED_SALARY_DEFERRAL_AMOUNTS = CATALOG.declare(
    "amt_forfeited_salary_deferral_amounts", Decimal, non_negative=True
)
"""Forfeited amounts under a salary deferral arrangement or an EPSP, Form T691 Part 1 line 74
"Forfeited amounts under a salary deferral arrangement or an EPSP": a starting amount, the caller's
figure."""

AMT_REPAYMENT_OF_WAGE_LOSS_REPLACEMENT = CATALOG.declare(
    "amt_repayment_of_wage_loss_replacement", Decimal, non_negative=True
)
"""Repayment of a wage loss replacement, Form T691 Part 1 line 75 "Repayment of a wage loss
replacement that was a top-up disability payment": a starting amount, the caller's figure."""

AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES = CATALOG.declare(
    "amt_non_deductible_office_expenses", Decimal, non_negative=True
)
"""Non-deductible office and employment expenses, Form T691 Part 1 line 76 "Add lines 70 to 75."
"67926 =": lines 70 to 75 added."""

AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES_CHECKED = CATALOG.declare(
    "amt_non_deductible_office_expenses_checked", Decimal, non_negative=True
)
"""Non-deductible office and employment expenses after the check, Form T691 Part 1 line 76 "Add
lines 70 to 75.": the amount of `ca/amt_non_deductible_office_expenses` after the check that it is
not more than line 69, `ca/other_employment_expenses` (`core/at_most`). Line 77 "Line 69 minus line
76" has no floor, so lines 70 to 75 are parts of line 69, and an amount above it is an input error,
not capped. Line 77 reads this amount."""

AMT_OFFICE_EXPENSES_ADJUSTMENT = CATALOG.declare("amt_office_expenses_adjustment", Decimal)
"""Office and employment expenses adjustment, Form T691 Part 1 line 77 "Line 69 minus line 76": the
other employment expenses (line 22900 of the return) less line 76, a loss in brackets."""

AMT_ADJUSTMENTS_BEFORE_RATE_TOTAL = CATALOG.declare("amt_adjustments_before_rate_total", Decimal)
"""Adjustments before the applicable rate, Form T691 Part 1 line 78 "Add lines 63, 68, and 77.":
lines 63, 68 and 77 in line order, a loss in brackets when line 63 or 77 is one."""

AMT_APPLICABLE_RATE_AMOUNT = CATALOG.declare("amt_applicable_rate_amount", Decimal)
"""Applicable rate amount, Form T691 Part 1 line 80 "Line 78 multiply by the percentage from line
79": line 78 times the applicable rate of line 79 "Applicable Rate" "× 50%" from its dataset,
rounded to the cent, a loss in brackets when line 78 is one."""

AMT_ADJUSTED_INCOME_WITH_SECURITY_OPTIONS = CATALOG.declare(
    "amt_adjusted_income_with_security_options", Decimal
)
"""Adjusted taxable income with the security options, Form T691 Part 1 line 33 "Line 27 plus line
32": line 27 and line 32 added, a loss in brackets."""

AMT_SECURITY_OPTIONS_AND_LOSSES_TOTAL = CATALOG.declare(
    "amt_security_options_and_losses_total", Decimal
)
"""Adjusted taxable income with the losses of other years, Form T691 Part 1 line 44 "Add lines 34,
38, and 43.": line 34 (the amount from line 33), line 38 and line 43 in line order, a loss in
brackets."""

AMT_ADJUSTMENTS_AFTER_RATE_TOTAL = CATALOG.declare("amt_adjustments_after_rate_total", Decimal)
"""Adjustments after the applicable rate, Form T691 Part 1 line 82 "Line 80 plus line 81": line 80
and line 81 (the amount from line 44) added, a loss in brackets."""

AMT_DIVIDENDS_OTHER_THAN_ELIGIBLE_ADJUSTMENT = CATALOG.declare(
    "amt_dividends_other_than_eligible_adjustment", Decimal, non_negative=True
)
"""Dividends other than eligible adjustment, Form T691 Part 1 line 84 "B × 13.0435%": B, the
taxable dividends other than eligible of line 12010 of the return, at the 13.0435% of its dataset,
rounded to the cent."""

AMT_AMOUNT_A_MINUS_AMOUNT_B = CATALOG.declare("amt_amount_a_minus_amount_b", Decimal)
"""Amount A minus amount B, Form T691 Part 1 line 85 "Amount A minus Amount B =": amount A, the
taxable dividends of line 12000 of the return, less amount B, line 12010 of the return."""

AMT_DIVIDENDS_DIFFERENCE_ADJUSTMENT = CATALOG.declare(
    "amt_dividends_difference_adjustment", Decimal
)
"""Dividends difference adjustment, Form T691 Part 1 line 85 "C × 27.5362% =": C, amount A minus
amount B, at the 27.5362% of its dataset, rounded to the cent."""

AMT_DIVIDENDS_ADJUSTMENTS_TOTAL = CATALOG.declare("amt_dividends_adjustments_total", Decimal)
"""Dividends adjustments, Form T691 Part 1 line 86 "Line 84 plus line 85": line 84 and line 85
added."""

AMT_LIFETIME_EXEMPTION_ADJUSTMENT = CATALOG.declare(
    "amt_lifetime_exemption_adjustment", Decimal, non_negative=True
)
"""Lifetime capital gains exemption adjustment, Form T691 Part 1 line 87 "Enter the amount from line
25400 of your return" "× 40% =": line 25400 at the 40% of its dataset, rounded to the cent."""

AMT_ADJUSTMENTS_WITH_LIFETIME_EXEMPTION_TOTAL = CATALOG.declare(
    "amt_adjustments_with_lifetime_exemption_total", Decimal
)
"""Adjustments with the lifetime capital gains exemption, Form T691 Part 1 line 88 "Line 86 plus
line 87": line 86 and line 87 added."""

AMT_QBT_CAPITAL_GAINS_DEDUCTION_DOUBLED = CATALOG.declare(
    "amt_qbt_capital_gains_deduction_doubled", Decimal, non_negative=True
)
"""Capital gains deduction on a qualifying business transfer doubled, Form T691 Part 1 line 89
"Amount from line 25395 of your return" "× 2 =": line 25395 times 2, rounded to the cent."""

AMT_QBT_CAPITAL_GAINS_DEDUCTION_DIFFERENCE = CATALOG.declare(
    "amt_qbt_capital_gains_deduction_difference", Decimal, non_negative=True
)
"""Capital gains deduction on a qualifying business transfer difference, Form T691 Part 1 line 91
"line 89 minus line 90": line 89 less line 90, the amount from line 25395 of the return."""

AMT_CAPITAL_GAINS_DEDUCTIONS_TOTAL = CATALOG.declare("amt_capital_gains_deductions_total", Decimal)
"""Capital gains deductions, Form T691 Part 1 line 92 "Line 88 plus line 91": line 88 and line 91
added."""

AMT_ADJUSTED_TAXABLE_INCOME = CATALOG.declare(
    "amt_adjusted_taxable_income", Decimal, non_negative=True
)
"""Adjusted taxable income, Form T691 Part 1 line 93 "Line 83 minus line 92 (if negative, enter
"0")": line 83 (the amount from line 82) less line 92, not below zero."""

AMT_BASIC_EXEMPTION = CATALOG.declare("amt_basic_exemption", Decimal, non_negative=True)
"""Basic exemption, Form T691 Part 1 line 94 "Basic exemption" "177,882.00": the printed amount of
its dataset, claimed whole."""

AMT_NET_ADJUSTED_TAXABLE_INCOME = CATALOG.declare(
    "amt_net_adjusted_taxable_income", Decimal, non_negative=True
)
"""Net adjusted taxable income, Form T691 Part 1 line 95 "Line 93 minus line 94 (if negative, enter
"0")": line 93 less line 94, not below zero."""

AMT_GROSS_MINIMUM_AMOUNT = CATALOG.declare("amt_gross_minimum_amount", Decimal, non_negative=True)
"""Gross minimum amount, Form T691 Part 1 line 97 "Gross minimum amount: line 95 multiplied by the
percentage on line 96.": line 95 at the 20.5% federal tax rate of line 96 from its dataset, rounded
to the cent."""

AMT_NON_REFUNDABLE_CREDITS_ADJUSTMENT = CATALOG.declare(
    "amt_non_refundable_credits_adjustment", Decimal, non_negative=True
)
"""Net non-refundable tax credits adjustment, Form T691 Part 1 line 98 "Net non-refundable tax
credits (line 33800 of your return)" "× 50% =": line 33800 at the 50% of its dataset, rounded to
the cent."""

AMT_DONATIONS_AND_GIFTS_ADJUSTMENT = CATALOG.declare(
    "amt_donations_and_gifts_adjustment", Decimal, non_negative=True
)
"""Donations and gifts adjustment, Form T691 Part 1 line 99 "Donations and gifts (line 34900 of your
return)" "× 80% =": line 34900 at the 80% of its dataset, rounded to the cent."""

AMT_SECTION_119_FORMER_RESIDENT_CREDIT = CATALOG.declare(
    "amt_section_119_former_resident_credit", Decimal, non_negative=True
)
"""Section 119 former resident credit, Form T691 Part 1 line 101 "Section 119 former resident
credit": a starting amount, the caller's figure."""

AMT_CREDITS_ADJUSTMENTS_TOTAL = CATALOG.declare(
    "amt_credits_adjustments_total", Decimal, non_negative=True
)
"""Credits adjustments, Form T691 Part 1 line 102 "Add lines 98 to 101.": lines 98, 99, 100 and 101
added."""

AMT_MINIMUM_AMOUNT = CATALOG.declare("amt_minimum_amount", Decimal, non_negative=True)
"""Minimum amount, Form T691 Part 1 line 103 "Line 97 minus line 102 (if negative, enter "0")":
line 97 less line 102, not below zero."""


AMT_CREDITS_TOTAL = CATALOG.declare("amt_credits_total", Decimal, non_negative=True)
"""Total of the credits, Form T691 Part 2 line 4 "Line 2 plus line 3": line 2 "Total non-refundable
tax credits (line 35000 of your return)" and line 3 "Dividend tax credit (line 40425 of your
return)", in line order."""

AMT_TAX_PAYABLE_BEFORE_MINIMUM_TAX_CARRYOVER = CATALOG.declare(
    "amt_tax_payable_before_minimum_tax_carryover", Decimal
)
"""Tax payable before minimum tax carryover, Form T691 Part 2 line 5 "Line 1 minus line 4" "Tax
payable before minimum tax carryover": line 1 "Enter the amount from line 40400 of your return"
less line 4. The form prints no floor, so the difference may be negative."""

AMT_BASIC_FEDERAL_TAX = CATALOG.declare("amt_basic_federal_tax", Decimal)
"""Basic federal tax, Form T691 Part 2 line 7 "Line 5 minus line 6" "Basic federal tax": line 5
less line 6, the minimum tax carryover applied in 2025 from line 12 of Part 8. The form prints no
floor, so the difference may be negative."""

AMT_MINIMUM_TAX_CARRYOVER_FROM_PREVIOUS_YEARS = CATALOG.declare(
    "amt_minimum_tax_carryover_from_previous_years", Decimal, non_negative=True
)
"""Minimum tax carryover from previous years, Form T691 Part 8 line 1 "Minimum tax carryover from
previous years (2018 to 2024)": a starting amount, the caller's figure from earlier returns."""

AMT_TAX_PAYABLE_WITH_ITC_RECAPTURE = CATALOG.declare("amt_tax_payable_with_itc_recapture", Decimal)
"""Tax payable with the investment tax credit recapture, Form T691 Part 8 line 4 "Line 2 plus line
3": line 2 "Tax payable before minimum tax carryover from line 5 of Part 2" and line 3 "Recapture of
investment tax credit from line 3 of Part C of Form T2038(IND)" (`itc_recapture`), in line order."""

AMT_SPLIT_INCOME_AND_CREDITS_TOTAL = CATALOG.declare(
    "amt_split_income_and_credits_total", Decimal, non_negative=True
)
"""Split income tax and credits, Form T691 Part 8 line 8 "Add lines 5 to 7": line 5 "Federal tax on
split income from line 8 of Form T1206", line 6 "Federal logging tax credit" (line 133 of
the return, as on Part 1 line 100) and line 7 "Amount from line 41600 of your return", in line
order."""

AMT_TAX_PAYABLE_AFTER_CREDITS = CATALOG.declare("amt_tax_payable_after_credits", Decimal)
"""Tax payable after credits, Form T691 Part 8 line 9 "Line 4 minus line 8": line 4 less line 8.
The form prints no floor, so the difference may be negative."""

AMT_MAXIMUM_CARRYOVER_APPLIED = CATALOG.declare(
    "amt_maximum_carryover_applied", Decimal, non_negative=True
)
"""Maximum carryover that can be applied in 2025, Form T691 Part 8 line 11 "Maximum carryover that
can be applied in 2025: line 9 minus line 10 (if negative, enter "0")": line 9 less line 10, the
minimum amount from line 103 of Part 1, not below zero."""

AMT_MAXIMUM_CARRYOVER_CLAIM = CATALOG.declare(
    "amt_maximum_carryover_claim", Decimal, non_negative=True
)
"""Largest claim on the minimum tax carryover, Form T691 Part 8 line 12 "Claim an amount that is not
more than line 1 or 11, whichever is less.": the lesser of line 1 and line 11. The form does not
print it; it is the bound the claim is checked against."""

AMT_MINIMUM_TAX_CARRYOVER_APPLIED = CATALOG.declare(
    "amt_minimum_tax_carryover_applied", Decimal, non_negative=True
)
"""Minimum tax carryover applied in 2025, Form T691 Part 8 line 12 "Claim an amount that is not more
than line 1 or 11, whichever is less." "Enter this amount on line 40427 of your return.": the amount
the filer chooses to claim, an input; Part 2 line 6 "Minimum tax carryover applied in 2025 from line
12 of Part 8" and T1 line 124 (line 40427) read it. It may not exceed the lesser of lines 1 and 11,
which `amt_minimum_tax_carryover_within_maximum` checks."""

AMT_MINIMUM_TAX_CARRYOVER_WITHIN_MAXIMUM = CATALOG.declare(
    "amt_minimum_tax_carryover_within_maximum", Decimal, non_negative=True
)
"""Minimum tax carryover within the largest claim, Form T691 Part 8 line 12 "Claim an amount that is
not more than line 1 or 11, whichever is less.": the claim, passed on when it is not above the
largest claim, and refused when it is. Part 8 line 13 reads it; the other readers of line 12 read
the claim itself, because line 11 reads line 41600."""

AMT_FEDERAL_SURTAX_AT_48_PERCENT = CATALOG.declare("amt_federal_surtax_at_48_percent", Decimal)
"""Federal surtax at 48 percent, Form T691 Part 3 line 2 "Federal surtax on business income earned
outside Canada" "Multiply the amount from line 1 by 48%.": line 1, the basic federal tax of Part 2
line 7, times the 48% of its dataset, rounded to the cent. The form prints no floor, so a negative
basic federal tax gives a negative surtax."""

AMT_T2203_COLUMN_5_PERCENTAGE = CATALOG.declare(
    "amt_t2203_column_5_percentage", Decimal, non_negative=True
)
"""Percentage in Column 5 of line 52220 of Form T2203, Form T691 Part 3 line 3 "If you have to pay
tax to multiple jurisdictions, multiply the amount from line 2 by the percentage in Column 5 of line
52220 on Form T2203.": a starting percentage, the caller's figure as the form prints it (50 for
50%), 0 when there is no tax to multiple jurisdictions."""

AMT_T2203_COLUMN_5_PERCENTAGE_MAXIMUM = CATALOG.declare(
    "amt_t2203_column_5_percentage_maximum", Decimal, non_negative=True
)
"""Largest percentage in Column 5 of line 52220 of Form T2203, Form T691 Part 3 line 3 "multiply the
amount from line 2 by the percentage in Column 5 of line 52220 on Form T2203.": the whole of the
amount, 100%, from a dataset, as the form prints a percentage (100 for 100%). The form prints no
maximum; the limit is a choice, not a form rule."""

AMT_T2203_COLUMN_5_PERCENTAGE_CHECKED = CATALOG.declare(
    "amt_t2203_column_5_percentage_checked", Decimal, non_negative=True
)
"""Percentage in Column 5 of line 52220 of Form T2203 after the check, Form T691 Part 3 line 3
"multiply the amount from line 2 by the percentage in Column 5 of line 52220 on Form T2203.": the
percentage of `ca/amt_t2203_column_5_percentage` after the check that it is not more than
`ca/amt_t2203_column_5_percentage_maximum` (`core/at_most`), entered as the form prints it. The form
prints no maximum, so the refusal above 100 is a choice, not a form rule. The readers of the
percentage read this kind."""

AMT_FEDERAL_SURTAX_MULTIPLE_JURISDICTIONS = CATALOG.declare(
    "amt_federal_surtax_multiple_jurisdictions", Decimal
)
"""Federal surtax for multiple jurisdictions, Form T691 Part 3 line 3 "If you have to pay tax to
multiple jurisdictions, multiply the amount from line 2 by the percentage in Column 5 of line 52220
on Form T2203.": line 2 times the percentage of Form T2203, rounded once to the cent. The form
prints no floor, so the product may be negative."""

AMT_NON_RESIDENT_OR_DEEMED_RESIDENT = CATALOG.declare(
    "amt_non_resident_or_deemed_resident", int, non_negative=True
)
"""Non-resident or deemed resident, Form T691 Part 3 line 4 "If not, and you are a non-resident or
deemed resident, enter the amount from line 2.": a yes or no count, 1 when you are a non-resident or
deemed resident and 0 otherwise, a starting count. A count of 2 or more is refused by
`ca/amt_non_resident_or_deemed_resident_checked` (`ca/yes_or_no_count`), not read as a second
surtax."""

AMT_NON_RESIDENT_OR_DEEMED_RESIDENT_CHECKED = CATALOG.declare(
    "amt_non_resident_or_deemed_resident_checked", int, non_negative=True
)
"""Non-resident or deemed resident, Form T691 Part 3 line 4 "If not, and you are a non-resident or
deemed resident, enter the amount from line 2.": the answer of
`ca/amt_non_resident_or_deemed_resident` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

AMT_SUBJECT_TO_MINIMUM_TAX = CATALOG.declare("amt_subject_to_minimum_tax", int, non_negative=True)
"""Subject to minimum tax, Form T2203 Part 2 "If you are subject to minimum tax, do not complete
lines 4 to 10. Instead, calculate the federal surtax on income you allocated to "Other (Outside
Canada)" on Form T691 and enter it on line 10.": a yes or no count, 1 when you are subject to
minimum tax and 0 otherwise, the caller's choice. It is an input and not derived from Form T691 Part
5 line 11 (`amt_part_5_line_11_is_positive`): that line reads the federal foreign tax credit (line
129), which the surtax of line 127 feeds, so deriving it there would be a cycle through the federal
foreign tax credit."""

AMT_LINE_3_HAS_AMOUNT = CATALOG.declare("amt_line_3_has_amount", int, non_negative=True)
"""You have an amount on line 3, Form T691 Part 3 line 4 "If you have an amount on line 3, enter
that amount.": 1 when line 3 is not 0, and 0 otherwise, the count of the condition."""

AMT_FEDERAL_SURTAX_IF_NON_RESIDENT = CATALOG.declare("amt_federal_surtax_if_non_resident", Decimal)
"""Federal surtax for a non-resident or deemed resident, Form T691 Part 3 line 4 "If not, and you
are a non-resident or deemed resident, enter the amount from line 2.": line 2 when you are a
non-resident or deemed resident, and 0 otherwise. The form prints no floor, so line 2 may be
negative."""

AMT_FEDERAL_SURTAX = CATALOG.declare("amt_federal_surtax", Decimal)
"""Federal surtax, Form T691 Part 3 line 4 "If you have an amount on line 3, enter that amount. If
not, and you are a non-resident or deemed resident, enter the amount from line 2. Otherwise, enter
"0".": line 3 when it has an amount, else the surtax for a non-resident or deemed resident, in the
form's order."""

AMT_FEDERAL_TAX_WITH_SURTAX_AND_RECAPTURE = CATALOG.declare(
    "amt_federal_tax_with_surtax_and_recapture", Decimal
)
"""Federal tax with the surtax and the recapture, Form T691 Part 3 line 6 "Add lines 1, 4, and 5.":
line 1 (the basic federal tax of Part 2 line 7), line 4 (the federal surtax) and line 5 "Recapture
of investment tax credit (from line 3 of Part C of Form T2038(IND))", in line order. The form prints
no floor, so the sum may be negative."""

AMT_FOREIGN_AND_LOGGING_CREDITS_TOTAL = CATALOG.declare(
    "amt_foreign_and_logging_credits_total", Decimal, non_negative=True
)
"""Foreign and logging tax credits, Form T691 Part 3 line 9 "Line 7 plus line 8": line 7 "Federal
foreign tax credit from Form T2209" and line 8 "Federal logging tax credit", in line order."""

AMT_FEDERAL_TAX_PAYABLE = CATALOG.declare("amt_federal_tax_payable", Decimal, non_negative=True)
"""Federal tax payable, Form T691 Part 3 line 10 "Line 6 minus line 9 (if negative, enter "0")"
"Federal tax payable": line 6 less line 9, not below zero."""

AMT_INVESTMENT_TAX_CREDIT_CLAIM = CATALOG.declare(
    "amt_investment_tax_credit_claim", Decimal, non_negative=True
)
"""Investment tax credit claimed, Form T691 Part 3 line 12 "Investment tax credit amount up to, but
not more than the amount I of Form T2038(IND)": the amount the filer claims, an election, entered as
the form takes it; it may not be more than amount I."""

AMT_INVESTMENT_TAX_CREDIT = CATALOG.declare("amt_investment_tax_credit", Decimal, non_negative=True)
"""Investment tax credit amount, Form T691 Part 3 line 12 "Investment tax credit amount up to, but
not more than the amount I of Form T2038(IND)": the claim, which may not be more than amount I; a
claim above it is refused, not capped."""

AMT_REGULAR_TAX_CREDITS_TOTAL = CATALOG.declare(
    "amt_regular_tax_credits_total", Decimal, non_negative=True
)
"""Regular tax credits, Form T691 Part 3 line 14 "Add lines 11 to 13.": line 11 "Federal political
contribution tax credit from line 41000 of your return", line 12 the investment tax credit and line
13 "Labour-sponsored funds tax credit from line 41400 of your return", in line order."""

AMT_REGULAR_NET_FEDERAL_TAX_PAYABLE = CATALOG.declare(
    "amt_regular_net_federal_tax_payable", Decimal, non_negative=True
)
"""Regular net federal tax payable, Form T691 Part 3 line 15 "Line 10 minus line 14 (if negative,
enter "0")" "Regular net federal tax payable": line 10 less line 14, not below zero."""

AMT_FOREIGN_BUSINESS_INCOME = CATALOG.declare("amt_foreign_business_income", Decimal)
"""Foreign business income, Form T691 Part 4 line 1 "(i) Foreign business income (total business
income earned in the foreign country, minus allowable expenses and deductions for the foreign
income)": a caller's figure, which is net of expenses and so may be a loss, left signed."""

AMT_FOREIGN_NON_BUSINESS_INCOME = CATALOG.declare(
    "amt_foreign_non_business_income", Decimal, non_negative=True
)
"""Foreign non-business income, Form T691 Part 4 line 2 "Foreign non-business income (on which
non-business income tax was paid to a foreign country (12))": the total of the net foreign
non-business income of the foreign tax countries, "Net foreign non-business income (2) 43300" of
each country's Form T2209 line 2."""

AMT_FOREIGN_CAPITAL_GAINS_NON_TAXABLE_CLAIM = CATALOG.declare(
    "amt_foreign_capital_gains_non_taxable_claim", Decimal, non_negative=True
)
"""Non-taxable part of foreign capital gains claimed, Form T691 Part 4 line 3 "Non-taxable part of
foreign capital gains included in adjusted taxable income (cannot be more than line 23 of Part 1)"
"67940": the amount the filer claims, an input, which may not be more than line 23 of Part 1."""

AMT_FOREIGN_CAPITAL_GAINS_NON_TAXABLE = CATALOG.declare(
    "amt_foreign_capital_gains_non_taxable", Decimal, non_negative=True
)
"""Non-taxable part of foreign capital gains, Form T691 Part 4 line 3 "Non-taxable part of foreign
capital gains included in adjusted taxable income (cannot be more than line 23 of Part 1)" "67940":
the claim, which may not be more than the capital gains added of Part 1 line 23 not below zero, a
claim above it is refused, not capped."""

AMT_TOTAL_FOREIGN_INCOME = CATALOG.declare("amt_total_foreign_income", Decimal, non_negative=True)
"""Total foreign income, Form T691 Part 4 line 4 "Total foreign income: add lines 1 to 3 (if
negative, enter "0")": lines 1, 2 and 3 added, not below zero."""

AMT_FOREIGN_INCOME_LIMIT = CATALOG.declare("amt_foreign_income_limit", Decimal, non_negative=True)
"""Foreign income limit for special foreign tax credit, Form T691 Part 4 line 6 "Foreign income
limit for special foreign tax credit: line 4 multiplied by the percentage on line 5 (if negative,
enter "0")" and "Applicable rate" "× 20.5%" on line 5: line 4 times the rate of Part 1 line 96,
rounded once to the cent. Line 4 is never negative, so the floor cannot apply."""

AMT_FOREIGN_NON_BUSINESS_TAX_PAID_BEFORE_EXCESS = CATALOG.declare(
    "amt_foreign_non_business_tax_paid_before_excess", Decimal, non_negative=True
)
"""Total before the deductible part, Form T691 Part 4 line 7 "(ii) Total non-business income tax
paid to a foreign country (12)": the total of "Non-business income tax paid to a foreign country
(1) 43100" of each country's Form T2209 line 1, before the tax on income from property over 15% of
it, deducted on line 23200, is taken off (note (12))."""

AMT_FOREIGN_NON_BUSINESS_TAX_PAID = CATALOG.declare(
    "amt_foreign_non_business_tax_paid", Decimal, non_negative=True
)
"""Non-business income tax paid to a foreign country, Form T691 Part 4 line 7 "(ii) Total
non-business income tax paid to a foreign country (12)": the total of the non-business income tax
paid of the foreign tax countries, "Non-business income tax paid to a foreign country (1) 43100" of
each country's Form T2209 line 1, less the tax on income from property over 15% of it (note (12):
the part deductible under subsection 20(11) is not counted)."""

AMT_FOREIGN_NON_BUSINESS_TAX_TWO_THIRDS = CATALOG.declare(
    "amt_foreign_non_business_tax_two_thirds", Decimal, non_negative=True
)
"""Non-business income tax paid times 66.6666%, Form T691 Part 4 line 7 "× 66.6666%": the tax paid
of line 7 times the percentage of its dataset, rounded once to the cent."""

AMT_FOREIGN_BUSINESS_TAX_PAID = CATALOG.declare(
    "amt_foreign_business_tax_paid", Decimal, non_negative=True
)
"""Business income tax paid to a foreign country, Form T691 Part 4 line 8 "Total business income
tax paid to a foreign country (13)": the total of the business income tax paid for the year of the
foreign tax countries, "Business income tax paid to a foreign country (5) for the year" of each
country's Form T2209 line 4, its first part; the unused credits of that line are not part of it."""

AMT_FOREIGN_TAXES_PAID = CATALOG.declare("amt_foreign_taxes_paid", Decimal, non_negative=True)
"""Foreign taxes paid for special foreign tax credit, Form T691 Part 4 line 9 "Foreign taxes paid
for special foreign tax credit: line 7 plus line 8 (if negative, enter "0")": lines 7 and 8 added,
not below zero."""

AMT_FOREIGN_TAX_CREDIT_LESSER = CATALOG.declare(
    "amt_foreign_tax_credit_lesser", Decimal, non_negative=True
)
"""Lesser of the foreign income limit and the foreign taxes paid, Form T691 Part 4 line 10 "Enter
whichever is less: amount from line 6 or line 9.": the lesser of lines 6 and 9."""

AMT_SPECIAL_FOREIGN_TAX_CREDIT = CATALOG.declare(
    "amt_special_foreign_tax_credit", Decimal, non_negative=True
)
"""Special foreign tax credit, Form T691 Part 4 line 11 "Enter whichever is more: amount from line 7
of Part 3 or line 10." "Special foreign tax credit": the greater of the federal foreign tax credit
of Part 3 line 7 (Form T2209) and line 10."""

AMT_NET_MINIMUM_TAX_PAYABLE = CATALOG.declare(
    "amt_net_minimum_tax_payable", Decimal, non_negative=True
)
"""Net minimum tax payable, Form T691 Part 5 line 3 "Line 1 minus line 2 (if negative, enter "0")"
"Net minimum tax payable": line 1 less line 2, not below zero."""

AMT_REGULAR_NET_TAX_LESS_SURTAX = CATALOG.declare(
    "amt_regular_net_tax_less_surtax", Decimal, non_negative=True
)
"""Regular net tax less the surtax, Form T691 Part 5 line 6 "Line 4 minus line 5 (if negative, enter
"0")": line 4, the regular net federal tax payable of Part 3 line 15, less line 5, the federal
surtax of Part 3 line 4, which may be negative and is then added back; not below zero."""

AMT_MINIMUM_TAX_AFTER_REGULAR_TAX = CATALOG.declare(
    "amt_minimum_tax_after_regular_tax", Decimal, non_negative=True
)
"""Minimum tax after the regular tax, Form T691 Part 5 line 7 "Line 3 minus line 6 (if negative,
enter "0")": line 3 less line 6, not below zero."""

AMT_INVESTMENT_TAX_CREDIT_LESS_PART_D = CATALOG.declare(
    "amt_investment_tax_credit_less_part_d", Decimal, non_negative=True
)
"""Investment tax credit less amount 15 of Part D, Form T691 Part 5 line 10 "Line 8 minus line 9 (if
negative, enter "0")": line 8, the investment tax credit of Part 3 line 12, less line 9, not below
zero."""

AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE = CATALOG.declare(
    "amt_alternative_minimum_tax_payable", Decimal, non_negative=True
)
"""Alternative minimum tax payable, Form T691 Part 5 line 11 "Line 7 minus line 10 (if negative,
enter "0")": line 7 less line 10, not below zero; a positive amount means Parts 6 and 7 apply."""

AMT_PART_5_LINE_11_IS_POSITIVE = CATALOG.declare(
    "amt_part_5_line_11_is_positive", int, non_negative=True
)
"""Line 11 is positive, Form T691 Part 5 line 11 "If line 11 is positive, complete parts 6 and 7.":
1 when line 11 (`amt_alternative_minimum_tax_payable`) is more than 0, and 0 otherwise, the count of
the condition."""

AMT_BASIC_FEDERAL_TAX_LESS_SPLIT_INCOME_TAX = CATALOG.declare(
    "amt_basic_federal_tax_less_split_income_tax", Decimal, non_negative=True
)
"""Basic federal tax less the split income tax, Form T691 Part 6 line 3 "Line 1 minus line 2 (if
negative, enter "0")": line 1, the basic federal tax of Part 2 line 7, less line 2, the amount from
line 22 of Form T1206, Tax on Split Income, not below zero."""

AMT_GREATER_OF_BASIC_TAX_AND_MINIMUM_AMOUNT = CATALOG.declare(
    "amt_greater_of_basic_tax_and_minimum_amount", Decimal, non_negative=True
)
"""Greater of the basic tax and the minimum amount, Form T691 Part 6 line 5 "Enter whichever is
more: amount from line 3 or line 4.": the greater of line 3 and line 4, the minimum amount from
line 103 of Part 1."""

AMT_FEDERAL_TAX_UNDER_MINIMUM_TAX = CATALOG.declare("amt_federal_tax_under_minimum_tax", Decimal)
"""Federal tax under the minimum tax, Form T691 Part 6 line 7 "Line 5 plus line 6 (14)": line 5 and
line 6, the amount from line 22 of Form T1206, in line order. The form prints no floor, so the sum
may be negative."""

AMT_PART_6_SURTAX_AT_48_PERCENT = CATALOG.declare("amt_part_6_surtax_at_48_percent", Decimal)
"""Federal surtax at 48 percent, Form T691 Part 6 line 9 "Federal surtax on business income earned
outside Canada" "Multiply the amount from line 7 by 48%.": line 7 times the 48% of its dataset,
rounded to the cent. The form prints no floor, so a negative line 7 gives a negative surtax."""

AMT_PART_6_SURTAX_MULTIPLE_JURISDICTIONS = CATALOG.declare(
    "amt_part_6_surtax_multiple_jurisdictions", Decimal
)
"""Federal surtax for multiple jurisdictions, Form T691 Part 6 line 10 "If you have to pay tax to
multiple jurisdictions, multiply the amount from line 9 by the percentage in Column 5 of line 52220
on Form T2203.": line 9 times the percentage of Form T2203, the caller's figure as the form prints
it (50 for 50%), rounded once to the cent. The form prints no floor, so the product may be
negative."""

AMT_PART_6_HAS_AMOUNT_ON_LINE_10 = CATALOG.declare(
    "amt_part_6_has_amount_on_line_10", int, non_negative=True
)
"""You have an amount on line 10, Form T691 Part 6 line 11 "If you have an amount on line 10, enter
that amount.": 1 when line 10 is not 0, and 0 otherwise, the count of the condition."""

AMT_PART_6_SURTAX_IF_NON_RESIDENT = CATALOG.declare("amt_part_6_surtax_if_non_resident", Decimal)
"""Federal surtax for a non-resident or deemed resident, Form T691 Part 6 line 11 "If not, and you
are a non-resident or deemed resident, enter the amount from line 9.": line 9 when you are a
non-resident or deemed resident, and 0 otherwise. The form prints no floor, so line 9 may be
negative."""

AMT_PART_6_FEDERAL_SURTAX = CATALOG.declare("amt_part_6_federal_surtax", Decimal)
"""Federal surtax, Form T691 Part 6 line 11 "If you have an amount on line 10, enter that amount. If
not, and you are a non-resident or deemed resident, enter the amount from line 9. Otherwise, enter
"0".": line 10 when it has an amount, else the surtax for a non-resident or deemed resident, in the
form's order."""

AMT_PART_6_TAX_WITH_SURTAX = CATALOG.declare("amt_part_6_tax_with_surtax", Decimal)
"""Federal tax with the surtax, Form T691 Part 6 line 12 "Line 8 plus line 11": line 8, the net
minimum tax payable of Part 5 line 3, and line 11, in line order. The form prints no floor, so the
sum may be negative."""

AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX = CATALOG.declare(
    "amt_federal_tax_payable_under_minimum_tax", Decimal, non_negative=True
)
"""Federal tax payable (under alternative minimum tax), Form T691 Part 6 line 14 "Enter whichever is
more: amount from line 12 or line 13. Enter this amount on line 41700 of your return." "Federal tax
payable (under alternative minimum tax)": the greater of line 12 and line 13, "Amount from line 24
of Form T1206", which is not below zero. The entry on line 41700 of the return is made by the choice
of the line 41700 entry, which takes this amount only when Part 5 line 11 is positive."""

AMT_UNAPPLIED_2018_CARRYOVER = CATALOG.declare(
    "amt_unapplied_2018_carryover", Decimal, non_negative=True
)
"""Unapplied 2018 minimum tax carryover, Form T691 Part 8 line 16 "Unapplied 2018 minimum tax
carryover": a starting amount, the caller's figure, not below zero."""

AMT_UNAPPLIED_2018_CARRYOVER_CHECKED = CATALOG.declare(
    "amt_unapplied_2018_carryover_checked", Decimal, non_negative=True
)
"""Unapplied 2018 minimum tax carryover after the check, Form T691 Part 8 line 16 "Unapplied 2018
minimum tax carryover": the amount of `ca/amt_unapplied_2018_carryover` after the check that it is
not more than line 13, `ca/amt_carryover_balance` (`core/at_most`). Line 17 subtracts line 16 from
line 15, which is line 13 plus line 14, so the expiring 2018 amount is part of line 13 and an amount
above it is an input error, not capped. Line 17 reads this amount."""

AMT_PART_7_BASIC_TAX_WITH_RECAPTURE = CATALOG.declare(
    "amt_part_7_basic_tax_with_recapture", Decimal
)
"""Basic federal tax with the recapture, Form T691 Part 7 line 4 "Line 2 plus line 3": line 2, the
basic federal tax of Part 2 line 7, and line 3, the recapture of investment tax credit, in line
order. The form prints no floor, so the sum may be negative."""

AMT_PART_7_CREDITS_TOTAL = CATALOG.declare("amt_part_7_credits_total", Decimal, non_negative=True)
"""Credits, Form T691 Part 7 line 7 "Line 5 plus line 6": line 5, the federal logging tax credit,
and line 6, "Amount from line 41600 of your return", in line order."""

AMT_PART_7_TAX_LESS_CREDITS = CATALOG.declare("amt_part_7_tax_less_credits", Decimal)
"""Tax less the credits, Form T691 Part 7 line 8 "Line 4 minus line 7": line 4 less line 7. The form
prints no floor, so the difference may be negative."""

AMT_PART_7_FOREIGN_CREDIT_DIFFERENCE = CATALOG.declare(
    "amt_part_7_foreign_credit_difference", Decimal, non_negative=True
)
"""Foreign credit difference, Form T691 Part 7 line 11 "Line 9 minus line 10 (if negative, enter
"0")": the special foreign tax credit of Part 4 line 11 less the federal foreign tax credit of Part
3 line 7, not below zero."""

AMT_PART_7_FOREIGN_TAXES_PAID = CATALOG.declare(
    "amt_part_7_foreign_taxes_paid", Decimal, non_negative=True
)
"""Foreign taxes paid, the denominator of Form T691 Part 7 line 12 "Foreign taxes* paid
(non-business income tax paid to a foreign country (15) plus business income tax paid to a foreign
country (16))": the non-business income tax paid to a foreign country and the business income tax
paid to a foreign country, added. It is the fraction's denominator, not a numbered line."""

AMT_PART_7_FOREIGN_CREDIT_SHARE = CATALOG.declare(
    "amt_part_7_foreign_credit_share", Decimal, non_negative=True
)
"""Foreign credit share, Form T691 Part 7 line 12 "Line 11 × [Foreign taxes paid for special foreign
tax credit (line 9 of Part 4)] / [Foreign taxes paid ...]" "= +": line 11 times the foreign taxes
paid for the special foreign tax credit, over the foreign taxes paid, rounded once to the cent; 0
when there are no foreign taxes paid."""

AMT_PART_7_TAX_LESS_CREDITS_PLUS_SHARE = CATALOG.declare(
    "amt_part_7_tax_less_credits_plus_share", Decimal
)
"""Tax less the credits plus the foreign credit share, Form T691 Part 7 line 13 "Line 8 plus line
12": line 8 and line 12, in line order. The form prints no floor, so the sum may be negative."""

AMT_ADDITIONAL_TAXES_FOR_CARRYOVER = CATALOG.declare(
    "amt_additional_taxes_for_carryover", Decimal, non_negative=True
)
"""Additional taxes paid for minimum tax carryover, Form T691 Part 7 line 14 "Line 1 minus line 13
(if negative, enter "0")" "Additional taxes paid for minimum tax carryover": the minimum amount of
line 1 less line 13, not below zero. Part 8 line 14 reads it."""

AMT_PART_8_ADDITIONAL_TAXES = CATALOG.declare(
    "amt_part_8_additional_taxes", Decimal, non_negative=True
)
"""Additional 2025 taxes, Form T691 Part 8 line 14 "Additional 2025 taxes for carryover
to later years from line 14 of Part 7": line 14 of Part 7 (`amt_additional_taxes_for_carryover`)
when Part 5 line 11 is positive, and 0 otherwise, since Part 7 is completed only then."""

AMT_CARRYOVER_BALANCE = CATALOG.declare("amt_carryover_balance", Decimal, non_negative=True)
"""Balance of minimum tax carryover available for later years, Form T691 Part 8 line 13 "Balance of
minimum tax carryover available for later years, if any: line 1 minus line 12": line 1 less line 12.
Line 12 is at most line 1, so the balance is not below zero."""

AMT_CARRYOVER_BALANCE_WITH_ADDITIONAL_TAXES = CATALOG.declare(
    "amt_carryover_balance_with_additional_taxes", Decimal, non_negative=True
)
"""Carryover balance with the additional taxes, Form T691 Part 8 line 15 "Line 13 plus line 14":
line 13 and line 14, the additional 2025 taxes of Part 7 line 14, in line order."""

AMT_CARRYOVER_AVAILABLE_FOR_2026 = CATALOG.declare("amt_carryover_available_for_2026", Decimal)
"""Total minimum tax carryover available for 2026, Form T691 Part 8 line 17 "Total minimum tax
carryover available for 2026: line 15 minus line 16": line 15 less line 16, the unapplied 2018
carryover. The form prints no floor, so the difference may be negative."""

AMT_LINES_39_AND_40_BOTH = CATALOG.declare("amt_lines_39_and_40_both", int, non_negative=True)
"""Form T691 Part 1 lines 39 and 40 "complete line 39 or 40 depending on your situation": 1 when
line 39 (the difference with no election) and line 40 (the difference with an election) are both
more than 0, else 0, a starting count. The form says to complete one of the two, so this count of
1 is refused (see `amt_lines_39_and_40_both_checked`)."""

AMT_LINES_39_AND_40_BOTH_CHECKED = CATALOG.declare(
    "amt_lines_39_and_40_both_checked", int, non_negative=True
)
"""Form T691 Part 1 lines 39 and 40 both filled in, checked: the count of `amt_lines_39_and_40_both`
when it is 0, the only value produced. A count of 1 is an input error, not capped, so lines 43 and
46 never add a line 40 on top of a line 39."""

AMT_PPIP_PREMIUMS_IN_ONTARIO = CATALOG.declare(
    "amt_ppip_premiums_in_ontario", int, non_negative=True
)
"""Form T691 Part 1 line 59 "Deduction for PPIP premiums on self-employment income from line 22300
of your return (Quebec only)": 1 when line 59 is more than 0 and the filer was a resident of Ontario
on December 31, 2025 (`ca-on/not_resident_of_ontario_at_year_end_checked` is 0), else 0, a starting
count. An Ontario resident has no Quebec line 22300 to deduct, so this count of 1 is refused (see
`amt_ppip_premiums_in_ontario_checked`)."""

AMT_PPIP_PREMIUMS_IN_ONTARIO_CHECKED = CATALOG.declare(
    "amt_ppip_premiums_in_ontario_checked", int, non_negative=True
)
"""Form T691 Part 1 line 59 for an Ontario resident, checked: the count of
`amt_ppip_premiums_in_ontario` when it is 0, the only value produced. A count of 1 is an input
error, not capped, so line 63 never adds a Quebec-only deduction for an Ontario resident."""

AMT_EXPENSES_INCLUDED_ON_LINE_22100 = CATALOG.declare(
    "amt_expenses_included_on_line_22100", Decimal, non_negative=True
)
"""Expenses included on line 22100 of the return, not a form line: Form T691 Part 1 line 10
"Carrying charges (2) for acquiring an interest in a partnership of which you are a limited or
non-active partner, or which owns a rental or leasing property or a film property (included on line
22100 of your return) (6)" and lines 64 to 67, each "(included on line 22100 of your return)": line
10 and the four amounts of lines 64 to 67 added, which is line 68. Refused above line 22100 of the
return (see `amt_expenses_included_on_line_22100_checked`)."""

AMT_EXPENSES_INCLUDED_ON_LINE_22100_CHECKED = CATALOG.declare(
    "amt_expenses_included_on_line_22100_checked", Decimal, non_negative=True
)
"""Form T691 Part 1 lines 10 and 64 to 67 "(included on line 22100 of your return)", checked: the
amount of `amt_expenses_included_on_line_22100` after the check that it is not more than line 22100
of the return, `ca/carrying_charges_interest_expenses_and_other_expenses` (`core/at_most`). An
amount above line 22100 is an input error, not capped. A guard of this check, which nothing on the
return reads."""

AMT_LINES_22100_22400_AND_23200 = CATALOG.declare(
    "amt_lines_22100_22400_and_23200", Decimal, non_negative=True
)
"""Lines 22100, 22400 and 23200 of the return added, not a form line: line 22100 (carrying
charges, interest and other expenses), line 22400 (exploration and development expenses) and line
23200 (other deductions and total split income). The bound of Form T691 Part 9 line 1 "Total of all
resource expenditures, depletion allowances and carrying charges for resource property and
flow-through shares (included on lines 22100, 22400, and 23200 of your return)"."""

AMT_RESOURCE_EXPENDITURES_CHECKED = CATALOG.declare(
    "amt_resource_expenditures_checked", Decimal, non_negative=True
)
"""Form T691 Part 9 line 1 "Total of all resource expenditures, depletion allowances and carrying
charges for resource property and flow-through shares (included on lines 22100, 22400, and 23200
of your return)", checked: the amount of `amt_resource_expenditures` after the check that it is not
more than `amt_lines_22100_22400_and_23200` (`core/at_most`). An amount above those lines is an
input error, not capped. Part 9 line 6 reads it."""
