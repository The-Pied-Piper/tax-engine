"""The 2025 donations and gifts figures and arithmetic, checked against CRA's Schedule 9 and the
Federal Worksheet.

2025 Schedule 9 (form 5000-S9), front: "Line 6: Enter your net income from line 23600 of your
return. Line A multiplied by 75% ="; "Line 7: Amount B plus amount C Line D = multiplied by 25%
="; "Line 8: Line 6 plus line 7 ="; "Line 9: Enter whichever is less: amount A or line 8. Total
charitable donations limit"; "Line 13: Enter whichever is less: amount from line 12 or $200.";
"Line 18: Income threshold 253,414.00"; back: "Line 20: Enter whichever is less: amount from line
16 or line 19. Line F multiplied by 33% ="; "Line 21: Amount E minus amount F Line G =
multiplied by 29% ="; "Line 22: Amount from line 13 of the previous page Line H multiplied by
14.5% ="; "Line 23: Add lines 20 to 22. Enter this amount on line 34900 of your return.
Allowable donations for 2025 =". Federal Worksheet (form 5000-D1), "Line 34990 - Top-up tax
credit": "Line 4: 8,319.38"; "Line 6: Applicable rate 3.45%"; "Line 7: Line 5 multiplied by the
percentage from line 6 Enter this amount on line 34990 of your return. =". Each percentage is a
rate (the `rate` kind); the $200, the 253,414.00 and the 8,319.38 are amounts claimed whole
(the `credit` kind, as the basic reduction is). Every box is dollars and cents, so each product
is rounded half-up to the cent; the sums, differences and lessers take amounts already in cents.

Line A is the net income itself: line 9 is the lesser of the net income and line 8 (line 6 plus
line 7), not of line 6 and line 8, so the 25% of the gifts of capital property can raise the
limit above 75% of the net income, up to the net income.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capability import Capability
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
S9_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s9/5000-s9-25e.txt"
D1_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-d1/5000-d1-25e.txt"

NET_INCOME_RATE = "ca/donation_net_income_rate"
CAPITAL_GIFTS_RATE = "ca/capital_gifts_limit_rate"
FIRST_TIER_MAXIMUM = "ca/donation_first_tier_maximum"
HIGH_INCOME_THRESHOLD = "ca/donation_high_income_threshold"
HIGH_INCOME_RATE = "ca/donation_high_income_rate"
REGULAR_RATE = "ca/donation_regular_rate"
FIRST_TIER_RATE = "ca/donation_first_tier_rate"
TOP_UP_THRESHOLD = "ca/top_up_threshold"
TOP_UP_RATE = "ca/top_up_rate"

# Made up for this test and not registered: one kind for each line of the schedule, the chart
# lines and the worksheet, named for the line.
NET_INCOME = ArtifactKind("ex/net_income", Decimal)
TAXABLE_INCOME = ArtifactKind("ex/taxable_income", Decimal)
LINE_1 = ArtifactKind("ex/line_1", Decimal)
LINE_2 = ArtifactKind("ex/line_2", Decimal)
LINE_3 = ArtifactKind("ex/line_3", Decimal)
LINE_4 = ArtifactKind("ex/line_4", Decimal)
LINE_5 = ArtifactKind("ex/line_5", Decimal)
LINE_6 = ArtifactKind("ex/line_6", Decimal)
LINE_7 = ArtifactKind("ex/line_7", Decimal)
LINE_8 = ArtifactKind("ex/line_8", Decimal)
LINE_9 = ArtifactKind("ex/line_9", Decimal)
LINE_10 = ArtifactKind("ex/line_10", Decimal)
LINE_11 = ArtifactKind("ex/line_11", Decimal)
LINE_12 = ArtifactKind("ex/line_12", Decimal)
FIRST_TIER_CAP = ArtifactKind("ex/first_tier_cap", Decimal)
LINE_13 = ArtifactKind("ex/line_13", Decimal)
LINE_14 = ArtifactKind("ex/line_14", Decimal)
LINE_15 = ArtifactKind("ex/line_15", Decimal)
LINE_16 = ArtifactKind("ex/line_16", Decimal)
THRESHOLD = ArtifactKind("ex/threshold", Decimal)
LINE_19 = ArtifactKind("ex/line_19", Decimal)
LINE_F = ArtifactKind("ex/line_f", Decimal)
LINE_20 = ArtifactKind("ex/line_20", Decimal)
LINE_G = ArtifactKind("ex/line_g", Decimal)
LINE_21 = ArtifactKind("ex/line_21", Decimal)
LINE_22 = ArtifactKind("ex/line_22", Decimal)
LINE_23 = ArtifactKind("ex/line_23", Decimal)
LINE_B = ArtifactKind("ex/line_b", Decimal)
LINE_C = ArtifactKind("ex/line_c", Decimal)
LINE_D = ArtifactKind("ex/line_d", Decimal)
DEPRECIABLE_1 = ArtifactKind("ex/depreciable_line_1", Decimal)
DEPRECIABLE_2 = ArtifactKind("ex/depreciable_line_2", Decimal)
DEPRECIABLE_3 = ArtifactKind("ex/depreciable_line_3", Decimal)
DEPRECIABLE_4 = ArtifactKind("ex/depreciable_line_4", Decimal)
CAPITAL_1 = ArtifactKind("ex/capital_line_1", Decimal)
CAPITAL_2 = ArtifactKind("ex/capital_line_2", Decimal)
CREDITS_AT_RATE = ArtifactKind("ex/credit_amounts_at_credit_rate", Decimal)
TOP_UP_3 = ArtifactKind("ex/top_up_line_3", Decimal)
TOP_UP_4 = ArtifactKind("ex/top_up_line_4", Decimal)
TOP_UP_5 = ArtifactKind("ex/top_up_line_5", Decimal)
TOP_UP_7 = ArtifactKind("ex/top_up_line_7", Decimal)


def rated(family: str, base: Money, output: Money) -> ApplyRate:
    return ApplyRate(SOURCE.get(family, 2025, RATE), base, output)


def claimed(family: str, output: Money) -> CreditAmount:
    return CreditAmount(SOURCE.get(family, 2025, CREDIT), output)


def depreciable_chart() -> tuple[Capability, ...]:
    """The chart for line 33700: line 4, then line 5 (line B)."""
    return (
        LesserOf((DEPRECIABLE_2, DEPRECIABLE_3), DEPRECIABLE_4),
        LesserOf((DEPRECIABLE_1, DEPRECIABLE_4), LINE_B),
    )


def capital_chart() -> tuple[Capability, ...]:
    """The chart for line 33900: line 3 (line C)."""
    return (Subtract(CAPITAL_1, CAPITAL_2, LINE_C),)


def schedule_9() -> tuple[Capability, ...]:
    """Schedule 9, front and back, from the charts' lines B and C to line 23, in line order."""
    return (
        Sum((LINE_1, LINE_2, LINE_3, LINE_4), LINE_5),
        rated(NET_INCOME_RATE, NET_INCOME, LINE_6),
        Sum((LINE_B, LINE_C), LINE_D),
        rated(CAPITAL_GIFTS_RATE, LINE_D, LINE_7),
        Sum((LINE_6, LINE_7), LINE_8),
        LesserOf((NET_INCOME, LINE_8), LINE_9),
        LesserOf((LINE_5, LINE_9), LINE_10),
        Sum((LINE_10, LINE_11), LINE_12),
        claimed(FIRST_TIER_MAXIMUM, FIRST_TIER_CAP),
        LesserOf((LINE_12, FIRST_TIER_CAP), LINE_13),
        Subtract(LINE_12, LINE_13, LINE_14),
        SubtractNotBelowZero(LINE_14, LINE_15, LINE_16),
        claimed(HIGH_INCOME_THRESHOLD, THRESHOLD),
        SubtractNotBelowZero(TAXABLE_INCOME, THRESHOLD, LINE_19),
        LesserOf((LINE_16, LINE_19), LINE_F),
        rated(HIGH_INCOME_RATE, LINE_F, LINE_20),
        Subtract(LINE_14, LINE_F, LINE_G),
        rated(REGULAR_RATE, LINE_G, LINE_21),
        rated(FIRST_TIER_RATE, LINE_13, LINE_22),
        Sum((LINE_20, LINE_21, LINE_22), LINE_23),
    )


