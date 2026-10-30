"""The 2025 Ontario co-operative education tax credit figures, checked against CRA's ON479 forms.

2025 Worksheet ON479 (form 5006-D1), "Line 20 - Ontario co-operative education tax credit", for
each qualifying work placement: line 1 "Amount of eligible expenditures (Note 1) incurred in 2025
Line A multiplied by 25%"; line 2 "5%"; line 3 "Amount A multiplied by the percentage from line 2";
line 4 "Total salaries and wages paid in the 2024 taxation year"; line 5 "400,000.00"; line 6
"Line 4 minus line 5 (if negative, enter "0")"; line 7 "200,000.00"; line 8 "Line 6 divided by line
7"; line 9 "1.00"; line 10 "Amount from line 8 above"; line 11 "Line 9 minus line 10 (if negative,
enter "0")"; line 12 "Line 3 multiplied by line 11"; line 13 "Line 1 plus line 12 (maximum $3,000
per student)". The two percentages are rates (the `rate` kind), the printed constants of lines 5, 7
and 9 claimed amounts (the `credit` kind, as the age amount's are) and the maximum a plain cap (the
`amount` kind). Every figure sits in a dollars-and-cents box, so each dataset carries the half-up
cent rule; the capability that reads the rates leaves lines 1, 3 and 12 exact, and rounds line 13
and the total with the maximum's rule.
"""

from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_on.capabilities.coop_education_credit import (
    CoopEducationCredit,
)
from tax_engine.jurisdictions.ca_on.capabilities.quotient import Quotient
from tax_engine.jurisdictions.ca_on.catalog import (
    COOP_EDUCATION_CREDIT,
    COOP_EDUCATION_FULL_SHARE,
    COOP_EDUCATION_PAYROLL,
    COOP_EDUCATION_PAYROLL_OVER_THRESHOLD,
    COOP_EDUCATION_PAYROLL_RANGE,
    COOP_EDUCATION_PAYROLL_THRESHOLD,
    COOP_EDUCATION_PHASE_OUT_SHARE,
    COOP_EDUCATION_PLACEMENT_EXPENDITURES,
    COOP_EDUCATION_PLACEMENTS,
    COOP_EDUCATION_REMAINING_SHARE,
)

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
EXPENDITURE_RATE = "ca-on/coop_education_expenditure_rate"
SUPPLEMENT_RATE = "ca-on/coop_education_supplement_rate"
MAXIMUM = "ca-on/coop_education_maximum"
THRESHOLD = "ca-on/coop_education_payroll_threshold"
RANGE = "ca-on/coop_education_payroll_range"
FULL_SHARE = "ca-on/coop_education_full_share"
WORKSHEET_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-d1/5006-d1-25e.txt"
ON479_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-tc/5006-tc-25e.txt"
FORMS = Path(__file__).parents[3] / "tests" / "fixtures" / "cra-forms-2025"
WORKSHEET_FILE = FORMS / "5006-d1-25e.txt"
ON479_FILE = FORMS / "5006-tc-25e.txt"


def squashed(text: str) -> str:
    """`text` with the comment markers and line breaks gone and runs of blanks made one."""
    return re.sub(r"\s+", " ", text.replace("#", " ")).strip()


def dataset_header(family: str) -> str:
    """The comment lines above the dataset's first key, squashed."""
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca-on")]
    name = family.removeprefix("ca-on/")
    lines = (root / "parameters" / name / "2025.yaml").read_text().splitlines()
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return squashed("\n".join(lines[:first_key]))


def test_2025_expenditure_rate_is_25_percent() -> None:
    data = SOURCE.get(EXPENDITURE_RATE, 2025, RATE)

    assert data.values == Rate(D("0.25"))
    assert data.rounding == CENT


def test_2025_supplement_rate_is_5_percent() -> None:
    data = SOURCE.get(SUPPLEMENT_RATE, 2025, RATE)

    assert data.values == Rate(D("0.05"))
    assert data.rounding == CENT


def test_2025_maximum_is_3000_per_student() -> None:
    data = SOURCE.get(MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("3000"))
    # Line 13, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_payroll_threshold_is_400000() -> None:
    data = SOURCE.get(THRESHOLD, 2025, CREDIT)

    assert data.values == Credit(D("400000.00"))
    assert data.rounding == CENT


def test_2025_payroll_range_is_200000() -> None:
    data = SOURCE.get(RANGE, 2025, CREDIT)

    assert data.values == Credit(D("200000.00"))
    assert data.rounding == CENT


