"""Shared helpers of the solidarity credit wiring tests: the answers, the maximum before reduction
and the family income.

The wiring part files are `solidarity_credit_answers.yaml` (the optional answers),
`solidarity_credit_maximum.yaml` (the QST and housing components, added) and
`solidarity_credit_family_income.yaml` (TP-1 line 275). The tests compose the real parts under a
test header and a test-local form declaration that exports `identifier` and every figure of the
parts that no later step consumes. The salary is the only required input; an answer the caller does
not give takes its default (not alone, neither tenant nor owner, one owner or tenant).
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent
from typing import Any

import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds

FORM = "ca-qc/solidarity_credit"
ALONE = "ca-qc/solidarity_lived_alone_line_12"
TENANT = "ca-qc/solidarity_tenant_or_owner_lines_32_36"
OCCUPANTS = "ca-qc/solidarity_occupants_lines_33_36"
ANSWERS_PART = "solidarity_credit_answers.yaml"
AMOUNTS_PART = "solidarity_credit_amounts.yaml"
MAXIMUM_PART = "solidarity_credit_maximum.yaml"
HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    """)


def _steps(part: str) -> list[dict[str, Any]]:
    steps = yaml.safe_load((QUEBEC_PARTS / part).read_text("utf-8"))["capabilities"]
    assert isinstance(steps, list)
    return steps


def _consumed(parts: tuple[str, ...]) -> set[str]:
    consumed: set[str] = set()
    for part in parts:
        for step in _steps(part):
            for value in step["consumes"].values():
                consumed.update(value if isinstance(value, list) else [value])
    return consumed


def _printed_amounts() -> list[str]:
    """The exports of the real form that the amounts part produces."""
    produced = {step["produces"]["output"] for step in _steps(AMOUNTS_PART)}
    form = yaml.safe_load((QUEBEC_PARTS / "solidarity_credit.yaml").read_text("utf-8"))["form"]
    return [name for name in form["exports"] if name in produced]


def form_part(identifier: str, parts: tuple[str, ...]) -> str:
    """A form declaration exporting `identifier`, the printed amounts and the figures of `parts`
    nothing consumes."""
    consumed = _consumed(parts)
    exports = [identifier, *_printed_amounts()]
    for part in parts:
        for step in _steps(part):
            output = step["produces"]["output"]
            if output not in consumed and output not in exports:
                exports.append(output)
    lines = "".join(f"    - {name}\n" for name in exports)
    return f"form:\n  name: {FORM}\n  required: true\n  exports:\n{lines}"


def maximum_figure(
    take_home_service: TakeHomeService,
    identifier: str,
    alone: int | None = None,
    tenant: int | None = None,
    occupants: int | None = None,
) -> Any:
    """The figure `identifier` of the maximum chain for the given answers (a left-out answer takes
    its default)."""
    parts = (MAXIMUM_PART,)
    service = take_home_service(
        HEADER, form_part(identifier, parts), AMOUNTS_PART, ANSWERS_PART, *parts
    )
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, Decimal("70000"))]
    for name, answer in ((ALONE, alone), (TENANT, tenant), (OCCUPANTS, occupants)):
        if answer is not None:
            given.append(Artifact(quebec_kinds().kind(name), answer))
    (sheet,) = service.compute(JurisdictionCode("CA-QC"), 2025, *given)[FORM]
    return sheet.get(quebec_kinds().kind(identifier)).value
