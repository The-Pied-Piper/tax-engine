"""The 2025 capital cost allowance class rates (T776 Area A), checked against CRA's forms and
guides, and the rental lines they feed (T776 lines 9947, 9948 and 9936).

2025 Form T776 (Statement of Real Estate Rentals), Area A, "Calculation of capital cost allowance
(CCA) claim": "Column 20: CCA rate %"; Note 3: "If you have a negative amount in column 7, add it
to income as a recapture under "Recaptured capital cost allowance" on line 9947. If no property is
left in the class and there is a positive amount in this column, deduct the amount from your
income as a terminal loss under "Terminal loss" on line 9948. Recapture and terminal loss do not
apply to a Class 10.1 property unless it is a DIEP."; Note 7 (the AIIP factors) and Note 8 (the
RIIP factors), which end "The factor is 0 for any remaining AIIPs not listed in this note" and
"The factor is one half for any remaining RIIPs not listed in this note". The rates are the ones
printed in Guides T4036 and T4002 ("Class 1 (4%)", "Class 8 (20%)" and so on); the half-year rule
"does not apply to AIIPs, ZEVs, Class 56 properties" (T4002), and the owner decided that it does
not apply to Classes 12 and 52 either. A class with no printed rate (13, 14, 23, 24, 27 and 34)
is not listed, so it is refused. Every amount of Area A is a dollars-and-cents box, so the
columns the form computes (15, 17, 18 and the maximum) round half-up to the cent, the owner's
decision, as the forms state no rounding rule.

The dataset is tested on its own and with the capabilities that read it on the registered kinds;
the lines together, from the classes to T1 line 12600, are in `returns/2025_return_ap.yaml` and
`end_to_end/test_return_ap.py`.
"""

from __future__ import annotations

import re
from fractions import Fraction as ExactFraction
from pathlib import Path
from typing import Any

import pytest

import tax_engine.registrations
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.errors import InputAboveBoundError, InvalidRecordError
from tax_engine.domain.parameters.class_rates import (
    CLASS_RATES,
    ClassRate,
    HalfYearRule,
    HalfYearRuleOnSale,
    RecaptureAndTerminalLoss,
)
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    NET_RENTAL_INCOME,
    RENTAL_CCA_CLAIM,
    RENTAL_CCA_LIMIT,
    RENTAL_CCA_TABLE_CLAIM,
    RENTAL_CLOSING_UCC,
    RENTAL_NET_INCOME_AFTER_CCA,
    RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS,
    RENTAL_NET_INCOME_WITH_RECAPTURE,
    RENTAL_RECAPTURED_CCA,
    RENTAL_TERMINAL_LOSS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
FAMILY = "ca/cca_class_rates"
T776_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t776/t776-25e.txt"
T776_FILE = Path(__file__).parents[3] / "tests" / "fixtures" / "cra-forms-2025" / "t776-25e.txt"

# Every class with a printed rate in Guides T4036 and T4002.
RATES = {
    "1": "0.04",
    "2": "0.06",
    "3": "0.05",
    "6": "0.10",
    "7": "0.15",
    "8": "0.20",
    "9": "0.25",
    "10": "0.30",
    "10.1": "0.30",
    "12": "1",
    "14.1": "0.05",
    "16": "0.40",
    "17": "0.08",
    "31": "0.05",
    "32": "0.10",
    "43": "0.30",
    "43.1": "0.30",
    "43.2": "0.50",
    "44": "0.25",
    "45": "0.45",
    "46": "0.30",
    "50": "0.55",
    "52": "1",
    "53": "0.50",
    "54": "0.30",
    "55": "0.40",
    "56": "0.30",
}
UNLISTED = ["13", "14", "15", "23", "24", "27", "34", "59"]
HALF_YEAR_EXEMPT = {"12", "52", "56"}
EXCLUDED = {"10.1"}
# T776 Note 7, the AIIP factors; "The factor is 0 for any remaining AIIPs not listed in this note".
AIIP_FACTORS = {
    "43.1": ExactFraction(3, 2),
    "54": ExactFraction(3, 2),
    "56": ExactFraction(3, 2),
    "55": ExactFraction(7, 8),
    "43.2": ExactFraction(1, 2),
    "53": ExactFraction(1, 2),
    "44": ExactFraction(3),
    "46": ExactFraction(7, 3),
    "50": ExactFraction(9, 11),
}
# T776 Note 8, the RIIP factors; "The factor is one half for any remaining RIIPs not listed in
# this note".
RIIP_FACTORS = {
    "44": ExactFraction(3),
    "43.1": ExactFraction(7, 3),
    "46": ExactFraction(7, 3),
    "54": ExactFraction(7, 3),
    "56": ExactFraction(7, 3),
    "55": ExactFraction(3, 2),
    "53": ExactFraction(1),
    "50": ExactFraction(9, 11),
    "12": ExactFraction(0),
}


