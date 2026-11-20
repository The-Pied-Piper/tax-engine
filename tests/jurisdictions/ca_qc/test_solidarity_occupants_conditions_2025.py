"""The 2025 `ca-qc/solidarity_occupants_conditions` dataset: the condition of the solidarity tax
credit's basic housing amount, checked against Table C.9 of fiche 110201.

Quebec Ministry of Finance, Dépenses fiscales 2025, fiche 110201, Table C.9, column "Juillet 2026 à
juin 2027": the basic housing amount is 746 for one owner or tenant and 906 shared among them for
more than one. The fiche is a web page, so the figures are a listed check until a printed source is
found. The dataset holds one condition, the number of owners or tenants (the first count, Schedule D
line 33 or 36) is more than 1. The count is 1 when it applies and 0 when it does not. It is a count,
so nothing is rounded.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import CountKind
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tests.jurisdictions.ca_qc.support import quebec_packages, quebec_parameter_parsers

D = Decimal
# Quebec is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers())
FAMILY = "ca-qc/solidarity_occupants_conditions"
SOURCE_PAGE = (
    "https://www.revenuquebec.ca/en/citizens/tax-credits/solidarity-tax-credit/"
    "calculation-of-the-credit/"
)

# Made up for this test and not registered: the number of owners or tenants and the count it gives.
OCCUPANTS = CountKind("ex/occupants")
MORE_THAN_ONE = CountKind("ex/more_than_one_occupant")


def test_2025_condition_is_more_than_one_owner_or_tenant() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "More than one owner or tenant",
                (ConditionPart((ConditionTest("count", 1, "more_than", D(1), None),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 0


def test_2025_condition_cites_the_source_page_and_does_not_round() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.sources == (SOURCE_PAGE,)
    assert data.rounding == NO_ROUNDING


def test_2025_condition_reads_one_count_and_no_amount() -> None:
    values = SOURCE.get(FAMILY, 2025, CONDITIONS).values

    assert values.count_positions_read == frozenset({1})
    assert values.amount_positions_read == frozenset()


@pytest.mark.parametrize(("occupants", "count"), [(0, 0), (1, 0), (2, 1), (3, 1), (10, 1)])
def test_the_count_is_1_for_more_than_one_owner_or_tenant_and_0_otherwise(
    occupants: int, count: int
) -> None:
    capability = CountByConditions(
        SOURCE.get(FAMILY, 2025, CONDITIONS), (OCCUPANTS,), (), MORE_THAN_ONE
    )

    result = capability.compute((Artifact(OCCUPANTS, occupants),)).outputs

    assert result == (Artifact(MORE_THAN_ONE, count),)
