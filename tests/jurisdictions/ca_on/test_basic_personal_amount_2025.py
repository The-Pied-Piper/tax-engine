"""2025 federal and Ontario basic personal amounts and credit rates, checked against CRA's forms.

Federal: 2025 T1 (form 5000-R) line 77 (line 30000) "If the amount on line 23600 is $177,882 or
less, enter $16,129. If the amount on line 23600 is $253,414 or more, enter $14,538. Otherwise,
use the Federal Worksheet to calculate the amount to enter. (maximum $16,129)". The Federal
Worksheet (form 5000-D1), line 30000: line 1 "Base amount 14,538.00"; line 2 "Supplement amount
1,591.00"; line 3 "Amount from line 23600 of your return"; line 4 "Income threshold 177,882.00";
line 5 "Line 3 minus line 4"; line 6 "75,532.00"; line 7 "Line 5 divided by line 6"; line 8
"1,591.00"; line 9 "Line 7 multiplied by line 8"; line 10 "Line 2 minus line 9 (if negative,
enter "0")"; line 11 "Line 1 plus line 10 Enter this amount on line 30000 of your return.
(maximum $16,129)". So the amount is a taper (the `taper` kind) on net income: base 14,538,
supplement 1,591, threshold 177,882, range 75,532. The worksheet states no rounding; T4127
(120th edition) gives the rule: "Note that there is no rounding on this division." and "If the
BPAF has three or more digits after the decimal point, increase the second digit after the
decimal point by one if the third digit is five or more, and drop the third digit.", so the
amount is rounded half-up to the cent, once. The federal non-refundable credit rate is T1 line
114 (14.5%).

Ontario: 2025 ON428 line 58040 ($12,747), with no reduction, and the credit rate on ON428 line 45
(5.05%). Each rate is its own dataset (`credit_rate`), stated once, and applies to the total of
the credit amounts (T1 line 33500, ON428 line 58800), of which the basic personal amount is one
part. The Ontario amount and both rates' products are dollars-and-cents boxes too (ON428 line
58040; T1 line 33800, ON428 line 58840), so each is rounded half-up to the cent. Sources are
listed in each dataset.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.tapered_amount import TaperedAmount
from tax_engine.domain.parameters.brackets import BRACKETS
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.taper import TAPER, Taper

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
FEDERAL = "ca/basic_personal_amount"
ONTARIO = "ca-on/basic_personal_amount"


# Made up for this test and not registered: the net income the federal amount is tapered on, the
# basic personal amount as an artifact, the credit amounts it stands for alone, the credits (the
# amounts times the rate), whichever basic tax the credits come off, and that tax less the credits.
NET_INCOME = ArtifactKind("ex/net_income", Decimal)
AMOUNT = ArtifactKind("ex/basic_personal_amount", Decimal)
CREDITS = ArtifactKind("ex/non_refundable_tax_credits", Decimal)
BASIC_TAX = ArtifactKind("ex/basic_tax", Decimal)
TAX_AFTER_CREDITS = ArtifactKind("ex/tax_after_credits", Decimal)


def test_2025_federal_amount_is_the_worksheet_taper() -> None:
    data = SOURCE.get(FEDERAL, 2025, TAPER)

    # Worksheet lines 1, 2, 4 and 6: base, supplement, income threshold and range.
    assert data.values == Taper(
        base=D("14538"), supplement=D("1591"), threshold=D("177882"), range=D("75532")
    )
    # T4127's BPAF footnote: half-up to the second digit after the decimal point.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_federal_full_amount_is_the_t1_maximum() -> None:
    taper = SOURCE.get(FEDERAL, 2025, TAPER).values

    # Line 30000's "(maximum $16,129)" is the base plus the supplement; the worksheet's line
    # 30000 text gives $14,538 at $253,414 or more, the threshold plus the range.
    assert taper.base + taper.supplement == D("16129")
    assert taper.threshold + taper.range == D("253414")


@pytest.mark.parametrize(
    "source",
    [
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-r/5000-r-25e.txt",
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-d1/5000-d1-25e.txt",
        "https://www.canada.ca/en/revenue-agency/services/forms-publications/payroll/payroll-deductions-t4127-payroll-deductions-formulas/t4127-jan-120th-edition-effective-january-1-2025/t4127-jan-payroll-deductions-formulas-computer-programs.html",
    ],
)
def test_2025_federal_amount_cites_its_sources(source: str) -> None:
    data = SOURCE.get(FEDERAL, 2025, TAPER)

    assert source in data.sources


@pytest.mark.parametrize(
    ("net_income", "amount"),
    [
        # Returns A, C and D, and the low-income return: at or below the threshold, so the full
        # 14,538 + 1,591 = 16,129.
        ("115000", "16129.00"),
        ("49535.00", "16129.00"),
        ("74174.00", "16129.00"),
        ("9935.00", "16129.00"),
        # At the threshold, and a cent past it: 16,129 - 1,591 x 0.01 / 75,532 =
        # 16,128.99978936..., half-up to 16,129.00.
        ("177882", "16129.00"),
        ("177882.01", "16129.00"),
        # Return E: 16,129 - 1,591 x 21,044 / 75,532 = 15,685.73086903..., half-up to 15,685.73.
        ("198926.00", "15685.73"),
        # 16,129 - 1,591 x 22,118 / 75,532 = 15,663.10821903...: half-up gives 15,663.11, where
        # dropping the third digit would give 15,663.10.
        ("200000", "15663.11"),
        # At threshold plus range the whole supplement is gone; a cent past it the reduction
        # exceeds the supplement and line 10 enters 0, so the amount stays the base.
        ("253414", "14538.00"),
        ("253414.01", "14538.00"),
        ("0", "16129.00"),
    ],
)
def test_tapers_net_income(net_income: str, amount: str) -> None:
    capability = TaperedAmount(SOURCE.get(FEDERAL, 2025, TAPER), NET_INCOME, AMOUNT)

    result = capability.compute((Artifact(NET_INCOME, D(net_income)),))

    assert result.outputs == (Artifact(AMOUNT, D(amount)),)


def test_tapered_amount_is_rounded_to_the_cent() -> None:
    capability = TaperedAmount(SOURCE.get(FEDERAL, 2025, TAPER), NET_INCOME, AMOUNT)

    (amount,) = capability.compute((Artifact(NET_INCOME, D("198926.00")),)).outputs

    assert amount.value.as_tuple().exponent == -2


def test_2025_ontario_amount() -> None:
    data = SOURCE.get(ONTARIO, 2025, CREDIT)

    assert data.values == Credit(amount=D("12747"))
    # ON428 line 58040, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources


@pytest.mark.parametrize(
    ("family", "rate"),
    [("ca/credit_rate", "0.145"), ("ca-on/credit_rate", "0.0505")],
)
def test_2025_credit_rates(family: str, rate: str) -> None:
    data = SOURCE.get(family, 2025, RATE)

    assert data.values == Rate(D(rate))
    # T1 line 33800 and ON428 line 58840, dollars-and-cents boxes: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources


@pytest.mark.parametrize(
    ("rate_family", "brackets_family"),
    [("ca/credit_rate", "ca/brackets"), ("ca-on/credit_rate", "ca-on/brackets")],
)
def test_2025_credit_rate_is_the_lowest_bracket_rate(
    rate_family: str, brackets_family: str
) -> None:
    rate = SOURCE.get(rate_family, 2025, RATE).values.value
    lowest = SOURCE.get(brackets_family, 2025, BRACKETS).values.brackets[0].rate

    assert rate == lowest


@pytest.mark.parametrize(
    ("net_income", "basic_tax", "after"),
    [
        # $115,000 of net and taxable income: federal basic tax 20,146.25 less 16,129 × 14.5% =
        # 2,338.705, a tie, up to 2,338.71.
        ("115000", "20146.25", "17807.54"),
        # $10,000 of net and taxable income: federal basic tax 1,450 is fully offset.
        ("10000", "1450", "0"),
    ],
)
def test_federal_amount_applies_to_basic_tax(net_income: str, basic_tax: str, after: str) -> None:
    amount = SOURCE.get(FEDERAL, 2025, TAPER)
    rate = SOURCE.get("ca/credit_rate", 2025, RATE)

    # The basic personal amount is tapered on net income, and with no other credit amount it is
    # the whole total the rate is applied to; the credits then come off the basic tax, not
    # below zero.
    (claimed,) = (
        TaperedAmount(amount, NET_INCOME, AMOUNT)
        .compute((Artifact(NET_INCOME, D(net_income)),))
        .outputs
    )
    (credits,) = ApplyRate(rate, base=AMOUNT, output=CREDITS).compute((claimed,)).outputs
    less = SubtractNotBelowZero(amount=BASIC_TAX, less=CREDITS, output=TAX_AFTER_CREDITS)

    result = less.compute((Artifact(BASIC_TAX, D(basic_tax)), credits))

    assert claimed == Artifact(AMOUNT, D("16129"))
    assert credits == Artifact(CREDITS, D("2338.71"))
    assert result.outputs == (Artifact(TAX_AFTER_CREDITS, D(after)),)


def test_ontario_amount_applies_to_basic_tax() -> None:
    amount = SOURCE.get(ONTARIO, 2025, CREDIT)
    rate = SOURCE.get("ca-on/credit_rate", 2025, RATE)

    # Ontario basic tax on $115,000 (ON428 Part A, column 3: 11.16% x 9,225 + 7,510.09 =
    # 8,539.60) less 12,747 × 5.05% = 643.7235, rounded half-up to 643.72.
    (claimed,) = CreditAmount(amount, AMOUNT).compute(()).outputs
    (credits,) = ApplyRate(rate, base=AMOUNT, output=CREDITS).compute((claimed,)).outputs
    less = SubtractNotBelowZero(amount=BASIC_TAX, less=CREDITS, output=TAX_AFTER_CREDITS)

    result = less.compute((Artifact(BASIC_TAX, D("8539.60")), credits))

    assert claimed == Artifact(AMOUNT, amount.values.amount)
    assert credits == Artifact(CREDITS, D("643.72"))
    assert result.outputs == (Artifact(TAX_AFTER_CREDITS, D("7895.88")),)
