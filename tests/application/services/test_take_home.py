"""TakeHomeService answers what tax-service's take-home answer was when it did the mapping itself.

`take_home_answers.json` holds the answers tax-service gave for every province and year it serves,
at three salaries; the trace is kept as a hash and the number of lines of each form, at $70,000.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from tax_engine import build_take_home
from tax_engine.application.services.take_home import TakeHomeService
from tax_engine.application.services.take_home_models import (
    TakeHomeRequest,
    TraceEntry,
    UnitDescription,
)
from tax_engine.domain.errors import NotFoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode

ANSWERS: list[dict[str, Any]] = json.loads(
    (Path(__file__).parent / "take_home_answers.json").read_text()
)


@pytest.fixture(scope="module")
def service() -> TakeHomeService:
    return build_take_home()


def _unit(unit: UnitDescription) -> dict[str, Any]:
    return {
        "name": unit.name,
        "placement": unit.placement,
        "singular": unit.singular,
        "plural": unit.plural,
        "spaced": unit.spaced,
        "as_percentage": unit.as_percentage,
    }


def _entry(entry: TraceEntry) -> dict[str, Any]:
    return {
        "label": entry.label,
        "name": entry.name,
        "reference": entry.reference,
        "amount": None if entry.amount is None else str(entry.amount),
        "text": entry.text,
        "unit": None if entry.unit is None else _unit(entry.unit),
    }


@dataclass(frozen=True)
class Case:
    answer: dict[str, Any]

    def __repr__(self) -> str:
        a = self.answer
        return f"{a['jurisdiction']}-{a['year']}-{a['salary']}"


@pytest.mark.parametrize("case", [Case(a) for a in ANSWERS], ids=repr)
def test_answers_match_what_tax_service_gave(service: TakeHomeService, case: Case) -> None:
    want = case.answer
    got = service.compute(
        TakeHomeRequest(
            JurisdictionCode(want["jurisdiction"]),
            want["year"],
            Decimal(want["salary"]),
            include_trace="trace_sha256" in want,
        )
    )
    assert {f.name: str(f.amount) for f in got.figures} == want["figures"]
    assert all(isinstance(f.amount, Decimal) for f in got.figures)
    assert str(got.income_tax) == want["income_tax"]
    assert str(got.total_deductions) == want["total_deductions"]
    assert str(got.take_home) == want["take_home"]
    assert _unit(got.unit) == want["unit"]
    for rate, key in (
        (got.average_income_tax_rate, "average_income_tax_rate"),
        (got.marginal_income_tax_rate, "marginal_income_tax_rate"),
    ):
        assert str(rate.value) == want[key]["value"]
        assert _unit(rate.unit) == want[key]["unit"]
    if "trace_sha256" not in want:
        assert got.trace is None
        return
    assert got.trace is not None
    assert [{"form": t.form, "lines": len(t.lines)} for t in got.trace] == want["trace_forms"]
    shown = [
        {"form": t.form, "name": t.name, "lines": [_entry(line) for line in t.lines]}
        for t in got.trace
    ]
    digest = hashlib.sha256(
        json.dumps(shown, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert digest == want["trace_sha256"]


def test_ontario_2025_at_seventy_thousand(service: TakeHomeService) -> None:
    got = service.compute(TakeHomeRequest(JurisdictionCode("CA-ON"), 2025, Decimal(70000)))
    assert got.take_home == Decimal("53468.68")
    assert got.salary == Decimal("70000.00")


def test_trace_is_left_out_unless_asked_for(service: TakeHomeService) -> None:
    request = TakeHomeRequest(JurisdictionCode("CA-ON"), 2025, Decimal(70000))
    assert request.include_trace is False
    assert service.compute(request).trace is None


def test_a_jurisdiction_that_declares_no_take_home_figures_is_not_found(
    service: TakeHomeService,
) -> None:
    with pytest.raises(NotFoundError, match="CA-QC"):
        service.compute(TakeHomeRequest(JurisdictionCode("CA-QC"), 2025, Decimal(70000)))
