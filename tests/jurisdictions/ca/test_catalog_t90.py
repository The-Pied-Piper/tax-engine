"""Registered kinds of Form T90 "Income Exempt from Tax under the Indian Act", in the federal
catalog family `t90` (`tax_engine/jurisdictions/ca/catalog/t90.py`).

The form `ca/t90` runs once. Its sixteen starting amounts are the printed lines 1 to 19 (line 10019
is the unnumbered line "EI maternity and parental benefits and PPIP benefits included on line 9"),
and the steps compute lines 4, 14, 16, 18 and 20 and check line 10019. The exports are line 4,
the checked line 10019 and line 20. The kinds of lines 14, 16 and 18 are registered beside them.
"""

from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path

import tax_engine.jurisdictions.ca.catalog
from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.jurisdictions.ca.catalog import (
    T90_COVID_19_PAYMENTS,
    T90_CPP_QPP_BENEFITS,
    T90_DEDUCTIONS_RELATING_TO_EXEMPT_INCOME,
    T90_EI_MATERNITY_PARENTAL_PPIP_BENEFITS,
    T90_EI_MATERNITY_PARENTAL_PPIP_BENEFITS_CHECKED,
    T90_EI_PPIP_AND_OTHER_BENEFITS,
    T90_EXEMPT_WORKING_INCOME,
    T90_INTEREST_DIVIDENDS_INVESTMENT_INCOME,
    T90_LINE_14,
    T90_LINE_16,
    T90_NET_EXEMPT_INCOME,
    T90_NET_RENTAL_INCOME,
    T90_NET_RENTAL_LOSSES,
    T90_NET_SELF_EMPLOYMENT_INCOME,
    T90_NET_SELF_EMPLOYMENT_LOSSES,
    T90_OTHER_EMPLOYMENT_INCOME,
    T90_OTHER_EXEMPT_INCOME,
    T90_OTHER_PENSIONS_AND_SUPERANNUATION,
    T90_RRSP_RRIF_PENSION_TRANSFER_INCOME,
    T90_SOCIAL_ASSISTANCE_PAYMENTS,
    T90_T4_BOX_71_EMPLOYMENT_INCOME,
    T90_TOTAL_EXEMPT_INCOME,
)
from tests.jurisdictions.ca.catalog_snapshot import COUNTS, RECORD_LISTS, REGISTERED, SIGNED

# The sixteen starting amounts: the printed lines 1, 2, 3, 5 to 13, 10019, 15, 17 and 19, each a
# non-negative amount as the filer enters it.
INPUTS = (
    T90_T4_BOX_71_EMPLOYMENT_INCOME,
    T90_OTHER_EMPLOYMENT_INCOME,
    T90_NET_SELF_EMPLOYMENT_INCOME,
    T90_CPP_QPP_BENEFITS,
    T90_RRSP_RRIF_PENSION_TRANSFER_INCOME,
    T90_COVID_19_PAYMENTS,
    T90_OTHER_PENSIONS_AND_SUPERANNUATION,
    T90_EI_PPIP_AND_OTHER_BENEFITS,
    T90_EI_MATERNITY_PARENTAL_PPIP_BENEFITS,
    T90_INTEREST_DIVIDENDS_INVESTMENT_INCOME,
    T90_NET_RENTAL_INCOME,
    T90_SOCIAL_ASSISTANCE_PAYMENTS,
    T90_OTHER_EXEMPT_INCOME,
    T90_NET_RENTAL_LOSSES,
    T90_NET_SELF_EMPLOYMENT_LOSSES,
    T90_DEDUCTIONS_RELATING_TO_EXEMPT_INCOME,
)
# The computed amounts: the exports, and the lines 14 and 16 and the total of line 18 registered
# beside them. Line 16, line 18 and line 20 are signed ("if negative, show in brackets", or no
# floor).
COMPUTED = (
    T90_EXEMPT_WORKING_INCOME,
    T90_EI_MATERNITY_PARENTAL_PPIP_BENEFITS_CHECKED,
    T90_LINE_14,
    T90_LINE_16,
    T90_TOTAL_EXEMPT_INCOME,
    T90_NET_EXEMPT_INCOME,
)
SIGNED_KINDS = (T90_LINE_16, T90_TOTAL_EXEMPT_INCOME, T90_NET_EXEMPT_INCOME)
ALL_KINDS = (*INPUTS, *COMPUTED)


