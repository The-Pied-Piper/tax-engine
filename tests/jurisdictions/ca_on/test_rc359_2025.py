"""The 2025 Form RC359 datasets, checked against the printed form.

Form RC359 (2025), Tax on Excess Employees Profit Sharing Plan Amounts, read from the PDF
(https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/rc359/rc359-25e.pdf; no .txt is
published). Three datasets, one for each figure the form prints:
- `ca/rc359_employment_income_rate`: line 5 "Rate" "× 20%", a rate of 0.2 (the form's line 6
  "Line 4 multiplied by the percentage from line 5" is a dollars-and-cents box, so it rounds
  half-up to the cent, the owner's decision, as the form states no rounding rule);
- `ca/rc359_province_percentage`: line 8's chart "Jurisdiction" "Rate", printed in two columns and
  read in order, left then right: the fourteen rates keyed by the province code the caller enters
  (1 Newfoundland and Labrador, 2 Prince Edward Island, 3 Nova Scotia, 4 New Brunswick, 5 Québec,
  6 Ontario, 7 Manitoba, 8 Saskatchewan, 9 Alberta, 10 British Columbia, 11 Northwest Territories,
  12 Yukon, 13 Nunavut, 14 Other (non-resident)); a code with no row is refused;
- `ca/rc359_tax_rounding`: line 9 "Line 7 multiplied by the percentage from line 8", a
  dollars-and-cents box, rounded half-up to the cent once.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.amount_by_count import AmountForCount
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.errors import NoAmountForCountError
from tax_calculator.domain.parameters.amount_by_count import AMOUNT_BY_COUNT, AmountByCount
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.jurisdictions.ca.capabilities.apply_percentage import ApplyPercentage

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
RC359_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/rc359/rc359-25e.pdf"
EMPLOYMENT_INCOME_RATE = "ca/rc359_employment_income_rate"
PROVINCE_PERCENTAGE = "ca/rc359_province_percentage"
TAX_ROUNDING = "ca/rc359_tax_rounding"

# The chart as printed, keyed by the province code: line 8's rate for each jurisdiction.
PRINTED = {
    1: "54.8",  # Newfoundland and Labrador
    2: "52",  # Prince Edward Island
    3: "54",  # Nova Scotia
    4: "52.5",  # New Brunswick
    5: "33",  # Québec
    6: "53.53",  # Ontario
    7: "50.4",  # Manitoba
    8: "47.5",  # Saskatchewan
    9: "48",  # Alberta
    10: "53.5",  # British Columbia
    11: "47.05",  # Northwest Territories
    12: "48",  # Yukon
    13: "44.5",  # Nunavut
    14: "49",  # Other (non-resident)
}

# Made up for this test and not registered: the province code, the percentage, the amount and
# the figure the capabilities read and produce.
COUNT = ArtifactKind("ex/province_code", int)
PERCENT = ArtifactKind("ex/percentage", Decimal)
AMOUNT = ArtifactKind("ex/amount", Decimal)
BASE = ArtifactKind("ex/base", Decimal)
OUTPUT = ArtifactKind("ex/output", Decimal)


def test_2025_employment_income_rate_is_twenty_percent_rounded_to_the_cent() -> None:
    data = SOURCE.get(EMPLOYMENT_INCOME_RATE, 2025, RATE)

    assert data.values == Rate(D("0.2"))
    assert data.rounding == CENT
    assert RC359_PDF in data.sources


def test_2025_province_percentage_is_the_printed_chart_by_province_code() -> None:
    data = SOURCE.get(PROVINCE_PERCENTAGE, 2025, AMOUNT_BY_COUNT)

    assert data.values == AmountByCount(tuple((code, D(rate)) for code, rate in PRINTED.items()))
    assert RC359_PDF in data.sources


def test_the_chart_has_a_row_for_each_of_the_fourteen_codes_and_no_other() -> None:
    data = SOURCE.get(PROVINCE_PERCENTAGE, 2025, AMOUNT_BY_COUNT)

    assert sorted(dict(data.values.rows)) == list(range(1, 15))


def test_ontario_is_code_6_and_other_non_resident_is_code_14() -> None:
    rows = dict(SOURCE.get(PROVINCE_PERCENTAGE, 2025, AMOUNT_BY_COUNT).values.rows)

    assert rows[6] == D("53.53")
    assert rows[7] == D("50.4")
    assert rows[14] == D("49")


def test_2025_province_percentage_is_rounded_half_up_to_the_cent() -> None:
    data = SOURCE.get(PROVINCE_PERCENTAGE, 2025, AMOUNT_BY_COUNT)

    assert data.rounding == CENT


@pytest.mark.parametrize("code", [0, 15])
def test_a_province_code_with_no_row_is_refused(code: int) -> None:
    capability = AmountForCount(
        SOURCE.get(PROVINCE_PERCENTAGE, 2025, AMOUNT_BY_COUNT), COUNT, OUTPUT
    )

    with pytest.raises(NoAmountForCountError):
        capability.compute((Artifact(COUNT, code),))


@pytest.mark.parametrize(("code", "rate"), [(6, "53.53"), (7, "50.40"), (14, "49.00")])
def test_reads_the_printed_rate_for_the_province_code(code: int, rate: str) -> None:
    capability = AmountForCount(
        SOURCE.get(PROVINCE_PERCENTAGE, 2025, AMOUNT_BY_COUNT), COUNT, OUTPUT
    )

    result = capability.compute((Artifact(COUNT, code),))

    assert result.outputs == (Artifact(OUTPUT, D(rate)),)


def test_2025_tax_rounding_is_half_up_to_the_cent_with_no_other_figure() -> None:
    data = SOURCE.get(TAX_ROUNDING, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == CENT
    assert RC359_PDF in data.sources


def test_line_9_of_an_ontario_copy_is_6000_at_53_53_percent_3211_80() -> None:
    # Line 7 of the first employer's copy is 6,000.00 (20,000.00 less 4,000.00 on line 6), line 8
    # is Ontario's 53.53 and line 9 is 6,000.00 x 53.53 / 100 = 3,211.80.
    capability = ApplyPercentage(
        SOURCE.get(TAX_ROUNDING, 2025, ROUNDING_ONLY), AMOUNT, PERCENT, OUTPUT
    )

    result = capability.compute((Artifact(AMOUNT, D("6000.00")), Artifact(PERCENT, D("53.53"))))

    assert result.outputs == (Artifact(OUTPUT, D("3211.80")),)


@pytest.mark.parametrize(
    ("excess", "percent", "line_9"),
    [
        # Manitoba's copy of employer A: 6,000.00 x 50.4 / 100 = 3,024.00.
        ("6000.00", "50.4", "3024.00"),
        # Other (non-resident): 6,000.00 x 49 / 100 = 2,940.00.
        ("6000.00", "49", "2940.00"),
        # Employer B's excess is 0.00 (line 7 floored), and 0.00 at any rate is 0.00.
        ("0.00", "53.53", "0.00"),
    ],
)
def test_line_9_is_the_excess_at_the_printed_percentage(
    excess: str, percent: str, line_9: str
) -> None:
    capability = ApplyPercentage(
        SOURCE.get(TAX_ROUNDING, 2025, ROUNDING_ONLY), AMOUNT, PERCENT, OUTPUT
    )

    result = capability.compute((Artifact(AMOUNT, D(excess)), Artifact(PERCENT, D(percent))))

    assert result.outputs == (Artifact(OUTPUT, D(line_9)),)


def test_line_6_is_twenty_percent_of_line_4_on_employer_a() -> None:
    # Line 4 is 20,000.00 (20,000.00 employment income less nothing); line 6 is 20% of it.
    capability = ApplyRate(SOURCE.get(EMPLOYMENT_INCOME_RATE, 2025, RATE), BASE, OUTPUT)

    result = capability.compute((Artifact(BASE, D("20000.00")),))

    assert result.outputs == (Artifact(OUTPUT, D("4000.00")),)
