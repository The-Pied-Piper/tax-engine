"""A blank input is one row in the trace, however many steps read it.

CA-ON 2025 at $70,000 has no self-employment earnings, so `ca/t2204_self_employment_earnings`
(T2204 line 2) is left blank. Two steps read it (the line 1 check and the line 1 plus 2 sum), and
the trace says once that it was left blank and taken as 0. With a figure entered it has no blank
row at all.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.trace import BlankFallbackLine, LeftBlankLine, TraceLine
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.refund import T2204_SELF_EMPLOYMENT_EARNINGS
from tax_engine.registrations import JURISDICTIONS, parameter_parsers
from tests.capabilities import bundled_capabilities
from tests.kinds import bundled_kinds

D = Decimal


def t2204_trace(*extra: Artifact[Decimal]) -> tuple[TraceLine, ...]:
    service = TaxComputationService(
        YamlJurisdictionSource(JURISDICTIONS.roots(), bundled_kinds()),
        YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers()),
        bundled_capabilities(),
    )
    sheets = service.compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(70000)), *extra
    )
    (sheet,) = sheets["ca/t2204"]
    return sheet.trace


def about(trace: tuple[TraceLine, ...], label: str) -> list[TraceLine]:
    return [
        line
        for line in trace
        if isinstance(line, (LeftBlankLine, BlankFallbackLine)) and line.label == label
    ]


def test_a_blank_input_read_by_two_steps_is_one_row_at_70000() -> None:
    trace = t2204_trace()

    rows = about(trace, "t2204_self_employment_earnings")
    assert [type(row) for row in rows] == [BlankFallbackLine]
    assert rows[0].amount == 0


def test_every_blank_row_of_the_t2204_trace_is_about_a_different_input() -> None:
    labels = [
        line.label for line in t2204_trace() if isinstance(line, (LeftBlankLine, BlankFallbackLine))
    ]

    assert len(labels) == len(set(labels))


def test_an_entered_figure_has_no_blank_row() -> None:
    trace = t2204_trace(Artifact(T2204_SELF_EMPLOYMENT_EARNINGS, D(5)))

    assert about(trace, "t2204_self_employment_earnings") == []
