"""Solidarity credit, the housing component amount: the basic housing amount for a tenant,
subtenant or owner.

Source: Quebec Ministry of Finance, fiche 110201, Table C.9, and the Revenu Quebec page "Calculation
of the Credit" (web pages, so the figures are a listed check). The step is `core/times_count`. The
answers a caller does not give take their defaults (not alone, neither tenant nor owner, one owner
or tenant). The expected figures are hand-computed from the printed figures, not an official
example.
"""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import SOLIDARITY_HOUSING_AMOUNT
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.solidarity_maximum_support import maximum_figure
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

PART = "solidarity_credit_maximum.yaml"
FORM = "ca-qc/solidarity_credit"
IDENTIFIER = "ca-qc/solidarity_housing_amount"


@pytest.mark.parametrize(
    ("answers", "expected"),
    [
        ({}, "0.00"),
        ({"tenant": 1}, "746.00"),
        ({"tenant": 1, "occupants": 3}, "302.00"),
        ({"tenant": 0, "occupants": 3}, "0.00"),
    ],
)
def test_housing_amount_is_the_printed_figure(
    take_home_service: TakeHomeService, answers: dict[str, int], expected: str
) -> None:
    figure = maximum_figure(take_home_service, IDENTIFIER, **answers)

    assert str(figure) == expected


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_the_step_produces_the_kind() -> None:
    part = _part()

    assert part["form"] == {"name": FORM}
    (step,) = [step for step in part["capabilities"] if step["produces"] == {"output": IDENTIFIER}]
    assert step == {
        "name": "core/times_count",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {
            "amount": "ca-qc/solidarity_housing_basic_amount",
            "count": "ca-qc/solidarity_housing_received",
        },
        "produces": {"output": IDENTIFIER},
    }
    assert "reference" not in step
    assert "title" not in step


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    assert quebec_kinds().kind(IDENTIFIER) is SOLIDARITY_HOUSING_AMOUNT
    assert isinstance(SOLIDARITY_HOUSING_AMOUNT, AmountKind)
    assert non_negative(SOLIDARITY_HOUSING_AMOUNT)
