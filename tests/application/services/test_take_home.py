"""TakeHomeService answers what tax-service's take-home answer was when it did the mapping itself.

`take_home_answers.json` holds the answers tax-service gave for every province and year it serves,
at three salaries; the trace is kept as a hash and the number of lines of each form, at $70,000.
"""

from __future__ import annotations

import hashlib
import json
import threading
from concurrent.futures import ThreadPoolExecutor
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
        (got.average_tax_rate, "average_tax_rate"),
        (got.marginal_tax_rate, "marginal_tax_rate"),
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
    assert got.average_tax_rate is None
    assert got.marginal_tax_rate is None


def test_average_rate_is_total_deductions_over_salary(service: TakeHomeService) -> None:
    got = service.compute(
        TakeHomeRequest(JurisdictionCode("CA-ON"), 2025, Decimal(70000), include_rates=True)
    )
    assert got.average_tax_rate is not None
    assert got.average_tax_rate.value == Decimal("0.2362")
    assert got.average_tax_rate.unit.name == "core/percent"


@pytest.mark.parametrize(
    ("salary", "ei"),
    [("2000", "0.00"), ("2001", "1.00"), ("2033", "33.00"), ("2100", "34.23")],
)
def test_ei_is_the_figure_the_form_uses_for_the_credit(
    service: TakeHomeService, salary: str, ei: str
) -> None:
    got = service.compute(TakeHomeRequest(JurisdictionCode("CA-ON"), 2026, Decimal(salary)))
    assert {f.name: str(f.amount) for f in got.figures}["ei"] == ei


def test_average_rate_is_rounded_by_the_dataset_rule_of_the_tax_year(
    service: TakeHomeService,
) -> None:
    got = service.compute(
        TakeHomeRequest(JurisdictionCode("CA-ON"), 2026, Decimal(70000), include_rates=True)
    )
    assert got.average_tax_rate is not None
    assert got.average_tax_rate.value == got.average_tax_rate.value.quantize(Decimal("0.0001"))


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
        _WithoutTakeHome(source),
        build_tax_computation(),
        EnglishTakeHomeText(),
    )
    with pytest.raises(NotFoundError, match="CA-ON 2025"):
        bare.compute(TakeHomeRequest(JurisdictionCode("CA-ON"), 2025, Decimal(70000)))


@pytest.mark.parametrize(
    ("year", "figures", "take_home"),
    [
        (
            2025,
            {
                "income_tax": "14678.32",
                "qpp_base": "3591.00",
                "qpp_enhanced": "665.00",
                "qpp2": "0.00",
                "ei": "860.67",
                "qpip": "345.80",
            },
            "49859.21",
        ),
        (
            2026,
            {
                "income_tax": "14346.59",
                "qpp_base": "3524.50",
                "qpp_enhanced": "665.00",
                "qpp2": "0.00",
                "ei": "895.70",
                "qpip": "301.00",
            },
            "50267.21",
        ),
    ],
)
# The income tax is both returns' total payable less the refundable Quebec abatement (5005-R line
# 44000): at $70,000 in 2026 15,540.41 - 1,193.82 = 14,346.59 (Umar, 25 Nov 2026).
def test_quebec_takes_off_both_returns_the_pension_plan_ei_and_qpip(
    service: TakeHomeService, year: int, figures: dict[str, str], take_home: str
) -> None:
    got = service.compute(TakeHomeRequest(JurisdictionCode("CA-QC"), year, Decimal(70000)))
    assert {f.name: str(f.amount) for f in got.figures} == figures
    assert str(got.take_home) == take_home
    assert str(got.income_tax) == figures["income_tax"]
    assert got.average_tax_rate is None  # rates are left out unless asked for
    assert got.marginal_tax_rate is None


