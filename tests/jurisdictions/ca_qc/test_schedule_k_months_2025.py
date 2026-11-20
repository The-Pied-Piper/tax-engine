"""The 2025 Schedule K month-box datasets, `ca-qc/schedule_k_months_box_60` and `_box_61`.

Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part B, section 1: "Number of months checked from
January to June ... 60" and "Number of months checked from July to December ... 61". The form
prints no table. Each box counts the months checked for line 50, and the answer to line 50 means
covered all year (owner's optional-answer ruling, 19 Nov 2026), so each dataset is two rows keyed
by the answer: 0 gives 0 months and 1 gives 6. Whole months, so the cent rounding changes none.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NoAmountForCountError
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.jurisdictions.ca.capabilities.amount_by_count import AmountForCount
from tax_engine.jurisdictions.ca.parameter_shapes.amount_by_count import (
    AMOUNT_BY_COUNT,
    AmountByCount,
)
from tests.jurisdictions.ca_qc.support import (
    quebec_packages,
    quebec_parameter_parsers,
    quebec_units,
)

D = Decimal
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers(), quebec_units())
FAMILIES = ("ca-qc/schedule_k_months_box_60", "ca-qc/schedule_k_months_box_61")
FORM = "Revenu Quebec TP-1.D.K-V (2025-12)"

# Made up for this test and not registered: the answer, and the figure the capability reads.
ANSWER = CountKind("ex/answer")
FIGURE = AmountKind("ex/figure")


@pytest.mark.parametrize("family", FAMILIES)
def test_2025_table_is_6_months_for_a_yes_and_0_for_a_no(family: str) -> None:
    data = SOURCE.get(family, 2025, AMOUNT_BY_COUNT)

    assert data.values == AmountByCount(((0, D("0")), (1, D("6"))))


@pytest.mark.parametrize("family", FAMILIES)
def test_2025_table_is_rounded_half_up_to_the_cent(family: str) -> None:
    data = SOURCE.get(family, 2025, AMOUNT_BY_COUNT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


@pytest.mark.parametrize("family", FAMILIES)
def test_2025_table_cites_the_schedule_k_form(family: str) -> None:
    data = SOURCE.get(family, 2025, AMOUNT_BY_COUNT)

    assert FORM in data.sources


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize(("answer", "months"), [(0, "0.00"), (1, "6.00")])
def test_reads_the_row_for_the_answer(family: str, answer: int, months: str) -> None:
    capability = AmountForCount(SOURCE.get(family, 2025, AMOUNT_BY_COUNT), ANSWER, FIGURE)

    result = capability.compute((Artifact(ANSWER, answer),))

    assert result.outputs[0].value == D(months)


@pytest.mark.parametrize("family", FAMILIES)
def test_an_answer_with_no_row_is_refused(family: str) -> None:
    capability = AmountForCount(SOURCE.get(family, 2025, AMOUNT_BY_COUNT), ANSWER, FIGURE)

    with pytest.raises(NoAmountForCountError):
        capability.compute((Artifact(ANSWER, 2),))
