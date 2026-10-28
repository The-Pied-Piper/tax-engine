"""The 2025 Ontario provincial foreign tax credit datasets (Form T2036, ON428 lines 70 to 83).

2025 Form T2036, Provincial or Territorial Foreign Tax Credit: line 4 "Net foreign non-business
income (2)" "× Provincial or territorial tax otherwise payable (4)" over "Net income (3)"; line 5
"Enter whichever amount is less: line 3 or line 4." Note (4): "If you were a resident of Ontario,
calculate this amount by entering "0" on lines 70 and 72 of Form ON428 and continue the
calculation. The result from line 81 is your provincial or territorial tax otherwise payable."
Line 4 multiplies and divides, so the credit has one `rounding_only` dataset,
`ca-on/provincial_foreign_tax_credit_rounding`: line 4 is a dollars-and-cents box, so the quotient
rounds half-up to the cent, the owner's decision, as the form states no rounding rule. Lines 1, 2,
3 and 5 take amounts already in cents. The form is a PDF with no published .txt, so the dataset
cites the PDF.

With "0" on line 72 the ON428 condition "There is an amount on line 72" for "Enter "0" on line 80"
cannot apply, so the tax otherwise payable has the conditions dataset
`ca-on/tax_reduction_conditions_without_line_72`: the same five other conditions in the form's
order and wording, "You were not a resident of Canada at the beginning of the year", "You were not
a resident of Ontario on December 31, 2025", "You were bankrupt at any time in 2025", "Your return
is filed for you by a trustee in bankruptcy" and "You are choosing not to claim an Ontario tax
reduction", reading the same five counts as `ca-on/tax_reduction_conditions` and no amount. The
count is 0 when any applies and 1 when none does, so nothing is rounded.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.parameters.amount import AMOUNT
from tax_calculator.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_calculator.domain.parameters.rate import RATE
from tax_calculator.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.registry import Namespace
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_calculator.jurisdictions.ca.catalog import (
    FOREIGN_BUSINESS_TAX_PAID,
    FOREIGN_BUSINESS_UNUSED_TAX_CREDITS,
    FOREIGN_NON_BUSINESS_TAX_PAID,
    FOREIGN_SURTAX_OUTSIDE_CANADA,
    FOREIGN_TAX_CREDIT_SHEET_LINE_3,
    FOREIGN_TAX_CREDIT_SHEETS,
    NET_FOREIGN_BUSINESS_INCOME,
    NET_FOREIGN_NON_BUSINESS_INCOME,
)
from tax_calculator.jurisdictions.ca_on.capabilities.provincial_foreign_tax_credit import (
    ProvincialForeignTaxCredit,
)

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
ROUNDING = "ca-on/provincial_foreign_tax_credit_rounding"
THRESHOLD = "ca-on/provincial_foreign_tax_credit_separate_sheet_threshold"
RATE_FAMILY = "ca/amt_special_foreign_tax_credit_rate"
CONDITIONS_WITHOUT_LINE_72 = "ca-on/tax_reduction_conditions_without_line_72"
LINE_80_CONDITIONS = "ca-on/tax_reduction_conditions"
T2036_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2036/t2036-25e.pdf"
ON428_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt"

# Made up for this test and not registered.
NET_INCOME = ArtifactKind("ex/net_income", Decimal)
PROVINCIAL_TAX = ArtifactKind("ex/provincial_tax", Decimal, non_negative=True)
CREDIT = ArtifactKind("ex/provincial_credit", Decimal, non_negative=True)
MINIMUM_TAX = ArtifactKind("ex/minimum_tax_applies", int, non_negative=True)
LINE_7 = ArtifactKind("ex/non_business_tax_two_thirds", Decimal, non_negative=True)
LINE_8 = ArtifactKind("ex/business_tax_paid", Decimal, non_negative=True)
LINE_11 = ArtifactKind("ex/special_foreign_tax_credit", Decimal, non_negative=True)
NOT_RESIDENT_CANADA = ArtifactKind("ex/not_resident_of_canada", int)
NOT_RESIDENT_ONTARIO = ArtifactKind("ex/not_resident_of_ontario", int)
BANKRUPT = ArtifactKind("ex/bankrupt", int)
TRUSTEE = ArtifactKind("ex/filed_by_trustee", int)
NOT_CLAIMING = ArtifactKind("ex/not_claiming", int)
GATE = ArtifactKind("ex/gate", int)
FIVE_COUNTS = (NOT_RESIDENT_CANADA, NOT_RESIDENT_ONTARIO, BANKRUPT, TRUSTEE, NOT_CLAIMING)


def squashed(text: str) -> str:
    """`text` with the comment markers and line breaks gone and runs of blanks made one."""
    return re.sub(r"\s+", " ", text.replace("#", " ")).strip()


def dataset_header(family: str) -> str:
    """The comment lines above the dataset's first key, squashed."""
    root = tax_calculator.registrations.JURISDICTIONS.roots()[Namespace("ca-on")]
    name = family.removeprefix("ca-on/")
    lines = (root / "parameters" / name / "2025.yaml").read_text().splitlines()
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return squashed("\n".join(lines[:first_key]))


