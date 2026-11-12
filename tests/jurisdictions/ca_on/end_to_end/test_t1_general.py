"""T1 General (CRA 5006-R, 2025, Ontario edition) from the salary alone: the take-home
manifest's real parts composed end to end, at several salaries.

Every form has its own end-to-end module in this folder, and every line part has its own test with
its neighbours typed in. This module composes the whole real take-home manifest (the real header
`manifest.yaml`, the form-less `return.yaml`, `salary.yaml` and every form's part files: Schedule
8, T2204, ca/t1_taxable_income, ON428-A, ON428, Schedule 6 and the T1 General) and types in only
the gross salary (`ca/employment_income`). It pins the T1 lines the salary-only filer fills, the
return's one output (line 167, refund or balance owing) and the CPP and EI figures the calculator
reads from Schedule 8 and T2204. It is not a worked return: no return file, no slips, no tax paid.
The partial CPP2 range (salary between 71,300 and 81,200) is covered by one salary in ANCHORS and
by the boundary salaries (BOUNDARY_ANCHORS).

Form text: T1 General (CRA 5006-R, 2025, docs/cra-forms-2025/5006-r-25e.txt) "Line 75" columns
"Line 26000 is more than $57,375 but not more than $114,750" and the printed constants 8,319.38,
20,081.25, 36,495.57, 58,399.85; "Line 74: Line 72 multiplied by the percentage from line 73";
"Line 76: Line 74 plus line 75"; "Line 167: Line 149 minus line 166". ON428 (CRA 5006-C, 2025,
docs/cra-forms-2025/5006-c-25e.txt) Part A columns "Line 1 is more than $52,886 but not more than
$105,775", line 7 constants 2,670.74, 7,510.09, 12,445.60, 20,957.60, and "Line 90: Line 88 plus
line 89 Enter this amount on line 42800 of your return". Schedule 8 (CRA 5000-S8) lines 12 and 28
give line 22215 (maximum $1,074.00). A taxable income equal to a column's upper bound belongs to
that column. The form prints no rounding rule for lines 6 and 74; the engine rounds them half-up to
the cent (the project's cent rounding), and the module's oracle does the same.

Oracles by salary: $70,000 Return DD (traced in the Schedule 8, T2204, ON428 and Schedule 6
audits); $20,000, $275,000 and $2,010 from the PDOC check and T4127 (CRA, 121st
edition), as recorded in the project's validation notes; the bracket salaries from arithmetic on
the printed constants above; the boundary salaries are engine pins checked against the TaxTips.ca
2025 calculator (see BOUNDARY_ANCHORS). Line 167 literals exist only at the anchor and boundary
salaries; at the other salaries line 167 is checked against the federal tax after credits and
Ontario line 90. The take-home subtraction (salary less CPP, EI and tax) lives in the calculator,
outside the engine.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.credits_against_federal_tax import (
    CREDITS_AGAINST_FEDERAL_TAX,
    FEDERAL_LOGGING_TAX_CREDIT,
    FEDERAL_TAX,
    FEDERAL_TAX_LESS_CREDITS,
)
from tax_engine.jurisdictions.ca.catalog.deductions import (
    SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
)
from tax_engine.jurisdictions.ca.catalog.income import (
    CREDITS_AGAINST_BASIC_FEDERAL_TAX,
    EMPLOYMENT_INCOME,
    OTHER_EMPLOYMENT_INCOME,
)
from tax_engine.jurisdictions.ca.catalog.net_tax import (
    NET_FEDERAL_TAX,
    PROVINCIAL_TAX_LINE_42800,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca.catalog.non_refundable_credits import (
    CANADA_EMPLOYMENT_AMOUNT,
    CANADA_EMPLOYMENT_AMOUNT_INCOME,
    CREDIT_AMOUNTS_AT_CREDIT_RATE,
    CREDIT_AMOUNTS_LINE_84,
    CREDIT_AMOUNTS_LINE_98,
    CREDIT_AMOUNTS_LINE_106,
    FEDERAL_FOREIGN_TAX_CREDIT,
    FEDERAL_TAX_AFTER_CREDITS,
    FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT,
    FEDERAL_TAX_WITH_ITC_RECAPTURE,
    FEDERAL_TAX_WITH_SPLIT_INCOME,
    FEDERAL_TAX_WITH_SURTAX,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    NON_REFUNDABLE_TAX_CREDITS,
)
from tax_engine.jurisdictions.ca.catalog.personal_amounts import (
    BASIC_PERSONAL_AMOUNT,
    CPP_BASE_CONTRIBUTIONS_LINE_86,
    CREDITS_SUBTOTAL_LINE_96,
    EI_PREMIUMS_LINE_88,
    FEDERAL_BRACKET_COLUMN_RATE_LINE_73,
    FEDERAL_BRACKET_LOWER_BOUND_LINE_71,
    FEDERAL_EXCESS_TIMES_COLUMN_RATE_LINE_74,
    FEDERAL_TAX_AT_COLUMN_START_LINE_75,
    FEDERAL_TAX_ON_TAXABLE_INCOME_LINE_76,
    FEDERAL_TAX_TAXABLE_INCOME_LINE_70,
    FEDERAL_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_72,
)
from tax_engine.jurisdictions.ca.catalog.refund import (
    CWB_LINE_45300,
    EI_OVERPAYMENT_LINE_45000,
    REFUND_OR_BALANCE_OWING,
    T2204_PREMIUMS_DEDUCTED,
    TOTAL_CREDITS,
)
from tax_engine.jurisdictions.ca_on.catalog import (
    ON428_ONTARIO_TAX_LINE_90,
    ON428_TAX_ON_TAXABLE_INCOME_LINE_8,
    ON428_TAXABLE_INCOME_LINE_1,
)
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService, header_without_imports

D = Decimal
CODE = JurisdictionCode("CA-ON")
# The two files that are not parts of a form: the real header and the form-less return.
HEADER = header_without_imports()
RETURN = (TAKE_HOME / "return.yaml").read_text(encoding="utf-8")
PARTS = (
    "salary.yaml",
    *(
        part.name
        for part in sorted(TAKE_HOME.rglob("*.yaml"))
        if part.name not in {"manifest.yaml", "return.yaml", "salary.yaml"}
    ),
)

# T1 General lines by kind, at $70,000 (Return DD). The label is the form line the kind is.
T1_AT_70000: dict[str, tuple[AmountKind, str]] = {
    "30000": (BASIC_PERSONAL_AMOUNT, "16129.00"),
    "70": (FEDERAL_TAX_TAXABLE_INCOME_LINE_70, "69335.00"),
    "71": (FEDERAL_BRACKET_LOWER_BOUND_LINE_71, "57375"),
    "72": (FEDERAL_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_72, "11960.00"),
    "73": (FEDERAL_BRACKET_COLUMN_RATE_LINE_73, "0.205"),
    "74": (FEDERAL_EXCESS_TIMES_COLUMN_RATE_LINE_74, "2451.80"),
    "75": (FEDERAL_TAX_AT_COLUMN_START_LINE_75, "8319.38"),
    "76": (FEDERAL_TAX_ON_TAXABLE_INCOME_LINE_76, "10771.18"),
    "84": (CREDIT_AMOUNTS_LINE_84, "16129.00"),
    "86": (CPP_BASE_CONTRIBUTIONS_LINE_86, "3291.75"),
    "88": (EI_PREMIUMS_LINE_88, "1077.48"),
    "96": (CREDITS_SUBTOTAL_LINE_96, "5840.23"),
    "98": (CREDIT_AMOUNTS_LINE_98, "21969.23"),
    "106": (CREDIT_AMOUNTS_LINE_106, "21969.23"),
    "31260 income": (CANADA_EMPLOYMENT_AMOUNT_INCOME, "70000.00"),
    "31260": (CANADA_EMPLOYMENT_AMOUNT, "1471.00"),
    "33800": (CREDIT_AMOUNTS_AT_CREDIT_RATE, "3185.54"),
    "33500": (NON_REFUNDABLE_CREDIT_AMOUNTS, "21969.23"),
    "35000": (NON_REFUNDABLE_TAX_CREDITS, "3185.54"),
    "125": (CREDITS_AGAINST_BASIC_FEDERAL_TAX, "3185.54"),
    "40400": (FEDERAL_TAX_WITH_SPLIT_INCOME, "10771.18"),
    "42800": (PROVINCIAL_TAX_LINE_42800, "3911.45"),
    "42900": (FEDERAL_TAX_AFTER_CREDITS, "7585.64"),
    "128": (FEDERAL_TAX_WITH_SURTAX, "7585.64"),
    "130": (FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT, "7585.64"),
    "132": (FEDERAL_TAX_WITH_ITC_RECAPTURE, "7585.64"),
    "40600": (FEDERAL_TAX, "7585.64"),
    "41600": (CREDITS_AGAINST_FEDERAL_TAX, "0.00"),
    "41700": (FEDERAL_TAX_LESS_CREDITS, "7585.64"),
    "42000": (NET_FEDERAL_TAX, "7585.64"),
    "43500": (TOTAL_PAYABLE, "11497.09"),
    "45000": (EI_OVERPAYMENT_LINE_45000, "0.00"),
    "48200": (TOTAL_CREDITS, "0.00"),
    "45300": (CWB_LINE_45300, "0.00"),
    "167": (REFUND_OR_BALANCE_OWING, "11497.09"),
}

# Lines that are the form's printed bound or rate, not a computed dollar figure.
PRINTED_AS_IS = {"71", "73"}

# The return's line 167 and the payroll figures the calculator reads, by salary, with sources:
# (salary, line 167, federal tax after credits, Ontario tax line 90, CPP base + enhanced, EI, CWB).
# $70,000: Return DD (fed 7,585.64 + ON428 line 90 3,911.45); CPP and EI from T4127 (121st ed.),
# confirmed against the PDOC check. $20,000: PDOC check; the Canada workers benefit
# (1,633.00) exceeds the tax, so line 167 is a refund. $275,000: PDOC check; CPP is capped (base
# 3,356.10, enhanced 678.00, CPP2 396.00: 4,430.10) and line 22215 is 1,074.00. $2,010: T2204
# (EI premium 32.96, line 15 overpayment 22.96 on T1 line 45000), CPP 0.00.
ANCHORS: list[tuple[str, str, str, str, str, str, str]] = [
    ("70000", "11497.09", "7585.64", "3911.45", "3956.75", "1077.48", "0.00"),
    ("20000", "-1474.91", "158.09", "0.00", "981.75", "328.00", "1633.00"),
    ("275000", "101743.28", "62204.64", "39538.64", "4430.10", "1077.48", "0.00"),
    ("2010", "-22.96", "0.00", "0.00", "0.00", "32.96", "0.00"),
]

# Boundary salaries (same column order as ANCHORS): for each edge, the first whole-dollar salary at
# or above it and the dollar either side. The only input is salary, so each net-income edge (line
# 23600) is converted to the salary where it falls, after the line 22215 CPP deduction; because
# that is rarely a whole dollar, the middle row is at most $1 above the exact edge, and the three
# rows straddle it. Edges: CWB phase-in start and end, CPP exemption (3,500), first positive
# federal tax, Ontario health premium steps, Ontario tax reduction end (ON428 line 73 reaches
# 588.00, twice the basic reduction), CWB phase-out start and end, LIFT start and end, the point
# where ON428 line 86 first turns positive (line 81 reaches the LIFT maximum 875), the EI maximum
# (65,700), YMPE (71,300), YAMPE (81,200), Ontario surtax tiers 1 and 2 (printed 5,710 and 7,307
# on ON428 line 65), every federal and Ontario bracket edge (also covered by BRACKET_SALARIES),
# and the federal basic personal amount taper (177,882 to 253,414). A label like "ON bracket 2"
# names the top of bracket 2. Oracle: the engine's own cents as a regression pin; the independent
# TaxTips.ca 2025 calculator (dollar-rounded, not CRA) agreed within $1 on every figure at every
# salary here when the rows were made (8 Nov 2026), and the edge constants are the printed ones.
# Where a pin cannot show its own edge (the tax reduction end), the group comment says so.
BOUNDARY_ANCHORS: list[tuple[str, str, str, str, str, str, str]] = [
    # CWB start
    ("2999", "0.00", "0.00", "0.00", "0.00", "49.18", "0.00"),
    ("3000", "0.00", "0.00", "0.00", "0.00", "49.20", "0.00"),
    ("3001", "-0.27", "0.00", "0.00", "0.00", "49.22", "0.27"),
    # CPP exemption 3,500
    ("3499", "-134.73", "0.00", "0.00", "0.00", "57.38", "134.73"),
    ("3500", "-135.00", "0.00", "0.00", "0.00", "57.40", "135.00"),
    ("3501", "-135.27", "0.00", "0.00", "0.06", "57.42", "135.27"),
    # CWB phase-in end
    ("9048", "-1632.96", "0.00", "0.00", "330.11", "148.39", "1632.96"),
    ("9049", "-1633.00", "0.00", "0.00", "330.17", "148.40", "1633.00"),
    ("9050", "-1633.00", "0.00", "0.00", "330.23", "148.42", "1633.00"),
    # Federal tax first positive
    ("18820", "-1633.00", "0.00", "0.00", "911.54", "308.65", "1633.00"),
    ("18821", "-1632.89", "0.11", "0.00", "911.60", "308.66", "1633.00"),
    ("18822", "-1632.76", "0.24", "0.00", "911.66", "308.68", "1633.00"),
    # OHP 20,000
    ("20166", "-1452.68", "180.32", "0.00", "991.63", "330.72", "1633.00"),
    ("20167", "-1452.52", "180.46", "0.02", "991.69", "330.74", "1633.00"),
    ("20168", "-1452.33", "180.59", "0.08", "991.75", "330.76", "1633.00"),
    # OHP 25,000
    ("25217", "-475.87", "857.14", "299.99", "1292.16", "413.56", "1633.00"),
    ("25218", "-475.73", "857.27", "300.00", "1292.22", "413.58", "1633.00"),
    ("25219", "-475.60", "857.40", "300.00", "1292.28", "413.59", "1633.00"),
    # ON tax reduction end (line 73 reaches 588)
    # (not visible in line 90: the LIFT credit absorbs the tax; line 73 reaches 588.00 mid-group)
    ("26168", "-348.44", "984.56", "300.00", "1348.75", "429.16", "1633.00"),
    ("26169", "-348.31", "984.69", "300.00", "1348.81", "429.17", "1633.00"),
    ("26170", "-348.17", "984.83", "300.00", "1348.87", "429.19", "1633.00"),
    # CWB phase-out start
    ("27090", "-224.90", "1108.10", "300.00", "1403.61", "444.28", "1633.00"),
    ("27091", "-224.75", "1108.24", "300.00", "1403.66", "444.29", "1632.99"),
    ("27092", "-224.47", "1108.37", "300.00", "1403.72", "444.31", "1632.84"),
    # ON428 line 86 first positive (LIFT maximum reached)
    ("32318", "1251.85", "1808.63", "300.00", "1714.67", "530.02", "856.78"),
    ("32319", "1252.17", "1808.77", "300.03", "1714.73", "530.03", "856.63"),
    ("32320", "1252.50", "1808.90", "300.08", "1714.79", "530.05", "856.48"),
    # LIFT start
    ("32792", "1407.86", "1872.15", "322.10", "1742.87", "537.79", "786.39"),
    ("32793", "1408.18", "1872.28", "322.14", "1742.93", "537.81", "786.24"),
    ("32794", "1408.56", "1872.41", "322.24", "1742.99", "537.82", "786.09"),
    # OHP 36,000
    ("36328", "2746.77", "2345.95", "662.11", "1953.27", "595.78", "261.29"),
    ("36329", "2747.18", "2346.08", "662.24", "1953.33", "595.80", "261.14"),
    ("36330", "2747.63", "2346.22", "662.40", "1953.39", "595.81", "260.99"),
    # CWB phase-out end
    ("38087", "3517.29", "2581.64", "935.73", "2057.93", "624.63", "0.08"),
    ("38088", "3517.67", "2581.78", "935.89", "2057.99", "624.64", "0.00"),
    ("38089", "3517.96", "2581.91", "936.05", "2058.05", "624.66", "0.00"),
    # OHP 38,500
    ("38853", "3739.16", "2684.28", "1054.88", "2103.50", "637.19", "0.00"),
    ("38854", "3739.43", "2684.42", "1055.01", "2103.56", "637.21", "0.00"),
    ("38855", "3739.66", "2684.55", "1055.11", "2103.62", "637.22", "0.00"),
    # OHP 48,000
    ("48449", "5947.85", "3970.10", "1977.75", "2674.47", "794.56", "0.00"),
    ("48450", "5948.21", "3970.23", "1977.98", "2674.53", "794.58", "0.00"),
    ("48451", "5948.67", "3970.37", "1978.30", "2674.58", "794.60", "0.00"),
    # OHP 48,600
    ("49055", "6237.17", "4051.30", "2185.87", "2710.52", "804.50", "0.00"),
    ("49056", "6237.54", "4051.43", "2186.11", "2710.58", "804.52", "0.00"),
    ("49057", "6237.78", "4051.57", "2186.21", "2710.64", "804.53", "0.00"),
    # LIFT end
    ("50469", "6562.77", "4240.76", "2322.01", "2794.66", "827.69", "0.00"),
    ("50470", "6562.97", "4240.89", "2322.08", "2794.72", "827.71", "0.00"),
    ("50471", "6563.17", "4241.04", "2322.13", "2794.77", "827.72", "0.00"),
    # ON bracket 1
    ("53384", "7089.43", "4631.36", "2458.07", "2968.10", "875.50", "0.00"),
    ("53385", "7089.60", "4631.49", "2458.11", "2968.16", "875.51", "0.00"),
    ("53386", "7089.83", "4631.63", "2458.20", "2968.22", "875.53", "0.00"),
    # Fed bracket 1
    ("57919", "8092.77", "5239.03", "2853.74", "3237.93", "949.87", "0.00"),
    ("57920", "8093.04", "5239.21", "2853.83", "3237.99", "949.89", "0.00"),
    ("57921", "8093.33", "5239.41", "2853.92", "3238.05", "949.90", "0.00"),
    # EI max 65,700
    ("65699", "10276.23", "6743.63", "3532.60", "3700.84", "1077.46", "0.00"),
    ("65700", "10276.51", "6743.82", "3532.69", "3700.90", "1077.48", "0.00"),
    ("65701", "10276.80", "6744.02", "3532.78", "3700.96", "1077.48", "0.00"),
    # YMPE 71,300
    ("71299", "11865.82", "7839.95", "4025.87", "4034.04", "1077.48", "0.00"),
    ("71300", "11866.11", "7840.15", "4025.96", "4034.10", "1077.48", "0.00"),
    ("71301", "11866.39", "7840.34", "4026.05", "4034.14", "1077.48", "0.00"),
    # OHP 72,000
    ("72735", "12274.56", "8122.55", "4152.01", "4091.50", "1077.48", "0.00"),
    ("72736", "12274.99", "8122.75", "4152.24", "4091.54", "1077.48", "0.00"),
    ("72737", "12275.52", "8122.95", "4152.57", "4091.58", "1077.48", "0.00"),
    # OHP 72,600
    ("73360", "12602.36", "8245.55", "4356.81", "4116.50", "1077.48", "0.00"),
    ("73361", "12602.75", "8245.75", "4357.00", "4116.54", "1077.48", "0.00"),
    ("73362", "12603.04", "8245.95", "4357.09", "4116.58", "1077.48", "0.00"),
    # YAMPE 81,200
    ("81199", "14833.76", "9788.27", "5045.49", "4430.06", "1077.48", "0.00"),
    ("81200", "14834.05", "9788.47", "5045.58", "4430.10", "1077.48", "0.00"),
    ("81201", "14834.34", "9788.67", "5045.67", "4430.10", "1077.48", "0.00"),
    # ON surtax tier 1
    ("96658", "19417.35", "12957.36", "6459.99", "4430.10", "1077.48", "0.00"),
    ("96659", "19417.66", "12957.56", "6460.10", "4430.10", "1077.48", "0.00"),
    ("96660", "19417.97", "12957.77", "6460.20", "4430.10", "1077.48", "0.00"),
    # ON bracket 2
    ("106848", "22625.15", "15046.31", "7578.84", "4430.10", "1077.48", "0.00"),
    ("106849", "22625.46", "15046.51", "7578.95", "4430.10", "1077.48", "0.00"),
    ("106850", "22625.82", "15046.72", "7579.10", "4430.10", "1077.48", "0.00"),
    # ON surtax tier 2
    ("112803", "24643.41", "16267.08", "8376.33", "4430.10", "1077.48", "0.00"),
    ("112804", "24643.77", "16267.29", "8376.48", "4430.10", "1077.48", "0.00"),
    ("112805", "24644.14", "16267.49", "8376.65", "4430.10", "1077.48", "0.00"),
    # Fed bracket 2
    ("115823", "25788.25", "16886.18", "8902.07", "4430.10", "1077.48", "0.00"),
    ("115824", "25788.64", "16886.39", "8902.25", "4430.10", "1077.48", "0.00"),
    ("115825", "25789.06", "16886.64", "8902.42", "4430.10", "1077.48", "0.00"),
    # ON bracket 3
    ("151073", "41090.07", "26051.12", "15038.95", "4430.10", "1077.48", "0.00"),
    ("151074", "41090.51", "26051.38", "15039.13", "4430.10", "1077.48", "0.00"),
    ("151075", "41090.96", "26051.64", "15039.32", "4430.10", "1077.48", "0.00"),
    # Fed bracket 3 / BPA taper start
    ("178955", "53628.48", "33300.44", "20328.04", "4430.10", "1077.48", "0.00"),
    ("178956", "53628.93", "33300.70", "20328.23", "4430.10", "1077.48", "0.00"),
    ("178957", "53629.41", "33300.99", "20328.42", "4430.10", "1077.48", "0.00"),
    # OHP 200,000
    ("201073", "64305.92", "39782.18", "24523.74", "4430.10", "1077.48", "0.00"),
    ("201074", "64306.40", "39782.47", "24523.93", "4430.10", "1077.48", "0.00"),
    ("201075", "64307.14", "39782.77", "24524.37", "4430.10", "1077.48", "0.00"),
    # OHP 200,600
    ("201673", "64745.32", "39958.01", "24787.31", "4430.10", "1077.48", "0.00"),
    ("201674", "64746.06", "39958.31", "24787.75", "4430.10", "1077.48", "0.00"),
    ("201675", "64746.53", "39958.60", "24787.93", "4430.10", "1077.48", "0.00"),
    # ON bracket 4
    ("221073", "74110.93", "45643.27", "28467.66", "4430.10", "1077.48", "0.00"),
    ("221074", "74111.41", "45643.56", "28467.85", "4430.10", "1077.48", "0.00"),
    ("221075", "74111.90", "45643.85", "28468.05", "4430.10", "1077.48", "0.00"),
    # Fed bracket 4 / BPA taper end
    ("254487", "90762.79", "55435.38", "35327.41", "4430.10", "1077.48", "0.00"),
    ("254488", "90763.28", "55435.68", "35327.60", "4430.10", "1077.48", "0.00"),
    ("254489", "90763.82", "55436.01", "35327.81", "4430.10", "1077.48", "0.00"),
]  # fmt: skip

# Printed bracket columns: (more than, rate, line 75 / line 7 constant). A taxable income equal to
# a column's upper bound belongs to that column ("not more than"), so the edge is in the lower one.
FEDERAL_COLUMNS = (  # T1 General line 75 (CRA 5000-D1), taxable income at line 26000
    ("0", "0.145", "0.00"),
    ("57375", "0.205", "8319.38"),
    ("114750", "0.26", "20081.25"),
    ("177882", "0.29", "36495.57"),
    ("253414", "0.33", "58399.85"),
)
ONTARIO_COLUMNS = (  # ON428 Part A line 7 (CRA 5006-C)
    ("0", "0.0505", "0.00"),
    ("52886", "0.0915", "2670.74"),
    ("105775", "0.1116", "7510.09"),
    ("150000", "0.1216", "12445.60"),
    ("220000", "0.1316", "20957.60"),
)


def cents(amount: Decimal) -> Decimal:
    return amount.quantize(D("0.01"), rounding=ROUND_HALF_UP)


def tax_on(taxable: Decimal, columns: tuple[tuple[str, str, str], ...]) -> Decimal:
    """The form's own arithmetic: pick the column ("more than" its start); line 4 or 72 is the
    excess, line 6 or 74 the excess times the printed rate to the cent, plus the constant."""
    start, rate, constant = [c for c in columns if taxable > D(c[0]) or c[0] == "0"][-1]
    return cents((taxable - D(start)) * D(rate)) + D(constant)


def enhanced_cpp_deduction(salary: Decimal) -> Decimal:
    """T1 line 22215 for a salary alone: Schedule 8 line 12 (1% of earnings between the 3,500
    exemption and the 71,300 ceiling) and line 28 from 81,200 up (CPP2 396.00, ceiling 81,200).
    Between the two, line 22 adds 4% of the earnings over 71,300 to the line 12 maximum 678.00."""
    if salary >= D("81200"):
        return D("1074.00")
    if salary > D("71300"):
        return D("678.00") + cents((salary - D("71300")) * D("0.04"))
    return cents(max(salary - D("3500"), D("0")) * D("0.01"))


# A salary inside every federal and every Ontario column, and the exact edge of each column with
# the salary one dollar above. Salaries are chosen so that taxable income (line 26000 =
# salary less the line 22215 deduction) is exactly the printed bound: for example 115,824.00 less
# 1,074.00 is 114,750.00 (federal edge, the 20,081.26 case) and 53,384.85 less 498.85 is 52,886.00.
BRACKET_SALARIES = [
    "0", "30000", "75000", "53384.85", "53385.86", "57919.19", "57920.20", "70000", "115824",
    "115825",
    "106849", "106850", "130000", "151074", "151075", "160000", "178956", "178957", "200000",
    "221074", "221075", "240000", "254488", "254489", "275000",
]  # fmt: skip


def run(take_home_service: TakeHomeService, salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return take_home_service(HEADER, RETURN, *PARTS).compute(
        CODE, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )


def sheet(worksheets: dict[str, tuple[Worksheet, ...]], form: str) -> Worksheet:
    (found,) = worksheets[form]
    return found


def test_every_line_matches_the_printed_form(
    take_home_service: TakeHomeService,
) -> None:
    t1 = sheet(run(take_home_service, "70000"), "ca/t1_tax_and_credits")

    assert {line: t1.get(kind).value for line, (kind, _) in T1_AT_70000.items()} == {
        line: D(figure) for line, (_, figure) in T1_AT_70000.items()
    }


def test_every_dollar_line_is_printed_to_the_cent(take_home_service: TakeHomeService) -> None:
    # Decimal equality ignores scale, so a whole-dollar figure would pass the table above: every
    # dollar line is two decimals (line 71 is the printed whole-dollar bound and line 73 a rate).
    t1 = sheet(run(take_home_service, "70000"), "ca/t1_tax_and_credits")

    assert {
        line: t1.get(kind).value.as_tuple().exponent
        for line, (kind, _) in T1_AT_70000.items()
        if line not in PRINTED_AS_IS
    } == {line: -2 for line in T1_AT_70000 if line not in PRINTED_AS_IS}


def test_line_42800_names_ontario_line_90_in_the_trace(take_home_service: TakeHomeService) -> None:
    t1 = sheet(run(take_home_service, "70000"), "ca/t1_tax_and_credits")

    assert "Line 90 of ON428 (CA$3911.45) gives CA$3911.45." in (
        EnglishTraceRenderer().render_all(t1.trace, t1)
    )


@pytest.mark.parametrize(
    ("given", "line_130", "line_40600", "line_167"),
    [
        # Nothing given: the salary-only return.
        ({}, "7585.64", "7585.64", "11497.09"),
        # Line 10400, other employment income of 500.00: 70,500.00 of income, tax 7,733.14.
        ({"10400": "500"}, None, None, "11645.34"),
        # Line 40500, a foreign tax credit of 1,000.00, comes off the federal tax.
        ({"40500": "1000"}, "6585.64", "6585.64", "10497.09"),
        # Line 133, a logging tax credit of 100.00, comes off line 132 to give line 40600.
        ({"133": "100"}, "7585.64", "7485.64", "11397.09"),
        # A foreign tax credit above the federal tax: line 130 is signed and goes negative, line
        # 40600 stops at 0.00 and line 167 is the Ontario tax alone.
        ({"40500": "9000"}, "-1414.36", "0.00", "3911.45"),
    ],
)
def test_the_optional_inputs_route_through_the_chain(
    take_home_service: TakeHomeService,
    given: dict[str, str],
    line_130: str | None,
    line_40600: str | None,
    line_167: str,
) -> None:
    # The line tests cover each optional input alone; here one return types them in beside the
    # salary and the real chain from the input to line 167 is read.
    kinds_by_line = {
        "10400": OTHER_EMPLOYMENT_INCOME,
        "40500": FEDERAL_FOREIGN_TAX_CREDIT,
        "133": FEDERAL_LOGGING_TAX_CREDIT,
    }
    worksheets = take_home_service(HEADER, RETURN, *PARTS).compute(
        CODE,
        2025,
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        *(Artifact(kinds_by_line[line], D(value)) for line, value in given.items()),
    )
    t1 = sheet(worksheets, "ca/t1_tax_and_credits")

    if line_130 is not None:
        assert t1.get(FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT).value == D(line_130)
    if line_40600 is not None:
        assert t1.get(FEDERAL_TAX).value == D(line_40600)
    assert t1.get(REFUND_OR_BALANCE_OWING).value == D(line_167)


def assert_the_return_and_its_payroll_figures(
    take_home_service: TakeHomeService,
    salary: str,
    line_167: str,
    federal: str,
    ontario: str,
    cpp: str,
    ei: str,
    cwb: str,
) -> None:
    worksheets = run(take_home_service, salary)
    t1 = sheet(worksheets, "ca/t1_tax_and_credits")

    # The return's one output is T1 line 167, and line 167 is federal tax plus Ontario tax less
    # the credits the filer has (here only the Canada workers benefit and the EI overpayment).
    assert sheet(worksheets, "ca-on/return").get(REFUND_OR_BALANCE_OWING).value == D(line_167)
    assert t1.get(FEDERAL_TAX_AFTER_CREDITS).value == D(federal)
    assert t1.get(PROVINCIAL_TAX_LINE_42800).value == D(ontario)
    assert t1.get(CWB_LINE_45300).value == D(cwb)
    schedule_8 = sheet(worksheets, "ca/schedule_8")
    assert (
        schedule_8.get(SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN).value
        + schedule_8.get(SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value
    ) == D(cpp)
    assert sheet(worksheets, "ca/t2204").get(T2204_PREMIUMS_DEDUCTED).value == D(ei)


@pytest.mark.parametrize(("salary", "line_167", "federal", "ontario", "cpp", "ei", "cwb"), ANCHORS)
def test_the_return_and_its_payroll_figures(
    take_home_service: TakeHomeService,
    salary: str,
    line_167: str,
    federal: str,
    ontario: str,
    cpp: str,
    ei: str,
    cwb: str,
) -> None:
    assert_the_return_and_its_payroll_figures(
        take_home_service, salary, line_167, federal, ontario, cpp, ei, cwb
    )


@pytest.mark.parametrize(
    ("salary", "line_167", "federal", "ontario", "cpp", "ei", "cwb"), BOUNDARY_ANCHORS
)
def test_the_return_and_its_payroll_figures_at_the_boundaries(
    take_home_service: TakeHomeService,
    salary: str,
    line_167: str,
    federal: str,
    ontario: str,
    cpp: str,
    ei: str,
    cwb: str,
) -> None:
    assert_the_return_and_its_payroll_figures(
        take_home_service, salary, line_167, federal, ontario, cpp, ei, cwb
    )


def test_line_167_adds_the_ontario_tax_once_and_never_the_health_premium_again(
    take_home_service: TakeHomeService,
) -> None:
    # ON428 line 90 already holds the Ontario health premium (line 89, 600.00 at $70,000), so
    # line 167 is exactly line 42900 plus line 42800.
    worksheets = run(take_home_service, "70000")
    t1 = sheet(worksheets, "ca/t1_tax_and_credits")

    assert sheet(worksheets, "ca-on/on428").get(ON428_ONTARIO_TAX_LINE_90).value == D("3911.45")
    assert t1.get(REFUND_OR_BALANCE_OWING).value == (
        t1.get(FEDERAL_TAX_AFTER_CREDITS).value + t1.get(PROVINCIAL_TAX_LINE_42800).value
    )


@pytest.mark.parametrize("salary", BRACKET_SALARIES)
def test_the_bracket_lines_follow_the_printed_columns_at_every_salary(
    take_home_service: TakeHomeService, salary: str
) -> None:
    # Federal line 76 and ON428 line 8 are the printed-constant arithmetic of the taxable income
    # (salary less the line 22215 deduction); line 167 is the federal tax after credits plus the
    # Ontario tax (line 90, which holds the health premium and surtax), and it has two decimals.
    worksheets = run(take_home_service, salary)
    t1 = sheet(worksheets, "ca/t1_tax_and_credits")
    on428 = sheet(worksheets, "ca-on/on428")
    taxable = D(salary) - enhanced_cpp_deduction(D(salary))

    assert t1.get(FEDERAL_TAX_TAXABLE_INCOME_LINE_70).value == taxable
    assert on428.get(ON428_TAXABLE_INCOME_LINE_1).value == taxable
    assert t1.get(FEDERAL_TAX_ON_TAXABLE_INCOME_LINE_76).value == tax_on(taxable, FEDERAL_COLUMNS)
    assert on428.get(ON428_TAX_ON_TAXABLE_INCOME_LINE_8).value == tax_on(taxable, ONTARIO_COLUMNS)
    line_167 = sheet(worksheets, "ca-on/return").get(REFUND_OR_BALANCE_OWING).value
    assert (
        line_167
        == t1.get(FEDERAL_TAX_AFTER_CREDITS).value
        + on428.get(ON428_ONTARIO_TAX_LINE_90).value
        - t1.get(CWB_LINE_45300).value
        - t1.get(EI_OVERPAYMENT_LINE_45000).value
    )
    assert line_167.as_tuple().exponent == -2


def test_the_federal_edge_at_114750_belongs_to_the_lower_column(
    take_home_service: TakeHomeService,
) -> None:
    # T1 line 75 prints "more than 57,375 but not more than 114,750": the lower column applies at
    # exactly 114,750, so line 74 is 20.5% of 57,375.00 = 11,761.875 -> 11,761.88 and line 76 is
    # 8,319.38 + 11,761.88 = 20,081.26 (the next column's constant is 20,081.25).
    t1 = sheet(run(take_home_service, "115824"), "ca/t1_tax_and_credits")

    assert t1.get(FEDERAL_TAX_ON_TAXABLE_INCOME_LINE_76).value == D("20081.26")


def test_a_negative_salary_is_refused(take_home_service: TakeHomeService) -> None:
    with pytest.raises(NegativeArtifactError, match="ca/employment_income cannot be negative"):
        run(take_home_service, "-1")


def test_the_ninety_thousand_dollar_return_matches_the_hand_computed_chain(
    take_home_service: TakeHomeService,
) -> None:
    # $90,000: line 22215 is 678.00 + 396.00 = 1,074.00, so taxable income is 88,926.00; line 76 is
    # 14,787.34 (8,319.38 + 20.5% x 31,551.00) and the credits are 14.5% of the
    # credit amounts; the federal tax after credits is 11,592.47.
    worksheets = run(take_home_service, "90000")
    t1 = sheet(worksheets, "ca/t1_tax_and_credits")
    schedule_8 = sheet(worksheets, "ca/schedule_8")

    assert t1.get(FEDERAL_TAX_TAXABLE_INCOME_LINE_70).value == D("88926.00")
    assert t1.get(FEDERAL_TAX_ON_TAXABLE_INCOME_LINE_76).value == D("14787.34")
    assert t1.get(NON_REFUNDABLE_TAX_CREDITS).value == D("3194.87")
    assert t1.get(FEDERAL_TAX_AFTER_CREDITS).value == D("11592.47")
    assert schedule_8.get(SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("1074.00")
    assert sheet(worksheets, "ca/t2204").get(T2204_PREMIUMS_DEDUCTED).value == D("1077.48")


def test_the_two_thousand_dollar_refund_is_the_ei_overpayment(
    take_home_service: TakeHomeService,
) -> None:
    # The EI overpayment of line 45000 (22.96, T2204 line 15) is the whole of the refund
    # because no tax is owing and the Canada workers benefit is 0 (working income
    # is under 3,000).
    worksheets = run(take_home_service, "2010")
    t1 = sheet(worksheets, "ca/t1_tax_and_credits")

    assert t1.get(EI_OVERPAYMENT_LINE_45000).value == D("22.96")
    assert t1.get(CWB_LINE_45300).value == D("0.00")
    assert t1.get(REFUND_OR_BALANCE_OWING).value == D("-22.96")