def squashed(text: str) -> str:
    return " ".join(text.split())


def docstring_of(identifier: str) -> str:
    """The string right after the declaration of the kind `identifier` in a catalog module (its
    name is a constant of the declaration's call, which may take the catalog first)."""
    folder = Path(tax_engine.jurisdictions.ca.catalog.__file__).parent
    for path in sorted(folder.glob("*.py")):
        body = ast.parse(path.read_text()).body
        for statement, following in zip(body, body[1:], strict=False):
            if not (isinstance(statement, ast.Assign) and isinstance(statement.value, ast.Call)):
                continue
            constants = [
                each.value for each in statement.value.args if isinstance(each, ast.Constant)
            ]
            if not (
                identifier.rpartition("/")[2] in constants
                and isinstance(following, ast.Expr)
                and isinstance(following.value, ast.Constant)
            ):
                continue
            return str(following.value.value)
    raise AssertionError(f"no declaration of {identifier!r} followed by a docstring")


def test_the_t90_kinds_are_registered_under_their_identifiers(registry: ArtifactRegistry) -> None:
    for kind in ALL_KINDS:
        assert registry.get(kind.identifier) is kind, kind.identifier


def test_the_t90_kinds_are_in_the_snapshot() -> None:
    assert {kind.identifier for kind in ALL_KINDS} <= REGISTERED


def test_the_three_exports_of_the_form_are_registered_money() -> None:
    assert T90_EXEMPT_WORKING_INCOME.identifier == "ca/t90_exempt_working_income"
    assert T90_NET_EXEMPT_INCOME.identifier == "ca/t90_net_exempt_income"
    assert (
        T90_EI_MATERNITY_PARENTAL_PPIP_BENEFITS_CHECKED.identifier
        == "ca/t90_ei_maternity_parental_ppip_benefits_checked"
    )
    for kind in (
        T90_EXEMPT_WORKING_INCOME,
        T90_NET_EXEMPT_INCOME,
        T90_EI_MATERNITY_PARENTAL_PPIP_BENEFITS_CHECKED,
    ):
        assert kind.value_type is Decimal, kind.identifier


def test_the_starting_amounts_are_non_negative_decimals() -> None:
    for kind in INPUTS:
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier


def test_the_starting_amounts_are_the_registered_inputs_of_the_form() -> None:
    assert {kind.identifier for kind in INPUTS} == {
        "ca/t90_t4_box_71_employment_income",
        "ca/t90_other_employment_income",
        "ca/t90_net_self_employment_income",
        "ca/t90_cpp_qpp_benefits",
        "ca/t90_rrsp_rrif_pension_transfer_income",
        "ca/t90_covid_19_payments",
        "ca/t90_other_pensions_and_superannuation",
        "ca/t90_ei_ppip_and_other_benefits",
        "ca/t90_ei_maternity_parental_ppip_benefits",
        "ca/t90_interest_dividends_investment_income",
        "ca/t90_net_rental_income",
        "ca/t90_social_assistance_payments",
        "ca/t90_other_exempt_income",
        "ca/t90_net_rental_losses",
        "ca/t90_net_self_employment_losses",
        "ca/t90_deductions_relating_to_exempt_income",
    }


def test_the_signed_lines_of_the_form_are_signed_and_the_rest_are_not() -> None:
    for kind in SIGNED_KINDS:
        assert kind.non_negative is False, kind.identifier
        assert kind.identifier in SIGNED, kind.identifier
    for kind in (T90_EXEMPT_WORKING_INCOME, T90_LINE_14, *INPUTS):
        assert kind.non_negative is True, kind.identifier
        assert kind.identifier not in SIGNED, kind.identifier