# --- the rounding dataset ------------------------------------------------------------------------


def test_2025_rounding_is_half_up_to_the_cent_with_no_other_figure() -> None:
    data = SOURCE.get(ROUNDING, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    # Line 4, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_rounding_cites_only_the_t2036_pdf() -> None:
    assert SOURCE.get(ROUNDING, 2025, ROUNDING_ONLY).sources == (T2036_PDF,)


def test_the_rounding_header_quotes_t2036_as_the_form_prints_it() -> None:
    header = dataset_header(ROUNDING)

    for quoted in (
        "Net foreign non-business income (2)",
        "Provincial or territorial tax otherwise payable (4)",
        "Net income (3)",
        "Enter whichever amount is less: line 3 or line 4.",
        "Provincial or territorial foreign tax credit",
    ):
        assert quoted in header, quoted


def test_the_rounding_header_states_the_half_up_cent_rule() -> None:
    header = dataset_header(ROUNDING).lower()

    assert "dollars-and-cents box" in header
    assert "half-up" in header
    assert "owner's decision" in header


def test_the_rounding_dataset_runs_through_the_capability() -> None:
    capability = ProvincialForeignTaxCredit(
        rounding=SOURCE.get(ROUNDING, 2025, ROUNDING_ONLY),
        threshold=SOURCE.get(THRESHOLD, 2025, AMOUNT),
        rate=SOURCE.get(RATE_FAMILY, 2025, RATE),
        minimum_tax_applies=MINIMUM_TAX,
        sheets=FOREIGN_TAX_CREDIT_SHEETS,
        net_income=NET_INCOME,
        provincial_tax=PROVINCIAL_TAX,
        non_business_tax_paid=LINE_7,
        business_tax_paid=LINE_8,
        special_foreign_tax_credit=LINE_11,
        total=CREDIT,
    )
    records: list[dict[ArtifactKind[Any], object]] = [
        {
            FOREIGN_NON_BUSINESS_TAX_PAID: D("50"),
            NET_FOREIGN_NON_BUSINESS_INCOME: D("10"),
            FOREIGN_TAX_CREDIT_SHEET_LINE_3: D("0"),
            FOREIGN_BUSINESS_TAX_PAID: D(0),
            FOREIGN_BUSINESS_UNUSED_TAX_CREDITS: D(0),
            NET_FOREIGN_BUSINESS_INCOME: D(0),
            FOREIGN_SURTAX_OUTSIDE_CANADA: D(0),
        },
        {
            FOREIGN_NON_BUSINESS_TAX_PAID: D("50"),
            NET_FOREIGN_NON_BUSINESS_INCOME: D("20"),
            FOREIGN_TAX_CREDIT_SHEET_LINE_3: D("0"),
            FOREIGN_BUSINESS_TAX_PAID: D(0),
            FOREIGN_BUSINESS_UNUSED_TAX_CREDITS: D(0),
            NET_FOREIGN_BUSINESS_INCOME: D(0),
            FOREIGN_SURTAX_OUTSIDE_CANADA: D(0),
        },
    ]

    (output,) = capability.compute(
        (
            Artifact(
                FOREIGN_TAX_CREDIT_SHEETS, RecordList(FOREIGN_TAX_CREDIT_SHEETS.fields, records)
            ),
            Artifact(NET_INCOME, D("300")),
            Artifact(PROVINCIAL_TAX, D("100")),
            Artifact(MINIMUM_TAX, 0),
            Artifact(LINE_7, D("0")),
            Artifact(LINE_8, D("0")),
            Artifact(LINE_11, D("0")),
        )
    ).outputs

    # 10 x 100 / 300 = 3.33 and 20 x 100 / 300 = 6.67, each rounded half-up to the cent.
    assert output.value == D("10.00")


def test_2025_sheets_with_non_business_tax_of_100_in_all_are_worked_once_on_the_totals() -> None:
    capability = ProvincialForeignTaxCredit(
        rounding=SOURCE.get(ROUNDING, 2025, ROUNDING_ONLY),
        threshold=SOURCE.get(THRESHOLD, 2025, AMOUNT),
        rate=SOURCE.get(RATE_FAMILY, 2025, RATE),
        minimum_tax_applies=MINIMUM_TAX,
        sheets=FOREIGN_TAX_CREDIT_SHEETS,
        net_income=NET_INCOME,
        provincial_tax=PROVINCIAL_TAX,
        non_business_tax_paid=LINE_7,
        business_tax_paid=LINE_8,
        special_foreign_tax_credit=LINE_11,
        total=CREDIT,
    )
    # Each sheet's Form T2209 line 3 is its federal credit: 0 for sheet 1 and 50 (all its tax) for
    # sheet 2.
    records: list[dict[ArtifactKind[Any], object]] = [
        {
            FOREIGN_NON_BUSINESS_TAX_PAID: D("50"),
            NET_FOREIGN_NON_BUSINESS_INCOME: D("10"),
            FOREIGN_TAX_CREDIT_SHEET_LINE_3: D("0"),
            FOREIGN_BUSINESS_TAX_PAID: D(0),
            FOREIGN_BUSINESS_UNUSED_TAX_CREDITS: D(0),
            NET_FOREIGN_BUSINESS_INCOME: D(0),
            FOREIGN_SURTAX_OUTSIDE_CANADA: D(0),
        },
        {
            FOREIGN_NON_BUSINESS_TAX_PAID: D("50"),
            NET_FOREIGN_NON_BUSINESS_INCOME: D("20"),
            FOREIGN_TAX_CREDIT_SHEET_LINE_3: D("50"),
            FOREIGN_BUSINESS_TAX_PAID: D(0),
            FOREIGN_BUSINESS_UNUSED_TAX_CREDITS: D(0),
            NET_FOREIGN_BUSINESS_INCOME: D(0),
            FOREIGN_SURTAX_OUTSIDE_CANADA: D(0),
        },
    ]

    (output,) = capability.compute(
        (
            Artifact(
                FOREIGN_TAX_CREDIT_SHEETS, RecordList(FOREIGN_TAX_CREDIT_SHEETS.fields, records)
            ),
            Artifact(NET_INCOME, D("300")),
            Artifact(PROVINCIAL_TAX, D("100")),
            Artifact(MINIMUM_TAX, 0),
            Artifact(LINE_7, D("0")),
            Artifact(LINE_8, D("0")),
            Artifact(LINE_11, D("0")),
        )
    ).outputs

    # Total 100 is not more than 200, so one calculation on the totals: line 1 100; line 2 = 0 + 50
    # = 50; line 3 = 50; income 10 + 20 = 30; line 4 = 30 x 100 / 300 = 10.00; line 5 = lesser(50,
    # 10.00) = 10.00. Sheet by sheet it would be 10 x 100 / 300 = 3.33 for sheet 1 (line 5 3.33)
    # and nil for sheet 2 (line 3 0), a total of 3.33.
    assert output.value == D("10.00")


# --- the conditions without line 72 -------------------------------------------------------------


def a_count_applies(text: str, position: int) -> Condition:
    return Condition(
        text, (ConditionPart((ConditionTest("count", position, "equal_to", D(1), None),)),)
    )


def conditions_dataset() -> Any:
    return SOURCE.get(CONDITIONS_WITHOUT_LINE_72, 2025, CONDITIONS)


def test_2025_the_conditions_are_the_five_other_than_line_72_in_the_forms_order() -> None:
    data = conditions_dataset()

    assert data.values == ConditionList(
        0,
        (
            a_count_applies("You were not a resident of Canada at the beginning of the year", 1),
            a_count_applies("You were not a resident of Ontario on December 31, 2025", 2),
            a_count_applies("You were bankrupt at any time in 2025", 3),
            a_count_applies("Your return is filed for you by a trustee in bankruptcy", 4),
            a_count_applies("You are choosing not to claim an Ontario tax reduction", 5),
        ),
    )
    assert data.values.count_when_none_applies == 1
    # A count, not the amount of a line: nothing is rounded.
    assert data.rounding == NO_ROUNDING


def test_2025_the_conditions_read_the_same_five_counts_and_no_amount() -> None:
    values = conditions_dataset().values
    full = SOURCE.get(LINE_80_CONDITIONS, 2025, CONDITIONS).values

    assert values.count_positions_read == full.count_positions_read == frozenset({1, 2, 3, 4, 5})
    assert values.amount_positions_read == frozenset()


def test_2025_the_conditions_are_the_line_80_conditions_less_the_line_72_one() -> None:
    full = SOURCE.get(LINE_80_CONDITIONS, 2025, CONDITIONS).values
    without = conditions_dataset().values
    line_72 = "There is an amount on line 72"

    assert [c.text for c in full.conditions if c.text != line_72] == [
        c.text for c in without.conditions
    ]
    assert line_72 not in [c.text for c in without.conditions]


def test_2025_the_conditions_cite_only_the_on428_text() -> None:
    assert conditions_dataset().sources == (ON428_TEXT,)


def test_the_conditions_header_quotes_on428_and_t2036_note_4() -> None:
    header = dataset_header(CONDITIONS_WITHOUT_LINE_72)

    for quoted in (
        'Enter "0" on line 80 if any of the following applies to you:',
        "If none of the above applies to you, complete lines 74 to 80 to calculate your Ontario "
        "tax reduction.",
        'calculate this amount by entering "0" on lines 70 and 72 of Form ON428 and continue the '
        "calculation. The result from line 81 is your provincial or territorial tax otherwise "
        "payable.",
        "There is an amount on line 72",
    ):
        assert quoted in header, quoted


def gate(flags: tuple[int, int, int, int, int] = (0, 0, 0, 0, 0)) -> int:
    capability = CountByConditions(conditions_dataset(), FIVE_COUNTS, (), GATE)
    inputs: list[Artifact[Any]] = [
        Artifact(kind, flag) for kind, flag in zip(FIVE_COUNTS, flags, strict=True)
    ]

    (output,) = capability.compute(tuple(inputs)).outputs

    assert isinstance(output.value, int)
    return output.value


def test_no_condition_applying_gives_1() -> None:
    assert gate() == 1


@pytest.mark.parametrize(
    "flags",
    [
        (1, 0, 0, 0, 0),
        (0, 1, 0, 0, 0),
        (0, 0, 1, 0, 0),
        (0, 0, 0, 1, 0),
        (0, 0, 0, 0, 1),
        (1, 1, 1, 1, 1),
    ],
)
def test_any_one_of_the_five_counts_gives_0(flags: tuple[int, int, int, int, int]) -> None:
    # Bankrupt at any time in 2025 is the third printed condition left, and the third count.
    assert gate(flags) == 0
