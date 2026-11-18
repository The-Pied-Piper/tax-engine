"""A sentence of a line the form numbers never names a figure by its internal label, and stays
short enough to read, for every listed jurisdiction.

The returns are salary-only, so an entry line that a salary-only caller leaves blank (a credit with
a printed maximum, say) renders its blank reason, not its bound: a step that supplies such a
bound is titled by hand and pinned by its own part's test.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from decimal import Decimal
from itertools import product

import pytest

import tax_engine.adapters.inbound.trace_english.names as names_module
from tax_engine import build_tax_computation
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.trace import SubtractedNotBelowZeroLine, TraceLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units
from tests.application.services.test_every_resolvable_year import resolvable_years

MAXIMUM_WORDS = 40
SALARIES = ("20000", "70000", "150000", "275000")


def record_label_fallbacks(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """The list that gets each internal label a sentence falls back to, in plain words."""
    labels: list[str] = []
    plain_words = names_module._plain_words

    def recording(label: str) -> str:
        labels.append(label)
        return plain_words(label)

    monkeypatch.setattr(names_module, "_plain_words", recording)
    return labels


def numbered_sentences(
    sheet: Worksheet, lines: Iterable[TraceLine], fallbacks: list[str]
) -> Iterator[tuple[TraceLine, str, list[str]]]:
    """Each of `lines` the form numbers, its sentence, and the labels that sentence fell back to
    (read from `fallbacks`, which the rendering fills).
    """
    renderer = EnglishTraceRenderer()
    for line in lines:
        fallbacks.clear()
        text = renderer.render(line, sheet)
        if line.label is not None and sheet.reference(line.label):
            yield line, text, list(fallbacks)


def test_the_guard_sees_a_sentence_that_names_a_figure_by_its_label(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gross, less, net = (AmountKind(f"ex/{name}") for name in ("gross_pay", "allowance", "net_pay"))
    line = SubtractedNotBelowZeroLine(
        output=net,
        minuend=gross,
        minuend_amount=Decimal("70000.00"),
        subtrahend=less,
        subtrahend_amount=Decimal("71300.00"),
        result=Decimal("0.00"),
        rounding=NO_ROUNDING,
    )
    sheet = Worksheet(figure_references={"net_pay": "4", "gross_pay": "2"})

    fallbacks = record_label_fallbacks(monkeypatch)

    assert [labels for _, _, labels in numbered_sentences(sheet, (line,), fallbacks)] == [
        ["allowance"]
    ]


@pytest.mark.parametrize("code", JURISDICTIONS.jurisdiction_codes(), ids=str)
def test_numbered_lines_never_name_a_figure_by_its_internal_label(
    code: JurisdictionCode, monkeypatch: pytest.MonkeyPatch
) -> None:
    fallbacks = record_label_fallbacks(monkeypatch)
    roots = JURISDICTIONS.roots()
    jurisdiction = YamlJurisdictionSource(roots, artifact_kinds(), units()).get_jurisdiction(code)
    engine = build_tax_computation()
    by_label: list[str] = []
    too_long: list[str] = []
    for year, salary in product(resolvable_years(roots.values(), jurisdiction), SALARIES):
        sheets = engine.compute(code, year, Artifact(EMPLOYMENT_INCOME, Decimal(salary)))
        for form, form_sheets in sheets.items():
            for sheet in form_sheets:
                for line, text, labels in numbered_sentences(sheet, sheet.trace, fallbacks):
                    where = f"{form} {line.label}"
                    by_label += [f"{where} names {label}" for label in labels]
                    if len(text.split()) > MAXIMUM_WORDS:
                        too_long.append(f"{where}: {text}")
    assert by_label == []
    assert too_long == []