@pytest.mark.parametrize(
    "code", ["CA-ON", "CA-AB", "CA-BC", "CA-MB", "CA-NB", "CA-NL", "CA-SK", "CA-QC"]
)
@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize("salary", ["0", "100", "2050", "70000", "250000"])
def test_the_average_rate_is_the_total_deductions_over_the_salary_in_every_jurisdiction(
    service: TakeHomeService, code: str, year: int, salary: str
) -> None:
    # The return's steps and the take-home block each list the deductions; this keeps them equal.
    got = service.compute(
        TakeHomeRequest(JurisdictionCode(code), year, Decimal(salary), include_rates=True)
    )

    assert got.average_tax_rate is not None
    expected = (
        Decimal(0)
        if got.salary == 0
        else (got.total_deductions / got.salary).quantize(
            Decimal("0.0001"), rounding="ROUND_HALF_UP"
        )
    )
    assert got.average_tax_rate.value == expected


def test_quebec_has_an_average_rate_with_qpip_in_it_and_a_marginal_rate(
    service: TakeHomeService,
) -> None:
    got = service.compute(
        TakeHomeRequest(JurisdictionCode("CA-QC"), 2025, Decimal(70000), include_rates=True)
    )
    assert got.average_tax_rate is not None
    assert got.average_tax_rate.value == Decimal("0.2877")
    assert got.marginal_tax_rate is not None
    # By hand 0.4193671 (see the Quebec marginal rate values test); the engine rounds the marginal
    # rate half-up to 0.0001 like the average rate.
    assert got.marginal_tax_rate.value == Decimal("0.4194")
    assert got.marginal_tax_rate.unit.name == "core/percent"


@pytest.mark.parametrize(
    ("code", "salary", "rate"),
    [
        # 2026 at the exact edges of the CPP bands ($74,600) and the end of the federal basic
        # personal amount taper ($259,609): a contribution band reads the band that starts there,
        # a bracket or taper reads the band below, so the rate matches a cent either side.
        ("CA-ON", "74599.99", "0.3436"),
        ("CA-ON", "74600", "0.3246"),
        ("CA-ON", "74600.01", "0.3246"),
        ("CA-ON", "259608.99", "0.4982"),
        ("CA-ON", "259609", "0.4982"),
        ("CA-ON", "259609.01", "0.5353"),
        ("CA-QC", "74599.99", "0.4182"),
        ("CA-QC", "74600", "0.3905"),
        ("CA-QC", "74600.01", "0.3905"),
        ("CA-QC", "259608.99", "0.5021"),
        ("CA-QC", "259609", "0.5021"),
        ("CA-QC", "259609.01", "0.5331"),
    ],
)
def test_the_marginal_rate_at_an_edge_matches_the_cent_either_side(
    service: TakeHomeService, code: str, salary: str, rate: str
) -> None:
    got = service.compute(
        TakeHomeRequest(JurisdictionCode(code), 2026, Decimal(salary), include_rates=True)
    )

    assert got.marginal_tax_rate is not None
    assert got.marginal_tax_rate.value == Decimal(rate)


@pytest.mark.parametrize(
    ("code", "year", "salary", "rate"),
    [
        # At $2,000 of salary EI starts to charge a dollar for a dollar (T2204 line 7) and, in
        # Quebec, the QPIP premium applies (Schedule 10), so the rate at the edge matches the cent
        # above it; the cent below it has neither.
        ("CA-ON", 2025, "1999.99", "0.0000"),
        ("CA-ON", 2025, "2000", "1.0000"),
        ("CA-ON", 2025, "2000.01", "1.0000"),
        ("CA-ON", 2026, "2000", "1.0000"),
        ("CA-QC", 2025, "1999.99", "0.0000"),
        ("CA-QC", 2025, "2000", "1.0049"),
        ("CA-QC", 2025, "2000.01", "1.0049"),
        ("CA-QC", 2026, "1999.99", "0.0000"),
        ("CA-QC", 2026, "2000", "1.0043"),
        ("CA-QC", 2026, "2000.01", "1.0043"),
    ],
)
def test_the_marginal_rate_at_2000_of_salary_matches_the_cent_above_it(
    service: TakeHomeService, code: str, year: int, salary: str, rate: str
) -> None:
    got = service.compute(
        TakeHomeRequest(JurisdictionCode(code), year, Decimal(salary), include_rates=True)
    )

    assert got.marginal_tax_rate is not None
    assert got.marginal_tax_rate.value == Decimal(rate)


