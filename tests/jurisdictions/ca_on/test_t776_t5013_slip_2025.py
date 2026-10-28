"""The 2025 datasets of Form T776's T5013 slip conflicts, checked against the guide.

Guide T4036: "If you determine that you are a member of a partnership and you received a T5013
slip, fill in only the following fields on Form T776" (the business number, the percentage and
amount 7), and on line 9936: "Do not use the amount from line 9936 if you are a member of a
partnership that has to file Form T5013 SUM ... Your CCA amount is already included in box 110 of
your T5013 slip." A partner who received no slip fills in all of the parts. So the slip answer "yes"
with the partner answer "no" is a conflict, and so is a CCA claim of amount ii with the slip answer
"yes". So is any other figure of the statement but amount 7 and lines 9974 and 9943: the gross
rents and other income, an expense, a recapture or terminal loss, a land addition or disposition,
and an opening UCC, an addition or a remaining personal part of a row of Area A, which a row can
keep with a claim of 0, and the additions of Area B (line 9925) and Area C (line 9927).
The conditions of `ca/t776_t5013_slip_conflicts` say so: a condition applies when every one of its
parts holds. The conditions read the partner answer (count 1), the slip answer (count 2) and the
amounts: the CCA claim (1), the gross rents (2), the other income (3), the expense lines (4 to 16),
the recapture (17), the terminal loss (18), the land additions (19), the land dispositions (20), the
opening UCC total (21), the additions total (22) and the remaining personal part total (23) of Area
A, the total equipment additions (24) and the total building additions (25). The count is
refused when it is 1 (`ca/t776_t5013_slip_conflict_refused`). Nothing is
rounded.

The conditions are tested with made-up kinds, not registered.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.errors import InputOutOfRangeError
from tax_calculator.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_calculator.domain.parameters.rounding import NO_ROUNDING
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_calculator.jurisdictions.ca.capabilities.count_refused_by_conditions import (
    CountRefusedByConditions,
)

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
T776_TXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t776/t776-25e.txt"
T4036_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t4036/t4036-25e.pdf"

CONFLICTS_FAMILY = "ca/t776_t5013_slip_conflicts"
REFUSED_FAMILY = "ca/t776_t5013_slip_conflict_refused"

SLIP_WITHOUT_PARTNER_TEXT = "the T5013 slip answer is yes with the partner answer no"
CLAIM_WITH_SLIP_TEXT = "a CCA claim (amount ii of Area A) is entered with the T5013 slip answer yes"
INCOME_WITH_SLIP_TEXT = (
    "a figure of the gross rents or other income (lines 8141, 8230) is entered with the T5013 slip "
    "answer yes"
)
EXPENSE_WITH_SLIP_TEXT = (
    "an expense (a line of Part 4, lines 8521 to 9270) is entered with the T5013 slip answer yes"
)
RECAPTURE_WITH_SLIP_TEXT = (
    "a recapture or terminal loss (lines 9947, 9948) is entered with the T5013 slip answer yes"
)
LAND_WITH_SLIP_TEXT = (
    "a land addition or disposition (lines 9923, 9924) is entered with the T5013 slip answer yes"
)
AREA_A_ENTRY_WITH_SLIP_TEXT = (
    "an opening UCC, an addition or a remaining personal part of a row of Area A (columns 2, 3, 4, "
    "11 and 12, Note 9) is entered with the T5013 slip answer yes"
)
AREA_BC_WITH_SLIP_TEXT = (
    "an equipment addition of Area B or a building addition of Area C (lines 9925, 9927) is "
    "entered with the T5013 slip answer yes"
)
REFUSED_TEXT = (
    "the T5013 slip answer conflicts with the partner answer or the figures of the statement"
)

# Made up for this test and not registered: the two checked answers, the amounts the conditions
# read (position 1 the CCA claim), the count of the conflicts and its checked count.
PARTNER = ArtifactKind("ex/t776_partner_checked", int)
SLIP = ArtifactKind("ex/t776_t5013_slip_checked", int)
AMOUNT_NAMES = (
    "cca_table_claim",
    "gross_rents",
    "other_income",
    "advertising",
    "insurance",
    "interest_and_bank_charges",
    "office_expenses",
    "professional_fees",
    "management_and_administration_fees",
    "repairs_and_maintenance",
    "salaries_wages_and_benefits",
    "property_taxes",
    "travel",
    "utilities",
    "motor_vehicle_expenses",
    "other_expenses",
    "recapture",
    "terminal_loss",
    "land_additions",
    "land_dispositions",
    "opening_ucc_total",
    "additions_total",
    "personal_part_remaining_total",
    "equipment_additions_total",
    "building_additions_total",
)
AMOUNTS = tuple(ArtifactKind(f"ex/t776_{name}", Decimal) for name in AMOUNT_NAMES)
CLAIM = AMOUNTS[0]
CONFLICT = ArtifactKind("ex/t776_t5013_slip_conflict", int)
CONFLICT_CHECKED = ArtifactKind("ex/t776_t5013_slip_conflict_checked", int)


def _conflict(partner: int, slip: int, claim: str = "0", **others: str) -> int:
    """The count of the conflicts for the two answers, the CCA claim and the other amounts named
    (by their name in `AMOUNT_NAMES`); the amounts not named are 0."""
    capability = CountByConditions(
        SOURCE.get(CONFLICTS_FAMILY, 2025, CONDITIONS), (PARTNER, SLIP), AMOUNTS, CONFLICT
    )
    figures = {"cca_table_claim": claim, **others}
    inputs: tuple[Artifact[Any], ...] = (
        Artifact(PARTNER, partner),
        Artifact(SLIP, slip),
        *(
            Artifact(kind, D(figures.get(name, "0")))
            for name, kind in zip(AMOUNT_NAMES, AMOUNTS, strict=True)
        ),
    )
    (count,) = capability.compute(inputs).outputs
    return int(count.value)


def _refused(count: int) -> tuple[Artifact[Any], ...]:
    """The checked count of the conflicts for a count given, which is refused when it is 1."""
    capability = CountRefusedByConditions(
        SOURCE.get(REFUSED_FAMILY, 2025, CONDITIONS), CONFLICT, CONFLICT_CHECKED
    )
    return capability.compute((Artifact(CONFLICT, count),)).outputs


def _test(kind: str, position: int, relation: str, than: str) -> ConditionTest:
    """A test of the count or amount at `position`."""
    return ConditionTest(kind, position, relation, D(than), None)


def _with_slip(text: str, *positions: int) -> Condition:
    """The condition of the slip answer yes with any of the amounts at `positions` not 0."""
    return Condition(
        text,
        (
            ConditionPart((_test("count", 2, "equal_to", "1"),)),
            ConditionPart(tuple(_test("amount", p, "not_equal_to", "0") for p in positions)),
        ),
    )


def test_2025_the_conflicts_are_the_conditions_in_the_order_of_the_guide() -> None:
    data = SOURCE.get(CONFLICTS_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                SLIP_WITHOUT_PARTNER_TEXT,
                (
                    ConditionPart((_test("count", 2, "equal_to", "1"),)),
                    ConditionPart((_test("count", 1, "equal_to", "0"),)),
                ),
            ),
            Condition(
                CLAIM_WITH_SLIP_TEXT,
                (
                    ConditionPart((_test("count", 2, "equal_to", "1"),)),
                    ConditionPart((_test("amount", 1, "not_equal_to", "0"),)),
                ),
            ),
            _with_slip(INCOME_WITH_SLIP_TEXT, 2, 3),
            _with_slip(EXPENSE_WITH_SLIP_TEXT, *range(4, 17)),
            _with_slip(RECAPTURE_WITH_SLIP_TEXT, 17, 18),
            _with_slip(LAND_WITH_SLIP_TEXT, 19, 20),
            _with_slip(AREA_A_ENTRY_WITH_SLIP_TEXT, 21, 22, 23),
            _with_slip(AREA_BC_WITH_SLIP_TEXT, 24, 25),
        ),
    )


def test_2025_a_conflict_is_1_when_a_condition_applies_and_0_when_none_does() -> None:
    values = SOURCE.get(CONFLICTS_FAMILY, 2025, CONDITIONS).values

    assert values.count_when_any_applies == 1
    assert values.count_when_none_applies == 0


def test_2025_the_conflicts_read_the_two_answers_and_the_amounts() -> None:
    values = SOURCE.get(CONFLICTS_FAMILY, 2025, CONDITIONS).values

    assert values.count_positions_read == frozenset({1, 2})
    assert values.amount_positions_read == frozenset(range(1, len(AMOUNTS) + 1))


def test_2025_the_conflicts_are_not_rounded_and_cite_the_guide_and_the_form() -> None:
    data = SOURCE.get(CONFLICTS_FAMILY, 2025, CONDITIONS)

    assert data.rounding == NO_ROUNDING
    assert T4036_PDF in data.sources
    assert T776_TXT in data.sources


def test_a_slip_without_the_partner_answer_is_a_conflict() -> None:
    assert _conflict(0, 1) == 1


@pytest.mark.parametrize("partner", [0, 1])
def test_a_cca_claim_with_the_slip_answer_yes_is_a_conflict(partner: int) -> None:
    assert _conflict(partner, 1, "100") == 1


def test_a_partner_with_a_slip_and_no_cca_claim_is_not_a_conflict() -> None:
    assert _conflict(1, 1) == 0


# The groups of figures refused with the slip answer yes: each name of `AMOUNT_NAMES` alone.
GROUPS = {
    "income": ("gross_rents", "other_income"),
    "expense": AMOUNT_NAMES[3:16],
    "recapture and terminal loss": ("recapture", "terminal_loss"),
    "land": ("land_additions", "land_dispositions"),
    "Area A entries": ("opening_ucc_total", "additions_total", "personal_part_remaining_total"),
    "Areas B and C": ("equipment_additions_total", "building_additions_total"),
}


@pytest.mark.parametrize("name", [name for names in GROUPS.values() for name in names])
def test_a_figure_other_than_the_slip_lines_with_the_slip_answer_yes_is_a_conflict(
    name: str,
) -> None:
    assert _conflict(1, 1, **{name: "100"}) == 1


@pytest.mark.parametrize("name", [name for names in GROUPS.values() for name in names])
def test_a_loss_figure_with_the_slip_answer_yes_is_a_conflict_too(name: str) -> None:
    assert _conflict(1, 1, **{name: "-0.01"}) == 1


@pytest.mark.parametrize("name", AMOUNT_NAMES[1:])
def test_the_same_figure_is_no_conflict_without_a_slip(name: str) -> None:
    assert _conflict(1, 0, **{name: "100"}) == 0
    assert _conflict(0, 0, **{name: "100"}) == 0


@pytest.mark.parametrize("claim", ["0", "2500.50"])
def test_a_partner_without_a_slip_may_claim_cca(claim: str) -> None:
    assert _conflict(1, 0, claim) == 0


def test_an_owner_with_a_claim_is_not_a_conflict() -> None:
    assert _conflict(0, 0, "100") == 0


def test_2025_the_refusal_is_the_count_of_1() -> None:
    data = SOURCE.get(REFUSED_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                REFUSED_TEXT,
                (ConditionPart((_test("count", 1, "equal_to", "1"),)),),
            ),
        ),
    )
    assert data.rounding == NO_ROUNDING


def test_a_count_of_0_passes_the_refusal_and_a_count_of_1_is_refused() -> None:
    (checked,) = _refused(0)
    assert checked.value == 0

    with pytest.raises(InputOutOfRangeError, match="ex/t776_t5013_slip_conflict 1 is refused"):
        _refused(1)
