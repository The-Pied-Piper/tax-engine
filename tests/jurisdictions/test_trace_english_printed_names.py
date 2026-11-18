"""A sentence of a line the form numbers never names a figure by its internal label, and stays
short enough to read, for every listed jurisdiction.
"""

from __future__ import annotations

from decimal import Decimal
from itertools import product

import pytest

import tax_engine.adapters.inbound.trace_english.names as names_module
from tax_engine import build_tax_computation
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units
from tests.application.services.test_every_resolvable_year import resolvable_years

MAXIMUM_WORDS = 40
SALARIES = ("20000", "70000", "150000", "275000")


@pytest.mark.parametrize("code", JURISDICTIONS.jurisdiction_codes(), ids=str)
def test_numbered_lines_never_name_a_figure_by_its_internal_label(
    code: JurisdictionCode, monkeypatch: pytest.MonkeyPatch
) -> None:
    current = [""]
    fallbacks: list[tuple[str, str]] = []
    plain_words = names_module._plain_words

    def recording(label: str) -> str:
        fallbacks.append((current[0], label))
        return plain_words(label)

    monkeypatch.setattr(names_module, "_plain_words", recording)
    engine = build_tax_computation()
    too_long: list[str] = []
    named_by_label: list[str] = []
    roots = JURISDICTIONS.roots()
    jurisdiction = YamlJurisdictionSource(roots, artifact_kinds(), units()).get_jurisdiction(code)
    for year, salary in product(resolvable_years(roots.values(), jurisdiction), SALARIES):
        sheets = engine.compute(code, year, Artifact(EMPLOYMENT_INCOME, Decimal(salary)))
        for form, form_sheets in sheets.items():
            for sheet in form_sheets:
                renderer = EnglishTraceRenderer()
                for line in sheet.trace:
                    current[0] = f"{form} {line.label}"
                    text = renderer.render(line, sheet)
                    if line.label is None or not sheet.reference(line.label):
                        continue  # the page hides a line the form does not number
                    if len(text.split()) > MAXIMUM_WORDS:
                        too_long.append(f"{current[0]}: {text}")
                    named_by_label += [
                        f"{where} names {label}"
                        for where, label in fallbacks
                        if where == current[0]
                    ]
    assert named_by_label == []
    assert too_long == []