def test_the_t90_kinds_are_not_counts_or_record_lists() -> None:
    for kind in ALL_KINDS:
        assert kind.identifier not in COUNTS | RECORD_LISTS, kind.identifier


def test_each_t90_kind_has_a_docstring_that_names_the_form() -> None:
    for kind in ALL_KINDS:
        assert "T90" in squashed(docstring_of(kind.identifier)), kind.identifier


def test_line_1_docstring_quotes_the_t4_box_of_the_form() -> None:
    text = squashed(docstring_of(T90_T4_BOX_71_EMPLOYMENT_INCOME.identifier))

    assert "Employment income (box 71 of your T4 slip(s))" in text


def test_line_10019_docstring_quotes_the_line_it_is_included_on() -> None:
    text = squashed(docstring_of(T90_EI_MATERNITY_PARENTAL_PPIP_BENEFITS.identifier))

    assert "EI maternity and parental benefits and PPIP benefits included on line 9" in text


def test_line_4_docstring_quotes_the_sum_of_lines_1_to_3() -> None:
    text = squashed(docstring_of(T90_EXEMPT_WORKING_INCOME.identifier))

    assert "Add lines 1 to 3." in text
    assert "Total exempt working income" in text


def test_line_20_docstring_quotes_the_net_exempt_income_and_its_brackets() -> None:
    text = squashed(docstring_of(T90_NET_EXEMPT_INCOME.identifier))

    assert "Line 18 minus line 19 (if negative, show in brackets)" in text
    assert "Net exempt income 10026" in text


def test_the_lines_that_are_not_exports_are_documented_by_their_printed_lines() -> None:
    assert "Add lines 4 to 13." in squashed(docstring_of(T90_LINE_14.identifier))
    assert "Line 14 minus line 15" in squashed(docstring_of(T90_LINE_16.identifier))
    assert "Total exempt income" in squashed(docstring_of(T90_TOTAL_EXEMPT_INCOME.identifier))


def test_the_other_lines_quote_their_printed_labels() -> None:
    quotes = {
        T90_OTHER_EMPLOYMENT_INCOME.identifier: (
            "Other employment income such as tips, net research grants, and income maintenance "
            "insurance plans"
        ),
        T90_NET_SELF_EMPLOYMENT_INCOME.identifier: "Net self-employment income (excluding losses)",
        T90_CPP_QPP_BENEFITS.identifier: (
            "Canada pension plan (CPP) or Quebec pension plan (QPP) benefits"
        ),
        T90_COVID_19_PAYMENTS.identifier: (
            "Federal, provincial, or territorial government COVID-19 payments received in the year"
        ),
        T90_OTHER_PENSIONS_AND_SUPERANNUATION.identifier: "Other pensions and superannuation",
        T90_EI_PPIP_AND_OTHER_BENEFITS.identifier: (
            "Employment Insurance (EI), Provincial parental insurance plan (PPIP), and other "
            "benefits"
        ),
        T90_INTEREST_DIVIDENDS_INVESTMENT_INCOME.identifier: (
            "Interest, dividends, and other investment income"
        ),
        T90_NET_RENTAL_INCOME.identifier: "Net rental income (excluding losses)",
        T90_SOCIAL_ASSISTANCE_PAYMENTS.identifier: (
            "Social assistance payments received from a First Nation or band council"
        ),
        T90_OTHER_EXEMPT_INCOME.identifier: "Other sources of exempt income",
        T90_NET_RENTAL_LOSSES.identifier: "Net rental losses",
        T90_NET_SELF_EMPLOYMENT_LOSSES.identifier: "Net self-employment losses",
        T90_DEDUCTIONS_RELATING_TO_EXEMPT_INCOME.identifier: (
            "Deductions relating to exempt income above"
        ),
    }
    for identifier, quote in quotes.items():
        assert quote in squashed(docstring_of(identifier)), identifier
