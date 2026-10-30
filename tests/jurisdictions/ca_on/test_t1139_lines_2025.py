"""The 2025 datasets of Form T1139: the five line flags, the three formula flags, the two refusals
and the rounding of the three products.

Form T1139 (2025), Part 4 "Report amount G as self-employment income on your return" (Part 5 says
the same of amount L) lists five lines: "For business income, enter it at line 13500", "For
professional income, enter it at line 13700", "For commission income, enter it at line 13900", "For
farming income, enter it at line 14100" and "For fishing income, enter it at line 14300". The form
names no codes. A business's line is the number of the filer's choice in that list, 1 to 5. Each
flag is a conditions dataset that counts 1 when the number is its line's and 0 otherwise. Nothing is
rounded: a count is never an amount of a line.

Amounts B, C and 3H are each an amount multiplied by a quotient of days, dollars-and-cents boxes
for which the form states no rounding rule, so each product rounds half-up to the cent, once, from
the exact fraction (the form's example: 45,000 x 275 / 365 = 33,904.11).

The form is at https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1139/t1139-25e.pdf (no .txt
is published).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.errors import InputOutOfRangeError
from tax_engine.domain.parameters.conditions import CONDITIONS
from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_engine.jurisdictions.ca.capabilities.count_refused_by_conditions import (
    CountRefusedByConditions,
)
from tax_engine.jurisdictions.ca.catalog import (
    T1139_FORMULA_CHECKED,
    T1139_FORMULA_IS_3H,
    T1139_FORMULA_IS_B,
    T1139_FORMULA_IS_C,
    T1139_LINE,
    T1139_ON_BUSINESS_LINE,
    T1139_ON_COMMISSION_LINE,
    T1139_ON_FARMING_LINE,
    T1139_ON_FISHING_LINE,
    T1139_ON_PROFESSIONAL_LINE,
)

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
T1139_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1139/t1139-25e.pdf"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

FLAGS = {
    "ca/t1139_line_is_business": (
        1,
        T1139_ON_BUSINESS_LINE,
        "For business income, enter it at line 13500",
    ),
    "ca/t1139_line_is_professional": (
        2,
        T1139_ON_PROFESSIONAL_LINE,
        "For professional income, enter it at line 13700",
    ),
    "ca/t1139_line_is_commission": (
        3,
        T1139_ON_COMMISSION_LINE,
        "For commission income, enter it at line 13900",
    ),
    "ca/t1139_line_is_farming": (
        4,
        T1139_ON_FARMING_LINE,
        "For farming income, enter it at line 14100",
    ),
    "ca/t1139_line_is_fishing": (
        5,
        T1139_ON_FISHING_LINE,
        "For fishing income, enter it at line 14300",
    ),
}


def flag(family: str, code: int) -> int:
    """The flag `family` gives a business whose line number is `code`."""
    _number, kind, _text = FLAGS[family]
    capability = CountByConditions(SOURCE.get(family, 2025, CONDITIONS), (T1139_LINE,), (), kind)
    (output,) = capability.compute((Artifact(T1139_LINE, code),)).outputs

    assert isinstance(output.value, int)
    return output.value


@pytest.mark.parametrize("family", FLAGS)
def test_each_flag_is_a_one_condition_count_of_the_line_number(family: str) -> None:
    _number, _kind, text = FLAGS[family]
    data = SOURCE.get(family, 2025, CONDITIONS)

    assert [condition.text for condition in data.values.conditions] == [text]
    assert data.values.count_when_any_applies == 1
    assert data.values.count_when_none_applies == 0
    # The line number is the count read (position 1 of the counts); no amount is read.
    assert data.values.count_positions_read == frozenset({1})
    assert data.values.amount_positions_read == frozenset()
    # A count, not the amount of a line: nothing is rounded.
    assert data.rounding == NO_ROUNDING
    assert data.sources == (T1139_PDF,)


@pytest.mark.parametrize("family", FLAGS)
def test_a_flag_is_1_for_its_own_line_and_0_for_the_other_four(family: str) -> None:
    number, _kind, _text = FLAGS[family]

    for code in range(1, 6):
        assert flag(family, code) == (1 if code == number else 0), (family, code)


@pytest.mark.parametrize("code", [0, 6])
@pytest.mark.parametrize("family", FLAGS)
def test_a_number_outside_1_to_5_flags_no_line(family: str, code: int) -> None:
    assert flag(family, code) == 0


def test_the_rounding_is_half_up_to_the_cent_with_no_other_figure() -> None:
    data: Any = SOURCE.get("ca/t1139_rounding", 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == CENT
    assert data.sources == (T1139_PDF,)


def test_the_rounding_gives_the_forms_example_of_amounts_b_and_c() -> None:
    # 45,000 x 275 / 365 = 33,904.109..., which is 33,904.11 to the cent.
    data: Any = SOURCE.get("ca/t1139_rounding", 2025, ROUNDING_ONLY)

    assert data.rounding.apply(D(45000) * 275 / 365) == D("33904.11")


FORMULA_FLAGS = {
    "ca/t1139_formula_is_b": (1, T1139_FORMULA_IS_B),
    "ca/t1139_formula_is_c": (2, T1139_FORMULA_IS_C),
    "ca/t1139_formula_is_3h": (3, T1139_FORMULA_IS_3H),
}


@pytest.mark.parametrize("family", FORMULA_FLAGS)
def test_a_formula_flag_is_1_for_its_own_number_and_0_for_the_others(family: str) -> None:
    number, kind = FORMULA_FLAGS[family]
    capability = CountByConditions(
        SOURCE.get(family, 2025, CONDITIONS), (T1139_FORMULA_CHECKED,), (), kind
    )

    for code in range(0, 4):
        (output,) = capability.compute((Artifact(T1139_FORMULA_CHECKED, code),)).outputs
        assert output.value == (1 if code == number else 0), (family, code)


@pytest.mark.parametrize(
    ("family", "accepted"),
    [("ca/t1139_line_refused", range(1, 6)), ("ca/t1139_formula_refused", range(0, 4))],
)
def test_the_accepted_numbers_pass_and_every_other_number_is_refused(
    family: str, accepted: range
) -> None:
    raw = ArtifactKind("ex/number", int)
    checked = ArtifactKind("ex/number_checked", int)
    data: Any = SOURCE.get(family, 2025, CONDITIONS)
    capability = CountRefusedByConditions(data, raw, checked)

    assert data.rounding == NO_ROUNDING
    assert data.sources == (T1139_PDF,)
    for code in range(0, 9):
        if code in accepted:
            assert capability.compute((Artifact(raw, code),)).outputs == (Artifact(checked, code),)
        else:
            with pytest.raises(InputOutOfRangeError):
                capability.compute((Artifact(raw, code),))