def test_2025_full_share_is_1() -> None:
    data = SOURCE.get(FULL_SHARE, 2025, CREDIT)

    assert data.values == Credit(D("1.00"))
    assert data.rounding == CENT


def test_2025_datasets_cite_only_the_worksheet_text() -> None:
    assert SOURCE.get(EXPENDITURE_RATE, 2025, RATE).sources == (WORKSHEET_TEXT,)
    assert SOURCE.get(SUPPLEMENT_RATE, 2025, RATE).sources == (WORKSHEET_TEXT,)
    assert SOURCE.get(THRESHOLD, 2025, CREDIT).sources == (WORKSHEET_TEXT,)
    assert SOURCE.get(RANGE, 2025, CREDIT).sources == (WORKSHEET_TEXT,)
    assert SOURCE.get(FULL_SHARE, 2025, CREDIT).sources == (WORKSHEET_TEXT,)


def test_2025_maximum_cites_the_worksheet_and_the_on479_text() -> None:
    sources = SOURCE.get(MAXIMUM, 2025, AMOUNT).sources

    assert set(sources) == {WORKSHEET_TEXT, ON479_TEXT}
    assert len(sources) == 2


@pytest.mark.parametrize(
    ("family", "quotes"),
    [
        (
            EXPENDITURE_RATE,
            (
                "line 20 - ontario co-operative education tax credit",
                "line 1",
                "amount of eligible expenditures",
                "multiplied by 25%",
            ),
        ),
        (
            SUPPLEMENT_RATE,
            (
                "line 20 - ontario co-operative education tax credit",
                "line 2",
                "5%",
                "line 3",
                "multiplied by the percentage from line 2",
            ),
        ),
        (
            THRESHOLD,
            ("line 20 - ontario co-operative education tax credit", "line 5", "400,000.00"),
        ),
        (
            RANGE,
            ("line 20 - ontario co-operative education tax credit", "line 7", "200,000.00"),
        ),
        (
            FULL_SHARE,
            ("line 20 - ontario co-operative education tax credit", "line 9", "1.00"),
        ),
        (
            MAXIMUM,
            (
                "line 20 - ontario co-operative education tax credit",
                "line 13",
                "line 1 plus line 12",
                "(maximum $3,000 per student)",
            ),
        ),
    ],
)
def test_each_dataset_header_quotes_the_worksheet_as_the_form_prints_it(
    family: str, quotes: tuple[str, ...]
) -> None:
    header = dataset_header(family).lower()
    form = squashed(WORKSHEET_FILE.read_text(encoding="utf-8-sig")).lower()

    for quoted in quotes:
        assert quoted in header, quoted
        assert quoted in form, quoted


def test_the_maximum_header_also_quotes_on479_line_20() -> None:
    header = dataset_header(MAXIMUM).lower()
    form = squashed(ON479_FILE.read_text(encoding="utf-8-sig")).lower()

    for quoted in ("line 20 and line 63300", "(maximum $3,000 per student)"):
        assert quoted in header, quoted
        assert quoted in form, quoted


def test_the_form_text_in_the_repository_is_the_text_the_figures_are_checked_against() -> None:
    worksheet = squashed(WORKSHEET_FILE.read_text(encoding="utf-8-sig"))

    for printed in (
        "Line 5: 400,000.00",
        "Line 7: 200,000.00",
        "Line 9: 1.00",
        "Line 2: 5%",
        "multiplied by 25%",
        "(maximum $3,000 per student)",
    ):
        assert printed in worksheet, printed


# --- the payroll lines, from the datasets ---------------------------------------------------------
#
# Lines 5, 6, 7, 8, 9 and 11 for each total of salaries and wages paid in the 2024 taxation year:
# line 8 is the exact fraction (payroll - 400,000.00, not below zero) / 200,000.00, and line 11 is
# 1.00 less it, not below zero.