def top_up() -> tuple[Capability, ...]:
    """The Federal Worksheet's line 34990 calculation, from line 33800 and Schedule 9 line 22."""
    return (
        Sum((CREDITS_AT_RATE, LINE_22), TOP_UP_3),
        claimed(TOP_UP_THRESHOLD, TOP_UP_4),
        SubtractNotBelowZero(TOP_UP_3, TOP_UP_4, TOP_UP_5),
        rated(TOP_UP_RATE, TOP_UP_5, TOP_UP_7),
    )


def run(start: dict[Money, str], *capabilities: Capability) -> dict[Money, Decimal]:
    """Run `capabilities` in the order given over the starting amounts; every amount by kind."""
    known = {kind: D(value) for kind, value in start.items()}
    for capability in capabilities:
        result = capability.compute(tuple(Artifact(kind, v) for kind, v in known.items()))
        for artifact in result.outputs:
            known[artifact.kind] = artifact.value
    return known


def donations(
    net_income: str,
    taxable_income: str,
    line_1: str = "0",
    line_2: str = "0",
    line_3: str = "0",
    line_4: str = "0",
    line_11: str = "0",
    line_15: str = "0",
    depreciable: tuple[str, str, str] = ("0", "0", "0"),
    capital: tuple[str, str] = ("0", "0"),
) -> dict[Money, Decimal]:
    """Schedule 9 and both charts for the inputs given, as the schedule takes them."""
    return run(
        {
            NET_INCOME: net_income,
            TAXABLE_INCOME: taxable_income,
            LINE_1: line_1,
            LINE_2: line_2,
            LINE_3: line_3,
            LINE_4: line_4,
            LINE_11: line_11,
            LINE_15: line_15,
            DEPRECIABLE_1: depreciable[0],
            DEPRECIABLE_2: depreciable[1],
            DEPRECIABLE_3: depreciable[2],
            CAPITAL_1: capital[0],
            CAPITAL_2: capital[1],
        },
        *depreciable_chart(),
        *capital_chart(),
        *schedule_9(),
    )


