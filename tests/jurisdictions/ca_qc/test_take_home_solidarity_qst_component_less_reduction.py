"""The solidarity credit reduction rule: the QST component less the 3% reduction.

Source: Quebec Ministry of Finance, fiche 110201, Table C.9, and the Revenu Quebec page
"Calculation of the Credit" (web pages, so the figures are a listed check). The step is
`core/subtract_not_below_zero`. It reads artifacts the solidarity wiring produces, so these tests
give them as inputs. The family incomes are line 275 of the 2025 return at a salary of 20,000 /
70,000 / 200,000 (18,635 / 67,915 / 197,506); the reduction threshold is 43,195 and 64,545 is the
printed maximum family income.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import SOLIDARITY_QST_COMPONENT_LESS_REDUCTION
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.solidarity_support import solidarity_figure
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

D = Decimal
PART = "solidarity_credit_reduction.yaml"
FORM = "ca-qc/solidarity_credit"
IDENTIFIER = "ca-qc/solidarity_qst_component_less_reduction"


@pytest.mark.parametrize(
    ("income", "qst", "expected"),
    [
        ("18635", "363", "363.00"),
        ("45000", "363", "308.85"),
        ("45000", "535", "480.85"),
        ("67915", "535", "0.00"),
    ],
)
def test_qst_component_less_reduction_is_the_printed_figure(
    take_home_service: TakeHomeService, income: str, qst: str, expected: str
) -> None:
    figure = solidarity_figure(take_home_service, IDENTIFIER, income, qst=qst)

    assert figure == D(expected)


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_the_step_produces_the_kind() -> None:
    part = _part()

    assert part["form"] == {"name": FORM}
    (step,) = [step for step in part["capabilities"] if step["produces"] == {"output": IDENTIFIER}]
    assert step["name"] == "core/subtract_not_below_zero"
    assert step["unit"] == "ca/cad"
    assert step["params"] == {"rounding": "ca-qc/cent_rounding"}
    assert step["consumes"] == {
        "amount": "ca-qc/solidarity_qst_component_amount",
        "less": "ca-qc/solidarity_reduction_at_one_component_rate",
    }
    assert "reference" not in step
    assert "title" not in step


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    assert quebec_kinds().kind(IDENTIFIER) is SOLIDARITY_QST_COMPONENT_LESS_REDUCTION
    assert isinstance(SOLIDARITY_QST_COMPONENT_LESS_REDUCTION, AmountKind)
    assert non_negative(SOLIDARITY_QST_COMPONENT_LESS_REDUCTION)
