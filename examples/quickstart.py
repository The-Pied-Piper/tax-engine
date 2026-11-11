import sys
from decimal import Decimal

from tax_engine import build_tax_computation
from tax_engine.adapters.inbound.trace_english import EnglishNames, EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME

engine = build_tax_computation()
sheets = engine.compute(
    JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, Decimal(sys.argv[1]))
)
for form, form_sheets in sheets.items():
    for sheet in form_sheets:
        print(f"\n== {form} ==")
        renderer = EnglishTraceRenderer()
        names = EnglishNames(sheet)
        for line in sheet.trace:
            # The sentence names the figures it uses as the form prints them when it is given
            # the worksheet; the figure the line is about is named beside it.
            sentence = renderer.render(line, sheet)
            print(sentence if line.label is None else f"{names.of_label(line.label)}: {sentence}")