@pytest.mark.parametrize(
    ("family", "value"),
    [
        (NET_INCOME_RATE, "0.75"),
        (CAPITAL_GIFTS_RATE, "0.25"),
        (HIGH_INCOME_RATE, "0.33"),
        (REGULAR_RATE, "0.29"),
        (FIRST_TIER_RATE, "0.145"),
    ],
)
def test_2025_schedule_9_rates(family: str, value: str) -> None:
    data = SOURCE.get(family, 2025, RATE)

    assert data.values == Rate(D(value))
    # Schedule 9 lines 6, 7, 20, 21 and 22, dollars-and-cents boxes: half-up to the cent.
    assert data.rounding == CENT


@pytest.mark.parametrize(
    ("family", "value"),
    [
        (FIRST_TIER_MAXIMUM, "200"),
        (HIGH_INCOME_THRESHOLD, "253414.00"),
        (TOP_UP_THRESHOLD, "8319.38"),
    ],
)
def test_2025_schedule_9_and_worksheet_amounts(family: str, value: str) -> None:
    data = SOURCE.get(family, 2025, CREDIT)

    assert data.values == Credit(amount=D(value))
    # Schedule 9 lines 13 and 18 and Federal Worksheet line 4, dollars-and-cents boxes.
    assert data.rounding == CENT


