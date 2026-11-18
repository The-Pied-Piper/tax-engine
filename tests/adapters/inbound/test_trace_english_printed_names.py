"""A sentence of a line the form numbers never names a figure by its internal label, and stays
short enough to read.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.adapters.inbound.trace_english.names as names_module
from tax_engine import build_tax_computation
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME

MAXIMUM_WORDS = 40
SALARIES = ("20000", "70000", "150000", "275000")


@pytest.mark.parametrize("code", ["CA-ON", "CA-AB", "CA-BC"])
@pytest.mark.parametrize("year", [2025, 2026])
def test_numbered_lines_never_name_a_figure_by_its_internal_label(
    code: str, year: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    fallbacks: list[tuple[str, str]] = []
    current: list[str] = [""]
    original = names_module._plain_words

    def recording(label: str) -> str:
        fallbacks.append((current[0], label))
        return original(label)

    monkeypatch.setattr(names_module, "_plain_words", recording)
    engine = build_tax_computation()
    too_long: list[str] = []
    for salary in SALARIES:
        sheets = engine.compute(
            JurisdictionCode(code), year, Artifact(EMPLOYMENT_INCOME, Decimal(salary))
        )
        for form, form_sheets in sheets.items():
            for sheet in form_sheets:
                renderer = EnglishTraceRenderer()
                for line in sheet.trace:
                    current[0] = f"{form} {line.label}"
                    text = renderer.render(line, sheet)
                    if line.label is None or not sheet.reference(line.label):
                        continue  # the page hides a line the form does not number
                    if len(text.split()) > MAXIMUM_WORDS:
                        too_long.append(f"{form} {line.label}: {text}")
                    named = [found for found in fallbacks if found[0] == current[0]]
                    assert named == [], f"{current[0]} names {named} by its internal label"
    assert too_long == []