def squashed(text: str) -> str:
    """`text` with the comment markers and line breaks gone and runs of blanks made one."""
    return re.sub(r"\s+", " ", text.replace("#", " ")).strip()


def dataset_header() -> str:
    """The comment lines above the dataset's first key, squashed."""
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    lines = (root / "parameters" / "cca_class_rates" / "2025.yaml").read_text().splitlines()
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return squashed("\n".join(lines[:first_key]))


def dataset_class(number: str) -> ClassRate:
    found = SOURCE.get(FAMILY, 2025, CLASS_RATES).values.for_class(D(number))
    assert found is not None, number
    return found


def as_exact(part: Any) -> ExactFraction:
    return ExactFraction(part.numerator, part.denominator)


def test_2025_classes_are_every_class_with_a_printed_rate_in_the_guides() -> None:
    data = SOURCE.get(FAMILY, 2025, CLASS_RATES)

    assert {str(entry.class_number): entry.rate.value for entry in data.values.classes} == {
        number: D(rate) for number, rate in RATES.items()
    }


@pytest.mark.parametrize("number", UNLISTED)
def test_a_class_with_no_printed_rate_is_not_listed(number: str) -> None:
    assert SOURCE.get(FAMILY, 2025, CLASS_RATES).values.for_class(D(number)) is None


def test_2025_rounding_is_half_up_to_the_cent() -> None:
    assert SOURCE.get(FAMILY, 2025, CLASS_RATES).rounding == CENT


def test_2025_full_year_is_365_days() -> None:
    assert SOURCE.get(FAMILY, 2025, CLASS_RATES).values.full_year_days == 365


def test_2025_dataset_cites_the_t776_text() -> None:
    assert T776_TEXT in SOURCE.get(FAMILY, 2025, CLASS_RATES).sources


def test_the_half_year_rule_is_exempt_for_classes_12_52_and_56_only() -> None:
    data = SOURCE.get(FAMILY, 2025, CLASS_RATES)

    exempt = {
        str(entry.class_number)
        for entry in data.values.classes
        if entry.half_year_rule is HalfYearRule.EXEMPT
    }
    assert exempt == HALF_YEAR_EXEMPT


def test_recapture_and_terminal_loss_are_excluded_for_class_10_1_only() -> None:
    data = SOURCE.get(FAMILY, 2025, CLASS_RATES)

    excluded = {
        str(entry.class_number)
        for entry in data.values.classes
        if entry.recapture_and_terminal_loss is RecaptureAndTerminalLoss.EXCLUDED
    }
    assert excluded == EXCLUDED


def test_the_half_year_rule_on_sale_applies_to_class_10_1_only() -> None:
    data = SOURCE.get(FAMILY, 2025, CLASS_RATES)

    on_sale = {
        str(entry.class_number)
        for entry in data.values.classes
        if entry.half_year_rule_on_sale is HalfYearRuleOnSale.APPLIES
    }
    assert on_sale == {"10.1"}


def test_class_1_lists_the_elections_of_the_guide_and_no_other_class_does() -> None:
    # Guide T4036 2025, "Class 1 (4%)": 10% for a new purpose-built residential rental (code 1),
    # and, by election to put a building in a separate class, 6% for other eligible non-residential
    # buildings (code 2) and 10% for manufacturing or processing ones (code 3).
    data = SOURCE.get(FAMILY, 2025, CLASS_RATES)

    held = {
        str(entry.class_number): {e.code: str(e.rate.value) for e in entry.elections}
        for entry in data.values.classes
        if entry.elections
    }
    assert held == {"1": {1: "0.10", 2: "0.06", 3: "0.10"}}
    assert [e.code for e in dataset_class("1").elections] == [1, 2, 3]
    assert str(dataset_class("1").rate.value) == "0.04"


