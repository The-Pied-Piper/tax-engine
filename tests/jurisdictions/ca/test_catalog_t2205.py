"""Registered kinds of Form T2205 "Amounts from a Spousal or Common-law Partner RRSP, RRIF, or SPP
to Include in Income", in the federal catalog family `t2205`
(`tax_engine/jurisdictions/ca/catalog/t2205.py`).

The form `ca/t2205` runs once. Its twelve starting amounts are the printed lines 1, 2, 4, 6, 7, 12,
13, 14, 17, 18 and 20 and the part of line 11 that relates to SPP withdrawals; the steps compute
the other printed lines. The return reads the exports (the RRSP part of line 11, the SPP part of
line 11 and line 22) through the amounts it reports on T1 lines 12900, 11500 and 13000.
"""

from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path

import tax_engine.jurisdictions.ca.catalog
from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.jurisdictions.ca.catalog import (
    T2205_LINE_1,
    T2205_LINE_2,
    T2205_LINE_3,
    T2205_LINE_4,
    T2205_LINE_4_CHECKED,
    T2205_LINE_5,
    T2205_LINE_6,
    T2205_LINE_7,
    T2205_LINE_7_CHECKED,
    T2205_LINE_8,
    T2205_LINE_10,
    T2205_LINE_11,
    T2205_LINE_11_RRSP_PART,
    T2205_LINE_11_SPP_PART,
    T2205_LINE_11_SPP_PART_CHECKED,
    T2205_LINE_12,
    T2205_LINE_13,
    T2205_LINE_14,
    T2205_LINE_14_CHECKED,
    T2205_LINE_15,
    T2205_LINE_16,
    T2205_LINE_17,
    T2205_LINE_17_USED,
    T2205_LINE_18,
    T2205_LINE_18_CHECKED,
    T2205_LINE_18_FROM_PART_1,
    T2205_LINE_18_USED,
    T2205_LINE_19,
    T2205_LINE_20,
    T2205_LINE_21,
    T2205_LINE_22,
    T2205_LINE_22_ON_LINE_11500,
    T2205_LINE_22_ON_LINE_13000,
    T2205_LINE_22_TOTAL,
    T2205_ON_LINE_11500,
    T2205_ON_LINE_12900,
    T2205_ON_LINE_13000,
    T2205_SPP_PART_ON_LINE_11500,
    T2205_SPP_PART_ON_LINE_13000,
    T2205_SPP_PART_TOTAL,
)
from tests.jurisdictions.ca.catalog_snapshot import COUNTS, RECORD_LISTS, REGISTERED, SIGNED

# The twelve starting amounts, each a non-negative amount as the filer enters it.
INPUTS = (
    T2205_LINE_1,
    T2205_LINE_2,
    T2205_LINE_4,
    T2205_LINE_6,
    T2205_LINE_7,
    T2205_LINE_11_SPP_PART,
    T2205_LINE_12,
    T2205_LINE_13,
    T2205_LINE_14,
    T2205_LINE_17,
    T2205_LINE_18,
    T2205_LINE_20,
)
# The amounts the form computes that cannot be negative: the printed lines are differences of a
# whole and a part that is refused above it, or the lesser of two such amounts.
COMPUTED = (
    T2205_LINE_3,
    T2205_LINE_4_CHECKED,
    T2205_LINE_5,
    T2205_LINE_7_CHECKED,
    T2205_LINE_8,
    T2205_LINE_10,
    T2205_LINE_11,
    T2205_LINE_11_SPP_PART_CHECKED,
    T2205_LINE_11_RRSP_PART,
    T2205_LINE_14_CHECKED,
    T2205_LINE_15,
    T2205_LINE_16,
    T2205_LINE_17_USED,
    T2205_LINE_18_FROM_PART_1,
    T2205_LINE_18_USED,
    T2205_LINE_18_CHECKED,
    T2205_LINE_19,
    T2205_LINE_21,
)
# Line 22 prints no floor, so it and the amounts routed from it are signed.
SIGNED_KINDS = (
    T2205_LINE_22,
    T2205_LINE_22_TOTAL,
    T2205_LINE_22_ON_LINE_11500,
    T2205_LINE_22_ON_LINE_13000,
    T2205_ON_LINE_11500,
    T2205_ON_LINE_13000,
)
# The amounts the return holds from the exports of the form, by T1 line.
RETURN_UNSIGNED = (
    T2205_ON_LINE_12900,
    T2205_SPP_PART_TOTAL,
    T2205_SPP_PART_ON_LINE_11500,
    T2205_SPP_PART_ON_LINE_13000,
)
ALL_KINDS = (*INPUTS, *COMPUTED, *SIGNED_KINDS, *RETURN_UNSIGNED)


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


