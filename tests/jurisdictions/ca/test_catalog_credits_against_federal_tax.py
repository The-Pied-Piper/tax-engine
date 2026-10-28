"""Registered and money kinds of the federal catalog family `credits_against_federal_tax`."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_calculator.domain.artifact import Artifact, ArtifactKind, ArtifactRegistry
from tax_calculator.domain.errors import InvalidRecordError, NegativeArtifactError
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.jurisdictions.ca.catalog import (
    CREDITS_AGAINST_FEDERAL_TAX,
    FEDERAL_BUSINESS_FOREIGN_TAX_CREDIT,
    FEDERAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT,
    FEDERAL_LOGGING_TAX_CREDIT,
    FEDERAL_TAX,
    FEDERAL_TAX_LESS_CREDITS,
    FEDERAL_TAX_LINE_41700,
    FOREIGN_BUSINESS_TAX_CREDIT_LINE_4,
    FOREIGN_BUSINESS_TAX_CREDIT_LINE_5,
    FOREIGN_BUSINESS_TAX_CREDIT_LINE_7,
    FOREIGN_BUSINESS_TAX_CREDIT_LINE_8,
    FOREIGN_BUSINESS_TAX_CREDIT_LINE_10,
    FOREIGN_BUSINESS_TAX_PAID,
    FOREIGN_BUSINESS_UNUSED_TAX_CREDITS,
    FOREIGN_NON_BUSINESS_TAX_PAID,
    FOREIGN_PROPERTY_TAX_PAID,
    FOREIGN_SURTAX_OUTSIDE_CANADA,
    FOREIGN_TAX_COUNTRIES,
    FOREIGN_TAX_CREDIT_SHEET_LINE_3,
    FOREIGN_TAX_CREDIT_SHEETS,
    ITC_APPRENTICE_SALARY_AND_WAGES,
    ITC_APPRENTICES,
    ITC_APPRENTICESHIP_WAGES_TOTAL,
    LABOUR_SPONSORED_FUNDS_CREDIT,
    LABOUR_SPONSORED_FUNDS_CREDIT_BEFORE_MAXIMUM,
    LABOUR_SPONSORED_FUNDS_NET_COST,
    LOGGING_CREDIT_BASE,
    LOGGING_CREDIT_CAP,
    LOGGING_OPERATIONS,
    LOGGING_TAX_PAID,
    NET_FOREIGN_BUSINESS_INCOME,
    NET_FOREIGN_NON_BUSINESS_INCOME,
    NET_FOREIGN_PROPERTY_INCOME,
    NET_LOGGING_INCOME,
    POLITICAL_CREDIT,
    POLITICAL_CREDIT_BEFORE_MAXIMUM,
    POLITICAL_CREDIT_CHOSEN_COLUMN,
    POLITICAL_CREDIT_COLUMN_1_LINE_2,
    POLITICAL_CREDIT_COLUMN_1_LINE_3,
    POLITICAL_CREDIT_COLUMN_1_LINE_5,
    POLITICAL_CREDIT_COLUMN_1_LINE_6,
    POLITICAL_CREDIT_COLUMN_1_LINE_7,
    POLITICAL_CREDIT_COLUMN_2_LINE_2,
    POLITICAL_CREDIT_COLUMN_2_LINE_3,
    POLITICAL_CREDIT_COLUMN_2_LINE_5,
    POLITICAL_CREDIT_COLUMN_2_LINE_6,
    POLITICAL_CREDIT_COLUMN_2_LINE_7,
    POLITICAL_CREDIT_COLUMN_3_LINE_2,
    POLITICAL_CREDIT_COLUMN_3_LINE_3,
    POLITICAL_CREDIT_COLUMN_3_LINE_5,
    POLITICAL_CREDIT_COLUMN_3_LINE_6,
    POLITICAL_CREDIT_COLUMN_3_LINE_7,
    POLITICAL_CREDIT_SHORTCUT_AMOUNT,
    POLITICAL_CREDIT_SHORTCUT_THRESHOLD,
    PROVINCES_LOGGING_TAX_CREDIT,
)


def test_the_credits_against_federal_tax_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    assert registry.get("ca/labour_sponsored_funds_net_cost") is LABOUR_SPONSORED_FUNDS_NET_COST
    assert registry.get("ca/political_credit_column_1_line_2") is POLITICAL_CREDIT_COLUMN_1_LINE_2
    assert registry.get("ca/political_credit_column_1_line_3") is POLITICAL_CREDIT_COLUMN_1_LINE_3
    assert registry.get("ca/political_credit_column_1_line_5") is POLITICAL_CREDIT_COLUMN_1_LINE_5
    assert registry.get("ca/political_credit_column_1_line_6") is POLITICAL_CREDIT_COLUMN_1_LINE_6
    assert registry.get("ca/political_credit_column_1_line_7") is POLITICAL_CREDIT_COLUMN_1_LINE_7
    assert registry.get("ca/political_credit_column_2_line_2") is POLITICAL_CREDIT_COLUMN_2_LINE_2
    assert registry.get("ca/political_credit_column_2_line_3") is POLITICAL_CREDIT_COLUMN_2_LINE_3
    assert registry.get("ca/political_credit_column_2_line_5") is POLITICAL_CREDIT_COLUMN_2_LINE_5
    assert registry.get("ca/political_credit_column_2_line_6") is POLITICAL_CREDIT_COLUMN_2_LINE_6
    assert registry.get("ca/political_credit_column_2_line_7") is POLITICAL_CREDIT_COLUMN_2_LINE_7
    assert registry.get("ca/political_credit_column_3_line_2") is POLITICAL_CREDIT_COLUMN_3_LINE_2
    assert registry.get("ca/political_credit_column_3_line_3") is POLITICAL_CREDIT_COLUMN_3_LINE_3
    assert registry.get("ca/political_credit_column_3_line_5") is POLITICAL_CREDIT_COLUMN_3_LINE_5
    assert registry.get("ca/political_credit_column_3_line_6") is POLITICAL_CREDIT_COLUMN_3_LINE_6
    assert registry.get("ca/political_credit_column_3_line_7") is POLITICAL_CREDIT_COLUMN_3_LINE_7
    assert registry.get("ca/political_credit_chosen_column") is POLITICAL_CREDIT_CHOSEN_COLUMN
    assert (
        registry.get("ca/political_credit_shortcut_threshold")
        is POLITICAL_CREDIT_SHORTCUT_THRESHOLD
    )
    assert registry.get("ca/political_credit_shortcut_amount") is POLITICAL_CREDIT_SHORTCUT_AMOUNT
    assert registry.get("ca/political_credit_before_maximum") is POLITICAL_CREDIT_BEFORE_MAXIMUM
    assert registry.get("ca/political_credit") is POLITICAL_CREDIT
    assert (
        registry.get("ca/labour_sponsored_funds_credit_before_maximum")
        is LABOUR_SPONSORED_FUNDS_CREDIT_BEFORE_MAXIMUM
    )
    assert registry.get("ca/labour_sponsored_funds_credit") is LABOUR_SPONSORED_FUNDS_CREDIT
    assert registry.get("ca/credits_against_federal_tax") is CREDITS_AGAINST_FEDERAL_TAX
    assert registry.get("ca/federal_tax_less_credits") is FEDERAL_TAX_LESS_CREDITS
    assert registry.get("ca/federal_tax_line_41700") is FEDERAL_TAX_LINE_41700


def test_the_federal_tax_line_41700_is_a_non_negative_decimal(registry: ArtifactRegistry) -> None:
    # T1 line 139 and line 41700 "Line 134 minus line 138 (if negative, enter "0")", or, when Part 5
    # line 11 of Form T691 is positive, Part 6 line 14 "Enter this amount on line 41700 of your
    # return.": the figure entered on line 41700, never below 0.
    assert FEDERAL_TAX_LINE_41700.identifier == "ca/federal_tax_line_41700"
    assert FEDERAL_TAX_LINE_41700.value_type is Decimal
    assert FEDERAL_TAX_LINE_41700.non_negative is True
    assert registry.kind("ca/federal_tax_line_41700") is FEDERAL_TAX_LINE_41700


def test_a_negative_federal_tax_line_41700_is_refused() -> None:
    # A negative figure is an input error on the line 41700 entry, refused and not taken as 0.
    with pytest.raises(NegativeArtifactError, match="ca/federal_tax_line_41700 cannot be negative"):
        Artifact(FEDERAL_TAX_LINE_41700, Decimal("-1"))


def test_the_credits_against_federal_tax_kinds_are_money() -> None:
    for kind in (
        LABOUR_SPONSORED_FUNDS_NET_COST,
        POLITICAL_CREDIT_COLUMN_1_LINE_2,
        POLITICAL_CREDIT_COLUMN_1_LINE_3,
        POLITICAL_CREDIT_COLUMN_1_LINE_5,
        POLITICAL_CREDIT_COLUMN_1_LINE_6,
        POLITICAL_CREDIT_COLUMN_1_LINE_7,
        POLITICAL_CREDIT_COLUMN_2_LINE_2,
        POLITICAL_CREDIT_COLUMN_2_LINE_3,
        POLITICAL_CREDIT_COLUMN_2_LINE_5,
        POLITICAL_CREDIT_COLUMN_2_LINE_6,
        POLITICAL_CREDIT_COLUMN_2_LINE_7,
        POLITICAL_CREDIT_COLUMN_3_LINE_2,
        POLITICAL_CREDIT_COLUMN_3_LINE_3,
        POLITICAL_CREDIT_COLUMN_3_LINE_5,
        POLITICAL_CREDIT_COLUMN_3_LINE_6,
        POLITICAL_CREDIT_COLUMN_3_LINE_7,
        POLITICAL_CREDIT_CHOSEN_COLUMN,
        POLITICAL_CREDIT_SHORTCUT_THRESHOLD,
        POLITICAL_CREDIT_SHORTCUT_AMOUNT,
        POLITICAL_CREDIT_BEFORE_MAXIMUM,
        POLITICAL_CREDIT,
        LABOUR_SPONSORED_FUNDS_CREDIT_BEFORE_MAXIMUM,
        LABOUR_SPONSORED_FUNDS_CREDIT,
        CREDITS_AGAINST_FEDERAL_TAX,
        FEDERAL_TAX_LESS_CREDITS,
        FEDERAL_TAX_LINE_41700,
    ):
        assert kind.value_type is Decimal, kind.identifier


# --- Form T2209: the countries of the foreign tax credit ----------------------------------------


def test_the_foreign_non_business_tax_paid_is_a_non_negative_decimal(
    registry: ArtifactRegistry,
) -> None:
    # T2209 line 1 "Non-business income tax paid to a foreign country (1) 43100"; note (1) is
    # the tax paid minus the part deductible under subsection 20(11) or deducted under 20(12).
    assert FOREIGN_NON_BUSINESS_TAX_PAID.identifier == "ca/foreign_non_business_tax_paid"
    assert FOREIGN_NON_BUSINESS_TAX_PAID.value_type is Decimal
    assert FOREIGN_NON_BUSINESS_TAX_PAID.non_negative is True
    assert registry.kind("ca/foreign_non_business_tax_paid") is FOREIGN_NON_BUSINESS_TAX_PAID


def test_the_net_foreign_non_business_income_is_a_non_negative_decimal(
    registry: ArtifactRegistry,
) -> None:
    # T2209 line 2 "Net foreign non-business income (2) 43300".
    assert NET_FOREIGN_NON_BUSINESS_INCOME.identifier == "ca/net_foreign_non_business_income"
    assert NET_FOREIGN_NON_BUSINESS_INCOME.value_type is Decimal
    assert NET_FOREIGN_NON_BUSINESS_INCOME.non_negative is True
    assert registry.kind("ca/net_foreign_non_business_income") is NET_FOREIGN_NON_BUSINESS_INCOME


def test_the_foreign_tax_countries_are_a_record_list_of_the_t2209_inputs(
    registry: ArtifactRegistry,
) -> None:
    # T2209: "do the applicable calculation ... for each country on a separate sheet"; each
    # record holds one country's non-business figures (lines 43100, 43300), then its business
    # figures: line 4's two parts (43400), line 43900 and line 6.
    assert isinstance(FOREIGN_TAX_COUNTRIES, RecordListKind)
    assert FOREIGN_TAX_COUNTRIES.identifier == "ca/foreign_tax_countries"
    assert FOREIGN_TAX_COUNTRIES.value_type is RecordList
    assert FOREIGN_TAX_COUNTRIES.fields == (
        FOREIGN_NON_BUSINESS_TAX_PAID,
        NET_FOREIGN_NON_BUSINESS_INCOME,
        FOREIGN_BUSINESS_TAX_PAID,
        FOREIGN_BUSINESS_UNUSED_TAX_CREDITS,
        NET_FOREIGN_BUSINESS_INCOME,
        FOREIGN_SURTAX_OUTSIDE_CANADA,
        FOREIGN_PROPERTY_TAX_PAID,
        NET_FOREIGN_PROPERTY_INCOME,
    )
    assert registry.get("ca/foreign_tax_countries") is FOREIGN_TAX_COUNTRIES


def foreign_country_record(**changes: object) -> dict[ArtifactKind[Any], object]:
    names: dict[str, ArtifactKind[Any]] = {
        "tax_paid": FOREIGN_NON_BUSINESS_TAX_PAID,
        "income": NET_FOREIGN_NON_BUSINESS_INCOME,
        "business_tax_paid": FOREIGN_BUSINESS_TAX_PAID,
        "unused_credits": FOREIGN_BUSINESS_UNUSED_TAX_CREDITS,
        "business_income": NET_FOREIGN_BUSINESS_INCOME,
        "surtax": FOREIGN_SURTAX_OUTSIDE_CANADA,
        "property_tax_paid": FOREIGN_PROPERTY_TAX_PAID,
        "property_income": NET_FOREIGN_PROPERTY_INCOME,
    }
    record: dict[ArtifactKind[Any], object] = {
        FOREIGN_NON_BUSINESS_TAX_PAID: Decimal("1500"),
        NET_FOREIGN_NON_BUSINESS_INCOME: Decimal("10000"),
        FOREIGN_BUSINESS_TAX_PAID: Decimal("400"),
        FOREIGN_BUSINESS_UNUSED_TAX_CREDITS: Decimal("50"),
        NET_FOREIGN_BUSINESS_INCOME: Decimal("6000"),
        FOREIGN_SURTAX_OUTSIDE_CANADA: Decimal("0"),
        FOREIGN_PROPERTY_TAX_PAID: Decimal("0"),
        NET_FOREIGN_PROPERTY_INCOME: Decimal("0"),
    }
    for name, value in changes.items():
        record[names[name]] = value
    return record


def test_the_foreign_tax_countries_hold_each_countrys_figures_in_the_callers_order() -> None:
    rows = RecordList(
        FOREIGN_TAX_COUNTRIES.fields,
        [foreign_country_record(), foreign_country_record(tax_paid=Decimal("100"))],
    )

    assert [record[FOREIGN_NON_BUSINESS_TAX_PAID] for record in rows.records] == [
        Decimal("1500"),
        Decimal("100"),
    ]
    assert rows.records[0][NET_FOREIGN_NON_BUSINESS_INCOME] == Decimal("10000")


def test_the_foreign_tax_countries_may_be_empty() -> None:
    assert RecordList(FOREIGN_TAX_COUNTRIES.fields, []).records == ()


@pytest.mark.parametrize(
    "field",
    [
        "tax_paid",
        "income",
        "business_tax_paid",
        "unused_credits",
        "business_income",
        "surtax",
        "property_tax_paid",
        "property_income",
    ],
)
def test_a_foreign_country_refuses_a_negative_figure(field: str) -> None:
    with pytest.raises(NegativeArtifactError, match="item 1"):
        RecordList(FOREIGN_TAX_COUNTRIES.fields, [foreign_country_record(**{field: Decimal("-1")})])


def test_a_foreign_country_missing_a_figure_is_refused_naming_the_row() -> None:
    record = foreign_country_record()
    del record[NET_FOREIGN_NON_BUSINESS_INCOME]

    with pytest.raises(InvalidRecordError, match="item 1.*net_foreign_non_business_income"):
        RecordList(FOREIGN_TAX_COUNTRIES.fields, [record])


@pytest.mark.parametrize(
    "missing",
    [
        FOREIGN_BUSINESS_TAX_PAID,
        FOREIGN_BUSINESS_UNUSED_TAX_CREDITS,
        NET_FOREIGN_BUSINESS_INCOME,
        FOREIGN_SURTAX_OUTSIDE_CANADA,
        FOREIGN_PROPERTY_TAX_PAID,
        NET_FOREIGN_PROPERTY_INCOME,
    ],
    ids=lambda kind: kind.identifier,
)
def test_a_foreign_country_missing_a_business_figure_is_refused_naming_the_row(
    missing: ArtifactKind[Any],
) -> None:
    record = foreign_country_record()
    del record[missing]

    with pytest.raises(
        InvalidRecordError, match=f"item 1.*{missing.identifier.removeprefix('ca/')}"
    ):
        RecordList(FOREIGN_TAX_COUNTRIES.fields, [record])


# --- Form T2209: the business figures of a country (lines 4 to 6) --------------------------------

BUSINESS_FIELDS: list[tuple[str, ArtifactKind[Any]]] = [
    ("ca/foreign_business_tax_paid", FOREIGN_BUSINESS_TAX_PAID),
    ("ca/foreign_business_unused_tax_credits", FOREIGN_BUSINESS_UNUSED_TAX_CREDITS),
    ("ca/net_foreign_business_income", NET_FOREIGN_BUSINESS_INCOME),
    ("ca/foreign_surtax_outside_canada", FOREIGN_SURTAX_OUTSIDE_CANADA),
    ("ca/foreign_property_tax_paid", FOREIGN_PROPERTY_TAX_PAID),
    ("ca/net_foreign_property_income", NET_FOREIGN_PROPERTY_INCOME),
]


@pytest.mark.parametrize(("identifier", "kind"), BUSINESS_FIELDS)
def test_the_foreign_business_record_fields_are_non_negative_decimals(
    registry: ArtifactRegistry, identifier: str, kind: ArtifactKind[Any]
) -> None:
    # T2209 line 4 (43400) "Business income tax paid to a foreign country (5) for the year, plus
    # any unused foreign tax credits for that country for the 10 years (6) before, and the 3 years
    # after this year"; line 5 "Net foreign business income (7) 43900"; line 6 "Federal surtax on
    # income allocated to "Other (Outside Canada)"": record fields, not artifacts of their own.
    assert kind.identifier == identifier
    assert kind.value_type is Decimal
    assert kind.non_negative is True
    assert registry.kind(identifier) is kind


# --- Form T2209: the sheets of the foreign tax credit -------------------------------------------


def test_the_sheet_line_3_is_a_non_negative_decimal(registry: ArtifactRegistry) -> None:
    # T2209 line 3 "Enter whichever is less: the amount from line 1 or line 2."
    assert FOREIGN_TAX_CREDIT_SHEET_LINE_3.identifier == "ca/foreign_tax_credit_sheet_line_3"
    assert FOREIGN_TAX_CREDIT_SHEET_LINE_3.value_type is Decimal
    assert FOREIGN_TAX_CREDIT_SHEET_LINE_3.non_negative is True
    assert registry.kind("ca/foreign_tax_credit_sheet_line_3") is FOREIGN_TAX_CREDIT_SHEET_LINE_3


def test_the_foreign_tax_credit_sheets_are_a_record_list_of_the_sheet_figures() -> None:
    assert isinstance(FOREIGN_TAX_CREDIT_SHEETS, RecordListKind)
    assert FOREIGN_TAX_CREDIT_SHEETS.identifier == "ca/foreign_tax_credit_sheets"
    assert FOREIGN_TAX_CREDIT_SHEETS.value_type is RecordList
    assert FOREIGN_TAX_CREDIT_SHEETS.fields == (
        FOREIGN_NON_BUSINESS_TAX_PAID,
        NET_FOREIGN_NON_BUSINESS_INCOME,
        FOREIGN_TAX_CREDIT_SHEET_LINE_3,
        FOREIGN_BUSINESS_TAX_PAID,
        FOREIGN_BUSINESS_UNUSED_TAX_CREDITS,
        NET_FOREIGN_BUSINESS_INCOME,
        FOREIGN_SURTAX_OUTSIDE_CANADA,
    )


def foreign_sheet_record(**changes: object) -> dict[ArtifactKind[Any], object]:
    names = {
        "tax_paid": FOREIGN_NON_BUSINESS_TAX_PAID,
        "income": NET_FOREIGN_NON_BUSINESS_INCOME,
        "line_3": FOREIGN_TAX_CREDIT_SHEET_LINE_3,
        "business_tax_paid": FOREIGN_BUSINESS_TAX_PAID,
        "unused_credits": FOREIGN_BUSINESS_UNUSED_TAX_CREDITS,
        "business_income": NET_FOREIGN_BUSINESS_INCOME,
        "surtax": FOREIGN_SURTAX_OUTSIDE_CANADA,
    }
    record: dict[ArtifactKind[Any], object] = {
        FOREIGN_NON_BUSINESS_TAX_PAID: Decimal("1500"),
        NET_FOREIGN_NON_BUSINESS_INCOME: Decimal("10000"),
        FOREIGN_TAX_CREDIT_SHEET_LINE_3: Decimal("1400"),
        FOREIGN_BUSINESS_TAX_PAID: Decimal("400"),
        FOREIGN_BUSINESS_UNUSED_TAX_CREDITS: Decimal("50"),
        NET_FOREIGN_BUSINESS_INCOME: Decimal("6000"),
        FOREIGN_SURTAX_OUTSIDE_CANADA: Decimal("0"),
    }
    for name, value in changes.items():
        record[names[name]] = value
    return record


def test_the_foreign_tax_credit_sheets_hold_each_sheet_in_order() -> None:
    rows = RecordList(
        FOREIGN_TAX_CREDIT_SHEETS.fields,
        [foreign_sheet_record(), foreign_sheet_record(line_3=Decimal("100"))],
    )

    assert [record[FOREIGN_TAX_CREDIT_SHEET_LINE_3] for record in rows.records] == [
        Decimal("1400"),
        Decimal("100"),
    ]


def test_the_foreign_tax_credit_sheets_may_be_empty() -> None:
    assert RecordList(FOREIGN_TAX_CREDIT_SHEETS.fields, []).records == ()


def test_a_foreign_tax_credit_sheet_refuses_a_negative_line_3() -> None:
    with pytest.raises(NegativeArtifactError):
        RecordList(FOREIGN_TAX_CREDIT_SHEETS.fields, [foreign_sheet_record(line_3=Decimal("-1"))])


@pytest.mark.parametrize(
    "field", ["business_tax_paid", "unused_credits", "business_income", "surtax"]
)
def test_a_foreign_tax_credit_sheet_refuses_a_negative_business_figure(field: str) -> None:
    with pytest.raises(NegativeArtifactError, match="item 1"):
        RecordList(
            FOREIGN_TAX_CREDIT_SHEETS.fields, [foreign_sheet_record(**{field: Decimal("-1")})]
        )


def test_a_foreign_tax_credit_sheet_missing_a_business_figure_is_refused_naming_the_row() -> None:
    record = foreign_sheet_record()
    del record[NET_FOREIGN_BUSINESS_INCOME]

    with pytest.raises(InvalidRecordError, match="item 1.*net_foreign_business_income"):
        RecordList(FOREIGN_TAX_CREDIT_SHEETS.fields, [record])


# --- Form T2209: the lines of the federal business foreign tax credit -----------------------------

BUSINESS_LINES: list[tuple[str, ArtifactKind[Any], bool]] = [
    # (identifier, kind, non_negative); line 10 is "Line 8 minus line 9" and can be below 0.
    ("ca/foreign_business_tax_credit_line_4", FOREIGN_BUSINESS_TAX_CREDIT_LINE_4, True),
    ("ca/foreign_business_tax_credit_line_5", FOREIGN_BUSINESS_TAX_CREDIT_LINE_5, True),
    ("ca/foreign_business_tax_credit_line_7", FOREIGN_BUSINESS_TAX_CREDIT_LINE_7, True),
    ("ca/foreign_business_tax_credit_line_8", FOREIGN_BUSINESS_TAX_CREDIT_LINE_8, True),
    ("ca/foreign_business_tax_credit_line_10", FOREIGN_BUSINESS_TAX_CREDIT_LINE_10, False),
    ("ca/federal_business_foreign_tax_credit", FEDERAL_BUSINESS_FOREIGN_TAX_CREDIT, True),
    (
        "ca/federal_foreign_tax_credit_before_limit",
        FEDERAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT,
        True,
    ),
]


@pytest.mark.parametrize(("identifier", "kind", "non_negative"), BUSINESS_LINES)
def test_the_business_line_kinds_are_registered_decimals(
    registry: ArtifactRegistry, identifier: str, kind: ArtifactKind[Any], non_negative: bool
) -> None:
    # T2209 line 4 (43400), 5, 7 "Add lines 5 and 6.", 8, 10 "Line 8 minus line 9", 11 "Federal
    # business foreign tax credit" and 13 "Add lines 11 and 12." "Federal foreign tax credit".
    assert kind.identifier == identifier
    assert kind.value_type is Decimal
    assert kind.non_negative is non_negative
    assert registry.kind(identifier) is kind


def test_the_business_line_10_may_be_negative_and_the_others_may_not() -> None:
    Artifact(FOREIGN_BUSINESS_TAX_CREDIT_LINE_10, Decimal("-1"))
    for _identifier, kind, non_negative in BUSINESS_LINES:
        if non_negative:
            with pytest.raises(NegativeArtifactError):
                Artifact(kind, Decimal("-1"))


# --- Form T2038(IND): the apprentices of the apprenticeship job creation tax credit ---------------


def test_the_itc_apprentice_salary_and_wages_is_a_non_negative_decimal(
    registry: ArtifactRegistry,
) -> None:
    # T2038(IND) Part B Table 1 column 3 "The lesser of eligible salary and wages** payable in the
    # year or $20,000.": each apprentice's eligible salary and wages, net of any assistance.

    assert ITC_APPRENTICE_SALARY_AND_WAGES.identifier == "ca/itc_apprentice_salary_and_wages"
    assert ITC_APPRENTICE_SALARY_AND_WAGES.value_type is Decimal
    assert ITC_APPRENTICE_SALARY_AND_WAGES.non_negative is True
    assert registry.kind("ca/itc_apprentice_salary_and_wages") is ITC_APPRENTICE_SALARY_AND_WAGES


def test_the_itc_apprentices_are_a_record_list_of_their_salary_and_wages(
    registry: ArtifactRegistry,
) -> None:
    # T2038(IND) Part B Table 1: one row for each apprentice, its own record list.

    assert isinstance(ITC_APPRENTICES, RecordListKind)
    assert ITC_APPRENTICES.identifier == "ca/itc_apprentices"
    assert ITC_APPRENTICES.value_type is RecordList
    assert ITC_APPRENTICES.fields == (ITC_APPRENTICE_SALARY_AND_WAGES,)
    assert registry.get("ca/itc_apprentices") is ITC_APPRENTICES


def test_the_itc_apprentices_may_be_empty() -> None:

    assert RecordList(ITC_APPRENTICES.fields, []).records == ()


def test_an_itc_apprentice_refuses_negative_salary_and_wages() -> None:

    with pytest.raises(NegativeArtifactError, match="item 1"):
        RecordList(ITC_APPRENTICES.fields, [{ITC_APPRENTICE_SALARY_AND_WAGES: Decimal("-1")}])


def test_an_itc_apprentice_missing_salary_and_wages_is_refused_naming_the_row() -> None:

    with pytest.raises(InvalidRecordError, match="item 1.*itc_apprentice_salary_and_wages"):
        RecordList(ITC_APPRENTICES.fields, [{}])


def test_the_itc_apprenticeship_wages_total_is_a_non_negative_decimal(
    registry: ArtifactRegistry,
) -> None:
    # T2038(IND) Part B Table 1: the total of column 3 is the amount the credit's 10% is taken of.

    assert ITC_APPRENTICESHIP_WAGES_TOTAL.identifier == "ca/itc_apprenticeship_wages_total"
    assert ITC_APPRENTICESHIP_WAGES_TOTAL.value_type is Decimal
    assert ITC_APPRENTICESHIP_WAGES_TOTAL.non_negative is True
    assert registry.kind("ca/itc_apprenticeship_wages_total") is ITC_APPRENTICESHIP_WAGES_TOTAL


# --- the federal logging tax credit, T1 line 133, and line 134 (40600) ----------------------------

# The caller's figures, one record per province with a logging operation: the logging tax paid to
# the province and the net logging income in it (5000-G, "Federal logging tax credit").
LOGGING_FIELDS = (LOGGING_TAX_PAID, NET_LOGGING_INCOME)

# The computed figures: the sum over the provinces, the base and the cap of line 133, line 133 and
# line 134 (40600).
LOGGING_COMPUTED = (
    PROVINCES_LOGGING_TAX_CREDIT,
    LOGGING_CREDIT_BASE,
    LOGGING_CREDIT_CAP,
    FEDERAL_LOGGING_TAX_CREDIT,
    FEDERAL_TAX,
)


def test_the_logging_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    for kind in (LOGGING_OPERATIONS, *LOGGING_FIELDS, *LOGGING_COMPUTED):
        assert registry.get(kind.identifier) is kind, kind.identifier


def test_the_logging_operations_list_one_record_per_province_of_two_fields(
    registry: ArtifactRegistry,
) -> None:
    assert isinstance(LOGGING_OPERATIONS, RecordListKind)
    assert LOGGING_OPERATIONS.identifier == "ca/logging_operations"
    assert LOGGING_OPERATIONS.fields == LOGGING_FIELDS
    assert registry.get("ca/logging_operations") is LOGGING_OPERATIONS


def test_the_logging_operations_may_be_empty() -> None:
    assert RecordList(LOGGING_OPERATIONS.fields, []).records == ()


def test_a_logging_operation_refuses_negative_tax_paid_or_income_naming_the_row() -> None:
    with pytest.raises(NegativeArtifactError, match="item 1"):
        RecordList(
            LOGGING_OPERATIONS.fields,
            [{LOGGING_TAX_PAID: Decimal("-1"), NET_LOGGING_INCOME: Decimal("1")}],
        )

    with pytest.raises(NegativeArtifactError, match="item 2"):
        RecordList(
            LOGGING_OPERATIONS.fields,
            [
                {LOGGING_TAX_PAID: Decimal("1"), NET_LOGGING_INCOME: Decimal("1")},
                {LOGGING_TAX_PAID: Decimal("1"), NET_LOGGING_INCOME: Decimal("-1")},
            ],
        )


def test_a_logging_operation_missing_a_field_is_refused_naming_the_row() -> None:
    with pytest.raises(InvalidRecordError, match="item 1.*net_logging_income"):
        RecordList(LOGGING_OPERATIONS.fields, [{LOGGING_TAX_PAID: Decimal("300")}])


def test_the_logging_fields_are_non_negative_decimals(registry: ArtifactRegistry) -> None:
    # The tax paid to a province and the net logging income in it are amounts, never below zero.
    for kind in LOGGING_FIELDS:
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier


def test_the_logging_computed_figures_are_non_negative_decimals() -> None:
    # The sum, the base and the cap are sums or products of amounts, and line 133 is a lesser
    # amount; line 134 is "if negative, enter 0", so it is never below zero either.
    for kind in LOGGING_COMPUTED:
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier


def test_line_134_is_named_federal_tax_and_is_the_federal_tax_of_line_40600() -> None:
    # 5006-R Ontario edition: "Line 134 and line 40600: Line 132 minus line 133 (if negative, enter
    # "0") Federal tax =". The kind is `federal_tax`, not a name that already exists.
    assert FEDERAL_TAX.identifier == "ca/federal_tax"


def test_line_133_is_the_federal_logging_tax_credit_kind() -> None:
    assert FEDERAL_LOGGING_TAX_CREDIT.identifier == "ca/federal_logging_tax_credit"


def test_the_amt_logging_stand_in_is_no_longer_a_kind(registry: ArtifactRegistry) -> None:
    # Form T691 Part 1 line 100 is "Federal logging tax credit (line 133 of your return)": the
    # alternative minimum tax reads the computed line 133, so the caller's stand-in is removed.
    assert "ca/amt_federal_logging_tax_credit" not in registry.identifiers()