def test_the_dataset_header_quotes_the_guide_on_the_class_1_elections() -> None:
    header = dataset_header().lower()

    for quoted in (
        "may now be eligible for an accelerated cca rate of 10%.",
        "the cca rate for eligible non-residential buildings acquired by a taxpayer after march "
        "18, 2007, and used in canada to manufacture or process goods for sale or lease includes "
        "an additional allowance of 6% for a total rate of 10%.",
        "the cca rate for other eligible non-residential buildings includes an additional "
        "allowance of 2% for a total rate of 6%.",
        "if you do not file an election to put it in a separate class, the 4% rate will apply.",
        "under proposed changes",
    ):
        assert quoted in header, quoted


@pytest.mark.parametrize("number", RATES)
def test_each_class_has_the_aiip_and_riip_factors_of_notes_7_and_8(number: str) -> None:
    entry = dataset_class(number)

    assert as_exact(entry.aiip_factor) == AIIP_FACTORS.get(number, ExactFraction(0))
    assert as_exact(entry.riip_factor) == RIIP_FACTORS.get(number, ExactFraction(1, 2))


def test_the_dataset_header_quotes_the_form_as_it_prints_it() -> None:
    header = dataset_header().lower()
    form = squashed(T776_FILE.read_text(encoding="utf-8-sig")).lower()

    for quoted in (
        "column 20: cca rate %",
        "recapture and terminal loss do not apply to a class 10.1 property unless it is a diep",
        "the factor is 0 for any remaining aiips not listed in this note",
        "the factor is one half for any remaining riips not listed in this note",
    ):
        assert quoted in header, quoted
        assert quoted in form, quoted


def test_the_dataset_header_quotes_the_guides_on_the_half_year_rule_on_sale() -> None:
    header = dataset_header().lower()

    for quoted in (
        "for a class 10.1 vehicle you disposed of in your 2025 fiscal period, you may be able to "
        "claim 50% of the cca that would be allowed if you still owned the vehicle at the end of "
        "your 2025 fiscal period. this is known as the half-year rule on sale.",
        "you can use the half-year rule on sale if, at the end of your 2024 fiscal period, you "
        "owned the class 10.1 vehicle you disposed of in 2025.",
        "enter 50% of the amount from column 2 (for class 10.1 vehicles) in column 19.",
    ):
        assert quoted in header, quoted


def test_the_dataset_header_quotes_the_guide_on_prorating_a_short_first_fiscal_period() -> None:
    # Guide T4002 2025 "You were asking?".
    header = dataset_header().lower()

    for quoted in (
        "since your fiscal period is less than 365 days, you have to prorate your cca claim.",
        "base your cca claim on the number of days in your fiscal period compared to 365 days.",
        "the amount of cca you can claim is $2,052 ($3,500 \u00d7 214 \u00f7 365).",
    ):
        assert quoted in header, quoted


def test_the_dataset_header_states_the_half_year_rule_and_the_rounding_decisions() -> None:
    header = dataset_header().lower()

    assert "the half-year rule does not apply to aiips, zevs, class 56 properties" in header
    assert "half-up" in header
    assert "owner's decision" in header
    assert "to the cent" in header


# --- the rental lines the classes feed ------------------------------------------------------------


