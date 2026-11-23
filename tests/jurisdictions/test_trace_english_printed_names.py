"""A sentence of a line the form numbers never names a figure by its internal label, and stays
short enough to read, for every listed jurisdiction.

The returns are salary-only, so an entry line that a salary-only caller leaves blank (a credit with
a printed maximum, say) renders its blank reason, not its bound: a step that supplies such a
bound is titled by hand and pinned by its own part's test.
"""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal
from itertools import product

import pytest

import tax_engine.adapters.inbound.trace_english.names as names_module
from tax_engine import build_tax_computation
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
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


def sentence_failures(
    sheet: Worksheet, lines: Iterable[TraceLine], fallbacks: list[str]
) -> list[str]:
    """One line for each sentence of `lines` the form numbers that names a figure by its internal
    label or has more than `MAXIMUM_WORDS` words; `fallbacks` is the list the rendering fills.
    """
    renderer = EnglishTraceRenderer()
    failures: list[str] = []
    for line in lines:
        fallbacks.clear()
        text = renderer.render(line, sheet)
        if line.label is None or not sheet.reference(line.label):
            continue  # the page hides a line the form does not number
        failures += [f"{line.label} names {label}" for label in fallbacks]
        if len(text.split()) > MAXIMUM_WORDS:
            failures.append(f"{line.label} is {len(text.split())} words: {text}")
    return failures


# --- the real jurisdictions ---------------------------------------------------------------------


@pytest.mark.parametrize("code", JURISDICTIONS.jurisdiction_codes(), ids=str)
def test_numbered_lines_never_name_a_figure_by_its_internal_label(
    code: JurisdictionCode, monkeypatch: pytest.MonkeyPatch
) -> None:
    fallbacks = record_label_fallbacks(monkeypatch)
    roots = JURISDICTIONS.roots()
    jurisdiction = YamlJurisdictionSource(roots, artifact_kinds(), units()).get_jurisdiction(code)
    engine = build_tax_computation()
    failures: list[str] = []
    for year, salary in product(resolvable_years(roots.values(), jurisdiction), SALARIES):
        sheets = engine.compute(
            TaxCalculationRequest(code, year, (Artifact(EMPLOYMENT_INCOME, Decimal(salary)),))
        )
        for form, form_sheets in sheets.items():
            for sheet in form_sheets:
                failures += [
                    f"{form} {failure}"
                    for failure in sentence_failures(sheet, sheet.trace, fallbacks)
                ]
    assert failures == []


# --- the guard itself, on made-up kinds ---------------------------------------------------------

GROSS, ALLOWANCE, NET = (AmountKind(f"ex/{name}") for name in ("gross_pay", "allowance", "net_pay"))
LINE = SubtractedNotBelowZeroLine(
    output=NET,
    minuend=GROSS,
    minuend_amount=Decimal("70000.00"),
    subtrahend=ALLOWANCE,
    subtrahend_amount=Decimal("71300.00"),
    result=Decimal("0.00"),
    rounding=NO_ROUNDING,
)


def test_the_guard_sees_a_sentence_that_names_a_figure_by_its_label(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sheet = Worksheet(figure_references={"net_pay": "4", "gross_pay": "2"})

    failures = sentence_failures(sheet, (LINE,), record_label_fallbacks(monkeypatch))

    assert failures == ["net_pay names allowance"]


def test_the_guard_passes_a_sentence_that_names_every_figure_as_printed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sheet = Worksheet(figure_references={"net_pay": "4", "gross_pay": "2", "allowance": "B"})

    assert sentence_failures(sheet, (LINE,), record_label_fallbacks(monkeypatch)) == []


def test_the_guard_skips_a_line_the_form_does_not_number(monkeypatch: pytest.MonkeyPatch) -> None:
    assert sentence_failures(Worksheet(), (LINE,), record_label_fallbacks(monkeypatch)) == []


def test_the_guard_sees_a_sentence_over_the_word_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    long_title = " ".join(["word"] * MAXIMUM_WORDS)
    sheet = Worksheet(
        figure_references={"net_pay": "4", "gross_pay": "2"},
        figure_titles={"allowance": long_title},
    )

    (failure,) = sentence_failures(sheet, (LINE,), record_label_fallbacks(monkeypatch))

    assert failure.startswith("net_pay is ")