def test_2025_top_up_rate_is_3_45_percent() -> None:
    data = SOURCE.get(TOP_UP_RATE, 2025, RATE)

    assert data.values == Rate(D("0.0345"))
    # Federal Worksheet line 7, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_schedule_9_datasets_cite_only_the_schedule_9_text() -> None:
    for family in (NET_INCOME_RATE, CAPITAL_GIFTS_RATE, HIGH_INCOME_RATE, REGULAR_RATE):
        assert SOURCE.get(family, 2025, RATE).sources == (S9_TEXT,), family
    assert SOURCE.get(FIRST_TIER_RATE, 2025, RATE).sources == (S9_TEXT,)
    assert SOURCE.get(FIRST_TIER_MAXIMUM, 2025, CREDIT).sources == (S9_TEXT,)
    assert SOURCE.get(HIGH_INCOME_THRESHOLD, 2025, CREDIT).sources == (S9_TEXT,)


def test_2025_top_up_datasets_cite_only_the_federal_worksheet_text() -> None:
    assert SOURCE.get(TOP_UP_THRESHOLD, 2025, CREDIT).sources == (D1_TEXT,)
    assert SOURCE.get(TOP_UP_RATE, 2025, RATE).sources == (D1_TEXT,)


def test_the_worked_example() -> None:
    # Net income 60000, taxable income 55000, donations to registered charities 1500 (line 1).
    lines = donations("60000", "55000", line_1="1500")

    assert lines[LINE_5] == D("1500")
    assert lines[LINE_6] == D("45000.00")
    assert lines[LINE_9] == D("45000.00")
    assert lines[LINE_10] == D("1500")
    assert lines[LINE_12] == D("1500")
    assert lines[LINE_13] == D("200")
    assert lines[LINE_14] == D("1300")
    assert lines[LINE_16] == D("1300")
    assert lines[LINE_19] == D("0")
    assert lines[LINE_F] == D("0")
    assert lines[LINE_20] == D("0.00")
    assert lines[LINE_G] == D("1300")
    assert lines[LINE_21] == D("377.00")
    assert lines[LINE_22] == D("29.00")
    assert lines[LINE_23] == D("406.00")


def test_taxable_income_over_the_threshold_charges_33_percent_on_line_f() -> None:
    # Taxable income 300000, line 16 of 50000: line 19 = 300000 - 253414.00 = 46586, below line
    # 16, so line F = 46586 and line 20 = 33% x 46586 = 15373.38; line G = 50000 - 46586 = 3414
    # at 29% = 990.06; line 22 = 14.5% x 200 = 29.00; line 23 = 16392.44.
    lines = donations("310000", "300000", line_1="50200")

    assert lines[LINE_12] == D("50200")
    assert lines[LINE_13] == D("200")
    assert lines[LINE_14] == D("50000")
    assert lines[LINE_16] == D("50000")
    assert lines[LINE_19] == D("46586.00")
    assert lines[LINE_F] == D("46586.00")
    assert lines[LINE_20] == D("15373.38")
    assert lines[LINE_G] == D("3414.00")
    assert lines[LINE_21] == D("990.06")
    assert lines[LINE_22] == D("29.00")
    assert lines[LINE_23] == D("16392.44")


def test_line_f_is_line_16_when_line_19_is_larger() -> None:
    # Taxable income 400000: line 19 = 146586.00, above line 16 of 50000, so line F = 50000 and
    # the whole of line 14 is at 33%: 16500.00; line G = 0.
    lines = donations("400000", "400000", line_1="50200")

    assert lines[LINE_19] == D("146586.00")
    assert lines[LINE_F] == D("50000")
    assert lines[LINE_20] == D("16500.00")
    assert lines[LINE_G] == D("0")
    assert lines[LINE_21] == D("0.00")
    assert lines[LINE_23] == D("16529.00")


@pytest.mark.parametrize(
    ("taxable_income", "line_19"),
    [
        ("253414.00", "0"),
        ("253414.01", "0.01"),
        ("253413.99", "0"),
        ("0", "0"),
        ("300000", "46586.00"),
    ],
)
def test_line_19_is_taxable_income_over_the_threshold_not_below_zero(
    taxable_income: str, line_19: str
) -> None:
    lines = donations("400000", taxable_income, line_1="1000")

    assert lines[THRESHOLD] == D("253414.00")
    assert lines[LINE_19] == D(line_19)