def test_the_t2205_kinds_are_registered_under_their_identifiers(registry: ArtifactRegistry) -> None:
    for kind in ALL_KINDS:
        assert registry.get(kind.identifier) is kind, kind.identifier


def test_the_t2205_kinds_are_in_the_snapshot() -> None:
    assert {kind.identifier for kind in ALL_KINDS} <= REGISTERED


def test_the_kinds_have_the_identifiers_named_for_the_printed_lines() -> None:
    assert [kind.identifier for kind in INPUTS] == [
        "ca/t2205_line_1",
        "ca/t2205_line_2",
        "ca/t2205_line_4",
        "ca/t2205_line_6",
        "ca/t2205_line_7",
        "ca/t2205_line_11_spp_part",
        "ca/t2205_line_12",
        "ca/t2205_line_13",
        "ca/t2205_line_14",
        "ca/t2205_line_17",
        "ca/t2205_line_18",
        "ca/t2205_line_20",
    ]
    assert T2205_LINE_11_RRSP_PART.identifier == "ca/t2205_line_11_rrsp_part"
    assert T2205_LINE_11_SPP_PART_CHECKED.identifier == "ca/t2205_line_11_spp_part_checked"
    assert T2205_LINE_22.identifier == "ca/t2205_line_22"
    assert T2205_ON_LINE_12900.identifier == "ca/t2205_on_line_12900"
    assert T2205_ON_LINE_11500.identifier == "ca/t2205_on_line_11500"
    assert T2205_ON_LINE_13000.identifier == "ca/t2205_on_line_13000"


def test_every_t2205_kind_is_a_decimal() -> None:
    for kind in ALL_KINDS:
        assert kind.value_type is Decimal, kind.identifier


def test_the_starting_amounts_are_non_negative() -> None:
    for kind in INPUTS:
        assert kind.non_negative is True, kind.identifier
        assert kind.identifier not in SIGNED, kind.identifier


def test_the_computed_lines_and_the_unsigned_return_amounts_are_non_negative() -> None:
    for kind in (*COMPUTED, *RETURN_UNSIGNED):
        assert kind.non_negative is True, kind.identifier
        assert kind.identifier not in SIGNED, kind.identifier


def test_line_22_and_the_amounts_routed_from_it_are_signed() -> None:
    for kind in SIGNED_KINDS:
        assert kind.non_negative is False, kind.identifier
        assert kind.identifier in SIGNED, kind.identifier


def test_the_t2205_kinds_are_not_counts_or_record_lists() -> None:
    for kind in ALL_KINDS:
        assert kind.identifier not in COUNTS | RECORD_LISTS, kind.identifier


def test_each_t2205_kind_has_a_docstring_that_names_the_form() -> None:
    for kind in ALL_KINDS:
        assert "T2205" in squashed(docstring_of(kind.identifier)), kind.identifier


