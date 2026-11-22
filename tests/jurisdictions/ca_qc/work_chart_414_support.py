"""Shared helpers of the Work Chart 414 line tests.

Work Chart 414 (TP-1.D.GR-V 2025-12, "Tax credit for contributions to authorized Québec political
parties") has no upstream form: its line 1 is its own optional input. A test declares the chart
form itself, exporting the lines it checks, over the part files of the lines under test; the
end-to-end test uses the real form declaration and every real part. The salary only gives the
header's starting input.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import WORK_CHART_414_CONTRIBUTIONS_INPUT_LINE_1
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import HEADER, UPSTREAM_PARTS

D = Decimal
FORM_NAME = "ca-qc/work_chart_414"
# The line 1 input and its step, which every later line reads.
LINE_1_PARTS = ("work_chart_414_line_1_input.yaml", "work_chart_414_line_1.yaml")
# The parts of each line with the parts it reads, in form order.
LINE_2_PARTS = (*LINE_1_PARTS, "work_chart_414_line_2.yaml")
LINE_10_PARTS = (*LINE_2_PARTS, "work_chart_414_line_10.yaml")
LINE_3_PARTS = (*LINE_2_PARTS, "work_chart_414_line_3.yaml")
LINE_11_PARTS = (*LINE_3_PARTS, "work_chart_414_line_11.yaml")
LINE_14_PARTS = (
    *LINE_2_PARTS,
    "work_chart_414_line_10.yaml",
    "work_chart_414_line_3.yaml",
    "work_chart_414_line_11.yaml",
    "work_chart_414_line_14.yaml",
)


def chart_form(*exports: str) -> str:
    """A test form declaration of Work Chart 414 exporting `exports`."""
    lines = "".join(f"    - {name}\n" for name in exports)
    return f"form:\n  name: {FORM_NAME}\n  required: true\n  exports:\n{lines}"


def chart_sheet(
    take_home_service: TakeHomeService,
    exports: tuple[str, ...],
    parts: tuple[str, ...],
    contributions: str | None = None,
    form: str | None = None,
) -> Worksheet:
    """The Work Chart 414 worksheet for `contributions` (line 1 is left blank when None) over the
    chart `parts`. `form` replaces the test chart form (the end-to-end test uses the real one)."""
    starting = [Artifact(EMPLOYMENT_INCOME, D("70000"))]
    if contributions is not None:
        starting.append(Artifact(WORK_CHART_414_CONTRIBUTIONS_INPUT_LINE_1, D(contributions)))
    service = take_home_service(
        HEADER,
        chart_form(*exports) if form is None else form,
        *UPSTREAM_PARTS,
        *parts,
    )
    (sheet,) = service.compute(
        TaxCalculationRequest(JurisdictionCode("CA-QC"), 2025, tuple(starting))
    )[FORM_NAME]
    return sheet
