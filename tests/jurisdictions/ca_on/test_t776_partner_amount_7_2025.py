"""The 2025 datasets of Form T776's amount 7 of a partner, checked against the guide.

Guide T4036: "If you are in a partnership and you do not receive a T5013 slip ... fill in all of the
parts in Form T776 that apply to you" and "Amount 7 - Partnerships: If you are a member of a
partnership, enter your share of amount 6 or the amount from box 107 or 110 from your T5013 slip."
Form T776 Part 1 prints "Your percentage of the partnership %". The share of amount 6 is amount 6
times that percentage as the form prints it (50 for 50%); line 7 is a dollars-and-cents box and
the form states no rounding rule, so the product rounds half-up to the cent, the repo's rule for a
dollars-and-cents box. The conditions of `ca/t776_partner_amount_7_conflicts` refuse an amount 7
typed by a partner with no slip; the count is refused when it is 1
(`ca/t776_partner_amount_7_conflict_refused`). Nothing else is rounded.

The datasets are tested with the capabilities that read them, on made-up kinds; the lines together
are in `returns/2025_return_ka.yaml` and `end_to_end/test_return_ka.py`.
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
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.jurisdictions.ca.capabilities.apply_percentage import ApplyPercentage
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.capabilities.count_refused_by_conditions import (
    CountRefusedByConditions,
)

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
T776_TXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t776/t776-25e.txt"
T4036_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t4036/t4036-25e.pdf"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

ROUNDING = "ca/rental_partner_share_rounding"
CONFLICTS_FAMILY = "ca/t776_partner_amount_7_conflicts"
REFUSED_FAMILY = "ca/t776_partner_amount_7_conflict_refused"

NO_SLIP_TEXT = "an amount 7 is entered by a partner who received no T5013 slip"
REFUSED_TEXT = "amount 7 conflicts with the partner and slip answers"

# Made up for this test and not registered.
PARTNER = ArtifactKind("ex/t776_partner_checked", int)
SLIP = ArtifactKind("ex/t776_t5013_slip_checked", int)
AMOUNT_7 = ArtifactKind("ex/t776_amount_7_typed", Decimal)
PERCENTAGE = ArtifactKind("ex/t776_percentage", Decimal)
AMOUNT_6 = ArtifactKind("ex/t776_amount_6", Decimal)
SHARE = ArtifactKind("ex/t776_share", Decimal)
CONFLICT = ArtifactKind("ex/t776_amount_7_conflict", int)
CONFLICT_CHECKED = ArtifactKind("ex/t776_amount_7_conflict_checked", int)


def _test(kind: str, position: int, relation: str, than: str) -> ConditionTest:
    """A test of the count or amount at `position`."""
    return ConditionTest(kind, position, relation, D(than), None)


def _conflict(partner: int, slip: int, typed: str = "0") -> int:
    """The count of the conflicts for the two answers and the typed amount 7."""
    capability = CountByConditions(
        SOURCE.get(CONFLICTS_FAMILY, 2025, CONDITIONS),
        (PARTNER, SLIP),
        (AMOUNT_7,),
        CONFLICT,
    )
    inputs: tuple[Artifact[Any], ...] = (
        Artifact(PARTNER, partner),
        Artifact(SLIP, slip),
        Artifact(AMOUNT_7, D(typed)),
    )
    (count,) = capability.compute(inputs).outputs
    return int(count.value)


def test_2025_the_share_rounding_is_half_up_to_the_cent() -> None:
    assert SOURCE.get(ROUNDING, 2025, ROUNDING_ONLY).rounding == CENT


def test_2025_the_share_rounding_cites_the_form_it_is_printed_on() -> None:
    assert SOURCE.get(ROUNDING, 2025, ROUNDING_ONLY).sources == (T776_TXT,)


@pytest.mark.parametrize(
    ("percentage", "result"),
    [
        # 1100 x 50% = 550.00.
        ("50", "550.00"),
        ("100", "1100.00"),
        ("0", "0.00"),
        # 1100 x 33.335 / 100 = 366.685, half-up to the cent, 366.69.
        ("33.335", "366.69"),
    ],
)
def test_the_share_is_amount_6_times_the_percentage_as_printed_rounded_once(
    percentage: str, result: str
) -> None:
    capability = ApplyPercentage(
        SOURCE.get(ROUNDING, 2025, ROUNDING_ONLY), AMOUNT_6, PERCENTAGE, SHARE
    )

    (output,) = capability.compute(
        (Artifact(AMOUNT_6, D("1100")), Artifact(PERCENTAGE, D(percentage)))
    ).outputs

    assert output.value == D(result)
    assert output.value.as_tuple().exponent == -2


def test_2025_the_conflicts_are_the_conditions_in_the_order_of_the_guide() -> None:
    data = SOURCE.get(CONFLICTS_FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                NO_SLIP_TEXT,
                (
                    ConditionPart((_test("count", 1, "equal_to", "1"),)),
                    ConditionPart((_test("count", 2, "equal_to", "0"),)),
                    ConditionPart((_test("amount", 1, "not_equal_to", "0"),)),
                ),
            ),
        ),
    )


def test_2025_the_conflicts_are_not_rounded_and_cite_the_guide_and_the_form() -> None:
    data = SOURCE.get(CONFLICTS_FAMILY, 2025, CONDITIONS)

    assert data.rounding == NO_ROUNDING
    assert T4036_PDF in data.sources
    assert T776_TXT in data.sources


def test_a_typed_amount_7_from_a_partner_with_no_slip_is_a_conflict() -> None:
    assert _conflict(1, 0, typed="550") == 1
    assert _conflict(1, 0, typed="-0.01") == 1


def test_a_typed_amount_7_from_a_partner_with_a_slip_is_no_conflict() -> None:
    assert _conflict(1, 1, typed="550") == 0


def test_no_figures_are_no_conflict() -> None:
    assert _conflict(0, 0) == 0
    assert _conflict(1, 0) == 0


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


def test_a_count_of_1_is_refused_and_a_count_of_0_passes() -> None:
    capability = CountRefusedByConditions(
        SOURCE.get(REFUSED_FAMILY, 2025, CONDITIONS), CONFLICT, CONFLICT_CHECKED
    )

    (checked,) = capability.compute((Artifact(CONFLICT, 0),)).outputs
    assert checked.value == 0
    with pytest.raises(InputOutOfRangeError):
        capability.compute((Artifact(CONFLICT, 1),))