def test_the_starting_amounts_quote_their_printed_lines() -> None:
    quotes = {
        T2205_LINE_1: "Add the amounts from boxes 20, 22 and 26 of all your T4RSP slips",
        T2205_LINE_2: (
            "Enter the amount of transfers from your spousal or common-law partner's RRSPs to "
            "your FHSAs"
        ),
        T2205_LINE_4: (
            "Enter the part of the amount from line 1 that was directly transferred to an RRSP, "
            "PRPP, SPP, RRIF"
        ),
        T2205_LINE_6: (
            "Enter the total amount that your spouse or common-law partner contributed to your "
            "RRSPs and SPP in the year you indicated above and the two preceding years."
        ),
        T2205_LINE_7: (
            "Enter the part of the amount from line 6 that your spouse or common-law partner "
            "contributed to your RRSPs and SPP in the two preceding years"
        ),
        T2205_LINE_11_SPP_PART: "If part of this amount relates to withdrawals from an SPP",
        T2205_LINE_12: "Enter the total amounts from box 20 of all your T4RIF slips",
        T2205_LINE_13: "Enter the total amounts from box 24 of the T4RIF slips",
        T2205_LINE_14: (
            "Enter the part of the amount from line 13 that was directly transferred to a RRIF, "
            "an RRSP, a PRPP, an SPP"
        ),
        T2205_LINE_17: (
            "Enter the total amount that your spouse or common-law partner contributed to your "
            "RRSPs and SPP"
        ),
        T2205_LINE_18: (
            "Enter the part of the amount from line 17 that your spouse or common-law partner "
            "contributed to your RRSPs and SPP in the two preceding years"
        ),
        T2205_LINE_20: "Add the amounts from boxes 16 and 20 of all T4RIF slips",
    }
    for kind, quote in quotes.items():
        assert quote in squashed(docstring_of(kind.identifier)), kind.identifier


def test_the_computed_lines_quote_their_printed_lines() -> None:
    quotes = {
        T2205_LINE_3: "Line 1 plus line 2",
        T2205_LINE_5: "Line 3 minus line 4",
        T2205_LINE_8: "Line 6 minus line 7",
        T2205_LINE_10: "Enter the amount from line 5 or line 8, whichever is less.",
        T2205_LINE_11: "Line 9 minus line 10.",
        T2205_LINE_15: "Line 13 minus line 14",
        T2205_LINE_16: "Line 12 plus line 15",
        T2205_LINE_19: "Line 17 minus line 18",
        T2205_LINE_21: "Enter the amount from line 16 or line 19, whichever is less.",
        T2205_LINE_22: "Line 20 minus line 21.",
    }
    for kind, quote in quotes.items():
        assert quote in squashed(docstring_of(kind.identifier)), kind.identifier


def test_the_used_lines_quote_the_part_1_instruction() -> None:
    assert "If you filled in Part 1 above, enter the amount from line 6." in squashed(
        docstring_of(T2205_LINE_17_USED.identifier)
    )
    text = squashed(docstring_of(T2205_LINE_18_FROM_PART_1.identifier))
    assert "If you filled in Part 1 above, add the amounts from line 7 and line 10" in text
    assert "Line 18" in squashed(docstring_of(T2205_LINE_18_USED.identifier))


def test_the_rrsp_income_docstring_says_the_caller_no_longer_types_the_t2205_amount() -> None:
    text = squashed(docstring_of("ca/rrsp_income"))

    assert "T2205" in text
    assert "no longer types" in text


def test_the_routed_amounts_name_the_t1_lines_and_the_age_rule() -> None:
    for kind in (T2205_ON_LINE_11500, T2205_SPP_PART_ON_LINE_11500, T2205_LINE_22_ON_LINE_11500):
        assert "11500" in squashed(docstring_of(kind.identifier)), kind.identifier
    for kind in (T2205_ON_LINE_13000, T2205_SPP_PART_ON_LINE_13000, T2205_LINE_22_ON_LINE_13000):
        assert "13000" in squashed(docstring_of(kind.identifier)), kind.identifier
    assert "12900" in squashed(docstring_of(T2205_ON_LINE_12900.identifier))
    assert "65 or older at the end of the year" in squashed(
        docstring_of(T2205_LINE_22_ON_LINE_11500.identifier)
    )
