"""The 2025 Ontario focused flow-through share credit's condition (Form T1221).

2025 Form T1221 (`t1221-25e.pdf`, confirmed from the PDF; no .txt published), intro: "You must be a
resident of Ontario on the last day of the tax year to claim this credit." The conditions dataset
`ca-on/flow_through_share_conditions` holds the one case that rules the credit out, "You were not a
resident of Ontario on the last day of the tax year", read from a count, 1 when it applies. The
count it gives is 0 when the condition applies and 1 when it does not, so nothing is rounded.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
FAMILY = "ca-on/flow_through_share_conditions"
T1221_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1221/t1221-25e.pdf"

# Made up for this test and not registered.
NOT_RESIDENT_ONTARIO = ArtifactKind("ex/not_resident_of_ontario", int)
GATE = ArtifactKind("ex/gate", int)


def squashed(text: str) -> str:
    """`text` with the comment markers and line breaks gone and runs of blanks made one."""
    return re.sub(r"\s+", " ", text.replace("#", " ")).strip()


def dataset_header() -> str:
    """The comment lines above the dataset's first key, squashed."""
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca-on")]
    name = FAMILY.removeprefix("ca-on/")
    lines = (root / "parameters" / name / "2025.yaml").read_text().splitlines()
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return squashed("\n".join(lines[:first_key]))


def conditions_dataset() -> Any:
    return SOURCE.get(FAMILY, 2025, CONDITIONS)


def test_2025_the_one_condition_is_not_a_resident_of_ontario_on_the_last_day() -> None:
    data = conditions_dataset()

    assert data.values == ConditionList(
        0,
        (
            Condition(
                "You were not a resident of Ontario on the last day of the tax year",
                (ConditionPart((ConditionTest("count", 1, "equal_to", D(1), None),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 1
    assert data.values.count_positions_read == frozenset({1})
    assert data.values.amount_positions_read == frozenset()
    # A count, not the amount of a line: nothing is rounded.
    assert data.rounding == NO_ROUNDING


def test_2025_the_condition_cites_only_the_t1221_pdf() -> None:
    assert conditions_dataset().sources == (T1221_PDF,)


def test_the_header_quotes_t1221_as_the_form_prints_it() -> None:
    header = dataset_header()

    assert (
        "You must be a resident of Ontario on the last day of the tax year to claim this credit."
        in header
    )


@pytest.mark.parametrize(("not_resident", "claimable"), [(0, 1), (1, 0)])
def test_the_count_is_0_for_a_filer_who_was_not_a_resident_and_1_otherwise(
    not_resident: int, claimable: int
) -> None:
    capability = CountByConditions(conditions_dataset(), (NOT_RESIDENT_ONTARIO,), (), GATE)

    (output,) = capability.compute((Artifact(NOT_RESIDENT_ONTARIO, not_resident),)).outputs

    assert output.value == claimable
