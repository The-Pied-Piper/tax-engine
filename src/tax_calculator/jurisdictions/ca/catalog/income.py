"""The federal catalog: income.

The T1 income lines, total income, the dividend and investment income lines that feed them, and
the short-term rental rows of Form T776 Chart A and the business statement of Form T2125.
"""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.jurisdictions.ca.catalog.base import CATALOG
from tax_calculator.jurisdictions.ca.catalog.personal_amounts import (
    CCA_ADDITIONS,
    CCA_AIIP_ADDITIONS,
    CCA_CLAIMED,
    CCA_CLASS_NUMBER,
    CCA_DIEP_ADDITIONS,
    CCA_DIEP_PROCEEDS,
    CCA_HALF_YEAR_RULE_DIFFERS,
    CCA_IMMEDIATE_EXPENSING,
    CCA_NO_PROPERTY_LEFT,
    CCA_PERSONAL_PART_REMAINING,
    CCA_PROCEEDS,
    CCA_RATE_ELECTION,
    CCA_RIIP_ADDITIONS,
    CCA_UCC_AT_END,
    CCA_UCC_AT_START,
    CCA_VEHICLE_ACQUIRED_YEAR,
    CCA_VEHICLE_COST,
    CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
    CCA_ZEPV_DIEP_PROCEEDS,
    CCA_ZEPV_PROCEEDS,
)

EMPLOYMENT_INCOME = CATALOG.declare("employment_income", Decimal, non_negative=True)
"""Employment income, T1 line 10100: a starting amount that total income sums directly."""

EMERGENCY_SERVICES_VOLUNTEER_EXEMPT_INCOME = CATALOG.declare(
    "emergency_services_volunteer_exempt_income", Decimal, non_negative=True
)
"""Emergency services volunteer exempt income, T1 line 10105 "Tax-exempt income for emergency
services volunteers": carried as entered and read by the Schedule 6 election (lines 4 and 8) and
the conflict check. The exempt amount is not added to total income."""

EMERGENCY_SERVICES_VOLUNTEER_CONFLICT = CATALOG.declare(
    "emergency_services_volunteer_conflict", int, non_negative=True
)
"""Emergency services volunteers, Form 5000-G "Emergency services volunteers": "If you are eligible
for the $1,000 exemption on line 10100 of your return and the VFA or SRVA (lines 31220 and 31240 of
your return), you must choose which one you want to claim." The exemption (line 10105, "Tax-exempt
income for emergency services volunteers") with either the volunteer firefighters' amount (line
31220) or the search and rescue volunteers' amount (line 31240): 1 when the exemption is above 0 and
either flag is above 0, else 0, a starting count. A conflict is an input error (see
`ca/emergency_services_volunteer_conflict_checked`), so the return never claims both."""

EMERGENCY_SERVICES_VOLUNTEER_CONFLICT_CHECKED = CATALOG.declare(
    "emergency_services_volunteer_conflict_checked", int, non_negative=True
)
"""Emergency services volunteers, checked, Form 5000-G "Emergency services volunteers": "you must
choose which one you want to claim.": the count of `ca/emergency_services_volunteer_conflict` when
it is 0, the only value produced. A count of 1 is an input error, not capped, so the return never
claims the $1,000 exemption with the VFA or SRVA."""

T4_COMMISSIONS = CATALOG.declare("t4_commissions", Decimal, non_negative=True)
"""Commissions on the T4 slips, T1 line 10120 "Commissions included on line 10100 (box 42 of all T4
slips)": a memo carried as entered, which no step reads. The amount is already included in line
10100 and must not be added again."""

WAGE_LOSS_REPLACEMENT_CONTRIBUTIONS = CATALOG.declare(
    "wage_loss_replacement_contributions", Decimal, non_negative=True
)
"""Wage-loss replacement contributions, T1 line 10130 "Wage-loss replacement contributions": a memo
carried as entered, which no step reads."""

CAPITAL_GAIN = CATALOG.declare("capital_gain", Decimal)
"""Total capital gains or losses, Schedule 3 line 21 and line 19700 "Line 19 plus line 20 Total
capital gains or losses =": line 19 plus the reserves of line 20, worked out from Part 3 and Part 4.
Signed, as the form reports "all negative amounts (losses) using brackets"; line 22 is the same
figure and the inclusion rate applies to it."""

DISPOSITION_PROCEEDS = CATALOG.declare("disposition_proceeds", Decimal, non_negative=True)
"""Proceeds of a disposition, Schedule 3 Part 3 "(Column 2): Proceeds of disposition": a field of
each record of the property lists, not an artifact of its own."""

DISPOSITION_ADJUSTED_COST_BASE = CATALOG.declare(
    "disposition_adjusted_cost_base", Decimal, non_negative=True
)
"""Adjusted cost base of a disposition, Schedule 3 Part 3 "(Column 3): Adjusted cost base": a field
of each record of the property lists, not an artifact of its own."""

DISPOSITION_OUTLAYS = CATALOG.declare("disposition_outlays", Decimal, non_negative=True)
"""Outlays and expenses of a disposition, Schedule 3 Part 3 "(Column 4): Outlays and expenses": a
field of each record of the property lists, not an artifact of its own."""

QSBCS_DISPOSITIONS = RecordListKind.declare(
    CATALOG,
    "qsbcs_dispositions",
    fields=(DISPOSITION_PROCEEDS, DISPOSITION_ADJUSTED_COST_BASE, DISPOSITION_OUTLAYS),
)
"""Qualified small business corporation shares (QSBCS) dispositions, Schedule 3 Part 3 "Qualified
small business corporation shares (QSBCS)" "For each Gain or loss enter as many lines as
necessary.": a starting list with one record for each disposition, holding "(Column 2): Proceeds of
disposition", "(Column 3): Adjusted cost base" and "(Column 4): Outlays and expenses" (column 1 and
the narrative columns feed no line)."""

QSBCS_GAIN_OR_LOSS = CATALOG.declare("qsbcs_gain_or_loss", Decimal)
"""Qualified small business corporation shares (QSBCS) gain or loss, Schedule 3 line 1 and line
10700 "Total gain or loss (add all the amounts under column 5)": the rows' column 5 "Gain or loss
(column 2 minus columns 3 and 4)" added, a loss in brackets."""

QSBCS_PROCEEDS = CATALOG.declare("qsbcs_proceeds", Decimal, non_negative=True)
"""Qualified small business corporation shares (QSBCS) total proceeds, Schedule 3 line 10699 "Total
proceeds of disposition (add all the amounts under column 2)": the rows' column 2 "Proceeds of
disposition" added."""

DISPOSITION_FARM_LOSS_TAXES_AND_INTEREST = CATALOG.declare(
    "disposition_farm_loss_taxes_and_interest", Decimal, non_negative=True
)
"""Property taxes and interest of the restricted farm loss, Guide T4037 p.34 "The amount of RFLs
that you can apply cannot be more than the property taxes and interest on money you borrowed to buy
the farmland that were included in the calculation of the RFLs for each year.": the part of the
filer's unapplied restricted farm loss that is property taxes and interest on the farmland, 0 when
the row is not farmland. A field of each record of the qualified farm or fishing property, other
foreclosures and real estate lists, not an artifact of its own."""

DISPOSITION_FARM_LOSS_PROPERTY_TAXES = CATALOG.declare(
    "disposition_farm_loss_property_taxes", Decimal, non_negative=True
)
"""Property taxes of the restricted farm loss added to a disposition's adjusted cost base, Guide
T4037 p.34 example "Plus: Property taxes + $ C": the amount of line C added to column 3, 0 when
none is applied. A field of each record of the qualified farm or fishing property and real estate
lists, not an artifact of its own."""

DISPOSITION_FARM_LOSS_INTEREST = CATALOG.declare(
    "disposition_farm_loss_interest", Decimal, non_negative=True
)
"""Interest of the restricted farm loss added to a disposition's adjusted cost base, Guide T4037
p.34 example "Interest + $ D": the amount of line D added to column 3, 0 when none is applied. A
field of each record of the qualified farm or fishing property and real estate lists, not an
artifact of its own."""

QFFP_DISPOSITIONS = RecordListKind.declare(
    CATALOG,
    "qffp_dispositions",
    fields=(
        DISPOSITION_PROCEEDS,
        DISPOSITION_ADJUSTED_COST_BASE,
        DISPOSITION_OUTLAYS,
        DISPOSITION_FARM_LOSS_TAXES_AND_INTEREST,
        DISPOSITION_FARM_LOSS_PROPERTY_TAXES,
        DISPOSITION_FARM_LOSS_INTEREST,
    ),
)
"""Qualified farm or fishing property (QFFP) dispositions, Schedule 3 Part 3 "Qualified farm or
fishing property (QFFP)" "For each Gain or loss enter as many lines as necessary.": a starting list
with one record for each disposition, holding "(Column 2): Proceeds of disposition", "(Column 3):
Adjusted cost base" and "(Column 4): Outlays and expenses" (column 1 and the narrative columns feed
no line), and the restricted farm loss (the property taxes and interest part, then the Guide's line
C property taxes and line D interest added to column 3) as a fourth, fifth and sixth."""

QFFP_GAIN_OR_LOSS = CATALOG.declare("qffp_gain_or_loss", Decimal)
"""Qualified farm or fishing property (QFFP) gain or loss, Schedule 3 line 2 and line 11000 "Total
gain or loss (add all the amounts under column 5)": the rows' column 5 "Gain or loss (column 2 minus
columns 3 and 4)" added, a loss in brackets."""

QFFP_PROCEEDS = CATALOG.declare("qffp_proceeds", Decimal, non_negative=True)
"""Qualified farm or fishing property (QFFP) total proceeds, Schedule 3 line 10999 "Total proceeds
of disposition (add all the amounts under column 2)": the rows' column 2 "Proceeds of disposition"
added."""

QFFP_RESTRICTED_FARM_LOSS_APPLIED = CATALOG.declare(
    "qffp_restricted_farm_loss_applied", Decimal, non_negative=True
)
"""Qualified farm or fishing property (QFFP) restricted farm loss applied, Guide T4037 p.34 "Plus:
Property taxes + $ C" and "Interest + $ D": the rows' property taxes and interest added to column 3,
the amount the filer has applied on this list."""

QFFP_FORECLOSURE_DISPOSITIONS = RecordListKind.declare(
    CATALOG,
    "qffp_foreclosure_dispositions",
    fields=(
        DISPOSITION_PROCEEDS,
        DISPOSITION_ADJUSTED_COST_BASE,
        DISPOSITION_OUTLAYS,
        DISPOSITION_FARM_LOSS_TAXES_AND_INTEREST,
        DISPOSITION_FARM_LOSS_PROPERTY_TAXES,
        DISPOSITION_FARM_LOSS_INTEREST,
    ),
)
"""QFFP: Mortgage foreclosures and conditional sales repossessions dispositions, Schedule 3 Part 3
"QFFP: Mortgage foreclosures and conditional sales repossessions" "For each Gain or loss enter as
many lines as necessary.": a starting list with one record for each disposition, holding "(Column
2): Proceeds of disposition", "(Column 3): Adjusted cost base" and "(Column 4): Outlays and
expenses" (column 1 and the narrative columns feed no line), and the restricted farm loss as on the
qualified farm or fishing property list (Guide T4037: a repossession is a sale of the property)."""

QFFP_FORECLOSURE_GAIN_OR_LOSS = CATALOG.declare("qffp_foreclosure_gain_or_loss", Decimal)
"""QFFP: Mortgage foreclosures and conditional sales repossessions gain or loss, Schedule 3 line 3
and line 12400 "Total gain or loss (add all the amounts under column 5)": the rows' column 5 "Gain
or loss (column 2 minus columns 3 and 4)" added, a loss in brackets."""

QFFP_FORECLOSURE_PROCEEDS = CATALOG.declare("qffp_foreclosure_proceeds", Decimal, non_negative=True)
"""QFFP: Mortgage foreclosures and conditional sales repossessions total proceeds, Schedule 3 line
12399 "Total proceeds of disposition (add all the amounts under column 2)": the rows' column 2
"Proceeds of disposition" added."""

QFFP_FORECLOSURE_RESTRICTED_FARM_LOSS_APPLIED = CATALOG.declare(
    "qffp_foreclosure_restricted_farm_loss_applied", Decimal, non_negative=True
)
"""QFFP: Mortgage foreclosures and conditional sales repossessions restricted farm loss applied,
Guide T4037 p.34 "Plus: Property taxes + $ C" and "Interest + $ D": the rows' property taxes and
interest added to column 3, the amount the filer has applied on this list."""

OTHER_FORECLOSURE_RESTRICTED_FARM_LOSS_APPLIED = CATALOG.declare(
    "other_foreclosure_restricted_farm_loss_applied", Decimal, non_negative=True
)
"""Other mortgage foreclosures and conditional sales repossessions restricted farm loss applied,
Guide T4037 p.34 "Plus: Property taxes + $ C" and "Interest + $ D": the rows' property taxes and
interest added to column 3, the amount the filer has applied on this list."""

SHARE_DISPOSITIONS = RecordListKind.declare(
    CATALOG,
    "share_dispositions",
    fields=(DISPOSITION_PROCEEDS, DISPOSITION_ADJUSTED_COST_BASE, DISPOSITION_OUTLAYS),
)
"""Publicly traded shares, mutual fund units, deferral of eligible small business corporation shares
and other shares dispositions, Schedule 3 Part 3 "Publicly traded shares, mutual fund units,
deferral of eligible small business corporation shares and other shares" "For each Gain or loss
enter as many lines as necessary.": a starting list with one record for each disposition, holding
"(Column 2): Proceeds of disposition", "(Column 3): Adjusted cost base" and "(Column 4): Outlays and
expenses" (column 1 and the narrative columns feed no line)."""

SHARE_GAIN_OR_LOSS = CATALOG.declare("share_gain_or_loss", Decimal)
"""Publicly traded shares, mutual fund units, deferral of eligible small business corporation shares
and other shares gain or loss, Schedule 3 line 4 and line 13200 "Total gain or loss (add all the
amounts under column 5)": the rows' column 5 "Gain or loss (column 2 minus columns 3 and 4)" added,
a loss in brackets."""

SHARE_GAIN_NOT_BELOW_ZERO = CATALOG.declare("share_gain_not_below_zero", Decimal, non_negative=True)
"""Publicly traded shares, mutual fund units, deferral of eligible small business corporation shares
and other shares gain, Schedule 3 line 4 and line 13200 "Total gain or loss (add all the amounts
under column 5)" with a loss counted as 0: `ca/share_gain_or_loss` floored at 0, the most the
deferral of line 13 may be (`core/at_most`), since a loss leaves no share gain to defer."""

SHARE_PROCEEDS = CATALOG.declare("share_proceeds", Decimal, non_negative=True)
"""Publicly traded shares, mutual fund units, deferral of eligible small business corporation shares
and other shares total proceeds, Schedule 3 line 13199 "Total proceeds of disposition (add all the
amounts under column 2)": the rows' column 2 "Proceeds of disposition" added."""

DISPOSITION_DEPRECIABLE_PROPERTY = CATALOG.declare(
    "disposition_depreciable_property", int, non_negative=True
)
"""Depreciable property, Schedule 3 Part 3 line 5 row, Guide T4037 p.19 "A loss from the sale of
depreciable property is not considered to be a capital loss.": 1 if the property sold is
depreciable property, else 0, a yes or no answer taken as a count like the forms' other yes or no
questions; a value above 1 is refused by `ca/depreciable_property_gains`. A field of each record of
the real estate list, not an artifact of its own."""

REAL_ESTATE_DISPOSITIONS = RecordListKind.declare(
    CATALOG,
    "real_estate_dispositions",
    fields=(
        DISPOSITION_PROCEEDS,
        DISPOSITION_ADJUSTED_COST_BASE,
        DISPOSITION_OUTLAYS,
        DISPOSITION_DEPRECIABLE_PROPERTY,
        DISPOSITION_FARM_LOSS_TAXES_AND_INTEREST,
        DISPOSITION_FARM_LOSS_PROPERTY_TAXES,
        DISPOSITION_FARM_LOSS_INTEREST,
    ),
)
"""Real estate, depreciable property, and other properties (see parts 1 and 2) dispositions,
Schedule 3 Part 3 "Real estate, depreciable property, and other properties (see parts 1 and 2)" "For
each Gain or loss enter as many lines as necessary.": a starting list with one record for each
disposition, holding "(Column 2): Proceeds of disposition", "(Column 3): Adjusted cost base" and
"(Column 4): Outlays and expenses" (column 1 and the narrative columns feed no line), and the
filer's 0 or 1 depreciable property answer as a fourth field, and the restricted farm loss
(the property taxes and interest part, then the Guide's line C property taxes and line D interest
added to column 3) as a fifth, sixth and seventh."""

REAL_ESTATE_GAIN_OR_LOSS = CATALOG.declare("real_estate_gain_or_loss", Decimal)
"""Real estate, depreciable property, and other properties (see parts 1 and 2) gain or loss,
Schedule 3 line 5 and line 13800 "Total gain or loss (add all the amounts under column 5)": the
rows' column 5 "Gain or loss (column 2 minus columns 3 and 4)" added, a loss in brackets."""

REAL_ESTATE_PROCEEDS = CATALOG.declare("real_estate_proceeds", Decimal, non_negative=True)
"""Real estate, depreciable property, and other properties (see parts 1 and 2) total proceeds,
Schedule 3 line 13599 "Total proceeds of disposition (add all the amounts under column 2)": the
rows' column 2 "Proceeds of disposition" added."""

REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED = CATALOG.declare(
    "real_estate_restricted_farm_loss_applied", Decimal, non_negative=True
)
"""Real estate, depreciable property, and other properties (see parts 1 and 2) restricted farm loss
applied, Guide T4037 p.34 "Plus: Property taxes + $ C" and "Interest + $ D": the rows' property
taxes and interest added to column 3, the amount the filer has applied on this list."""

BOND_DISPOSITIONS = RecordListKind.declare(
    CATALOG,
    "bond_dispositions",
    fields=(DISPOSITION_PROCEEDS, DISPOSITION_ADJUSTED_COST_BASE, DISPOSITION_OUTLAYS),
)
"""Bonds, debentures, promissory notes, and other similar properties dispositions, Schedule 3 Part 3
"Bonds, debentures, promissory notes, and other similar properties" "For each Gain or loss enter as
many lines as necessary.": a starting list with one record for each disposition, holding "(Column
2): Proceeds of disposition", "(Column 3): Adjusted cost base" and "(Column 4): Outlays and
expenses" (column 1 and the narrative columns feed no line)."""

BOND_GAIN_OR_LOSS = CATALOG.declare("bond_gain_or_loss", Decimal)
"""Bonds, debentures, promissory notes, and other similar properties gain or loss, Schedule 3 line 6
and line 15300 "Total gain or loss (add all the amounts under column 5)": the rows' column 5 "Gain
or loss (column 2 minus columns 3 and 4)" added, a loss in brackets."""

BOND_PROCEEDS = CATALOG.declare("bond_proceeds", Decimal, non_negative=True)
"""Bonds, debentures, promissory notes, and other similar properties total proceeds, Schedule 3 line
15199 "Total proceeds of disposition (add all the amounts under column 2)": the rows' column 2
"Proceeds of disposition" added."""

CRYPTO_ASSET_DISPOSITIONS = RecordListKind.declare(
    CATALOG,
    "crypto_asset_dispositions",
    fields=(DISPOSITION_PROCEEDS, DISPOSITION_ADJUSTED_COST_BASE, DISPOSITION_OUTLAYS),
)
"""Crypto-assets dispositions, Schedule 3 Part 3 "Crypto-assets" "For each Gain or loss enter as
many lines as necessary.": a starting list with one record for each disposition, holding "(Column
2): Proceeds of disposition", "(Column 3): Adjusted cost base" and "(Column 4): Outlays and
expenses" (column 1 and the narrative columns feed no line)."""

CRYPTO_ASSET_GAIN_OR_LOSS = CATALOG.declare("crypto_asset_gain_or_loss", Decimal)
"""Crypto-assets gain or loss, Schedule 3 line 7 and line 15301 "Total gain or loss (add all the
amounts under column 5)": the rows' column 5 "Gain or loss (column 2 minus columns 3 and 4)" added,
a loss in brackets."""

CRYPTO_ASSET_PROCEEDS = CATALOG.declare("crypto_asset_proceeds", Decimal, non_negative=True)
"""Crypto-assets total proceeds, Schedule 3 line 15200 "Total proceeds of disposition (add all the
amounts under column 2)": the rows' column 2 "Proceeds of disposition" added."""

OTHER_FORECLOSURE_DISPOSITIONS = RecordListKind.declare(
    CATALOG,
    "other_foreclosure_dispositions",
    fields=(
        DISPOSITION_PROCEEDS,
        DISPOSITION_ADJUSTED_COST_BASE,
        DISPOSITION_OUTLAYS,
        DISPOSITION_FARM_LOSS_TAXES_AND_INTEREST,
        DISPOSITION_FARM_LOSS_PROPERTY_TAXES,
        DISPOSITION_FARM_LOSS_INTEREST,
    ),
)
"""Other mortgage foreclosures and conditional sales repossessions dispositions, Schedule 3 Part 3
"Other mortgage foreclosures and conditional sales repossessions" "For each Gain or loss enter as
many lines as necessary.": a starting list with one record for each disposition, holding "(Column
2): Proceeds of disposition", "(Column 3): Adjusted cost base" and "(Column 4): Outlays and
expenses" (column 1 and the narrative columns feed no line), and the restricted farm loss as on the
qualified farm or fishing property lists (Guide T4037 p.22: a mortgagor whose property is
repossessed is considered to have sold it)."""

OTHER_FORECLOSURE_GAIN_OR_LOSS = CATALOG.declare("other_foreclosure_gain_or_loss", Decimal)
"""Other mortgage foreclosures and conditional sales repossessions gain or loss, Schedule 3 line 8
and line 15500 "Total gain (or loss) (add all the amounts under column 5)": the rows' column 5 "Gain
or loss (column 2 minus columns 3 and 4)" added, a loss in brackets."""

OTHER_FORECLOSURE_PROCEEDS = CATALOG.declare(
    "other_foreclosure_proceeds", Decimal, non_negative=True
)
"""Other mortgage foreclosures and conditional sales repossessions total proceeds, Schedule 3 line
15499 "Total proceeds of disposition (add all the amounts under column 2)": the rows' column 2
"Proceeds of disposition" added."""

PERSONAL_USE_PROPERTY_DISPOSITIONS = RecordListKind.declare(
    CATALOG,
    "personal_use_property_dispositions",
    fields=(DISPOSITION_PROCEEDS, DISPOSITION_ADJUSTED_COST_BASE, DISPOSITION_OUTLAYS),
)
"""Personal-use property dispositions, Schedule 3 Part 3 "Personal-use property (see parts 1 and 2)"
"(provide a full description)": a starting list with one record for each disposition, holding
"(Column 2): Proceeds of disposition", "(Column 3): Adjusted cost base" and "(Column 4): Outlays and
expenses". The principal residence rows come from Form T2091(IND), not from this list."""

PERSONAL_USE_PROPERTY_GAIN_ROWS = CATALOG.declare(
    "personal_use_property_gain_rows", Decimal, non_negative=True
)
"""Gain on the personal-use property rows, Schedule 3 "Line 9 and line 15800: Total gain only (add
all the amounts under column 5)": the rows' column 5 added, a row with a loss counting 0. A part of
line 9."""

PERSONAL_USE_PROPERTY_GAIN = CATALOG.declare(
    "personal_use_property_gain", Decimal, non_negative=True
)
"""Personal-use property gain, Schedule 3 "Line 9 and line 15800: Total gain only (add all the
amounts under column 5)": the sum of its parts, today only the rows listed on the form."""

LISTED_PERSONAL_PROPERTY_DISPOSITIONS = RecordListKind.declare(
    CATALOG,
    "listed_personal_property_dispositions",
    fields=(DISPOSITION_PROCEEDS, DISPOSITION_ADJUSTED_COST_BASE, DISPOSITION_OUTLAYS),
)
"""Listed personal property dispositions, Schedule 3 Part 3 "Listed personal property (LPP) (LPP
losses can only be applied against LPP gains)" "(provide a full description)": a starting list with
one record for each disposition, holding "(Column 2): Proceeds of disposition", "(Column 3):
Adjusted cost base" and "(Column 4): Outlays and expenses"."""

LISTED_PERSONAL_PROPERTY_GAIN_OR_LOSS = CATALOG.declare(
    "listed_personal_property_gain_or_loss", Decimal
)
"""Listed personal property gain or loss, Schedule 3 Part 3 "Listed personal property (LPP) (LPP
losses can only be applied against LPP gains)": the rows' column 5 "Gain or loss (column 2 minus
columns 3 and 4)" added, a loss in brackets, before "Subtract: unapplied LPP losses from other
years"."""

UNAPPLIED_LISTED_PERSONAL_PROPERTY_LOSSES = CATALOG.declare(
    "unapplied_listed_personal_property_losses", Decimal, non_negative=True
)
"""Unapplied listed personal property losses, Schedule 3 Part 3 "Subtract: unapplied LPP losses from
other years": a starting amount."""

LISTED_PERSONAL_PROPERTY_NET_GAIN = CATALOG.declare(
    "listed_personal_property_net_gain", Decimal, non_negative=True
)
"""Listed personal property net gain, Schedule 3 "Line 10 and line 15900: Net gain only": the rows'
gain or loss less the unapplied LPP losses from other years, not below 0."""

CAPITAL_GAINS_OF_QUALIFIED_AND_OTHER_PROPERTIES = CATALOG.declare(
    "capital_gains_of_qualified_and_other_properties", Decimal
)
"""Total gains or losses of qualified properties and other properties, Schedule 3 "Line 11: Add
lines 1 to 10. Total gains or losses of qualified properties and other properties =", also Part 4
"Line 12: Amount from line 11 of the previous page"."""

CAPITAL_GAINS_DEFERRAL = CATALOG.declare("capital_gains_deferral", Decimal, non_negative=True)
"""Capital gains deferral, Schedule 3 "Line 13 and line 16100: Capital gains deferral from
qualifying dispositions of eligible small business corporation shares included on line 4": a
starting amount. Line 14 reads the checked kind, `ca/capital_gains_deferral_checked`, not this
amount."""

CAPITAL_GAINS_DEFERRAL_CHECKED = CATALOG.declare(
    "capital_gains_deferral_checked", Decimal, non_negative=True
)
"""Capital gains deferral after the check, Schedule 3 "Line 13 and line 16100: Capital gains
deferral from qualifying dispositions of eligible small business corporation shares included on
line 4": `ca/capital_gains_deferral` when it is not more than `ca/share_gain_not_below_zero`
(`core/at_most`), the share gain of line 4. An amount above it is refused, not capped. Line 14
reads this amount."""

CAPITAL_GAINS_AFTER_DEFERRAL = CATALOG.declare("capital_gains_after_deferral", Decimal)
"""Gains or losses after the deferral, Schedule 3 "Line 14: Line 12 minus line 13 =", a loss in
brackets."""

SLIP_CAPITAL_GAINS_OR_LOSSES = CATALOG.declare("slip_capital_gains_or_losses", Decimal)
"""Capital gains or losses from slips, Schedule 3 "Line 15 and line 17400: Capital gains or losses
from your T5, T5013, and T4PS slips": a starting amount, a loss in brackets."""

T3_CAPITAL_GAINS_OR_LOSSES = CATALOG.declare("t3_capital_gains_or_losses", Decimal)
"""Capital gains or losses from T3 slips, Schedule 3 "Line 16 and line 17600: Capital gains or
losses from your T3 slips": a starting amount, a loss in brackets."""

CAPITAL_GAINS_BEFORE_INVESTMENT_LOSS_REDUCTION = CATALOG.declare(
    "capital_gains_before_investment_loss_reduction", Decimal
)
"""Gains or losses before the business investment loss reduction, Schedule 3 "Line 17: Add lines 14
to 16. =", a loss in brackets."""

CAPITAL_GAINS_BEFORE_RESERVES = CATALOG.declare("capital_gains_before_reserves", Decimal)
"""Gains or losses before reserves, Schedule 3 "Line 19 and line 19100: Total gains or losses before
reserves: line 17 minus line 18 =", a loss in brackets."""

SCHEDULE_3_LINE_19200 = CATALOG.declare("schedule_3_line_19200", Decimal)
"""Reserves, Schedule 3 line 19200 "Line 20 and line 19200: Reserves to be included in (or deducted
from) income from Form T2017": the total of the record of `ca/t2017.t2017_line_31`, Form T2017
"Total reserve to be included in income", a deduction in brackets."""

INCLUDED_CAPITAL_GAIN = CATALOG.declare("included_capital_gain", Decimal)
"""Included capital gain, Schedule 3 "Line 24: Line 22 multiplied by the percentage from line 23
=", a net capital loss in brackets."""

PARTNERSHIP_GAINS_AT_FULL_INCLUSION = CATALOG.declare(
    "partnership_gains_at_full_inclusion", Decimal, non_negative=True
)
"""Partnership gains at full inclusion, Schedule 3 line 25 "Line 25 and line 19890: Capital gains
from certain dispositions of an interest in a partnership subject to 100% inclusion rate (if
negative, enter "0")": a starting amount, added to the included capital gain (line 24)."""

TAXABLE_CAPITAL_GAINS = CATALOG.declare("taxable_capital_gains", Decimal, non_negative=True)
"""Taxable capital gains, T1 line 12700: Schedule 3 line 26 "If positive, enter the result on line
12700 of your return", line 24 plus line 25, or 0 when that is negative (a net capital loss)."""

TOTAL_INCOME = CATALOG.declare("total_income", Decimal)
"""Total income, T1 line 15000 "Line 28 plus line 32 Total income": the sum of the income lines
wired so far, in line order, with the taxable dividends (line 12000), the taxable capital gains
and the taxable support payments. Not floored, so a loss larger than the other income is shown in
brackets as the form prints it (T1 line 33 prints no floor; the General Guide says "If you have a
loss, show it on the applicable line using brackets").

The net rental income (line 13) and the net self-employment income (line 27, through line 28) are
part of it.
"""

OTHER_EMPLOYMENT_INCOME = CATALOG.declare("other_employment_income", Decimal, non_negative=True)
"""Other employment income, T1 line 10400 "Other employment income": a starting amount."""

OLD_AGE_SECURITY = CATALOG.declare("old_age_security", Decimal, non_negative=True)
"""Old age security pension, T1 line 11300 "Old age security (OAS) pension (box 18 of the T4A(OAS)
slip)": a starting amount."""

CPP_OR_QPP_BENEFITS = CATALOG.declare("cpp_or_qpp_benefits", Decimal, non_negative=True)
"""CPP or QPP benefits, T1 line 11400 "CPP or QPP benefits (box 20 of the T4A(P) slip)": a starting
amount."""

OTHER_PENSIONS_AND_SUPERANNUATION = CATALOG.declare(
    "other_pensions_and_superannuation", Decimal, non_negative=True
)
"""Other pensions and superannuation, T1 line 11500 "Other pensions and superannuation": a starting
amount."""

ELECTED_SPLIT_PENSION_AMOUNT = CATALOG.declare(
    "elected_split_pension_amount", Decimal, non_negative=True
)
"""Elected split-pension amount, T1 line 11600 "Elected split-pension amount (complete Form T1032)":
the election made with the spouse or common-law partner: Form T1032 line 22 when
`ca/t1032_filer_is_transferring_spouse` is 0 (this return is the receiving spouse's), otherwise
0; worked out, never entered."""

T4AP_DISABILITY_BENEFITS = CATALOG.declare("t4ap_disability_benefits", Decimal, non_negative=True)
"""Disability benefits on the T4A(P) slip, T1 line 11410 "Disability benefits included on line 11400
(box 16 of the T4A(P) slip)": a memo carried as entered, which no step reads. The amount is already
included in line 11400 and must not be added again."""

UNIVERSAL_CHILD_CARE_BENEFIT = CATALOG.declare(
    "universal_child_care_benefit", Decimal, non_negative=True
)
"""Universal child care benefit, T1 line 11700 "Universal child care benefit (UCCB) (see the RC62
slip)": a starting amount."""

UCCB_DESIGNATED_TO_DEPENDANT = CATALOG.declare(
    "uccb_designated_to_dependant", Decimal, non_negative=True
)
"""UCCB amount designated to a dependant, T1 line 11701 "UCCB amount designated to a dependant": a
memo carried as entered, which no step reads."""

EI_AND_OTHER_BENEFITS = CATALOG.declare("ei_and_other_benefits", Decimal, non_negative=True)
"""Employment insurance and other benefits, T1 line 11900 "Employment insurance (EI) and other
benefits (box 14 of the T4E slip)": a starting amount."""

EI_MATERNITY_PARENTAL_BENEFITS = CATALOG.declare(
    "ei_maternity_parental_benefits", Decimal, non_negative=True
)
"""EI maternity and parental benefits, T1 line 11905 "EI maternity and parental benefits, and
provincial parental insurance plan (PPIP) benefits": a memo carried as entered, which no step
reads. The amount is already included in line 11900 and must not be added again."""

T3_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE = CATALOG.declare(
    "t3_taxable_dividends_other_than_eligible", Decimal, non_negative=True
)
"""T3 taxable dividends other than eligible, Federal Worksheet for lines 12000 and 12010 line 1 "Box
32 of all T3 slips": a starting amount."""

T4PS_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE = CATALOG.declare(
    "t4ps_taxable_dividends_other_than_eligible", Decimal, non_negative=True
)
"""T4PS taxable dividends other than eligible, Federal Worksheet for lines 12000 and 12010 line 2
"Box 25 of all T4PS slips": a starting amount."""

T5_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE = CATALOG.declare(
    "t5_taxable_dividends_other_than_eligible", Decimal, non_negative=True
)
"""T5 taxable dividends other than eligible, Federal Worksheet for lines 12000 and 12010 line 3 "Box
11 of all T5 slips": a starting amount."""

T5013_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE = CATALOG.declare(
    "t5013_taxable_dividends_other_than_eligible", Decimal, non_negative=True
)
"""T5013 taxable dividends other than eligible, Federal Worksheet for lines 12000 and 12010 line 4
"Box 130 of all T5013 slips": a starting amount."""

T3_TAXABLE_DIVIDENDS = CATALOG.declare("t3_taxable_dividends", Decimal, non_negative=True)
"""T3 taxable dividends, Federal Worksheet for lines 12000 and 12010 line 6 "Boxes 32 and 50 of all
T3 slips": a starting amount."""

T4PS_TAXABLE_DIVIDENDS = CATALOG.declare("t4ps_taxable_dividends", Decimal, non_negative=True)
"""T4PS taxable dividends, Federal Worksheet for lines 12000 and 12010 line 7 "Boxes 25 and 31 of
all T4PS slips": a starting amount."""

T5_TAXABLE_DIVIDENDS = CATALOG.declare("t5_taxable_dividends", Decimal, non_negative=True)
"""T5 taxable dividends, Federal Worksheet for lines 12000 and 12010 line 8 "Boxes 11 and 25 of all
T5 slips": a starting amount."""

T5013_TAXABLE_DIVIDENDS = CATALOG.declare("t5013_taxable_dividends", Decimal, non_negative=True)
"""T5013 taxable dividends, Federal Worksheet for lines 12000 and 12010 line 9 "Boxes 130 and 133 of
all T5013 slips": a starting amount."""

T3_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED = CATALOG.declare(
    "t3_taxable_dividends_other_than_eligible_checked", Decimal, non_negative=True
)
"""T3 taxable dividends other than eligible after the check, Federal Worksheet for lines 12000 and
12010 line 1 "Box 32 of all T3 slips": `ca/t3_taxable_dividends_other_than_eligible` when it is not
more than `ca/t3_taxable_dividends` (`core/at_most`), the part of the line 6 whole. An amount above
it is refused, not capped. Line 5 reads this amount."""

T4PS_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED = CATALOG.declare(
    "t4ps_taxable_dividends_other_than_eligible_checked", Decimal, non_negative=True
)
"""T4PS taxable dividends other than eligible after the check, Federal Worksheet for lines 12000
and 12010 line 2 "Box 25 of all T4PS slips": `ca/t4ps_taxable_dividends_other_than_eligible` when
it is not more than `ca/t4ps_taxable_dividends` (`core/at_most`), the part of the line 7 whole. An
amount above it is refused, not capped. Line 5 reads this amount."""

T5_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED = CATALOG.declare(
    "t5_taxable_dividends_other_than_eligible_checked", Decimal, non_negative=True
)
"""T5 taxable dividends other than eligible after the check, Federal Worksheet for lines 12000 and
12010 line 3 "Box 11 of all T5 slips": `ca/t5_taxable_dividends_other_than_eligible` when it is not
more than `ca/t5_taxable_dividends` (`core/at_most`), the part of the line 8 whole. An amount above
it is refused, not capped. Line 5 reads this amount."""

T5013_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED = CATALOG.declare(
    "t5013_taxable_dividends_other_than_eligible_checked", Decimal, non_negative=True
)
"""T5013 taxable dividends other than eligible after the check, Federal Worksheet for lines 12000
and 12010 line 4 "Box 130 of all T5013 slips": `ca/t5013_taxable_dividends_other_than_eligible`
when it is not more than `ca/t5013_taxable_dividends` (`core/at_most`), the part of the line 9
whole. An amount above it is refused, not capped. Line 5 reads this amount."""

ELIGIBLE_DIVIDENDS_RECEIVED_WITHOUT_A_SLIP = CATALOG.declare(
    "eligible_dividends_received_without_a_slip", Decimal, non_negative=True
)
"""Eligible dividends received with no slip, Federal Worksheet for lines 12000 and 12010 line 11
"Actual amount of eligible dividends received", under "Taxable amount of dividends if you did not
receive an information slip": a starting amount."""

OTHER_DIVIDENDS_RECEIVED_WITHOUT_A_SLIP = CATALOG.declare(
    "other_dividends_received_without_a_slip", Decimal, non_negative=True
)
"""Other dividends received with no slip, Federal Worksheet for lines 12000 and 12010 line 14
"Actual amount of dividends other than eligible dividends received", under "Taxable amount of
dividends if you did not receive an information slip": a starting amount."""

T3_DIVIDEND_TAX_CREDIT = CATALOG.declare("t3_dividend_tax_credit", Decimal, non_negative=True)
"""T3 dividend tax credit, Federal Worksheet for line 40425 line 1 "Boxes 39 and 51 of all T3
slips": a starting amount."""

T4PS_DIVIDEND_TAX_CREDIT = CATALOG.declare("t4ps_dividend_tax_credit", Decimal, non_negative=True)
"""T4PS dividend tax credit, Federal Worksheet for line 40425 line 2 "Boxes 26 and 32 of all T4PS
slips": a starting amount."""

T5_DIVIDEND_TAX_CREDIT = CATALOG.declare("t5_dividend_tax_credit", Decimal, non_negative=True)
"""T5 dividend tax credit, Federal Worksheet for line 40425 line 3 "Boxes 12 and 26 of all T5
slips": a starting amount."""

T5013_DIVIDEND_TAX_CREDIT = CATALOG.declare("t5013_dividend_tax_credit", Decimal, non_negative=True)
"""T5013 dividend tax credit, Federal Worksheet for line 40425 line 4 "Boxes 131 and 134 of all
T5013 slips": a starting amount."""

SLIP_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE = CATALOG.declare(
    "slip_taxable_dividends_other_than_eligible", Decimal, non_negative=True
)
"""Slip taxable dividends other than eligible, Federal Worksheet for lines 12000 and 12010 line 5
"Add lines 1 to 4. Enter this amount on line 12010 of your return.": the four slip boxes of lines 1
to 4."""

SLIP_TAXABLE_DIVIDENDS = CATALOG.declare("slip_taxable_dividends", Decimal, non_negative=True)
"""Slip taxable dividends, Federal Worksheet for lines 12000 and 12010 line 10 "Add lines 6 to 9.
Enter this amount on line 12000 of your return.": the four slip boxes of lines 6 to 9."""

ELIGIBLE_DIVIDENDS_GROSSED_UP = CATALOG.declare(
    "eligible_dividends_grossed_up", Decimal, non_negative=True
)
"""Eligible dividends grossed up, Federal Worksheet for lines 12000 and 12010 line 13 "Line 11
multiplied by the percentage from line 12": line 12 "Applicable rate 138%" on the eligible dividends
received with no slip."""

OTHER_DIVIDENDS_GROSSED_UP = CATALOG.declare(
    "other_dividends_grossed_up", Decimal, non_negative=True
)
"""Other dividends grossed up, Federal Worksheet for lines 12000 and 12010 line 16 "Line 14
multiplied by the percentage from line 15 Include this amount on line 12010 of your return.": line
15 "Applicable rate 115%" on the dividends other than eligible received with no slip."""

DIVIDENDS_WITHOUT_A_SLIP_GROSSED_UP = CATALOG.declare(
    "dividends_without_a_slip_grossed_up", Decimal, non_negative=True
)
"""Dividends with no slip, grossed up, Federal Worksheet for lines 12000 and 12010 line 17 "Line 13
plus line 16. Include this amount on line 12000 of your return.": the grossed-up eligible dividends
and the grossed-up other dividends."""

TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE = CATALOG.declare(
    "taxable_dividends_other_than_eligible", Decimal, non_negative=True
)
"""Taxable dividends other than eligible, T1 line 12010 "Amount of dividends (other than
eligible)" (use Federal Worksheet): the slip amount (line 5) plus the amount with no slip (line 16).

No federal line reads it, so the manifest returns it as a return line."""

TAXABLE_DIVIDENDS = CATALOG.declare("taxable_dividends", Decimal, non_negative=True)
"""Taxable dividends, T1 line 12000 "Amount of dividends (eligible and other than eligible)"
(use Federal Worksheet): the slip amount (line 10) plus the amount with no slip (line 17); total
income sums it."""

SLIP_DIVIDEND_TAX_CREDIT = CATALOG.declare("slip_dividend_tax_credit", Decimal, non_negative=True)
"""Slip dividend tax credit, Federal Worksheet for line 40425 line 5 "Add lines 1 to 4.": the
credits shown on the T3, T4PS, T5 and T5013 slips, which the worksheet enters on line 40425 as they
are."""

DIVIDENDS_AMOUNT_A = CATALOG.declare("dividends_amount_a", Decimal, non_negative=True)
"""Dividends amount A, Federal Worksheet for line 40425 line A "Amount from line 12000 of your
return (Note 1)", Note 1 being "Enter only the amount of dividends that were not shown on an
information slip.": the worksheet's line 17 for lines 12000 and 12010, the grossed-up dividends with
no slip."""

DIVIDENDS_AMOUNT_B = CATALOG.declare("dividends_amount_b", Decimal, non_negative=True)
"""Dividends amount B, Federal Worksheet for line 40425 line B "Amount from line 12010 of your
return (Note 1)", Note 1 being "Enter only the amount of dividends that were not shown on an
information slip.": the worksheet's line 16 for lines 12000 and 12010, the grossed-up other
dividends with no slip."""

OTHER_DIVIDENDS_CREDIT = CATALOG.declare("other_dividends_credit", Decimal, non_negative=True)
"""Credit on other dividends, Federal Worksheet for line 40425 line 6 "Line B multiplied by
9.0301%": the amount B times the credit rate for dividends other than eligible."""

DIVIDENDS_AMOUNT_A_LESS_B = CATALOG.declare("dividends_amount_a_less_b", Decimal, non_negative=True)
"""Dividends amount A less amount B, Federal Worksheet for line 40425 line C "Amount A minus amount
B": the grossed-up eligible dividends with no slip."""

ELIGIBLE_DIVIDENDS_CREDIT = CATALOG.declare("eligible_dividends_credit", Decimal, non_negative=True)
"""Credit on eligible dividends, Federal Worksheet for line 40425 line 7 (printed "Line 2") "Line C
multiplied by 15.0198%": the amount A less amount B times the credit rate for eligible dividends."""

NO_SLIP_DIVIDEND_TAX_CREDIT = CATALOG.declare(
    "no_slip_dividend_tax_credit", Decimal, non_negative=True
)
"""Dividend tax credit with no slip, Federal Worksheet for line 40425 line 8 "Line 6 plus line 7":
the credit on other dividends and the credit on eligible dividends."""

DIVIDEND_TAX_CREDIT = CATALOG.declare("dividend_tax_credit", Decimal, non_negative=True)
"""Federal dividend tax credit, T1 line 123 (line 40425) "Federal dividend tax credit (use Federal
Worksheet)": Federal Worksheet line 9 "Line 5 plus line 8 Enter this amount on line 40425 of your
return.", the slip credits and the credit with no slip."""

CREDITS_AGAINST_BASIC_FEDERAL_TAX = CATALOG.declare(
    "credits_against_basic_federal_tax", Decimal, non_negative=True
)
"""Credits against the basic federal tax, T1 line 125 "Add lines 122 to 124.": line 122 "Amount from
line 35000", line 123 (40425), the federal dividend tax credit, and line 124 (40427), the minimum
tax carryover applied on Form T691 Part 8 line 12, in line order."""

T3_INVESTMENT_INCOME = CATALOG.declare("t3_investment_income", Decimal, non_negative=True)
"""T3 investment income, Federal Worksheet for line 12100 line 1 "Box 25 of all T3 slips": a
starting amount."""

T5_INVESTMENT_INCOME = CATALOG.declare("t5_investment_income", Decimal, non_negative=True)
"""T5 investment income, Federal Worksheet for line 12100 line 2 "Boxes 13, 14, 15, and 30 of all T5
slips": a starting amount."""

T5013_INVESTMENT_INCOME = CATALOG.declare("t5013_investment_income", Decimal, non_negative=True)
"""T5013 investment income, Federal Worksheet for line 12100 line 3 "Boxes 128, 135, and 146 of all
T5013 slips": a starting amount."""

INVESTMENT_INCOME_CREDITED_NOT_RECEIVED = CATALOG.declare(
    "investment_income_credited_not_received", Decimal, non_negative=True
)
"""Investment income credited and not received, Federal Worksheet for line 12100 line 4 "Amounts
credited to you that you did not receive (such as reinvestments)": a starting amount."""

TAX_REFUND_INTEREST = CATALOG.declare("tax_refund_interest", Decimal, non_negative=True)
"""Interest on a tax refund, Federal Worksheet for line 12100 line 5 "Interest on any tax refund you
received in 2025 as shown on your notice of assessment or reassessment": a starting amount."""

FOREIGN_INVESTMENT_INCOME = CATALOG.declare("foreign_investment_income", Decimal, non_negative=True)
"""Foreign investment income, Federal Worksheet for line 12100 line 6 "Income from foreign sources,
including foreign dividends, in Canadian dollars": a starting amount."""

INVESTMENT_INCOME_WITHOUT_A_SLIP = CATALOG.declare(
    "investment_income_without_a_slip", Decimal, non_negative=True
)
"""Investment income with no slip, Federal Worksheet for line 12100 line 7 "Interest or income
earned from bank accounts, term deposits, guaranteed investment certificates (GICs), and other
similar investments, treasury bills or life insurance policies not reported on any information
slip": a starting amount."""

INVESTMENT_ROYALTIES = CATALOG.declare("investment_royalties", Decimal, non_negative=True)
"""Investment royalties, Federal Worksheet for line 12100 line 8 "Royalties not included on line
10400 or line 13500 of your return": a starting amount."""

INVESTMENT_INCOME_BEFORE_PRIOR_YEARS = CATALOG.declare(
    "investment_income_before_prior_years", Decimal, non_negative=True
)
"""Investment income before the part reported in previous years, Federal Worksheet for line 12100
line 9 "Add lines 1 to 8.": the sum of the eight sources."""

INVESTMENT_INCOME_REPORTED_IN_PREVIOUS_YEARS = CATALOG.declare(
    "investment_income_reported_in_previous_years", Decimal, non_negative=True
)
"""Investment income reported in previous years, Federal Worksheet for line 12100 line 10 "Interest
and other investment income, included on line 9, received and reported in previous years": a
starting amount."""

INVESTMENT_INCOME_REPORTED_IN_PREVIOUS_YEARS_APPLIED = CATALOG.declare(
    "investment_income_reported_in_previous_years_applied", Decimal, non_negative=True
)
"""Investment income reported in previous years, applied, Federal Worksheet for line 12100 line 10
"Interest and other investment income, included on line 9, received and reported in previous
years": the amount received and reported in previous years, refused when above line 9, not
capped."""

INTEREST_AND_OTHER_INVESTMENT_INCOME = CATALOG.declare(
    "interest_and_other_investment_income", Decimal, non_negative=True
)
"""Interest and other investment income, T1 line 12100 "Interest and other investment income (use
Federal Worksheet)": Federal Worksheet line 11 "Line 9 minus line 10. Enter this amount on line
12100 of your return.", the investment income less the part reported in previous years."""

NET_PARTNERSHIP_INCOME = CATALOG.declare("net_partnership_income", Decimal, non_negative=True)
"""Net partnership income, T1 line 12200 "Net partnership income (limited or non-active partners
only)": a starting amount."""

RDSP_INCOME = CATALOG.declare("rdsp_income", Decimal, non_negative=True)
"""Registered disability savings plan income, T1 line 12500 "Registered disability savings plan
(RDSP) income (box 131 of the T4A slip)": a starting amount."""

SUPPORT_PAYMENTS_RECEIVED_TOTAL = CATALOG.declare(
    "support_payments_received_total", Decimal, non_negative=True
)
"""Support payments received, total, T1 line 12799 "Total" under "Line 15: Support payments
received": a memo carried as entered, which no step reads. Line 12800 "Taxable amount" is the
taxable part, a starting amount."""

TAXABLE_SUPPORT_PAYMENTS = CATALOG.declare("taxable_support_payments", Decimal, non_negative=True)
"""Taxable support payments, T1 line 12800 "Taxable amount": a starting amount."""

RRSP_INCOME = CATALOG.declare("rrsp_income", Decimal, non_negative=True)
"""RRSP income, T1 line 12900 "Registered retirement savings plan (RRSP) income (from all T4RSP
slips)": a starting amount. The amounts Form T2205 reports on line 12900 (the RRSP part of its line
11) are added to it in the sum of the income lines (`ca/t2205_on_line_12900`), so the caller no
longer types them here."""

FHSA_INCOME = CATALOG.declare("fhsa_income", Decimal, non_negative=True)
"""Taxable FHSA income, T1 line 12905 "Taxable first home savings account (FHSA) income (see the
T4FHSA slip)": a starting amount."""

OTHER_FHSA_INCOME = CATALOG.declare("other_fhsa_income", Decimal, non_negative=True)
"""Taxable FHSA income - other, T1 line 12906 "Taxable FHSA income - other (see the T4FHSA slip)": a
starting amount."""

OTHER_INCOME = CATALOG.declare("other_income", Decimal, non_negative=True)
"""Other income, T1 line 13000 "Other income": a starting amount."""

TAXABLE_SCHOLARSHIPS = CATALOG.declare("taxable_scholarships", Decimal, non_negative=True)
"""Taxable scholarships, T1 line 13010 "Taxable scholarships, fellowships, bursaries and artists'
project grants": a starting amount."""

BUSINESS_INCOME = CATALOG.declare("business_income", Decimal)
"""Business income, Form T2125 line 9946 "Your net income (loss): Amount 5D minus line 9945": the
net of each statement inside the form, whatever its line code, signed, a loss is negative as the
form prints no floor. T1 line 22 "Business income", line 13500 "Net", is the total of the same
name over the statements whose code is business (1) only."""

PROFESSIONAL_INCOME = CATALOG.declare("professional_income", Decimal)
"""Professional income, T1 line 23 "Professional income", line 13700 "Net": the net of the
statements whose line code is professional (Form T2125 line 9946), totalled over them, signed, a
loss is negative as the form prints no floor."""

COMMISSION_INCOME = CATALOG.declare("commission_income", Decimal)
"""Commission income, T1 line 24 "Commission income", line 13900 "Net": the net of the statements
whose line code is commission (Form T2125 line 9946), totalled over them, signed, a loss is negative
as the form prints no floor."""

FARMING_INCOME = CATALOG.declare("farming_income", Decimal)
"""Farming income, T1 line 25 "Farming income", line 14100 "Net", Form T2042 line 9946 "Your net
income (loss): Amount 5C minus line 9945 (enter this amount on line 14100 of your income tax and
benefit return)": the net farming income of the farming statement, signed, a loss is negative as
the form prints no floor."""

FISHING_INCOME = CATALOG.declare("fishing_income", Decimal)
"""Fishing income, T1 line 26 "Fishing income", line 14300 "Net", Form T2121 line 9946 "Your net
income (loss): Amount 5C minus line 9945 (enter this amount on line 14300 of your income tax and
benefit return)": the net fishing income of the fishing statement, signed, a loss is negative as
the form prints no floor."""

NET_SELF_EMPLOYMENT_INCOME = CATALOG.declare("net_self_employment_income", Decimal)
"""Net self-employment income, T1 line 27 "Add lines 22 to 26. Net self-employment income": the net
business, professional, commission, farming and fishing income, in line order. Negative when the
losses exceed the income, as the form prints no floor.

Part of line 28 "Line 21 plus line 27" and of total income (line 15000). Not part of the working
income of Schedule 6, whose line 3 reads the net self-employment income of the five lines, not
including losses, through its own kind, ca/medical_supplement_self_employment_income. Schedule 8
and Schedule 13 read it.
"""

WORKERS_COMPENSATION_BENEFITS = CATALOG.declare(
    "workers_compensation_benefits", Decimal, non_negative=True
)
"""Workers' compensation benefits, T1 line 14400 "Workers' compensation benefits (box 10 of the
T5007 slip)": a starting amount."""

SOCIAL_ASSISTANCE_PAYMENTS = CATALOG.declare(
    "social_assistance_payments", Decimal, non_negative=True
)
"""Social assistance payments, T1 line 14500 "Social assistance payments": a starting amount."""

NET_FEDERAL_SUPPLEMENTS = CATALOG.declare("net_federal_supplements", Decimal, non_negative=True)
"""Net federal supplements paid, T1 line 14600 "Net federal supplements paid (box 21 of the T4A(OAS)
slip)": a starting amount."""

INCOME_SUPPORT_BENEFITS = CATALOG.declare("income_support_benefits", Decimal, non_negative=True)
"""Income support benefits, T1 line 14700 "Add lines 29 to 31 (see line 25000 in Step 4).": the
workers' compensation benefits, social assistance payments and net federal supplements."""

SHORT_TERM_RENTAL_RELATED_EXPENSES = CATALOG.declare(
    "short_term_rental_related_expenses", Decimal, non_negative=True
)
"""Related expenses of a short-term rental, Form T776 Chart A, column 3 "Related portion of the
total from line 9365 of Part 4": a field of each record of the short-term rental units, not an
artifact of its own."""

SHORT_TERM_RENTAL_NON_COMPLIANT_DAYS = CATALOG.declare(
    "short_term_rental_non_compliant_days", int, non_negative=True
)
"""Non-compliant days of a short-term rental, Form T776 Chart A, column 4 "Number of days the
residential property was a non compliant short-term rental": a field of each record of the
short-term rental units, not an artifact of its own."""

SHORT_TERM_RENTAL_DAYS = CATALOG.declare("short_term_rental_days", int, non_negative=True)
"""Days of a short-term rental, Form T776 Chart A, column 5 "Number of days the residential
property was a short-term rental": a field of each record of the short-term rental units, not an
artifact of its own."""

SHORT_TERM_RENTAL_UNITS = RecordListKind.declare(
    CATALOG,
    "short_term_rental_units",
    fields=(
        SHORT_TERM_RENTAL_RELATED_EXPENSES,
        SHORT_TERM_RENTAL_NON_COMPLIANT_DAYS,
        SHORT_TERM_RENTAL_DAYS,
    ),
)
"""Short-term rental units, Form T776 Chart A "Enter each short-term rental or mixed rental
property on a separate row": a starting list with one record for each row, holding column 3
"Related portion of the total from line 9365 of Part 4", column 4 "Number of days the residential
property was a non compliant short-term rental" and column 5 "Number of days the residential
property was a short-term rental" (columns 1 and 2, the address and the unit number, are labels
the engine does not use)."""

SHORT_TERM_RENTAL_RELATED_EXPENSES_TOTAL = CATALOG.declare(
    "short_term_rental_related_expenses_total", Decimal, non_negative=True
)
"""Total of the related expenses of the short-term rentals, Form T776 Chart A
"Column 3: Related portion of the total from line 9365 of Part 4": the column of the short-term
rental units, added."""

SHORT_TERM_RENTAL_RELATED_EXPENSES_TOTAL_CHECKED = CATALOG.declare(
    "short_term_rental_related_expenses_total_checked", Decimal, non_negative=True
)
"""Total of the related expenses of the short-term rentals, Form T776 Chart A
"Column 3: Related portion of the total from line 9365 of Part 4", checked: the total of
`ca/short_term_rental_related_expenses_total` at most `ca/rental_short_term_portion` (line 9365,
`core/at_most`). The form is silent on that check; the refusal is a choice, not a form rule."""

SHORT_TERM_RENTAL_RELATED_CCA = CATALOG.declare(
    "short_term_rental_related_cca", Decimal, non_negative=True
)
"""Related CCA of a short-term rental, Form T776 Chart B, column 4 "Related portion of the
available CCA from column 21 in Area A": a field of each record of the short-term rental CCA
units, not an artifact of its own."""

SHORT_TERM_RENTAL_CCA_UNITS = RecordListKind.declare(
    CATALOG,
    "short_term_rental_cca_units",
    fields=(
        CCA_CLASS_NUMBER,
        SHORT_TERM_RENTAL_RELATED_CCA,
        SHORT_TERM_RENTAL_NON_COMPLIANT_DAYS,
        SHORT_TERM_RENTAL_DAYS,
    ),
)
"""Short-term rental CCA units, Form T776 Chart B "Enter each short-term rental or mixed rental
property on a separate row": a starting list with one record for each row, holding column 1 "Class
number", column 4 "Related portion of the available CCA from column 21 in Area A", column 5
"Number of days the residential property was a non-compliant short-term rental" and column 6
"Number of days the residential property was a short-term rental" (columns 2 and 3, the address
and the unit number, are labels the engine does not use)."""

NON_COMPLIANT_CCA = CATALOG.declare("non_compliant_cca", Decimal, non_negative=True)
"""Non-compliant amount of CCA of a class, Form T776 Area A "Column 22: Non-compliant amount of CCA
(see Chart B below)": a field of each record of the non-compliant CCA by class, not an artifact of
its own."""

SHORT_TERM_RENTAL_NON_COMPLIANT_CCA_BY_CLASS = RecordListKind.declare(
    CATALOG,
    "short_term_rental_non_compliant_cca_by_class",
    fields=(CCA_CLASS_NUMBER, NON_COMPLIANT_CCA),
)
"""Non-compliant CCA by class, Form T776 Chart B "*** For each class, add the amounts from column 7
of Chart B and enter each total in column 22 of Area A, in the respective row.": one record for
each class of the short-term rental CCA units, holding its class number and column 22."""


RENTAL_PROPERTY_UNITS = CATALOG.declare("rental_property_units", int, non_negative=True)
"""Number of units of a rental property, Form T776 Part 3 "Number of units": a field of each
record of the rental properties, not an artifact of its own."""

RENTAL_PROPERTY_SHORT_TERM_RENTS = CATALOG.declare(
    "rental_property_short_term_rents", Decimal, non_negative=True
)
"""Gross rents for short-term rentals of a rental property, Form T776 Part 3 "Gross rents for
short-term rentals": a field of each record of the rental properties, not an artifact of its
own."""

RENTAL_PROPERTY_GROSS_RENTS = CATALOG.declare(
    "rental_property_gross_rents", Decimal, non_negative=True
)
"""Gross rents for all units of a rental property, Form T776 Part 3 "Gross rents for all units": a
field of each record of the rental properties, not an artifact of its own."""

RENTAL_PROPERTIES = RecordListKind.declare(
    CATALOG,
    "rental_properties",
    fields=(
        RENTAL_PROPERTY_UNITS,
        RENTAL_PROPERTY_SHORT_TERM_RENTS,
        RENTAL_PROPERTY_GROSS_RENTS,
    ),
)
"""Rental properties, Form T776 Part 3 "List the addresses of your rental properties." with the
columns "Number of units", "Gross rents for short-term rentals" and "Gross rents for all units": a
starting list with one record for each property, holding those three columns (the address is a
label the engine does not use)."""

SHORT_TERM_RENTAL_GROSS_RENTS = CATALOG.declare(
    "short_term_rental_gross_rents", Decimal, non_negative=True
)
"""Total gross rents for short-term rentals, Form T776 line 8140 "Total of your gross rents for
short-term rentals in the year you receive them (add amounts under "Gross rents for short-term
rentals")": the column of the rental properties, added."""

RENTAL_GROSS_RENTS = CATALOG.declare("rental_gross_rents", Decimal, non_negative=True)
"""Total of all gross rents, Form T776 line 8141 "Total of all your gross rents in the year you
receive them (add lines under "Gross rents for all units")": the column of the rental
properties, added."""

RENTAL_OTHER_INCOME = CATALOG.declare("rental_other_income", Decimal, non_negative=True)
"""Other rental income, Form T776 line 8230 "Other income (for example, premiums and leases,
sharecropping)": a starting amount."""

GROSS_RENTAL_INCOME = CATALOG.declare("gross_rental_income", Decimal, non_negative=True)
"""Gross rental income, Form T776 line 8299 "Total gross rental income: Enter this amount on your
income tax and benefit return on line 12599 (line 8141 plus line 8230)", T1 line 13 and line
12599 "Gross": line 8141 plus line 8230."""

RENTAL_ADVERTISING = CATALOG.declare("rental_advertising", Decimal, non_negative=True)
"""Rental advertising, Form T776 line 8521 "Advertising", "Total expenses": a starting amount."""

RENTAL_ADVERTISING_PERSONAL_PORTION = CATALOG.declare(
    "rental_advertising_personal_portion", Decimal, non_negative=True
)
"""Personal portion of the rental advertising, Form T776 line 8521 "Advertising", "Personal
portion of total expenses": a starting amount."""

RENTAL_ADVERTISING_SHORT_TERM_PORTION = CATALOG.declare(
    "rental_advertising_short_term_portion", Decimal, non_negative=True
)
"""Short-term rental portion of the rental advertising, Form T776 line 8521 "Advertising",
"Short-term rental portion of total expenses": a starting amount."""


RENTAL_INSURANCE = CATALOG.declare("rental_insurance", Decimal, non_negative=True)
"""Rental insurance, Form T776 line 8690 "Insurance", "Total expenses": a starting amount."""

RENTAL_INSURANCE_PERSONAL_PORTION = CATALOG.declare(
    "rental_insurance_personal_portion", Decimal, non_negative=True
)
"""Personal portion of the rental insurance, Form T776 line 8690 "Insurance", "Personal portion of
total expenses": a starting amount."""

RENTAL_INSURANCE_SHORT_TERM_PORTION = CATALOG.declare(
    "rental_insurance_short_term_portion", Decimal, non_negative=True
)
"""Short-term rental portion of the rental insurance, Form T776 line 8690 "Insurance", "Short-term
rental portion of total expenses": a starting amount."""


RENTAL_INTEREST_AND_BANK_CHARGES = CATALOG.declare(
    "rental_interest_and_bank_charges", Decimal, non_negative=True
)
"""Rental interest and bank charges, Form T776 line 8710 "Interest and bank charges", "Total
expenses": a starting amount."""

RENTAL_INTEREST_AND_BANK_CHARGES_PERSONAL_PORTION = CATALOG.declare(
    "rental_interest_and_bank_charges_personal_portion", Decimal, non_negative=True
)
"""Personal portion of the rental interest and bank charges, Form T776 line 8710 "Interest and
bank charges", "Personal portion of total expenses": a starting amount."""

RENTAL_INTEREST_AND_BANK_CHARGES_SHORT_TERM_PORTION = CATALOG.declare(
    "rental_interest_and_bank_charges_short_term_portion", Decimal, non_negative=True
)
"""Short-term rental portion of the rental interest and bank charges, Form T776 line 8710
"Interest and bank charges", "Short-term rental portion of total expenses": a starting amount."""


RENTAL_OFFICE_EXPENSES = CATALOG.declare("rental_office_expenses", Decimal, non_negative=True)
"""Rental office expenses, Form T776 line 8810 "Office expenses", "Total expenses": a starting
amount."""

RENTAL_OFFICE_EXPENSES_PERSONAL_PORTION = CATALOG.declare(
    "rental_office_expenses_personal_portion", Decimal, non_negative=True
)
"""Personal portion of the rental office expenses, Form T776 line 8810 "Office expenses",
"Personal portion of total expenses": a starting amount."""

RENTAL_OFFICE_EXPENSES_SHORT_TERM_PORTION = CATALOG.declare(
    "rental_office_expenses_short_term_portion", Decimal, non_negative=True
)
"""Short-term rental portion of the rental office expenses, Form T776 line 8810 "Office expenses",
"Short-term rental portion of total expenses": a starting amount."""


RENTAL_PROFESSIONAL_FEES = CATALOG.declare("rental_professional_fees", Decimal, non_negative=True)
"""Rental professional fees, Form T776 line 8860 "Professional fees (including legal and
accounting fees)", "Total expenses": a starting amount."""

RENTAL_PROFESSIONAL_FEES_PERSONAL_PORTION = CATALOG.declare(
    "rental_professional_fees_personal_portion", Decimal, non_negative=True
)
"""Personal portion of the rental professional fees, Form T776 line 8860 "Professional fees
(including legal and accounting fees)", "Personal portion of total expenses": a starting
amount."""

RENTAL_PROFESSIONAL_FEES_SHORT_TERM_PORTION = CATALOG.declare(
    "rental_professional_fees_short_term_portion", Decimal, non_negative=True
)
"""Short-term rental portion of the rental professional fees, Form T776 line 8860 "Professional
fees (including legal and accounting fees)", "Short-term rental portion of total expenses": a
starting amount."""


RENTAL_MANAGEMENT_AND_ADMINISTRATION_FEES = CATALOG.declare(
    "rental_management_and_administration_fees", Decimal, non_negative=True
)
"""Rental management and administration fees, Form T776 line 8871 "Management and administration
fees", "Total expenses": a starting amount."""

RENTAL_MANAGEMENT_AND_ADMINISTRATION_FEES_PERSONAL_PORTION = CATALOG.declare(
    "rental_management_and_administration_fees_personal_portion", Decimal, non_negative=True
)
"""Personal portion of the rental management and administration fees, Form T776 line 8871
"Management and administration fees", "Personal portion of total expenses": a starting amount."""

RENTAL_MANAGEMENT_AND_ADMINISTRATION_FEES_SHORT_TERM_PORTION = CATALOG.declare(
    "rental_management_and_administration_fees_short_term_portion", Decimal, non_negative=True
)
"""Short-term rental portion of the rental management and administration fees, Form T776 line 8871
"Management and administration fees", "Short-term rental portion of total expenses": a starting
amount."""


RENTAL_REPAIRS_AND_MAINTENANCE = CATALOG.declare(
    "rental_repairs_and_maintenance", Decimal, non_negative=True
)
"""Rental repairs and maintenance, Form T776 line 8960 "Repairs and maintenance", "Total
expenses": a starting amount."""

RENTAL_REPAIRS_AND_MAINTENANCE_PERSONAL_PORTION = CATALOG.declare(
    "rental_repairs_and_maintenance_personal_portion", Decimal, non_negative=True
)
"""Personal portion of the rental repairs and maintenance, Form T776 line 8960 "Repairs and
maintenance", "Personal portion of total expenses": a starting amount."""

RENTAL_REPAIRS_AND_MAINTENANCE_SHORT_TERM_PORTION = CATALOG.declare(
    "rental_repairs_and_maintenance_short_term_portion", Decimal, non_negative=True
)
"""Short-term rental portion of the rental repairs and maintenance, Form T776 line 8960 "Repairs
and maintenance", "Short-term rental portion of total expenses": a starting amount."""


RENTAL_SALARIES_WAGES_AND_BENEFITS = CATALOG.declare(
    "rental_salaries_wages_and_benefits", Decimal, non_negative=True
)
"""Rental salaries, wages and benefits, Form T776 line 9060 "Salaries, wages and benefits
(including employer's contributions)", "Total expenses": a starting amount."""

RENTAL_SALARIES_WAGES_AND_BENEFITS_PERSONAL_PORTION = CATALOG.declare(
    "rental_salaries_wages_and_benefits_personal_portion", Decimal, non_negative=True
)
"""Personal portion of the rental salaries, wages and benefits, Form T776 line 9060 "Salaries,
wages and benefits (including employer's contributions)", "Personal portion of total expenses":
a starting amount."""

RENTAL_SALARIES_WAGES_AND_BENEFITS_SHORT_TERM_PORTION = CATALOG.declare(
    "rental_salaries_wages_and_benefits_short_term_portion", Decimal, non_negative=True
)
"""Short-term rental portion of the rental salaries, wages and benefits, Form T776 line 9060
"Salaries, wages and benefits (including employer's contributions)", "Short-term rental portion
of total expenses": a starting amount."""


RENTAL_PROPERTY_TAXES = CATALOG.declare("rental_property_taxes", Decimal, non_negative=True)
"""Rental property taxes, Form T776 line 9180 "Property taxes", "Total expenses": a starting
amount."""

RENTAL_PROPERTY_TAXES_PERSONAL_PORTION = CATALOG.declare(
    "rental_property_taxes_personal_portion", Decimal, non_negative=True
)
"""Personal portion of the rental property taxes, Form T776 line 9180 "Property taxes", "Personal
portion of total expenses": a starting amount."""

RENTAL_PROPERTY_TAXES_SHORT_TERM_PORTION = CATALOG.declare(
    "rental_property_taxes_short_term_portion", Decimal, non_negative=True
)
"""Short-term rental portion of the rental property taxes, Form T776 line 9180 "Property taxes",
"Short-term rental portion of total expenses": a starting amount."""


RENTAL_TRAVEL = CATALOG.declare("rental_travel", Decimal, non_negative=True)
"""Rental travel, Form T776 line 9200 "Travel", "Total expenses": a starting amount."""

RENTAL_TRAVEL_PERSONAL_PORTION = CATALOG.declare(
    "rental_travel_personal_portion", Decimal, non_negative=True
)
"""Personal portion of the rental travel, Form T776 line 9200 "Travel", "Personal portion of total
expenses": a starting amount."""

RENTAL_TRAVEL_SHORT_TERM_PORTION = CATALOG.declare(
    "rental_travel_short_term_portion", Decimal, non_negative=True
)
"""Short-term rental portion of the rental travel, Form T776 line 9200 "Travel", "Short-term
rental portion of total expenses": a starting amount."""


RENTAL_UTILITIES = CATALOG.declare("rental_utilities", Decimal, non_negative=True)
"""Rental utilities, Form T776 line 9220 "Utilities", "Total expenses": a starting amount."""

RENTAL_UTILITIES_PERSONAL_PORTION = CATALOG.declare(
    "rental_utilities_personal_portion", Decimal, non_negative=True
)
"""Personal portion of the rental utilities, Form T776 line 9220 "Utilities", "Personal portion of
total expenses": a starting amount."""

RENTAL_UTILITIES_SHORT_TERM_PORTION = CATALOG.declare(
    "rental_utilities_short_term_portion", Decimal, non_negative=True
)
"""Short-term rental portion of the rental utilities, Form T776 line 9220 "Utilities", "Short-term
rental portion of total expenses": a starting amount."""


RENTAL_MOTOR_VEHICLE_EXPENSES = CATALOG.declare(
    "rental_motor_vehicle_expenses", Decimal, non_negative=True
)
"""Rental motor vehicle expenses, Form T776 line 9281 "Motor vehicle expenses (not including
capital cost allowance)", "Total expenses": a starting amount."""

RENTAL_MOTOR_VEHICLE_EXPENSES_PERSONAL_PORTION = CATALOG.declare(
    "rental_motor_vehicle_expenses_personal_portion", Decimal, non_negative=True
)
"""Personal portion of the rental motor vehicle expenses, Form T776 line 9281 "Motor vehicle
expenses (not including capital cost allowance)", "Personal portion of total expenses": a
starting amount."""

RENTAL_MOTOR_VEHICLE_EXPENSES_SHORT_TERM_PORTION = CATALOG.declare(
    "rental_motor_vehicle_expenses_short_term_portion", Decimal, non_negative=True
)
"""Short-term rental portion of the rental motor vehicle expenses, Form T776 line 9281 "Motor
vehicle expenses (not including capital cost allowance)", "Short-term rental portion of total
expenses": a starting amount."""


RENTAL_OTHER_EXPENSES = CATALOG.declare("rental_other_expenses", Decimal, non_negative=True)
"""Rental other expenses, Form T776 line 9270 "Other expenses", "Total expenses": a starting
amount."""

RENTAL_OTHER_EXPENSES_PERSONAL_PORTION = CATALOG.declare(
    "rental_other_expenses_personal_portion", Decimal, non_negative=True
)
"""Personal portion of the rental other expenses, Form T776 line 9270 "Other expenses", "Personal
portion of total expenses": a starting amount."""

RENTAL_OTHER_EXPENSES_SHORT_TERM_PORTION = CATALOG.declare(
    "rental_other_expenses_short_term_portion", Decimal, non_negative=True
)
"""Short-term rental portion of the rental other expenses, Form T776 line 9270 "Other expenses",
"Short-term rental portion of total expenses": a starting amount."""


RENTAL_TOTAL_EXPENSES = CATALOG.declare("rental_total_expenses", Decimal, non_negative=True)
"""Total rental expenses, Form T776 line A "Total expenses (add amounts listed under "Total
expenses")": the 13 expense lines (8521 to 9270), in line order."""

RENTAL_PERSONAL_PORTION = CATALOG.declare("rental_personal_portion", Decimal, non_negative=True)
"""Personal portion of the rental expenses, Form T776 line 9949 "Total for personal portion (add
amounts listed under "Personal portion of total expenses")": the 13 expense lines, in line
order."""

RENTAL_SHORT_TERM_PORTION = CATALOG.declare("rental_short_term_portion", Decimal, non_negative=True)
"""Short-term rental portion of the rental expenses, Form T776 line 9365 "Total for short-term
rental portion (add amounts listed under "Short-term rental portion of total expenses")": the
13 expense lines, in line order."""

RENTAL_NON_COMPLIANT_EXPENSES = CATALOG.declare(
    "rental_non_compliant_expenses", Decimal, non_negative=True
)
"""Non-compliant amount of the short-term rental expenses, Form T776 line 9366
"Non-compliant amount for short-term rentals (amount B from Chart A)": Chart A line B, the total
of column 6 over the short-term rental units."""

RENTAL_NON_COMPLIANT_EXPENSES_CHECKED = CATALOG.declare(
    "rental_non_compliant_expenses_checked", Decimal, non_negative=True
)
"""Non-compliant amount of the short-term rental expenses, Form T776 line 9366
"Non-compliant amount for short-term rentals (amount B from Chart A)", checked: line B of
`ca/rental_non_compliant_expenses` at most `ca/short_term_rental_related_expenses_total_checked`
(`core/at_most`), so it is read by line 1 after that check. The form is silent on that check; the
refusal is a choice, not a form rule."""

RENTAL_NON_COMPLIANT_CCA = CATALOG.declare("rental_non_compliant_cca", Decimal, non_negative=True)
"""Non-compliant amount of the short-term rental CCA, Form T776 Chart B "Line C: Total
non-compliant amount of CCA for short-term rentals: Total of column 7 (enter on line 9367 of Part
4)": the total of column 7 over the short-term rental CCA units."""

RENTAL_EXPENSES_LESS_PERSONAL_PORTION = CATALOG.declare(
    "rental_expenses_less_personal_portion", Decimal
)
"""Rental expenses less the personal portion, the first step of Form T776 line 1 "Deductible
expenses (amount A minus line 9949 minus line 9366)": amount A minus line 9949, which the form
prints as one line with no figure of its own. Signed: the form prints no floor and no maximum for
the personal portions."""

RENTAL_DEDUCTIBLE_EXPENSES = CATALOG.declare("rental_deductible_expenses", Decimal)
"""Deductible rental expenses, Form T776 line 1 "Deductible expenses (amount A minus line 9949
minus line 9366)": amount A minus line 9949, less line 9366, as the form prints it, signed."""

RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS = CATALOG.declare(
    "rental_net_income_before_adjustments", Decimal
)
"""Rental net income (loss) before adjustments, Form T776 line 9369 "Net income (loss) before
adjustments (total gross rental income from line 8299 minus deductible expenses from amount
1)": signed, a loss is negative."""

RENTAL_COOWNER = CATALOG.declare("rental_coowner", int, non_negative=True)
"""Whether the filer is a co-owner of the rental, Form T776 line 2 "Co-owners: calculate your
share of net income from line 9369. Enter your result on amount 2": 1 for a co-owner, 0 for a
sole proprietor or a partner, a starting count."""

RENTAL_COOWNER_CHECKED = CATALOG.declare("rental_coowner_checked", int, non_negative=True)
"""Whether the filer is a co-owner of the rental, Form T776 "Line 2: Co-owners: calculate your
share of net income from line 9369. Enter your result on amount 2": the answer of
`ca/rental_coowner` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a count of 1 or 0.
A count of 2 or more is refused, not capped."""

RENTAL_COOWNER_SHARE = CATALOG.declare("rental_coowner_share", Decimal)
"""Co-owner's share of the rental net income, Form T776 line 2 "Co-owners: calculate your share of
net income from line 9369. Enter your result on amount 2": a starting amount, signed."""

RENTAL_NET_INCOME_SHARE = CATALOG.declare("rental_net_income_share", Decimal)
"""Rental net income share, Form T776 amount 2 "Co-owners: calculate your share of net income from
line 9369. Enter your result on amount 2": the co-owner's share (line 2, as entered) when the
filer is a co-owner; otherwise line 9369, which is how this wiring reads a sole proprietor's
amount 2 (the form prints no instruction for one)."""

RENTAL_COOWNER_OTHER_EXPENSES = CATALOG.declare(
    "rental_coowner_other_expenses", Decimal, non_negative=True
)
"""Other expenses of the rental co-owner, Form T776 line 9945 "Other expenses of the co-owner:
other deductible expenses you have as a co-owner which you did not deduct elsewhere": a
starting amount."""

RENTAL_NET_INCOME_AFTER_COOWNER_EXPENSES = CATALOG.declare(
    "rental_net_income_after_coowner_expenses", Decimal
)
"""Rental subtotal after the co-owner's other expenses, Form T776 line 3 "Subtotal (amount 2 minus
line 9945)": signed."""

RENTAL_RECAPTURED_CCA = CATALOG.declare("rental_recaptured_cca", Decimal, non_negative=True)
"""Recaptured capital cost allowance on the rental, Form T776 line 9947 "Recaptured capital cost
allowance (co-owners: enter your share of the amount)": a starting amount, as entered."""

RENTAL_NET_INCOME_WITH_RECAPTURE = CATALOG.declare("rental_net_income_with_recapture", Decimal)
"""Rental subtotal with recaptured capital cost allowance, Form T776 line 4 "Subtotal (amount 3
plus line 9947)": signed."""

RENTAL_TERMINAL_LOSS = CATALOG.declare("rental_terminal_loss", Decimal, non_negative=True)
"""Terminal loss on the rental, Form T776 line 9948 "Terminal loss (co-owners: enter your share of
the amount)": a starting amount, as entered."""

RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS = CATALOG.declare(
    "rental_net_income_after_terminal_loss", Decimal
)
"""Rental subtotal after the terminal loss, Form T776 line 5 "Subtotal (amount 4 minus line
9948)": signed."""

RENTAL_CCA_CLAIM = CATALOG.declare("rental_cca_claim", Decimal)
"""Capital cost allowance claimed on the rental, Form T776 line 9936 "Total CCA claim for the year
(amount ii from Area A minus any personal part of CCA, and any CCA for business-use-of home
expenses)": amount ii less the personal part and less the CCA for business-use-of-home expenses,
as the form prints it, signed: the form prints no floor and no maximum for the two parts."""

RENTAL_NET_INCOME_AFTER_CCA = CATALOG.declare("rental_net_income_after_cca", Decimal)
"""Rental net income (loss) of a sole proprietor or a co-owner, Form T776 line 6 "Net income
(loss) (amount 5 minus line 9936)": signed, a loss is negative."""

RENTAL_PARTNER = CATALOG.declare("rental_partner", int, non_negative=True)
"""Whether the filer is a partner in the rental, Form T776 line 7 "Partners: your share of amount
6, or the amount from your T5013 slip, Statement of Partnership Income": 1 for a partner, 0
otherwise, a starting count."""

RENTAL_PARTNER_CHECKED = CATALOG.declare("rental_partner_checked", int, non_negative=True)
"""Whether the filer is a partner in the rental, Form T776 "Line 7: Partners: your share of amount
6, or the amount from your T5013 slip, Statement of Partnership Income": the answer of
`ca/rental_partner` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a count of 1 or 0.
A count of 2 or more is refused, not capped."""

RENTAL_PARTNER_T5013_SLIP = CATALOG.declare("rental_partner_t5013_slip", int, non_negative=True)
"""Whether the filer received a T5013 slip (Statement of Partnership Income), Guide T4036
(confirmed 2026-10-27 from the PDF; no .txt published) "If you determine that you are a member of a
partnership and you received a T5013 slip, fill in only the following fields on Form T776": 1 when
it did, 0 when it did not ("If you are in a partnership and you do not receive a T5013 slip ... fill
in all of the parts in Form T776 that apply to you"), a starting count."""

RENTAL_PARTNER_T5013_SLIP_CHECKED = CATALOG.declare(
    "rental_partner_t5013_slip_checked", int, non_negative=True
)
"""Whether the partnership sent the filer a T5013 slip, the answer of `ca/rental_partner_t5013_slip`
after the check that it is 0 or 1 (`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is
refused, not capped."""

RENTAL_PARTNER_PERCENTAGE = CATALOG.declare("rental_partner_percentage", Decimal, non_negative=True)
"""Your percentage of the partnership, Form T776 Part 1 "Your percentage of the partnership %", as
the form prints a percentage (50 for 50%), a starting amount: the share of amount 6 of a partner
who received no T5013 slip is amount 6 times it. A partner with a slip enters it too (Guide T4036),
and it is then ignored: amount 7 is the slip's."""

RENTAL_PARTNER_PERCENTAGE_CHECKED = CATALOG.declare(
    "rental_partner_percentage_checked", Decimal, non_negative=True
)
"""Your percentage of the partnership, Form T776 Part 1 "Your percentage of the partnership %": the
percentage of `ca/rental_partner_percentage` after the check that it is not more than 100
(`ca/rental_epop_percentage_maximum`, `core/at_most`), entered as the form prints it. A share of
the partnership above the whole is refused, not capped."""

RENTAL_PARTNER_AMOUNT_7_CONFLICT = CATALOG.declare(
    "rental_partner_amount_7_conflict", int, non_negative=True
)
"""Form T776 amount 7 with the partner and T5013 slip answers: 1 when an amount 7 is entered by a
partner who received no slip, else 0, a starting count. Guide T4036 "Amount 7 - Partnerships".
A conclusion the form does not print, not a printed line."""

RENTAL_PARTNER_AMOUNT_7_CONFLICT_CHECKED = CATALOG.declare(
    "rental_partner_amount_7_conflict_checked", int, non_negative=True
)
"""Form T776 amount 7 conflicts, checked: the count of `ca/rental_partner_amount_7_conflict` when it
is 0, the only value produced. A count of 1 is an input error, not capped."""

RENTAL_PARTNER_SHARE_OF_AMOUNT_6 = CATALOG.declare("rental_partner_share_of_amount_6", Decimal)
"""Your share of amount 6, Form T776 line 7 "Partners: your share of amount 6, or the amount from
your T5013 slip": amount 6 times "Your percentage of the partnership %", signed, for a partner who
received no T5013 slip (Guide T4036 "Amount 7 - Partnerships")."""

RENTAL_PARTNER_AMOUNT_7 = CATALOG.declare("rental_partner_amount_7", Decimal)
"""Amount 7, Form T776 "Line 7: Partners: your share of amount 6, or the amount from your T5013
slip, Statement of Partnership Income": the amount from the T5013 slip (`ca/rental_partner_share`)
for a partner who received one, else the share of amount 6 (`ca/rental_partner_share_of_amount_6`),
signed."""

RENTAL_T5013_SLIP_CONFLICT = CATALOG.declare("rental_t5013_slip_conflict", int, non_negative=True)
"""Form T776 T5013 slip answer with the partner answer and the other figures of the statement: 1
when the slip answer is 1 and the partner answer is 0, or when the slip answer is 1 and any of the
amounts below is not 0, else 0 (Guide T4036, confirmed 2026-10-27 from the PDF; no .txt published:
a partner who received a slip fills in "only" the business number, the percentage and amount 7, and
the CCA "is already included in box 110"). The amounts are the CCA claim of amount ii, the gross
rents, the other income, the expense lines, the recapture, the terminal loss, the land additions
and dispositions, the totals of Area A's opening UCC, additions and remaining personal part, and
the total equipment additions of Area B and total building additions of Area C."""

RENTAL_T5013_SLIP_CONFLICT_CHECKED = CATALOG.declare(
    "rental_t5013_slip_conflict_checked", int, non_negative=True
)
"""Form T776 T5013 slip conflicts, checked: the count of `ca/rental_t5013_slip_conflict` when it is
0, the only value produced. A count of 1 is an input error, not capped."""

RENTAL_PARTNER_SHARE = CATALOG.declare("rental_partner_share", Decimal)
"""Partner's share of the rental net income, Form T776 line 7 "Partners: your share of amount 6,
or the amount from your T5013 slip, Statement of Partnership Income": the amount from the T5013
slip of a partner who received one, as entered, signed. A partner who received no slip enters none:
amount 7 is the share of amount 6 (`ca/rental_partner_share_of_amount_6`)."""

RENTAL_PARTNER_GST_HST_REBATE = CATALOG.declare("rental_partner_gst_hst_rebate", Decimal)
"""GST/HST rebate of the rental partner, Form T776 line 9974 "Partners: GST/HST rebate for
partners received in the year": a starting amount."""

RENTAL_PARTNER_OTHER_EXPENSES = CATALOG.declare(
    "rental_partner_other_expenses", Decimal, non_negative=True
)
"""Other expenses of the rental partner, Form T776 line 9943 "Partners: other expenses of the
partner": a starting amount."""

RENTAL_EPOP_ASSOCIATED = CATALOG.declare("rental_epop_associated", int, non_negative=True)
"""Whether the filer is associated with an EPOP, Form T776 Area A Note 5 "$1.5 million, if you are
not associated with any other eligible person or partnership (EPOP) in the tax year" and "amount
iii of Area G, if you are associated with one or more EPOPs in the tax year": 1 if the filer is
associated with one or more EPOPs in the tax year, 0 if not, a starting count. It is Note 5's
association, whether or not an agreement was filed; Area G is filled in when one was."""

RENTAL_EPOP_ASSOCIATED_CHECKED = CATALOG.declare(
    "rental_epop_associated_checked", int, non_negative=True
)
"""Whether the filer is associated with an EPOP, Form T776 Area A Note 5 "$1.5 million, if you
are not associated with any other eligible person or partnership (EPOP) in the tax year": the
answer of `ca/rental_epop_associated` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

RENTAL_EPOP_AGREEMENT_FILED = CATALOG.declare("rental_epop_agreement_filed", int, non_negative=True)
"""Whether the agreement was filed, Form T776 Area A Note 5 "zero, if you are associated with one
or more EPOPs and an agreement that assigns a percentage to one or more of the associated EPOPs
was not filed with the minister in a prescribed form": 1 if the agreement was filed, 0 if it was
not, a starting count."""

RENTAL_EPOP_AGREEMENT_FILED_CHECKED = CATALOG.declare(
    "rental_epop_agreement_filed_checked", int, non_negative=True
)
"""Whether the agreement was filed, Form T776 Area A Note 5 "zero, if you are associated with
one or more EPOPs and an agreement that assigns a percentage to one or more of the associated
EPOPs was not filed with the minister in a prescribed form": the answer of
`ca/rental_epop_agreement_filed` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a
count of 1 or 0. A count of 2 or more is refused, not capped."""

RENTAL_EPOP_PERCENTAGE = CATALOG.declare("rental_epop_percentage", Decimal, non_negative=True)
"""Percentage assigned to the filer, Form T776 Area G "Column 3: Percentage assigned under the
agreement" (the filer's own row), entered as the form prints it, 40 for 40%: a starting
amount."""

RENTAL_EPOP_PERCENTAGE_TOTAL = CATALOG.declare(
    "rental_epop_percentage_total", Decimal, non_negative=True
)
"""Total of the percentages assigned, Form T776 Area G "Total of percentage assigned: Total of
column 3", entered as the form prints it: a starting amount."""

RENTAL_MINISTER_ALLOCATION_GIVEN = CATALOG.declare(
    "rental_minister_allocation_given", int, non_negative=True
)
"""Whether the minister allocated an amount, Form T776 Area A Note 5 "any amount allocated by the
minister under subsection 1104(3.4) of the Regulations": 1 if an amount was allocated, 0
otherwise, a starting count."""

RENTAL_MINISTER_ALLOCATION_GIVEN_CHECKED = CATALOG.declare(
    "rental_minister_allocation_given_checked", int, non_negative=True
)
"""Whether the minister allocated an amount, Form T776 Area A Note 5 "any amount allocated by
the minister under subsection 1104(3.4) of the Regulations": the answer of
`ca/rental_minister_allocation_given` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

RENTAL_MINISTER_ALLOCATION = CATALOG.declare(
    "rental_minister_allocation", Decimal, non_negative=True
)
"""Amount allocated by the minister, Form T776 Area A Note 5 "any amount allocated by the minister
under subsection 1104(3.4) of the Regulations": a starting amount, which replaces the immediate
expensing limit when the minister allocated one."""

RENTAL_IMMEDIATE_EXPENSING_CAP = CATALOG.declare(
    "rental_immediate_expensing_cap", Decimal, non_negative=True
)
"""Immediate expensing limit when not associated, Form T776 Area A Note 5 "$1.5 million, if you are
not associated with any other eligible person or partnership (EPOP) in the tax year" and Area G
line iii "Multiply $1.5 million by": the printed $1.5 million, from a dataset."""

RENTAL_EPOP_PERCENTAGE_MAXIMUM = CATALOG.declare(
    "rental_epop_percentage_maximum", Decimal, non_negative=True
)
"""Largest total of the percentages assigned, Form T776 Area G "The total of all percentages
assigned under the agreement should not be more than 100%" and Note 11 "If the total of column 3
is more than 100%, enter "0."": the printed 100%, from a dataset, as the form prints a percentage
(100 for 100%)."""

RENTAL_IMMEDIATE_EXPENSING_SHARE = CATALOG.declare(
    "rental_immediate_expensing_share", Decimal, non_negative=True
)
"""Immediate expensing limit times the percentage, the first step of Form T776 Area G "Line iii:
Immediate expensing limit allocated to you: Multiply $1.5 million by the percentage assigned to
you in column 3 (see note 11)": $1.5 million times the percentage assigned to you."""

RENTAL_EPOP_PERCENTAGE_ROOM = CATALOG.declare("rental_epop_percentage_room", Decimal)
"""Room under 100% in the percentages assigned, the test of Form T776 Area G Note 11 "If the total
of column 3 is more than 100%, enter "0."": 100 less the total of column 3, signed, negative when
the total is more than 100%."""

RENTAL_IMMEDIATE_EXPENSING_ALLOCATED = CATALOG.declare(
    "rental_immediate_expensing_allocated", Decimal, non_negative=True
)
"""Immediate expensing limit allocated to the filer, Form T776 Area G "Line iii: Immediate
expensing limit allocated to you: Multiply $1.5 million by the percentage assigned to you in
column 3 (see note 11)", Note 11 "If the total of column 3 is more than 100%, enter "0."": the
multiple, or 0 when the total of column 3 is more than 100%."""

RENTAL_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT = CATALOG.declare(
    "rental_immediate_expensing_associated_limit", Decimal, non_negative=True
)
"""Immediate expensing limit when associated with an EPOP, Form T776 Area A Note 5 "amount iii of
Area G, if you are associated with one or more EPOPs in the tax year" and "zero, if you are
associated with one or more EPOPs and an agreement that assigns a percentage to one or more of the
associated EPOPs was not filed with the minister in a prescribed form": line iii, or 0 when no
agreement was filed."""

RENTAL_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER = CATALOG.declare(
    "rental_immediate_expensing_limit_before_minister", Decimal, non_negative=True
)
"""Immediate expensing limit before any amount allocated by the minister, Form T776 Area A Note 5
"the immediate expensing limit, which is equal to one of the following, whichever is applicable":
$1.5 million when not associated with an EPOP, else the limit when associated."""

RENTAL_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION = CATALOG.declare(
    "rental_immediate_expensing_limit_before_proration", Decimal, non_negative=True
)
"""Immediate expensing limit before the days of the fiscal period scale it, Income Tax
Regulations 1104(3.5)(b): "where an eligible person or partnership has a taxation year that is
less than 51 weeks, its immediate expensing limit for the year is that proportion of its
immediate expensing limit for the year determined without reference to this paragraph that the
number of days in the year is of 365". Form T776 Area A Note 5 "the immediate expensing limit,
which is equal to one of the following, whichever is applicable", and "any amount allocated by
the minister under subsection 1104(3.4) of the Regulations": the limit before any amount
allocated by the minister, or that amount when there is one, unscaled. Guide T4036,
"Immediate expensing incentive": "The limit is also prorated for tax years shorter than 365
days"."""

RENTAL_IMMEDIATE_EXPENSING_LIMIT = CATALOG.declare(
    "rental_immediate_expensing_limit", Decimal, non_negative=True
)
"""Immediate expensing limit, Form T776 Area A Note 5 "the immediate expensing limit, which is
equal to one of the following, whichever is applicable", including "any amount allocated by the
minister under subsection 1104(3.4) of the Regulations": the limit above, or the amount allocated
by the minister when there is one."""

RENTAL_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED = CATALOG.declare(
    "rental_immediate_expensing_limit_unprorated", Decimal, non_negative=True
)
"""Immediate expensing limit before the days scaling, Form T776 Area A Note 5 "the immediate
expensing limit, which is equal to one of the following, whichever is applicable", and Guide T4036:
"The limit is also prorated for tax years shorter than 365 days": the per-person limit before the
limit is scaled to the days of the fiscal period, the minister's amount as entered."""

RENTAL_IMMEDIATE_EXPENSING_CLAIM = CATALOG.declare(
    "rental_immediate_expensing_claim", Decimal, non_negative=True
)
"""Total immediate expensing claim for the year, Form T776 Area A "Line i: Total immediate
expensing claim for the year: Total of column 9", limited by Note 5 to "the lesser of" the
immediate expensing limit, "the UCC of DIEPs in column 8" and "the amount of income, if any,
earned from the source of income that is a property (before any CCA deductions)": the total of
column 9 over the classes."""

RENTAL_PARTNER_SHARE_WITH_REBATE = CATALOG.declare("rental_partner_share_with_rebate", Decimal)
"""Rental partner's share with the GST/HST rebate, the first step of Form T776 line 9946 "For
partnerships, enter the result from amount 7 plus line 9974 minus line 9943": amount 7 plus
line 9974."""

RENTAL_PARTNERSHIP_NET_INCOME = CATALOG.declare("rental_partnership_net_income", Decimal)
"""Rental net income (loss) of a partner, Form T776 line 9946 "For partnerships, enter the result
from amount 7 plus line 9974 minus line 9943": amount 7 plus line 9974, less line 9943, signed."""

NET_RENTAL_INCOME = CATALOG.declare("net_rental_income", Decimal)
"""Net rental income, Form T776 line 9946 "Your net income (loss): For sole proprietors or
co-owners, enter the result from amount 6. For partnerships, enter the result from amount 7
plus line 9974 minus line 9943. Enter this amount on line 12600 of your income tax and benefit
return", T1 line 13 and line 12600 "Net": amount 6, or for a partner the partnership figure;
signed, a loss is negative."""

RENTAL_VEHICLE_SALES_TAX_RATE = CATALOG.declare(
    "rental_vehicle_sales_tax_rate", Decimal, non_negative=True
)
"""GST plus PST, or HST, rate on a passenger vehicle, Form T776 Column 5 Note 2 and Guide T4036
"Class 10.1 (30%)" (the prescribed amounts are each "plus the GST/HST or PST"), and the Guide T4036
note "Use the GST rate of 5% and the appropriate PST rate for your province or territory. If your
province is a participating province, use the appropriate HST rate.": the rate in percent, so 13
is 13%, a starting amount. The rate feeds the Class 10.1 limit with tax of Form T776 Area A (the
prescribed amount plus the same amount at this rate), which refuses a row above it."""

RENTAL_FISCAL_PERIOD_DAYS_ENTERED = CATALOG.declare(
    "rental_fiscal_period_days_entered", int, non_negative=True
)
"""Days of the fiscal period of Form T776, the days the filer enters when the fiscal period is
shorter than a full year, 0 when none are entered (a full year). Form T776 Part 1 "Fiscal period
from Date (Year/Month/Day) to (Year/12/31)" and Guide T4036 2025 "Fiscal period": "If this is the
first year of operation, enter the year, month, and day you began your rental operation.
Otherwise, enter January 1 of the current year." Guide T4036 2025 Area A "Column 23 – CCA claim
for the year": "In your first year of rental activities, you may have to prorate your CCA claim."
Guide T4036 prints no formula, so the Guide T4002 2025 "You were asking?" rule applies: "Since your
fiscal period is less than 365 days, you have to prorate your CCA claim. ... base your CCA claim on
the number of days in your fiscal period compared to 365 days. In this case, your fiscal period is
214 days." A starting count."""

RENTAL_FISCAL_PERIOD_DAYS = CATALOG.declare("rental_fiscal_period_days", int, non_negative=True)
"""Days of the fiscal period of Form T776 that the CCA claim and closing UCC are prorated by: the
days entered when above 0, else the days in a full year. Guide T4036 2025 Area A "Column 23 – CCA
claim for the year": "In your first year of rental activities, you may have to prorate your CCA
claim." Guide T4036 prints no formula, so the Guide T4002 2025 "You were asking?" rule applies:
"base your CCA claim on the number of days in your fiscal period compared to 365 days" (the
Guide's example: "your fiscal period is 214 days")."""

RENTAL_LAND_ADDITIONS = CATALOG.declare("rental_land_additions", Decimal, non_negative=True)
"""Cost of the land added in the year, Form T776 Area F "Line 9923: Total cost of all land additions
in the year": a starting amount, taken as entered."""

RENTAL_LAND_DISPOSITIONS = CATALOG.declare("rental_land_dispositions", Decimal, non_negative=True)
"""Proceeds of the land disposed of in the year, Form T776 Area F "Line 9924: Total proceeds from
all land dispositions in the year": a starting amount, taken as entered."""

RENTAL_ADDITION_TOTAL_COST = CATALOG.declare(
    "rental_addition_total_cost", Decimal, non_negative=True
)
"""Total cost of an addition, Form T776 Area B and Area C "Column 3: Total cost": a starting
amount, a field of each record of the equipment additions and of the building additions, taken as
entered."""

RENTAL_ADDITION_PERSONAL_PORTION = CATALOG.declare(
    "rental_addition_personal_portion", Decimal, non_negative=True
)
"""Personal portion of an addition, Form T776 Area B and Area C "Column 4: Personal portion (if
applicable)": a starting amount, a field of each record of the equipment additions and of the
building additions, taken as entered."""

RENTAL_EQUIPMENT_ADDITIONS = RecordListKind.declare(
    CATALOG,
    "rental_equipment_additions",
    fields=(CCA_CLASS_NUMBER, RENTAL_ADDITION_TOTAL_COST, RENTAL_ADDITION_PERSONAL_PORTION),
)
"""Equipment additions, Form T776 Area B "Equipment additions in the year": a starting list with
one record for each addition, holding column 1 "Class number", column 3 "Total cost" and column 4
"Personal portion (if applicable)" (column 2, the property details, is a label the engine does not
use; column 5 is worked out)."""

RENTAL_BUILDING_ADDITIONS = RecordListKind.declare(
    CATALOG,
    "rental_building_additions",
    fields=(CCA_CLASS_NUMBER, RENTAL_ADDITION_TOTAL_COST, RENTAL_ADDITION_PERSONAL_PORTION),
)
"""Building additions, Form T776 Area C "Building additions in the year": a starting list with one
record for each addition, holding column 1 "Class number", column 3 "Total cost" and column 4
"Personal portion (if applicable)" (column 2, the property details, is a label the engine does not
use; column 5 is worked out)."""

RENTAL_EQUIPMENT_ADDITIONS_TOTAL = CATALOG.declare(
    "rental_equipment_additions_total", Decimal, non_negative=True
)
"""Total equipment additions in the year, Form T776 Area B "Line 9925: Total equipment additions in
the year: Total of column 5": the rental portion (column 3 minus column 4) of each addition,
added. The line feeds no other line of the form."""

RENTAL_BUILDING_ADDITIONS_TOTAL = CATALOG.declare(
    "rental_building_additions_total", Decimal, non_negative=True
)
"""Total building additions in the year, Form T776 Area C "Line 9927: Total building additions in
the year: Total of column 5": the rental portion (column 3 minus column 4) of each addition,
added. The line feeds no other line of the form."""

CCA_SOLD_ZEPVS = RecordListKind.declare(
    CATALOG,
    "cca_sold_zepvs",
    fields=(
        CCA_VEHICLE_ACQUIRED_YEAR,
        CCA_VEHICLE_COST,
        CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
        CCA_ZEPV_PROCEEDS,
        CCA_ZEPV_DIEP_PROCEEDS,
    ),
)
"""Sold zero-emission passenger vehicles of a Class 54 row, Guide T4036 2025 "Class 54 (30%)":
"Class 54 may include both zero-emission passenger vehicles that do and do not exceed the
prescribed threshold. However, unlike Class 10.1, Class 54 does not establish a separate class for
each vehicle whose cost exceeds the threshold", and "If a zero-emission passenger vehicle is
disposed of to a person or partnership with whom you deal at arm's length, and its cost exceeds the
prescribed amount [...], the proceeds of disposition will be adjusted based on a factor equal to the
prescribed amount as a proportion of the actual cost of the vehicle." One record for each vehicle
sold from the row: the year it was acquired (0 when the rule does not apply to it), its cost, the
government assistance for it, its proceeds and the DIEP part of them. A field of each record of a
list of capital cost allowance classes."""

RENTAL_CCA_CLASSES = RecordListKind.declare(
    CATALOG,
    "rental_cca_classes",
    fields=(
        CCA_CLASS_NUMBER,
        CCA_UCC_AT_START,
        CCA_ADDITIONS,
        CCA_DIEP_ADDITIONS,
        CCA_PROCEEDS,
        CCA_DIEP_PROCEEDS,
        CCA_IMMEDIATE_EXPENSING,
        CCA_AIIP_ADDITIONS,
        CCA_RIIP_ADDITIONS,
        CCA_CLAIMED,
        CCA_NO_PROPERTY_LEFT,
        CCA_PERSONAL_PART_REMAINING,
        CCA_HALF_YEAR_RULE_DIFFERS,
        CCA_RATE_ELECTION,
        CCA_VEHICLE_ACQUIRED_YEAR,
        CCA_VEHICLE_COST,
        CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
        CCA_SOLD_ZEPVS,
    ),
)
"""Rental classes, Form T776 Area A "Calculation of capital cost allowance (CCA) claim": a
starting list with one record for each class, holding the columns the filer enters (class
number, UCC at the start of the year, additions, the DIEP part of the additions, proceeds, the
proceeds of DIEPs, the immediate expensing amount, the AIIP and RIIP parts of the additions, the
CCA claimed), whether any property is left in the class, the remaining personal part of a
property used for both personal and rental use (Note 9), and whether the
additions are treated the opposite way from their class for the half-year rule (column 18), and the
CCA rate the caller elects for it (a purpose-built rental or a building in a separate class),
then the year the vehicle was acquired, its actual cost and the government assistance for it
(Note 2), then the vehicles sold from a Class 54 row, last."""

RENTAL_CCA_CLASSES_ADJUSTED = RecordListKind.declare(
    CATALOG,
    "rental_cca_classes_adjusted",
    fields=tuple(
        field
        for field in RENTAL_CCA_CLASSES.fields
        if field
        not in (
            CCA_VEHICLE_ACQUIRED_YEAR,
            CCA_VEHICLE_COST,
            CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
            CCA_SOLD_ZEPVS,
        )
    ),
)
"""Rental classes with the proceeds adjusted, Form T776 Area A Column 5 Note 2: "The proceeds of
disposition of [...] a passenger vehicle bought after April 18, 2021, that has been included in
Class 10.1, and whose cost is more than the prescribed amount will be adjusted based on a factor
equal to its prescribed amount as a proportion of the actual cost of the vehicle". The list of
rental classes without the year the vehicle was acquired, its cost, the government
assistance and the vehicles sold from a Class 54 row, with columns 5 and 6 (the proceeds and the
proceeds of DIEPs) adjusted."""
RENTAL_CCA_CLASSES_CHECKED = RecordListKind.declare(
    CATALOG,
    "rental_cca_classes_checked",
    fields=RENTAL_CCA_CLASSES.fields,
)
"""Rental classes checked, Form T776 Area A "Calculation of capital cost allowance (CCA) claim":
the list of the rental classes with the cost of additions of each Class 10.1 passenger vehicle
checked, that is, not more than its limit with tax (Guide T4036 "Class 10.1 (30%)"). The rows
are passed on unchanged, with the same fields as the list they check."""

RENTAL_CLOSING_UCC = RecordListKind.declare(
    CATALOG, "rental_closing_ucc", fields=(CCA_CLASS_NUMBER, CCA_UCC_AT_END)
)
"""Rental closing UCC, Form T776 Area A "Column 24: UCC at the end of the year (column 7 minus
column 23)": one record for each class of the rental classes, holding its class number and
column 24."""

RENTAL_CCA_TABLE_RECAPTURE = CATALOG.declare(
    "rental_cca_table_recapture", Decimal, non_negative=True
)
"""Recapture of the rental classes, Form T776 Area A Note 3 "If you have a negative amount in
column 7, add it to income as a recapture under "Recaptured capital cost allowance" on line
9947": the recapture of each class, totalled."""

RENTAL_CCA_TABLE_TERMINAL_LOSS = CATALOG.declare(
    "rental_cca_table_terminal_loss", Decimal, non_negative=True
)
"""Terminal loss of the rental classes, Form T776 Area A Note 3 "If no property is left in the
class and there is a positive amount in this column, deduct the amount from your income as a
terminal loss under "Terminal loss" on line 9948": the terminal loss of each class, totalled."""

RENTAL_CCA_TABLE_CLAIM = CATALOG.declare("rental_cca_table_claim", Decimal, non_negative=True)
"""Total CCA claim of the rental classes, Form T776 Area A "Line ii: Total CCA claim for the year
*: Total of column 23": the CCA claimed on each class, at most its maximum, totalled."""

RENTAL_CCA_OPENING_UCC_TOTAL = CATALOG.declare(
    "rental_cca_opening_ucc_total", Decimal, non_negative=True
)
"""Opening UCC of the rental classes, Form T776 Area A "Column 2: Undepreciated capital cost (UCC)
at the start of the year": the column of each class of the rental classes, totalled. It is a test
of any entry (the T5013 slip partner's check), not a figure of the form."""

RENTAL_CCA_ADDITIONS_TOTAL = CATALOG.declare(
    "rental_cca_additions_total", Decimal, non_negative=True
)
"""Additions of the rental classes, Form T776 Area A "Column 3: Cost of additions in the year", its
DIEP part (column 4) and its AIIP and RIIP parts (columns 11 and 12): the four columns of each
class of the rental classes, added, then totalled. It is a test of any entry (the T5013 slip
partner's check), not a figure of the form."""

RENTAL_CCA_PERSONAL_PART_REMAINING_TOTAL = CATALOG.declare(
    "rental_cca_personal_part_remaining_total", Decimal, non_negative=True
)
"""Remaining personal part of the rental classes, Form T776 Area A Note 9 (column 24): the
remaining personal part of each class of the rental classes, totalled. It is a test of any entry
(the T5013 slip partner's check), not a figure of the form."""

RENTAL_COOWNER_RECAPTURED_CCA = CATALOG.declare(
    "rental_coowner_recaptured_cca", Decimal, non_negative=True
)
"""Co-owner's share of the recapture, Form T776 line 9947 "Recaptured capital cost allowance
(co-owners: enter your share of the amount)": a starting amount, used for a co-owner."""

RENTAL_COOWNER_TERMINAL_LOSS = CATALOG.declare(
    "rental_coowner_terminal_loss", Decimal, non_negative=True
)
"""Co-owner's share of the terminal loss, Form T776 line 9948 "Terminal loss (co-owners: enter
your share of the amount)": a starting amount, used for a co-owner."""

RENTAL_COOWNER_CCA_CLAIM = CATALOG.declare("rental_coowner_cca_claim", Decimal, non_negative=True)
"""Co-owner's share of the CCA claim, Form T776 Area A "Co-owners: Enter only your share of the
total CCA claim for the year from amount ii on line 9936": a starting amount, used for a
co-owner."""

RENTAL_CCA_CLAIM_SHARE = CATALOG.declare("rental_cca_claim_share", Decimal, non_negative=True)
"""Rental CCA claim before deductions, Form T776 Area A amount ii: the co-owner's share for a
co-owner, otherwise the total CCA claim of the rental classes."""

RENTAL_CCA_PERSONAL_PART = CATALOG.declare("rental_cca_personal_part", Decimal, non_negative=True)
"""Personal part of the rental CCA, Form T776 line 9936 "amount ii from Area A minus any personal
part of CCA": a starting amount."""

RENTAL_CCA_BUSINESS_USE_OF_HOME = CATALOG.declare(
    "rental_cca_business_use_of_home", Decimal, non_negative=True
)
"""CCA for business-use-of-home expenses, Form T776 line 9936 "and any CCA for business-use-of
home expenses": a starting amount."""

RENTAL_COOWNER_RECAPTURED_CCA_CHECKED = CATALOG.declare(
    "rental_coowner_recaptured_cca_checked", Decimal, non_negative=True
)
"""Co-owner's share of the recapture, checked, Form T776 line 9947
"Recaptured capital cost allowance (co-owners: enter your share of the amount)": a part of the
recapture of Area A (`ca/rental_cca_table_recapture`), refused above it (`core/at_most`)."""

RENTAL_COOWNER_TERMINAL_LOSS_CHECKED = CATALOG.declare(
    "rental_coowner_terminal_loss_checked", Decimal, non_negative=True
)
"""Co-owner's share of the terminal loss, checked, Form T776 line 9948
"Terminal loss (co-owners: enter your share of the amount)": a part of the terminal loss of Area A
(`ca/rental_cca_table_terminal_loss`), refused above it (`core/at_most`)."""

RENTAL_COOWNER_CCA_CLAIM_CHECKED = CATALOG.declare(
    "rental_coowner_cca_claim_checked", Decimal, non_negative=True
)
"""Co-owner's share of the CCA claim, checked, Form T776 Area A "Co-owners: Enter only your share
of the total CCA claim for the year from amount ii on line 9936": a part of amount ii of Area A
(`ca/rental_cca_table_claim`), refused above it (`core/at_most`)."""

RENTAL_NET_INCOME_LOSS_SIZE = CATALOG.declare(
    "rental_net_income_loss_size", Decimal, non_negative=True
)
"""Size of the rental net loss, Form T776 line 9369 "Net income (loss) before adjustments": the
negation of line 9369 when it is a loss, else 0 (`ca/positive_part_of_negation`), never below
zero."""

RENTAL_NET_INCOME_UPPER_BOUND = CATALOG.declare("rental_net_income_upper_bound", Decimal)
"""Upper bound of the co-owner's share of the rental net income, Form T776 line 2 "Co-owners:
calculate your share of net income from line 9369": the positive part of line 9369, line 9369
plus its loss size (`ca/rental_net_income_loss_size`), so 0 for a loss."""

RENTAL_NET_INCOME_LOWER_BOUND = CATALOG.declare("rental_net_income_lower_bound", Decimal)
"""Lower bound of the co-owner's share of the rental net income, Form T776 line 2 "Co-owners:
calculate your share of net income from line 9369": the negative part of line 9369, line 9369
less its upper bound (`ca/rental_net_income_upper_bound`), so 0 for a profit."""

RENTAL_COOWNER_SHARE_CHECKED = CATALOG.declare("rental_coowner_share_checked", Decimal)
"""Co-owner's share of the rental net income, checked, Form T776 line 2 "Co-owners: calculate your
share of net income from line 9369. Enter your result on amount 2": at most the upper bound of
line 9369 (`ca/rental_net_income_upper_bound`), refused above it (`core/at_most`), signed."""

RENTAL_COOWNER_SHARE_LOWER_CHECKED = CATALOG.declare("rental_coowner_share_lower_checked", Decimal)
"""Co-owner's share of the rental net income, checked against the lower bound, Form T776 line 2
"Co-owners: calculate your share of net income from line 9369": at least the lower bound of line
9369 (`ca/rental_net_income_lower_bound`), so a share of a loss is a loss no larger than the whole,
refused below it (`core/at_most`), signed."""

T776_STATEMENTS = RecordListKind.declare(
    CATALOG,
    "t776_statements",
    fields=(
        RENTAL_PROPERTIES,
        RENTAL_OTHER_INCOME,
        RENTAL_ADVERTISING,
        RENTAL_ADVERTISING_PERSONAL_PORTION,
        RENTAL_ADVERTISING_SHORT_TERM_PORTION,
        RENTAL_INSURANCE,
        RENTAL_INSURANCE_PERSONAL_PORTION,
        RENTAL_INSURANCE_SHORT_TERM_PORTION,
        RENTAL_INTEREST_AND_BANK_CHARGES,
        RENTAL_INTEREST_AND_BANK_CHARGES_PERSONAL_PORTION,
        RENTAL_INTEREST_AND_BANK_CHARGES_SHORT_TERM_PORTION,
        RENTAL_OFFICE_EXPENSES,
        RENTAL_OFFICE_EXPENSES_PERSONAL_PORTION,
        RENTAL_OFFICE_EXPENSES_SHORT_TERM_PORTION,
        RENTAL_PROFESSIONAL_FEES,
        RENTAL_PROFESSIONAL_FEES_PERSONAL_PORTION,
        RENTAL_PROFESSIONAL_FEES_SHORT_TERM_PORTION,
        RENTAL_MANAGEMENT_AND_ADMINISTRATION_FEES,
        RENTAL_MANAGEMENT_AND_ADMINISTRATION_FEES_PERSONAL_PORTION,
        RENTAL_MANAGEMENT_AND_ADMINISTRATION_FEES_SHORT_TERM_PORTION,
        RENTAL_REPAIRS_AND_MAINTENANCE,
        RENTAL_REPAIRS_AND_MAINTENANCE_PERSONAL_PORTION,
        RENTAL_REPAIRS_AND_MAINTENANCE_SHORT_TERM_PORTION,
        RENTAL_SALARIES_WAGES_AND_BENEFITS,
        RENTAL_SALARIES_WAGES_AND_BENEFITS_PERSONAL_PORTION,
        RENTAL_SALARIES_WAGES_AND_BENEFITS_SHORT_TERM_PORTION,
        RENTAL_PROPERTY_TAXES,
        RENTAL_PROPERTY_TAXES_PERSONAL_PORTION,
        RENTAL_PROPERTY_TAXES_SHORT_TERM_PORTION,
        RENTAL_TRAVEL,
        RENTAL_TRAVEL_PERSONAL_PORTION,
        RENTAL_TRAVEL_SHORT_TERM_PORTION,
        RENTAL_UTILITIES,
        RENTAL_UTILITIES_PERSONAL_PORTION,
        RENTAL_UTILITIES_SHORT_TERM_PORTION,
        RENTAL_MOTOR_VEHICLE_EXPENSES,
        RENTAL_MOTOR_VEHICLE_EXPENSES_PERSONAL_PORTION,
        RENTAL_MOTOR_VEHICLE_EXPENSES_SHORT_TERM_PORTION,
        RENTAL_OTHER_EXPENSES,
        RENTAL_OTHER_EXPENSES_PERSONAL_PORTION,
        RENTAL_OTHER_EXPENSES_SHORT_TERM_PORTION,
        SHORT_TERM_RENTAL_UNITS,
        SHORT_TERM_RENTAL_CCA_UNITS,
        RENTAL_COOWNER,
        RENTAL_COOWNER_SHARE,
        RENTAL_COOWNER_OTHER_EXPENSES,
        RENTAL_FISCAL_PERIOD_DAYS_ENTERED,
        RENTAL_LAND_ADDITIONS,
        RENTAL_LAND_DISPOSITIONS,
        RENTAL_VEHICLE_SALES_TAX_RATE,
        RENTAL_CCA_CLASSES,
        RENTAL_EQUIPMENT_ADDITIONS,
        RENTAL_BUILDING_ADDITIONS,
        RENTAL_COOWNER_RECAPTURED_CCA,
        RENTAL_COOWNER_TERMINAL_LOSS,
        RENTAL_COOWNER_CCA_CLAIM,
        RENTAL_CCA_PERSONAL_PART,
        RENTAL_CCA_BUSINESS_USE_OF_HOME,
        RENTAL_PARTNER,
        RENTAL_PARTNER_T5013_SLIP,
        RENTAL_PARTNER_SHARE,
        RENTAL_PARTNER_PERCENTAGE,
        RENTAL_PARTNER_GST_HST_REBATE,
        RENTAL_PARTNER_OTHER_EXPENSES,
        RENTAL_EPOP_ASSOCIATED,
        RENTAL_EPOP_AGREEMENT_FILED,
        RENTAL_EPOP_PERCENTAGE,
        RENTAL_EPOP_PERCENTAGE_TOTAL,
        RENTAL_MINISTER_ALLOCATION_GIVEN,
        RENTAL_MINISTER_ALLOCATION,
    ),
)
"""Statements of Form T776, one record for each statement of real estate rentals the return
carries (one for each rental operation): its fields are the starting amounts, counts and lists of
one statement, Parts 3 and 4, Areas A, B, C and G and
the partner and co-owner lines, in the order of
the form. The form `ca/t776` runs once for each record; T1 line 12600 "Net" adds the lines 9946
of the records. A field is not an artifact of the return."""

RENTAL_CCA_CLAIM_LESS_PERSONAL_PART = CATALOG.declare(
    "rental_cca_claim_less_personal_part", Decimal
)
"""Rental CCA claim less the personal part, the first step of Form T776 line 9936: amount ii
minus the personal part of CCA, signed."""

RENTAL_CCA_LIMIT = CATALOG.declare("rental_cca_limit", Decimal, non_negative=True)
"""Income of one rental property before CCA, Form T776 Area A Note 5 "the amount of income, if any,
earned from the source of income that is a property (before any CCA deductions) in which the
relevant DIEP is used for the tax year": amount 5 ("Line 5: Subtotal (amount 4 minus line 9948)"),
or 0 when amount 5 is negative. It is read by the immediate expensing claim; the CCA claim of an
owner is limited over all the statements together (`ca/rental_cca_limit_all_statements`)."""

RENTAL_INCOME_BEFORE_CCA = CATALOG.declare("rental_income_before_cca", Decimal)
"""Net rental income or loss of one statement before CCA, the figure Guide T4036 "calculate your
overall net income or loss for the year from all your rental properties before you can claim CCA"
adds over the statements: Form T776 amount 5 for an owner or co-owner (a partner answer of 0), or
for a partner (a partner answer of 1, with or without a T5013 slip) amount 7 alone
(`ca/rental_partner_amount_7`), signed. Guide T4036 p.26 (confirmed 2026-10-27 from the PDF; no .txt
published): "If you are a partner, include the net rental income or loss from your T5013 slip in the
calculation." IT-195R4
(docs/cra-forms-2025/web/it195r4-rental-property-cca-restrictions.txt, web page) para 10: "A
partnership that is subject to the CCA restriction calculates the amount of CCA it can claim and
allocates the resulting net rental income or loss among the members of the partnership. ... The
share of partnership rental income or loss allocated to the member will be combined with the total
rental income or loss after expenses, but before CCA, from the member's own rental properties." The
allocated share is already the result after the partnership's CCA, so the statement's own line 9936
is not added to it."""

RENTAL_NO_CCA_CLAIM = CATALOG.declare("rental_no_cca_claim", Decimal, non_negative=True)
"""Zero, the CCA claim on the member's own rental properties of a partner statement, Form T776
"Line 9936: Total CCA claim for the year": no artifact of the form or of the datasets is a zero (the
zero of Schedule 8, `ca/schedule_8_zero`, is that form's own printed "0"), so it is made from the
statement's amount ii of Area A (`ca/rental_cca_table_claim`): it is never below zero, so its
negation is never above zero, and the positive part of such a figure
(`ca/positive_part_of_negation`) is exactly 0. IT-195R4
(docs/cra-forms-2025/web/it195r4-rental-property-cca-restrictions.txt, web page) para 10: CCA "may
be claimed on the member's rental properties (subject to prescribed rates) only to the extent of
that combined rental income"; a partner statement's line 9936 is the partnership's depreciation
allocated to the partner (already inside line 7), not a claim on the partner's own properties."""

RENTAL_CCA_CLAIM_ON_OWN_PROPERTIES = CATALOG.declare("rental_cca_claim_on_own_properties", Decimal)
"""CCA claimed on the person's own rental properties on one statement, the figure tested against the
limit over all statements: the CCA claim of line 9936 (`ca/rental_cca_claim`) for an owner or
co-owner (a partner answer of 0), or 0 (`ca/rental_no_cca_claim`) for a partner, whose line 9936 is
the partnership's depreciation allocated to the partner and already inside line 7. IT-195R4
(docs/cra-forms-2025/web/it195r4-rental-property-cca-restrictions.txt, web page) para 2: "The
entire CCA claim for all the properties must not exceed the total of the rental income from all
properties less the total of the rental losses from the properties."; "If you are a member of a
partnership, the amount of CCA you can claim has already been determined by the partnership" (Guide
T4036 p.26, confirmed 2026-10-27 from the PDF; no .txt published)."""

RENTAL_INCOME_BEFORE_CCA_TOTAL = CATALOG.declare("rental_income_before_cca_total", Decimal)
"""Overall net rental income or loss before CCA of all the statements of Form T776, Guide T4036
"Combine the rental income and loss from all your properties, even if they belong to different
classes": the total of `ca/rental_income_before_cca` over the statements, signed."""

RENTAL_CCA_LIMIT_ALL_STATEMENTS = CATALOG.declare(
    "rental_cca_limit_all_statements", Decimal, non_negative=True
)
"""Most the CCA claimed on all the statements of Form T776 together may be, Guide T4036 "You
cannot use CCA to create or increase a rental loss": the overall net rental income before CCA of
all the statements, or 0 when it is negative."""

RENTAL_CCA_CLAIMS_TOTAL = CATALOG.declare("rental_cca_claims_total", Decimal)
"""Total CCA claim of all the statements on the person's own properties, Form T776 "Line 9936:
Total CCA claim for the year": the total of `ca/rental_cca_claim_on_own_properties` over the
statements of the form, which is line 9936 of an owner or co-owner statement and 0 for a partner
statement, whose line 9936 is the partnership's depreciation, already inside line 7. A
negative claim on one own property offsets the others."""

RENTAL_CCA_TOTAL_CLAIM = CATALOG.declare("rental_cca_total_claim", Decimal)
"""Total CCA claim over all the statements of Form T776, Guide T4036 "If you own more than one
rental property, you have to calculate your overall net income or loss for the year from all your
rental properties before you can claim CCA ... You cannot use CCA to create or increase a rental
loss": the total of `ca/rental_cca_claim_on_own_properties` over the statements (line 9936 of an
owner or co-owner statement, 0 for a partner statement), at most the overall limit
(`ca/rental_cca_limit_all_statements`)."""

BUSINESS_GROSS_SALES = CATALOG.declare("business_gross_sales", Decimal, non_negative=True)
"""Gross sales, commissions or fees, Form T2125 amount 3A "Gross sales, commissions, or fees
(include GST/HST collected or collectible)": a starting amount."""

BUSINESS_SALES_ADJUSTMENTS = CATALOG.declare(
    "business_sales_adjustments", Decimal, non_negative=True
)
"""GST/HST, sales tax, returns and allowances, Form T2125 amount 3B "GST/HST, provincial sales tax,
returns, allowances, discounts, and GST/HST adjustments (included in amount 3A)": a starting
amount."""

BUSINESS_QUICK_METHOD_GST_HST = CATALOG.declare(
    "business_quick_method_gst_hst", Decimal, non_negative=True
)
"""GST/HST collected on quick method sales, Form T2125 amount 3D "GST/HST collected or collectible
on sales, commissions, and fees eligible for the quick method": a starting amount."""

BUSINESS_QUICK_METHOD_REMITTED = CATALOG.declare(
    "business_quick_method_remitted", Decimal, non_negative=True
)
"""GST/HST remitted under the quick method, Form T2125 amount 3E "GST/HST remitted: (sales,
commissions, and fees eligible for the quick method plus GST/HST collected or collectible)
multiplied by the applicable quick method remittance rate": a starting amount, the rate applied by
the filer."""

BUSINESS_RESERVES_DEDUCTED_LAST_YEAR = CATALOG.declare(
    "business_reserves_deducted_last_year", Decimal, non_negative=True
)
"""Reserves deducted last year, Form T2125 line 8290 "Reserves deducted last year": a starting
amount."""

BUSINESS_OTHER_INCOME = CATALOG.declare("business_other_income", Decimal, non_negative=True)
"""Other business income, Form T2125 line 8230 "Other income (specify)": a starting amount, before
the recapture of Area A."""

BUSINESS_OPENING_INVENTORY = CATALOG.declare(
    "business_opening_inventory", Decimal, non_negative=True
)
"""Opening inventory, Form T2125 amount 3Q "Opening inventory (include raw materials, goods in
process, and finished goods)": a starting amount."""

BUSINESS_PURCHASES = CATALOG.declare("business_purchases", Decimal, non_negative=True)
"""Purchases during the year, Form T2125 amount 3R "Purchases during the year (net of returns,
allowances, and discounts)": a starting amount."""

BUSINESS_DIRECT_WAGE_COSTS = CATALOG.declare(
    "business_direct_wage_costs", Decimal, non_negative=True
)
"""Direct wage costs, Form T2125 amount 3S "Direct wage costs": a starting amount."""

BUSINESS_SUBCONTRACTS = CATALOG.declare("business_subcontracts", Decimal, non_negative=True)
"""Subcontracts, Form T2125 amount 3T "Subcontracts": a starting amount."""

BUSINESS_OTHER_COSTS = CATALOG.declare("business_other_costs", Decimal, non_negative=True)
"""Other costs of goods sold, Form T2125 amount 3U "Other costs": a starting amount."""

BUSINESS_CLOSING_INVENTORY = CATALOG.declare(
    "business_closing_inventory", Decimal, non_negative=True
)
"""Closing inventory, Form T2125 line 8500 "Closing inventory (include raw materials, goods in
process, and finished goods)": a starting amount."""

BUSINESS_ADVERTISING = CATALOG.declare("business_advertising", Decimal, non_negative=True)
"""Advertising of the business, Form T2125 line 8521 (amount 4B) "Advertising": a starting
amount."""

BUSINESS_MEALS_AND_ENTERTAINMENT = CATALOG.declare(
    "business_meals_and_entertainment", Decimal, non_negative=True
)
"""Meals and entertainment of the business, Form T2125 line 8523 (amount 4C) "Meals and
entertainment": a starting amount, the allowable part entered by the filer."""

BUSINESS_BAD_DEBTS = CATALOG.declare("business_bad_debts", Decimal, non_negative=True)
"""Bad debts of the business, Form T2125 line 8590 (amount 4D) "Bad debts": a starting amount."""

BUSINESS_INSURANCE = CATALOG.declare("business_insurance", Decimal, non_negative=True)
"""Insurance of the business, Form T2125 line 8690 (amount 4E) "Insurance": a starting amount."""

BUSINESS_INTEREST_AND_BANK_CHARGES = CATALOG.declare(
    "business_interest_and_bank_charges", Decimal, non_negative=True
)
"""Interest and bank charges of the business, Form T2125 line 8710 (amount 4F) "Interest and bank
charges": a starting amount."""

BUSINESS_BUSINESS_TAXES_LICENCES_AND_MEMBERSHIPS = CATALOG.declare(
    "business_business_taxes_licences_and_memberships", Decimal, non_negative=True
)
"""Business taxes, licences and memberships of the business, Form T2125 line 8760 (amount 4G)
"Business taxes, licences, and memberships": a starting amount."""

BUSINESS_OFFICE_EXPENSES = CATALOG.declare("business_office_expenses", Decimal, non_negative=True)
"""Office expenses of the business, Form T2125 line 8810 (amount 4H) "Office expenses": a starting
amount."""

BUSINESS_OFFICE_STATIONERY_AND_SUPPLIES = CATALOG.declare(
    "business_office_stationery_and_supplies", Decimal, non_negative=True
)
"""Office stationery and supplies of the business, Form T2125 line 8811 (amount 4I) "Office
stationery and supplies": a starting amount."""

BUSINESS_PROFESSIONAL_FEES = CATALOG.declare(
    "business_professional_fees", Decimal, non_negative=True
)
"""Professional fees of the business, Form T2125 line 8860 (amount 4J) "Professional fees (includes
legal and accounting fees)": a starting amount."""

BUSINESS_MANAGEMENT_AND_ADMINISTRATION_FEES = CATALOG.declare(
    "business_management_and_administration_fees", Decimal, non_negative=True
)
"""Management and administration fees of the business, Form T2125 line 8871 (amount 4K) "Management
and administration fees": a starting amount."""

BUSINESS_RENT = CATALOG.declare("business_rent", Decimal, non_negative=True)
"""Rent of the business, Form T2125 line 8910 (amount 4L) "Rent": a starting amount."""

BUSINESS_REPAIRS_AND_MAINTENANCE = CATALOG.declare(
    "business_repairs_and_maintenance", Decimal, non_negative=True
)
"""Repairs and maintenance of the business, Form T2125 line 8960 (amount 4M) "Repairs and
maintenance": a starting amount."""

BUSINESS_SALARIES_WAGES_AND_BENEFITS = CATALOG.declare(
    "business_salaries_wages_and_benefits", Decimal, non_negative=True
)
"""Salaries, wages and benefits of the business, Form T2125 line 9060 (amount 4N) "Salaries, wages,
and benefits (including employer's contributions)": a starting amount."""

BUSINESS_PROPERTY_TAXES = CATALOG.declare("business_property_taxes", Decimal, non_negative=True)
"""Property taxes of the business, Form T2125 line 9180 (amount 4O) "Property taxes": a starting
amount."""

BUSINESS_TRAVEL_EXPENSES = CATALOG.declare("business_travel_expenses", Decimal, non_negative=True)
"""Travel expenses of the business, Form T2125 line 9200 (amount 4P) "Travel expenses": a starting
amount."""

BUSINESS_UTILITIES = CATALOG.declare("business_utilities", Decimal, non_negative=True)
"""Utilities of the business, Form T2125 line 9220 (amount 4Q) "Utilities": a starting amount."""

BUSINESS_FUEL_COSTS = CATALOG.declare("business_fuel_costs", Decimal, non_negative=True)
"""Fuel costs of the business, Form T2125 line 9224 (amount 4R) "Fuel costs (except for motor
vehicles)": a starting amount."""

BUSINESS_DELIVERY_FREIGHT_AND_EXPRESS = CATALOG.declare(
    "business_delivery_freight_and_express", Decimal, non_negative=True
)
"""Delivery, freight and express of the business, Form T2125 line 9275 (amount 4S) "Delivery,
freight, and express": a starting amount."""

BUSINESS_MOTOR_VEHICLE_EXPENSES = CATALOG.declare(
    "business_motor_vehicle_expenses", Decimal, non_negative=True
)
"""Motor vehicle expenses of the business, Form T2125 line 9281 (amount 4T) "Motor vehicle expenses
(not including CCA) (amount 16 of Chart A)": amount 16 of Chart A, "Allowable motor vehicle
expenses: Add amounts 13 to 15 (enter this total on line 9281 of Part 4)"."""

# Form T2125 Charts A to C, motor vehicle expenses: the caller's amounts of one vehicle, the
# printed constants (each a dataset of the same name); the lines the charts compute are
# not artifacts.
BUSINESS_VEHICLE_BUSINESS_KILOMETRES = CATALOG.declare(
    "business_vehicle_business_kilometres", Decimal, non_negative=True
)
"""Business kilometres, Form T2125 Chart A amount 1 "Kilometres you drove in the fiscal period that
was part of earning business income": a starting amount."""

BUSINESS_VEHICLE_TOTAL_KILOMETRES = CATALOG.declare(
    "business_vehicle_total_kilometres", Decimal, non_negative=True
)
"""Total kilometres, Form T2125 Chart A amount 2 "Total kilometres you drove in the fiscal period":
a starting amount."""

BUSINESS_VEHICLE_FUEL_AND_OIL = CATALOG.declare(
    "business_vehicle_fuel_and_oil", Decimal, non_negative=True
)
"""Fuel and oil, Form T2125 Chart A amount 3 "Fuel and oil": a starting amount."""

BUSINESS_VEHICLE_INSURANCE = CATALOG.declare(
    "business_vehicle_insurance", Decimal, non_negative=True
)
"""Insurance, Form T2125 Chart A amount 5 "Insurance": a starting amount."""

BUSINESS_VEHICLE_LICENCE_AND_REGISTRATION = CATALOG.declare(
    "business_vehicle_licence_and_registration", Decimal, non_negative=True
)
"""Licence and registration, Form T2125 Chart A amount 6 "Licence and registration": a starting
amount."""

BUSINESS_VEHICLE_MAINTENANCE_AND_REPAIRS = CATALOG.declare(
    "business_vehicle_maintenance_and_repairs", Decimal, non_negative=True
)
"""Maintenance and repairs, Form T2125 Chart A amount 7 "Maintenance and repairs": a starting
amount."""

BUSINESS_VEHICLE_ELECTRICITY_ZEV = CATALOG.declare(
    "business_vehicle_electricity_zev", Decimal, non_negative=True
)
"""Electricity for zero-emission vehicles, Form T2125 Chart A amount 9 "Electricity for
zero-emission vehicles": a starting amount."""

BUSINESS_VEHICLE_OTHER_EXPENSES_10 = CATALOG.declare(
    "business_vehicle_other_expenses_10", Decimal, non_negative=True
)
"""Other motor vehicle expenses, Form T2125 Chart A amount 10 "Other expenses (specify)": a starting
amount."""

BUSINESS_VEHICLE_OTHER_EXPENSES_11 = CATALOG.declare(
    "business_vehicle_other_expenses_11", Decimal, non_negative=True
)
"""Other motor vehicle expenses, Form T2125 Chart A amount 11 "Other expenses (specify)": a starting
amount."""

BUSINESS_VEHICLE_PARKING_FEES = CATALOG.declare(
    "business_vehicle_parking_fees", Decimal, non_negative=True
)
"""Business parking fees, Form T2125 Chart A amount 14 "Business parking fees": a starting
amount."""

BUSINESS_VEHICLE_SUPPLEMENTARY_INSURANCE = CATALOG.declare(
    "business_vehicle_supplementary_insurance", Decimal, non_negative=True
)
"""Supplementary business insurance, Form T2125 Chart A amount 15 "Supplementary business
insurance": a starting amount."""

BUSINESS_VEHICLE_INTEREST_PAYABLE = CATALOG.declare(
    "business_vehicle_interest_payable", Decimal, non_negative=True
)
"""Total interest payable, Form T2125 Chart B amount 17 "Total interest payable (accrual method) or
paid (cash method) in the fiscal period": a starting amount."""

BUSINESS_VEHICLE_INTEREST_DAYS = CATALOG.declare(
    "business_vehicle_interest_days", Decimal, non_negative=True
)
"""Days of interest, Form T2125 Chart B line 18 "... the number of days in the fiscal period for
which interest was payable (accrual method) or paid (cash method)": a starting count of days."""

BUSINESS_VEHICLE_LEASE_CHARGES = CATALOG.declare(
    "business_vehicle_lease_charges", Decimal, non_negative=True
)
"""Total lease charges, Form T2125 Chart C amount 20 "Total lease charges incurred in your current
fiscal period for the vehicle": a starting amount."""

BUSINESS_VEHICLE_LEASE_PAYMENTS_BEFORE = CATALOG.declare(
    "business_vehicle_lease_payments_before", Decimal, non_negative=True
)
"""Lease payments before the fiscal period, Form T2125 Chart C amount 21 "Total lease payments
deducted before your current fiscal period for the vehicle": a starting amount."""

BUSINESS_VEHICLE_LEASE_DAYS = CATALOG.declare(
    "business_vehicle_lease_days", Decimal, non_negative=True
)
"""Days leased, Form T2125 Chart C amount 22 "Total number of days the vehicle was leased in your
current and previous fiscal periods": a starting count of days."""

BUSINESS_VEHICLE_LIST_PRICE = CATALOG.declare(
    "business_vehicle_list_price", Decimal, non_negative=True
)
"""Manufacturer's list price, Form T2125 Chart C amount 23 "Manufacturer's list price": a starting
amount."""

BUSINESS_VEHICLE_SALES_TAX_RATE = CATALOG.declare(
    "business_vehicle_sales_tax_rate", Decimal, non_negative=True
)
"""GST plus PST, or HST, rate, Form T2125 Chart C "Use a GST rate of 5% or HST rate applicable to
your province.": the rate in percent, so 13 is 13% (5 plus 8 in a province with a PST of 8%, 5 where
only the GST applies), a starting amount."""

BUSINESS_VEHICLE_PASSENGER_VEHICLE = CATALOG.declare(
    "business_vehicle_passenger_vehicle", int, non_negative=True
)
"""Passenger vehicle, Form T2125 Chart B "Available interest expense for passenger vehicles and
zero-emission passenger vehicles", Chart C "Eligible leasing cost for passenger vehicles" and Guide
T4002 "When you use a passenger vehicle or a zero-emission passenger vehicle to earn income, there
is a limit on the amount of interest you can deduct." and "You can deduct costs you incur to lease a
passenger vehicle you use to earn income.": 1 when the vehicle is a passenger vehicle or a
zero-emission passenger vehicle, 0 when it is not (the guide's definitions and chart of vehicle
types decide, by the vehicle's type, seating and use in the year it was bought or leased, so the
answer does not change from year to year; a zero-emission vehicle that is not a zero-emission
passenger vehicle is 0, but a leased vehicle that would qualify as a zero-emission passenger vehicle
if owned is 1, Chart C footnote "****"), a starting count. An answer above 1 is refused, not
capped."""

BUSINESS_VEHICLE_PURCHASE_YEAR = CATALOG.declare(
    "business_vehicle_purchase_year", int, non_negative=True
)
"""Year the vehicle was bought, Form T2125 Chart B line 18 footnote "*** For passenger vehicles
bought after 2023. For passenger vehicles bought after 2000 and before 2024, the amount is $300.":
the year, 0 when it does not apply, a starting count."""

BUSINESS_VEHICLE_LEASE_YEAR = CATALOG.declare("business_vehicle_lease_year", int, non_negative=True)
"""Year the lease was entered into, Form T2125 Chart C endnotes 11 to 13 (leases entered into in
2024, 2023, 2022 and before 2022): the year, 0 when it does not apply, a starting count."""

BUSINESS_VEHICLE_LEASE_REPAYMENT_OWING = CATALOG.declare(
    "business_vehicle_lease_repayment_owing", int, non_negative=True
)
"""Repayment owing on a leased passenger vehicle, Guide T4002 (printed page 56) "Repayments and
imputed interest": "When you lease a passenger vehicle, you may have a repayment owing to you, or
you may have imputed interest. If so, you will not be able to use the chart." (Chart C): 1 when the
leased vehicle has a repayment owing to the filer, 0 when it has none, a starting count. It is read
only for a passenger vehicle, as Chart C is. An answer above 1 is refused, not capped."""

BUSINESS_VEHICLE_LEASE_DEPOSITS_MADE = CATALOG.declare(
    "business_vehicle_lease_deposits_made", int, non_negative=True
)
"""Deposits made for a leased passenger vehicle, Guide T4002 (printed page 56) "Repayments and
imputed interest", first condition: "one or more deposits were made for the leased passenger
vehicle": 1 when one or more were, 0 when none were, a starting count. It is read only for a
passenger vehicle, as Chart C is. An answer above 1 is refused, not capped."""

BUSINESS_VEHICLE_LEASE_DEPOSITS_REFUNDABLE = CATALOG.declare(
    "business_vehicle_lease_deposits_refundable", int, non_negative=True
)
"""Refundable deposits on a leased passenger vehicle, Guide T4002 (printed page 56) "Repayments and
imputed interest", second condition: "one or more deposits are refundable": 1 when one or more are,
0 when none are, a starting count. It is read only for a passenger vehicle, as Chart C is. An
answer above 1 is refused, not capped."""

BUSINESS_VEHICLE_LEASE_DEPOSITS_TOTAL = CATALOG.declare(
    "business_vehicle_lease_deposits_total", Decimal, non_negative=True
)
"""Total of the deposits on a leased passenger vehicle, Guide T4002 (printed page 56) "Repayments
and imputed interest", third condition: "the total of the deposits is more than $1,000": a starting
amount, 0 when there are no deposits. It is read only for a passenger vehicle, as Chart C is."""

BUSINESS_VEHICLE_DAYS_DIVISOR = CATALOG.declare(
    "business_vehicle_days_divisor", Decimal, non_negative=True
)
"""Days divisor, Form T2125 Chart B line 18 "($350*** ÷ 30)" and Chart C line 25 "÷ 30": the
printed 30, a dataset of the same name."""

BUSINESS_CCA_PERSONAL_PART = CATALOG.declare(
    "business_cca_personal_part", Decimal, non_negative=True
)
"""Personal part of the business CCA, Form T2125 line 9936 "Capital cost allowance (CCA). Enter
amount ii of Area A minus any personal part and any CCA for business-use-of-home expenses": a
starting amount, the personal part."""

BUSINESS_OTHER_EXPENSES = CATALOG.declare("business_other_expenses", Decimal, non_negative=True)
"""Other business expenses, Form T2125 line 9270 "Other expenses (specify)": a starting amount,
before the terminal loss of Area A."""

BUSINESS_JOURNALISM_LABOUR_TAX_CREDIT = CATALOG.declare(
    "business_journalism_labour_tax_credit", Decimal, non_negative=True
)
"""Canadian journalism labour tax credit, Form T2125 amount 5B "Canadian journalism labour tax
credit allocated to you in the year (box 236 of your T5013 slip)": a starting amount."""

BUSINESS_PARTNER_GST_HST_REBATE = CATALOG.declare("business_partner_gst_hst_rebate", Decimal)
"""GST/HST rebate of the business partner, Form T2125 line 9974 "GST/HST rebate for partners
received in the year": a starting amount."""

BUSINESS_PARTNER_OTHER_AMOUNT_A = CATALOG.declare(
    "business_partner_other_amount_a", Decimal, non_negative=True
)
"""Partner expense 1, Form T2125 amount 6A "List details of expenses: Expense amounts": a starting
amount among the five lines of Part 6."""

BUSINESS_PARTNER_OTHER_AMOUNT_B = CATALOG.declare(
    "business_partner_other_amount_b", Decimal, non_negative=True
)
"""Partner expense 2, Form T2125 amount 6B "List details of expenses: Expense amounts": a starting
amount among the five lines of Part 6."""

BUSINESS_PARTNER_OTHER_AMOUNT_C = CATALOG.declare(
    "business_partner_other_amount_c", Decimal, non_negative=True
)
"""Partner expense 3, Form T2125 amount 6C "List details of expenses: Expense amounts": a starting
amount among the five lines of Part 6."""

BUSINESS_PARTNER_OTHER_AMOUNT_D = CATALOG.declare(
    "business_partner_other_amount_d", Decimal, non_negative=True
)
"""Partner expense 4, Form T2125 amount 6D "List details of expenses: Expense amounts": a starting
amount among the five lines of Part 6."""

BUSINESS_PARTNER_OTHER_AMOUNT_E = CATALOG.declare(
    "business_partner_other_amount_e", Decimal, non_negative=True
)
"""Partner expense 5, Form T2125 amount 6E "List details of expenses: Expense amounts": a starting
amount among the five lines of Part 6."""

BUSINESS_HOME_HEAT = CATALOG.declare("business_home_heat", Decimal, non_negative=True)
"""Heat for the business use of the home, Form T2125 amount 7A "Heat": a starting amount."""

BUSINESS_HOME_ELECTRICITY = CATALOG.declare("business_home_electricity", Decimal, non_negative=True)
"""Electricity for the business use of the home, Form T2125 amount 7B "Electricity": a starting
amount."""

BUSINESS_HOME_INSURANCE = CATALOG.declare("business_home_insurance", Decimal, non_negative=True)
"""Insurance for the business use of the home, Form T2125 amount 7C "Insurance": a starting
amount."""

BUSINESS_HOME_MAINTENANCE = CATALOG.declare("business_home_maintenance", Decimal, non_negative=True)
"""Maintenance for the business use of the home, Form T2125 amount 7D "Maintenance": a starting
amount."""

BUSINESS_HOME_MORTGAGE_INTEREST = CATALOG.declare(
    "business_home_mortgage_interest", Decimal, non_negative=True
)
"""Mortgage interest for the business use of the home, Form T2125 amount 7E "Mortgage interest": a
starting amount."""

BUSINESS_HOME_PROPERTY_TAXES = CATALOG.declare(
    "business_home_property_taxes", Decimal, non_negative=True
)
"""Property taxes for the business use of the home, Form T2125 amount 7F "Property taxes": a
starting amount."""

BUSINESS_HOME_OTHER_EXPENSES = CATALOG.declare(
    "business_home_other_expenses", Decimal, non_negative=True
)
"""Other expenses for the business use of the home, Form T2125 amount 7G "Other expenses (specify)":
a starting amount."""

BUSINESS_HOME_PERSONAL_USE_PART = CATALOG.declare(
    "business_home_personal_use_part", Decimal, non_negative=True
)
"""Personal-use part of the home expenses, Form T2125 amount 7I "Personal-use part of the
business-use-of-home expenses": a starting amount."""

BUSINESS_HOME_CCA = CATALOG.declare("business_home_cca", Decimal, non_negative=True)
"""CCA for the business use of the home, Form T2125 amount 7K "Capital cost allowance (business part
only), which means amount ii of Area A minus any portion of capital cost allowance that is for
personal use or entered on line 9936 of Part 4": a starting amount."""

BUSINESS_HOME_CARRIED_FORWARD = CATALOG.declare(
    "business_home_carried_forward", Decimal, non_negative=True
)
"""Home expenses carried forward from last year, Form T2125 amount 7L "Amount carried forward from
previous year": a starting amount."""

BUSINESS_PARTNER_SHARE = CATALOG.declare("business_partner_share", Decimal)
"""Partner's share of the business net income, Form T2125 amount 5A "Your share of line 9369 or the
amount from your T5013 slip, Statement of Partnership Income": a starting amount, signed."""

BUSINESS_PARTNER = CATALOG.declare("business_partner", int, non_negative=True)
"""Whether the filer is a partner in the business, Form T2125 amount 5A "Your share of line 9369 or
the amount from your T5013 slip, Statement of Partnership Income": 1 for a partner, 0 otherwise, a
starting count."""

BUSINESS_PARTNER_CHECKED = CATALOG.declare("business_partner_checked", int, non_negative=True)
"""Whether the filer is a partner in the business, Form T2125 amount 5A "Your share of line 9369 or
the amount from your T5013 slip, Statement of Partnership Income": the answer of
`ca/business_partner` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a count of 1 or 0.
A count of 2 or more is refused, not capped."""

BUSINESS_CCA_CLASSES = RecordListKind.declare(
    CATALOG,
    "business_cca_classes",
    fields=(
        CCA_CLASS_NUMBER,
        CCA_UCC_AT_START,
        CCA_ADDITIONS,
        CCA_DIEP_ADDITIONS,
        CCA_PROCEEDS,
        CCA_DIEP_PROCEEDS,
        CCA_IMMEDIATE_EXPENSING,
        CCA_AIIP_ADDITIONS,
        CCA_RIIP_ADDITIONS,
        CCA_CLAIMED,
        CCA_NO_PROPERTY_LEFT,
        CCA_PERSONAL_PART_REMAINING,
        CCA_HALF_YEAR_RULE_DIFFERS,
        CCA_RATE_ELECTION,
        CCA_VEHICLE_ACQUIRED_YEAR,
        CCA_VEHICLE_COST,
        CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
        CCA_SOLD_ZEPVS,
    ),
)
"""Business classes, Form T2125 Area A "Calculation of capital cost allowance (CCA) claim": a
starting list with one record for each class, holding the columns the filer enters (class
number, UCC at the start of the year, additions, the DIEP part of the additions, proceeds, the
proceeds of DIEPs, the immediate expensing amount, the AIIP and RIIP parts of the additions, the
CCA claimed), whether any property is left in the class, the remaining personal part of a
property used for both personal and business use (endnote 9), whether the additions are treated the
opposite way from their class for the half-year rule (column 18), and the CCA rate the
caller elects for it (a purpose-built rental or a building in a separate class), then the year the
vehicle was acquired, its actual cost and the government assistance for it (endnote 2),
then the vehicles sold from a Class 54 row, last."""

BUSINESS_CCA_CLASSES_ADJUSTED = RecordListKind.declare(
    CATALOG,
    "business_cca_classes_adjusted",
    fields=tuple(
        field
        for field in BUSINESS_CCA_CLASSES.fields
        if field
        not in (
            CCA_VEHICLE_ACQUIRED_YEAR,
            CCA_VEHICLE_COST,
            CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
            CCA_SOLD_ZEPVS,
        )
    ),
)
"""Business classes with the proceeds adjusted, Form T2125 Area A endnote 2: "The proceeds of
disposition of [...] a passenger vehicle bought after April 18, 2021, that has been included in
Class 10.1, and whose cost is more than the prescribed amount will be adjusted based on a factor
equal to its prescribed amount as a proportion of the actual cost of the vehicle". The list of
business classes without the year the vehicle was acquired, its cost, the government
assistance and the vehicles sold from a Class 54 row, with columns 5 and 6 (the proceeds and the
proceeds of DIEPs) adjusted."""
BUSINESS_CCA_CLASSES_CHECKED = RecordListKind.declare(
    CATALOG,
    "business_cca_classes_checked",
    fields=BUSINESS_CCA_CLASSES.fields,
)
"""Business classes checked, Form T2125 Area A "Calculation of capital cost allowance (CCA) claim":
the list of the business classes with the cost of additions of each Class 10.1 passenger vehicle
checked, that is, not more than its limit with tax (Guide T4002 2025, "Class 10.1 (30%)"). The rows
are passed on unchanged, with the same fields as the list they check."""


BUSINESS_EPOP_ASSOCIATED = CATALOG.declare("business_epop_associated", int, non_negative=True)
"""Whether the filer is associated with an EPOP, Form T2125 Area A endnote 5 "$1.5 million, if you
are not associated with any other eligible person or partnership (EPOP) in the tax year" and
"amount iii of Area G, if you are associated with one or more EPOPs in the tax year": 1 if the
filer is associated with one or more EPOPs in the tax year, 0 if not, a starting count. It is
endnote 5's association, whether or not an agreement was filed; Area G is filled in when one
was."""

BUSINESS_EPOP_ASSOCIATED_CHECKED = CATALOG.declare(
    "business_epop_associated_checked", int, non_negative=True
)
"""Whether the filer is associated with an EPOP, Form T2125 Area A endnote 5 "$1.5 million, if
you are not associated with any other eligible person or partnership (EPOP) in the tax year":
the answer of `ca/business_epop_associated` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

BUSINESS_EPOP_AGREEMENT_FILED = CATALOG.declare(
    "business_epop_agreement_filed", int, non_negative=True
)
"""Whether the agreement was filed, Form T2125 Area A endnote 5 "zero, if you are associated with
one or more EPOPs and an agreement that assigns a percentage to one or more of the associated
EPOPs was not filed with the minister in a prescribed form": 1 if the agreement was filed, 0 if
it was not, a starting count."""

BUSINESS_EPOP_AGREEMENT_FILED_CHECKED = CATALOG.declare(
    "business_epop_agreement_filed_checked", int, non_negative=True
)
"""Whether the agreement was filed, Form T2125 Area A endnote 5 "zero, if you are associated with
one or more EPOPs and an agreement that assigns a percentage to one or more of the associated
EPOPs was not filed with the minister in a prescribed form": the answer of
`ca/business_epop_agreement_filed` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a
count of 1 or 0. A count of 2 or more is refused, not capped."""

BUSINESS_EPOP_PERCENTAGE = CATALOG.declare("business_epop_percentage", Decimal, non_negative=True)
"""Percentage assigned to the business, Form T2125 Area G "Column 3: Percentage assigned under the
agreement" (the filer's own row), entered as the form prints it, 40 for 40%: a starting
amount."""

BUSINESS_EPOP_PERCENTAGE_TOTAL = CATALOG.declare(
    "business_epop_percentage_total", Decimal, non_negative=True
)
"""Total of the percentages assigned, Form T2125 Area G "Total of percentage assigned: Total of
column 3", entered as the form prints it: a starting amount."""

BUSINESS_MINISTER_ALLOCATION_GIVEN = CATALOG.declare(
    "business_minister_allocation_given", int, non_negative=True
)
"""Whether the minister allocated an amount, Form T2125 Area A endnote 5 "any amount allocated by
the minister under subsection 1104(3.4) of the Regulations": 1 if an amount was allocated, 0
otherwise, a starting count."""

BUSINESS_MINISTER_ALLOCATION_GIVEN_CHECKED = CATALOG.declare(
    "business_minister_allocation_given_checked", int, non_negative=True
)
"""Whether the minister allocated an amount, Form T2125 Area A endnote 5 "any amount allocated by
the minister under subsection 1104(3.4) of the Regulations": the answer of
`ca/business_minister_allocation_given` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

BUSINESS_MINISTER_ALLOCATION = CATALOG.declare(
    "business_minister_allocation", Decimal, non_negative=True
)
"""Amount allocated by the minister, Form T2125 Area A endnote 5 "any amount allocated by the
minister under subsection 1104(3.4) of the Regulations": a starting amount, which replaces the
immediate expensing limit when the minister allocated one."""

BUSINESS_FISCAL_PERIOD_FROM = CATALOG.declare("business_fiscal_period_from", int, non_negative=True)
"""First day of the fiscal period of Form T2125 page 1 "Fiscal period From / to, Date (YYYYMMDD)":
a whole number like 20250601, 0 when no dates are entered (a full year). Guide T4002 2025, "A
fiscal period cannot be longer than 12 months.\""""

BUSINESS_FISCAL_PERIOD_TO = CATALOG.declare("business_fiscal_period_to", int, non_negative=True)
"""Last day of the fiscal period of Form T2125 page 1 "Fiscal period From / to, Date (YYYYMMDD)":
a whole number like 20251231, 0 when no dates are entered (a full year). Guide T4002 2025, "A
fiscal period cannot be longer than 12 months.\""""

BUSINESS_LAND_ADDITIONS = CATALOG.declare("business_land_additions", Decimal, non_negative=True)
"""Cost of the land added in the year, Form T2125 Area F "Line 9923: Total cost of all land
additions in the year": a starting amount, taken as entered."""

BUSINESS_LAND_DISPOSITIONS = CATALOG.declare(
    "business_land_dispositions", Decimal, non_negative=True
)
"""Proceeds of the land disposed of in the year, Form T2125 Area F "Line 9924: Total proceeds from
all land dispositions in the year": a starting amount, taken as entered."""

BUSINESS_LIABILITIES = CATALOG.declare("business_liabilities", Decimal, non_negative=True)
"""Total business liabilities, Form T2125 Part 9 "Details of equity" "Line 9931: Total business
liabilities": a starting amount, taken as entered."""

BUSINESS_DRAWINGS = CATALOG.declare("business_drawings", Decimal, non_negative=True)
"""Drawings in the current year, Form T2125 Part 9 "Details of equity" "Line 9932: Drawings in the
current year": a starting amount, taken as entered."""

BUSINESS_CAPITAL_CONTRIBUTIONS = CATALOG.declare(
    "business_capital_contributions", Decimal, non_negative=True
)
"""Capital contributions in the current year, Form T2125 Part 9 "Details of equity" "Line 9933:
Capital contributions in the current year": a starting amount, taken as entered."""

BUSINESS_VEHICLES = RecordListKind.declare(
    CATALOG,
    "business_vehicles",
    fields=(
        BUSINESS_VEHICLE_BUSINESS_KILOMETRES,
        BUSINESS_VEHICLE_TOTAL_KILOMETRES,
        BUSINESS_VEHICLE_FUEL_AND_OIL,
        BUSINESS_VEHICLE_INSURANCE,
        BUSINESS_VEHICLE_LICENCE_AND_REGISTRATION,
        BUSINESS_VEHICLE_MAINTENANCE_AND_REPAIRS,
        BUSINESS_VEHICLE_ELECTRICITY_ZEV,
        BUSINESS_VEHICLE_OTHER_EXPENSES_10,
        BUSINESS_VEHICLE_OTHER_EXPENSES_11,
        BUSINESS_VEHICLE_PARKING_FEES,
        BUSINESS_VEHICLE_SUPPLEMENTARY_INSURANCE,
        BUSINESS_VEHICLE_INTEREST_PAYABLE,
        BUSINESS_VEHICLE_INTEREST_DAYS,
        BUSINESS_VEHICLE_LEASE_CHARGES,
        BUSINESS_VEHICLE_LEASE_PAYMENTS_BEFORE,
        BUSINESS_VEHICLE_LEASE_DAYS,
        BUSINESS_VEHICLE_LIST_PRICE,
        BUSINESS_VEHICLE_PASSENGER_VEHICLE,
        BUSINESS_VEHICLE_PURCHASE_YEAR,
        BUSINESS_VEHICLE_LEASE_YEAR,
        BUSINESS_VEHICLE_LEASE_REPAYMENT_OWING,
        BUSINESS_VEHICLE_LEASE_DEPOSITS_MADE,
        BUSINESS_VEHICLE_LEASE_DEPOSITS_REFUNDABLE,
        BUSINESS_VEHICLE_LEASE_DEPOSITS_TOTAL,
    ),
)
"""Business vehicles, Form T2125 Charts A to C "Motor vehicle expenses": a starting list with one
record for each vehicle, holding the amounts the filer enters in the charts of that vehicle (Chart
A amounts 1, 2, 3, 5, 6, 7, 9, 10, 11, 14 and 15, Chart B amount 17 and its days, Chart C amounts
20, 21, 22 and 23), then whether the vehicle is a passenger vehicle (Charts B and C apply only to
one), the year the vehicle was bought and the year the lease was entered into, which choose the
printed figures of Charts B and C, and the repayment owing and the deposits of a leased passenger
vehicle (Guide T4002 "Repayments and imputed interest"). The charts are worked for each vehicle and
their line 16 amounts added, on line 9281."""

BUSINESS_INCOME_LINE = CATALOG.declare("business_income_line", int, non_negative=True)
"""T1 line of a statement, Form T2125 line 9946 "Report the net income amount from line 9946 on the
applicable line of your income tax and benefit return as indicated below": the code of the choice,
1 business income (line 13500 and line 13499), 2 professional income (line 13700 and line 13699) or
3 commission income (line 13900 and line 13899). The form names no codes. A code outside 1 to 3
names no line, so `ca/count_refused_by_conditions` refuses it (see `business_income_line_checked`).
A starting count."""

BUSINESS_INCOME_LINE_CHECKED = CATALOG.declare(
    "business_income_line_checked", int, non_negative=True
)
"""Statement line code, once checked, Form T2125 line 9946: the `business_income_line` code
unchanged, produced only when it is 1, 2 or 3, the lines the form lists (a code outside them is
refused, so the statement's net and gross never drop out of the return). The three line flags read
this kind, not the raw code."""

T2125_STATEMENTS = RecordListKind.declare(
    CATALOG,
    "t2125_statements",
    fields=(
        BUSINESS_INCOME_LINE,
        BUSINESS_GROSS_SALES,
        BUSINESS_SALES_ADJUSTMENTS,
        BUSINESS_QUICK_METHOD_GST_HST,
        BUSINESS_QUICK_METHOD_REMITTED,
        BUSINESS_RESERVES_DEDUCTED_LAST_YEAR,
        BUSINESS_OTHER_INCOME,
        BUSINESS_OPENING_INVENTORY,
        BUSINESS_PURCHASES,
        BUSINESS_DIRECT_WAGE_COSTS,
        BUSINESS_SUBCONTRACTS,
        BUSINESS_OTHER_COSTS,
        BUSINESS_CLOSING_INVENTORY,
        BUSINESS_ADVERTISING,
        BUSINESS_MEALS_AND_ENTERTAINMENT,
        BUSINESS_BAD_DEBTS,
        BUSINESS_INSURANCE,
        BUSINESS_INTEREST_AND_BANK_CHARGES,
        BUSINESS_BUSINESS_TAXES_LICENCES_AND_MEMBERSHIPS,
        BUSINESS_OFFICE_EXPENSES,
        BUSINESS_OFFICE_STATIONERY_AND_SUPPLIES,
        BUSINESS_PROFESSIONAL_FEES,
        BUSINESS_MANAGEMENT_AND_ADMINISTRATION_FEES,
        BUSINESS_RENT,
        BUSINESS_REPAIRS_AND_MAINTENANCE,
        BUSINESS_SALARIES_WAGES_AND_BENEFITS,
        BUSINESS_PROPERTY_TAXES,
        BUSINESS_TRAVEL_EXPENSES,
        BUSINESS_UTILITIES,
        BUSINESS_FUEL_COSTS,
        BUSINESS_DELIVERY_FREIGHT_AND_EXPRESS,
        BUSINESS_VEHICLE_SALES_TAX_RATE,
        BUSINESS_CCA_PERSONAL_PART,
        BUSINESS_OTHER_EXPENSES,
        BUSINESS_JOURNALISM_LABOUR_TAX_CREDIT,
        BUSINESS_PARTNER_GST_HST_REBATE,
        BUSINESS_PARTNER_OTHER_AMOUNT_A,
        BUSINESS_PARTNER_OTHER_AMOUNT_B,
        BUSINESS_PARTNER_OTHER_AMOUNT_C,
        BUSINESS_PARTNER_OTHER_AMOUNT_D,
        BUSINESS_PARTNER_OTHER_AMOUNT_E,
        BUSINESS_HOME_HEAT,
        BUSINESS_HOME_ELECTRICITY,
        BUSINESS_HOME_INSURANCE,
        BUSINESS_HOME_MAINTENANCE,
        BUSINESS_HOME_MORTGAGE_INTEREST,
        BUSINESS_HOME_PROPERTY_TAXES,
        BUSINESS_HOME_OTHER_EXPENSES,
        BUSINESS_HOME_PERSONAL_USE_PART,
        BUSINESS_HOME_CCA,
        BUSINESS_HOME_CARRIED_FORWARD,
        BUSINESS_PARTNER_SHARE,
        BUSINESS_PARTNER,
        BUSINESS_FISCAL_PERIOD_FROM,
        BUSINESS_FISCAL_PERIOD_TO,
        BUSINESS_LAND_ADDITIONS,
        BUSINESS_LAND_DISPOSITIONS,
        BUSINESS_LIABILITIES,
        BUSINESS_DRAWINGS,
        BUSINESS_CAPITAL_CONTRIBUTIONS,
        BUSINESS_CCA_CLASSES,
        BUSINESS_EPOP_ASSOCIATED,
        BUSINESS_EPOP_AGREEMENT_FILED,
        BUSINESS_EPOP_PERCENTAGE,
        BUSINESS_EPOP_PERCENTAGE_TOTAL,
        BUSINESS_MINISTER_ALLOCATION_GIVEN,
        BUSINESS_MINISTER_ALLOCATION,
        BUSINESS_VEHICLES,
    ),
)
"""Statements of Form T2125, one record for each statement of business or professional activities
the return carries (one for each business): its fields are the starting amounts, the Area A list
and the Area G answers of one statement, Parts 3A to 7 and Chart C, in the order of the form. The
form `ca/t2125` runs once for each record; T1 lines 13500, 13700 and 13900 "Net" add the lines
9946 of the records that the line code sends to them.
A field is not an artifact of the return."""


BUSINESS_SALES_SUBTOTAL = CATALOG.declare("business_sales_subtotal", Decimal, non_negative=True)
"""Business sales subtotal, Form T2125 amount 3C "Subtotal: Amount 3A minus amount 3B": amount 3A
less amount 3B."""

BUSINESS_RECAPTURED_CCA = CATALOG.declare("business_recaptured_cca", Decimal, non_negative=True)
"""Recapture of the business classes, Form T2125 Area A endnote 3 "If you have a negative amount in
column 7, add it to income as a recapture in Part 3C on line 8230": the recapture of each class of
the Area A list, totalled."""

BUSINESS_OTHER_INCOME_WITH_RECAPTURE = CATALOG.declare(
    "business_other_income_with_recapture", Decimal, non_negative=True
)
"""Other business income with the recapture, Form T2125 line 8230 "If you have a negative amount in
column 7, add it to income as a recapture in Part 3C on line 8230": the other income plus the
recapture of Area A."""

BUSINESS_RESERVES_AND_OTHER_INCOME = CATALOG.declare(
    "business_reserves_and_other_income", Decimal, non_negative=True
)
"""Reserves and other business income, Form T2125 amount 3O "Subtotal: Line 8290 plus line 8230":
line 8290 plus line 8230."""

BUSINESS_COST_OF_GOODS_SUBTOTAL = CATALOG.declare(
    "business_cost_of_goods_subtotal", Decimal, non_negative=True
)
"""Cost of goods subtotal, Form T2125 amount 3V "Subtotal: Add amounts 3Q to 3U.": amounts 3Q to 3U
added."""

BUSINESS_COST_OF_GOODS_SOLD = CATALOG.declare(
    "business_cost_of_goods_sold", Decimal, non_negative=True
)
"""Cost of goods sold, Form T2125 line 8518 "Cost of goods sold: Amount 3V minus line 8500": amount
3V less the closing inventory."""

BUSINESS_CCA_TABLE_CLAIM = CATALOG.declare("business_cca_table_claim", Decimal, non_negative=True)
"""CCA claim of the business classes, Form T2125 Area A amount ii "Total CCA claim for the year:
Total of column 21 (enter on line 9936 of Part 4 amount ii": the CCA claimed on each class, at most
its maximum, totalled."""

BUSINESS_CCA_CLAIM_LESS_PERSONAL_PART = CATALOG.declare(
    "business_cca_claim_less_personal_part", Decimal
)
"""Business CCA claim less the personal part, Form T2125 line 9936 "Capital cost allowance (CCA).
Enter amount ii of Area A minus any personal part and any CCA for business-use-of-home expenses":
the first step: amount ii less the personal part of CCA."""

BUSINESS_CCA_CLAIM = CATALOG.declare("business_cca_claim", Decimal)
"""CCA claim of the business, Form T2125 line 9936 (amount 4U) "Capital cost allowance (CCA). Enter
amount ii of Area A minus any personal part and any CCA for business-use-of-home expenses": the
second step: the first step less the CCA for business-use-of-home expenses (amount 7K)."""

BUSINESS_TERMINAL_LOSS = CATALOG.declare("business_terminal_loss", Decimal, non_negative=True)
"""Terminal loss of the business classes, Form T2125 Area A endnote 3 "If no property is left in the
class and there is a positive amount in this column, deduct the amount from income as a terminal
loss in Part 4 on line 9270": the terminal loss of each class of the Area A list, totalled."""

BUSINESS_OTHER_EXPENSES_WITH_TERMINAL_LOSS = CATALOG.declare(
    "business_other_expenses_with_terminal_loss", Decimal, non_negative=True
)
"""Other business expenses with the terminal loss, Form T2125 line 9270 (amount 4V) "Other expenses
(specify)": the other expenses plus the terminal loss of Area A."""

BUSINESS_TOTAL_EXPENSES = CATALOG.declare("business_total_expenses", Decimal)
"""Total business expenses, Form T2125 line 9368 "Total expenses: Total of amounts 4B to 4V":
amounts 4B to 4V added."""

BUSINESS_PARTNER_OTHER_AMOUNTS_TOTAL = CATALOG.declare(
    "business_partner_other_amounts_total", Decimal, non_negative=True
)
"""Total of the partner's other amounts, Form T2125 amount 6F "Total other amounts deductible from
your share of the net partnership income (loss): Add amounts 6A to 6E": amounts 6A to 6E added."""

BUSINESS_PARTNER_OTHER_AMOUNTS = CATALOG.declare(
    "business_partner_other_amounts", Decimal, non_negative=True
)
"""Partner's other amounts deductible, Form T2125 line 9943 "Other amounts deductible from your
share of net partnership income (loss) (amount 6F)": amount 6F."""

BUSINESS_HOME_EXPENSES_SUBTOTAL = CATALOG.declare(
    "business_home_expenses_subtotal", Decimal, non_negative=True
)
"""Home expenses subtotal, Form T2125 amount 7H "Subtotal: Add amounts 7A to 7G.": amounts 7A to 7G
added."""

BUSINESS_HOME_EXPENSES_BUSINESS_PART = CATALOG.declare(
    "business_home_expenses_business_part", Decimal
)
"""Business part of the home expenses, Form T2125 amount 7J "Subtotal: Amount 7H minus amount 7I":
amount 7H less amount 7I."""

BUSINESS_HOME_EXPENSES_AVAILABLE = CATALOG.declare("business_home_expenses_available", Decimal)
"""Home expenses available, Form T2125 amount 7M "Subtotal: Add amounts 7J to 7L.": amounts 7J to 7L
added."""

BUSINESS_HOME_INCOME_LIMIT = CATALOG.declare(
    "business_home_income_limit", Decimal, non_negative=True
)
"""Net income limit on the home expenses, Form T2125 amount 7N "Net income (loss) after adjustments
(amount 5D) (if negative, enter "0")": amount 5D, or 0 when it is negative."""

BUSINESS_HOME_CARRY_FORWARD = CATALOG.declare(
    "business_home_carry_forward", Decimal, non_negative=True
)
"""Home expenses to carry forward, Form T2125 amount 7O "Business-use-of-home expenses available to
carry forward: Amount 7M minus amount 7N (if negative, enter "0")": amount 7M less amount 7N, or 0
when it is negative."""

BUSINESS_HOME_ALLOWABLE_CLAIM = CATALOG.declare("business_home_allowable_claim", Decimal)
"""Allowable home expenses claim, Form T2125 amount 7P "Allowable claim: Amount 7M or 7N above,
whichever is less (enter your share of this amount on line 9945 of Part 5)": the lesser of amounts
7M and 7N."""

BUSINESS_HOME_EXPENSES = CATALOG.declare("business_home_expenses", Decimal)
"""Business-use-of-home expenses, Form T2125 line 9945 "Business-use-of-home expenses (amount 7P)":
amount 7P."""

BUSINESS_QUICK_METHOD_ASSISTANCE = CATALOG.declare("business_quick_method_assistance", Decimal)
"""Quick method government assistance, Form T2125 amount 3F "Subtotal: Amount 3D minus amount 3E":
amount 3D less amount 3E, signed."""

BUSINESS_ADJUSTED_GROSS_SALES = CATALOG.declare("business_adjusted_gross_sales", Decimal)
"""Adjusted gross sales, Form T2125 amount 3G and line 8000 "Adjusted gross sales: Amount 3C plus
amount 3F (enter on line 8000 of Part 3C)": amount 3C plus amount 3F, signed."""

BUSINESS_GROSS_INCOME = CATALOG.declare("business_gross_income", Decimal)
"""Gross business income, Form T2125 line 8299 "Gross business or professional income: Line 8000
plus amount 3O": line 8000 plus amount 3O, signed; the statement's gross before the line code
sends it to T1 line 13499, 13699 or 13899 "Gross"."""

BUSINESS_GROSS_INCOME_FOR_GROSS_PROFIT = CATALOG.declare(
    "business_gross_income_for_gross_profit", Decimal
)
"""Gross business income for the gross profit, Form T2125 amount 3P "Gross business income (line
8299 of Part 3C)": line 8299, signed."""

BUSINESS_GROSS_PROFIT = CATALOG.declare("business_gross_profit", Decimal)
"""Business gross profit, Form T2125 line 8519 "Gross profit (or loss): Amount 3P minus line 8518":
amount 3P less line 8518, signed, a loss is negative."""

BUSINESS_GROSS_INCOME_BEFORE_EXPENSES = CATALOG.declare(
    "business_gross_income_before_expenses", Decimal
)
"""Business income before expenses, Form T2125 amount 4A "Gross business or professional income
(line 8299 of Part 3C) or Gross profit (line 8519 of Part 3D)": line 8519, as a business statement
has a Part 3D; signed."""

GROSS_BUSINESS_INCOME = CATALOG.declare("gross_business_income", Decimal)
"""Gross business income, T1 line 13499 "Gross", Form T2125 line 8299 "Gross business or
professional income: Line 8000 plus amount 3O" "business income on line 13499": the gross of the
statements whose line code is business, totalled over them, signed."""

GROSS_PROFESSIONAL_INCOME = CATALOG.declare("gross_professional_income", Decimal)
"""Gross professional income, T1 line 13699 "Gross", Form T2125 line 8299 "Gross business or
professional income: Line 8000 plus amount 3O" "professional income on line 13699": the gross of
the statements whose line code is professional, totalled over them, signed."""

GROSS_COMMISSION_INCOME = CATALOG.declare("gross_commission_income", Decimal)
"""Gross commission income, T1 line 13899 "Gross", Form T2125 line 8299 "Gross business or
professional income: Line 8000 plus amount 3O" "commission income on line 13899": the gross of the
statements whose line code is commission, totalled over them, signed."""

BUSINESS_LINE_IS_BUSINESS = CATALOG.declare("business_line_is_business", int, non_negative=True)
"""Business line flag, Form T2125 line 9946 "business income on line 13500": 1 when the statement's
line code (`business_income_line`) is 1, else 0, from `ca/t2125_line_is_business`."""

BUSINESS_LINE_IS_PROFESSIONAL = CATALOG.declare(
    "business_line_is_professional", int, non_negative=True
)
"""Professional line flag, Form T2125 line 9946 "professional income on line 13700": 1 when the
statement's line code (`business_income_line`) is 2, else 0, from
`ca/t2125_line_is_professional`."""

BUSINESS_LINE_IS_COMMISSION = CATALOG.declare("business_line_is_commission", int, non_negative=True)
"""Commission line flag, Form T2125 line 9946 "commission income on line 13900": 1 when the
statement's line code (`business_income_line`) is 3, else 0, from `ca/t2125_line_is_commission`."""

NET_ON_BUSINESS_LINE = CATALOG.declare("net_on_business_line", Decimal)
"""Net on the business line, Form T2125 line 9946 "Report the net income amount from line 9946 on
the applicable line ... business income on line 13500": the statement's line 9946 when its code is
business, else 0, signed."""

NET_ON_PROFESSIONAL_LINE = CATALOG.declare("net_on_professional_line", Decimal)
"""Net on the professional line, Form T2125 line 9946 "professional income on line 13700": the
statement's line 9946 when its code is professional, else 0, signed."""

NET_ON_COMMISSION_LINE = CATALOG.declare("net_on_commission_line", Decimal)
"""Net on the commission line, Form T2125 line 9946 "commission income on line 13900": the
statement's line 9946 when its code is commission, else 0, signed."""

GROSS_ON_BUSINESS_LINE = CATALOG.declare("gross_on_business_line", Decimal)
"""Gross on the business line, Form T2125 line 8299 "Gross business or professional income" on
line 13499: the statement's line 8299 when its code is business, else 0, signed."""

GROSS_ON_PROFESSIONAL_LINE = CATALOG.declare("gross_on_professional_line", Decimal)
"""Gross on the professional line, Form T2125 line 8299 on line 13699: the statement's line 8299
when its code is professional, else 0, signed."""

GROSS_ON_COMMISSION_LINE = CATALOG.declare("gross_on_commission_line", Decimal)
"""Gross on the commission line, Form T2125 line 8299 on line 13899: the statement's line 8299 when
its code is commission, else 0, signed."""

BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS = CATALOG.declare(
    "business_net_income_before_adjustments", Decimal
)
"""Business net income before adjustments, Form T2125 line 9369 "Net income (loss) before
adjustments: Amount 4A minus line 9368": amount 4A less line 9368, signed, a loss is negative."""

BUSINESS_SHARE_OF_NET_INCOME = CATALOG.declare("business_share_of_net_income", Decimal)
"""Filer's share of the business net income, Form T2125 amount 5A "Your share of line 9369 or the
amount from your T5013 slip, Statement of Partnership Income": line 9369, or for a partner the T5013
amount; signed."""

BUSINESS_PARTNERSHIP_TOTAL = CATALOG.declare("business_partnership_total", Decimal)
"""Business net income with the partner's credits, Form T2125 amount 5C "Total: Amount 5A plus
amount 5B plus line 9974": amounts 5A and 5B plus line 9974, signed."""

BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS = CATALOG.declare(
    "business_net_income_after_adjustments", Decimal
)
"""Business net income after adjustments, Form T2125 amount 5D "Net income (loss) after adjustments:
Amount 5C minus line 9943": amount 5C less line 9943, signed, a loss is negative."""

BUSINESS_CLOSING_UCC = RecordListKind.declare(
    CATALOG, "business_closing_ucc", fields=(CCA_CLASS_NUMBER, CCA_UCC_AT_END)
)
"""Business closing UCC, Form T2125 Area A "UCC at the end of the year (col. 7 minus col. 21)": one
record for each class of the business classes, holding its class number and column 22."""

BUSINESS_IMMEDIATE_EXPENSING_CAP = CATALOG.declare(
    "business_immediate_expensing_cap", Decimal, non_negative=True
)
"""Immediate expensing limit when not associated, Form T2125 Area A endnote 5 "$1.5 million, if you
are not associated with any other eligible person or partnership (EPOP) in the tax year" and Area G
"Immediate expensing limit allocated to your business: Multiply $1.5 million by the percentage
assigned to your business in column 3**": the printed $1.5 million, from a dataset."""

BUSINESS_EPOP_PERCENTAGE_MAXIMUM = CATALOG.declare(
    "business_epop_percentage_maximum", Decimal, non_negative=True
)
"""Largest total of the percentages assigned, Form T2125 Area G "The total of all percentages
assigned under the agreement should not be more than 100%" and "** If the total of column 3 is
more than 100%, enter "0."": the printed 100%, from a dataset, as the form prints a percentage
(100 for 100%)."""

BUSINESS_IMMEDIATE_EXPENSING_SHARE = CATALOG.declare(
    "business_immediate_expensing_share", Decimal, non_negative=True
)
"""Immediate expensing limit times the percentage, the first step of Form T2125 Area G "Immediate
expensing limit allocated to your business: Multiply $1.5 million by the percentage assigned to
your business in column 3**": $1.5 million times the percentage assigned to your business."""

BUSINESS_EPOP_PERCENTAGE_ROOM = CATALOG.declare("business_epop_percentage_room", Decimal)
"""Room under 100% in the percentages assigned, the test of Form T2125 Area G "** If the total of
column 3 is more than 100%, enter "0."": 100 less the total of column 3, signed, negative when the
total is more than 100%."""

BUSINESS_IMMEDIATE_EXPENSING_ALLOCATED = CATALOG.declare(
    "business_immediate_expensing_allocated", Decimal, non_negative=True
)
"""Immediate expensing limit allocated to the business, Form T2125 Area G "Immediate expensing
limit allocated to your business: Multiply $1.5 million by the percentage assigned to your
business in column 3**" and "** If the total of column 3 is more than 100%, enter "0."": the
multiple, or 0 when the total of column 3 is more than 100%."""

BUSINESS_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT = CATALOG.declare(
    "business_immediate_expensing_associated_limit", Decimal, non_negative=True
)
"""Immediate expensing limit when associated with an EPOP, Form T2125 Area A endnote 5 "amount iii
of Area G, if you are associated with one or more EPOPs in the tax year" and "zero, if you are
associated with one or more EPOPs and an agreement that assigns a percentage to one or more of the
associated EPOPs was not filed with the minister in a prescribed form": amount iii, or 0 when no
agreement was filed."""

BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER = CATALOG.declare(
    "business_immediate_expensing_limit_before_minister", Decimal, non_negative=True
)
"""Immediate expensing limit before any amount allocated by the minister, Form T2125 Area A
endnote 5 "the immediate expensing limit, which is equal to one of the following, whichever is
applicable": $1.5 million when not associated with an EPOP, else the limit when associated."""

BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION = CATALOG.declare(
    "business_immediate_expensing_limit_before_proration", Decimal, non_negative=True
)
"""Immediate expensing limit before the days of the fiscal period scale it, Income Tax
Regulations 1104(3.5)(b): "where an eligible person or partnership has a taxation year that is
less than 51 weeks, its immediate expensing limit for the year is that proportion of its
immediate expensing limit for the year determined without reference to this paragraph that the
number of days in the year is of 365". Form T2125 Area A endnote 5 "the immediate expensing
limit, which is equal to one of the following, whichever is applicable", and "any amount
allocated by the minister under subsection 1104(3.4) of the Regulations": the limit before any
amount allocated by the minister, or that amount when there is one, unscaled. Guide T4002,
"Immediate expensing incentive": "The limit is also prorated for tax years shorter than 365
days"."""

BUSINESS_IMMEDIATE_EXPENSING_LIMIT = CATALOG.declare(
    "business_immediate_expensing_limit", Decimal, non_negative=True
)
"""Immediate expensing limit, Form T2125 Area A endnote 5 "the immediate expensing limit, which is
equal to one of the following, whichever is applicable", including "any amount allocated by the
minister under subsection 1104(3.4) of the Regulations": the limit above, or the amount allocated
by the minister when there is one."""

BUSINESS_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED = CATALOG.declare(
    "business_immediate_expensing_limit_unprorated", Decimal, non_negative=True
)
"""Immediate expensing limit before the days scaling, Form T2125 Area A endnote 5 "the immediate
expensing limit, which is equal to one of the following, whichever is applicable", and Guide T4002:
"The limit is also prorated for tax years shorter than 365 days": the per-person limit before the
limit is scaled to the days of the fiscal period, the minister's amount as entered."""

BUSINESS_IMMEDIATE_EXPENSING_CLAIM = CATALOG.declare(
    "business_immediate_expensing_claim", Decimal, non_negative=True
)
"""Total immediate expensing claim for the year, Form T2125 Area A "Total immediate expensing claim
for the year: Total of column 9" (line i), limited by endnote 5 to "the lesser of" the immediate
expensing limit, "the UCC of DIEPs in column 8" and "the amount of income, if any, earned from the
source of income that is a business (before any CCA deductions)": the total of column 9 over the
classes."""

BUSINESS_INCOME_BEFORE_CCA = CATALOG.declare(
    "business_income_before_cca", Decimal, non_negative=True
)
"""Business income before CCA, Form T2125 Area A endnote 5 "the amount of income, if any, earned
from the source of income that is a business (before any CCA deductions) in which the relevant
DIEP is used for the tax year": line 9369 "Net income (loss) before adjustments" plus line 9936,
the CCA it deducted, not below zero."""

BUSINESS_FISCAL_PERIOD_DAYS = CATALOG.declare("business_fiscal_period_days", int, non_negative=True)
"""Days of the fiscal period of Form T2125 that the CCA claim and closing UCC are prorated by:
the days entered when above 0, else the days in a full year.
Guide T4002 2025, "You were asking?": "Since your fiscal period is less than 365 days,
you have to prorate your CCA claim. ... base your CCA claim on the number of days in your
fiscal period compared to 365 days. In this case, your fiscal period is 214 days"
(the Guide's example)."""

FARM_WHEAT = CATALOG.declare("farm_wheat", Decimal, non_negative=True)
"""Wheat income, Form T2042 line 9371 "Wheat": a starting amount."""

FARM_OATS = CATALOG.declare("farm_oats", Decimal, non_negative=True)
"""Oats income, Form T2042 line 9372 "Oats": a starting amount."""

FARM_BARLEY = CATALOG.declare("farm_barley", Decimal, non_negative=True)
"""Barley income, Form T2042 line 9373 "Barley": a starting amount."""

FARM_MIXED_GRAINS = CATALOG.declare("farm_mixed_grains", Decimal, non_negative=True)
"""Mixed grains income, Form T2042 line 9374 "Mixed grains": a starting amount."""

FARM_CORN = CATALOG.declare("farm_corn", Decimal, non_negative=True)
"""Corn income, Form T2042 line 9375 "Corn.": a starting amount."""

FARM_CANOLA = CATALOG.declare("farm_canola", Decimal, non_negative=True)
"""Canola income, Form T2042 line 9376 "Canola": a starting amount."""

FARM_FLAXSEED = CATALOG.declare("farm_flaxseed", Decimal, non_negative=True)
"""Flaxseed income, Form T2042 line 9377 "Flaxseed": a starting amount."""

FARM_SOYBEANS = CATALOG.declare("farm_soybeans", Decimal, non_negative=True)
"""Soybeans income, Form T2042 line 9378 "Soybeans.": a starting amount."""

FARM_GRAINS_AND_OILSEEDS = CATALOG.declare("farm_grains_and_oilseeds", Decimal, non_negative=True)
"""Grains and oilseeds income, Form T2042 line 9370 "Grains and oilseeds": a starting amount."""

FARM_FRUIT = CATALOG.declare("farm_fruit", Decimal, non_negative=True)
"""Fruit income, Form T2042 line 9421 "Fruit": a starting amount."""

FARM_POTATOES = CATALOG.declare("farm_potatoes", Decimal, non_negative=True)
"""Potato income, Form T2042 line 9422 "Potatoes": a starting amount."""

FARM_VEGETABLES = CATALOG.declare("farm_vegetables", Decimal, non_negative=True)
"""Vegetable income, Form T2042 line 9423 "Vegetables (not including potatoes).": a starting
amount."""

FARM_TOBACCO = CATALOG.declare("farm_tobacco", Decimal, non_negative=True)
"""Tobacco income, Form T2042 line 9424 "Tobacco": a starting amount."""

FARM_GREENHOUSE_AND_NURSERY = CATALOG.declare(
    "farm_greenhouse_and_nursery", Decimal, non_negative=True
)
"""Greenhouse and nursery income, Form T2042 line 9425 "Greenhouse and nursery products.": a
starting amount."""

FARM_FORAGE_CROPS_OR_SEEDS = CATALOG.declare(
    "farm_forage_crops_or_seeds", Decimal, non_negative=True
)
"""Forage crops or seeds income, Form T2042 line 9426 "Forage crops or seeds": a starting amount."""

FARM_OTHER_CROPS = CATALOG.declare("farm_other_crops", Decimal, non_negative=True)
"""Other crops income, Form T2042 line 9420 "Other crops": a starting amount."""

FARM_CATTLE = CATALOG.declare("farm_cattle", Decimal, non_negative=True)
"""Cattle income, Form T2042 line 9471 "Cattle": a starting amount."""

FARM_SWINE = CATALOG.declare("farm_swine", Decimal, non_negative=True)
"""Swine income, Form T2042 line 9472 "Swine": a starting amount."""

FARM_POULTRY = CATALOG.declare("farm_poultry", Decimal, non_negative=True)
"""Poultry income, Form T2042 line 9473 "Poultry": a starting amount."""

FARM_SHEEP_AND_LAMBS = CATALOG.declare("farm_sheep_and_lambs", Decimal, non_negative=True)
"""Sheep and lambs income, Form T2042 line 9474 "Sheep and lambs": a starting amount."""

FARM_LIVESTOCK_AND_ANIMAL_PRODUCTS_REVENUE = CATALOG.declare(
    "farm_livestock_and_animal_products_revenue", Decimal, non_negative=True
)
"""Livestock and animal products revenue income, Form T2042 line 9470 "Livestock and animal
products revenue": a starting amount."""

FARM_MILK_AND_CREAM = CATALOG.declare("farm_milk_and_cream", Decimal, non_negative=True)
"""Milk and cream income, Form T2042 line 9476 "Milk and cream (not including dairy subsidies).": a
starting amount."""

FARM_EGGS = CATALOG.declare("farm_eggs", Decimal, non_negative=True)
"""Eggs income, Form T2042 line 9477 "Eggs for consumption": a starting amount."""

FARM_OTHER_COMMODITIES = CATALOG.declare("farm_other_commodities", Decimal, non_negative=True)
"""Other commodities income, Form T2042 line 9520 "Other commodities.": a starting amount."""

FARM_DAIRY_SUBSIDIES = CATALOG.declare("farm_dairy_subsidies", Decimal, non_negative=True)
"""Dairy subsidies income, Form T2042 line 9541 "Dairy subsidies": a starting amount."""

FARM_CROP_INSURANCE = CATALOG.declare("farm_crop_insurance", Decimal, non_negative=True)
"""Crop insurance income, Form T2042 line 9542 "Crop insurance": a starting amount."""

FARM_OTHER_PROGRAM_PAYMENTS = CATALOG.declare(
    "farm_other_program_payments", Decimal, non_negative=True
)
"""Other program payments, Form T2042 line 9540 "Other program payments": a starting amount."""

FARM_REBATES = CATALOG.declare("farm_rebates", Decimal, non_negative=True)
"""Rebates income, Form T2042 line 9570 "Rebates": a starting amount."""

FARM_CUSTOM_WORK = CATALOG.declare("farm_custom_work", Decimal, non_negative=True)
"""Custom work income, Form T2042 line 9601 "Custom or contract work (includes machine rentals).":
a starting amount."""

FARM_INSURANCE_PROCEEDS = CATALOG.declare("farm_insurance_proceeds", Decimal, non_negative=True)
"""Insurance proceeds income, Form T2042 line 9604 "Insurance proceeds": a starting amount."""

FARM_PATRONAGE_DIVIDENDS = CATALOG.declare("farm_patronage_dividends", Decimal, non_negative=True)
"""Patronage dividends income, Form T2042 line 9605 "Patronage dividends": a starting amount."""

FARM_OTHER_INCOME = CATALOG.declare("farm_other_income", Decimal, non_negative=True)
"""Other farming income, Form T2042 line 9600 "Other income (specify):": a starting amount, before
the recapture of Area A."""

FARM_CONTAINERS_AND_TWINE = CATALOG.declare("farm_containers_and_twine", Decimal, non_negative=True)
"""Containers and twine of the farming business, Form T2042 line 9661 "Containers and twine": a
starting amount."""

FARM_FERTILIZERS_AND_LIME = CATALOG.declare("farm_fertilizers_and_lime", Decimal, non_negative=True)
"""Fertilizers and lime of the farming business, Form T2042 line 9662 "Fertilizers and lime": a
starting amount."""

FARM_PESTICIDES = CATALOG.declare("farm_pesticides", Decimal, non_negative=True)
"""Pesticides of the farming business, Form T2042 line 9663 "Pesticides (herbicides, insecticides,
fungicides)": a starting amount."""

FARM_SEEDS_AND_PLANTS = CATALOG.declare("farm_seeds_and_plants", Decimal, non_negative=True)
"""Seeds and plants of the farming business, Form T2042 line 9664 "Seeds and plants": a starting
amount."""

FARM_FEED_SUPPLEMENTS_STRAW_AND_BEDDING = CATALOG.declare(
    "farm_feed_supplements_straw_and_bedding", Decimal, non_negative=True
)
"""Feed, supplements, straw and bedding of the farming business, Form T2042 line 9711 "Feed,
supplements, straw, and bedding": a starting amount."""

FARM_LIVESTOCK_PURCHASED = CATALOG.declare("farm_livestock_purchased", Decimal, non_negative=True)
"""Livestock purchased of the farming business, Form T2042 line 9712 "Livestock purchased": a
starting amount."""

FARM_VETERINARY_FEES = CATALOG.declare("farm_veterinary_fees", Decimal, non_negative=True)
"""Veterinary fees of the farming business, Form T2042 line 9713 "Veterinary fees, medicine, and
breeding fees": a starting amount."""

FARM_MACHINERY_REPAIRS_LICENCES_AND_INSURANCE = CATALOG.declare(
    "farm_machinery_repairs_licences_and_insurance", Decimal, non_negative=True
)
"""Machinery repairs, licences and insurance of the farming business, Form T2042 line 9760
"Repairs, licences, and insurance": a starting amount."""

FARM_GASOLINE_DIESEL_AND_OIL = CATALOG.declare(
    "farm_gasoline_diesel_and_oil", Decimal, non_negative=True
)
"""Gasoline, diesel fuel and oil of the farming business, Form T2042 line 9764 "Gasoline, diesel
fuel, and oil": a starting amount."""

FARM_BUILDING_REPAIRS_AND_MAINTENANCE = CATALOG.declare(
    "farm_building_repairs_and_maintenance", Decimal, non_negative=True
)
"""Building repairs and maintenance of the farming business, Form T2042 line 9795 "Building repairs
and maintenance (includes fence repairs)": a starting amount."""

FARM_CLEARING_LEVELLING_AND_DRAINING = CATALOG.declare(
    "farm_clearing_levelling_and_draining", Decimal, non_negative=True
)
"""Clearing, levelling and draining of the farming business, Form T2042 line 9796 "Clearing,
levelling, and draining land": a starting amount."""

FARM_CROP_INSURANCE_PREMIUMS = CATALOG.declare(
    "farm_crop_insurance_premiums", Decimal, non_negative=True
)
"""Crop insurance premiums of the farming business, Form T2042 line 9797 "Crop insurance, Revenue
Protection Program, and stabilization premiums": a starting amount."""

FARM_CUSTOM_WORK_EXPENSES = CATALOG.declare("farm_custom_work_expenses", Decimal, non_negative=True)
"""Custom work of the farming business, Form T2042 line 9798 "Custom or contract work (includes
machine rentals).": a starting amount."""

FARM_ELECTRICITY = CATALOG.declare("farm_electricity", Decimal, non_negative=True)
"""Electricity of the farming business, Form T2042 line 9799 "Electricity.": a starting amount."""

FARM_HEATING_AND_CURING_FUEL = CATALOG.declare(
    "farm_heating_and_curing_fuel", Decimal, non_negative=True
)
"""Heating and curing fuel of the farming business, Form T2042 line 9802 "Heating fuel and curing
fuel.": a starting amount."""

FARM_INSURANCE_PROGRAM_OVERPAYMENT_RECAPTURE = CATALOG.declare(
    "farm_insurance_program_overpayment_recapture", Decimal, non_negative=True
)
"""Insurance program overpayment recapture of the farming business, Form T2042 line 9803 "Insurance
program overpayment recapture": a starting amount."""

FARM_INSURANCE = CATALOG.declare("farm_insurance", Decimal, non_negative=True)
"""Insurance of the farming business, Form T2042 line 9804 "Insurance.": a starting amount."""

FARM_INTEREST_AND_BANK_CHARGES = CATALOG.declare(
    "farm_interest_and_bank_charges", Decimal, non_negative=True
)
"""Interest and bank charges of the farming business, Form T2042 line 9805 "Interest and bank
charges.": a starting amount."""

FARM_OFFICE_EXPENSES = CATALOG.declare("farm_office_expenses", Decimal, non_negative=True)
"""Office expenses of the farming business, Form T2042 line 9808 "Office expenses": a starting
amount."""

FARM_PROFESSIONAL_FEES = CATALOG.declare("farm_professional_fees", Decimal, non_negative=True)
"""Professional fees of the farming business, Form T2042 line 9809 "Professional fees (includes
legal and accounting fees).": a starting amount."""

FARM_PROPERTY_TAXES = CATALOG.declare("farm_property_taxes", Decimal, non_negative=True)
"""Property taxes of the farming business, Form T2042 line 9810 "Property taxes": a starting
amount."""

FARM_RENT = CATALOG.declare("farm_rent", Decimal, non_negative=True)
"""Rent of the farming business, Form T2042 line 9811 "Rent (land, buildings, and pasture)": a
starting amount."""

FARM_SALARIES_WAGES_AND_BENEFITS = CATALOG.declare(
    "farm_salaries_wages_and_benefits", Decimal, non_negative=True
)
"""Salaries, wages and benefits of the farming business, Form T2042 line 9814 "Salaries, wages, and
benefits (including employer's contributions).": a starting amount."""

FARM_MOTOR_VEHICLE_EXPENSES = CATALOG.declare(
    "farm_motor_vehicle_expenses", Decimal, non_negative=True
)
"""Motor vehicle expenses of the farming business, Form T2042 line 9819 "Motor vehicle expenses
(not including CCA) (amount 16 of Chart A)": amount 16 of Chart A, "Allowable motor vehicle
expenses: Add amounts 13 to 15 (enter this total on line 9819 of Part 4)"."""

FARM_VEHICLE_SALES_TAX_RATE = CATALOG.declare(
    "farm_vehicle_sales_tax_rate", Decimal, non_negative=True
)
"""GST plus PST, or HST, rate, Form T2042 Chart C "Use a GST rate of 5% or HST rate applicable to
your province.": the rate in percent, so 13 is 13% (5 plus 8 in a province with a PST of 8%, 5 where
only the GST applies), a starting amount."""

FARM_SMALL_TOOLS = CATALOG.declare("farm_small_tools", Decimal, non_negative=True)
"""Small tools of the farming business, Form T2042 line 9820 "Small tools": a starting amount."""

FARM_MANDATORY_INVENTORY_ADJUSTMENT_PREVIOUS_YEAR = CATALOG.declare(
    "farm_mandatory_inventory_adjustment_previous_year", Decimal, non_negative=True
)
"""Mandatory inventory adjustment for the previous year of the farming business, Form T2042 line
9937 "Mandatory inventory adjustment included in the previous year": a starting amount."""

FARM_OPTIONAL_INVENTORY_ADJUSTMENT_PREVIOUS_YEAR = CATALOG.declare(
    "farm_optional_inventory_adjustment_previous_year", Decimal, non_negative=True
)
"""Optional inventory adjustment for the previous year of the farming business, Form T2042 line
9938 "Optional inventory adjustment included in the previous year": a starting amount."""

FARM_OTHER_EXPENSES = CATALOG.declare("farm_other_expenses", Decimal, non_negative=True)
"""Other farming expenses, Form T2042 line 9790 "Other expenses (specify):": a starting amount,
before the terminal loss of Area A."""

FARM_RECAPTURED_CCA = CATALOG.declare("farm_recaptured_cca", Decimal, non_negative=True)
"""Recapture of the farming classes, Form T2042 Area A endnote 3 "If you have a negative amount in
column 7, add it to income as a recapture in Part 3 on line 9600": the recapture of each class
of the Area A list, totalled."""

FARM_OTHER_INCOME_WITH_RECAPTURE = CATALOG.declare(
    "farm_other_income_with_recapture", Decimal, non_negative=True
)
"""Other farming income with the recapture, Form T2042 line 9600 "Other income (specify):": the
other income plus the recapture of Area A."""

FARM_GROSS_INCOME = CATALOG.declare("farm_gross_income", Decimal, non_negative=True)
"""Gross farming income, Form T2042 line 9659 "Gross income: Total of the income lines (enter this
amount on line 14099 of your income tax and benefit return)": the income lines of Part 3, with
line 9600 and its recapture."""

FARM_GROSS_INCOME_BEFORE_EXPENSES = CATALOG.declare(
    "farm_gross_income_before_expenses", Decimal, non_negative=True
)
"""Gross farming income before expenses, Form T2042 amount 4A "Gross income (line 9659 of Part 3)":
line 9659."""

FARM_TERMINAL_LOSS = CATALOG.declare("farm_terminal_loss", Decimal, non_negative=True)
"""Terminal loss of the farming classes, Form T2042 Area A endnote 3 "If no property is left in the
class and there is a positive amount in this column, deduct the amount from income as a terminal
loss in Part 4 on line 9790": the terminal loss of each class of the Area A list, totalled."""

FARM_OTHER_EXPENSES_WITH_TERMINAL_LOSS = CATALOG.declare(
    "farm_other_expenses_with_terminal_loss", Decimal, non_negative=True
)
"""Other farming expenses with the terminal loss, Form T2042 line 9790 "Total other expenses (see
column 7 of Area A on page 5)": the other expenses plus the terminal loss of Area A."""

FARM_EXPENSES_SUBTOTAL = CATALOG.declare("farm_expenses_subtotal", Decimal, non_negative=True)
"""Subtotal of farming expenses, Form T2042 amount 4B "Subtotal of expenses": the expense lines
9661 to 9820, the inventory adjustments of the previous year and line 9790, added."""

FARM_CCA_TABLE_CLAIM = CATALOG.declare("farm_cca_table_claim", Decimal, non_negative=True)
"""CCA claim of the farming classes, Form T2042 Area A amount ii "Total CCA claim for the year:
Total of column 21 (enter on line 9936 of Part 4 amount ii minus any personal part and any CCA
for business-use-of-home expenses)": the CCA claimed on each class, at most its maximum,
totalled."""

FARM_CCA_PERSONAL_PART = CATALOG.declare("farm_cca_personal_part", Decimal, non_negative=True)
"""Personal part of the farming CCA, Form T2042 line 9936 "Capital cost allowance (CCA). Enter
amount ii of Area A minus any personal part and any CCA for business-use-of-home expenses": a
starting amount, the personal part."""

FARM_CCA_CLAIM_LESS_PERSONAL_PART = CATALOG.declare("farm_cca_claim_less_personal_part", Decimal)
"""Farming CCA claim less the personal part, Form T2042 line 9936 "Capital cost allowance (CCA).
Enter amount ii of Area A minus any personal part and any CCA for business-use-of-home
expenses": the first step: amount ii less the personal part of CCA."""

FARM_CCA_CLAIM = CATALOG.declare("farm_cca_claim", Decimal)
"""CCA claim of the farming business, Form T2042 line 9936 "Capital cost allowance (CCA). Enter
amount ii of Area A minus any personal part and any CCA for business-use-of-home expenses": the
second step: the first step less the CCA for business-use-of-home expenses (amount 7K)."""

FARM_TOTAL_EXPENSES = CATALOG.declare("farm_total_expenses", Decimal)
"""Total farming expenses, Form T2042 line 9898 "Total farm expenses: Amount 4B plus line 9936":
amount 4B plus line 9936."""

FARM_NET_INCOME_BEFORE_ADJUSTMENTS = CATALOG.declare("farm_net_income_before_adjustments", Decimal)
"""Farming net income before inventory adjustments, Form T2042 line 9899 "Net income (loss) before
inventory adjustments: Amount 4A minus line 9898": amount 4A less line 9898, signed, a loss is
negative."""

FARM_OPTIONAL_INVENTORY_ADJUSTMENT_CURRENT_YEAR = CATALOG.declare(
    "farm_optional_inventory_adjustment_current_year", Decimal, non_negative=True
)
"""Optional inventory adjustment for the current year, Form T2042 line 9941 "Optional inventory
adjustment included in the current year": a starting amount."""

FARM_MANDATORY_INVENTORY_ADJUSTMENT_CURRENT_YEAR = CATALOG.declare(
    "farm_mandatory_inventory_adjustment_current_year", Decimal, non_negative=True
)
"""Mandatory inventory adjustment for the current year, Form T2042 line 9942 "Mandatory inventory
adjustment included in the current year": a starting amount."""

FARM_NET_INCOME_AFTER_INVENTORY_ADJUSTMENTS = CATALOG.declare(
    "farm_net_income_after_inventory_adjustments", Decimal
)
"""Farming net income after inventory adjustments, Form T2042 amount 4C "Net income (loss) after
inventory adjustments: Total of lines 9899, 9941, and 9942": the three added, signed, a loss is
negative."""

FARM_PARTNER_SHARE = CATALOG.declare("farm_partner_share", Decimal)
"""Partner's share of the farming net income, Form T2042 amount 5A "Your share of amount 4C or the
amount from your T5013 slip, Statement of Partnership Income": a starting amount, signed."""

FARM_PARTNER = CATALOG.declare("farm_partner", int, non_negative=True)
"""Whether the filer is a partner in the farm, Form T2042 amount 5A "Your share of amount 4C or the
amount from your T5013 slip, Statement of Partnership Income": 1 for a partner, 0 otherwise, a
starting count."""

FARM_PARTNER_CHECKED = CATALOG.declare("farm_partner_checked", int, non_negative=True)
"""Whether the filer is a partner in the farm, Form T2042 amount 5A "Your share of amount 4C or the
amount from your T5013 slip, Statement of Partnership Income": the answer of `ca/farm_partner`
after the check that it is 0 or 1 (`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more
is refused, not capped."""

FARM_SHARE_OF_NET_INCOME = CATALOG.declare("farm_share_of_net_income", Decimal)
"""Filer's share of the farming net income, Form T2042 amount 5A "Your share of amount 4C or the
amount from your T5013 slip, Statement of Partnership Income": amount 4C, or for a partner the
T5013 amount; signed."""

FARM_FUEL_CHARGE_CREDIT = CATALOG.declare("farm_fuel_charge_credit", Decimal, non_negative=True)
"""Fuel charge proceeds to farmers tax credit, Form T2042 line 9951 "Return of fuel charge proceeds
to farmers tax credit allocated to you in the year (amount 5C of Form T2043, Return of Fuel
Charge Proceeds to Farmers Tax Credit)": a starting amount."""

FARM_PARTNER_GST_HST_REBATE = CATALOG.declare("farm_partner_gst_hst_rebate", Decimal)
"""GST/HST rebate of the partner, Form T2042 line 9974 "GST/HST rebate for partners received in the
year": a starting amount."""

FARM_PARTNERSHIP_TOTAL = CATALOG.declare("farm_partnership_total", Decimal)
"""Farming net income with the partner's credits, Form T2042 amount 5B "Total: Amount 5A plus line
9951 plus line 9974": amount 5A plus line 9951 and line 9974, signed."""

FARM_PARTNER_OTHER_AMOUNT_A = CATALOG.declare(
    "farm_partner_other_amount_a", Decimal, non_negative=True
)
"""Partner expense 1, Form T2042 amount 6A "List details of expenses: Expense amounts": a starting
amount among the five lines of Part 6."""

FARM_PARTNER_OTHER_AMOUNT_B = CATALOG.declare(
    "farm_partner_other_amount_b", Decimal, non_negative=True
)
"""Partner expense 2, Form T2042 amount 6B "List details of expenses: Expense amounts": a starting
amount among the five lines of Part 6."""

FARM_PARTNER_OTHER_AMOUNT_C = CATALOG.declare(
    "farm_partner_other_amount_c", Decimal, non_negative=True
)
"""Partner expense 3, Form T2042 amount 6C "List details of expenses: Expense amounts": a starting
amount among the five lines of Part 6."""

FARM_PARTNER_OTHER_AMOUNT_D = CATALOG.declare(
    "farm_partner_other_amount_d", Decimal, non_negative=True
)
"""Partner expense 4, Form T2042 amount 6D "List details of expenses: Expense amounts": a starting
amount among the five lines of Part 6."""

FARM_PARTNER_OTHER_AMOUNT_E = CATALOG.declare(
    "farm_partner_other_amount_e", Decimal, non_negative=True
)
"""Partner expense 5, Form T2042 amount 6E "List details of expenses: Expense amounts": a starting
amount among the five lines of Part 6."""

FARM_PARTNER_OTHER_AMOUNTS_TOTAL = CATALOG.declare(
    "farm_partner_other_amounts_total", Decimal, non_negative=True
)
"""Total of the partner's other amounts, Form T2042 amount 6F "Total other amounts deductible from
your share of the net partnership income (loss): Add amounts 6A to 6E": amounts 6A to 6E added."""

FARM_PARTNER_OTHER_AMOUNTS = CATALOG.declare(
    "farm_partner_other_amounts", Decimal, non_negative=True
)
"""Partner's other amounts deductible, Form T2042 line 9943 "Other amounts deductible from your
share of net partnership income (loss) (amount 6F)": amount 6F."""

FARM_NET_INCOME_AFTER_ADJUSTMENTS = CATALOG.declare("farm_net_income_after_adjustments", Decimal)
"""Farming net income after adjustments, Form T2042 amount 5C "Net income (loss) after adjustments:
Amount 5B minus line 9943": amount 5B less line 9943, signed, a loss is negative."""

FARM_HOME_HEAT = CATALOG.declare("farm_home_heat", Decimal, non_negative=True)
"""Heat for the business use of the home, Form T2042 amount 7A "Heat": a starting amount."""

FARM_HOME_ELECTRICITY = CATALOG.declare("farm_home_electricity", Decimal, non_negative=True)
"""Electricity for the business use of the home, Form T2042 amount 7B "Electricity": a starting
amount."""

FARM_HOME_INSURANCE = CATALOG.declare("farm_home_insurance", Decimal, non_negative=True)
"""Insurance for the business use of the home, Form T2042 amount 7C "Insurance": a starting
amount."""

FARM_HOME_MAINTENANCE = CATALOG.declare("farm_home_maintenance", Decimal, non_negative=True)
"""Maintenance for the business use of the home, Form T2042 amount 7D "Maintenance": a starting
amount."""

FARM_HOME_MORTGAGE_INTEREST = CATALOG.declare(
    "farm_home_mortgage_interest", Decimal, non_negative=True
)
"""Mortgage interest for the business use of the home, Form T2042 amount 7E "Mortgage interest": a
starting amount."""

FARM_HOME_PROPERTY_TAXES = CATALOG.declare("farm_home_property_taxes", Decimal, non_negative=True)
"""Property taxes for the business use of the home, Form T2042 amount 7F "Property taxes": a
starting amount."""

FARM_HOME_OTHER_EXPENSES = CATALOG.declare("farm_home_other_expenses", Decimal, non_negative=True)
"""Other expenses for the business use of the home, Form T2042 amount 7G "Other expenses
(specify)": a starting amount."""

FARM_HOME_EXPENSES_SUBTOTAL = CATALOG.declare(
    "farm_home_expenses_subtotal", Decimal, non_negative=True
)
"""Home expenses subtotal, Form T2042 amount 7H "Subtotal: Add amounts 7A to 7G.": amounts 7A to 7G
added."""

FARM_HOME_PERSONAL_USE_PART = CATALOG.declare(
    "farm_home_personal_use_part", Decimal, non_negative=True
)
"""Personal-use part of the home expenses, Form T2042 amount 7I "Personal-use part of the
business-use-of-home expenses": a starting amount."""

FARM_HOME_EXPENSES_BUSINESS_PART = CATALOG.declare("farm_home_expenses_business_part", Decimal)
"""Business part of the home expenses, Form T2042 amount 7J "Subtotal: Amount 7H minus amount 7I":
amount 7H less amount 7I."""

FARM_HOME_CCA = CATALOG.declare("farm_home_cca", Decimal, non_negative=True)
"""CCA for the business use of the home, Form T2042 amount 7K "Capital cost allowance (business
part only), which means amount ii of Area A minus any portion of capital cost allowance that is
for personal use or entered on line 9936 of Part 4": a starting amount."""

FARM_HOME_CARRIED_FORWARD = CATALOG.declare("farm_home_carried_forward", Decimal, non_negative=True)
"""Home expenses carried forward from last year, Form T2042 amount 7L "Amount carried forward from
previous year": a starting amount."""

FARM_HOME_EXPENSES_AVAILABLE = CATALOG.declare("farm_home_expenses_available", Decimal)
"""Home expenses available, Form T2042 amount 7M "Subtotal: Add amounts 7J to 7L.": amounts 7J to
7L added."""

FARM_HOME_INCOME_LIMIT = CATALOG.declare("farm_home_income_limit", Decimal, non_negative=True)
"""Net income limit on the home expenses, Form T2042 amount 7N "Net income (loss) after adjustments
(amount 5C) (if negative, enter "0")": amount 5C, or 0 when it is negative."""

FARM_HOME_CARRY_FORWARD = CATALOG.declare("farm_home_carry_forward", Decimal, non_negative=True)
"""Home expenses to carry forward, Form T2042 amount 7O "Business-use-of-home expenses available to
carry forward: Amount 7M minus amount 7N (if negative, enter "0")": amount 7M less amount 7N, or
0 when it is negative."""

FARM_HOME_ALLOWABLE_CLAIM = CATALOG.declare("farm_home_allowable_claim", Decimal)
"""Allowable home expenses claim, Form T2042 amount 7P "Allowable claim: Amount 7M or 7N above,
whichever is less (enter your share of this amount on line 9945 of Part 5)": the lesser of
amounts 7M and 7N."""

FARM_HOME_EXPENSES = CATALOG.declare("farm_home_expenses", Decimal)
"""Farming business-use-of-home expenses, Form T2042 line 9945 "Business-use-of-home expenses
(amount 7P)": amount 7P."""

FARM_CCA_CLASSES = RecordListKind.declare(
    CATALOG,
    "farm_cca_classes",
    fields=(
        CCA_CLASS_NUMBER,
        CCA_UCC_AT_START,
        CCA_ADDITIONS,
        CCA_DIEP_ADDITIONS,
        CCA_PROCEEDS,
        CCA_DIEP_PROCEEDS,
        CCA_IMMEDIATE_EXPENSING,
        CCA_AIIP_ADDITIONS,
        CCA_RIIP_ADDITIONS,
        CCA_CLAIMED,
        CCA_NO_PROPERTY_LEFT,
        CCA_PERSONAL_PART_REMAINING,
        CCA_HALF_YEAR_RULE_DIFFERS,
        CCA_RATE_ELECTION,
        CCA_VEHICLE_ACQUIRED_YEAR,
        CCA_VEHICLE_COST,
        CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
        CCA_SOLD_ZEPVS,
    ),
)
"""Farming classes, Form T2042 Area A "Calculation of capital cost allowance (CCA) claim": a
starting list with one record for each class, holding the columns the filer enters (class
number, UCC at the start of the year, additions, the DIEP part of the additions, proceeds, the
proceeds of DIEPs, the immediate expensing amount, the AIIP and RIIP parts of the additions, the
CCA claimed), whether any property is left in the class, the remaining personal part of a
property used for both personal and business use (endnote 9), whether the additions are treated the
opposite way from their class for the half-year rule (column 18), the CCA rate the
caller elects for it (a purpose-built rental or a building in a separate class), then the year the
vehicle was acquired, its actual cost and the government assistance for it (endnote 2),
then the vehicles sold from a Class 54 row, last."""

FARM_CCA_CLASSES_ADJUSTED = RecordListKind.declare(
    CATALOG,
    "farm_cca_classes_adjusted",
    fields=tuple(
        field
        for field in FARM_CCA_CLASSES.fields
        if field
        not in (
            CCA_VEHICLE_ACQUIRED_YEAR,
            CCA_VEHICLE_COST,
            CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
            CCA_SOLD_ZEPVS,
        )
    ),
)
"""Farming classes with the proceeds adjusted, Form T2042 Area A endnote 2: "The proceeds of
disposition of [...] a passenger vehicle bought after April 18, 2021, that has been included in
Class 10.1, and whose cost is more than the prescribed amount will be adjusted based on a factor
equal to its prescribed amount as a proportion of the actual cost of the vehicle". The list of
farming classes without the year the vehicle was acquired, its cost, the government
assistance and the vehicles sold from a Class 54 row, with columns 5 and 6 (the proceeds and the
proceeds of DIEPs) adjusted."""
FARM_CCA_CLASSES_CHECKED = RecordListKind.declare(
    CATALOG,
    "farm_cca_classes_checked",
    fields=FARM_CCA_CLASSES.fields,
)
"""Farming classes checked, Form T2042 Area A "Calculation of capital cost allowance (CCA) claim":
the list of the farming classes with the cost of additions of each Class 10.1 passenger vehicle
checked, that is, not more than its limit with tax (Guide T4002 2025, "Class 10.1 (30%)"). The rows
are passed on unchanged, with the same fields as the list they check."""


FARM_EPOP_ASSOCIATED = CATALOG.declare("farm_epop_associated", int, non_negative=True)
"""Whether the filer is associated with an EPOP, Form T2042 Area A endnote 5 "$1.5 million, if you
are not associated with any other eligible person or partnership (EPOP) in the tax year" and
"amount iv of Area G, if you are associated with one or more EPOPs in the tax year": 1 if the
filer is associated with one or more EPOPs in the tax year, 0 if not, a starting count. It is
endnote 5's association, whether or not an agreement was filed; Area G is filled in when one
was."""

FARM_EPOP_ASSOCIATED_CHECKED = CATALOG.declare(
    "farm_epop_associated_checked", int, non_negative=True
)
"""Whether the filer is associated with an EPOP, Form T2042 Area A endnote 5 "$1.5 million, if
you are not associated with any other eligible person or partnership (EPOP) in the tax year":
the answer of `ca/farm_epop_associated` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

FARM_EPOP_AGREEMENT_FILED = CATALOG.declare("farm_epop_agreement_filed", int, non_negative=True)
"""Whether the agreement was filed, Form T2042 Area A endnote 5 "zero, if you are associated with
one or more EPOPs and an agreement that assigns a percentage to one or more of the associated
EPOPs was not filed with the minister in a prescribed form": 1 if the agreement was filed, 0 if
it was not, a starting count."""

FARM_EPOP_AGREEMENT_FILED_CHECKED = CATALOG.declare(
    "farm_epop_agreement_filed_checked", int, non_negative=True
)
"""Whether the agreement was filed, Form T2042 Area A endnote 5 "zero, if you are associated with
one or more EPOPs and an agreement that assigns a percentage to one or more of the associated
EPOPs was not filed with the minister in a prescribed form": the answer of
`ca/farm_epop_agreement_filed` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a
count of 1 or 0. A count of 2 or more is refused, not capped."""

FARM_EPOP_PERCENTAGE = CATALOG.declare("farm_epop_percentage", Decimal, non_negative=True)
"""Percentage assigned to the farm, Form T2042 Area G "Column 3: Percentage assigned under the
agreement" (the filer's own row), entered as the form prints it, 40 for 40%: a starting
amount."""

FARM_EPOP_PERCENTAGE_TOTAL = CATALOG.declare(
    "farm_epop_percentage_total", Decimal, non_negative=True
)
"""Total of the percentages assigned, Form T2042 Area G "Total of percentage assigned: Total of
column 3", entered as the form prints it: a starting amount."""

FARM_MINISTER_ALLOCATION_GIVEN = CATALOG.declare(
    "farm_minister_allocation_given", int, non_negative=True
)
"""Whether the minister allocated an amount, Form T2042 Area A endnote 5 "any amount allocated by
the minister under subsection 1104(3.4) of the Regulations": 1 if an amount was allocated, 0
otherwise, a starting count."""

FARM_MINISTER_ALLOCATION_GIVEN_CHECKED = CATALOG.declare(
    "farm_minister_allocation_given_checked", int, non_negative=True
)
"""Whether the minister allocated an amount, Form T2042 Area A endnote 5 "any amount allocated by
the minister under subsection 1104(3.4) of the Regulations": the answer of
`ca/farm_minister_allocation_given` after the check that it is 0 or 1 (`ca/yes_or_no_count`),
a count of 1 or 0. A count of 2 or more is refused, not capped."""

FARM_MINISTER_ALLOCATION = CATALOG.declare("farm_minister_allocation", Decimal, non_negative=True)
"""Amount allocated by the minister, Form T2042 Area A endnote 5 "any amount allocated by the
minister under subsection 1104(3.4) of the Regulations": a starting amount, which replaces the
immediate expensing limit when the minister allocated one."""

FARM_NOT_MAIN_SOURCE_OF_INCOME = CATALOG.declare(
    "farm_not_main_source_of_income", int, non_negative=True
)
"""Whether farming was not the main source of income, Guide T4002 "Restricted farm losses (partly
deductible)": "if farming was neither your main source of income ... nor was it your main source
of income in addition to some other subordinate source of income ... you may only be able to
deduct a part of your net farm loss" (confirmed from the PDF; no .txt published): 1 if it was
neither, 0 if it was (or was with a subordinate source), a starting count of the filer's yes or
no, asked once for the return."""

FARM_NOT_MAIN_SOURCE_OF_INCOME_CHECKED = CATALOG.declare(
    "farm_not_main_source_of_income_checked", int, non_negative=True
)
"""Whether farming was not the main source of income, Guide T4002 "Restricted farm losses (partly
deductible)" "neither your main source of income nor ... your main source of income in addition to
some other subordinate source of income" (confirmed from the PDF; no .txt published): the answer
of `ca/farm_not_main_source_of_income` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a
count of 1 or 0. A count of 2 or more is refused, not capped."""

FARM_NET_INCOME_LINE_9946 = CATALOG.declare("farm_net_income_line_9946", Decimal)
"""Net farming income before the restricted farm loss, Form T2042 line 9946 "Your net income (loss):
Amount 5C minus line 9945 (enter this amount on line 14100 of your income tax and benefit
return)", added over all the T2042 statements of the return: signed, a loss is negative.
`ca/farm_loss.farming_income` is the amount after the restricted part of a loss is added back."""

FARM_NET_LOSS = CATALOG.declare("farm_net_loss", Decimal, non_negative=True)
"""Net farm loss, Guide T4002 "Restricted farm losses (partly deductible)" "the lesser of: A) your
net farm loss for the year" (confirmed from the PDF; no .txt published): the negation of line 9946
when it is a loss, else 0."""

FARM_RESTRICTED_LOSS_BASE_AMOUNT = CATALOG.declare(
    "farm_restricted_loss_base_amount", Decimal, non_negative=True
)
"""Base amount of the restricted farm loss, Guide T4002 "Restricted farm losses (partly deductible)"
"B) $2,500 plus 50% × (your net farm loss minus $2,500)" (confirmed from the PDF; no .txt
published): the printed $2,500, from a dataset."""

FARM_RESTRICTED_LOSS_FULL_THRESHOLD = CATALOG.declare(
    "farm_restricted_loss_full_threshold", Decimal, non_negative=True
)
"""Net farm loss from which the annual maximum applies, Guide T4002 "Restricted farm losses (partly
deductible)" "When your net farm loss is $32,500 or more, you can deduct $17,500 from your other
income" (confirmed from the PDF; no .txt published): the printed $32,500, from a dataset."""

FARM_RESTRICTED_LOSS_ANNUAL_MAXIMUM = CATALOG.declare(
    "farm_restricted_loss_annual_maximum", Decimal, non_negative=True
)
"""Annual maximum deduction of a restricted farm loss, Guide T4002 "Restricted farm losses (partly
deductible)" "the annual maximum deduction used in the calculation for restricted farm losses is
$17,500" (confirmed from the PDF; no .txt published): the printed $17,500, from a dataset."""

FARM_RESTRICTED_LOSS_PERCENTAGE = CATALOG.declare(
    "farm_restricted_loss_percentage", Decimal, non_negative=True
)
"""Percentage of the restricted farm loss, Guide T4002 "Restricted farm losses (partly deductible)"
"B) $2,500 plus 50% × (your net farm loss minus $2,500)" (confirmed from the PDF; no .txt
published): the printed 50%, from a dataset, as the guide prints a percentage (50 for 50%)."""

FARM_NET_LOSS_LESS_BASE_AMOUNT = CATALOG.declare("farm_net_loss_less_base_amount", Decimal)
"""Net farm loss minus $2,500, Guide T4002 "Restricted farm losses (partly deductible)"
"50% × (your net farm loss minus $2,500)" (confirmed from the PDF; no .txt published): signed,
below $2,500 it is negative."""

FARM_RESTRICTED_LOSS_HALF_OF_EXCESS = CATALOG.declare(
    "farm_restricted_loss_half_of_excess", Decimal
)
"""50% of the net farm loss minus $2,500, Guide T4002 "Restricted farm losses (partly deductible)"
"50% × (your net farm loss minus $2,500)" (confirmed from the PDF; no .txt published): the printed
percentage of the difference, signed like it."""

FARM_RESTRICTED_LOSS_AMOUNT_B = CATALOG.declare(
    "farm_restricted_loss_amount_b", Decimal, non_negative=True
)
"""Amount B, Guide T4002 "Restricted farm losses (partly deductible)" "B) $2,500 plus 50% ×
(your net farm loss minus $2,500)" (confirmed from the PDF; no .txt published): the $2,500 plus 50%
of the net farm loss minus $2,500."""

FARM_RESTRICTED_LOSS_LESSER_OF_A_AND_B = CATALOG.declare(
    "farm_restricted_loss_lesser_of_a_and_b", Decimal, non_negative=True
)
"""Lesser of A and B, Guide T4002 "Restricted farm losses (partly deductible)" "the amount you can
deduct from your other income is the lesser of: A) your net farm loss for the year B) $2,500 plus
50% × (your net farm loss minus $2,500)" (confirmed from the PDF; no .txt published): the amount
deductible when the net farm loss is less than $32,500."""

FARM_NET_LOSS_LESS_FULL_THRESHOLD = CATALOG.declare("farm_net_loss_less_full_threshold", Decimal)
"""Net farm loss minus $32,500, Guide T4002 "Restricted farm losses (partly deductible)" "When your
net farm loss is $32,500 or more" (confirmed from the PDF; no .txt published): signed, it chooses
the amount deductible by its sign."""

FARM_LOSS_DEDUCTIBLE = CATALOG.declare("farm_loss_deductible", Decimal, non_negative=True)
"""Farm loss deductible from other income, Guide T4002 "Restricted farm losses (partly deductible)"
"When your net farm loss is $32,500 or more, you can deduct $17,500 from your other income" and
"When your net farm loss is less than $32,500, the amount you can deduct from your other income is
the lesser of" A and B (confirmed from the PDF; no .txt published): $17,500 at $32,500 or more,
else the lesser of A and B."""

FARM_RESTRICTED_LOSS = CATALOG.declare("farm_restricted_loss", Decimal, non_negative=True)
"""Restricted farm loss, Guide T4002 "Restricted farm losses (partly deductible)" "The amount
remaining is your restricted farm loss" (confirmed from the PDF; no .txt published): the net farm
loss minus the amount deductible."""

FARM_RESTRICTED_LOSS_ADDED_BACK = CATALOG.declare(
    "farm_restricted_loss_added_back", Decimal, non_negative=True
)
"""Restricted farm loss added back to line 9946, Guide T4002 "Restricted farm losses (partly
deductible)" "she enters $5,850 on line 14100 of her income tax return" (confirmed from the PDF;
no .txt published): the restricted farm loss when the answer
`ca/farm_not_main_source_of_income_checked` is 1, else 0."""

FARM_FISCAL_PERIOD_DAYS_ENTERED = CATALOG.declare(
    "farm_fiscal_period_days_entered", int, non_negative=True
)
"""Days of the fiscal period of Form T2042, the days the filer enters when the fiscal period is
shorter than a full year, 0 when none are entered (a full year).
Guide T4002 2025, "You were asking?": "Since your fiscal period is less than 365 days,
you have to prorate your CCA claim. ... base your CCA claim on the number of days in your
fiscal period compared to 365 days. In this case, your fiscal period is 214 days." A starting
count."""

FARM_LAND_ADDITIONS = CATALOG.declare("farm_land_additions", Decimal, non_negative=True)
"""Cost of the land added in the year, Form T2042 Area F "Line 9923: Total cost of all land
additions in the year": a starting amount, taken as entered."""

FARM_LAND_DISPOSITIONS = CATALOG.declare("farm_land_dispositions", Decimal, non_negative=True)
"""Proceeds of the land disposed of in the year, Form T2042 Area F "Line 9924: Total proceeds from
all land dispositions in the year": a starting amount, taken as entered."""

FARM_QUOTA_ADDITIONS = CATALOG.declare("farm_quota_additions", Decimal, non_negative=True)
"""Cost of the quota added in the year, Form T2042 Area H "Line 9929: Total cost of all quota
additions in the year": a starting amount, taken as entered."""

FARM_QUOTA_DISPOSITIONS = CATALOG.declare("farm_quota_dispositions", Decimal, non_negative=True)
"""Proceeds of the quota disposed of in the year, Form T2042 Area H "Line 9930: Total proceeds from
all quota dispositions in the year": a starting amount, taken as entered."""

FARM_LIABILITIES = CATALOG.declare("farm_liabilities", Decimal, non_negative=True)
"""Total business liabilities, Form T2042 Part 9 "Details of equity" "Line 9931: Total business
liabilities": a starting amount, taken as entered."""

FARM_DRAWINGS = CATALOG.declare("farm_drawings", Decimal, non_negative=True)
"""Drawings in the current year, Form T2042 Part 9 "Details of equity" "Line 9932: Drawings in the
current year": a starting amount, taken as entered."""

FARM_CAPITAL_CONTRIBUTIONS = CATALOG.declare(
    "farm_capital_contributions", Decimal, non_negative=True
)
"""Capital contributions in the current year, Form T2042 Part 9 "Details of equity" "Line 9933:
Capital contributions in the current year": a starting amount, taken as entered."""

FARM_DESIGNATED_PROVINCE = CATALOG.declare("farm_designated_province", int, non_negative=True)
"""Designated province of the farming business, Form T2043 Part 2 "Fill in Part 2 for your farming
businesses that have one or more permanent establishments that operate in only one of the
designated provinces.": the province the statement's business operates in, as a code in the order
of the form's Part 2 (1 Ontario, 2 Manitoba, 3 Saskatchewan, 4 Alberta, 5 Nova Scotia, 6 Prince
Edward Island, 7 Newfoundland and Labrador, 8 New Brunswick), a starting count; 0 means none (a farm
outside the designated provinces adds nothing to Part 2). A code above 8 names no province, so
`ca/count_refused_by_conditions` refuses it (see
`farm_designated_province_checked`)."""

FARM_DESIGNATED_PROVINCE_CHECKED = CATALOG.declare(
    "farm_designated_province_checked", int, non_negative=True
)
"""Designated province of the farming business, once checked, Form T2043 Part 2: the
`farm_designated_province` code unchanged, produced only when it is 0 (none) or 1 to 8, the
provinces of lines 2A to 2H (a code above 8 is refused, so the statement's amount 8 never goes to
a province that does not exist). The eight province counts of Chart A read this kind, not the
raw code."""

FARM_ALSO_OUTSIDE_EIGHT = CATALOG.declare("farm_also_outside_eight", int, non_negative=True)
"""Whether the farming business also has a permanent establishment outside the eight designated
provinces, Form T2043 box 67062 "Tick this box if you have multiple farming businesses with one or
more permanent establishments in multiple provinces or territories": 1 for yes and 0 for no, a
starting count. Chart B lists only the eight designated provinces, so a business's share in another
province (Quebec, for example) is not on the form; this answer counts that share as a ninth place
for the box. It counts whether or not the statement uses Chart B (an Ontario Chart A farm that also
has an establishment elsewhere is present in both places). A value other than 0 or 1 is refused
(see `farm_also_outside_eight_checked`)."""

FARM_ALSO_OUTSIDE_EIGHT_CHECKED = CATALOG.declare(
    "farm_also_outside_eight_checked", int, non_negative=True
)
"""The answer `farm_also_outside_eight`, once checked to be 0 or 1, Form T2043 box 67062: the
presence of the statement outside the eight designated provinces reads this kind, not the raw
answer."""

FARM_NON_ARMS_LENGTH_EXPENSES = CATALOG.declare(
    "farm_non_arms_length_expenses", Decimal, non_negative=True
)
"""Non-arm's length expenses of the farming business, Form T2043 Chart A amount 4 "Non-arm's length
transactions (total of all expenses incurred in a non-arm's length transaction from Part 4 of Form
T2042)": a starting amount."""

FARM_DAYS_IN_2024 = CATALOG.declare("farm_days_in_2024", int, non_negative=True)
"""Days of the fiscal period in 2024, Form T2043 Chart A amount 7 "Total number of days in the
fiscal period that fall within the 2024 calendar year divided by the total number of days in the
fiscal period (if the fiscal period starts and ends in 2025, enter "0")": the numerator of that
fraction, 0 when the fiscal period starts and ends in 2025, a starting count."""

FARM_CHART_B_PROVINCE = CATALOG.declare("farm_chart_b_province", int, non_negative=True)
"""Province code of one row of the Form T2043 Chart B province list of a statement, the designated
province of the row, in the order of the form's Part 2 and of `farm_designated_province` (1 Ontario,
2 Manitoba, 3 Saskatchewan, 4 Alberta, 5 Nova Scotia, 6 Prince Edward Island, 7 Newfoundland and
Labrador, 8 New Brunswick). A code outside 1 to 8 names no province and is refused by the Chart B
total that reads the row, naming the row by its position."""

FARM_CHART_B_PROVINCE_GROSS_INCOME = CATALOG.declare(
    "farm_chart_b_province_gross_income", Decimal, non_negative=True
)
"""Gross income of the farming business in the row's province, Form T2043 Chart B row 1 "Gross
income ($) of the farming business reasonably allocated to the permanent establishment(s) in the
designated province (applicable portion of line 9659 of Form T2042, excluding the credit). See
note 5.": a starting amount of that row, summed with the other rows of the same province."""

FARM_CHART_B_PROVINCE_SALARIES = CATALOG.declare(
    "farm_chart_b_province_salaries", Decimal, non_negative=True
)
"""Salaries and wages of the farming business in the row's province, Form T2043 Chart B row 4
"Salaries and wages paid ($) to employees of the farming business reasonably allocated to the
permanent establishment(s) in the designated province (applicable portion of line 9814 of Form
T2042). See note 7.": a starting amount of that row, summed with the other rows of the same
province."""

FARM_CHART_B_PROVINCES = RecordListKind.declare(
    CATALOG,
    "farm_chart_b_provinces",
    fields=(
        FARM_CHART_B_PROVINCE,
        FARM_CHART_B_PROVINCE_GROSS_INCOME,
        FARM_CHART_B_PROVINCE_SALARIES,
    ),
)
"""Form T2043 Chart B province list of a statement, a starting list with one record for each
designated province in which the farming business has a permanent establishment: the province's
code, Chart B row 1 and row 4 of that province. A province with no record counts as 0 (the form
is silent on blank versus 0, and the Act s.127.42 and Regulations s.2603(2) give a province with no
permanent establishment none of the income). Two records for one province add."""

FARM_CHART_B_GROSS_INCOME_ON = CATALOG.declare(
    "farm_chart_b_gross_income_on", Decimal, non_negative=True
)
"""Gross income of the farming business in Ontario, Form T2043 Chart B row 1 "Gross income ($) of
the farming business reasonably allocated to the permanent establishment(s) in the designated
province (applicable portion of line 9659 of Form T2042, excluding the credit). See note 5.":
line 67067 of Part 3 adds it over the statements. Computed, not a starting amount: the total
of the statement's province list rows for this province (`ca/farm_chart_b_provinces`), 0 when
there is none."""

FARM_CHART_B_GROSS_INCOME_MB = CATALOG.declare(
    "farm_chart_b_gross_income_mb", Decimal, non_negative=True
)
"""Gross income of the farming business in Manitoba, Form T2043 Chart B row 1 "Gross income ($)
of the farming business reasonably allocated to the permanent establishment(s) in the
designated province (applicable portion of line 9659 of Form T2042, excluding the credit). See
note 5.": line 67068 of Part 3 adds it over the statements. Computed, not a starting amount:
the total of the statement's province list rows for this province
(`ca/farm_chart_b_provinces`), 0 when there is none."""

FARM_CHART_B_GROSS_INCOME_SK = CATALOG.declare(
    "farm_chart_b_gross_income_sk", Decimal, non_negative=True
)
"""Gross income of the farming business in Saskatchewan, Form T2043 Chart B row 1 "Gross income
($) of the farming business reasonably allocated to the permanent establishment(s) in the
designated province (applicable portion of line 9659 of Form T2042, excluding the credit). See
note 5.": line 67069 of Part 3 adds it over the statements. Computed, not a starting amount:
the total of the statement's province list rows for this province
(`ca/farm_chart_b_provinces`), 0 when there is none."""

FARM_CHART_B_GROSS_INCOME_AB = CATALOG.declare(
    "farm_chart_b_gross_income_ab", Decimal, non_negative=True
)
"""Gross income of the farming business in Alberta, Form T2043 Chart B row 1 "Gross income ($) of
the farming business reasonably allocated to the permanent establishment(s) in the designated
province (applicable portion of line 9659 of Form T2042, excluding the credit). See note 5.":
line 67070 of Part 3 adds it over the statements. Computed, not a starting amount: the total
of the statement's province list rows for this province (`ca/farm_chart_b_provinces`), 0 when
there is none."""

FARM_CHART_B_GROSS_INCOME_NS = CATALOG.declare(
    "farm_chart_b_gross_income_ns", Decimal, non_negative=True
)
"""Gross income of the farming business in Nova Scotia, Form T2043 Chart B row 1 "Gross income
($) of the farming business reasonably allocated to the permanent establishment(s) in the
designated province (applicable portion of line 9659 of Form T2042, excluding the credit). See
note 5.": line 67095 of Part 3 adds it over the statements. Computed, not a starting amount:
the total of the statement's province list rows for this province
(`ca/farm_chart_b_provinces`), 0 when there is none."""

FARM_CHART_B_GROSS_INCOME_PE = CATALOG.declare(
    "farm_chart_b_gross_income_pe", Decimal, non_negative=True
)
"""Gross income of the farming business in Prince Edward Island, Form T2043 Chart B row 1 "Gross
income ($) of the farming business reasonably allocated to the permanent establishment(s) in
the designated province (applicable portion of line 9659 of Form T2042, excluding the credit).
See note 5.": line 67096 of Part 3 adds it over the statements. Computed, not a starting
amount: the total of the statement's province list rows for this province
(`ca/farm_chart_b_provinces`), 0 when there is none."""

FARM_CHART_B_GROSS_INCOME_NL = CATALOG.declare(
    "farm_chart_b_gross_income_nl", Decimal, non_negative=True
)
"""Gross income of the farming business in Newfoundland and Labrador, Form T2043 Chart B row 1
"Gross income ($) of the farming business reasonably allocated to the permanent
establishment(s) in the designated province (applicable portion of line 9659 of Form T2042,
excluding the credit). See note 5.": line 67097 of Part 3 adds it over the statements.
Computed, not a starting amount: the total of the statement's province list rows for this
province (`ca/farm_chart_b_provinces`), 0 when there is none."""

FARM_CHART_B_GROSS_INCOME_NB = CATALOG.declare(
    "farm_chart_b_gross_income_nb", Decimal, non_negative=True
)
"""Gross income of the farming business in New Brunswick, Form T2043 Chart B row 1 "Gross income
($) of the farming business reasonably allocated to the permanent establishment(s) in the
designated province (applicable portion of line 9659 of Form T2042, excluding the credit). See
note 5.": line 67098 of Part 3 adds it over the statements. Computed, not a starting amount:
the total of the statement's province list rows for this province
(`ca/farm_chart_b_provinces`), 0 when there is none."""

FARM_CHART_B_SALARIES_ON = CATALOG.declare("farm_chart_b_salaries_on", Decimal, non_negative=True)
"""Salaries and wages of the farming business in Ontario, Form T2043 Chart B row 4 "Salaries and
wages paid ($) to employees of the farming business reasonably allocated to the permanent
establishment(s) in the designated province (applicable portion of line 9814 of Form T2042).
See note 7.": line 67071 of Part 3 adds it over the statements. Computed, not a starting
amount: the total of the statement's province list rows for this province
(`ca/farm_chart_b_provinces`), 0 when there is none."""

FARM_CHART_B_SALARIES_MB = CATALOG.declare("farm_chart_b_salaries_mb", Decimal, non_negative=True)
"""Salaries and wages of the farming business in Manitoba, Form T2043 Chart B row 4 "Salaries and
wages paid ($) to employees of the farming business reasonably allocated to the permanent
establishment(s) in the designated province (applicable portion of line 9814 of Form T2042).
See note 7.": line 67072 of Part 3 adds it over the statements. Computed, not a starting
amount: the total of the statement's province list rows for this province
(`ca/farm_chart_b_provinces`), 0 when there is none."""

FARM_CHART_B_SALARIES_SK = CATALOG.declare("farm_chart_b_salaries_sk", Decimal, non_negative=True)
"""Salaries and wages of the farming business in Saskatchewan, Form T2043 Chart B row 4 "Salaries
and wages paid ($) to employees of the farming business reasonably allocated to the permanent
establishment(s) in the designated province (applicable portion of line 9814 of Form T2042).
See note 7.": line 67073 of Part 3 adds it over the statements. Computed, not a starting
amount: the total of the statement's province list rows for this province
(`ca/farm_chart_b_provinces`), 0 when there is none."""

FARM_CHART_B_SALARIES_AB = CATALOG.declare("farm_chart_b_salaries_ab", Decimal, non_negative=True)
"""Salaries and wages of the farming business in Alberta, Form T2043 Chart B row 4 "Salaries and
wages paid ($) to employees of the farming business reasonably allocated to the permanent
establishment(s) in the designated province (applicable portion of line 9814 of Form T2042).
See note 7.": line 67074 of Part 3 adds it over the statements. Computed, not a starting
amount: the total of the statement's province list rows for this province
(`ca/farm_chart_b_provinces`), 0 when there is none."""

FARM_CHART_B_SALARIES_NS = CATALOG.declare("farm_chart_b_salaries_ns", Decimal, non_negative=True)
"""Salaries and wages of the farming business in Nova Scotia, Form T2043 Chart B row 4 "Salaries
and wages paid ($) to employees of the farming business reasonably allocated to the permanent
establishment(s) in the designated province (applicable portion of line 9814 of Form T2042).
See note 7.": line 67099 of Part 3 adds it over the statements. Computed, not a starting
amount: the total of the statement's province list rows for this province
(`ca/farm_chart_b_provinces`), 0 when there is none."""

FARM_CHART_B_SALARIES_PE = CATALOG.declare("farm_chart_b_salaries_pe", Decimal, non_negative=True)
"""Salaries and wages of the farming business in Prince Edward Island, Form T2043 Chart B row 4
"Salaries and wages paid ($) to employees of the farming business reasonably allocated to the
permanent establishment(s) in the designated province (applicable portion of line 9814 of Form
T2042). See note 7.": line 67100 of Part 3 adds it over the statements. Computed, not a
starting amount: the total of the statement's province list rows for this province
(`ca/farm_chart_b_provinces`), 0 when there is none."""

FARM_CHART_B_SALARIES_NL = CATALOG.declare("farm_chart_b_salaries_nl", Decimal, non_negative=True)
"""Salaries and wages of the farming business in Newfoundland and Labrador, Form T2043 Chart B
row 4 "Salaries and wages paid ($) to employees of the farming business reasonably allocated
to the permanent establishment(s) in the designated province (applicable portion of line 9814
of Form T2042). See note 7.": line 67101 of Part 3 adds it over the statements. Computed, not
a starting amount: the total of the statement's province list rows for this province
(`ca/farm_chart_b_provinces`), 0 when there is none."""

FARM_CHART_B_SALARIES_NB = CATALOG.declare("farm_chart_b_salaries_nb", Decimal, non_negative=True)
"""Salaries and wages of the farming business in New Brunswick, Form T2043 Chart B row 4
"Salaries and wages paid ($) to employees of the farming business reasonably allocated to the
permanent establishment(s) in the designated province (applicable portion of line 9814 of Form
T2042). See note 7.": line 67102 of Part 3 adds it over the statements. Computed, not a
starting amount: the total of the statement's province list rows for this province
(`ca/farm_chart_b_provinces`), 0 when there is none."""

T2042_STATEMENTS = RecordListKind.declare(
    CATALOG,
    "t2042_statements",
    fields=(
        FARM_WHEAT,
        FARM_OATS,
        FARM_BARLEY,
        FARM_MIXED_GRAINS,
        FARM_CORN,
        FARM_CANOLA,
        FARM_FLAXSEED,
        FARM_SOYBEANS,
        FARM_GRAINS_AND_OILSEEDS,
        FARM_FRUIT,
        FARM_POTATOES,
        FARM_VEGETABLES,
        FARM_TOBACCO,
        FARM_GREENHOUSE_AND_NURSERY,
        FARM_FORAGE_CROPS_OR_SEEDS,
        FARM_OTHER_CROPS,
        FARM_CATTLE,
        FARM_SWINE,
        FARM_POULTRY,
        FARM_SHEEP_AND_LAMBS,
        FARM_LIVESTOCK_AND_ANIMAL_PRODUCTS_REVENUE,
        FARM_MILK_AND_CREAM,
        FARM_EGGS,
        FARM_OTHER_COMMODITIES,
        FARM_DAIRY_SUBSIDIES,
        FARM_CROP_INSURANCE,
        FARM_OTHER_PROGRAM_PAYMENTS,
        FARM_REBATES,
        FARM_CUSTOM_WORK,
        FARM_INSURANCE_PROCEEDS,
        FARM_PATRONAGE_DIVIDENDS,
        FARM_OTHER_INCOME,
        FARM_CONTAINERS_AND_TWINE,
        FARM_FERTILIZERS_AND_LIME,
        FARM_PESTICIDES,
        FARM_SEEDS_AND_PLANTS,
        FARM_FEED_SUPPLEMENTS_STRAW_AND_BEDDING,
        FARM_LIVESTOCK_PURCHASED,
        FARM_VETERINARY_FEES,
        FARM_MACHINERY_REPAIRS_LICENCES_AND_INSURANCE,
        FARM_GASOLINE_DIESEL_AND_OIL,
        FARM_BUILDING_REPAIRS_AND_MAINTENANCE,
        FARM_CLEARING_LEVELLING_AND_DRAINING,
        FARM_CROP_INSURANCE_PREMIUMS,
        FARM_CUSTOM_WORK_EXPENSES,
        FARM_ELECTRICITY,
        FARM_HEATING_AND_CURING_FUEL,
        FARM_INSURANCE_PROGRAM_OVERPAYMENT_RECAPTURE,
        FARM_INSURANCE,
        FARM_INTEREST_AND_BANK_CHARGES,
        FARM_OFFICE_EXPENSES,
        FARM_PROFESSIONAL_FEES,
        FARM_PROPERTY_TAXES,
        FARM_RENT,
        FARM_SALARIES_WAGES_AND_BENEFITS,
        BUSINESS_VEHICLES,
        FARM_VEHICLE_SALES_TAX_RATE,
        FARM_SMALL_TOOLS,
        FARM_MANDATORY_INVENTORY_ADJUSTMENT_PREVIOUS_YEAR,
        FARM_OPTIONAL_INVENTORY_ADJUSTMENT_PREVIOUS_YEAR,
        FARM_OTHER_EXPENSES,
        FARM_OPTIONAL_INVENTORY_ADJUSTMENT_CURRENT_YEAR,
        FARM_MANDATORY_INVENTORY_ADJUSTMENT_CURRENT_YEAR,
        FARM_CCA_PERSONAL_PART,
        FARM_PARTNER,
        FARM_PARTNER_SHARE,
        FARM_FUEL_CHARGE_CREDIT,
        FARM_PARTNER_GST_HST_REBATE,
        FARM_PARTNER_OTHER_AMOUNT_A,
        FARM_PARTNER_OTHER_AMOUNT_B,
        FARM_PARTNER_OTHER_AMOUNT_C,
        FARM_PARTNER_OTHER_AMOUNT_D,
        FARM_PARTNER_OTHER_AMOUNT_E,
        FARM_HOME_HEAT,
        FARM_HOME_ELECTRICITY,
        FARM_HOME_INSURANCE,
        FARM_HOME_MAINTENANCE,
        FARM_HOME_MORTGAGE_INTEREST,
        FARM_HOME_PROPERTY_TAXES,
        FARM_HOME_OTHER_EXPENSES,
        FARM_HOME_PERSONAL_USE_PART,
        FARM_HOME_CCA,
        FARM_HOME_CARRIED_FORWARD,
        FARM_FISCAL_PERIOD_DAYS_ENTERED,
        FARM_LAND_ADDITIONS,
        FARM_LAND_DISPOSITIONS,
        FARM_QUOTA_ADDITIONS,
        FARM_QUOTA_DISPOSITIONS,
        FARM_LIABILITIES,
        FARM_DRAWINGS,
        FARM_CAPITAL_CONTRIBUTIONS,
        FARM_DESIGNATED_PROVINCE,
        FARM_NON_ARMS_LENGTH_EXPENSES,
        FARM_DAYS_IN_2024,
        FARM_CHART_B_PROVINCES,
        FARM_ALSO_OUTSIDE_EIGHT,
        FARM_CCA_CLASSES,
        FARM_EPOP_ASSOCIATED,
        FARM_EPOP_AGREEMENT_FILED,
        FARM_EPOP_PERCENTAGE,
        FARM_EPOP_PERCENTAGE_TOTAL,
        FARM_MINISTER_ALLOCATION_GIVEN,
        FARM_MINISTER_ALLOCATION,
    ),
)
"""Statements of Form T2042, one record for each statement of farming activities the return
carries (one for each farming business): its fields are the starting amounts, the Area A list
and the Area G answers of one statement, Parts 3 to 7 and Area G, in the order of the form. The
form `ca/t2042` runs once for each record; T1 line 14100 "Net" adds the lines 9946 of the records.
A field is not an artifact of the return."""

FARM_CLOSING_UCC = RecordListKind.declare(
    CATALOG, "farm_closing_ucc", fields=(CCA_CLASS_NUMBER, CCA_UCC_AT_END)
)
"""Farming closing UCC, Form T2042 Area A "UCC at the end of the year (col. 7 minus col. 21)": one
record for each class of the farming classes, holding its class number and column 22."""

FARM_IMMEDIATE_EXPENSING_CAP = CATALOG.declare(
    "farm_immediate_expensing_cap", Decimal, non_negative=True
)
"""Immediate expensing limit when not associated, Form T2042 Area A endnote 5 "$1.5 million, if you
are not associated with any other eligible person or partnership (EPOP) in the tax year" and Area G
"Immediate expensing limit allocated to your business: Multiply $1.5 million by the percentage
assigned to your business in column 3**": the printed $1.5 million, from a dataset."""

FARM_EPOP_PERCENTAGE_MAXIMUM = CATALOG.declare(
    "farm_epop_percentage_maximum", Decimal, non_negative=True
)
"""Largest total of the percentages assigned, Form T2042 Area G "The total of all percentages
assigned under the agreement should not be more than 100%" and "** If the total of column 3 is
more than 100%, enter "0."": the printed 100%, from a dataset, as the form prints a percentage
(100 for 100%)."""

FARM_IMMEDIATE_EXPENSING_SHARE = CATALOG.declare(
    "farm_immediate_expensing_share", Decimal, non_negative=True
)
"""Immediate expensing limit times the percentage, the first step of Form T2042 Area G "Immediate
expensing limit allocated to your business: Multiply $1.5 million by the percentage assigned to
your business in column 3**": $1.5 million times the percentage assigned to your business."""

FARM_EPOP_PERCENTAGE_ROOM = CATALOG.declare("farm_epop_percentage_room", Decimal)
"""Room under 100% in the percentages assigned, the test of Form T2042 Area G "** If the total of
column 3 is more than 100%, enter "0."": 100 less the total of column 3, signed, negative when the
total is more than 100%."""

FARM_IMMEDIATE_EXPENSING_ALLOCATED = CATALOG.declare(
    "farm_immediate_expensing_allocated", Decimal, non_negative=True
)
"""Immediate expensing limit allocated to the farm, Form T2042 Area G "Immediate expensing limit
allocated to your business: Multiply $1.5 million by the percentage assigned to your business in
column 3**" and "** If the total of column 3 is more than 100%, enter "0."": the multiple, or 0
when the total of column 3 is more than 100%."""

FARM_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT = CATALOG.declare(
    "farm_immediate_expensing_associated_limit", Decimal, non_negative=True
)
"""Immediate expensing limit when associated with an EPOP, Form T2042 Area A endnote 5 "amount iv
of Area G, if you are associated with one or more EPOPs in the tax year" and "zero, if you are
associated with one or more EPOPs and an agreement that assigns a percentage to one or more of the
associated EPOPs was not filed with the minister in a prescribed form": amount iv, or 0 when no
agreement was filed."""

FARM_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER = CATALOG.declare(
    "farm_immediate_expensing_limit_before_minister", Decimal, non_negative=True
)
"""Immediate expensing limit before any amount allocated by the minister, Form T2042 Area A
endnote 5 "the immediate expensing limit, which is equal to one of the following, whichever is
applicable": $1.5 million when not associated with an EPOP, else the limit when associated."""

FARM_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION = CATALOG.declare(
    "farm_immediate_expensing_limit_before_proration", Decimal, non_negative=True
)
"""Immediate expensing limit before the days of the fiscal period scale it, Income Tax
Regulations 1104(3.5)(b): "where an eligible person or partnership has a taxation year that is
less than 51 weeks, its immediate expensing limit for the year is that proportion of its
immediate expensing limit for the year determined without reference to this paragraph that the
number of days in the year is of 365". Form T2042 Area A endnote 5 "the immediate expensing
limit, which is equal to one of the following, whichever is applicable", and "any amount
allocated by the minister under subsection 1104(3.4) of the Regulations": the limit before any
amount allocated by the minister, or that amount when there is one, unscaled. Guide T4002,
"Immediate expensing incentive": "The limit is also prorated for tax years shorter than 365
days"."""

FARM_IMMEDIATE_EXPENSING_LIMIT = CATALOG.declare(
    "farm_immediate_expensing_limit", Decimal, non_negative=True
)
"""Immediate expensing limit, Form T2042 Area A endnote 5 "the immediate expensing limit, which is
equal to one of the following, whichever is applicable", including "any amount allocated by the
minister under subsection 1104(3.4) of the Regulations": the limit above, or the amount allocated
by the minister when there is one."""

FARM_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED = CATALOG.declare(
    "farm_immediate_expensing_limit_unprorated", Decimal, non_negative=True
)
"""Immediate expensing limit before the days scaling, Form T2042 Area A endnote 5 "the immediate
expensing limit, which is equal to one of the following, whichever is applicable", and Guide T4002:
"The limit is also prorated for tax years shorter than 365 days": the per-person limit before the
limit is scaled to the days of the fiscal period, the minister's amount as entered."""

FARM_IMMEDIATE_EXPENSING_CLAIM = CATALOG.declare(
    "farm_immediate_expensing_claim", Decimal, non_negative=True
)
"""Total immediate expensing claim for the year, Form T2042 Area A "Total immediate expensing claim
for the year: Total of column 9" (line i), limited by endnote 5 to "the lesser of" the immediate
expensing limit, "the UCC of DIEPs in column 8" and "the amount of income, if any, earned from the
source of income that is a business (before any CCA deductions)": the total of column 9 over the
classes."""

FARM_INCOME_BEFORE_CCA = CATALOG.declare("farm_income_before_cca", Decimal, non_negative=True)
"""Farming income before CCA, Form T2042 Area A endnote 5 "the amount of income, if any, earned
from the source of income that is a business (before any CCA deductions) in which the relevant
DIEP is used for the tax year": line 9899 "Net income (loss) before inventory adjustments" plus
line 9936, the CCA it deducted, not below zero. Guide T4002 2025 pairs line 9899 on Form T2042
with line 9369 on Forms T2125 and T2121, the figure those forms use as income before CCA. The
recapture on line 9600 is already in gross income and the terminal loss on line 9790 is already
an expense."""

FARM_FISCAL_PERIOD_DAYS = CATALOG.declare("farm_fiscal_period_days", int, non_negative=True)
"""Days of the fiscal period of Form T2042 that the CCA claim and closing UCC are prorated by:
the days entered when above 0, else the days in a full year.
Guide T4002 2025, "You were asking?": "Since your fiscal period is less than 365 days,
you have to prorate your CCA claim. ... base your CCA claim on the number of days in your
fiscal period compared to 365 days. In this case, your fiscal period is 214 days"
(the Guide's example)."""

FARM_CHART_A_SUBTOTAL = CATALOG.declare("farm_chart_a_subtotal", Decimal, non_negative=True)
"""Subtotal of Chart A of Form T2043, Chart A amount 5 "Subtotal: Add amounts 2 to 4": the
mandatory (line 9937) and optional (line 9938) inventory adjustments of the previous year and the
non-arm's length transactions of this statement."""

FARM_CHART_A_GROSS_EXPENSES = CATALOG.declare("farm_chart_a_gross_expenses", Decimal)
"""Gross farming expenses of the statement, Form T2043 Chart A amount 6 "Gross farming expenses:
Amount 1 minus amount 5": line 9898 less amount 5, as the form prints it, signed: the form prints
no floor and no maximum for amount 5."""

FARM_CHART_A_AMOUNT_8 = CATALOG.declare("farm_chart_a_amount_8", Decimal)
"""Gross farming expenses in 2024 of the statement, Form T2043 Chart A amount 8 "Amount 6
multiplied by amount 7.": amount 6 times the days of the fiscal period in 2024 over its total
days, rounded once to the cent."""

FARM_IN_PROVINCE_ON = CATALOG.declare("farm_in_province_on", int, non_negative=True)
"""Statement in Ontario, Form T2043 Part 2 line 67063 "Add all farming expenses in ON from amount 8
of Chart A.": 1 when the statement's designated province is Ontario, else 0, a count."""


FARM_IN_PROVINCE_MB = CATALOG.declare("farm_in_province_mb", int, non_negative=True)
"""Statement in Manitoba, Form T2043 Part 2 line 67064 "Add all farming expenses in MB from amount 8
of Chart A.": 1 when the statement's designated province is Manitoba, else 0, a count."""


FARM_IN_PROVINCE_SK = CATALOG.declare("farm_in_province_sk", int, non_negative=True)
"""Statement in Saskatchewan, Form T2043 Part 2 line 67065 "Add all farming expenses in SK from
amount 8 of Chart A.": 1 when the statement's designated province is Saskatchewan, else 0, a
count."""


FARM_IN_PROVINCE_AB = CATALOG.declare("farm_in_province_ab", int, non_negative=True)
"""Statement in Alberta, Form T2043 Part 2 line 67066 "Add all farming expenses in AB from amount 8
of Chart A.": 1 when the statement's designated province is Alberta, else 0, a count."""


FARM_IN_PROVINCE_NS = CATALOG.declare("farm_in_province_ns", int, non_negative=True)
"""Statement in Nova Scotia, Form T2043 Part 2 line 67091 "Add all farming expenses in NS from
amount 8 of Chart A.": 1 when the statement's designated province is Nova Scotia, else 0, a
count."""


FARM_IN_PROVINCE_PE = CATALOG.declare("farm_in_province_pe", int, non_negative=True)
"""Statement in Prince Edward Island, Form T2043 Part 2 line 67092 "Add all farming expenses in PE
from amount 8 of Chart A.": 1 when the statement's designated province is Prince Edward Island, else
0, a count."""


FARM_IN_PROVINCE_NL = CATALOG.declare("farm_in_province_nl", int, non_negative=True)
"""Statement in Newfoundland and Labrador, Form T2043 Part 2 line 67093 "Add all farming expenses in
NL from amount 8 of Chart A.": 1 when the statement's designated province is Newfoundland and
Labrador, else 0, a count."""


FARM_IN_PROVINCE_NB = CATALOG.declare("farm_in_province_nb", int, non_negative=True)
"""Statement in New Brunswick, Form T2043 Part 2 line 67094 "Add all farming expenses in NB from
amount 8 of Chart A.": 1 when the statement's designated province is New Brunswick, else 0, a
count."""

FARM_AMOUNT_8_ON = CATALOG.declare("farm_amount_8_on", Decimal)
"""Amount 8 of the statement in Ontario, Form T2043 Part 2 line 67063 "Add all farming expenses in
ON from amount 8 of Chart A.": amount 8 of Chart A when the statement's designated province is
Ontario, else 0."""


FARM_AMOUNT_8_MB = CATALOG.declare("farm_amount_8_mb", Decimal)
"""Amount 8 of the statement in Manitoba, Form T2043 Part 2 line 67064 "Add all farming expenses in
MB from amount 8 of Chart A.": amount 8 of Chart A when the statement's designated province is
Manitoba, else 0."""


FARM_AMOUNT_8_SK = CATALOG.declare("farm_amount_8_sk", Decimal)
"""Amount 8 of the statement in Saskatchewan, Form T2043 Part 2 line 67065 "Add all farming expenses
in SK from amount 8 of Chart A.": amount 8 of Chart A when the statement's designated province is
Saskatchewan, else 0."""


FARM_AMOUNT_8_AB = CATALOG.declare("farm_amount_8_ab", Decimal)
"""Amount 8 of the statement in Alberta, Form T2043 Part 2 line 67066 "Add all farming expenses in
AB from amount 8 of Chart A.": amount 8 of Chart A when the statement's designated province is
Alberta, else 0."""


FARM_AMOUNT_8_NS = CATALOG.declare("farm_amount_8_ns", Decimal)
"""Amount 8 of the statement in Nova Scotia, Form T2043 Part 2 line 67091 "Add all farming expenses
in NS from amount 8 of Chart A.": amount 8 of Chart A when the statement's designated province is
Nova Scotia, else 0."""


FARM_AMOUNT_8_PE = CATALOG.declare("farm_amount_8_pe", Decimal)
"""Amount 8 of the statement in Prince Edward Island, Form T2043 Part 2 line 67092 "Add all farming
expenses in PE from amount 8 of Chart A.": amount 8 of Chart A when the statement's designated
province is Prince Edward Island, else 0."""


FARM_AMOUNT_8_NL = CATALOG.declare("farm_amount_8_nl", Decimal)
"""Amount 8 of the statement in Newfoundland and Labrador, Form T2043 Part 2 line 67093 "Add all
farming expenses in NL from amount 8 of Chart A.": amount 8 of Chart A when the statement's
designated province is Newfoundland and Labrador, else 0."""


FARM_AMOUNT_8_NB = CATALOG.declare("farm_amount_8_nb", Decimal)
"""Amount 8 of the statement in New Brunswick, Form T2043 Part 2 line 67094 "Add all farming
expenses in NB from amount 8 of Chart A.": amount 8 of Chart A when the statement's designated
province is New Brunswick, else 0."""

FARM_CHART_B_TOTAL_GROSS_INCOME = CATALOG.declare(
    "farm_chart_b_total_gross_income", Decimal, non_negative=True
)
"""Total gross income of the farming business, Form T2043 Chart B row 2 "Total gross income ($) of
the farming business in all provinces and territories (line 9659 of Form T2042, excluding the
credit). See note 6.": the statement's line 9659 (the gross income of Form T2042 Part 3 excluding
the credit), the denominator of the row 3 percentages. Line 67075 of Part 3 adds it over the
statements."""

FARM_CHART_B_TOTAL_SALARIES = CATALOG.declare(
    "farm_chart_b_total_salaries", Decimal, non_negative=True
)
"""Total salaries and wages of the farming business, Form T2043 Chart B row 5 "Total salaries and
wages paid ($) to employees of the farming business in all provinces and territories (line 9814
of Form T2042). See note 8.": the statement's line 9814, the denominator of the row 6
percentages. Line 67076 of Part 3 adds it over the statements."""

FARM_CHART_B_IN_USE = CATALOG.declare("farm_chart_b_in_use", int, non_negative=True)
"""Use of Chart B by the statement, Form T2043 "Fill in a separate Chart B for each farming business
with one or more permanent establishments in more than one province or territory, where at least
one province is a designated province": 1 when any total of rows 1 or 4 for a designated
province is more than 0, else 0, a count. Part 3 adds rows 2 and 5 only of the statements that
fill in a Chart B ("row 2 of every Chart B you fill in")."""

FARM_PRESENT_IN_PROVINCE_ON = CATALOG.declare("farm_present_in_province_on", int, non_negative=True)
"""Statement present in Ontario, Form T2043 box 67062 "Tick this box if you have multiple farming
businesses with one or more permanent establishments in multiple provinces or territories.": 1
when the statement's designated province is Ontario and no Chart B is in use, or its Chart B has
a row 1 or row 4 amount for it, else 0, a count."""

FARM_PRESENT_IN_PROVINCE_MB = CATALOG.declare("farm_present_in_province_mb", int, non_negative=True)
"""Statement present in Manitoba, Form T2043 box 67062 "Tick this box if you have multiple farming
businesses with one or more permanent establishments in multiple provinces or territories.": 1
when the statement's designated province is Manitoba and no Chart B is in use, or its Chart B
has a row 1 or row 4 amount for it, else 0, a count."""

FARM_PRESENT_IN_PROVINCE_SK = CATALOG.declare("farm_present_in_province_sk", int, non_negative=True)
"""Statement present in Saskatchewan, Form T2043 box 67062 "Tick this box if you have multiple
farming businesses with one or more permanent establishments in multiple provinces or
territories.": 1 when the statement's designated province is Saskatchewan and no Chart B is in
use, or its Chart B has a row 1 or row 4 amount for it, else 0, a count."""

FARM_PRESENT_IN_PROVINCE_AB = CATALOG.declare("farm_present_in_province_ab", int, non_negative=True)
"""Statement present in Alberta, Form T2043 box 67062 "Tick this box if you have multiple farming
businesses with one or more permanent establishments in multiple provinces or territories.": 1
when the statement's designated province is Alberta and no Chart B is in use, or its Chart B has
a row 1 or row 4 amount for it, else 0, a count."""

FARM_PRESENT_IN_PROVINCE_NS = CATALOG.declare("farm_present_in_province_ns", int, non_negative=True)
"""Statement present in Nova Scotia, Form T2043 box 67062 "Tick this box if you have multiple
farming businesses with one or more permanent establishments in multiple provinces or
territories.": 1 when the statement's designated province is Nova Scotia and no Chart B is in
use, or its Chart B has a row 1 or row 4 amount for it, else 0, a count."""

FARM_PRESENT_IN_PROVINCE_PE = CATALOG.declare("farm_present_in_province_pe", int, non_negative=True)
"""Statement present in Prince Edward Island, Form T2043 box 67062 "Tick this box if you have
multiple farming businesses with one or more permanent establishments in multiple provinces or
territories.": 1 when the statement's designated province is Prince Edward Island and no Chart B
is in use, or its Chart B has a row 1 or row 4 amount for it, else 0, a count."""

FARM_PRESENT_IN_PROVINCE_NL = CATALOG.declare("farm_present_in_province_nl", int, non_negative=True)
"""Statement present in Newfoundland and Labrador, Form T2043 box 67062 "Tick this box if you have
multiple farming businesses with one or more permanent establishments in multiple provinces or
territories.": 1 when the statement's designated province is Newfoundland and Labrador and no
Chart B is in use, or its Chart B has a row 1 or row 4 amount for it, else 0, a count."""

FARM_PRESENT_IN_PROVINCE_NB = CATALOG.declare("farm_present_in_province_nb", int, non_negative=True)
"""Statement present in New Brunswick, Form T2043 box 67062 "Tick this box if you have multiple
farming businesses with one or more permanent establishments in multiple provinces or
territories.": 1 when the statement's designated province is New Brunswick and no Chart B is in
use, or its Chart B has a row 1 or row 4 amount for it, else 0, a count."""

FARM_PRESENT_OUTSIDE_EIGHT = CATALOG.declare("farm_present_outside_eight", int, non_negative=True)
"""Statement present outside the eight designated provinces, Form T2043 box 67062 "Tick this box if
you have multiple farming businesses with one or more permanent establishments in multiple
provinces or territories.": 1 when the statement's designated province is code 0 and no Chart B
is in use, else 0, a count."""

FARM_PRESENT_AMOUNT_ON = CATALOG.declare("farm_present_amount_on", Decimal, non_negative=True)
"""Statement present in Ontario counted once, Form T2043 box 67062 "Tick this box if you have
multiple farming businesses with one or more permanent establishments in multiple provinces or
territories.": the statement counted, "1", once for each count of 1 of its presence in this
place, so 1 for a statement present in it and 0 for any other; one record for each statement,
totalled by Form T2043."""

FARM_PRESENT_AMOUNT_MB = CATALOG.declare("farm_present_amount_mb", Decimal, non_negative=True)
"""Statement present in Manitoba counted once, Form T2043 box 67062 "Tick this box if you have
multiple farming businesses with one or more permanent establishments in multiple provinces or
territories.": the statement counted, "1", once for each count of 1 of its presence in this
place, so 1 for a statement present in it and 0 for any other; one record for each statement,
totalled by Form T2043."""

FARM_PRESENT_AMOUNT_SK = CATALOG.declare("farm_present_amount_sk", Decimal, non_negative=True)
"""Statement present in Saskatchewan counted once, Form T2043 box 67062 "Tick this box if you have
multiple farming businesses with one or more permanent establishments in multiple provinces or
territories.": the statement counted, "1", once for each count of 1 of its presence in this
place, so 1 for a statement present in it and 0 for any other; one record for each statement,
totalled by Form T2043."""

FARM_PRESENT_AMOUNT_AB = CATALOG.declare("farm_present_amount_ab", Decimal, non_negative=True)
"""Statement present in Alberta counted once, Form T2043 box 67062 "Tick this box if you have
multiple farming businesses with one or more permanent establishments in multiple provinces or
territories.": the statement counted, "1", once for each count of 1 of its presence in this
place, so 1 for a statement present in it and 0 for any other; one record for each statement,
totalled by Form T2043."""

FARM_PRESENT_AMOUNT_NS = CATALOG.declare("farm_present_amount_ns", Decimal, non_negative=True)
"""Statement present in Nova Scotia counted once, Form T2043 box 67062 "Tick this box if you have
multiple farming businesses with one or more permanent establishments in multiple provinces or
territories.": the statement counted, "1", once for each count of 1 of its presence in this
place, so 1 for a statement present in it and 0 for any other; one record for each statement,
totalled by Form T2043."""

FARM_PRESENT_AMOUNT_PE = CATALOG.declare("farm_present_amount_pe", Decimal, non_negative=True)
"""Statement present in Prince Edward Island counted once, Form T2043 box 67062 "Tick this box if
you have multiple farming businesses with one or more permanent establishments in multiple
provinces or territories.": the statement counted, "1", once for each count of 1 of its presence
in this place, so 1 for a statement present in it and 0 for any other; one record for each
statement, totalled by Form T2043."""

FARM_PRESENT_AMOUNT_NL = CATALOG.declare("farm_present_amount_nl", Decimal, non_negative=True)
"""Statement present in Newfoundland and Labrador counted once, Form T2043 box 67062 "Tick this box
if you have multiple farming businesses with one or more permanent establishments in multiple
provinces or territories.": the statement counted, "1", once for each count of 1 of its presence
in this place, so 1 for a statement present in it and 0 for any other; one record for each
statement, totalled by Form T2043."""

FARM_PRESENT_AMOUNT_NB = CATALOG.declare("farm_present_amount_nb", Decimal, non_negative=True)
"""Statement present in New Brunswick counted once, Form T2043 box 67062 "Tick this box if you have
multiple farming businesses with one or more permanent establishments in multiple provinces or
territories.": the statement counted, "1", once for each count of 1 of its presence in this
place, so 1 for a statement present in it and 0 for any other; one record for each statement,
totalled by Form T2043."""

FARM_PRESENT_AMOUNT_OUTSIDE_EIGHT = CATALOG.declare(
    "farm_present_amount_outside_eight", Decimal, non_negative=True
)
"""Statement present outside the eight designated provinces counted once, Form T2043 box 67062
"Tick this box if you have multiple farming businesses with one or more permanent establishments
in multiple provinces or territories.": the statement counted, "1", once for each count of 1 of
its presence in this place, so 1 for a statement present in it and 0 for any other; one record
for each statement, totalled by Form T2043."""

FARM_CHART_B_ROW_2_WHEN_IN_USE = CATALOG.declare(
    "farm_chart_b_row_2_when_in_use", Decimal, non_negative=True
)
"""Row 2 of Chart B when the statement uses Chart B, Form T2043 Part 3 line 67075 "Total gross
income in all provinces and territories from all farming businesses: Add the amount from row 2 of
every Chart B you fill in": row 2 times the use of Chart B, so 0 for a statement that fills in no
Chart B."""

FARM_CHART_B_ROW_5_WHEN_IN_USE = CATALOG.declare(
    "farm_chart_b_row_5_when_in_use", Decimal, non_negative=True
)
"""Row 5 of Chart B when the statement uses Chart B, Form T2043 Part 3 line 67076 "Total salaries
and wages paid to employees in all provinces and territories from all farming businesses: Add the
amount from row 5 of every Chart B you fill in": row 5 times the use of Chart B, so 0 for a
statement that fills in no Chart B."""

FARM_CHART_B_NOTE_9_APPLIES = CATALOG.declare("farm_chart_b_note_9_applies", int, non_negative=True)
"""Form T2043 Chart B note 9 "If either the total gross income from row 2 or the total salaries and
wages from row 5 is zero, do not multiply row 7 by 50%.": 1 when the total gross income (row 2) or
the total salaries and wages (row 5) is zero, else 0, a count. Row 8 is then 100% of row 7 rather
than 50%."""

FARM_CHART_B_ROW_8_PERCENTAGE = CATALOG.declare(
    "farm_chart_b_row_8_percentage", Decimal, non_negative=True
)
"""Percentage of row 7 kept at row 8, Form T2043 Chart B row 8 "Percentage (%) of expenses allocated
to the designated province. Row 7 multiplied by 50%. See note 9.": 50 when note 9 does not apply
and 100 when it does (50 means 50%)."""

FARM_CHART_B_ROW_3_ON = CATALOG.declare("farm_chart_b_row_3_on", Decimal, non_negative=True)
"""Ontario, Form T2043 Chart B row 3 "Percentage (%) of gross income allocated to the designated
province. Row 1 divided by row 2": the percentage of the statement's gross income allocated to
Ontario."""

FARM_CHART_B_ROW_6_ON = CATALOG.declare("farm_chart_b_row_6_on", Decimal, non_negative=True)
"""Ontario, Form T2043 Chart B row 6 "Percentage (%) of salaries and wages allocated to the
designated province. Row 4 divided by row 5": the percentage of the statement's salaries and
wages allocated to Ontario."""

FARM_CHART_B_ROW_7_ON = CATALOG.declare("farm_chart_b_row_7_on", Decimal, non_negative=True)
"""Ontario, Form T2043 Chart B row 7 "Total percentage (%) of expenses. Row 3 plus row 6": the total
percentage of expenses for Ontario."""

FARM_CHART_B_ROW_8_ON = CATALOG.declare("farm_chart_b_row_8_on", Decimal, non_negative=True)
"""Ontario, Form T2043 Chart B row 8 "Percentage (%) of expenses allocated to the designated
province. Row 7 multiplied by 50%. See note 9.": the percentage of expenses allocated to Ontario,
as a percent."""

FARM_CHART_B_ROW_9_ON = CATALOG.declare("farm_chart_b_row_9_on", Decimal)
"""Ontario, Form T2043 Chart B row 9 "Eligible farming expenses ($) of the farming business
allocated to the designated province. Row 8 multiplied by amount 6 of Chart A for this business":
the eligible farming expenses allocated to Ontario."""

FARM_CHART_B_ROW_11_ON = CATALOG.declare("farm_chart_b_row_11_on", Decimal)
"""Ontario, Form T2043 Chart B row 11 "Portion of eligible farming expenses of the farming business
allocated to the designated province attributed to the 2024 calendar year. Row 9 multiplied by row
10": the eligible farming expenses of Ontario for the 2024 calendar year."""

FARM_CHART_C_AMOUNT_ON = CATALOG.declare("farm_chart_c_amount_on", Decimal)
"""Ontario, Form T2043 Chart C amount 7 "Eligible farming expenses in ON from row 11 of Chart B. Add
amount 7 at amount 4A" times the ON payment rate 0.229%, rounded half-up to the cent."""

FARM_CHART_B_ROW_3_MB = CATALOG.declare("farm_chart_b_row_3_mb", Decimal, non_negative=True)
"""Manitoba, Form T2043 Chart B row 3 "Percentage (%) of gross income allocated to the designated
province. Row 1 divided by row 2": the percentage of the statement's gross income allocated to
Manitoba."""

FARM_CHART_B_ROW_6_MB = CATALOG.declare("farm_chart_b_row_6_mb", Decimal, non_negative=True)
"""Manitoba, Form T2043 Chart B row 6 "Percentage (%) of salaries and wages allocated to the
designated province. Row 4 divided by row 5": the percentage of the statement's salaries and
wages allocated to Manitoba."""

FARM_CHART_B_ROW_7_MB = CATALOG.declare("farm_chart_b_row_7_mb", Decimal, non_negative=True)
"""Manitoba, Form T2043 Chart B row 7 "Total percentage (%) of expenses. Row 3 plus row 6": the
total percentage of expenses for Manitoba."""

FARM_CHART_B_ROW_8_MB = CATALOG.declare("farm_chart_b_row_8_mb", Decimal, non_negative=True)
"""Manitoba, Form T2043 Chart B row 8 "Percentage (%) of expenses allocated to the designated
province. Row 7 multiplied by 50%. See note 9.": the percentage of expenses allocated to
Manitoba, as a percent."""

FARM_CHART_B_ROW_9_MB = CATALOG.declare("farm_chart_b_row_9_mb", Decimal)
"""Manitoba, Form T2043 Chart B row 9 "Eligible farming expenses ($) of the farming business
allocated to the designated province. Row 8 multiplied by amount 6 of Chart A for this business":
the eligible farming expenses allocated to Manitoba."""

FARM_CHART_B_ROW_11_MB = CATALOG.declare("farm_chart_b_row_11_mb", Decimal)
"""Manitoba, Form T2043 Chart B row 11 "Portion of eligible farming expenses of the farming business
allocated to the designated province attributed to the 2024 calendar year. Row 9 multiplied by row
10": the eligible farming expenses of Manitoba for the 2024 calendar year."""

FARM_CHART_C_AMOUNT_MB = CATALOG.declare("farm_chart_c_amount_mb", Decimal)
"""Manitoba, Form T2043 Chart C amount 8 "Eligible farming expenses in MB from row 11 of Chart B.
Add amount 8 at amount 4B" times the MB payment rate 0.229%, rounded half-up to the cent."""

FARM_CHART_B_ROW_3_SK = CATALOG.declare("farm_chart_b_row_3_sk", Decimal, non_negative=True)
"""Saskatchewan, Form T2043 Chart B row 3 "Percentage (%) of gross income allocated to the
designated province. Row 1 divided by row 2": the percentage of the statement's gross income
allocated to Saskatchewan."""

FARM_CHART_B_ROW_6_SK = CATALOG.declare("farm_chart_b_row_6_sk", Decimal, non_negative=True)
"""Saskatchewan, Form T2043 Chart B row 6 "Percentage (%) of salaries and wages allocated to the
designated province. Row 4 divided by row 5": the percentage of the statement's salaries and wages
allocated to Saskatchewan."""

FARM_CHART_B_ROW_7_SK = CATALOG.declare("farm_chart_b_row_7_sk", Decimal, non_negative=True)
"""Saskatchewan, Form T2043 Chart B row 7 "Total percentage (%) of expenses. Row 3 plus row 6": the
total percentage of expenses for Saskatchewan."""

FARM_CHART_B_ROW_8_SK = CATALOG.declare("farm_chart_b_row_8_sk", Decimal, non_negative=True)
"""Saskatchewan, Form T2043 Chart B row 8 "Percentage (%) of expenses allocated to the designated
province. Row 7 multiplied by 50%. See note 9.": the percentage of expenses allocated to
Saskatchewan, as a percent."""

FARM_CHART_B_ROW_9_SK = CATALOG.declare("farm_chart_b_row_9_sk", Decimal)
"""Saskatchewan, Form T2043 Chart B row 9 "Eligible farming expenses ($) of the farming business
allocated to the designated province. Row 8 multiplied by amount 6 of Chart A for this business":
the eligible farming expenses allocated to Saskatchewan."""

FARM_CHART_B_ROW_11_SK = CATALOG.declare("farm_chart_b_row_11_sk", Decimal)
"""Saskatchewan, Form T2043 Chart B row 11 "Portion of eligible farming expenses of the farming
business allocated to the designated province attributed to the 2024 calendar year. Row 9 multiplied
by row 10": the eligible farming expenses of Saskatchewan for the 2024 calendar year."""

FARM_CHART_C_AMOUNT_SK = CATALOG.declare("farm_chart_c_amount_sk", Decimal)
"""Saskatchewan, Form T2043 Chart C amount 9 "Eligible farming expenses in SK from row 11 of Chart
B. Add amount 9 at amount 4C" times the SK payment rate 0.229%, rounded half-up to the cent."""

FARM_CHART_B_ROW_3_AB = CATALOG.declare("farm_chart_b_row_3_ab", Decimal, non_negative=True)
"""Alberta, Form T2043 Chart B row 3 "Percentage (%) of gross income allocated to the designated
province. Row 1 divided by row 2": the percentage of the statement's gross income allocated to
Alberta."""

FARM_CHART_B_ROW_6_AB = CATALOG.declare("farm_chart_b_row_6_ab", Decimal, non_negative=True)
"""Alberta, Form T2043 Chart B row 6 "Percentage (%) of salaries and wages allocated to the
designated province. Row 4 divided by row 5": the percentage of the statement's salaries and
wages allocated to Alberta."""

FARM_CHART_B_ROW_7_AB = CATALOG.declare("farm_chart_b_row_7_ab", Decimal, non_negative=True)
"""Alberta, Form T2043 Chart B row 7 "Total percentage (%) of expenses. Row 3 plus row 6": the total
percentage of expenses for Alberta."""

FARM_CHART_B_ROW_8_AB = CATALOG.declare("farm_chart_b_row_8_ab", Decimal, non_negative=True)
"""Alberta, Form T2043 Chart B row 8 "Percentage (%) of expenses allocated to the designated
province. Row 7 multiplied by 50%. See note 9.": the percentage of expenses allocated to Alberta,
as a percent."""

FARM_CHART_B_ROW_9_AB = CATALOG.declare("farm_chart_b_row_9_ab", Decimal)
"""Alberta, Form T2043 Chart B row 9 "Eligible farming expenses ($) of the farming business
allocated to the designated province. Row 8 multiplied by amount 6 of Chart A for this business":
the eligible farming expenses allocated to Alberta."""

FARM_CHART_B_ROW_11_AB = CATALOG.declare("farm_chart_b_row_11_ab", Decimal)
"""Alberta, Form T2043 Chart B row 11 "Portion of eligible farming expenses of the farming business
allocated to the designated province attributed to the 2024 calendar year. Row 9 multiplied by row
10": the eligible farming expenses of Alberta for the 2024 calendar year."""

FARM_CHART_C_AMOUNT_AB = CATALOG.declare("farm_chart_c_amount_ab", Decimal)
"""Alberta, Form T2043 Chart C amount 10 "Eligible farming expenses in AB from row 11 of Chart B.
Add amount 10 at amount 4D" times the AB payment rate 0.229%, rounded half-up to the cent."""

FARM_CHART_B_ROW_3_NS = CATALOG.declare("farm_chart_b_row_3_ns", Decimal, non_negative=True)
"""Nova Scotia, Form T2043 Chart B row 3 "Percentage (%) of gross income allocated to the designated
province. Row 1 divided by row 2": the percentage of the statement's gross income allocated to Nova
Scotia."""

FARM_CHART_B_ROW_6_NS = CATALOG.declare("farm_chart_b_row_6_ns", Decimal, non_negative=True)
"""Nova Scotia, Form T2043 Chart B row 6 "Percentage (%) of salaries and wages allocated to the
designated province. Row 4 divided by row 5": the percentage of the statement's salaries and wages
allocated to Nova Scotia."""

FARM_CHART_B_ROW_7_NS = CATALOG.declare("farm_chart_b_row_7_ns", Decimal, non_negative=True)
"""Nova Scotia, Form T2043 Chart B row 7 "Total percentage (%) of expenses. Row 3 plus row 6": the
total percentage of expenses for Nova Scotia."""

FARM_CHART_B_ROW_8_NS = CATALOG.declare("farm_chart_b_row_8_ns", Decimal, non_negative=True)
"""Nova Scotia, Form T2043 Chart B row 8 "Percentage (%) of expenses allocated to the designated
province. Row 7 multiplied by 50%. See note 9.": the percentage of expenses allocated to Nova
Scotia, as a percent."""

FARM_CHART_B_ROW_9_NS = CATALOG.declare("farm_chart_b_row_9_ns", Decimal)
"""Nova Scotia, Form T2043 Chart B row 9 "Eligible farming expenses ($) of the farming business
allocated to the designated province. Row 8 multiplied by amount 6 of Chart A for this business":
the eligible farming expenses allocated to Nova Scotia."""

FARM_CHART_B_ROW_11_NS = CATALOG.declare("farm_chart_b_row_11_ns", Decimal)
"""Nova Scotia, Form T2043 Chart B row 11 "Portion of eligible farming expenses of the farming
business allocated to the designated province attributed to the 2024 calendar year. Row 9
multiplied by row 10": the eligible farming expenses of Nova Scotia for the 2024 calendar year."""

FARM_CHART_C_AMOUNT_NS = CATALOG.declare("farm_chart_c_amount_ns", Decimal)
"""Nova Scotia, Form T2043 Chart C amount 11 "Eligible farming expenses in NS from row 11 of Chart
B. Add amount 11 at amount 4E" times the NS payment rate 0.229%, rounded half-up to the cent."""

FARM_CHART_B_ROW_3_PE = CATALOG.declare("farm_chart_b_row_3_pe", Decimal, non_negative=True)
"""Prince Edward Island, Form T2043 Chart B row 3 "Percentage (%) of gross income allocated to the
designated province. Row 1 divided by row 2": the percentage of the statement's gross income
allocated to Prince Edward Island."""

FARM_CHART_B_ROW_6_PE = CATALOG.declare("farm_chart_b_row_6_pe", Decimal, non_negative=True)
"""Prince Edward Island, Form T2043 Chart B row 6 "Percentage (%) of salaries and wages allocated to
the designated province. Row 4 divided by row 5": the percentage of the statement's salaries and
wages allocated to Prince Edward Island."""

FARM_CHART_B_ROW_7_PE = CATALOG.declare("farm_chart_b_row_7_pe", Decimal, non_negative=True)
"""Prince Edward Island, Form T2043 Chart B row 7 "Total percentage (%) of expenses. Row 3 plus row
6": the total percentage of expenses for Prince Edward Island."""

FARM_CHART_B_ROW_8_PE = CATALOG.declare("farm_chart_b_row_8_pe", Decimal, non_negative=True)
"""Prince Edward Island, Form T2043 Chart B row 8 "Percentage (%) of expenses allocated to the
designated province. Row 7 multiplied by 50%. See note 9.": the percentage of expenses allocated to
Prince Edward Island, as a percent."""

FARM_CHART_B_ROW_9_PE = CATALOG.declare("farm_chart_b_row_9_pe", Decimal)
"""Prince Edward Island, Form T2043 Chart B row 9 "Eligible farming expenses ($) of the farming
business allocated to the designated province. Row 8 multiplied by amount 6 of Chart A for this
business": the eligible farming expenses allocated to Prince Edward Island."""

FARM_CHART_B_ROW_11_PE = CATALOG.declare("farm_chart_b_row_11_pe", Decimal)
"""Prince Edward Island, Form T2043 Chart B row 11 "Portion of eligible farming expenses of the
farming business allocated to the designated province attributed to the 2024 calendar year. Row 9
multiplied by row 10": the eligible farming expenses of Prince Edward Island for the 2024
calendar year."""

FARM_CHART_C_AMOUNT_PE = CATALOG.declare("farm_chart_c_amount_pe", Decimal)
"""Prince Edward Island, Form T2043 Chart C amount 12 "Eligible farming expenses in PE from row 11
of Chart B. Add amount 12 at amount 4F" times the PE payment rate 0.229%, rounded half-up to the
cent."""

FARM_CHART_B_ROW_3_NL = CATALOG.declare("farm_chart_b_row_3_nl", Decimal, non_negative=True)
"""Newfoundland and Labrador, Form T2043 Chart B row 3 "Percentage (%) of gross income allocated to
the designated province. Row 1 divided by row 2": the percentage of the statement's gross income
allocated to Newfoundland and Labrador."""

FARM_CHART_B_ROW_6_NL = CATALOG.declare("farm_chart_b_row_6_nl", Decimal, non_negative=True)
"""Newfoundland and Labrador, Form T2043 Chart B row 6 "Percentage (%) of salaries and wages
allocated to the designated province. Row 4 divided by row 5": the percentage of the statement's
salaries and wages allocated to Newfoundland and Labrador."""

FARM_CHART_B_ROW_7_NL = CATALOG.declare("farm_chart_b_row_7_nl", Decimal, non_negative=True)
"""Newfoundland and Labrador, Form T2043 Chart B row 7 "Total percentage (%) of expenses. Row 3 plus
row 6": the total percentage of expenses for Newfoundland and Labrador."""

FARM_CHART_B_ROW_8_NL = CATALOG.declare("farm_chart_b_row_8_nl", Decimal, non_negative=True)
"""Newfoundland and Labrador, Form T2043 Chart B row 8 "Percentage (%) of expenses allocated to the
designated province. Row 7 multiplied by 50%. See note 9.": the percentage of expenses allocated to
Newfoundland and Labrador, as a percent."""

FARM_CHART_B_ROW_9_NL = CATALOG.declare("farm_chart_b_row_9_nl", Decimal)
"""Newfoundland and Labrador, Form T2043 Chart B row 9 "Eligible farming expenses ($) of the farming
business allocated to the designated province. Row 8 multiplied by amount 6 of Chart A for this
business": the eligible farming expenses allocated to Newfoundland and Labrador."""

FARM_CHART_B_ROW_11_NL = CATALOG.declare("farm_chart_b_row_11_nl", Decimal)
"""Newfoundland and Labrador, Form T2043 Chart B row 11 "Portion of eligible farming expenses of the
farming business allocated to the designated province attributed to the 2024 calendar year. Row 9
multiplied by row 10": the eligible farming expenses of Newfoundland and Labrador for the 2024
calendar year."""

FARM_CHART_C_AMOUNT_NL = CATALOG.declare("farm_chart_c_amount_nl", Decimal)
"""Newfoundland and Labrador, Form T2043 Chart C amount 13 "Eligible farming expenses in NL from row
11 of Chart B. Add amount 13 at amount 4G" times the NL payment rate 0.229%, rounded half-up to
the cent."""

FARM_CHART_B_ROW_3_NB = CATALOG.declare("farm_chart_b_row_3_nb", Decimal, non_negative=True)
"""New Brunswick, Form T2043 Chart B row 3 "Percentage (%) of gross income allocated to the
designated province. Row 1 divided by row 2": the percentage of the statement's gross income
allocated to New Brunswick."""

FARM_CHART_B_ROW_6_NB = CATALOG.declare("farm_chart_b_row_6_nb", Decimal, non_negative=True)
"""New Brunswick, Form T2043 Chart B row 6 "Percentage (%) of salaries and wages allocated to the
designated province. Row 4 divided by row 5": the percentage of the statement's salaries and wages
allocated to New Brunswick."""

FARM_CHART_B_ROW_7_NB = CATALOG.declare("farm_chart_b_row_7_nb", Decimal, non_negative=True)
"""New Brunswick, Form T2043 Chart B row 7 "Total percentage (%) of expenses. Row 3 plus row 6": the
total percentage of expenses for New Brunswick."""

FARM_CHART_B_ROW_8_NB = CATALOG.declare("farm_chart_b_row_8_nb", Decimal, non_negative=True)
"""New Brunswick, Form T2043 Chart B row 8 "Percentage (%) of expenses allocated to the designated
province. Row 7 multiplied by 50%. See note 9.": the percentage of expenses allocated to New
Brunswick, as a percent."""

FARM_CHART_B_ROW_9_NB = CATALOG.declare("farm_chart_b_row_9_nb", Decimal)
"""New Brunswick, Form T2043 Chart B row 9 "Eligible farming expenses ($) of the farming business
allocated to the designated province. Row 8 multiplied by amount 6 of Chart A for this business":
the eligible farming expenses allocated to New Brunswick."""

FARM_CHART_B_ROW_11_NB = CATALOG.declare("farm_chart_b_row_11_nb", Decimal)
"""New Brunswick, Form T2043 Chart B row 11 "Portion of eligible farming expenses of the farming
business allocated to the designated province attributed to the 2024 calendar year. Row 9 multiplied
by row 10": the eligible farming expenses of New Brunswick for the 2024 calendar year."""

FARM_CHART_C_AMOUNT_NB = CATALOG.declare("farm_chart_c_amount_nb", Decimal)
"""New Brunswick, Form T2043 Chart C amount 14 "Eligible farming expenses in NB from row 11 of Chart
B. Add amount 14 at amount 4H" times the NB payment rate 0.229%, rounded half-up to the cent."""

# Form T2121 (Statement of Fishing Activities), Parts 3 to 7 and Area A (T1 lines 14299 and 14300).
# Each kind is one line of the form; the caller's amounts are starting amounts, the rest are
# computed by the T2121 steps of the manifest part `03d_t2121.yaml`.

FISH_FISH_PRODUCTS = CATALOG.declare("fish_fish_products", Decimal, non_negative=True)
"""Fish products, Form T2121 line 3A "Fish products": a starting amount."""

FISH_OTHER_MARINE_PRODUCTS = CATALOG.declare(
    "fish_other_marine_products", Decimal, non_negative=True
)
"""Other marine products, Form T2121 line 3B "Other marine products": a starting amount."""

FISH_GRANTS_CREDITS_AND_REBATES = CATALOG.declare(
    "fish_grants_credits_and_rebates", Decimal, non_negative=True
)
"""Grants, credits and rebates of the fishing business, Form T2121 line 3C "Grants, credits, and
rebates": a starting amount."""

FISH_SUBSIDIES = CATALOG.declare("fish_subsidies", Decimal, non_negative=True)
"""Subsidies of the fishing business, Form T2121 line 3D "Subsidies": a starting amount."""

FISH_COMPENSATION_FOR_LOSS = CATALOG.declare(
    "fish_compensation_for_loss", Decimal, non_negative=True
)
"""Compensation for loss, Form T2121 line 3E "Compensation for loss of fishing income or
property": a starting amount."""

FISH_SHARESPERSON_INCOME = CATALOG.declare("fish_sharesperson_income", Decimal, non_negative=True)
"""Sharesperson income, Form T2121 line 3F "Sharesperson income (specify name of fishing boat and
captain below)": a starting amount."""

FISH_OTHER_INCOME = CATALOG.declare("fish_other_income", Decimal, non_negative=True)
"""Other fishing income, Form T2121 line 9600 "Other income (specify):": a starting amount, before
the recapture of Area A."""

FISH_SALT_BAIT_AND_ICE = CATALOG.declare("fish_salt_bait_and_ice", Decimal, non_negative=True)
"""Salt, bait and ice of the fishing business, Form T2121 line 9138 "Salt, bait, and ice": a
starting amount."""

FISH_CREW_SHARES = CATALOG.declare("fish_crew_shares", Decimal, non_negative=True)
"""Crew shares of the fishing business, Form T2121 line 9062 "Crew shares": a starting amount."""

FISH_FUEL_COSTS = CATALOG.declare("fish_fuel_costs", Decimal, non_negative=True)
"""Fuel costs of the fishing business, Form T2121 line 9224 "Fuel costs (except for motor
vehicles)": a starting amount."""

FISH_FISHING_GEAR = CATALOG.declare("fish_fishing_gear", Decimal, non_negative=True)
"""Fishing gear of the fishing business, Form T2121 line 9136 "Fishing gear": a starting amount."""

FISH_INSURANCE = CATALOG.declare("fish_insurance", Decimal, non_negative=True)
"""Insurance of the fishing business, Form T2121 line 8690 "Insurance": a starting amount."""

FISH_INTEREST_AND_BANK_CHARGES = CATALOG.declare(
    "fish_interest_and_bank_charges", Decimal, non_negative=True
)
"""Interest and bank charges of the fishing business, Form T2121 line 8710 "Interest and bank
charges": a starting amount."""

FISH_MEALS_AND_ENTERTAINMENT = CATALOG.declare(
    "fish_meals_and_entertainment", Decimal, non_negative=True
)
"""Meals and entertainment of the fishing business, Form T2121 line 8523 "Meals and
entertainment": a starting amount."""

FISH_BUSINESS_TAXES_LICENCES_AND_MEMBERSHIPS = CATALOG.declare(
    "fish_business_taxes_licences_and_memberships", Decimal, non_negative=True
)
"""Business taxes, licences and memberships of the fishing business, Form T2121 line 8760 "Business
taxes, licences, and memberships": a starting amount."""

FISH_MOTOR_VEHICLE_EXPENSES = CATALOG.declare(
    "fish_motor_vehicle_expenses", Decimal, non_negative=True
)
"""Motor vehicle expenses of the fishing business, Form T2121 line 9281 (amount 4J) "Motor vehicle
expenses (not including CCA) (amount 16 of Chart A)": amount 16 of Chart A, "Allowable motor vehicle
expenses: Add amounts 13 to 15 (enter this total on line 9281 of Part 4)"."""

FISH_VEHICLE_SALES_TAX_RATE = CATALOG.declare(
    "fish_vehicle_sales_tax_rate", Decimal, non_negative=True
)
"""GST plus PST, or HST, rate, Form T2121 Chart C "Use a GST rate of 5% or HST rate applicable to
your province.": the rate in percent, so 13 is 13% (5 plus 8 in a province with a PST of 8%, 5 where
only the GST applies), a starting amount."""

FISH_OFFICE_EXPENSES = CATALOG.declare("fish_office_expenses", Decimal, non_negative=True)
"""Office expenses of the fishing business, Form T2121 line 8810 "Office expenses": a starting
amount."""

FISH_NETS_AND_TRAPS = CATALOG.declare("fish_nets_and_traps", Decimal, non_negative=True)
"""Nets and traps of the fishing business, Form T2121 line 9137 "Nets and traps": a starting
amount."""

FISH_PROFESSIONAL_FEES = CATALOG.declare("fish_professional_fees", Decimal, non_negative=True)
"""Professional fees of the fishing business, Form T2121 line 8860 "Professional fees (includes
legal and accounting fees)": a starting amount."""

FISH_SALARIES_WAGES_AND_BENEFITS = CATALOG.declare(
    "fish_salaries_wages_and_benefits", Decimal, non_negative=True
)
"""Salaries, wages and benefits of the fishing business, Form T2121 line 9060 "Salaries, wages, and
benefits (including employer's contributions)": a starting amount."""

FISH_REPAIRS_FISHING_BOAT = CATALOG.declare("fish_repairs_fishing_boat", Decimal, non_negative=True)
"""Repairs and maintenance of the fishing boat, Form T2121 Part 4 amount 1 "Repairs and
maintenance: Fishing boat": a starting amount."""

FISH_REPAIRS_ENGINE = CATALOG.declare("fish_repairs_engine", Decimal, non_negative=True)
"""Repairs and maintenance of the engine, Form T2121 Part 4 amount 2 "Engine": a starting amount."""

FISH_REPAIRS_ELECTRICAL_EQUIPMENT = CATALOG.declare(
    "fish_repairs_electrical_equipment", Decimal, non_negative=True
)
"""Repairs and maintenance of the electrical equipment, Form T2121 Part 4 amount 3 "Electrical
equipment": a starting amount."""

FISH_INSURANCE_RECOVERY = CATALOG.declare("fish_insurance_recovery", Decimal, non_negative=True)
"""Insurance recovery of the repairs, Form T2121 Part 4 amount 5 "Insurance recovery": a starting
amount."""

FISH_OTHER_EXPENSES = CATALOG.declare("fish_other_expenses", Decimal, non_negative=True)
"""Other fishing expenses, Form T2121 line 9270 "Other expenses (specify):": a starting amount,
before the terminal loss of Area A."""

FISH_CCA_PERSONAL_PART = CATALOG.declare("fish_cca_personal_part", Decimal, non_negative=True)
"""Personal part of the fishing CCA, Form T2121 line 9936 "Capital cost allowance (CCA). Enter
amount ii of Area A minus any personal part and any CCA for business-use-of-home expenses": a
starting amount, the personal part."""

FISH_CCA_CLASSES = RecordListKind.declare(
    CATALOG,
    "fish_cca_classes",
    fields=(
        CCA_CLASS_NUMBER,
        CCA_UCC_AT_START,
        CCA_ADDITIONS,
        CCA_DIEP_ADDITIONS,
        CCA_PROCEEDS,
        CCA_DIEP_PROCEEDS,
        CCA_IMMEDIATE_EXPENSING,
        CCA_AIIP_ADDITIONS,
        CCA_RIIP_ADDITIONS,
        CCA_CLAIMED,
        CCA_NO_PROPERTY_LEFT,
        CCA_PERSONAL_PART_REMAINING,
        CCA_HALF_YEAR_RULE_DIFFERS,
        CCA_RATE_ELECTION,
        CCA_VEHICLE_ACQUIRED_YEAR,
        CCA_VEHICLE_COST,
        CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
        CCA_SOLD_ZEPVS,
    ),
)
"""Fishing classes, Form T2121 Area A "Calculation of capital cost allowance (CCA) claim": a
starting list with one record for each class, holding the columns the filer enters (class
number, UCC at the start of the year, additions, the DIEP part of the additions, proceeds, the
proceeds of DIEPs, the immediate expensing amount, the AIIP and RIIP parts of the additions, the
CCA claimed), whether any property is left in the class, the remaining personal part of a
property used for both personal and business use (endnote 9), whether the additions are treated the
opposite way from their class for the half-year rule (column 18), and the CCA rate the
caller elects for it (a purpose-built rental or a building in a separate class), then
the year the vehicle was acquired, its actual cost and the government assistance for it
(endnote 2), then the vehicles sold from a Class 54 row, last."""

FISH_CCA_CLASSES_ADJUSTED = RecordListKind.declare(
    CATALOG,
    "fish_cca_classes_adjusted",
    fields=tuple(
        field
        for field in FISH_CCA_CLASSES.fields
        if field
        not in (
            CCA_VEHICLE_ACQUIRED_YEAR,
            CCA_VEHICLE_COST,
            CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
            CCA_SOLD_ZEPVS,
        )
    ),
)
"""Fishing classes with the proceeds adjusted, Form T2121 Area A endnote 2: "The proceeds of
disposition of [...] a passenger vehicle bought after April 18, 2021, that has been included in
Class 10.1, and whose cost is more than the prescribed amount will be adjusted based on a factor
equal to its prescribed amount as a proportion of the actual cost of the vehicle". The list of
fishing classes without the year the vehicle was acquired, its cost, the government
assistance and the vehicles sold from a Class 54 row, with columns 5 and 6 (the proceeds and the
proceeds of DIEPs) adjusted."""
FISH_CCA_CLASSES_CHECKED = RecordListKind.declare(
    CATALOG,
    "fish_cca_classes_checked",
    fields=FISH_CCA_CLASSES.fields,
)
"""Fishing classes checked, Form T2121 Area A "Calculation of capital cost allowance (CCA) claim":
the list of the fishing classes with the cost of additions of each Class 10.1 passenger vehicle
checked, that is, not more than its limit with tax (Guide T4002 2025, "Class 10.1 (30%)"). The rows
are passed on unchanged, with the same fields as the list they check."""


FISH_PARTNER = CATALOG.declare("fish_partner", int, non_negative=True)
"""Whether the filer is a partner in the fishing business, Form T2121 amount 5A "Your share of line
9369 or the amount from your T5013 slip, Statement of Partnership Income": 1 for a partner, 0
otherwise, a starting count."""

FISH_PARTNER_CHECKED = CATALOG.declare("fish_partner_checked", int, non_negative=True)
"""Whether the filer is a partner in the fishing business, Form T2121 amount 5A "Your share of line
9369 or the amount from your T5013 slip, Statement of Partnership Income": the answer of
`ca/fish_partner` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a count of 1 or 0. A
count of 2 or more is refused, not capped."""

FISH_PARTNER_SHARE = CATALOG.declare("fish_partner_share", Decimal)
"""Partner's share of the fishing net income, Form T2121 amount 5A "Your share of line 9369 or the
amount from your T5013 slip, Statement of Partnership Income": a starting amount, signed."""

FISH_PARTNER_GST_HST_REBATE = CATALOG.declare("fish_partner_gst_hst_rebate", Decimal)
"""GST/HST rebate for partners, Form T2121 line 9974 "GST/HST rebate for partners received in the
year": a starting amount."""

FISH_PARTNER_OTHER_AMOUNT_A = CATALOG.declare(
    "fish_partner_other_amount_a", Decimal, non_negative=True
)
"""Partner expense 1, Form T2121 amount 6A "List details of expenses: Expense amounts": a starting
amount among the five lines of Part 6."""

FISH_PARTNER_OTHER_AMOUNT_B = CATALOG.declare(
    "fish_partner_other_amount_b", Decimal, non_negative=True
)
"""Partner expense 2, Form T2121 amount 6B "List details of expenses: Expense amounts": a starting
amount among the five lines of Part 6."""

FISH_PARTNER_OTHER_AMOUNT_C = CATALOG.declare(
    "fish_partner_other_amount_c", Decimal, non_negative=True
)
"""Partner expense 3, Form T2121 amount 6C "List details of expenses: Expense amounts": a starting
amount among the five lines of Part 6."""

FISH_PARTNER_OTHER_AMOUNT_D = CATALOG.declare(
    "fish_partner_other_amount_d", Decimal, non_negative=True
)
"""Partner expense 4, Form T2121 amount 6D "List details of expenses: Expense amounts": a starting
amount among the five lines of Part 6."""

FISH_PARTNER_OTHER_AMOUNT_E = CATALOG.declare(
    "fish_partner_other_amount_e", Decimal, non_negative=True
)
"""Partner expense 5, Form T2121 amount 6E "List details of expenses: Expense amounts": a starting
amount among the five lines of Part 6."""

FISH_HOME_HEAT = CATALOG.declare("fish_home_heat", Decimal, non_negative=True)
"""Heat for the business use of the home, Form T2121 amount 7A "Heat": a starting amount."""

FISH_HOME_ELECTRICITY = CATALOG.declare("fish_home_electricity", Decimal, non_negative=True)
"""Electricity for the business use of the home, Form T2121 amount 7B "Electricity": a starting
amount."""

FISH_HOME_INSURANCE = CATALOG.declare("fish_home_insurance", Decimal, non_negative=True)
"""Insurance for the business use of the home, Form T2121 amount 7C "Insurance": a starting
amount."""

FISH_HOME_MAINTENANCE = CATALOG.declare("fish_home_maintenance", Decimal, non_negative=True)
"""Maintenance for the business use of the home, Form T2121 amount 7D "Maintenance": a starting
amount."""

FISH_HOME_MORTGAGE_INTEREST = CATALOG.declare(
    "fish_home_mortgage_interest", Decimal, non_negative=True
)
"""Mortgage interest for the business use of the home, Form T2121 amount 7E "Mortgage interest": a
starting amount."""

FISH_HOME_PROPERTY_TAXES = CATALOG.declare("fish_home_property_taxes", Decimal, non_negative=True)
"""Property taxes for the business use of the home, Form T2121 amount 7F "Property taxes": a
starting amount."""

FISH_HOME_OTHER_EXPENSES = CATALOG.declare("fish_home_other_expenses", Decimal, non_negative=True)
"""Other home expenses for the business use of the home, Form T2121 amount 7G "Other expenses
(specify):": a starting amount."""

FISH_HOME_PERSONAL_USE_PART = CATALOG.declare(
    "fish_home_personal_use_part", Decimal, non_negative=True
)
"""Personal-use part of the business-use-of-home expenses, Form T2121 amount 7I "Personal-use part
of the business-use-of-home expenses": a starting amount."""

FISH_HOME_CCA = CATALOG.declare("fish_home_cca", Decimal, non_negative=True)
"""Capital cost allowance for the business part of the home, Form T2121 amount 7K "Capital cost
allowance (business part only), which means amount ii of Area A minus any portion of capital cost
allowance that is for personal use or entered on line 9936 of Part 4": a starting amount."""

FISH_HOME_CARRIED_FORWARD = CATALOG.declare("fish_home_carried_forward", Decimal, non_negative=True)
"""Home expenses carried forward from last year, Form T2121 amount 7L "Amount carried forward from
previous year": a starting amount."""

FISH_RECAPTURED_CCA = CATALOG.declare("fish_recaptured_cca", Decimal, non_negative=True)
"""Recapture of the fishing classes, Form T2121 Area A endnote 3 "If you have a negative amount in
column 7, add it to income as a recapture in Part 3 on line 9600": the recapture of each class
of the Area A list, totalled."""

FISH_OTHER_INCOME_WITH_RECAPTURE = CATALOG.declare(
    "fish_other_income_with_recapture", Decimal, non_negative=True
)
"""Other fishing income with the recapture, Form T2121 line 9600 "Other income (specify):": the
other income plus the recapture of Area A."""

FISH_GROSS_INCOME = CATALOG.declare("fish_gross_income", Decimal, non_negative=True)
"""Gross fishing income, Form T2121 line 8299 "Gross income: Total of amounts 3A to 3F and line
9600 (enter this amount on line 14299 of your income tax and benefit return)": the amounts 3A to
3F, with line 9600 and its recapture."""

FISH_GROSS_INCOME_BEFORE_EXPENSES = CATALOG.declare(
    "fish_gross_income_before_expenses", Decimal, non_negative=True
)
"""Gross fishing income before expenses, Form T2121 amount 4A "Gross income (line 8299 of Part
3)": line 8299."""

FISH_TERMINAL_LOSS = CATALOG.declare("fish_terminal_loss", Decimal, non_negative=True)
"""Terminal loss of the fishing classes, Form T2121 Area A endnote 3 "If no property is left in the
class and there is a positive amount in this column, deduct the amount from income as a terminal
loss in Part 4 on line 9270": the terminal loss of each class of the Area A list, totalled."""

FISH_OTHER_EXPENSES_WITH_TERMINAL_LOSS = CATALOG.declare(
    "fish_other_expenses_with_terminal_loss", Decimal, non_negative=True
)
"""Other fishing expenses with the terminal loss, Form T2121 line 9270 "Other expenses (specify):":
the other expenses plus the terminal loss of Area A."""

FISH_REPAIRS_TOTAL = CATALOG.declare("fish_repairs_total", Decimal, non_negative=True)
"""Total of the repairs and maintenance, Form T2121 Part 4 amount 4 "Total of amounts 1 to 3": the
three repairs amounts added."""

FISH_REPAIRS_YOUR_COST = CATALOG.declare("fish_repairs_your_cost", Decimal)
"""Your cost of the repairs, Form T2121 line 8963 "Your cost (amount 4 minus amount 5)", amount
4O: amount 4 less amount 5 (`fish_insurance_recovery`), as the form prints it."""

FISH_EXPENSES_SUBTOTAL = CATALOG.declare("fish_expenses_subtotal", Decimal)
"""Subtotal of fishing expenses, Form T2121 amount 4Q "Subtotal: Add amounts 4B to 4P.": the
expense lines 4B to 4N, amount 4O and the other expenses of line 9270 with the terminal loss;
signed, as amount 4O can be negative."""

FISH_CCA_TABLE_CLAIM = CATALOG.declare("fish_cca_table_claim", Decimal, non_negative=True)
"""CCA claim of the fishing classes, Form T2121 Area A amount ii "Total CCA claim for the year:
Total of column 21 (enter on line 9936 of Part 4 amount ii minus any personal part and any CCA
for business-use-of-home expenses)": the CCA claimed on each class, at most its maximum,
totalled."""

FISH_CCA_CLAIM_LESS_PERSONAL_PART = CATALOG.declare("fish_cca_claim_less_personal_part", Decimal)
"""Fishing CCA claim less the personal part, Form T2121 line 9936 "Capital cost allowance (CCA).
Enter amount ii of Area A minus any personal part and any CCA for business-use-of-home
expenses": the first step: amount ii less the personal part of CCA."""

FISH_CCA_CLAIM = CATALOG.declare("fish_cca_claim", Decimal)
"""CCA claim of the fishing business, Form T2121 line 9936 "Capital cost allowance (CCA). Enter
amount ii of Area A minus any personal part and any CCA for business-use-of-home expenses": the
second step: the first step less the CCA for business-use-of-home expenses (amount 7K)."""

FISH_TOTAL_EXPENSES = CATALOG.declare("fish_total_expenses", Decimal)
"""Total fishing expenses, Form T2121 line 9368 "Total expenses: Amount 4Q plus line 9936": amount
4Q plus line 9936."""

FISH_BOAT_MAINLY_PERSONAL = CATALOG.declare("fish_boat_mainly_personal", int, non_negative=True)
"""Whether the fishing boat was used mainly for personal use, Guide T4002 "Use of a fishing boat
mainly for personal use": "You may have used a fishing boat mainly for personal use, but sometimes
caught a small amount of fish to sell" (confirmed from the PDF; no .txt published): 1 if it was, 0
otherwise, a starting count of the filer's yes or no for each statement."""

FISH_BOAT_MAINLY_PERSONAL_CHECKED = CATALOG.declare(
    "fish_boat_mainly_personal_checked", int, non_negative=True
)
"""Whether the fishing boat was used mainly for personal use, Guide T4002 "Use of a fishing boat
mainly for personal use" (confirmed from the PDF; no .txt published): the answer of
`ca/fish_boat_mainly_personal` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a count
of 1 or 0. A count of 2 or more is refused, not capped."""

FISH_EXPENSES_LIMITED_TO_CATCH_INCOME = CATALOG.declare(
    "fish_expenses_limited_to_catch_income", Decimal
)
"""Expenses and CCA limited to the income from the catch, Guide T4002 "Use of a fishing boat mainly
for personal use" "the amount you deduct cannot be more than your income from the catch"
(confirmed from the PDF; no .txt published): the lesser of Form T2121 line 9368 and amount 4A,
signed like line 9368."""

FISH_TOTAL_EXPENSES_DEDUCTIBLE = CATALOG.declare("fish_total_expenses_deductible", Decimal)
"""Total fishing expenses deductible, Guide T4002 "Use of a fishing boat mainly for personal use"
"you can deduct expenses and CCA. However, the amount you deduct cannot be more than your income
from the catch" (confirmed from the PDF; no .txt published): the limited amount when the answer
`ca/fish_boat_mainly_personal_checked` is 1, else line 9368, signed like it."""

FISH_NET_INCOME_BEFORE_BOAT_LIMIT = CATALOG.declare("fish_net_income_before_boat_limit", Decimal)
"""Fishing net income before the limit of a boat mainly for personal use, Form T2121 line 9369
"Net income (loss) before adjustments: Amount 4A minus line 9368", before Guide T4002 "Use of a
fishing boat mainly for personal use" limits the deduction (confirmed from the PDF; no .txt
published): amount 4A less line 9368, signed. Area A endnote 5 reads it, as its income is "before
any CCA deductions"."""

FISH_NET_INCOME_BEFORE_ADJUSTMENTS = CATALOG.declare("fish_net_income_before_adjustments", Decimal)
"""Fishing net income before adjustments, Form T2121 line 9369 "Net income (loss) before
adjustments: Amount 4A minus line 9368": amount 4A less line 9368, signed, a loss is negative."""

FISH_SHARE_OF_NET_INCOME = CATALOG.declare("fish_share_of_net_income", Decimal)
"""Filer's share of the fishing net income, Form T2121 amount 5A "Your share of line 9369 or the
amount from your T5013 slip, Statement of Partnership Income": line 9369, or for a partner the
T5013 amount; signed."""

FISH_PARTNERSHIP_TOTAL = CATALOG.declare("fish_partnership_total", Decimal)
"""Partnership total, Form T2121 amount 5B "Total: Amount 5A plus line 9974": amount 5A plus line
9974, signed."""

FISH_PARTNER_OTHER_AMOUNTS_TOTAL = CATALOG.declare(
    "fish_partner_other_amounts_total", Decimal, non_negative=True
)
"""Total of the partner's other amounts, Form T2121 amount 6F "Total other amounts deductible from
your share of the net partnership income (loss): Add amounts 6A to 6E": amounts 6A to 6E added."""

FISH_PARTNER_OTHER_AMOUNTS = CATALOG.declare(
    "fish_partner_other_amounts", Decimal, non_negative=True
)
"""Partner's other amounts deductible, Form T2121 line 9943 "Other amounts deductible from your
share of net partnership income (loss) (amount 6F)": amount 6F."""

FISH_NET_INCOME_AFTER_ADJUSTMENTS = CATALOG.declare("fish_net_income_after_adjustments", Decimal)
"""Fishing net income after adjustments, Form T2121 amount 5C "Net income (loss) after adjustments:
Amount 5B minus line 9943": amount 5B less line 9943, signed, a loss is negative."""

FISH_HOME_EXPENSES_SUBTOTAL = CATALOG.declare(
    "fish_home_expenses_subtotal", Decimal, non_negative=True
)
"""Subtotal of the home expenses, Form T2121 amount 7H "Subtotal: Add amounts 7A to 7G.": amounts
7A to 7G added."""

FISH_HOME_EXPENSES_BUSINESS_PART = CATALOG.declare("fish_home_expenses_business_part", Decimal)
"""Business part of the home expenses, Form T2121 amount 7J "Subtotal: Amount 7H minus amount 7I":
amount 7H less amount 7I."""

FISH_HOME_EXPENSES_AVAILABLE = CATALOG.declare("fish_home_expenses_available", Decimal)
"""Home expenses available, Form T2121 amount 7M "Subtotal: Add amounts 7J to 7L.": amounts 7J to
7L added."""

FISH_HOME_INCOME_LIMIT = CATALOG.declare("fish_home_income_limit", Decimal, non_negative=True)
"""Net income limit on the home expenses, Form T2121 amount 7N "Net income (loss) after adjustments
(amount 5C) (if negative, enter "0")": amount 5C, or 0 when it is negative."""

FISH_HOME_CARRY_FORWARD = CATALOG.declare("fish_home_carry_forward", Decimal, non_negative=True)
"""Home expenses to carry forward, Form T2121 amount 7O "Business-use-of-home expenses available to
carry forward: Amount 7M minus amount 7N (if negative, enter "0")": amount 7M less amount 7N, or
0 when it is negative."""

FISH_HOME_ALLOWABLE_CLAIM = CATALOG.declare("fish_home_allowable_claim", Decimal)
"""Allowable home expenses claim, Form T2121 amount 7P "Allowable claim: Amount 7M or 7N above,
whichever is less (enter your share of this amount on line 9945 of Part 5)": the lesser of
amounts 7M and 7N."""

FISH_HOME_EXPENSES = CATALOG.declare("fish_home_expenses", Decimal)
"""Fishing business-use-of-home expenses, Form T2121 line 9945 "Business-use-of-home expenses
(amount 7P)": amount 7P."""

FISH_EPOP_ASSOCIATED = CATALOG.declare("fish_epop_associated", int, non_negative=True)
"""Whether the filer is associated with an EPOP, Form T2121 Area A endnote 5 "$1.5 million, if you
are not associated with any other eligible person or partnership (EPOP) in the tax year" and
"amount iii of Area G, if you are associated with one or more EPOPs in the tax year": 1 if the
filer is associated with one or more EPOPs in the tax year, 0 if not, a starting count. It is
endnote 5's association, whether or not an agreement was filed; Area G is filled in when one
was."""

FISH_EPOP_ASSOCIATED_CHECKED = CATALOG.declare(
    "fish_epop_associated_checked", int, non_negative=True
)
"""Whether the filer is associated with an EPOP, Form T2121 Area A endnote 5 "$1.5 million, if
you are not associated with any other eligible person or partnership (EPOP) in the tax year":
the answer of `ca/fish_epop_associated` after the check that it is 0 or 1
(`ca/yes_or_no_count`), a count of 1 or 0. A count of 2 or more is refused, not capped."""

FISH_EPOP_AGREEMENT_FILED = CATALOG.declare("fish_epop_agreement_filed", int, non_negative=True)
"""Whether the agreement was filed, Form T2121 Area A endnote 5 "zero, if you are associated with
one or more EPOPs and an agreement that assigns a percentage to one or more of the associated
EPOPs was not filed with the minister in a prescribed form": 1 if the agreement was filed, 0 if
it was not, a starting count."""

FISH_EPOP_AGREEMENT_FILED_CHECKED = CATALOG.declare(
    "fish_epop_agreement_filed_checked", int, non_negative=True
)
"""Whether the agreement was filed, Form T2121 Area A endnote 5 "zero, if you are associated with
one or more EPOPs and an agreement that assigns a percentage to one or more of the associated
EPOPs was not filed with the minister in a prescribed form": the answer of
`ca/fish_epop_agreement_filed` after the check that it is 0 or 1 (`ca/yes_or_no_count`), a
count of 1 or 0. A count of 2 or more is refused, not capped."""

FISH_EPOP_PERCENTAGE = CATALOG.declare("fish_epop_percentage", Decimal, non_negative=True)
"""Percentage assigned to the fishing business, Form T2121 Area G "Percentage assigned under the
agreement" (column 3, the filer's own row), entered as the form prints it, 40 for 40%: a starting
amount."""

FISH_EPOP_PERCENTAGE_TOTAL = CATALOG.declare(
    "fish_epop_percentage_total", Decimal, non_negative=True
)
"""Total of the percentages assigned, Form T2121 Area G "Total of percentage assigned: Total of
column 3", entered as the form prints it: a starting amount."""

FISH_MINISTER_ALLOCATION_GIVEN = CATALOG.declare(
    "fish_minister_allocation_given", int, non_negative=True
)
"""Whether the minister allocated an amount, Form T2121 Area A endnote 5 "any amount allocated by
the minister under subsection 1104(3.4) of the Regulations": 1 if an amount was allocated, 0
otherwise, a starting count."""

FISH_MINISTER_ALLOCATION_GIVEN_CHECKED = CATALOG.declare(
    "fish_minister_allocation_given_checked", int, non_negative=True
)
"""Whether the minister allocated an amount, Form T2121 Area A endnote 5 "any amount allocated by
the minister under subsection 1104(3.4) of the Regulations": the answer of
`ca/fish_minister_allocation_given` after the check that it is 0 or 1 (`ca/yes_or_no_count`),
a count of 1 or 0. A count of 2 or more is refused, not capped."""

FISH_MINISTER_ALLOCATION = CATALOG.declare("fish_minister_allocation", Decimal, non_negative=True)
"""Amount allocated by the minister, Form T2121 Area A endnote 5 "any amount allocated by the
minister under subsection 1104(3.4) of the Regulations": a starting amount, which replaces the
immediate expensing limit when the minister allocated one."""

FISH_FISCAL_PERIOD_DAYS_ENTERED = CATALOG.declare(
    "fish_fiscal_period_days_entered", int, non_negative=True
)
"""Days of the fiscal period of Form T2121, the days the filer enters when the fiscal period is
shorter than a full year, 0 when none are entered (a full year).
Guide T4002 2025, "You were asking?": "Since your fiscal period is less than 365 days,
you have to prorate your CCA claim. ... base your CCA claim on the number of days in your
fiscal period compared to 365 days. In this case, your fiscal period is 214 days." A starting
count."""

FISH_LAND_ADDITIONS = CATALOG.declare("fish_land_additions", Decimal, non_negative=True)
"""Cost of the land added in the year, Form T2121 Area F "Line 9923: Total cost of all land
additions in the year": a starting amount, taken as entered."""

FISH_LAND_DISPOSITIONS = CATALOG.declare("fish_land_dispositions", Decimal, non_negative=True)
"""Proceeds of the land disposed of in the year, Form T2121 Area F "Line 9924: Total proceeds from
all land dispositions in the year": a starting amount, taken as entered."""

FISH_LIABILITIES = CATALOG.declare("fish_liabilities", Decimal, non_negative=True)
"""Total business liabilities, Form T2121 Part 9 "Details of equity" "Line 9931: Total business
liabilities": a starting amount, taken as entered."""

FISH_DRAWINGS = CATALOG.declare("fish_drawings", Decimal, non_negative=True)
"""Drawings in the current year, Form T2121 Part 9 "Details of equity" "Line 9932: Drawings in the
current year": a starting amount, taken as entered."""

FISH_CAPITAL_CONTRIBUTIONS = CATALOG.declare(
    "fish_capital_contributions", Decimal, non_negative=True
)
"""Capital contributions in the current year, Form T2121 Part 9 "Details of equity" "Line 9933:
Capital contributions in the current year": a starting amount, taken as entered."""

T2121_STATEMENTS = RecordListKind.declare(
    CATALOG,
    "t2121_statements",
    fields=(
        FISH_FISH_PRODUCTS,
        FISH_OTHER_MARINE_PRODUCTS,
        FISH_GRANTS_CREDITS_AND_REBATES,
        FISH_SUBSIDIES,
        FISH_COMPENSATION_FOR_LOSS,
        FISH_SHARESPERSON_INCOME,
        FISH_OTHER_INCOME,
        FISH_SALT_BAIT_AND_ICE,
        FISH_CREW_SHARES,
        FISH_FUEL_COSTS,
        FISH_FISHING_GEAR,
        FISH_INSURANCE,
        FISH_INTEREST_AND_BANK_CHARGES,
        FISH_MEALS_AND_ENTERTAINMENT,
        FISH_BUSINESS_TAXES_LICENCES_AND_MEMBERSHIPS,
        BUSINESS_VEHICLES,
        FISH_VEHICLE_SALES_TAX_RATE,
        FISH_OFFICE_EXPENSES,
        FISH_NETS_AND_TRAPS,
        FISH_PROFESSIONAL_FEES,
        FISH_SALARIES_WAGES_AND_BENEFITS,
        FISH_REPAIRS_FISHING_BOAT,
        FISH_REPAIRS_ENGINE,
        FISH_REPAIRS_ELECTRICAL_EQUIPMENT,
        FISH_INSURANCE_RECOVERY,
        FISH_OTHER_EXPENSES,
        FISH_CCA_PERSONAL_PART,
        FISH_FISCAL_PERIOD_DAYS_ENTERED,
        FISH_LAND_ADDITIONS,
        FISH_LAND_DISPOSITIONS,
        FISH_LIABILITIES,
        FISH_DRAWINGS,
        FISH_CAPITAL_CONTRIBUTIONS,
        FISH_CCA_CLASSES,
        FISH_PARTNER,
        FISH_PARTNER_SHARE,
        FISH_PARTNER_GST_HST_REBATE,
        FISH_PARTNER_OTHER_AMOUNT_A,
        FISH_PARTNER_OTHER_AMOUNT_B,
        FISH_PARTNER_OTHER_AMOUNT_C,
        FISH_PARTNER_OTHER_AMOUNT_D,
        FISH_PARTNER_OTHER_AMOUNT_E,
        FISH_HOME_HEAT,
        FISH_HOME_ELECTRICITY,
        FISH_HOME_INSURANCE,
        FISH_HOME_MAINTENANCE,
        FISH_HOME_MORTGAGE_INTEREST,
        FISH_HOME_PROPERTY_TAXES,
        FISH_HOME_OTHER_EXPENSES,
        FISH_HOME_PERSONAL_USE_PART,
        FISH_HOME_CCA,
        FISH_HOME_CARRIED_FORWARD,
        FISH_EPOP_ASSOCIATED,
        FISH_EPOP_AGREEMENT_FILED,
        FISH_EPOP_PERCENTAGE,
        FISH_EPOP_PERCENTAGE_TOTAL,
        FISH_MINISTER_ALLOCATION_GIVEN,
        FISH_MINISTER_ALLOCATION,
        FISH_BOAT_MAINLY_PERSONAL,
    ),
)
"""Statements of Form T2121, one record for each statement of fishing activities the return
carries (one for each fishing business): its fields are the starting amounts, the Area A list
and the Area G answers of one statement, Parts 3 to 7 and Area G, in the order of the form. The
form `ca/t2121` runs once for each record; T1 line 14300 "Net" adds the lines 9946 of the
records. A field is not an artifact of the return."""

FISH_CLOSING_UCC = RecordListKind.declare(
    CATALOG, "fish_closing_ucc", fields=(CCA_CLASS_NUMBER, CCA_UCC_AT_END)
)
"""Fishing closing UCC, Form T2121 Area A "UCC at the end of the year (col. 7 minus col. 21)": one
record for each class of the fishing classes, holding its class number and column 22."""

FISH_IMMEDIATE_EXPENSING_CAP = CATALOG.declare(
    "fish_immediate_expensing_cap", Decimal, non_negative=True
)
"""Immediate expensing limit when not associated, Form T2121 Area A endnote 5 "$1.5 million, if you
are not associated with any other eligible person or partnership (EPOP) in the tax year" and Area G
"Immediate expensing limit allocated to your business: Multiply $1.5 million by the percentage
assigned to your business in column 3**": the printed $1.5 million, from a dataset."""

FISH_EPOP_PERCENTAGE_MAXIMUM = CATALOG.declare(
    "fish_epop_percentage_maximum", Decimal, non_negative=True
)
"""Largest total of the percentages assigned, Form T2121 Area G "The total of all percentages
assigned under the agreement should not be more than 100%" and "** If the total of column 3 is more
than 100%, enter "0."": the printed 100%, from a dataset, as the form prints a percentage (100 for
100%)."""

FISH_IMMEDIATE_EXPENSING_SHARE = CATALOG.declare(
    "fish_immediate_expensing_share", Decimal, non_negative=True
)
"""Immediate expensing limit times the percentage, the first step of Form T2121 Area G "Immediate
expensing limit allocated to your business: Multiply $1.5 million by the percentage assigned to
your business in column 3**": $1.5 million times the percentage assigned to your business."""

FISH_EPOP_PERCENTAGE_ROOM = CATALOG.declare("fish_epop_percentage_room", Decimal)
"""Room under 100% in the percentages assigned, the test of Form T2121 Area G "** If the total of
column 3 is more than 100%, enter "0."": 100 less the total of column 3, signed, negative when the
total is more than 100%."""

FISH_IMMEDIATE_EXPENSING_ALLOCATED = CATALOG.declare(
    "fish_immediate_expensing_allocated", Decimal, non_negative=True
)
"""Immediate expensing limit allocated to the fishing business, Form T2121 Area G "Immediate
expensing limit allocated to your business: Multiply $1.5 million by the percentage assigned to
your business in column 3**" and "** If the total of column 3 is more than 100%, enter "0."": the
multiple, or 0 when the total of column 3 is more than 100%."""

FISH_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT = CATALOG.declare(
    "fish_immediate_expensing_associated_limit", Decimal, non_negative=True
)
"""Immediate expensing limit when associated with an EPOP, Form T2121 Area A endnote 5 "amount iii
of Area G, if you are associated with one or more EPOPs in the tax year" and "zero, if you are
associated with one or more EPOPs and an agreement that assigns a percentage to one or more of the
associated EPOPs was not filed with the minister in a prescribed form": amount iii, or 0 when no
agreement was filed."""

FISH_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER = CATALOG.declare(
    "fish_immediate_expensing_limit_before_minister", Decimal, non_negative=True
)
"""Immediate expensing limit before any amount allocated by the minister, Form T2121 Area A
endnote 5 "the immediate expensing limit, which is equal to one of the following, whichever is
applicable": $1.5 million when not associated with an EPOP, else the limit when associated."""

FISH_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION = CATALOG.declare(
    "fish_immediate_expensing_limit_before_proration", Decimal, non_negative=True
)
"""Immediate expensing limit before the days of the fiscal period scale it, Income Tax
Regulations 1104(3.5)(b): "where an eligible person or partnership has a taxation year that is
less than 51 weeks, its immediate expensing limit for the year is that proportion of its
immediate expensing limit for the year determined without reference to this paragraph that the
number of days in the year is of 365". Form T2121 Area A endnote 5 "the immediate expensing
limit, which is equal to one of the following, whichever is applicable", and "any amount
allocated by the minister under subsection 1104(3.4) of the Regulations": the limit before any
amount allocated by the minister, or that amount when there is one, unscaled. Guide T4002,
"Immediate expensing incentive": "The limit is also prorated for tax years shorter than 365
days"."""

FISH_IMMEDIATE_EXPENSING_LIMIT = CATALOG.declare(
    "fish_immediate_expensing_limit", Decimal, non_negative=True
)
"""Immediate expensing limit, Form T2121 Area A endnote 5 "the immediate expensing limit, which is
equal to one of the following, whichever is applicable", including "any amount allocated by the
minister under subsection 1104(3.4) of the Regulations": the limit above, or the amount allocated
by the minister when there is one."""

FISH_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED = CATALOG.declare(
    "fish_immediate_expensing_limit_unprorated", Decimal, non_negative=True
)
"""Immediate expensing limit before the days scaling, Form T2121 Area A endnote 5 "the immediate
expensing limit, which is equal to one of the following, whichever is applicable", and Guide T4002:
"The limit is also prorated for tax years shorter than 365 days": the per-person limit before the
limit is scaled to the days of the fiscal period, the minister's amount as entered."""

FISH_IMMEDIATE_EXPENSING_CLAIM = CATALOG.declare(
    "fish_immediate_expensing_claim", Decimal, non_negative=True
)
"""Total immediate expensing claim for the year, Form T2121 Area A "Total immediate expensing claim
for the year: Total of column 9" (line i), limited by endnote 5 to "the lesser of" the immediate
expensing limit, "the UCC of DIEPs in column 8" and "the amount of income, if any, earned from the
source of income that is a business (before any CCA deductions)": the total of column 9 over the
classes."""

RENTAL_IMMEDIATE_EXPENSING_CLAIMS_TOTAL = CATALOG.declare(
    "rental_immediate_expensing_claims_total", Decimal, non_negative=True
)
"""Total of the immediate expensing claims of the statements of Form T776, Area A "Total of
column 9" (line i) of each statement added: the form's share of the person's total
for the year."""

BUSINESS_IMMEDIATE_EXPENSING_CLAIMS_TOTAL = CATALOG.declare(
    "business_immediate_expensing_claims_total", Decimal, non_negative=True
)
"""Total of the immediate expensing claims of the statements of Form T2125, Area A "Total of
column 9" (line i) of each statement added: the form's share of the person's total
for the year."""

FARM_IMMEDIATE_EXPENSING_CLAIMS_TOTAL = CATALOG.declare(
    "farm_immediate_expensing_claims_total", Decimal, non_negative=True
)
"""Total of the immediate expensing claims of the statements of Form T2042, Area A "Total of
column 9" (line i) of each statement added: the form's share of the person's total
for the year."""

FISH_IMMEDIATE_EXPENSING_CLAIMS_TOTAL = CATALOG.declare(
    "fish_immediate_expensing_claims_total", Decimal, non_negative=True
)
"""Total of the immediate expensing claims of the statements of Form T2121, Area A "Total of
column 9" (line i) of each statement added: the form's share of the person's total
for the year."""

IMMEDIATE_EXPENSING_CLAIMS_TOTAL = CATALOG.declare(
    "immediate_expensing_claims_total", Decimal, non_negative=True
)
"""Total immediate expensing claims of every statement of Forms T776, T2125, T2042 and T2121,
Area A endnote 5 "The total immediate expensing amount for the tax year (total of column 9) is
limited to the lesser of: the immediate expensing limit"; Guides T4002 and T4036: "The deduction is
limited to $1.5 million per tax year". The forms print the limit for each statement and are silent
on a person who files several statements; the Guides' "per tax year" is the only statement of the
rule across them: the four totals above added."""

IMMEDIATE_EXPENSING_AGREED_LIMIT = CATALOG.declare(
    "immediate_expensing_agreed_limit", Decimal, non_negative=True
)
"""The person's one immediate expensing limit for the year, Area A endnote 5 "the immediate
expensing limit, which is equal to one of the following, whichever is applicable: $1.5 million, if
you are not associated with any other eligible person or partnership (EPOP) in the tax year; amount
iii of Area G, if you are associated with one or more EPOPs in the tax year; ...": the limit the
statements that claim immediate expensing share, 0 when none does. The forms are silent on
statements whose limits differ."""

IMMEDIATE_EXPENSING_SHORT_YEAR_DAYS = CATALOG.declare(
    "immediate_expensing_short_year_days", Decimal, non_negative=True
)
"""The short-year figure of the immediate expensing limit, Income Tax Regulations 1104(3.5)(b):
"where an eligible person or partnership has a taxation year that is less than 51 weeks": the 51
weeks, printed as 51 weeks of 7 days, 357 days, the figure a year must be shorter than to be
prorated by its days over 365. Guide T4002 and Guide T4036, "Immediate expensing incentive": "The
limit is also prorated for tax years shorter than 365 days", give no figure; the Regulations
decide over the guides. Read from a dataset by each form's prorating step."""

IMMEDIATE_EXPENSING_TOTAL_CLAIM = CATALOG.declare(
    "immediate_expensing_total_claim", Decimal, non_negative=True
)
"""Total immediate expensing claim of the person across all statements of Forms T776, T2125, T2042
and T2121, Guides T4002 and T4036 "The deduction is limited to $1.5 million per tax year": the
total of every statement's column 9, at most the person's one limit."""

FISH_INCOME_BEFORE_CCA = CATALOG.declare("fish_income_before_cca", Decimal, non_negative=True)
"""Fishing income before CCA, Form T2121 Area A endnote 5 "the amount of income, if any, earned
from the source of income that is a business (before any CCA deductions) in which the relevant
DIEP is used for the tax year": line 9369 "Net income (loss) before adjustments" plus line 9936,
the CCA it deducted, not below zero."""

FISH_FISCAL_PERIOD_DAYS = CATALOG.declare("fish_fiscal_period_days", int, non_negative=True)
"""Days of the fiscal period of Form T2121 that the CCA claim and closing UCC are prorated by:
the days entered when above 0, else the days in a full year.
Guide T4002 2025, "You were asking?": "Since your fiscal period is less than 365 days,
you have to prorate your CCA claim. ... base your CCA claim on the number of days in your
fiscal period compared to 365 days. In this case, your fiscal period is 214 days"
(the Guide's example)."""


FLIPPED_PROPERTY_DISPOSED = CATALOG.declare("flipped_property_disposed", int, non_negative=True)
"""Line 17905 "Did you dispose of a housing unit, or a right to acquire a housing unit, located in
Canada (including a rental property) that was not considered inventory and was owned for less
than 365 consecutive days before the disposition? Yes or No": 1 for "Yes", 0 for "No", a
starting count."""

FLIPPED_PROPERTY_DISPOSED_CHECKED = CATALOG.declare(
    "flipped_property_disposed_checked", int, non_negative=True
)
"""Line 17905 "Yes or No", checked: the answer of line 17905 as a count, 0 or 1 (a count above 1 is
an input error, not capped), read by the flipped property count."""

FLIPPED_PROPERTY_LIFE_EVENT_1 = CATALOG.declare(
    "flipped_property_life_event_1", int, non_negative=True
)
"""Line 17906 "Box 1: the death of the taxpayer or a related person": 1 when the box is ticked, 0
when not, a starting count."""

FLIPPED_PROPERTY_LIFE_EVENT_1_CHECKED = CATALOG.declare(
    "flipped_property_life_event_1_checked", int, non_negative=True
)
"""Line 17906 "Box 1", checked: the tick box of box 1 as a count, 0 or 1 (a count above 1 is an
input error, not capped), read by the flipped property count."""

FLIPPED_PROPERTY_LIFE_EVENT_2 = CATALOG.declare(
    "flipped_property_life_event_2", int, non_negative=True
)
"""Line 17906 "Box 2: a related person joining the taxpayer's household or the taxpayer joining a
related person's household (for example, birth of a child, adoption, or care of an elderly
parent)": 1 when the box is ticked, 0 when not, a starting count."""

FLIPPED_PROPERTY_LIFE_EVENT_2_CHECKED = CATALOG.declare(
    "flipped_property_life_event_2_checked", int, non_negative=True
)
"""Line 17906 "Box 2", checked: the tick box of box 2 as a count, 0 or 1 (a count above 1 is an
input error, not capped), read by the flipped property count."""

FLIPPED_PROPERTY_LIFE_EVENT_3 = CATALOG.declare(
    "flipped_property_life_event_3", int, non_negative=True
)
"""Line 17906 "Box 3: the breakdown of a marriage or common-law partnership where the taxpayer had
been living separate and apart from their spouse or common-law partner for at least 90 days
before the disposition": 1 when the box is ticked, 0 when not, a starting count."""

FLIPPED_PROPERTY_LIFE_EVENT_3_CHECKED = CATALOG.declare(
    "flipped_property_life_event_3_checked", int, non_negative=True
)
"""Line 17906 "Box 3", checked: the tick box of box 3 as a count, 0 or 1 (a count above 1 is an
input error, not capped), read by the flipped property count."""

FLIPPED_PROPERTY_LIFE_EVENT_4 = CATALOG.declare(
    "flipped_property_life_event_4", int, non_negative=True
)
"""Line 17906 "Box 4: a threat to the personal safety of the taxpayer or a related person (for
example, domestic violence)": 1 when the box is ticked, 0 when not, a starting count."""

FLIPPED_PROPERTY_LIFE_EVENT_4_CHECKED = CATALOG.declare(
    "flipped_property_life_event_4_checked", int, non_negative=True
)
"""Line 17906 "Box 4", checked: the tick box of box 4 as a count, 0 or 1 (a count above 1 is an
input error, not capped), read by the flipped property count."""

FLIPPED_PROPERTY_LIFE_EVENT_5 = CATALOG.declare(
    "flipped_property_life_event_5", int, non_negative=True
)
"""Line 17906 "Box 5: a serious disability or illness of the taxpayer or a related person": 1 when
the box is ticked, 0 when not, a starting count."""

FLIPPED_PROPERTY_LIFE_EVENT_5_CHECKED = CATALOG.declare(
    "flipped_property_life_event_5_checked", int, non_negative=True
)
"""Line 17906 "Box 5", checked: the tick box of box 5 as a count, 0 or 1 (a count above 1 is an
input error, not capped), read by the flipped property count."""

FLIPPED_PROPERTY_LIFE_EVENT_6 = CATALOG.declare(
    "flipped_property_life_event_6", int, non_negative=True
)
"""Line 17906 "Box 6: the eligible relocation of the taxpayer or their spouse or common-law partner
where the taxpayer's new home (including area code): is at least 40 kilometres closer to the new
work (including area code): location or school (generally, an eligible relocation allows the
taxpayer to carry on business, be employed, or attend full-time post-secondary education)": 1
when the box is ticked, 0 when not, a starting count."""

FLIPPED_PROPERTY_LIFE_EVENT_6_CHECKED = CATALOG.declare(
    "flipped_property_life_event_6_checked", int, non_negative=True
)
"""Line 17906 "Box 6", checked: the tick box of box 6 as a count, 0 or 1 (a count above 1 is an
input error, not capped), read by the flipped property count."""

FLIPPED_PROPERTY_LIFE_EVENT_7 = CATALOG.declare(
    "flipped_property_life_event_7", int, non_negative=True
)
"""Line 17906 "Box 7: the involuntary termination of employment of the taxpayer or their spouse or
common-law partner": 1 when the box is ticked, 0 when not, a starting count."""

FLIPPED_PROPERTY_LIFE_EVENT_7_CHECKED = CATALOG.declare(
    "flipped_property_life_event_7_checked", int, non_negative=True
)
"""Line 17906 "Box 7", checked: the tick box of box 7 as a count, 0 or 1 (a count above 1 is an
input error, not capped), read by the flipped property count."""

FLIPPED_PROPERTY_LIFE_EVENT_8 = CATALOG.declare(
    "flipped_property_life_event_8", int, non_negative=True
)
"""Line 17906 "Box 8: the insolvency of the taxpayer (for example, due to an accumulation of
debt)": 1 when the box is ticked, 0 when not, a starting count."""

FLIPPED_PROPERTY_LIFE_EVENT_8_CHECKED = CATALOG.declare(
    "flipped_property_life_event_8_checked", int, non_negative=True
)
"""Line 17906 "Box 8", checked: the tick box of box 8 as a count, 0 or 1 (a count above 1 is an
input error, not capped), read by the flipped property count."""

FLIPPED_PROPERTY_LIFE_EVENT_9 = CATALOG.declare(
    "flipped_property_life_event_9", int, non_negative=True
)
"""Line 17906 "Box 9: the destruction or expropriation of the taxpayer's property (for example,
when the property is destroyed due to natural or man-made disaster)": 1 when the box is ticked,
0 when not, a starting count."""

FLIPPED_PROPERTY_LIFE_EVENT_9_CHECKED = CATALOG.declare(
    "flipped_property_life_event_9_checked", int, non_negative=True
)
"""Line 17906 "Box 9", checked: the tick box of box 9 as a count, 0 or 1 (a count above 1 is an
input error, not capped), read by the flipped property count."""

FLIPPED_PROPERTY = CATALOG.declare("flipped_property", int, non_negative=True)
"""Flipped property, Schedule 3 Part 1 page 2 "If none of the life events above apply to you, the
housing unit is considered a flipped property and the gain is taxable as business income": 1
when line 17905 is "Yes" and no box of line 17906 is ticked, else 0. A conclusion the form
states, not a printed line."""

FLIPPED_PROPERTY_LIFE_EVENT_WITHOUT_YES = CATALOG.declare(
    "flipped_property_life_event_without_yes", int, non_negative=True
)
"""Schedule 3 Part 1 line 17905 "If you ticked "no", the housing unit is not considered a flipped
property." and line 17906 "If any of the life events above apply to you, the housing unit is not
considered a flipped property.": 1 when line 17905 is "No" and a box of line 17906 is ticked, else
0, a starting count. A box of line 17906 is asked only after a "Yes" on line 17905, so this count
of 1 is refused (see `flipped_property_life_event_without_yes_checked`)."""

FLIPPED_PROPERTY_LIFE_EVENT_WITHOUT_YES_CHECKED = CATALOG.declare(
    "flipped_property_life_event_without_yes_checked", int, non_negative=True
)
"""Schedule 3 Part 1 line 17906 boxes ticked while line 17905 is not "Yes", checked: the count of
`flipped_property_life_event_without_yes` when it is 0, the only value produced. A count of 1 is an
input error, not capped, so the form never reads a box ticked with line 17905 "No"."""
