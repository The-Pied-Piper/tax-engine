"""Shared helpers of the Work Chart 401 line tests.

Work Chart 401 line 1 reads TP-1 line 299 from the net income form, so the tests run the real
parts of that form and of the forms it reads on the salary (the TP-1 slip figures that Schedule U
reads are plain starting inputs, as in the net income tests); only the part files of the chart
lines under test change from one test module to the next. Each test declares the chart form
itself, exporting the lines it checks.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import (
    HEADER,
    UPSTREAM_PARTS,
)

D = Decimal

# The net income lines that produce line 299; `tp1_net_income.yaml` declares the form and its
# exports.
NET_INCOME_LINE_PARTS = (
    "tp1_net_income_line_201.yaml",
    "tp1_net_income_line_248.yaml",
    "tp1_net_income_line_254_inputs.yaml",
    "tp1_net_income_line_254.yaml",
    "tp1_net_income_line_256.yaml",
    "tp1_net_income_line_260_input.yaml",
    "tp1_net_income_line_275.yaml",
    "tp1_net_income_line_276_input.yaml",
    "tp1_net_income_line_278_input.yaml",
    "tp1_net_income_line_279.yaml",
    "tp1_net_income_line_298_inputs.yaml",
    "tp1_net_income_line_298.yaml",
    "tp1_net_income_line_299.yaml",
)


def chart_form(*exports: str) -> str:
    """A test form declaration of Work Chart 401 exporting `exports`."""
    lines = "".join(f"    - {name}\n" for name in exports)
    return f"form:\n  name: ca-qc/work_chart_401\n  required: true\n  exports:\n{lines}"


def chart_sheet(
    take_home_service: TakeHomeService,
    salary: str,
    exports: tuple[str, ...],
    parts: tuple[str, ...],
    *given: tuple[AmountKind, str],
    form: str | None = None,
) -> Worksheet:
    """The Work Chart 401 worksheet for a salary, over the upstream parts, the net income parts and
    the chart `parts`; every optional input is left out unless in `given`. `form` replaces the
    test chart form (the end-to-end test declares the net income form and uses the real chart
    part)."""
    starting = [
        Artifact(EMPLOYMENT_INCOME, D(salary)),
    ]
    starting.extend(Artifact(kind, D(value)) for kind, value in given)
    declaration = (
        ("tp1_net_income.yaml", "tp1_net_income_line_275_spouse_input.yaml") if form is None else ()
    )
    service = take_home_service(
        HEADER,
        chart_form(*exports) if form is None else form,
        *UPSTREAM_PARTS,
        *declaration,
        *NET_INCOME_LINE_PARTS,
        *parts,
    )
    (sheet,) = service.compute(JurisdictionCode("CA-QC"), 2025, *starting)["ca-qc/work_chart_401"]
    return sheet
