"""The 2025 Form T2043 Chart A datasets: the province conditions and the amount 8 rounding.

Form T2043, Return of Fuel Charge Proceeds to Farmers Tax Credit, 2025 edition, read from the PDF
(https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2043/t2043-25e.pdf; no .txt is
published). Chart A, amount 8 is "Amount 6 multiplied by amount 7." and amount 7 is the days in 2024
over the days of the fiscal period; the form gives no rounding rule, so the product is rounded
half-up to the cent, as the other dollars-and-cents boxes are.

Two groups of datasets:
- `ca/farm_chart_a_amount_8_rounding` (`rounding_only`): the half-up cent rule for amount 8.
- `ca/farm_province_<p>_conditions` for the eight provinces, in the order of the form's Part 2
  lines 2A to 2H: on, mb, sk, ab, ns, pe, nl, nb. Each holds one condition, "the designated
  province is <name> and no Chart B is in use": two parts, read from the count
  `ca/farm_designated_province` (the province code 1 to 8 of Form T2042) and the count
  `ca/farm_chart_b_in_use` (0 when the statement uses no Chart B, so Part 2 skips a statement
  that Chart B credits). The count it gives is 1 when both hold, else 0, so nothing is rounded.
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
    ConditionPart,
    ConditionTest,
)
from tax_calculator.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.jurisdictions.ca.capabilities.count_refused_by_conditions import (
    CountRefusedByConditions,
)

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
T2043_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2043/t2043-25e.pdf"
AMOUNT_8_ROUNDING = "ca/farm_chart_a_amount_8_rounding"

# The province code of Form T2042 and the province name, in the order of Form T2043 Part 2.
PROVINCES: tuple[tuple[str, int, str], ...] = (
    ("on", 1, "Ontario"),
    ("mb", 2, "Manitoba"),
    ("sk", 3, "Saskatchewan"),
    ("ab", 4, "Alberta"),
    ("ns", 5, "Nova Scotia"),
    ("pe", 6, "Prince Edward Island"),
    ("nl", 7, "Newfoundland and Labrador"),
    ("nb", 8, "New Brunswick"),
)


def conditions_name(code: str) -> str:
    return f"ca/farm_province_{code}_conditions"


def conditions_dataset(code: str) -> Any:
    return SOURCE.get(conditions_name(code), 2025, CONDITIONS)


def test_2025_amount_8_is_rounded_half_up_to_the_cent() -> None:
    data = SOURCE.get(AMOUNT_8_ROUNDING, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == CENT
    assert T2043_PDF in data.sources


def test_each_province_has_a_conditions_dataset_of_its_own() -> None:
    for code, _, _ in PROVINCES:
        data = conditions_dataset(code)

        assert len(data.values.conditions) == 1, code


def test_each_province_condition_reads_the_designated_province_count_for_its_code() -> None:
    for code, province_code, name in PROVINCES:
        data = conditions_dataset(code)
        (condition,) = data.values.conditions

        assert isinstance(condition, Condition), code
        assert name in condition.text, code
        # Two parts, both of which must hold: the designated province is this one (count 1), and
        # no Chart B is in use (count 2, 0): a statement that uses Chart B is not counted in Part 2.
        assert condition.parts == (
            ConditionPart((ConditionTest("count", 1, "equal_to", D(province_code), None),)),
            ConditionPart((ConditionTest("count", 2, "equal_to", D("0"), None),)),
        ), code


def test_each_province_count_is_1_when_the_condition_applies_and_0_otherwise() -> None:
    for code, _, _ in PROVINCES:
        values = conditions_dataset(code).values

        assert values.count_when_any_applies == 1, code
        assert values.count_when_none_applies == 0, code


def test_each_province_condition_reads_the_province_count_and_the_chart_b_count() -> None:
    for code, _, _ in PROVINCES:
        values = conditions_dataset(code).values

        assert values.count_positions_read == frozenset({1, 2}), code
        assert values.amount_positions_read == frozenset(), code


def test_each_province_condition_is_a_count_so_nothing_is_rounded() -> None:
    for code, _, _ in PROVINCES:
        assert conditions_dataset(code).rounding == NO_ROUNDING, code


def test_each_province_condition_cites_only_the_t2043_pdf() -> None:
    for code, _, _ in PROVINCES:
        assert conditions_dataset(code).sources == (T2043_PDF,), code


# --- the code that is refused: a province code above 8 -------------------------------------------

FARM_REFUSED = "ca/farm_designated_province_refused"


def farm_refused() -> Any:
    return SOURCE.get(FARM_REFUSED, 2025, CONDITIONS)


def test_the_farm_refused_dataset_has_one_condition_with_the_text_of_the_range() -> None:
    (condition,) = farm_refused().values.conditions

    assert isinstance(condition, Condition)
    assert condition.text == "the designated province code is above 8"
    assert condition.parts == (
        ConditionPart((ConditionTest("count", 1, "more_than", D(8), None),)),
    )


def test_the_farm_refused_dataset_reads_only_the_count_at_position_1() -> None:
    values = farm_refused().values

    assert values.count_when_any_applies == 1
    assert values.count_positions_read == frozenset({1})
    assert values.amount_positions_read == frozenset()


def test_the_farm_refused_dataset_rounds_nothing_and_cites_the_pdf_of_the_form() -> None:
    data = farm_refused()

    assert data.rounding == NO_ROUNDING
    assert data.sources == (T2043_PDF,)


def test_the_farm_accepted_codes_pass_and_every_other_code_is_refused() -> None:
    raw = ArtifactKind("ex/code", int)
    checked = ArtifactKind("ex/code_checked", int)
    capability = CountRefusedByConditions(farm_refused(), raw, checked)

    for code in range(0, 13):
        if code in tuple(range(0, 9)):
            assert capability.compute((Artifact(raw, code),)).outputs == (Artifact(checked, code),)
        else:
            with pytest.raises(
                InputOutOfRangeError,
                match=f"ex/code {code} is refused: the designated province code is above 8",
            ):
                capability.compute((Artifact(raw, code),))
