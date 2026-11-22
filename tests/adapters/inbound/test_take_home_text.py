"""EnglishTakeHomeText writes units and trace lines in English."""

from __future__ import annotations

from decimal import Decimal

from tax_engine import build_tax_computation
from tax_engine.adapters.inbound.take_home_text import EnglishTakeHomeText
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.application.services.take_home_models import UnitDescription
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.unit import Unit
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME


def test_a_unit_is_described_with_its_english_text() -> None:
    assert EnglishTakeHomeText().unit(Unit("ca/cad")) == UnitDescription(
        name="ca/cad",
        placement="before",
        singular="CA$",
        plural="CA$",
        spaced=False,
        as_percentage=False,
    )
    assert EnglishTakeHomeText().unit(Unit("core/percent")).as_percentage is True


def test_a_trace_line_is_worded_as_the_english_renderer_words_it() -> None:
    sheets = build_tax_computation().compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, Decimal(70000))
    )
    (sheet,) = sheets["ca/t1_tax_and_credits"]
    line = sheet.trace[0]
    assert EnglishTakeHomeText().sentence(line, sheet) == EnglishTraceRenderer().render(line, sheet)
