"""Solidarity credit Schedule D line 12, the living-alone answer, checked.

Source: Quebec Ministry of Finance, fiche 110201, Table C.9, and the Revenu Quebec page "Calculation
of the Credit" (web pages, so the figures are a listed check). The step is `ca/yes_or_no_count`.
Line 12 asks "Did you live alone in a dwelling throughout 2025?"; the answer is a count of 1 for yes
and 0 for no, and the check refuses a count above 1. The answers a caller does not give take their
defaults (not alone, neither tenant nor owner, one owner or tenant). The expected figures are hand-
computed from the printed figures, not an official example.
"""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.domain.kinds import CountKind
from tax_engine.jurisdictions.ca_qc.catalog import SOLIDARITY_LIVED_ALONE_CHECKED_LINE_12
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.solidarity_maximum_support import maximum_figure
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

PART = "solidarity_credit_maximum.yaml"
FORM = "ca-qc/solidarity_credit"
IDENTIFIER = "ca-qc/solidarity_lived_alone_checked_line_12"


@pytest.mark.parametrize(
    ("answers", "expected"),
    [({}, 0), ({"alone": 0}, 0), ({"alone": 1}, 1)],
)
def test_lived_alone_checked_is_the_printed_figure(
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
        "consumes": {"count": "ca-qc/solidarity_lived_alone_line_12"},
        "blank": {"count": "0"},
        "produces": {"output": IDENTIFIER},
    }
    assert "reference" not in step
    assert "title" not in step


def test_the_output_kind_is_a_registered_non_negative_count() -> None:
    assert quebec_kinds().kind(IDENTIFIER) is SOLIDARITY_LIVED_ALONE_CHECKED_LINE_12
    assert isinstance(SOLIDARITY_LIVED_ALONE_CHECKED_LINE_12, CountKind)
    assert non_negative(SOLIDARITY_LIVED_ALONE_CHECKED_LINE_12)
