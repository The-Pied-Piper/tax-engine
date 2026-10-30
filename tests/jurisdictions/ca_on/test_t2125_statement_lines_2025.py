"""The 2025 T2125 line codes: each statement's code is one count; three conditions flag its line.

Form T2125 (2025), Part 5 line 9946 "Your net income (loss)" is reported on the applicable line of
the return "as indicated below":

- business income on line 13500
- professional income on line 13700
- commission income on line 13900

The form names no codes. The statement's code is a count chosen
by the filer: 1 for business (line 13500), 2 for professional (line 13700) and 3 for commission
(line 13900). Each flag is a conditions dataset that counts 1 when the code is its line's number,
and 0 otherwise, so a code outside 1 to 3 flags no line. Nothing is rounded: a count is never an
amount of a line.

The routed net and gross are the statement's line 9946 and line 8299 times these flags, checked
through the return in test_return_du.py.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.errors import InputOutOfRangeError
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.capabilities.count_refused_by_conditions import (
    CountRefusedByConditions,
)
from tax_engine.jurisdictions.ca.catalog import (
    BUSINESS_INCOME_LINE,
    BUSINESS_LINE_IS_BUSINESS,
    BUSINESS_LINE_IS_COMMISSION,
    BUSINESS_LINE_IS_PROFESSIONAL,
)

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
T2125_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2125/t2125-25e.pdf"

BUSINESS = "ca/t2125_line_is_business"
PROFESSIONAL = "ca/t2125_line_is_professional"
COMMISSION = "ca/t2125_line_is_commission"

LINE_OF_FAMILY = {BUSINESS: 1, PROFESSIONAL: 2, COMMISSION: 3}
FLAG_OF_FAMILY = {
    BUSINESS: BUSINESS_LINE_IS_BUSINESS,
    PROFESSIONAL: BUSINESS_LINE_IS_PROFESSIONAL,
    COMMISSION: BUSINESS_LINE_IS_COMMISSION,
}


def conditions_dataset(family: str) -> Any:
    return SOURCE.get(family, 2025, CONDITIONS)


def flag(family: str, code: int) -> int:
    """The flag `family` gives a statement whose line code is `code`."""
    capability = CountByConditions(
        conditions_dataset(family), (BUSINESS_INCOME_LINE,), (), FLAG_OF_FAMILY[family]
    )
    (output,) = capability.compute((Artifact(BUSINESS_INCOME_LINE, code),)).outputs

    assert isinstance(output.value, int)
    return output.value


# --- the datasets, in the form's wording ---------------------------------------------------------


@pytest.mark.parametrize(
    ("family", "text"),
    [
        (BUSINESS, "business income on line 13500"),
        (PROFESSIONAL, "professional income on line 13700"),
        (COMMISSION, "commission income on line 13900"),
    ],
)
def test_each_flag_is_a_one_condition_count_of_the_code(family: str, text: str) -> None:
    data = conditions_dataset(family)

    assert [condition.text for condition in data.values.conditions] == [text]
    assert data.values.count_when_any_applies == 1
    assert data.values.count_when_none_applies == 0
    # The code is the count read (position 1 of the counts); no amount is read.
    assert data.values.count_positions_read == frozenset({1})
    assert data.values.amount_positions_read == frozenset()
    # A count, not the amount of a line: nothing is rounded.
    assert data.rounding == NO_ROUNDING


def test_the_flags_cite_the_t2125_form() -> None:
    for family in (BUSINESS, PROFESSIONAL, COMMISSION):
        assert conditions_dataset(family).sources == (T2125_PDF,), family


# --- the datasets run through their capability ---------------------------------------------------


@pytest.mark.parametrize("family", [BUSINESS, PROFESSIONAL, COMMISSION])
def test_a_flag_is_1_for_its_own_code_and_0_for_the_other_two(family: str) -> None:
    for code in (1, 2, 3):
        expected = 1 if code == LINE_OF_FAMILY[family] else 0

        assert flag(family, code) == expected, (family, code)


@pytest.mark.parametrize("code", [0, 4])
@pytest.mark.parametrize("family", [BUSINESS, PROFESSIONAL, COMMISSION])
def test_a_code_outside_1_to_3_flags_no_line(family: str, code: int) -> None:
    assert flag(family, code) == 0


# --- the code that is refused: a line code outside 1 to 3 ----------------------------------------

T2125_REFUSED = "ca/t2125_line_code_refused"


def t2125_refused() -> Any:
    return SOURCE.get(T2125_REFUSED, 2025, CONDITIONS)


def test_the_t2125_refused_dataset_has_one_condition_with_the_text_of_the_range() -> None:
    (condition,) = t2125_refused().values.conditions

    assert isinstance(condition, Condition)
    assert condition.text == "the statement's line code is not 1, 2 or 3"
    assert condition.parts == tuple(
        ConditionPart((ConditionTest("count", 1, "not_equal_to", D(code), None),))
        for code in (1, 2, 3)
    )


def test_the_t2125_refused_dataset_reads_only_the_count_at_position_1() -> None:
    values = t2125_refused().values

    assert values.count_when_any_applies == 1
    assert values.count_positions_read == frozenset({1})
    assert values.amount_positions_read == frozenset()


def test_the_t2125_refused_dataset_rounds_nothing_and_cites_the_pdf_of_the_form() -> None:
    data = t2125_refused()

    assert data.rounding == NO_ROUNDING
    assert data.sources == (T2125_PDF,)


def test_the_t2125_accepted_codes_pass_and_every_other_code_is_refused() -> None:
    raw = ArtifactKind("ex/code", int)
    checked = ArtifactKind("ex/code_checked", int)
    capability = CountRefusedByConditions(t2125_refused(), raw, checked)

    for code in range(0, 13):
        if code in (1, 2, 3):
            assert capability.compute((Artifact(raw, code),)).outputs == (Artifact(checked, code),)
        else:
            with pytest.raises(
                InputOutOfRangeError,
                match=f"ex/code {code} is refused: the statement's line code is not 1, 2 or 3",
            ):
                capability.compute((Artifact(raw, code),))
