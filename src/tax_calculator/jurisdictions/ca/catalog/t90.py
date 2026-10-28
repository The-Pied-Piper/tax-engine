"""The federal catalog: Form T90, "Income Exempt from Tax under the Indian Act", the form `ca/t90`.

The form runs once (it has no instances). Its sixteen starting amounts are the printed lines 1 to
19, with line 10019 the unnumbered line "EI maternity and parental benefits and PPIP benefits
included on line 9"; the steps compute lines 4, 14, 16, 18 and 20 and check line 10019 against
line 9. The exports are line 4, the checked line 10019 and line 20, which Schedule 6 reads through
`ca/t90.<name>`. Lines 14, 16 and 18 are the intermediate kinds between the inputs and line 20."""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.jurisdictions.ca.catalog.base import CATALOG

T90_T4_BOX_71_EMPLOYMENT_INCOME = CATALOG.declare(
    "t90_t4_box_71_employment_income", Decimal, non_negative=True
)
"""Employment income, T90 line 1 "Employment income (box 71 of your T4 slip(s))": the amount the
filer enters, one total for all the T4 slips, a starting amount."""

T90_OTHER_EMPLOYMENT_INCOME = CATALOG.declare(
    "t90_other_employment_income", Decimal, non_negative=True
)
"""Other employment income, T90 line 2 "Other employment income such as tips, net research grants,
and income maintenance insurance plans": the amount the filer enters, a starting amount."""

T90_NET_SELF_EMPLOYMENT_INCOME = CATALOG.declare(
    "t90_net_self_employment_income", Decimal, non_negative=True
)
"""Net self-employment income, T90 line 3 "Net self-employment income (excluding losses)": the
amount the filer enters, a starting amount."""

T90_EXEMPT_WORKING_INCOME = CATALOG.declare("t90_exempt_working_income", Decimal, non_negative=True)
"""Total exempt working income, T90 line 4 "Add lines 1 to 3." "Total exempt working income 10000":
the sum of lines 1, 2 and 3, the export Schedule 6 line 4 reads."""

T90_CPP_QPP_BENEFITS = CATALOG.declare("t90_cpp_qpp_benefits", Decimal, non_negative=True)
"""Canada pension plan or Quebec pension plan benefits, T90 line 5 "Canada pension plan (CPP) or
Quebec pension plan (QPP) benefits": the amount the filer enters, a starting amount."""

T90_RRSP_RRIF_PENSION_TRANSFER_INCOME = CATALOG.declare(
    "t90_rrsp_rrif_pension_transfer_income", Decimal, non_negative=True
)
"""RRSP or RRIF income relating to exempt pension transfers, T90 line 6 "Registered retirement
savings plan (RRSP) or Registered retirement income fund (RRIF) income relating to exempt pension
transfers from a registered pension plan": the amount the filer enters, a starting amount."""

T90_COVID_19_PAYMENTS = CATALOG.declare("t90_covid_19_payments", Decimal, non_negative=True)
"""COVID-19 payments, T90 line 7 "Federal, provincial, or territorial government COVID-19 payments
received in the year (from your T4A or T4E slip) (1)": the amount the filer enters, a starting
amount."""

T90_OTHER_PENSIONS_AND_SUPERANNUATION = CATALOG.declare(
    "t90_other_pensions_and_superannuation", Decimal, non_negative=True
)
"""Other pensions and superannuation, T90 line 8 "Other pensions and superannuation": the amount
the filer enters, a starting amount."""

T90_EI_PPIP_AND_OTHER_BENEFITS = CATALOG.declare(
    "t90_ei_ppip_and_other_benefits", Decimal, non_negative=True
)
"""Employment Insurance, PPIP and other benefits, T90 line 9 "Employment Insurance (EI), Provincial
parental insurance plan (PPIP), and other benefits (box 18 of your T4E slip)": the amount the filer
enters, a starting amount, which line 10019 is part of."""

