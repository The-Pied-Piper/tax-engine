"""The shared setup of the Quebec Schedule P line tests: a test header, a stub of the TP-1 income
form that exports the salary as line 101, and a builder of the Schedule P worksheet for a salary
and the optional answers a test gives."""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    """)
TP1_STUB = dedent("""\
    form:
      name: ca-qc/tp1_income
      required: true
      exports:
        - ca/employment_income
    """)

FIRST_PARTS = ("salary.yaml", "schedule_p_line_10_inputs.yaml", "schedule_p_line_10.yaml")


def schedule_p_form(*exports: str) -> str:
    """A Schedule P form declaration that exports only the lines a test builds."""
    lines = "".join(f"    - {export}\n" for export in exports)
    return f"form:\n  name: ca-qc/schedule_p\n  required: true\n  exports:\n{lines}"


def schedule_p(
    take_home_service: TakeHomeService,
    form: str,
    parts: tuple[str, ...],
    salary: str,
    *given: tuple[AmountKind, str],
) -> Worksheet:
    """The Schedule P worksheet of a salary; `given` are the optional answers a test passes."""
    starting = [Artifact(EMPLOYMENT_INCOME, Decimal(salary))]
    starting += [Artifact(kind, Decimal(value)) for kind, value in given]
    (sheet,) = take_home_service(HEADER, form, *parts, texts=(TP1_STUB,)).compute(
        JurisdictionCode("CA-QC"), 2025, *starting
    )["ca-qc/schedule_p"]
    return sheet