def landlord(
    *classes: tuple[str, str, str, str, str, str, str, int, str, str, str, str], **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """A landlord with gross rents of 24000 and expenses of 12000, so amount 5 is 12000 before
    Area A, with the Area A `classes`."""
    statement: dict[str, Any] = {
        "rental_properties": ((2, "0", "24000"),),
        "rental_expenses": {"insurance": ("12000", "0", "0")},
        "rental_cca_classes_rows": classes,
    }
    return run("0", (), "0", "0", "0", "0", "0", rental_statements=({**statement, **overrides},))


def test_a_recapture_row_adds_the_negative_column_7_to_line_9947() -> None:
    # Class 8: UCC at the start 1000, proceeds of dispositions 4000, so column 7 is
    # 1000 + 0 - 4000 = -3000, "a negative amount in column 7", added to income as a recapture on
    # line 9947: 3000. Amount 4 is amount 3 (12000) plus 3000, 15000; no claim is allowed on a
    # negative column 7, so line 9936 is 0 and amount 6, line 9946 and T1 line 12600 are 15000.
    result = landlord(("8", "1000", "0", "4000", "0", "0", "0", 0, "0", "0", "0", "0"))
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_RECAPTURED_CCA).value == D("3000")
    assert statement.get(RENTAL_NET_INCOME_WITH_RECAPTURE).value == D("15000")
    assert statement.get(RENTAL_CCA_CLAIM).value == D("0")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("15000")
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert (
        "rental_cca_table_recapture: item 1 class 8: column 7 -3000 is negative: recapture 3000"
    ) in rendered
    assert (
        "rental_recaptured_cca: rental_cca_table_recapture 3000, "
        "chosen as rental_coowner_checked is 0"
    ) in rendered


def test_a_terminal_loss_row_takes_the_positive_column_7_off_on_line_9948() -> None:
    # Class 1: UCC at the start 2000, no additions or dispositions, no property left in the class:
    # column 7 is 2000, "a positive amount in this column" with "no property left in the class",
    # deducted as a terminal loss on line 9948. Amount 5 is 12000 - 2000 = 10000.
    result = landlord(("1", "2000", "0", "0", "0", "0", "0", 1, "0", "0", "0", "0"))
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_TERMINAL_LOSS).value == D("2000")
    assert statement.get(RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS).value == D("10000")
    assert statement.get(RENTAL_CCA_CLAIM).value == D("0")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("10000")
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert (
        "rental_cca_table_terminal_loss: item 1 class 1: column 7 2000 with no property left: "
        "terminal loss 2000"
    ) in rendered


def test_a_class_with_property_left_has_no_terminal_loss() -> None:
    result = landlord(("1", "2000", "0", "0", "0", "0", "0", 0, "0", "0", "0", "0"))
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_TERMINAL_LOSS).value == D("0")


def test_class_10_1_has_no_recapture_or_terminal_loss() -> None:
    # Note 3: "Recapture and terminal loss do not apply to a Class 10.1 property unless it is a
    # DIEP", and DIEPs (columns 4, 6, 8 and 9) are not modelled.
    recapture = landlord(("10.1", "1000", "0", "4000", "0", "0", "0", 0, "0", "0", "0", "0"))[
        "ca/t776"
    ][0]
    terminal = landlord(("10.1", "2000", "0", "0", "0", "0", "0", 1, "0", "0", "0", "0"))[
        "ca/t776"
    ][0]

    assert recapture.get(RENTAL_RECAPTURED_CCA).value == D("0")
    assert terminal.get(RENTAL_TERMINAL_LOSS).value == D("0")


def test_the_closing_ucc_of_a_recapture_row_is_zero() -> None:
    # Guide T4036, Column 7: "You cannot claim CCA when the amount in column 7 is: negative",
    # "In either case, enter "0" in column 24".
    result = landlord(("8", "1000", "0", "4000", "0", "0", "0", 0, "0", "0", "0", "0"))
    statement = result["ca/t776"][0]

    (record,) = statement.get(RENTAL_CLOSING_UCC).value.records
    assert [value for value in record.values()] == [D("8"), D("0")]


def test_a_claim_at_the_loss_limit_is_allowed_and_brings_the_rental_income_to_zero() -> None:
    # Class 1: UCC 400000, so the maximum is 400000 x 4% = 16000.00. The CCA of the owner's one
    # statement is limited over all the statements together to amount 5, 12000: "You cannot use
    # CCA to create or increase a rental loss". A claim of 12000 is allowed, so amount 6 is
    # 12000 - 12000 = 0.
    result = landlord(("1", "400000", "0", "0", "0", "0", "12000", 0, "0", "0", "0", "0"))
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_CCA_TABLE_CLAIM).value == D("12000")
    assert statement.get(RENTAL_CCA_LIMIT).value == D("12000")
    assert statement.get(RENTAL_CCA_CLAIM).value == D("12000")
    assert statement.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("0")
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert (
        "rental_cca_claim: rental_cca_claim_less_personal_part 12000 "
        "less rental_cca_business_use_of_home 0 = 12000"
    ) in rendered