def remaining_share_for(payroll: str) -> tuple[Decimal, Decimal]:
    """Lines 8 and 11 for a payroll (line 4), through the capabilities and datasets making them."""
    threshold = CreditAmount(SOURCE.get(THRESHOLD, 2025, CREDIT), COOP_EDUCATION_PAYROLL_THRESHOLD)
    spread = CreditAmount(SOURCE.get(RANGE, 2025, CREDIT), COOP_EDUCATION_PAYROLL_RANGE)
    full = CreditAmount(SOURCE.get(FULL_SHARE, 2025, CREDIT), COOP_EDUCATION_FULL_SHARE)
    start = [Artifact(COOP_EDUCATION_PAYROLL, D(payroll))]
    (line_5,) = threshold.compute(()).outputs
    (line_7,) = spread.compute(()).outputs
    (line_9,) = full.compute(()).outputs
    (line_6,) = (
        SubtractNotBelowZero(
            COOP_EDUCATION_PAYROLL,
            COOP_EDUCATION_PAYROLL_THRESHOLD,
            COOP_EDUCATION_PAYROLL_OVER_THRESHOLD,
        )
        .compute((*start, line_5))
        .outputs
    )
    (line_8,) = (
        Quotient(
            COOP_EDUCATION_PAYROLL_OVER_THRESHOLD,
            COOP_EDUCATION_PAYROLL_RANGE,
            COOP_EDUCATION_PHASE_OUT_SHARE,
        )
        .compute((line_6, line_7))
        .outputs
    )
    (line_11,) = (
        SubtractNotBelowZero(
            COOP_EDUCATION_FULL_SHARE,
            COOP_EDUCATION_PHASE_OUT_SHARE,
            COOP_EDUCATION_REMAINING_SHARE,
        )
        .compute((line_9, line_8))
        .outputs
    )
    return line_8.value, line_11.value


@pytest.mark.parametrize(
    ("payroll", "line_8", "line_11"),
    [
        # At or below 400,000.00: line 6 is 0, so the full 5% is added: 30%.
        ("0", "0", "1"),
        ("300000", "0", "1"),
        ("400000", "0", "1"),
        # Between: 500,000 gives 0.5 and 0.5; 450,000 gives 0.25 and 0.75; 550,000 gives 0.75
        # and 0.25.
        ("450000", "0.25", "0.75"),
        ("500000", "0.5", "0.5"),
        ("550000", "0.75", "0.25"),
        ("400001", "0.000005", "0.999995"),
        # At 600,000 line 8 is 1.00 and line 11 is 0: 25%. Above it line 11 is still 0.
        ("600000", "1", "0"),
        ("700000", "1.5", "0"),
    ],
)
def test_the_payroll_gives_lines_8_and_11(payroll: str, line_8: str, line_11: str) -> None:
    assert remaining_share_for(payroll) == (D(line_8), D(line_11))


def credit_for(payroll: str, *expenditures: str) -> Decimal:
    _, line_11 = remaining_share_for(payroll)
    records = [{COOP_EDUCATION_PLACEMENT_EXPENDITURES: D(amount)} for amount in expenditures]
    capability = CoopEducationCredit(
        expenditure_rate=SOURCE.get(EXPENDITURE_RATE, 2025, RATE),
        supplement_rate=SOURCE.get(SUPPLEMENT_RATE, 2025, RATE),
        maximum=SOURCE.get(MAXIMUM, 2025, AMOUNT),
        placements=COOP_EDUCATION_PLACEMENTS,
        remaining_share=COOP_EDUCATION_REMAINING_SHARE,
        output=COOP_EDUCATION_CREDIT,
    )
    (credit,) = capability.compute(
        (
            Artifact(
                COOP_EDUCATION_PLACEMENTS, RecordList(COOP_EDUCATION_PLACEMENTS.fields, records)
            ),
            Artifact(COOP_EDUCATION_REMAINING_SHARE, line_11),
        )
    ).outputs
    value = credit.value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("payroll", "credit"),
    [
        # The worked examples, for placements of 8,000 and 15,000.
        ("500000", "5200"),
        ("700000", "5000"),
        ("300000", "5400"),
        # The boundaries: 30% at 400,000 and 25% at 600,000, for each placement.
        ("400000", "5400"),
        ("600000", "5000"),
    ],
)
def test_the_worked_examples_from_the_payroll_to_line_20(payroll: str, credit: str) -> None:
    assert credit_for(payroll, "8000", "15000") == D(credit)


def test_a_payroll_of_400000_is_30_percent_and_600000_is_25_percent_of_one_placement() -> None:
    assert credit_for("400000", "8000") == D("2400")
    assert credit_for("600000", "8000") == D("2000")
    assert credit_for("500000", "8000") == D("2200")


def test_no_placements_give_zero_whatever_the_payroll() -> None:
    for payroll in ("0", "300000", "400000", "500000", "600000", "700000"):
        assert credit_for(payroll) == D("0")
