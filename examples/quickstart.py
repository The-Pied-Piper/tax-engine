import sys
from decimal import Decimal

from tax_engine import build_tax_computation
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
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
        for line in sheet.trace:
            # The sentence names the figures it uses, as the form prints them, when it is given
            # the worksheet; the title and reference of the figure it is about go beside it.
            title = None if line.label is None else sheet.title(line.label)
            reference = None if line.label is None else sheet.reference(line.label)
            heading = " ".join(
                part
                for part in (None if reference is None else f"[line {reference}]", title)
                if part is not None
            )
            print(f"{heading + ': ' if heading else ''}{renderer.render(line, sheet)}")