def test_the_75_percent_of_the_net_income_limits_the_donations() -> None:
    # Net income 10000: line 6 = 7500.00; no gifts of capital property, so line 8 = 7500.00 and
    # line 9 = the lesser of 10000 and 7500.00. Donations of 9000 are limited to 7500.00.
    lines = donations("10000", "10000", line_1="9000")

    assert lines[LINE_5] == D("9000")
    assert lines[LINE_6] == D("7500.00")
    assert lines[LINE_7] == D("0.00")
    assert lines[LINE_8] == D("7500.00")
    assert lines[LINE_9] == D("7500.00")
    assert lines[LINE_10] == D("7500.00")
    assert lines[LINE_14] == D("7300.00")
    # Taxable income of 10000 is below the threshold, so everything above 200 is at 29%.
    assert lines[LINE_20] == D("0.00")
    assert lines[LINE_21] == D("2117.00")
    assert lines[LINE_22] == D("29.00")
    assert lines[LINE_23] == D("2146.00")


def test_gifts_of_capital_property_raise_the_limit_above_75_percent() -> None:
    # Depreciable property (chart for line 33700): recaptured depreciation 3000 (line 1), net
    # proceeds 5000 (line 2), capital cost 4000 (line 3): line 4 = 4000, line 5 = 3000 (line B).
    # Other capital property (chart for line 33900): taxable gains 4000 less the gains deduction
    # 1000 = 3000 (line C). Line D = 6000; line 7 = 25% x 6000 = 1500.00; line 8 = 7500.00 +
    # 1500.00 = 9000.00; line 9 = the lesser of the net income 10000 and 9000.00.
    lines = donations(
        "10000",
        "10000",
        line_1="9000",
        depreciable=("3000", "5000", "4000"),
        capital=("4000", "1000"),
    )

    assert lines[DEPRECIABLE_4] == D("4000")
    assert lines[LINE_B] == D("3000")
    assert lines[LINE_C] == D("3000")
    assert lines[LINE_D] == D("6000")
    assert lines[LINE_6] == D("7500.00")
    assert lines[LINE_7] == D("1500.00")
    assert lines[LINE_8] == D("9000.00")
    assert lines[LINE_9] == D("9000.00")
    assert lines[LINE_10] == D("9000.00")
    assert lines[LINE_14] == D("8800.00")
    assert lines[LINE_21] == D("2552.00")
    assert lines[LINE_23] == D("2581.00")


def test_the_net_income_itself_limits_the_donations_when_line_8_is_larger() -> None:
    # Recaptured depreciation 20000, net proceeds 30000, capital cost 25000: line 4 = 25000,
    # line B = 20000. Line 7 = 25% x 20000 = 5000.00, line 8 = 7500.00 + 5000.00 = 12500.00,
    # more than the net income 10000, so line 9 = 10000 and the donations of 15000 are limited
    # to it.
    lines = donations("10000", "10000", line_1="15000", depreciable=("20000", "30000", "25000"))

    assert lines[LINE_B] == D("20000")
    assert lines[LINE_8] == D("12500.00")
    assert lines[LINE_9] == D("10000")
    assert lines[LINE_10] == D("10000")
    assert lines[LINE_14] == D("9800")
    assert lines[LINE_21] == D("2842.00")
    assert lines[LINE_23] == D("2871.00")


@pytest.mark.parametrize(
    ("recaptured", "proceeds", "cost", "line_4", "line_5"),
    [
        # Line 4 is the lesser of the proceeds and the cost; line 5 the lesser of line 1 and it.
        ("3000", "5000", "4000", "4000", "3000"),
        ("3000", "3500", "4000", "3500", "3000"),
        ("3000", "2000", "4000", "2000", "2000"),
        ("0", "5000", "4000", "4000", "0"),
        ("4000", "4000", "4000", "4000", "4000"),
    ],
)
def test_the_depreciable_property_chart(
    recaptured: str, proceeds: str, cost: str, line_4: str, line_5: str
) -> None:
    lines = run(
        {DEPRECIABLE_1: recaptured, DEPRECIABLE_2: proceeds, DEPRECIABLE_3: cost},
        *depreciable_chart(),
    )

    assert lines[DEPRECIABLE_4] == D(line_4)
    assert lines[LINE_B] == D(line_5)