class _Counting:
    """The real jurisdictions, counting each lookup (and failing the first `fail` of them)."""

    def __init__(self, source: JurisdictionSource, fail: int = 0) -> None:
        self._source = source
        self._fail = fail
        self.calls: list[JurisdictionCode] = []
        self._lock = threading.Lock()

    def get_jurisdiction(self, code: JurisdictionCode) -> Jurisdiction:
        with self._lock:
            self.calls.append(code)
            failing = len(self.calls) <= self._fail
        if failing:
            raise NotFoundError(f"no jurisdiction {code}")
        return self._source.get_jurisdiction(code)


def _counted(fail: int = 0) -> tuple[TakeHomeService, _Counting]:
    real = YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units())
    counting = _Counting(real, fail)
    return TakeHomeService(counting, build_tax_computation(), EnglishTakeHomeText()), counting


def _request(code: str = "CA-ON", year: int = 2025, salary: int = 70000) -> TakeHomeRequest:
    return TakeHomeRequest(JurisdictionCode(code), year, Decimal(salary))


def test_the_jurisdiction_is_read_once_per_jurisdiction_and_year() -> None:
    counted, counting = _counted()
    counted.compute(_request(salary=70000))
    counted.compute(_request(salary=90000))
    assert counting.calls == [JurisdictionCode("CA-ON")]


def test_another_year_or_jurisdiction_is_read_separately() -> None:
    counted, counting = _counted()
    counted.compute(_request("CA-ON", 2025))
    counted.compute(_request("CA-ON", 2026))
    counted.compute(_request("CA-QC", 2025))
    counted.compute(_request("CA-ON", 2025))
    counted.compute(_request("CA-ON", 2026))
    counted.compute(_request("CA-QC", 2025))
    assert counting.calls == [JurisdictionCode("CA-ON")] * 2 + [JurisdictionCode("CA-QC")]


def test_a_failed_lookup_is_not_cached() -> None:
    counted, counting = _counted(fail=1)
    with pytest.raises(NotFoundError):
        counted.compute(_request())
    assert counted.compute(_request()).take_home == Decimal("53468.68")
    assert len(counting.calls) == 2


def test_a_jurisdiction_without_take_home_figures_raises_on_every_call() -> None:
    source = YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units())
    counting = _Counting(_WithoutTakeHome(source))
    bare = TakeHomeService(counting, build_tax_computation(), EnglishTakeHomeText())
    for _ in range(2):
        with pytest.raises(NotFoundError, match="CA-ON 2025"):
            bare.compute(_request())


@pytest.mark.parametrize("case", [Case(a) for a in ANSWERS[:3]], ids=repr)
def test_a_cached_answer_equals_the_first_one(case: Case) -> None:
    want = case.answer
    counted, _ = _counted()
    request = TakeHomeRequest(
        JurisdictionCode(want["jurisdiction"]), want["year"], Decimal(want["salary"])
    )
    first = counted.compute(request)
    second = counted.compute(request)
    assert second == first
    assert str(second.take_home) == want["take_home"]


def test_concurrent_callers_of_a_cold_key_read_once() -> None:
    counted, counting = _counted()
    workers = 8
    barrier = threading.Barrier(workers)

    def run(_: int) -> Decimal:
        barrier.wait()
        return counted.compute(_request()).take_home

    with ThreadPoolExecutor(workers) as pool:
        results = list(pool.map(run, range(workers)))
    assert results == [Decimal("53468.68")] * workers
    assert counting.calls == [JurisdictionCode("CA-ON")]
