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
        print("\n".join(EnglishTraceRenderer().render_all(sheet.trace)))