def test_a_claim_above_the_loss_limit_is_refused_not_capped() -> None:
    # The same class with a claim of 12001, below the class maximum of 16000.00 but above amount
    # 5: refused by the combined limit over all the statements, not capped to 12000.
    with pytest.raises(
        InputAboveBoundError,
        match=r"rental_cca_claims_total 12001 is above ca/rental_cca_limit_all_statements 12000",
    ):
        landlord(("1", "400000", "0", "0", "0", "0", "12001", 0, "0", "0", "0", "0"))


def test_the_loss_limit_is_checked_on_line_9936_after_the_personal_part_and_business_use() -> None:
    # Amount ii is 13000 (a claim above amount 5), less a personal part of 1000 and 500 of CCA
    # for business-use-of-home expenses: line 9936 is 11500, within the limit of 12000, so
    # amount 6 is 12000 - 11500 = 500.
    result = landlord(
        ("1", "400000", "0", "0", "0", "0", "13000", 0, "0", "0", "0", "0"),
        rental_cca_personal_part="1000",
        rental_cca_business_use_of_home="500",
    )
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_CCA_TABLE_CLAIM).value == D("13000")
    assert statement.get(RENTAL_CCA_CLAIM).value == D("11500")
    assert statement.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("500")


def test_a_personal_part_that_leaves_the_claim_above_the_limit_is_still_refused() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=r"rental_cca_claims_total 12500 is above ca/rental_cca_limit_all_statements 12000",
    ):
        landlord(
            ("1", "400000", "0", "0", "0", "0", "16000", 0, "0", "0", "0", "0"),
            rental_cca_personal_part="3500",
        )


def test_the_limit_is_zero_for_a_rental_loss_and_no_claim_is_allowed() -> None:
    # Gross rents of 24000 and expenses of 26000: amount 5 is -2000, floored at 0, so a claim
    # of 1 is refused and a claim of 0 gives a loss of 2000.
    loss = {"rental_expenses": {"insurance": ("26000", "0", "0")}}

    result = landlord(("1", "400000", "0", "0", "0", "0", "0", 0, "0", "0", "0", "0"), **loss)
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]
    assert statement.get(RENTAL_CCA_LIMIT).value == D("0")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("-2000")
    with pytest.raises(
        InputAboveBoundError,
        match=r"rental_cca_claims_total 1 is above ca/rental_cca_limit_all_statements 0",
    ):
        landlord(("1", "400000", "0", "0", "0", "0", "1", 0, "0", "0", "0", "0"), **loss)


def test_a_recapture_in_the_class_list_raises_the_loss_limit() -> None:
    # Amount 5 is amount 4 (amount 3 plus line 9947) less line 9948, so a recapture of 3000 in the
    # class list lets a second class claim up to 15000, where 12000 alone would be the limit.
    result = landlord(
        ("8", "1000", "0", "4000", "0", "0", "0", 0, "0", "0", "0", "0"),
        ("1", "400000", "0", "0", "0", "0", "15000", 0, "0", "0", "0", "0"),
    )
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_CCA_LIMIT).value == D("15000")
    assert statement.get(RENTAL_CCA_CLAIM).value == D("15000")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("0")


def test_a_claim_above_the_classs_maximum_is_refused() -> None:
    # Class 1: 200000 x 4% = 8000.00 is the most; 8001 is refused by the table before the limit.
    with pytest.raises(
        InputAboveBoundError, match="item 1: ca/cca_claimed 8001 is above the maximum 8000.00"
    ):
        landlord(("1", "200000", "0", "0", "0", "0", "8001", 0, "0", "0", "0", "0"))


def test_a_class_with_no_printed_rate_is_refused_naming_the_item() -> None:
    with pytest.raises(InvalidRecordError, match="item 1: class 13 is not in the class rates"):
        landlord(("13", "1000", "0", "0", "0", "0", "0", 0, "0", "0", "0", "0"))
