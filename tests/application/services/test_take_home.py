"""TakeHomeService answers what tax-service's take-home answer was when it did the mapping itself.

`take_home_answers.json` holds the answers tax-service gave for every province and year it serves,
at three salaries; the trace is kept as a hash and the number of lines of each form, at $70,000.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from tax_engine import build_take_home, build_tax_computation
from tax_engine.adapters.inbound.take_home_text import EnglishTakeHomeText
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.application.models.take_home import (
    TraceEntry,
    UnitDescription,
)
from tax_engine.application.models.take_home_request import TakeHomeRequest
from tax_engine.application.ports.jurisdiction_source import JurisdictionSource
from tax_engine.application.services.take_home import TakeHomeService
from tax_engine.domain.errors import NotFoundError
from tax_engine.domain.jurisdiction import Jurisdiction
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.core.units import PERCENT
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units

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
            include_rates=True,
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
        assert rate is not None
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


def test_rates_are_left_out_unless_asked_for(service: TakeHomeService) -> None:
    request = TakeHomeRequest(JurisdictionCode("CA-ON"), 2025, Decimal(70000))
    assert request.include_rates is False
    got = service.compute(request)
    assert got.average_income_tax_rate is None
    assert got.marginal_income_tax_rate is None


def test_average_rate_is_total_deductions_over_salary(service: TakeHomeService) -> None:
    got = service.compute(
        TakeHomeRequest(JurisdictionCode("CA-ON"), 2025, Decimal(70000), include_rates=True)
    )
    assert got.average_income_tax_rate is not None
    assert got.average_income_tax_rate.value == Decimal("0.2362")
    assert got.average_income_tax_rate.unit.name == "core/percent"


@pytest.mark.parametrize(
    ("salary", "ei"),
    [("2000", "0.00"), ("2001", "1.00"), ("2033", "33.00"), ("2100", "34.23")],
)
def test_ei_is_the_figure_the_form_uses_for_the_credit(
    service: TakeHomeService, salary: str, ei: str
) -> None:
    got = service.compute(TakeHomeRequest(JurisdictionCode("CA-ON"), 2026, Decimal(salary)))
    assert {f.name: str(f.amount) for f in got.figures}["ei"] == ei


def test_trace_is_left_out_unless_asked_for(service: TakeHomeService) -> None:
    request = TakeHomeRequest(JurisdictionCode("CA-ON"), 2025, Decimal(70000))
    assert request.include_trace is False
    assert service.compute(request).trace is None


class _WithoutTakeHome:
    """The real jurisdictions, each manifest as if it declared no take-home figures."""

    def __init__(self, source: JurisdictionSource) -> None:
        self._source = source

    def get_jurisdiction(self, code: JurisdictionCode) -> Jurisdiction:
        found = self._source.get_jurisdiction(code)
        return Jurisdiction(found.code, tuple(replace(m, take_home=None) for m in found.manifests))


def test_a_jurisdiction_that_declares_no_take_home_figures_is_not_found(
    service: TakeHomeService,
) -> None:
    source = YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units())
    bare = TakeHomeService(
        _WithoutTakeHome(source), build_tax_computation(), EnglishTakeHomeText(), PERCENT
    )
    with pytest.raises(NotFoundError, match="CA-ON 2025"):
        bare.compute(TakeHomeRequest(JurisdictionCode("CA-ON"), 2025, Decimal(70000)))


@pytest.mark.parametrize(
    ("year", "figures", "take_home"),
    [
        (
            2025,
            {
                "income_tax": "15919.71",
                "qpp_base": "3591.00",
                "qpp_enhanced": "665.00",
                "qpp2": "0.00",
                "ei": "860.67",
                "qpip": "345.80",
            },
            "48617.82",
        ),
        (
            2026,
            {
                "income_tax": "15540.41",
                "qpp_base": "3524.50",
                "qpp_enhanced": "665.00",
                "qpp2": "0.00",
                "ei": "895.70",
                "qpip": "301.00",
            },
            "49073.39",
        ),
    ],
)
def test_quebec_takes_off_both_returns_the_pension_plan_ei_and_qpip(
    service: TakeHomeService, year: int, figures: dict[str, str], take_home: str
) -> None:
    got = service.compute(TakeHomeRequest(JurisdictionCode("CA-QC"), year, Decimal(70000)))
    assert {f.name: str(f.amount) for f in got.figures} == figures
    assert str(got.take_home) == take_home
    assert str(got.income_tax) == figures["income_tax"]
    # Quebec's return does not compute the two rates yet, so it declares none.
    assert got.average_income_tax_rate is None
    assert got.marginal_income_tax_rate is None
