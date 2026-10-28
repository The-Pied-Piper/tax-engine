"""The 2025 federal foreign tax credit figures (Form T2209), checked against CRA's form.

2025 Form T2209, Federal Foreign Tax Credits: "If you paid tax to more than one foreign country,
and the total foreign taxes paid to all foreign countries was more than $200, do the applicable
calculation shown on this form for non-business and business taxes paid to each country on a
separate sheet in Canadian dollars. Enter the total amount on this form."; the federal
non-business foreign tax credit's line 1 "Non-business income tax paid to a foreign country (1)
43100", line 2 "Net foreign non-business income (2) 43300" "x Basic federal tax (4) =" over "Net
income (3)" and line 3 "Enter whichever is less: the amount from line 1 or line 2. Federal
non-business foreign tax credit". The printed $200 is a dataset (the `amount` kind). Line 2
multiplies and divides, so its one dataset is a `rounding_only` one: the line is a
dollars-and-cents box, so the quotient rounds half-up to the cent, the owner's decision, as the
form states no rounding rule. Lines 1 and 3 take amounts already in cents. The form is a PDF with
no published .txt, so the datasets cite the PDF.

The datasets are tested with the capability that reads them, on the registered kinds of the
countries and made-up kinds for the two return-wide figures; the lines together, from the
countries to line 40500, are in the `end_to_end` tests and `returns/2025_return_aw.yaml`.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.rate import RATE
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.registry import Namespace
from tax_calculator.jurisdictions.ca.capabilities.foreign_business_tax_credit_line_5 import (
    ForeignBusinessTaxCreditLine5,
)
from tax_calculator.jurisdictions.ca.capabilities.foreign_non_business_tax_credit import (
    ForeignNonBusinessTaxCredit,
)
from tax_calculator.jurisdictions.ca.catalog import (
    FOREIGN_BUSINESS_TAX_PAID,
    FOREIGN_BUSINESS_UNUSED_TAX_CREDITS,
    FOREIGN_NON_BUSINESS_TAX_PAID,
    FOREIGN_PROPERTY_TAX_PAID,
    FOREIGN_SURTAX_OUTSIDE_CANADA,
    FOREIGN_TAX_COUNTRIES,
    FOREIGN_TAX_CREDIT_SHEET_LINE_3,
    FOREIGN_TAX_CREDIT_SHEETS,
    NET_FOREIGN_BUSINESS_INCOME,
    NET_FOREIGN_NON_BUSINESS_INCOME,
    NET_FOREIGN_PROPERTY_INCOME,
)

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
THRESHOLD = "ca/foreign_tax_pooling_threshold"
ROUNDING = "ca/foreign_non_business_tax_credit_rounding"
BUSINESS_ROUNDING = "ca/foreign_business_tax_credit_rounding"
LIMIT_RATE = "ca/foreign_property_income_credit_limit_rate"
T2209_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2209/t2209-25e.pdf"

# Made up for this test and not registered: the return-wide net income (note 3), basic federal
# tax (note 4) and the credit (line 3).
NET_INCOME = ArtifactKind("ex/net_income", Decimal, non_negative=True)
BASIC_TAX = ArtifactKind("ex/basic_federal_tax", Decimal, non_negative=True)
CREDIT = ArtifactKind("ex/foreign_credit", Decimal, non_negative=True)


def squashed(text: str) -> str:
    """`text` with the comment markers and line breaks gone and runs of blanks made one."""
    return re.sub(r"\s+", " ", text.replace("#", " ")).strip()


def dataset_header(family: str) -> str:
    """The comment lines above the dataset's first key, squashed."""
    root = tax_calculator.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    name = family.removeprefix("ca/")
    lines = (root / "parameters" / name / "2025.yaml").read_text().splitlines()
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return squashed("\n".join(lines[:first_key]))


def test_2025_pooling_threshold_is_200() -> None:
    data = SOURCE.get(THRESHOLD, 2025, AMOUNT)

    assert data.values == Amount(D("200"))
    assert data.rounding == CENT


def test_2025_pooling_threshold_cites_only_the_t2209_pdf() -> None:
    assert SOURCE.get(THRESHOLD, 2025, AMOUNT).sources == (T2209_PDF,)


