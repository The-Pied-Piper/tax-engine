"""2025 federal and Ontario bracket data, checked against CRA's published figures.

Sources are listed in each dataset file. Each bracket holds the form's column: its lower bound and
its rate (2025 T1, Step 5, Part A, lines 71 and 73; Form ON428, Part A, lines 3 and 5). The engine
computes the tax at each bracket's start, the exact tax on the brackets below rounded by the
dataset's rule, half-up to the cent; the figures it gives are the constants the forms print (T1
line 75; ON428 line 7). The tax on taxable income is "Line 72 multiplied by the percentage from
line 73" plus line 75 (T1), or line 6 plus line 7 (ON428), for the column the income falls in; an
income exactly at a column's upper bound falls in that column ("more than ... but not more than
..."). Line 76 (T1) and line 8 (ON428) are dollars-and-cents boxes, so the tax on taxable income
is rounded half-up to the cent, by the dataset's own rule.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact
from tax_calculator.domain.capabilities.progressive_tax import ProgressiveTax
from tax_calculator.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.jurisdictions.ca.catalog import FEDERAL_BASIC_TAX, TAXABLE_INCOME

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())

FEDERAL_SOURCES = (
    "https://www.canada.ca/en/revenue-agency/services/tax/individuals/tax-rates-brackets/last-year.html",
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-r/5000-r-25e.txt",
    "https://www.canada.ca/en/department-finance/news/2025/05/delivering-a-middle-class-tax-cut.html",
)
ONTARIO_SOURCES = (
    "https://www.canada.ca/en/revenue-agency/services/tax/individuals/tax-rates-brackets/last-year.html",
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt",
    "https://data.ontario.ca/en/dataset/personal-income-tax-rates-and-credits/resource/60f84727-7e12-4fd4-ba06-30955d31b2ae",
)


def tax_at_starts(schedule: BracketSchedule) -> list[Decimal]:
    """Each bracket's computed tax at its start, from the column of an income a cent above its
    lower bound (an income at the bound falls in the column below)."""
    return [schedule.column_for(b.lower + D("0.01")).tax_at_start for b in schedule.brackets]


def test_federal_2025_brackets() -> None:
    data = SOURCE.get("ca/brackets", 2025, BRACKETS)

    # 2025 T1, Step 5, Part A: line 71 lower bound, line 73 rate.
    assert [(b.lower, b.rate) for b in data.values.brackets] == [
        (D("0"), D("0.145")),
        (D("57375"), D("0.205")),
        (D("114750"), D("0.26")),
        (D("177882"), D("0.29")),
        (D("253414"), D("0.33")),
    ]
    assert data.values.tax_at_start_rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    # T1 line 76, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == FEDERAL_SOURCES


def test_ontario_2025_brackets() -> None:
    data = SOURCE.get("ca-on/brackets", 2025, BRACKETS)

    # 2025 ON428, Part A: line 3 lower bound, line 5 rate.
    assert [(b.lower, b.rate) for b in data.values.brackets] == [
        (D("0"), D("0.0505")),
        (D("52886"), D("0.0915")),
        (D("105775"), D("0.1116")),
        (D("150000"), D("0.1216")),
        (D("220000"), D("0.1316")),
    ]
    assert data.values.tax_at_start_rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    # ON428 line 8, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == ONTARIO_SOURCES


def test_the_computed_federal_tax_at_each_start_is_the_t1_line_75_printed_constant() -> None:
    schedule = SOURCE.get("ca/brackets", 2025, BRACKETS).values

    # 2025 T1, Step 5, Part A, line 75 in columns 1 to 5. The exact tax below the second column
    # is 14.5% x 57,375 = 8,319.375, printed 8,319.38.
    assert tax_at_starts(schedule) == [
        D("0.00"),
        D("8319.38"),
        D("20081.25"),
        D("36495.57"),
        D("58399.85"),
    ]


def test_the_computed_ontario_tax_at_each_start_is_the_on428_line_7_printed_constant() -> None:
    schedule = SOURCE.get("ca-on/brackets", 2025, BRACKETS).values

    # 2025 ON428, Part A, line 7 in columns 1 to 5. The exact tax below the third column is
    # 5.05% x 52,886 + 9.15% x 52,889 = 7,510.0865, printed 7,510.09.
    assert tax_at_starts(schedule) == [
        D("0.00"),
        D("2670.74"),
        D("7510.09"),
        D("12445.60"),
        D("20957.60"),
    ]


@pytest.mark.parametrize("family", ["ca/brackets", "ca-on/brackets"])
def test_the_computed_tax_at_each_start_is_held_to_the_cent(family: str) -> None:
    schedule = SOURCE.get(family, 2025, BRACKETS).values

    # Every start, the first's 0.00 included, carries the cent's scale.
    assert all(tax.as_tuple().exponent == -2 for tax in tax_at_starts(schedule))
    assert str(tax_at_starts(schedule)[0]) == "0.00"


@pytest.mark.parametrize(
    ("family", "income", "tax"),
    [
        # An income at a column's upper bound falls in that column: its rate on the excess
        # over the column's lower bound, plus the column's tax at its start (the printed constant).
        ("ca/brackets", "57375", "8319.375"),  # 14.5% x 57,375 + 0.00
        ("ca/brackets", "114750", "20081.255"),  # 20.5% x 57,375 + 8,319.38
        ("ca/brackets", "177882", "36495.57"),  # 26% x 63,132 + 20,081.25
        ("ca/brackets", "253414", "58399.85"),  # 29% x 75,532 + 36,495.57
        ("ca-on/brackets", "52886", "2670.743"),  # 5.05% x 52,886 + 0.00
        ("ca-on/brackets", "105775", "7510.0835"),  # 9.15% x 52,889 + 2,670.74
        ("ca-on/brackets", "150000", "12445.60"),  # 11.16% x 44,225 + 7,510.09
        ("ca-on/brackets", "220000", "20957.60"),  # 12.16% x 70,000 + 12,445.60
    ],
)
def test_an_income_at_a_threshold_is_taxed_in_the_lower_column(
    family: str, income: str, tax: str
) -> None:
    schedule = SOURCE.get(family, 2025, BRACKETS).values

    assert schedule.tax_on(D(income)) == D(tax)


@pytest.mark.parametrize(
    ("family", "income", "tax"),
    [
        # Just above a threshold: the next column's tax at its start, plus its rate on a cent.
        ("ca/brackets", "57375.01", "8319.38205"),  # 20.5% x 0.01 + 8,319.38
        ("ca-on/brackets", "105775.01", "7510.091116"),  # 11.16% x 0.01 + 7,510.09
    ],
)
def test_an_income_above_a_threshold_starts_from_the_next_columns_tax_at_start(
    family: str, income: str, tax: str
) -> None:
    schedule = SOURCE.get(family, 2025, BRACKETS).values

    assert schedule.tax_on(D(income)) == D(tax)


@pytest.mark.parametrize(
    ("taxable_income", "federal_basic_tax"),
    [
        ("10000", "1450"),  # CRA "Completing a basic tax return": Giovanni
        ("115000", "20146.25"),  # same page, Maria: 26% x 250 + 20,081.25
    ],
)
def test_matches_cra_worked_examples(taxable_income: str, federal_basic_tax: str) -> None:
    schedule = SOURCE.get("ca/brackets", 2025, BRACKETS)
    capability = ProgressiveTax(TAXABLE_INCOME, FEDERAL_BASIC_TAX, schedule)

    result = capability.compute((Artifact(TAXABLE_INCOME, D(taxable_income)),))

    assert result.outputs == (Artifact(FEDERAL_BASIC_TAX, D(federal_basic_tax)),)


@pytest.mark.parametrize(
    ("family", "taxable_income", "tax"),
    [
        # The schedule's tax at a threshold, rounded half-up to the cent by the dataset's rule:
        # 14.5% x 57,375 = 8,319.375, a tie, up to 8,319.38; 20.5% x 57,375 + 8,319.38 =
        # 20,081.255, a tie, up to 20,081.26, though column 3 starts at 20,081.25; 5.05% x 52,886
        # = 2,670.743, to 2,670.74; 9.15% x 52,889 + 2,670.74 = 7,510.0835, to 7,510.08, though
        # column 3 starts at 7,510.09.
        ("ca/brackets", "57375", "8319.38"),
        ("ca/brackets", "114750", "20081.26"),
        ("ca-on/brackets", "52886", "2670.74"),
        ("ca-on/brackets", "105775", "7510.08"),
        # Returns B and F: 14.5% x 29,735.00 = 4,311.575, to 4,311.58; 2,670.74 + 9.15% x 1,549.00
        # = 2,812.4735, to 2,812.47.
        ("ca/brackets", "29735.00", "4311.58"),
        ("ca-on/brackets", "54435.00", "2812.47"),
        # Return E's Ontario tax: 12,445.60 + 12.16% x 48,926.00 = 18,395.0016, to 18,395.00.
        ("ca-on/brackets", "198926.00", "18395.00"),
    ],
)
def test_the_tax_on_taxable_income_is_rounded_half_up_to_the_cent(
    family: str, taxable_income: str, tax: str
) -> None:
    capability = ProgressiveTax(
        TAXABLE_INCOME, FEDERAL_BASIC_TAX, SOURCE.get(family, 2025, BRACKETS)
    )

    result = capability.compute((Artifact(TAXABLE_INCOME, D(taxable_income)),))

    assert result.outputs == (Artifact(FEDERAL_BASIC_TAX, D(tax)),)