@pytest.mark.parametrize(
    ("gains", "deduction", "line_3"),
    [("4000", "1000", "3000"), ("4000", "0", "4000"), ("4000", "4000", "0"), ("0", "0", "0")],
)
def test_the_capital_property_chart(gains: str, deduction: str, line_3: str) -> None:
    lines = run({CAPITAL_1: gains, CAPITAL_2: deduction}, *capital_chart())

    assert lines[LINE_C] == D(line_3)


def test_lines_1_to_4_are_added_and_the_gifts_of_line_11_join_line_12() -> None:
    # Lines 1 to 4: 500 + 300.50 + 200 + 99.50 = 1100.00. Ecological and cultural gifts of 400
    # (line 11) join line 10: line 12 = 1500.00.
    lines = donations(
        "100000",
        "100000",
        line_1="500",
        line_2="300.50",
        line_3="200",
        line_4="99.50",
        line_11="400",
    )

    assert lines[LINE_5] == D("1100.00")
    assert lines[LINE_10] == D("1100.00")
    assert lines[LINE_12] == D("1500.00")
    assert lines[LINE_13] == D("200")
    assert lines[LINE_14] == D("1300.00")


def test_ecological_gifts_before_2016_come_off_line_14_for_the_33_percent() -> None:
    # Charitable donations 100000 and ecological gifts of 20000 (line 11), of which 15000 were
    # made before 2016 (line 15). Line 12 = 120000, line 14 = 119800, line 16 = 119800 - 15000 =
    # 104800. Taxable income 400000: line 19 = 146586.00, line F = 104800, line 20 = 33% x
    # 104800 = 34584.00; line G = 119800 - 104800 = 15000, at 29% = 4350.00; line 22 = 29.00.
    lines = donations("400000", "400000", line_1="100000", line_11="20000", line_15="15000")

    assert lines[LINE_12] == D("120000")
    assert lines[LINE_14] == D("119800")
    assert lines[LINE_16] == D("104800")
    assert lines[LINE_F] == D("104800")
    assert lines[LINE_20] == D("34584.00")
    assert lines[LINE_G] == D("15000")
    assert lines[LINE_21] == D("4350.00")
    assert lines[LINE_23] == D("38963.00")


def test_line_16_is_not_below_zero() -> None:
    # Ecological gifts before 2016 of 300 exceed line 14 of 100: line 16 is 0, line F is 0, and
    # line G is all of line 14.
    lines = donations("400000", "400000", line_1="100", line_11="200", line_15="300")

    assert lines[LINE_12] == D("300")
    assert lines[LINE_14] == D("100")
    assert lines[LINE_16] == D("0")
    assert lines[LINE_F] == D("0")
    assert lines[LINE_G] == D("100")
    assert lines[LINE_21] == D("29.00")
    assert lines[LINE_22] == D("29.00")
    assert lines[LINE_23] == D("58.00")


def test_donations_of_200_or_less_are_all_at_14_5_percent() -> None:
    lines = donations("60000", "55000", line_1="150")

    assert lines[LINE_13] == D("150")
    assert lines[LINE_14] == D("0")
    assert lines[LINE_21] == D("0.00")
    assert lines[LINE_22] == D("21.75")
    assert lines[LINE_23] == D("21.75")


def test_no_donations_give_zero_everywhere() -> None:
    lines = donations("60000", "55000")

    for line in (LINE_5, LINE_10, LINE_12, LINE_13, LINE_14, LINE_16, LINE_F, LINE_G):
        assert lines[line] == D("0"), line.identifier
    for line in (LINE_20, LINE_21, LINE_22, LINE_23):
        assert lines[line] == D("0.00"), line.identifier
    assert lines[LINE_6] == D("45000.00")
    assert lines[LINE_9] == D("45000.00")