def test_2025_rounding_is_half_up_to_the_cent_with_no_other_figure() -> None:
    data = SOURCE.get(ROUNDING, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    # Line 2, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_rounding_cites_only_the_t2209_pdf() -> None:
    assert SOURCE.get(ROUNDING, 2025, ROUNDING_ONLY).sources == (T2209_PDF,)


def test_the_threshold_header_quotes_t2209_as_the_form_prints_it() -> None:
    header = dataset_header(THRESHOLD)

    for quoted in (
        "If you paid tax to more than one foreign country, and the total foreign taxes paid to "
        "all foreign countries was more than $200",
        "do the applicable calculation shown on this form for non-business and business taxes "
        "paid to each country on a separate sheet in Canadian dollars",
        "Enter the total amount on this form.",
    ):
        assert quoted in header, quoted


def test_the_threshold_header_states_the_half_up_cent_rule() -> None:
    header = dataset_header(THRESHOLD).lower()

    assert "half-up" in header
    assert "owner's decision" in header


def test_the_rounding_header_quotes_t2209_as_the_form_prints_it() -> None:
    header = dataset_header(ROUNDING)

    for quoted in (
        "Non-business income tax paid to a foreign country (1) 43100",
        "Net foreign non-business income (2) 43300",
        "Basic federal tax (4)",
        "Net income (3)",
        "Enter whichever is less: the amount from line 1 or line 2.",
        "Federal non-business foreign tax credit",
    ):
        assert quoted in header, quoted


def test_the_rounding_header_states_the_half_up_cent_rule() -> None:
    header = dataset_header(ROUNDING).lower()

    assert "dollars-and-cents box" in header
    assert "half-up" in header
    assert "owner's decision" in header


def credit(*rows: tuple[str, str], net_income: str = "100000", basic_tax: str = "14000") -> Decimal:
    """Lines 1 to 3 over the registered countries, one (line 1, line 2 income) row for each, on
    the two real datasets."""
    capability = ForeignNonBusinessTaxCredit(
        SOURCE.get(ROUNDING, 2025, ROUNDING_ONLY),
        SOURCE.get(THRESHOLD, 2025, AMOUNT),
        SOURCE.get(LIMIT_RATE, 2025, RATE),
        FOREIGN_TAX_COUNTRIES,
        NET_INCOME,
        BASIC_TAX,
        CREDIT,
        FOREIGN_TAX_CREDIT_SHEETS,
    )
    records: list[dict[ArtifactKind[Any], object]] = [
        {
            FOREIGN_NON_BUSINESS_TAX_PAID: D(tax),
            NET_FOREIGN_NON_BUSINESS_INCOME: D(income),
            FOREIGN_BUSINESS_TAX_PAID: D(0),
            FOREIGN_BUSINESS_UNUSED_TAX_CREDITS: D(0),
            NET_FOREIGN_BUSINESS_INCOME: D(0),
            FOREIGN_SURTAX_OUTSIDE_CANADA: D(0),
            FOREIGN_PROPERTY_TAX_PAID: D(0),
            NET_FOREIGN_PROPERTY_INCOME: D(0),
        }
        for tax, income in rows
    ]
    output, _sheets = capability.compute(
        (
            Artifact(FOREIGN_TAX_COUNTRIES, RecordList(FOREIGN_TAX_COUNTRIES.fields, records)),
            Artifact(NET_INCOME, D(net_income)),
            Artifact(BASIC_TAX, D(basic_tax)),
        )
    ).outputs
    assert output.kind is CREDIT
    assert isinstance(output.value, Decimal)
    return output.value


def test_one_country_gives_the_lesser_of_its_tax_and_its_share_of_basic_federal_tax() -> None:
    # 10,000 x 14,000 / 100,000 = 1,400.00, less than the 1,500 paid.
    assert credit(("1500", "10000")) == D("1400.00")


def test_two_countries_over_200_of_tax_are_worked_one_by_one() -> None:
    # Total tax 1,600 is over 200: US lesser(1,500, 1,400.00) + UK lesser(100, 5,000 x 14,000 /
    # 100,000 = 700.00) = 1,400.00 + 100 = 1,500.00, not the pooled lesser(1,600, 2,100.00).
    assert credit(("1500", "10000"), ("100", "5000")) == D("1500.00")


def test_two_countries_with_exactly_200_of_tax_are_pooled() -> None:
    # Pooled: tax 200, income 1,500 x 14,000 / 100,000 = 210.00, so lesser(200, 210.00) = 200;
    # worked one by one it would be lesser(50, 70.00) + lesser(150, 140.00) = 50 + 140.00.
    assert credit(("50", "500"), ("150", "1000")) == D("200")


def test_two_countries_with_200_01_of_tax_are_worked_one_by_one() -> None:
    assert credit(("50", "500"), ("150.01", "1000")) == D("190.00")


# --- the business part (Form T2209 lines 4 to 11): line 5's rounding dataset ---------------------


def test_2025_business_rounding_is_half_up_to_the_cent_with_no_other_figure() -> None:
    data = SOURCE.get(BUSINESS_ROUNDING, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    # Line 5, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_business_rounding_cites_only_the_t2209_pdf() -> None:
    assert SOURCE.get(BUSINESS_ROUNDING, 2025, ROUNDING_ONLY).sources == (T2209_PDF,)


def test_the_business_rounding_header_quotes_t2209_as_the_form_prints_it() -> None:
    header = dataset_header(BUSINESS_ROUNDING)

    for quoted in (
        "Business income tax paid to a foreign country (5) for the year",
        "Net foreign business income (7) 43900",
        "Basic federal tax (8)",
        "Net income (3)",
        "Federal business foreign tax credit",
    ):
        assert quoted in header, quoted


def test_the_business_rounding_header_states_the_half_up_cent_rule() -> None:
    header = dataset_header(BUSINESS_ROUNDING).lower()

    assert "dollars-and-cents box" in header
    assert "half-up" in header
    assert "owner's decision" in header


def business_line_5(income: str, *, net_income: str, basic_tax: str) -> Decimal:
    """Line 5 of one sheet on the real business rounding dataset, through the line 5 capability."""
    capability = ForeignBusinessTaxCreditLine5(
        SOURCE.get(BUSINESS_ROUNDING, 2025, ROUNDING_ONLY),
        FOREIGN_TAX_CREDIT_SHEETS,
        NET_INCOME,
        BASIC_TAX,
        CREDIT,
    )
    sheet: dict[ArtifactKind[Any], object] = {
        FOREIGN_NON_BUSINESS_TAX_PAID: D(0),
        NET_FOREIGN_NON_BUSINESS_INCOME: D(0),
        FOREIGN_TAX_CREDIT_SHEET_LINE_3: D(0),
        FOREIGN_BUSINESS_TAX_PAID: D(0),
        FOREIGN_BUSINESS_UNUSED_TAX_CREDITS: D(0),
        NET_FOREIGN_BUSINESS_INCOME: D(income),
        FOREIGN_SURTAX_OUTSIDE_CANADA: D(0),
    }
    (output,) = capability.compute(
        (
            Artifact(
                FOREIGN_TAX_CREDIT_SHEETS, RecordList(FOREIGN_TAX_CREDIT_SHEETS.fields, [sheet])
            ),
            Artifact(NET_INCOME, D(net_income)),
            Artifact(BASIC_TAX, D(basic_tax)),
        )
    ).outputs
    assert output.kind is CREDIT
    assert isinstance(output.value, Decimal)
    return output.value


def test_business_line_5_is_the_income_times_basic_federal_tax_over_net_income() -> None:
    # 6,000 x 14,500 / 100,000 = 870.00 (note 8's basic federal tax).
    assert business_line_5("6000", net_income="100000", basic_tax="14500") == D("870.00")


def test_business_line_5_rounds_a_third_down_to_the_cent() -> None:
    # 100 x 100 / 300 = 33.333...
    assert business_line_5("100", net_income="300", basic_tax="100") == D("33.33")


def test_business_line_5_rounds_a_tie_up_to_the_cent() -> None:
    # 1 x 1 / 200 = 0.005 exactly, half-up gives 0.01.
    assert business_line_5("1", net_income="200", basic_tax="1") == D("0.01")