T90_EI_MATERNITY_PARENTAL_PPIP_BENEFITS = CATALOG.declare(
    "t90_ei_maternity_parental_ppip_benefits", Decimal, non_negative=True
)
"""EI maternity and parental benefits and PPIP benefits, T90 line 10019 "EI maternity and parental
benefits and PPIP benefits included on line 9": the amount the filer enters, a starting amount,
checked against line 9 by `ca/t90_ei_maternity_parental_ppip_benefits_checked`."""

T90_INTEREST_DIVIDENDS_INVESTMENT_INCOME = CATALOG.declare(
    "t90_interest_dividends_investment_income", Decimal, non_negative=True
)
"""Interest, dividends and other investment income, T90 line 10 "Interest, dividends, and other
investment income": the amount the filer enters, a starting amount."""

T90_NET_RENTAL_INCOME = CATALOG.declare("t90_net_rental_income", Decimal, non_negative=True)
"""Net rental income, T90 line 11 "Net rental income (excluding losses)": the amount the filer
enters, a starting amount."""

T90_SOCIAL_ASSISTANCE_PAYMENTS = CATALOG.declare(
    "t90_social_assistance_payments", Decimal, non_negative=True
)
"""Social assistance payments, T90 line 12 "Social assistance payments received from a First Nation
or band council": the amount the filer enters, a starting amount."""

T90_OTHER_EXEMPT_INCOME = CATALOG.declare("t90_other_exempt_income", Decimal, non_negative=True)
"""Other sources of exempt income, T90 line 13 "Other sources of exempt income": the amount the
filer enters, a starting amount."""

T90_LINE_14 = CATALOG.declare("t90_line_14", Decimal, non_negative=True)
"""Line 14 of Form T90, "Add lines 4 to 13.": line 4 and lines 5 to 13 except line 10019, which
line 9 already holds."""

T90_NET_RENTAL_LOSSES = CATALOG.declare("t90_net_rental_losses", Decimal, non_negative=True)
"""Net rental losses, T90 line 15 "Net rental losses": the amount the filer enters, a starting
amount, subtracted at line 16."""

T90_LINE_16 = CATALOG.declare("t90_line_16", Decimal)
"""Line 16 of Form T90, "Line 14 minus line 15": the amount of line 14 less the net rental losses,
which may be negative as the form prints no floor."""

T90_NET_SELF_EMPLOYMENT_LOSSES = CATALOG.declare(
    "t90_net_self_employment_losses", Decimal, non_negative=True
)
"""Net self-employment losses, T90 line 17 "Net self-employment losses": the amount the filer
enters, a starting amount, subtracted at line 18."""

T90_TOTAL_EXEMPT_INCOME = CATALOG.declare("t90_total_exempt_income", Decimal)
"""Total exempt income, T90 line 18 "Line 16 minus line 17" "Total exempt income": the amount of
line 16 less the net self-employment losses, which may be negative as the form prints no floor."""

T90_DEDUCTIONS_RELATING_TO_EXEMPT_INCOME = CATALOG.declare(
    "t90_deductions_relating_to_exempt_income", Decimal, non_negative=True
)
"""Deductions relating to exempt income, T90 line 19 "Deductions relating to exempt income above
(2)": the amount the filer enters, a starting amount, subtracted at line 20."""

T90_EI_MATERNITY_PARENTAL_PPIP_BENEFITS_CHECKED = CATALOG.declare(
    "t90_ei_maternity_parental_ppip_benefits_checked", Decimal, non_negative=True
)
"""EI maternity and parental benefits and PPIP benefits included on line 9, checked, T90 line 10019
"EI maternity and parental benefits and PPIP benefits included on line 9": the line 10019 amount,
refused above line 9 (the form prints no cap, and the amount is part of line 9), which the form
exports and line 14 does not add."""

T90_NET_EXEMPT_INCOME = CATALOG.declare("t90_net_exempt_income", Decimal)
"""Net exempt income, T90 line 20 "Line 18 minus line 19 (if negative, show in brackets)" "Net
exempt income 10026": line 18 less line 19, which may be negative, shown in brackets on the form.
The export Schedule 6 line 8 reads."""