@pytest.mark.parametrize(
    ("line_1", "line_20", "line_21", "line_22", "line_23"),
    [
        # Each product is rounded half-up to the cent on its own line.
        # 200.50: line 14 = 0.50 at 33% = 0.165 -> 0.17; line 22 = 14.5% x 200 = 29.00.
        ("200.50", "0.17", "0.00", "29.00", "29.17"),
        # 100.10: 14.5% x 100.10 = 14.5145 -> 14.51, no excess over 200.
        ("100.10", "0.00", "0.00", "14.51", "14.51"),
        # 100.30: 14.5% x 100.30 = 14.5435 -> 14.54.
        ("100.30", "0.00", "0.00", "14.54", "14.54"),
    ],
)
def test_each_product_is_rounded_half_up_to_the_cent(
    line_1: str, line_20: str, line_21: str, line_22: str, line_23: str
) -> None:
    # Taxable income 300000: line 19 is 46586.00, above every line 16 here, so line F = line 16.
    lines = donations("400000", "300000", line_1=line_1)

    assert lines[LINE_20] == D(line_20)
    assert lines[LINE_21] == D(line_21)
    assert lines[LINE_22] == D(line_22)
    assert lines[LINE_23] == D(line_23)


def test_line_21_is_rounded_half_up_to_the_cent() -> None:
    # Taxable income 0 (below the threshold): line 14 = 0.50 at 29% = 0.145 -> 0.15; line 22 =
    # 29.00; line 23 = 29.15.
    lines = donations("400000", "0", line_1="200.50")

    assert lines[LINE_F] == D("0")
    assert lines[LINE_G] == D("0.50")
    assert lines[LINE_21] == D("0.15")
    assert lines[LINE_23] == D("29.15")


@pytest.mark.parametrize(
    ("line_33800", "line_22", "line_3", "line_5", "line_34990"),
    [
        # Line 33800 of 2500 and line 22 of 29.00: 2529.00 is below 8319.38, so line 5 is 0.
        ("2500", "29.00", "2529.00", "0", "0.00"),
        # Line 33800 of 9000 and line 22 of 29.00: 9029.00 - 8319.38 = 709.62; x 3.45% =
        # 24.48189, rounded half-up to the cent: 24.48.
        ("9000", "29.00", "9029.00", "709.62", "24.48"),
        # No donations: 9000.00 - 8319.38 = 680.62; x 3.45% = 23.48139 -> 23.48.
        ("9000", "0", "9000", "680.62", "23.48"),
        # At the threshold, and a cent over it: 0.01 x 3.45% = 0.000345 -> 0.00.
        ("8319.38", "0", "8319.38", "0", "0.00"),
        ("8319.39", "0", "8319.39", "0.01", "0.00"),
        # 8319.38 + 100.00: 100.00 x 3.45% = 3.45 exactly.
        ("8400.00", "19.38", "8419.38", "100.00", "3.45"),
        # 1000.15 x 3.45% = 34.505175 -> 34.51.
        ("9300.00", "19.53", "9319.53", "1000.15", "34.51"),
    ],
)
def test_the_top_up_tax_credit(
    line_33800: str, line_22: str, line_3: str, line_5: str, line_34990: str
) -> None:
    lines = run({CREDITS_AT_RATE: line_33800, LINE_22: line_22}, *top_up())

    assert lines[TOP_UP_3] == D(line_3)
    assert lines[TOP_UP_4] == D("8319.38")
    assert lines[TOP_UP_5] == D(line_5)
    assert lines[TOP_UP_7] == D(line_34990)


def test_the_top_up_reads_line_22_of_the_schedule_not_line_23() -> None:
    # Net income 60000, donations of 1500: line 22 is 29.00 and line 23 is 406.00. With line 33800
    # of 9000 the worksheet's line 3 is 9029.00, not 9406.00.
    schedule = donations("60000", "55000", line_1="1500")
    start = {CREDITS_AT_RATE: "9000", LINE_22: str(schedule[LINE_22])}

    lines = run(start, *top_up())

    assert lines[TOP_UP_3] == D("9029.00")
    assert lines[TOP_UP_5] == D("709.62")
    assert lines[TOP_UP_7] == D("24.48")
