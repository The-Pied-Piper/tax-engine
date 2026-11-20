"""Solidarity credit Schedule D lines 32 to 36, the tenant or owner answer, checked.

Source: Quebec Ministry of Finance, fiche 110201, Table C.9, and the Revenu Quebec page "Calculation
of the Credit" (web pages, so the figures are a listed check). The step is `ca/yes_or_no_count`. The
answer is a count of 1 for a tenant, subtenant or owner and 0 for neither; the check refuses a count
above 1, and the reduction rule reads the checked count as the housing component received. The
answers a caller does not give take their defaults (not alone, neither tenant nor owner, one owner
or tenant). The expected figures are hand-computed from the printed figures, not an official
example.
"""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.domain.kinds import CountKind
from tax_engine.jurisdictions.ca_qc.catalog import SOLIDARITY_HOUSING_RECEIVED
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.solidarity_maximum_support import maximum_figure
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

PART = "solidarity_credit_maximum.yaml"
FORM = "ca-qc/solidarity_credit"
IDENTIFIER = "ca-qc/solidarity_housing_received"


@pytest.mark.parametrize(
    ("answers", "expected"),
    [({}, 0), ({"tenant": 0}, 0), ({"tenant": 1}, 1)],
)
def test_housing_received_is_the_printed_figure(
    take_home_service: TakeHomeService, answers: dict[str, int], expected: int
) -> None:
    figure = maximum_figure(take_home_service, IDENTIFIER, **answers)

    assert figure == expected


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_the_step_produces_the_kind() -> None:
    part = _part()

    assert part["form"] == {"name": FORM}
    (step,) = [step for step in part["capabilities"] if step["produces"] == {"output": IDENTIFIER}]
    assert step == {
        "name": "ca/yes_or_no_count",
        "consumes": {"count": "ca-qc/solidarity_tenant_or_owner_lines_32_36"},
        "blank": {"count": "0"},
        "produces": {"output": IDENTIFIER},
    }
    assert "reference" not in step
    assert "title" not in step


def test_the_output_kind_is_a_registered_non_negative_count() -> None:
    assert quebec_kinds().kind(IDENTIFIER) is SOLIDARITY_HOUSING_RECEIVED
    assert isinstance(SOLIDARITY_HOUSING_RECEIVED, CountKind)
    assert non_negative(SOLIDARITY_HOUSING_RECEIVED)
