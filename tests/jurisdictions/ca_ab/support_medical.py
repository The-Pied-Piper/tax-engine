"""The Alberta AB428 credits sheet through the registered engine, for the medical expenses and
donations line tests: a salary and any of the optional input lines 44, 50, 55 and 56."""

from __future__ import annotations

from decimal import Decimal

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ab import catalog as ab
from tax_engine.registrations import artifact_kinds

D = Decimal
INPUTS = {
    "line_44": ab.AB428_MEDICAL_EXPENSES_LINE_44,
    "line_50": ab.AB428_ALLOWABLE_MEDICAL_EXPENSES_FOR_OTHER_DEPENDANTS_LINE_50,
    "line_55": ab.AB428_DONATIONS_AMOUNT_LINE_55,
    "line_56": ab.AB428_DONATIONS_AMOUNT_LINE_56,
}


def credits_sheet(salary: str, **given: str) -> Worksheet:
    """The `ca-ab/ab428_credits` sheet of a $salary return with the given optional inputs."""
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    artifacts += [Artifact(INPUTS[name], D(value)) for name, value in given.items()]
    (sheet,) = build_tax_computation().compute(JurisdictionCode("CA-AB"), 2025, *artifacts)[
        "ca-ab/ab428_credits"
    ]
    return sheet


def figure(sheet: Worksheet, identifier: str) -> Decimal:
    """The amount the sheet holds for the named kind."""
    value = sheet.get(artifact_kinds().kind(identifier)).value
    assert isinstance(value, Decimal)
    return value
